from __future__ import print_function
import unittest
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from twcc.twcc import TWCC

class ServiceTest(unittest.TestCase):
    def setUp(self):
        import yaml
        self.fn_twcc_yaml = '../yaml/NCHC_API-Test_env.yaml'
        self.fn_swagger = "../yaml/apis_v2_swagger_v4.0_asus.yaml"


        self.swagger = yaml.load(open(self.fn_swagger, 'r').read())
        self.twcc = TWCC(self.fn_twcc_yaml, "http://"+self.swagger['host'], debug = False)

        keyname = "twc1234"
        self.mydict = {"keypairs": keyname}
        self.mydata = {"name": keyname}

        self.site_tags = range(7)
        self.yaml_keys = self.twcc.twcc_conf['stage']["keys"].keys()

    def test_connect(self):
        print (self.twcc)

    def test_list_solution(self):
        for x in self.site_tags:
            for y in self.yaml_keys:
                res = self.solution_list( site_sn = x, key_tag = y)
                print (x, y, res)

    def solution_list(self,
            site_tag = 1,
            key_tag = 'usr1',
            res_format = 'json'):

        return self.twcc.doAPI(
            site_sn = site_tag,
            key_tag = key_tag,
            func = "solutions",
            http = 'get',
            res_type = 'json')


if __name__  ==  '__main__':
    unittest.main()
