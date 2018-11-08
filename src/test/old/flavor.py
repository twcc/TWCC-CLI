from __future__ import print_function
import unittest
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from twcc.twcc import TWCC
from twcc.acls import acls
from twcc.util import *

class ServiceTest(unittest.TestCase):
    def setUp(self):
        self.fn_twcc_yaml = '../yaml/NCHC_API-Test_env.yaml'
        self.twcc = TWCC(self.fn_twcc_yaml, debug = True)

        self.api_key = "sys"

        keyname = "twc1234"
        self.mydict = {"flavors": keyname}
        self.mydata = {"name": keyname}

        site = acls(self.api_key)
        self.site_tags = site.getSites()
        self.yaml_keys = self.twcc.twcc_conf['stage']["keys"].keys()

    def test_connect(self):
        self.assertTrue(self.twcc.try_alive())

    def test_flavor_list(self):
        for site in self.site_tags:
            print("="*5, site, "="*5)
            res = self.get_flavor_list(site_tag=site)
            pp(res=res)

    def _test_flavor_create(self):
        y = 'sys'
        for x in self.site_tags:
            self.flavor_create(x, y, 'txt')
            res = self.flavor_get(x, y, 'txt')
            self.assertEqual(res['name'], self.mydict['flavors'])

    def _test_key_delete(self):
        for x in self.site_tags:
            for y in self.yaml_keys:
                self.flavor_delete(x, y, 'txt');
                res = self.flavor_get(x, y, 'json')
                self.assertIn('error', res)

    def get_flavor_list(self,
            site_tag = 1,
            key_tag = 'sys',
            res_format = 'json'):

        return self.twcc.doAPI(
            site_sn = site_tag,
            key_tag = key_tag,
            func = "flavors",
            http = 'get',
            res_type = 'json')

    def flavor_delete(self,
            site_tag = 1,
            key_tag = 'sys',
            res_format = 'json'):

        return self.twcc.doAPI(
            site_sn = site_tag,
            key_tag = key_tag,
            func = "flavors",
            url_dict = self.mydict,
            http = 'delete',
            res_type = 'txt')

    def flavor_get(self,
            site_tag = 1,
            key_tag = 'sys',
            res_format = 'json'):

        return self.twcc.doAPI(
            site_sn = site_tag,
            key_tag = key_tag,
            func = "flavors",
            url_dict = self.mydict,
            http = 'get',
            res_type = 'json')

    def flavor_create(self,
            site_tag = 1,
            key_tag = 'sys',
            res_format = 'json'):

        return self.twcc.doAPI(
            site_sn = site_tag,
            key_tag = key_tag,
            func = "flavors",
            data_dict = self.mydata,
            http = 'post',
            res_type = res_format)


if __name__  ==  '__main__':
    unittest.main()
