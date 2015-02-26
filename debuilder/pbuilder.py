import os
import logging
from debuilder.executable import Executable, ExecutableError


class PBuilder(Executable):
    """
    DEB packages builder wrapper class
    1. create/update build images
    2. build Debian packages
    3. sign Debian packages
    """
    def __init__(self):
        super(PBuilder, self).__init__()
        self.command = 'sudo pbuilder'

    def create_basebox(self, build_config):
        """
        Load data from repository and create build image for given configuration
        """
        self.subcommand = 'create'
        args = dict(
            basetgz=None,
            mirror=None,
            distribution=None,
            architecture=None,
            debootstrapopts=None,
            autocleanaptcache=True,
            override_config=True,
            buildplace=None,
            components=None,
        )

        args['basetgz'] = build_config.image
        args['mirror'] = build_config.distro['mirror']
        args['distribution'] = build_config.distro['distro']
        args['architecture'] = build_config.arch
        args['buildplace'] = build_config.builddir
        args['components'] = "main"
        args['debootstrapopts'] = ['--variant=buildd']
        if 'keyring' in build_config.distro:
            args['debootstrapopts'].append(' --keyring=' + build_config.distro['keyring'])

        cmd_args = self.create_args(args)
        logging.info(
            'Creating basebox - %s:%s into %s',
            args['distribution'],
            args['architecture'],
            args['basetgz']
        )
        self.execute(cmd_args, wait_command=True)
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
        """
        Update existing build image for given configuration
        """
        self.subcommand = 'update'
        args = dict(
            basetgz=None,
            distribution=None,
            architecture=None,
            autocleanaptcache=True,
        )
        args['basetgz'] = build_config.image
        args['distribution'] = build_config.distro['distro']
        args['architecture'] = build_config.arch
        cmd_args = self.create_args(args)
        logging.info(
            'Updating basebox - %s:%s - %s',
            args['distribution'],
            args['architecture'],
            args['basetgz']
        )
        self.execute(cmd_args, wait_command=True)
        try:
            self.check_errcode()
        except ExecutableError as e:
            logging.error(repr(e))
            logging.error('Aborting')
            logging.error('Failed to update - deleting basebox %s', args['basetgz'])
            os.remove(args['basetgz'])
            exit(1)
        logging.info('Finished')
        self.subcommand = None

    def build_product(self, build_config):
        """
        Create Debian package from scratch for given configuration
        """
        self.subcommand = 'build'
        if build_config.dsc is None:
            logging.error('There\'s no dsc file defined now')
            logging.error('Aborting')
            exit(1)
        args = dict(
            basetgz=None,
            architecture=None,
            buildresult=None,
            buildplace=None,
            autocleanaptcache=True,
        )
        args['basetgz'] = build_config.image
        args['architecture'] = build_config.arch
        args['buildresult'] = build_config.resultdir
        args['buildplace'] = build_config.builddir
        cmd_args = self.create_args(args)
        logging.info(
            'Building product %s:%s on %s into %s',
            build_config.distro['distro'],
            args['architecture'],
            args['basetgz'],
            args['buildresult']
        )
        self.execute(cmd_args, last=build_config.dsc, wait_command=True)
        try:
            self.check_errcode()
        except ExecutableError as e:
            logging.error(repr(e))
            logging.error('Aborting')
            exit(1)
        logging.info('Finished')
        self.subcommand = None

    def sign_product(self, sign_id, changes_file):
        """
        Sign debian packages changes file(path) with given keyring name
        """
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