# -*- coding: utf-8 -*-
"""ASUS SWAGGER API Difference

Show difference between Old and New SWAGGER documents

Example:
        $ python swagger_diff.py -o OLD_YAML -n NEW_YAML

usage: swagger_diff.py [-h] [-p PATH_YAML] [-n NEW_YAML] [-o OLD_YAML]

optional arguments:
  -h, --help            show this help message and exit
  -p PATH_YAML, --path_yaml PATH_YAML
                        where yaml file store, (default: ../yaml)

  -n NEW_YAML, --new_yaml NEW_YAML
                        latest yaml file name, (default:
                        api_v2_swagger_v5.0.0_staging.yaml)
  -o OLD_YAML, --old_yaml OLD_YAML
                        previous yaml file name, (default:
                        api_v2_swagger_v5.1.1_staging.yaml)


"""
from __future__ import print_function
from os import sys, path, strerror
import argparse
import yaml
import errno

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


def doAnaly(fn_new = "../yaml/GOC_PaaS_Admin_User_API_Swagger_v5.1.2.yaml",
        fn_old = "../yaml/api_v2_swagger_v5.1.1_staging.yaml" ):
    """doing difference between fn_old and fn_new in YAML format
       analysis only do Paths entries and its http verbs.

    Args:
        fn_old (str): OLD_YAML file path
        fn_new (str): NEW_YAML file path

    """

    swg_old = yaml.load(open(fn_old, 'r').read())
    swg_new = yaml.load(open(fn_new, 'r').read())

    swg_old_fns = set(swg_old['paths'].keys())
    swg_new_fns = set(swg_new['paths'].keys())

    print ("==="*5, "Old diff New", "==="*5)
    odn =  swg_old_fns.difference( swg_new_fns )
    if len(odn)==0:
        print (">>>> no change <<<<<");
    else:
        print ("API URL |\t HTTP Verb |\t Summary |");
        print ("| -- | -- | -- | ")
        for x in odn:
            for y in swg_old['paths'][x]:
                print ("|", " |\t".join( [x, y, swg_old['paths'][x][y]['summary']]))
    print ()
    print ("==="*5, "New diff Old", "==="*5)
    ndo = swg_new_fns.difference( swg_old_fns )
    if len(ndo)==0:
        print (">>>> no change <<<<<");
    else:
        print ("API URL |\t HTTP Verb |\t Summary |");
        print ("| -- | -- | -- | ")
        for x in ndo:
            for y in swg_new['paths'][x]:
                print ("|", " |\t".join( [x, y, swg_new['paths'][x][y]['summary']]))


if __name__  ==  '__main__':
	parser = argparse.ArgumentParser(description='Show difference between Old and New SWAGGER documents')
        parser.add_argument('-p', "--path_yaml",
                default="../yaml",
                help='where yaml file store, (default: %(default)s)')

        group = parser.add_argument_group()
        group.add_argument('-n', "--new_yaml",
                default="api_v2_swagger_v5.0.0_staging.yaml",
                help='latest yaml file name, (default: %(default)s)')
        group.add_argument('-o', "--old_yaml",
                default="api_v2_swagger_v5.1.1_staging.yaml",
                help='previous yaml file name, (default: %(default)s)')

	args = parser.parse_args()


        p_yaml = args.path_yaml
        n_yaml = "{0}/{1}".format(p_yaml, args.new_yaml)
        o_yaml = "{0}/{1}".format(p_yaml, args.old_yaml)

        if not path.isfile( o_yaml ):
            raise OSError, "{0} file not found".format(o_yaml)
        if not path.isfile( n_yaml ):
            raise OSError, "{0} file not found".format(n_yaml)

        doAnaly( fn_old = n_yaml, fn_new = o_yaml )

