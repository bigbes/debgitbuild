from debuilder.executable import Executable, ExecutableError

import os
import logging

class PBuilder(Executable):
    def __init__(self):
        Executable.__init__(self)
        self.command = 'sudo pbuilder'

    def create_basebox(self, build_config):
        self.subcommand = 'create'
        args = {
                'basetgz': None,
                'mirror': None,
                'distribution': None,
                'architecture': None,
                'debootstrapopts': None,
                'autocleanaptcache': True,
                'override_config': True,
                'buildplace': None,
                'components': None,
        }
        args['basetgz']      = build_config.image
        args['mirror']       = build_config.distro['mirror']
        args['distribution'] = build_config.distro['distro']
        args['architecture'] = build_config.arch
        args['buildplace']   = build_config.builddir
        args['components']   = "main"
        args['debootstrapopts'] = ['--variant=buildd']
        if 'keyring' in build_config.distro:
            args['debootstrapopts'].append(' --keyring=' + build_config.distro['keyring'])

        cmd_args = self.create_args(args)
        logging.info('Creating basebox - %s:%s into %s',
                args['distribution'],
                args['architecture'],
                args['basetgz']
        )
        self.execute(cmd_args, wait_command = True)
        try:
            self.check_errcode()
        except ExecutableError as e:
            logging.error(repr(e))
            logging.error('Aborting')
            os.remove(args['basetgz'])
            exit(1)
        logging.info('Finished')
        self.subcommand = None

    def update_basebox(self, build_config):
        self.subcommand = 'update'
        args = {
                'basetgz': None,
                'distribution': None,
                'architecture': None,
                # 'override_config': True, # no overwrite
                'autocleanaptcache': True,
        }
        args['basetgz']      = build_config.image
        args['distribution'] = build_config.distro['distro']
        args['architecture'] = build_config.arch
        cmd_args = self.create_args(args)
        logging.info('Updating basebox - %s:%s - %s',
                args['distribution'],
                args['architecture'],
                args['basetgz']
        )
        self.execute(cmd_args, wait_command = True)
        try:
            self.check_errcode()
        except ExecutableError as e:
            logging.error(repr(e))
            logging.error('Aborting')
            logging.error('Failed to update - deleting basebox %s',
                    args['basetgz']
            )
            os.remove(args['basetgz'])
            exit(1)
        logging.info('Finished')
        self.subcommand = None

    def build_product(self, build_config):
        self.subcommand = 'build'
        if build_config.dsc == None:
            logging.error('There\'s no dsc file defined now')
            logging.error('Aborting')
            exit(1)
        args = {
                'basetgz': None,
                'architecture': None,
                'buildresult': None,
                'buildplace': None,
                'autocleanaptcache': True,
#                'override_config': True,
        }
        args['basetgz']      = build_config.image
        args['architecture'] = build_config.arch
        args['buildresult']  = build_config.resultdir
        args['buildplace']   = build_config.builddir
        cmd_args = self.create_args(args)
        logging.info('Building product %s:%s on %s into %s',
                build_config.distro['distro'],
                args['architecture'],
                args['basetgz'],
                args['buildresult']
        )
        self.execute(cmd_args, last = build_config.dsc, wait_command = True)
        try:
            self.check_errcode()
        except ExecutableError as e:
            logging.error(repr(e))
            logging.error('Aborting')
            exit(1)
        logging.info('Finished')
        self.subcommand = None

    def sign_product(self, sign_id, changes_file):
        self.subcommand = 'debsign'
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