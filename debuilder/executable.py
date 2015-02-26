import subprocess
import logging
import shlex
import os


class ExecutableError(Exception):
    """
    Main exception class
    """
    def __init__(self, message, code):
        super(ExecutableError, self).__init__(message)
        self.code = code

    def __repr__(self):
        return '%s with errcode %d' % (self.message, self.code)


class Executable(object):
    """
    Common shell command class
    """
    def __init__(self):
        self.command = None
        self.subcommand = None
        self._process = None
        self._output = None

    @staticmethod
    def create_args(mapping):
        cmd = ''
        for k, v in mapping.iteritems():
            lval = k.replace('_', '-')
            lval = (' --' if len(lval) != 1 else ' -') + lval
            if v and (v is not True) and isinstance(v, basestring):
                if len(shlex.split(v)) != 1:
                    v = repr(v)
                cmd += ' '.join([lval, v])
            elif isinstance(v, (list, tuple)):
                cmd += ' '.join([('%s %s' % (lval, k)) for k in v])
            else:
                cmd += lval
        return cmd

    @property
    def process(self):
        return self._process

    @process.setter
    def process(self, value):
        self._process = value

    def append_subcommand(self, cmd):
        return cmd + ' ' + self.subcommand

    def execute(self, args=None, last=None, wait_command=True, workdir=None):
        if not isinstance(self.command, basestring):
            raise ExecutableError('Command must be defined must be basestring', -1)
        cmd = self.command
        if self.subcommand is not None:
            if not isinstance(self.subcommand, basestring):
                raise ExecutableError('Subcommand must be subclass of basestring or None', -2)
            cmd = self.append_subcommand(cmd)
        if args is not None:
            if not isinstance(args, basestring):
                raise ExecutableError('Args must be subclass of basestring or None', -3)
            cmd += args
        if last is not None:
            if not isinstance(last, basestring):
                raise ExecutableError('Last must be subclass of basestring or None', -4)
            cmd += ' ' + last
        logging.info(cmd)
        self.process = subprocess.Popen(
            shlex.split(cmd),
            cwd=(workdir if workdir else os.getcwd()),
        )
        if wait_command:
            self.process.wait()
            return self.process.returncode

        return None

    def check_errcode(self):
        if self.process.poll() and self.process.returncode:
            raise ExecutableError(
                'Command failed with code %d' % self.process.returncode,
                self.process.returncode
            )
