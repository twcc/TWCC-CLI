from __future__ import print_function
import unittest, time, re
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from twcc.twcc import TWCC
from twcc.util import *


getYN = lambda x: "Y" if x else "N"

class ServiceTest(unittest.TestCase):
    def setUp(self):
        import yaml
        self.fn_twcc_yaml = '../yaml/NCHC_API-Test_env.yaml'
        self.fn_swagger = "../yaml/apis_v2_swagger_v4.0_asus.yaml"


        self.swagger = yaml.load(open(self.fn_swagger, 'r').read())
        self.twcc = TWCC(self.fn_twcc_yaml, "http://"+self.swagger['host'], debug = False)

        self.site_tags = range(7)
        self.yaml_keys = self.twcc.twcc_conf['stage']["keys"].keys()

    def test_connect(self):
        self.assertTrue(self.twcc.try_alive())

    def test_create(self):

        # define solution name
        t_sol_name = "aug_test_{0}".format(time.time())

        # 1. create solution
        res = self.solution_create(sol_name = t_sol_name,
                site_tag = 6, key_tag = 'sys', res_format = 'json')

        self.assertEqual(res['name'], t_sol_name)

        # 2. test get solution detail
        sol_res = self.get_solution_detail( site_tag = 6,
                key_tag = 'sys',
                res_format='json',
                solution_id=res['id'])

        self.assertEqual(sol_res['name'], t_sol_name)

        # 3. test delete solution detail
        self.solution_delete(sol_id = sol_res['id'],
                site_tag = 6, key_tag = 'sys', res_format = 'txt')

        # 4. try get solution detail again
        sol_res = self.get_solution_detail( site_tag = 6,
                key_tag = 'sys',
                res_format='json',
                solution_id=sol_res['id'])
        self.assertEqual(sol_res['detail'], u'Solution not found')

        self.show_solution_list(False)

    def show_solution_list(self, show_pub_only=True):
        res = self.solution_list( site_tag = 6, key_tag = 'sys', res_format='json')
        buf = []
        print ()
        yres = [ ele for ele in res if ele['is_public']==True]
        print ("="*5, "public solutions list", "count={0}".format(len(yres)), "="*5)
        for (idx, sol) in zip(range(1, len(yres)+1), yres):
            buf.append("{num:02d}. :{is_tanet}|{is_pub}|{mid:03d}| [{name:25}] {ctime} {desc}".format(num=idx,
                ctime=sol['create_time'], name=sol['name'], desc=sol['desc'], mid=sol['id'],
                is_tanet=getYN(sol['is_tenant_admin_only']), is_pub=getYN(sol['is_public']) ))
            sol_res = self.get_solution_detail( site_tag = 6,
                key_tag = 'sys',
                res_format='json',
                solution_id=sol['id'])
        print ("\n".join(buf))

        if show_pub_only:
            return 1
        buf = []
        xres = [ ele for ele in res if not ele['is_public']==True]
        print ("="*5, "NON-public solutions list", "count={0}".format(len(xres)), "="*5)
        for (idx, sol) in zip(range(1, len(xres)), xres):
            buf.append("{num:02d}. :{is_tanet}|{is_pub}|{mid:03d}| [{name:25}] {ctime} {desc}".format(num=idx,
                ctime=sol['create_time'], name=sol['name'], desc=sol['desc'], mid=sol['id'],
                is_tanet=getYN(sol['is_tenant_admin_only']), is_pub=getYN(sol['is_public']) ))
            sol_res = self.get_solution_detail( site_tag = 6,
                key_tag = 'sys',
                res_format='json',
                solution_id=sol['id'])
        print ("\n".join(buf))

    def solution_create(self,
            sol_name = "TMP",
            site_tag = 1,
            key_tag = 'usr1',
            res_format = 'json'):

        return self.twcc.doAPI(
            site_sn = site_tag,
            key_tag = key_tag,
            func = "solutions",
            data_dict= {"name": sol_name},
            http = 'post',
            res_type = res_format)

    def solution_delete(self,
            sol_id = "TMP",
            site_tag = 1,
            key_tag = 'usr1',
            res_format = 'json'):

        return self.twcc.doAPI(
            site_sn = site_tag,
            key_tag = key_tag,
            func = "solutions",
            url_dict= {"solutions": sol_id},
            http = 'delete',
            res_type = res_format)


    def get_solution_detail(self,
            solution_id = 0,
            site_tag = 1,
            key_tag = 'usr1',
            res_format = 'json'):

        self.mydict = {"solutions": solution_id}

        return self.twcc.doAPI(
            site_sn = site_tag,
            key_tag = key_tag,
            func = "solutions",
            url_dict= self.mydict,
            http = 'get',
            res_type = res_format)

    def solution_list(self,
            site_tag = 1,
            key_tag = 'usr1',
            res_format = 'json'):

        return self.twcc.doAPI(
            site_sn = site_tag,
            key_tag = key_tag,
            func = "solutions",
            http = 'get',
            res_type = res_format)


if __name__  ==  '__main__':
    unittest.main()
