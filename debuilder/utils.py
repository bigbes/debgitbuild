import logging

from debuilder.executable import Executable, ExecutableError

class DCH(Executable):
    def __init__(self):
        Executable.__init__(self)
        self.command = 'debchange'

    def __call__(self, build_info, message):
        args = {
                'distribution': None,
                'newversion': None,
                'force_distribution': True,
                'force_bad_version': True
        }
        args['distribution'] = build_info.distro['distro']
        args['newversion']   = build_info.deb_version + '-1'
        cmd_args = self.create_args(args)
        logging.info('Pushing mark into changelog with version %s',
                args['newversion']
        )
        self.execute(cmd_args, last = message, wait_command = True)
        try:
            self.check_errcode()
        except ExecutableError as e:
            logging.error(repr(e))
            logging.error('Aborting')
            exit(1)
        logging.info('Finished')

class DPKG(Executable):
    def __init__(self):
        self.command = 'dpkg'

    def append_subcommand(self, cmd):
        return cmd + '-' + self.subcommand

    def build_source(self, name):
        self.subcommand = 'source'
        args = { 'b': True, }
        cmd_args = self.create_args(args)
        logging.info('Creating source package for %s', name)
        self.execute(cmd_args, last = name, wait_command = True)
        try:
            self.check_errcode()
        except ExecutableError as e:
            logging.error(repr(e))
            logging.error('Aborting')
            exit(1)
        logging.info('Finished')


class Debsign(Executable):
    def __init__(self):
        Executable.__init__(self)
        self.command = 'debsign'

    def sign_product(self, sign_id, changes_file):
        args = ' -m %s %s' % (sign_id, changes_file)
        self.execute(args, wait_command=True)
        try:
            self.check_errcode()
        except ExecutableError as e:
            logging.error(repr(e))
            logging.error('Aborting')
            exit(1)
        logging.info('Finished')
        self.subcommand = None

class Reprepro(Executable):
    def __init__(self):
        Executable.__init__(self)
        self.command = 'reprepro'

    def import_product(self, repo_path, distribution, changes_file):
        args = ' -b %s include %s %s' % (repo_path, distribution, changes_file)
        self.execute(args, wait_command=True)
        try:
            self.check_errcode()
        except ExecutableError as e:
            logging.error(repr(e))
            logging.error('Aborting')
            exit(1)
        logging.info('Finished')
        self.subcommand = None

