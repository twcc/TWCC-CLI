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

        self.site_tags = [1, 2]
        self.yaml_keys = self.twcc.twcc_conf['stage']["keys"].keys()

    def test_connect(self):
        print (self.twcc)

    def test_acls_g(self):
        res = self.twcc.doAPI(site_sn=0, key_tag='sys', func="acls-g", http='get', res_type = 'json')
        ans = [u'admin', u'slurm', u'goc', u'ceph', u'harbor', u'openstack', u'k8s']
        self.assertEqual(res.keys(), ans)

    def test_acls(self):
        res = self.twcc.doAPI(site_sn=0, key_tag='sys', func="acls", http='get', res_type = 'json')
        ans = [u'admin', u'slurm', u'goc', u'ceph', u'harbor', u'openstack', u'k8s']
        print (ans)
        self.assertEqual(res['total'], len(res['data']))

        pass


if __name__  ==  '__main__':
    unittest.main()
