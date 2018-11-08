from __future__ import print_function
import unittest
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from twcc.twcc import TWCC
_debug_mode_ = True

class ServiceTest(unittest.TestCase):
    def setUp(self):
        import yaml, time
        self.func = 'projects'

        self.fn_twcc_yaml = '../yaml/NCHC_API-Test_env.yaml'
        self.fn_swagger = "../yaml/apis_v2_swagger_v4.0_asus.yaml"


        self.swagger = yaml.load(open(self.fn_swagger, 'r').read())
        self.twcc = TWCC(self.fn_twcc_yaml, "http://"+self.swagger['host'], debug = _debug_mode_)

        keyname = "twc{0}".format(int(time.time()))

        self.mydict = {"projects": keyname}
        self.mydata = {"name": keyname}

        self.site_tags = range(7)
        self.yaml_keys = self.twcc.twcc_conf['stage']["keys"].keys()

    def test_connect(self):
        print (self.twcc)

    def _test_list(self):
        import re
        for x in [1]:
            #for y in self.yaml_keys:
            for y in ['sys']:
                res = self.projects_list(site_tag = x, key_tag = y)
                print ("Site: %s, Role: %s"%(self.getPFName(x), y) )
                print (res)
                print ("\n")

                for ele in res:
                    if re.search("twc\d+", ele['name']):
                        self.mydict = {"projects": ele['id']}
                        res = self.project_get(site_tag = 1, key_tag = 'sys')
                        print ("project info:")
                        print (res)
                        #res_del = self.project_del(site_tag = 1, key_tag = 'sys', res_format='txt')
                        #print ("DEL:")
                        #print (res_del)
                pass

    def test_create(self):

        print ("Site: %s, Role: %s"%(self.getPFName(1), 'sys') )
        print (" [create]")
        res = self.projects_create(site_tag = 1, key_tag = 'sys')
        #print ("get project id: %s"%res['id'])


        #print (" [delete]")
        #print (res)
        #print ("\n")
        pass

    def get_project_id(self,
            site_tag = 1,
            key_tag = 'sys',
            project_name = ""):

        res = self.projects_list(site_tag = site_tag, key_tag = key_tag)
        for ele in res:
            if ele['name'] == project_name:
                return ele
        else:
            print ("not found project name")
            return None

    def projects_create(self,
            site_tag = 1,
            key_tag = 'sys',
            res_format = 'json'):

        import time, random

        time_start = time.time()

        res = self.twcc.doAPI(
            site_sn = site_tag,
            key_tag = key_tag,
            func = self.func,
            data_dict = self.mydata,
            http = 'post',
            res_type = res_format)

        print (res)
        isCreating = True
        self.mydict = {"projects": res['id']}
        while isCreating:
            res = self.project_get(site_tag = 1, key_tag = 'sys')
            if 'status' in res:
                print (res['status'])
            else:
                print (res)
            if 'status' in res and res['status'] == 'Ready':
                isCreating = False
            time.sleep(random.randint(10,30))

        print ("Consuming time: {0}s".format( (time.time()-time_start) ) )

    def project_del(self,
            site_tag = 1,
            key_tag = 'sys',
            res_format = 'json'):

        return self.twcc.doAPI(
            site_sn = site_tag,
            key_tag = key_tag,
            func = self.func,
            url_dict = self.mydict,
            http = 'delete',
            res_type = res_format)

    def project_get(self,
            site_tag = 1,
            key_tag = 'sys',
            res_format = 'json'):

        return self.twcc.doAPI(
            site_sn = site_tag,
            key_tag = key_tag,
            func = self.func,
            url_dict = self.mydict,
            http = 'get',
            res_type = res_format)

    def projects_list(self,
            site_tag = 1,
            key_tag = 'usr1',
            res_format = 'json'):

        return self.twcc.doAPI(
            site_sn = site_tag,
            key_tag = key_tag,
            func = self.func,
            http = 'get',
            res_type = 'json')

    def getPFName(self, x):
        return self.twcc.twcc_conf['stage']['platforms'][x]['name']


if __name__  ==  '__main__':
    unittest.main()
