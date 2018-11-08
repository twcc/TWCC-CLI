from __future__ import print_function
import unittest
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from twcc.clidriver import ServiceOperation

class ServiceTest(unittest.TestCase):
    def setUp(self):
        self.fn_twcc_yaml = '../yaml/NCHC_API-Test_env.yaml'
        self.twcc_api = ServiceOperation(self.fn_twcc_yaml, debug = False)

        self.site_tags = [1, 2]
        self.yaml_keys = self.twcc_api.twcc_conf['stage']["keys"].keys()

    def test_acls_g(self):
        res = self.twcc_api.doAPI(site_sn=0, key_tag='sys', func="acls-g", http='get', res_type = 'json')
        ans = [u'admin', u'slurm', u'goc', u'ceph', u'harbor', u'openstack', u'k8s']
        self.assertEqual(res.keys(), ans)

    def test_acls(self):
        res = self.twcc_api.doAPI(site_sn=0, key_tag='sys', func="acls", http='get', res_type = 'json')
        ans = [u'admin', u'slurm', u'goc', u'ceph', u'harbor', u'openstack', u'k8s']
        self.assertEqual(res['total'], len(res['data']))


if __name__  ==  '__main__':
    unittest.main()
