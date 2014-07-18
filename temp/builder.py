import os
import os.path
import shutil
import shlex
import time
import tarfile
import yaml
import subprocess


def build_command(args, kwargs):
    cmd = ' '
    for arg in args:
        if arg.find(' ') != -1:
            arg = repr(arg)
        cmd += str(arg) + ' '

    for k, v in kwargs.iteritems():
        v = ('' if v == True else str(v))
        if v.find(' ') != -1:
            v = repr(v)
        if len(v) > 0:
            v = '=' + v
        k = str(k).replace('_', '-')
        pref = ' -'
        if len(k) != 1:
            pref = pref + '-'
        cmd += pref + k + v
    return cmd

class ChangeDir:
    def __init__(self, path):
        self.oldpath = None
        self.path = path

    def __enter__(self):
        self.oldpath = os.path.abspath(os.getcwd())
        os.chdir(self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.oldpath)


class PBuilder:
    def __init__(self):
        pass
    def __build_command(self, _type, _args, _kwargs):
        return 'sudo pbuilder %s %s' % (_type, build_command(_args, _kwargs))

    def update(self, *args, **kwargs):
        process = subprocess.Popen(
                shlex.split(self.__build_command('update', args, kwargs)),
#                stdout = subprocess.PIPE,
#                stderr = subprocess.PIPE,
        )
        output = process.communicate()
        print output

    def build(self, *args, **kwargs):
        process = subprocess.Popen(
                shlex.split(self.__build_command('build', args, kwargs)),
#                stdout = subprocess.PIPE,
#                stderr = subprocess.PIPE,
        )
        output = process.communicate()
        print output


def debchange(*args, **kwargs):
    cmd = 'dch' + build_command(args, kwargs)
    print cmd
    process = subprocess.Popen(
            shlex.split(cmd),
#            stdout = subprocess.PIPE,
#            stderr = subprocess.PIPE,
    )
    output = process.communicate()
    print output


class DPKG:
    def __init__(self):
        pass
    def source(self, name):
        cmd = 'dpkg-source -b ' + name
        process = subprocess.Popen(
                shlex.split(cmd),
#                stdout = subprocess.PIPE,
#                stderr = subprocess.PIPE,
        )
        output = process.communicate()
        print output


class Git:
    def __init__(self, repo, name):
        self.name = name
        self.repo = repo
        self.workdir = os.path.join(os.path.abspath(os.getcwd()), name)
        self.tag = 'master'
        process = subprocess.Popen(
                shlex.split('git clone --recursive %s %s' % (repo, name)),
#                stdout = subprocess.PIPE,
#                stderr = subprocess.PIPE,
        )
        output = process.communicate()
        print output

    def checkout(self, tag = None):
        if tag:
            self.tag = tag
        process = subprocess.Popen(
                shlex.split('git checkout %s' % self.tag),
#                stdout = subprocess.PIPE,
#                stderr = isubprocess.PIPE,
                cwd = self.workdir,
        )
        output = process.communicate()
        print output

    def describe(self, tag):
        process = subprocess.Popen(
                shlex.split('git describe %s' % tag),
                stdout = subprocess.PIPE,
#                stderr = subprocess.PIPE,
                cwd = self.workdir,
        )
        output = process.communicate()
        return output[0]

    def commit(self, *args, **kwargs):
        cmd = "git commit "
        cmd += build_command(args, kwargs)
        print cmd
        process = subprocess.Popen(
                shlex.split(cmd),
#                stdout = subprocess.PIPE,
#                stderr = subprocess.PIPE,
                cwd = self.workdir,
        )
        output = process.communicate()
        print output

pbuilder = PBuilder()
dpkg = DPKG()
# EXAMPLE OF CONFIGURATION
# precise-amd64   (<version>-<arch>)
# ---
# arch: amd64
# distribution: precise
# os: ubuntu
# tag: precise
# file: precise_amd64.tar.gz (OR MAYBE <tag>_<arch>.tar.gz)
# ...
# ubuntu-tarantool-master (<distro>-<product>-<branch>)
# ---
# branch: master
# product: tarantool
# repository: /home/buildbot/ubuntu-master
# sign_id: tarantool-ru
# sign_email: tarantool-ru@googlegroups.com
# git: git://github.com/mailru/tarantool.git
# ...
# ubuntu-tarantool-stable (<distro>-<product>-<branch>)
# ---
# branch: stable
# product: tarantool-lts
# repository: /home/buildbot/ubuntu-stable
# sign_id: tarantool-ru
# sign_email: tarantool-ru@googlegroups.com
# git: git://github.com/mailru/tarantool.git
# ...
distros = yaml.load("""---
arch: amd64
distribution: precise
os: ubuntu
tag: precise
file: base.tar.gz
...""")

oss = yaml.load("""---
branch: stable
product: tarantool-lts
repository: /home/buildbot/ubuntu-stable
sign_id: tarantool-ru
sign_email: tarantool-ru@googlegroups.com
git: git://github.com/mailru/tarantool.git
...""")

#distros = yaml.load(open('precise-amd64').read())
#oss     = yaml.load(open('ubuntu-master').read())

def main():
    pass

#---------------PREPARE-------------------#
def clean_and_create(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)

clean_and_create('pbuilder')
clean_and_create('pbuilder_result')
with ChangeDir('pbuilder'):
    git = Git(oss['git'], oss['product'])
git.checkout(oss['branch'])
version = git.describe('HEAD').replace('-', '+').strip()

current_time = time.strftime('+%Y%m%d+%H%M')
deb_version = version + current_time
build_msg = "automatic build of " + version
os.environ['NAME'] = oss['sign_id']
os.environ['DEBEMAIL'] = oss['sign_email']
with ChangeDir('pbuilder/' + oss['product']):
    debchange(
            build_msg,
            distribution = 'saucy',
            newversion = deb_version,
            force_distribution = True,
            force_bad_version = True
    )
git.commit(all = True, message = build_msg)

targz_name   = '%s_%s.orig.tar.gz' % (oss['product'], deb_version)
deb_dir_name = '%s-%s' % (oss['product'], deb_version)
new_dir_name = 'pbuilder/%s-%s' %  (oss['product'], deb_version)
shuti.move   ('pbuilder/%s' % oss['product'], new_dir_name)

with open(os.path.join(new_dir_name, 'VERSION'), 'w') as f:
    f.write(version)

with ChangeDir('pbuilder'):
    with tarfile.open(name = targz_name, mode = 'w:gz') as tar:
        for root, dirs, files in os.walk(deb_dir_name):
            if root.find('.git') != -1 or root.find('debian') != -1:
                continue
            for _file in files:
                tar.add(os.path.join(root, _file))
#    shutil.move(targz_name, '../')
    dpkg.source(deb_dir_name)
#--------------- UPDATE ------------------#
    pbuilder.update(
#             basetgz = distros['file'],
#             distribution = distros['distribution'],
#             architecture = distros['arch'],
            autocleanaptcache = True)
#--------------- UPDATE ------------------#
#--------------- BUILD  ------------------#
    pbuilder.build('%s_%s.dsc' % (oss['product'], deb_version),
#             basetgz = distros['file'],
             buildresult = '../pbuilder_result',
#             architecture = distros['arch'],
            autocleanaptcache = True)
#--------------- BUILD  ------------------#
build_changes = '%s_%s_%s.changes' % (oss['product'], deb_version, distros['arch'])
os.environ['DEBSIGN_MAINT'] = oss['sign_id']
debsign(build_changes, m=oss['sign_id'])
