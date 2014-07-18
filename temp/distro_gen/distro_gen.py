#!/usr/bin/env python
f = """---
distro: {distro}
os: {os}
mirror: http://mirror.yandex.ru/{os}/
arches: [i386, amd64]
keyring: {keyring}
..."""

import subprocess


release = subprocess.check_output(['lsb_release', '-sc'])
arch    = subprocess.check_output(['uname', '-p'])
arch    = 'amd64' if arch == 'x86_64' else arch
os      = subprocess.check_output(['lsb_release', '-si']).lower()

keyring = {
    'debian': '/usr/share/keyrings/debian-keyring.gpg',
    'ubuntu': '/usr/share/keyrnigs/ubuntu-master-keyring.gpg'
}
if os == 'ubuntu':
    keyring['ubuntu'] = '/etc/apt/trusted.gpg'

import yaml
import os
a = yaml.load(open('distro_gen.yml').read())
try:
    os.mkdir('temp')
except:
    pass
for k in a:
    for arch in ['i386', 'amd64']:
        for release in a[k]:
            open(os.path.join('temp', '%s') % (release), 'w').write(f.format(os = k, distro = release, keyring = keyring[k]))


