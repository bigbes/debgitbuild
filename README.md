De Builder
========
Utils to easy way build, sign and export Debian packages

Overview
--------
One day there was a need to build a DEB package from the python or command line. Key features:
* Create source tarball from git repository
* Build source package
* Build debian package
* Sign it with keyring
* Export package to repository

Install
---------------
```bash
pip install debuilder
```

Example: Python
---------------
```python
from debuilder import BuildConfig
# ...

distro_settings = {
    "distro": "wheezy",
    "os": "debian",
    "mirror": "http://mirror.yandex.ru/debian/",
    "arches": ["i386", "amd64"],
    "keyring": "/usr/share/keyrings/debian-keyring.gpg"
}
image = 'base_wheezy_i386.tgz'
output = '/home/admin/result/'
repository = '/home/admin/repo/'
arch = 'i386'
product_settings = {
    "branch": "master",
    "product": "my_awesome_project",
    "sign_id": "my_awesome_key",
    "sign_email": "foo@bar.com",
    "git": "git://github.com/somewhere/my_awesome_project.git"
}

build_config = BuildConfig(
    product_settings, distro_settings, arch,
    image=image, output=output
)
build_config.prepare_sourcecode()
build_config.build_sourcecode()
build_config.import_package(repository)
```

Example: Command line
---------------
```bash
./main.py -A i386 -D wheezy -P my_awesome_product -i base_wheezy_i386.tgz -o /home/admin/result/ -r /home/admin/repo/
```

Enjoy!