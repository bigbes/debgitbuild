#!/usr/bin/env python
import os
import sys
import yaml
import logging
import argparse

from debuilder import BuildConfig

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-D', '--distribution',
            type = str, default = '', dest = 'distro')
    parser.add_argument('-A', '--architecture',
            type = str, default = '', dest = 'arch')
    parser.add_argument('-P', '--product',
            type = str, default = '', dest = 'product')
    parser.add_argument('-v', '--verbose',
            action = 'count', default = False, dest = 'verbose')
    parser.add_argument('-i', '--image', type=str, default=None, dest='image')
    parser.add_argument('-o', '--output', type=str, default=None, dest='output')
    args = parser.parse_args()
    if not args.distro:
        logging.error('There\'s no distribution specified. Aborting.')
        exit(1)
    if not args.arch:
        logging.error('There\'s no architecture specified. Aborting.')
        exit(1)
    if not args.product:
        logging.error('There\'s no product specified. Aborting.')
    return args

def check_distro(distr):
    path_to = os.path.join('distro.available', distr)
    if not os.path.exists(path_to):
        logging.error('There\'s no distribution %s in "distro.available" directory. Aborting.' % distr)
        exit(1)
    yml = None
    try:
        yml = yaml.load(open(path_to).read())
    except yaml.YamlError:
        logging.error('Bad info in %s file. Aborting.' % path_to)
        exit(1)
    except IOError:
        logging.error('Error while opening file %s. Aborting.' % path_to)
        exit(1)
    return yml

def check_arch(dist_info, arch):
    if arch not in ['i386', 'amd64']:
        logging.error('Architecture must be one of i386 or amd64. Aborting.')
        exit(1)
    for k in dist_info['arches']:
        if k == arch:
            return True
    logging.error('Architecture %s not found in dist_info file. Aborting.' % arch)
    exit(1)

def check_product(product, arch):
    path_to = os.path.join('product.available', product)
    if not os.path.exists(path_to):
        logging.error('There\'s no product %s in "product.available" directory. Aborting.' % product)
        exit(1)
    yml = None
    try:
        yml = yaml.load(open(path_to).read())
    except yaml.YamlError:
        logging.error('Bad info in %s file. Aborting.' % path_to)
        exit(1)
    except IOError:
        logging.error('Error while opening file %s. Aborting.' % path_to)
        exit(1)
    return yml

def cd_to_script():
    path = os.path.dirname(sys.argv[0])
    if not path:
        path = '.'
    os.chdir(path)

def main():
    logging.basicConfig(level = logging.DEBUG)
    cd_to_script()
    args = parse_args()
    distro_settings = check_distro(args.distro)
    check_arch(distro_settings, args.arch)
    product_settings = check_product(args.product, args.arch)
    build_config = BuildConfig(
        product_settings, distro_settings, args.arch, 
        image=args.image, output=args.output
    )
    build_config.prepare_sourcecode()
    build_config.build_sourcecode()

exit(main())
