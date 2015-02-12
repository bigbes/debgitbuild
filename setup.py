import os
import sys
from setuptools import setup

requirements = [
    'PyYaml==3.10',
    'GitPython==0.3.6'
]


def long_description():
    return "Build debian packages easy with pbuilder"


setup(
    name='debuilder',
    version='0.3.1',
    description="Debian packages build tool",
    long_description=long_description(),
    url='https://github.com/bigbes/debgitbuild',
    download_url='https://github.com/bigbes/debgitbuild',
    author="Bigbes",
    author_email='bigbes@gmail.com',
    license='http://www.apache.org/licenses/LICENSE-2.0',
    packages=['debuilder'],
    install_requires=requirements,
    keywords = ['build', 'deb', 'packaging'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Utilities'
    ]
)
