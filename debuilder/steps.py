import os
import time
import shutil
import logging
import tarfile
import contextlib

import git

from debuilder.utils import DPKG, DCH, Debsign, Reprepro
from debuilder.pbuilder import PBuilder


@contextlib.contextmanager
def change_directory(path):
    starting_directory = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(starting_directory)

def create_or_cleanup(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)

class BuildConfig(object):
    variables = {
        'image'     : ['distros', '{distro}_{arch}', 'base.tar.gz'],
        'builddir'  : ['distros', '{distro}_{arch}', 'builddir'],
        'resultdir' : ['distros', '{distro}_{arch}', 'resultdir'],
        'gitpath'   : ['distros', '{distro}_{arch}', 'builddir', '{product}']
    }

    def check_image(self):
        if os.path.exists(self.image):
            return True
        return False

    def init_image(self):
        self.exe['pbuilder'].create_basebox(self)

    def update_image(self):
        self.exe['pbuilder'].update_basebox(self)

    def __init__(self, product, distro, arch, image=None, output=None):
        self.exe = {
                'pbuilder': PBuilder(),
                'dch'     : DCH(),
                'dpkg'    : DPKG()
        }
        self.distro  = distro
        self.product = product
        self.arch    = arch
        self.dsc     = None
        self.changes = None
        
        # customize workdir
        if output is not None: 
            for key in self.variables.keys():
                self.variables[key][0] = output

        for i in ['builddir', 'resultdir']:
            path = os.path.join(*self.variables[i])
            path = path.format(distro = distro['distro'], arch = arch)
            try:
                logging.info('Recreating dir %s', path)
                create_or_cleanup(path)
                setattr(self, i, path)
            except OSError as e:
                logging.error('Failed to create dir %s', repr(path))
                logging.error('Failed with error: %s', repr(e))
                logging.error('Aborting.')
                exit(1)
        path = os.path.join(*self.variables['image'])
        
        # customize os image path
        if image is not None:
            self.image = image
        else:
            self.image = path.format(distro = distro['distro'], arch = arch)
        if not self.check_image():
            self.init_image()
        else:
            self.update_image()

    def pack_sourcecode(self, path_name, targz_name):
        with tarfile.open(targz_name, 'w:gz') as tar:
            for root, dirs, files in os.walk(path_name):
                if root.find('.git') != -1 or root.find('debian') != -1:
                    continue
                for _file in files:
                    tar.add(os.path.join(root, _file))

    def prepare_sourcecode(self):
        path_to = os.path.join(*self.variables['gitpath']).format(
                distro = self.distro['distro'],
                arch = self.arch,
                product = self.product['product']
        )
        logging.info('Cloning repo %s into %s',
                repr(self.product['git']),
                repr(path_to)
        )
        try:
            self.repo = git.Repo.clone_from(
                    url = self.product['git'],
                    to_path = path_to,
                    recursive = True
            )
        except git.GitCommandError as e:
            logging.error('Failed cloning repo %s with error %s',
                    repr(self.product['git']),
                    e.stderr
            )
            logging.error('Aborting.')
            exit(1)
        logging.info('Checkoutin branch %s', repr(self.product['branch']))
        try:
            self.repo.git.checkout(self.product['branch'])
        except git.GitCommandError as e:
            logging.error('Failed to checkout branch %s with error %s',
                    repr(self.product['branch']),
                    e.stderr
            )
            logging.error('Aborting.')
            exit(1)
        self.version = self.repo.git.describe().strip()
        self.deb_version = '%s~%s' % (self.version, self.distro['distro'])
        build_msg = "Automatic build of " + self.version
        new_dir_name = '{product}-{version}'.format(
                product = self.product['product'],
                version = self.deb_version
        )
        targz_name   = '{product}_{version}.orig.tar.gz'.format(
                product = self.product['product'],
                version = self.deb_version
        )
        dsc_name   = '{product}_{version}-1.dsc'.format(
                product = self.product['product'],
                version = self.deb_version
        )
        with change_directory(path_to):
            os.environ['NAME'] = self.product['sign_id']
            os.environ['DEBEMAIL'] = self.product['sign_email']
            self.exe['dch'](self, build_msg)
            with open('VERSION', 'w') as f:
                f.write(self.version)
            self.repo.git.commit(a = True, m = build_msg)
            os.chdir('..')
            shutil.move(self.product['product'], new_dir_name)
            git.Repo(new_dir_name)
            self.pack_sourcecode(new_dir_name, targz_name)
            self.exe['dpkg'].build_source(new_dir_name)
            self.dsc = os.path.abspath(dsc_name)

    def build_sourcecode(self):
        self.exe['pbuilder'].build_product(self)

    def sign_package(self):
        path_to = os.path.join(*self.variables['resultdir']).format(
            distro=self.distro['distro'],
            arch=self.arch,
        )
        sign_id = self.product.get('sign_id', None)
        if not sign_id:
            logging.error('No sign id specified. Aborting')
            exit(1)
        if not self.deb_version:
            logging.error('Build is not prepared. Nothong to sign')
            exit(1)
        with change_directory(path_to):
            self.changes = '{product}_{version}-1_{arch}.changes'.format(
                product=self.product['product'], version=self.deb_version,
                arch=self.arch
            )
            signer = Debsign()
            signer.sign_product(sign_id, self.changes)


    def import_package(self, repo_path):
        path_to = os.path.join(*self.variables['resultdir']).format(
            distro=self.distro['distro'],
            arch=self.arch,
        )
        if not self.changes:
            logging.error('Build is not signed. Aborting')
            exit(0)
        with change_directory(path_to):
            importer = Reprepro()
            importer.import_product(repo_path, self.distro['distro'], self.changes)
        

