# -*- coding: utf-8 -*-
from __future__ import print_function
import re
import json
import os
import yaml
from twccli.twcc.session import Session2
from twccli.twcc.services.generic import GpuService, CpuService, GenericService
from twccli.twcc.services.base import projects, Flavors, iservice
from twccli.twcc.util import pp, isNone, table_layout, isDebug, strShorten, _debug, get_flavor_string


def chkPortPair(x):
    return True if type(x) == type({}) and len(
        set(['exposed', 'inner']).intersection(set(x.keys()))) == 2 else False


class GpuSolutions(GenericService):
    """ This Class is for solutions api call
    """

    def __init__(self):
        """ constractor for this solutions class

        Args:
            api_key_tag (str): see YAML for detail
        """
        GenericService.__init__(self)
        # current working information
        self._func_ = "solutions"
        self._csite_ = "goc"

    def list(self):
        self.ext_get = {'project': self._project_id, 'category': 'container'}
        return super(GpuSolutions, self).list()


class GpuSite(GpuService):

    def __init__(self, debug=False):
        GpuService.__init__(self)

        self._func_ = "sites"
        self._csite_ = Session2._getClusterName("CNTR")
        self._cache_sol_ = {}

    @staticmethod
    def getGpuList():
        # @todo, python 3 is not good with dict key object
        gpu_list = [
            ('0', '0 GPU + 01 cores + 008GB memory'),  # twcc test only
            ('1', '1 GPU + 04 cores + 090GB memory'),
            ('2', '2 GPU + 08 cores + 180GB memory'),
            ('4', '4 GPU + 16 cores + 360GB memory'),
            ('8', '8 GPU + 32 cores + 720GB memory'),
            ('1m', '1 GPU + 04 cores + 060GB memory + 030GB share memory'),
            ('2m', '2 GPU + 08 cores + 120GB memory + 060GB share memory'),
            ('4m', '4 GPU + 16 cores + 240GB memory + 120GB share memory'),
            ('8m', '8 GPU + 32 cores + 480GB memory + 240GB share memory'),
            ('1p', '1 GPU + 9 cores + 042GB memory'),
            ('2p', '2 GPU + 18 cores + 084GB memory'),
            ('4p', '4 GPU + 36 cores + 168GB memory'),
            ('1pm', '1 GPU + 9 cores + 028GB memory + 014GB share memory'),
            ('2pm', '2 GPU + 18 cores + 056GB memory + 028GB share memory'),
            ('4pm', '4 GPU + 36 cores + 112GB memory + 056GB share memory')
        ]

        return dict(gpu_list)

    @staticmethod
    def getSolList(mtype='dict', name_only=False, reverse=False):
        sol_list = [
            (4, "TensorFlow"),
            (9, "PyTorch"),
            (10, "Caffe"),
            (13, "CNTK"),
            (16, "CUDA"),
            (19, "MXNet"),
            (24, "Caffe2"),
            # (29, "TensorRT"), # not avalible for now
            # (35, "TensorRT_Server"), # not avalible for now
            (42, "Theano"),
            (49, "Torch"),
            (52, "DIGITS"),
        ]
        # (339, "AIFS"),]

        ext_cntr_sol = set([
            'Preemptive GPU', 'Custom Image', u'Preemptive GPU(Custom Image)'
        ])
        sols = GpuSolutions().list()
        
        for ele in sols:
            if ele['name'] in ext_cntr_sol:
                sol_list.append((ele['id'], ele['name']))

        if reverse:
            sol_list = [(y, x) for (x, y) in sol_list]

        if name_only and mtype == 'list':
            sol_list = [y for (x, y) in sol_list]

        if mtype == 'list':
            return sol_list
        elif mtype == 'dict' and not name_only:
            return dict(sol_list)

    def getCommitList(self, mtype='list'):
        self.func = 'image_commit'

        return self._do_api()

    @staticmethod
    def getGpuDefaultHeader(flavor, sol_name, gpus="1"):
        gpu_list = GpuSite.getGpuList()

        if not gpus in gpu_list.keys():
            raise ValueError("GPU number '{0}' is not valid.".format(gpus))

        gpu_default = {
            'command': "whoami; sleep 600;",
            'flavor': gpu_list[gpus],
            'replica': '1',
        }
        return dict([("x-extra-property-%s" % (x), gpu_default[x])
                     for x in gpu_default.keys()])

    @staticmethod
    def mkS3MountFormat(alist):
        if len(alist) > 0:
            return json.dumps([{
                "name": x,
                "mountpath": "/mnt/s3/%s" % (x)
            } for x in alist])
        else:
            return "[]"

    @staticmethod
    def getIpBindAttr(port_mapping, pod_name="_UNDEF_"):
        default_assign_ip = {
            "action": "associateIP",
            "pod_name": pod_name,
            "ports": []
        }
        if len(port_mapping) > 0:
            for each_port in port_mapping:
                if chkPortPair(each_port):
                    port_map = {
                        "targetPort": each_port['inner'],
                        "port": each_port['exposed']
                    }
                    default_assign_ip['ports'].append(port_map)
                else:
                    raise ValueError(
                        "Port Mapping Error {0}".format(port_mapping))
            return default_assign_ip

    def getAvblS3(self, mtype='list'):
        res = self.list_solution(4, isShow=False)
        buckets = [x['name'] for x in res['bucket']]
        if mtype == 'list':
            return buckets
        elif mtype == 'dict':
            return dict([(x, "/mnt/s3/%s" % (x)) for x in buckets])

    # @todo, this is duplicated with L419
    def getIsrvFlavors(self, name_or_id="flavor_id"):
        pass

    @staticmethod
    def getGpuListOnline():
        gpu_tag2spec = {
            '1': '1 GPU + 04 cores + 090GB memory',
            '1': '1 GPU + 04 cores + 090GB memory',
            '1': '1 GPU + 04 cores + 090GB memory',
            '1': '1 GPU + 04 cores + 090GB memory',
        }

        return gpu_tag2spec

    def getAvblFlv(self, sol_id):

        self.proj = projects()
        self.proj._csite_ = self._csite_

        ans = self.proj.getProjectSolution(self._project_id, sol_id)
        return ans['site_extra_prop']['flavor']

    def getAvblImg(self, sol_id, sol_name, latest_first=True):
        if sol_id:
            res = self.list_solution(sol_id, isShow=False)
            if latest_first:
                return sorted(list(set(res['image'])), reverse=True)
            else:
                return res['image']
        else:
            raise ValueError(
                "Solution name:'{0}' is not available.".format(sol_name))

    def list(self, is_all=False):
        if is_all:
            self.ext_get = {'project': self._project_id, "all_users": 1}
        elif not self.url_dic == None and self.url_dic['container'] == "":
            pass
        else:
            self.ext_get = {'project': self._project_id}
        return self._do_api()

    def create(self, name, sol_id, extra_prop):

        # @todo change this
        extra_prop['x-extra-property-gpfs01-mount-path'] = '/work/{}'.format(
            self.twcc_session.twcc_username)
        extra_prop['x-extra-property-gpfs02-mount-path'] = '/home/{}'.format(
            self.twcc_session.twcc_username)

        self.twcc.header_extra = extra_prop
        self.http_verb = 'post'
        self.data_dic = {
            "name": name,
            "desc": 'TWCC-Cli created GPU container',
            "project": self._project_id,
            "solution": sol_id
        }
        return self._do_api()

    def update(self, data_dic):
        self.http_verb = 'put'
        self.res_type = 'txt'
        self.data_dic = data_dic
        self.ext_get = None
        return self._do_api()

    def delete(self, site_id):
        self.http_verb = 'delete'
        self.res_type = 'txt'
        self.url_dic = {"sites": site_id}
        return self._do_api()

    def patch_desc(self, site_id, desc):
        self.http_verb = 'patch'
        self.url_dic = {'sites': site_id}
        self.data_dic = {"desc": desc}
        return self._do_api()

    def patch_keep(self, site_id, keep):
        self.http_verb = 'patch'
        self.url_dic = {'sites': site_id}
        self.data_dic = {"termination_protection": keep}
        return self._do_api()

    def list_solution(self, sol_id, isShow=True):
        if sol_id in self._cache_sol_:
            ans = self._cache_sol_[sol_id]
        else:
            self._do_list_solution(sol_id)
            ans = self._cache_sol_[sol_id]

        if isShow:
            #table_layout(" site_extra_prop for %s "%sol_id, [ans], list(ans.keys()))
            print(ans)
        elif not isShow:
            return ans

    def _do_list_solution(self, sol_id):
        self.proj = projects()
        self.proj._csite_ = self._csite_

        ans = self.proj.getProjectSolution(self._project_id, sol_id)
        table_info = ans['site_extra_prop']
        self._cache_sol_[sol_id] = table_info

    def getFlavors(self):
        flv = Flavors(self._csite_)
        return dict([(x['id'], x) for x in flv.list()])

    def getConnInfo(self, site_id, ssh_info=False):
        info_gen = self.queryById(site_id)

        info_detail = self.getDetail(site_id)
        usr_name = Session2._whoami()['username']
        info_pod_port = [
            x for x in info_detail['Pod'][0]['container'][0]['ports']
        ]
        info_pod_port2name = {}
        for each_pod_port in info_pod_port:
            info_pod_port2name[each_pod_port['port']] = each_pod_port['name']
        info_service = [x for x in info_detail['Service'][0]['ports']]
        if not ssh_info:
            # don't show node port
            ans = [
                dict([(y, x[y]) for y in x if not y == 'node_port'])
                for x in info_service
            ]
            for eachans in ans:
                if eachans['target_port'] in info_pod_port2name:
                    eachans['name'] = info_pod_port2name[
                        eachans['target_port']]
            return ans
        else:
            info_service = [
                x['port'] for x in info_detail['Service'][0]['ports']
                if x['target_port'] == 22
            ][0]
            info_pub_ip = info_detail['Service'][0]['public_ip'][0]
            return "{}@{} -p {}".format(usr_name, info_pub_ip, info_service)

    def isStable(self, site_id):
        site_info = self.queryById(site_id)
        return site_info['status'] == "Ready" or site_info['status'] == "Error"

    def getDetail(self, site_id):
        self.url_dic = {"sites": site_id, 'container': ""}
        self.http_verb = 'get'
        self.res_type = 'json'
        return self.list()

    def getPodName(self, site_id):
        detail = self.getDetail(site_id)
        if 'Pod' in detail and len(
                detail['Pod']
        ) == 1 and detail['Pod'][0]['status'] == 'running':
            return detail['Pod'][0]['name']

    def exposedPort(self, site_id, port_id):
        pod_name = self.getPodName(site_id)
        bindAttr = {
            "action": "associateIP",
            "pod_name": pod_name,
            "ports": [{
                'targetPort': int(port_id)
            }]
        }
        self.url_dic = {"sites": site_id, 'container/action': ""}
        self.update(bindAttr)

    def unbindPort(self, site_id, port_id):
        pod_name = self.getPodName(site_id)
        unbindAttr = {
            "action": "disassociateIP",
            "pod_name": pod_name,
            "ports": [{
                'targetPort': int(port_id)
            }]
        }
        self.url_dic = {"sites": site_id, 'container/action': ""}
        self.update(unbindAttr)

    def getLog(self, site_id):
        detail = self.getDetail(site_id)
        pod_name = detail['Pod'][0]['name']
        cntr_name = detail['Pod'][0]['container'][0]['name']
        self.ext_get = {"pod_name": pod_name, "container_name": cntr_name}
        self.url_dic = {"sites": site_id, 'container/logs': ""}
        self.http_verb = 'get'
        self.res_type = 'json'
        return self._do_api()

    def getJpnbToken(self, site_id):
        log_txt = self.getLog(site_id)
        re_comp = re.findall(r'https:\/\/(?P<ccs_host_name>.+):8888\/\?token=',
                             "\n".join(log_txt), re.M)
        if len(re_comp) > 0:
            import hashlib
            if type(re_comp[0]) == str:
                return hashlib.md5(re_comp[0].encode('utf8')).hexdigest()
            else:
                return hashlib.md5(re_comp[0].decode()).hexdigest()


class VcsSite(CpuService):

    def __init__(self):

        CpuService.__init__(self)

        self._func_ = "sites"
        self._csite_ = Session2._getClusterName("VCS")

    def list(self, isAll=False):
        if isAll:
            self.ext_get = {
                'project': self._project_id,
                "sol_categ": "os",
                "all_users": 1
            }
        else:
            self.ext_get = {'project': self._project_id}

        return self._do_api()

    def list_itype(self, isAll=False):
        self._csite_ = Session2._getClusterName("goc")
        print(self._csite_)
        self._func_ = "solutions"
        self.ext_get = {"category": "os", 'project': self._project_id, }
        result = self._do_api()
        self._func_ = "sites"
        self._csite_ = Session2._getClusterName("VCS")
        return result

    def stop(self, site_id):
        self.data_dic = {"status": "shelve"}
        self.url_dic = {'sites': site_id, 'action': ""}
        self.http_verb = 'put'
        return self._do_api()

    def start(self, site_id):
        self.data_dic = {"status": "unshelve"}
        self.url_dic = {'sites': site_id, 'action': ""}
        self.http_verb = 'put'
        return self._do_api()

    def reboot(self, site_id):
        self.data_dic = {"status": "reboot"}
        self.url_dic = {'sites': site_id, 'action': ""}
        self.http_verb = 'put'
        return self._do_api()

    @staticmethod
    def getSolList(mtype='list', name_only=False, reverse=False):
        """ This function is out of date!
        """

        return None

    def _do_list_solution(self, sol_id):
        self.proj = projects()
        self.proj._csite_ = self._csite_
        getProjectSolution = self.proj.getProjectSolution(
            self._project_id, sol_id)
        return getProjectSolution['site_extra_prop'] if 'site_extra_prop' in getProjectSolution else []

    def getFlavors(self):
        flv = Flavors(self._csite_)
        return dict([(str(x['id']), x) for x in flv.list()])

    def getAvblImg(self, sol_name):
        sols = VcsSolutions()
        return sols.get_images_by_sol_name(sol_name)

    @staticmethod
    def extend_vcs_flavor(name2id, flv_in_sol):
        # before production names sync w/ BMS, we need to make sure all portions types are
        # available for users.
        alternative_names = {
            'v.super':
            ['v.super', '02_vCPU_016GB_MEM_100GB_HDD', '02vCPU_016GB_MEM_LIC'],
            'v.xsuper': [
                'v.xsuper', '04_vCPU_032GB_MEM_100GB_HDD',
                '04vCPU_032GB_MEM_LIC'
            ],
            'v.2xsuper': [
                'v.2xsuper', '08_vCPU_064GB_MEM_100GB_HDD',
                '08vCPU_064GB_MEM_LIC'
            ],
            'v.4xsuper': [
                'v.4xsuper', '16_vCPU_128GB_MEM_100GB_HDD',
                '16vCPU_128GB_MEM_LIC'
            ],
            'v.8xsuper': [
                'v.8xsuper', '32_vCPU_256GB_MEM_100GB_HDD',
                '32vCPU_256GB_MEM_LIC'
            ]
        }
        alt_name = set(alternative_names.keys())

        for flv_lv in alt_name:
            for flv_lv2 in sorted(alternative_names[flv_lv], reverse=True):
                if flv_lv2 in flv_in_sol and flv_lv not in name2id:
                    name2id[flv_lv] = flv_lv2

    def getExtraProp(self, sol_id):

        extra_prop = self._do_list_solution(sol_id)
        # processing flavors

        extra_flv = set(
            extra_prop['flavor']) if 'flavor' in extra_prop else set([])

        def filter_flv(x):
            return True if x in extra_flv else False

        flvs = self.getFlavors()

        flv_in_sol = set(
            [flvs[x]['name'] for x in flvs if filter_flv(flvs[x]['name'])])

        wanted_name2id = dict([(x, x) for x in flv_in_sol])
        VcsSite.extend_vcs_flavor(wanted_name2id, flv_in_sol)

        res = {}
        for ele in extra_prop:
            if ele == 'flavor':
                res["x-extra-property-{}".format(ele)] = wanted_name2id
            elif ele == 'image':
                res["x-extra-property-{}".format(ele)] = [
                    x.split(")")[1] for x in extra_prop[ele]
                    if re.search('public', x)
                ]
            elif ele == 'system-volume-type':
                # current setting
                res["x-extra-property-{}".format(ele)] = {
                    "hdd": "block_storage-hdd"
                }
            else:
                res["x-extra-property-{}".format(ele)] = extra_prop[ele]

        return res

    def getIsrvFlavors(self, value_type="list_vcs_ptype"):

        if value_type == "list_vcs_ptype":
            return dict([(x['spec'].split("(")[0].strip(),
                          x['spec'].split("(")[1].strip().replace(")", ""))
                         for x in iservice().getVCSProducts()])
        return {}

        # def get_flavor_dict(isrv_products):
        #     for x in isrv_products:
        #         print(x)
        #         print(x['other_content'])
        #     # dict([(get_flavor_id(x), x)
        #     #              for x in isrv.getProducts() if filter_flavor_id(x)])

        #     # return int(
        #     # json.loads(x['other_content'])['flavor_id'])
        #     return dict()

        # fid_desc = get_flavor_dict(isrv.getProducts())

        # if name_or_id == "flavor_id":
        #     return fid_desc
        # else:
        #     return dict([(fid_desc[x]['desc'], fid_desc[x])for x in fid_desc])

    def create(self, name, sol_id, extra_prop):
        self.twcc.header_extra = extra_prop
        self.http_verb = 'post'
        self.data_dic = {
            "name": name,
            "desc": 'TWCC-Cli created VCS',
            "project": self._project_id,
            "solution": sol_id
        }
        return self._do_api()

    def patch_desc(self, site_id, desc):
        self.http_verb = 'patch'
        self.url_dic = {'sites': site_id}
        self.data_dic = {"desc": desc}
        return self._do_api()

    def patch_keep(self, site_id, keep):
        self.http_verb = 'patch'
        self.url_dic = {'sites': site_id}
        self.data_dic = {"termination_protection": keep}
        return self._do_api()

    def isStable(self, site_id):
        site_info = self.queryById(site_id)
        return site_info['status'] == "Ready" or site_info['status'] == "Error"

    def isStopped(self, site_id):
        site_info = self.queryById(site_id)
        return site_info['status'] == "NotReady"


class VcsServerNet(CpuService):

    def __init__(self):
        CpuService.__init__(self)
        self._func_ = "servers"
        self._csite_ = Session2._getClusterName("VCS")

    def associateIP(self, site_id, eip_id=None):
        self.action(site_id, is_bind=True, eip_id=eip_id)

    def deAssociateIP(self, site_id):
        self.action(site_id, is_bind=False)

    def reboot(self, server_id):
        self.http_verb = 'put'
        self.url_dic = {self._func_: server_id, 'action': ""}
        self.data_dic = {"action": "reboot"}
        self._do_api()

    def action(self, site_id, is_bind=True, eip_id=None):
        server_id = getServerId(site_id)
        self.http_verb = 'put'
        self.url_dic = {self._func_: server_id, 'action': ""}
        self.data_dic = {
            "action": "associateIP" if is_bind else "disassociateIP"
        }
        if not isNone(eip_id):
            self.data_dic.update({'ip': int(eip_id)})
        self._do_api()


class VcsSecurityGroup(CpuService):

    def __init__(self):
        CpuService.__init__(self)

        self._func_ = "security_groups"
        self._csite_ = Session2._getClusterName("VCS")

    def list(self, server_id=None):
        if not isNone(server_id):
            self.ext_get = {'project': self._project_id, 'server': server_id}
            return self._do_api()

    def addSecurityGroup(self, secg_id, port_min, port_max, cidr, protocol,
                         direction):

        self.http_verb = "patch"
        self.url_dic = {"security_groups": secg_id}
        self.data_dic = {
            "project": self._project_id,
            "direction": direction,
            "protocol": protocol,
            "remote_ip_prefix": cidr,
            "port_range_max": port_max,
            "port_range_min": port_min
        }
        self._do_api()

    def deleteRule(self, rule_id):
        self.http_verb = "delete"
        self.ext_get = {'project': self._project_id}
        self._func_ = "security_group_rules"
        self.url_dic = {self._func_: rule_id}
        return self._do_api()


class VcsFalvor(CpuService):

    def __init__(self):
        CpuService.__init__(self)
        self._func_ = "flavors"
        self._csite_ = Session2._getClusterName("VCS")


class VcsSolutions(CpuService):

    def __init__(self):
        CpuService.__init__(self)
        self._func_ = "solutions"
        self._csite_ = 'goc'

    def list(self, return_in_dic=False):
        self.http_verb = 'get'
        self.url_dic = {"solutions": ""}
        self.ext_get = {
            'category': 'os',
            'project': self._project_id,
        }
        ans = self._do_api()
        if return_in_dic:
            return dict([(x['name'], x['id']) for x in ans])
        return ans

    def get_images_by_sol_name(self, sol_name):
        all_imgs = self.get_info_by_sol_name(sol_name, field_name='image')
        return_ans = []
        for img in all_imgs:
            return_ans.append({
                "Provider": img.split(")")[0].replace("(", ""),
                "VCSi Name": img.split(")")[1],
            })
        return sorted(sorted(return_ans, key=lambda d: d['Provider'], reverse=True), key=lambda d: d['VCSi Name'])

    def get_flavors_by_sol_name(self, sol_name):
        flv_in_sol = self.get_info_by_sol_name(sol_name, field_name='flavor')
        flvObj = VcsFalvor()
        all_flvs = flvObj.list()

        return_ans = []

        for x in flv_in_sol:
            for y in all_flvs:
                if x == y['name']:
                    res_obj = y['resource']
                    return_ans.append({
                        "flavor name":
                        x,
                        "spec":
                        get_flavor_string(res_obj['gpu'], res_obj['cpu'],
                                          res_obj['memory'])
                    })
        return sorted(return_ans, key=lambda d: int(d['spec'][:2]))

    def get_info_by_sol_name(self, sol_name, field_name='flavor'):
        sols = self.list()
        found_sol_id = [
            x for x in sols if str(x['name']).lower() == sol_name.lower()
        ]
        if len(found_sol_id) > 0:
            found_sol_id = found_sol_id[0]['id']

            self._csite_ = Session2._getClusterName("VCS")
            self._func_ = "projects"
            self.url_dic = {
                "projects": self._project_id,
                "solutions": found_sol_id,
            }
            ans = self._do_api()
            # reset
            self._func_ = "solutions"
            self._csite_ = 'goc'
            return ans['site_extra_prop'][field_name]


class VcsImage(CpuService):

    def __init__(self):
        CpuService.__init__(self)
        self._func_ = "images"
        self._csite_ = 'goc'

    def deleteById(self, sys_vol_id):
        self.http_verb = 'delete'
        self.res_type = 'txt'
        self.url_dic = {"images": sys_vol_id}
        return self._do_api()

    def list(self, srv_id=None, isAll=False):
        if not isNone(srv_id):
            images = []
            self.ext_get = {'project': self._project_id}
            all_images = self._do_api()
            for one_image in all_images:
                if not isNone(one_image['server']):
                    if one_image['server']['id'] == srv_id:
                        images.append(one_image)
            return images
        else:
            self.ext_get = {'project': self._project_id, 'sol_categ': 'os'}
            ans = self._do_api()
            all_sys_snap = [x for x in ans if not x['is_public']]
            if isAll:
                return all_sys_snap
            else:
                my_username = sess = Session2().twcc_username
                return [
                    x for x in all_sys_snap
                    if x["user"]['username'] == my_username
                ]

    def createSnapshot(self, sid, name, desc_str):
        vcs = VcsSite()
        sites = vcs.queryById(sid)
        site_name = sites['name']
        server = VcsServer()
        server_detail = server.getServerDetail(sid)
        if len(server_detail) > 0:
            tsrv = server_detail[0]

            self.http_verb = "put"
            self.url_dic = {self._func_: "{}/save/".format(tsrv['id'])}
            self.data_dic = {
                "name": name,
                "desc": desc_str,
                "os": tsrv['os'],
                "os_version": tsrv['os_version']
            }
        return self._do_api()


class VcsServer(CpuService):

    def __init__(self):
        CpuService.__init__(self)
        self._func_ = "servers"
        self._csite_ = Session2._getClusterName("VCS")

    def getServerDetail(self, site_id):
        self.ext_get = {'project': self._project_id, 'site': site_id}
        return self._do_api()


class Fixedip(CpuService):

    def __init__(self, debug=False):
        CpuService.__init__(self)
        self._func_ = "ips"
        self._csite_ = Session2._getClusterName("VCS")

    def create(self, desc=None):
        self.http_verb = 'post'
        self.data_dic = {'project': self._project_id, 'desc': desc}
        return self._do_api()

    def list(self, ip_id=None, filter=None, isAll=False):
        if isNone(ip_id):
            self.ext_get = {'project': self._project_id}
            if not isNone(filter) and not filter == 'ALL':
                self.ext_get.update({'type': filter.upper()})
            all_fixedips = self._do_api()
            my_username = Session2().twcc_username
            if isAll:
                return all_fixedips
            else:
                return [
                    x for x in all_fixedips
                    if x["user"]['username'] == my_username
                ]

        else:
            self.http_verb = 'get'
            self.res_type = 'json'
            self.url_dic = {"ips": ip_id}
            return self._do_api()

    def patch_desc(self, ip_id, desc):
        self.http_verb = 'patch'
        self.url_dic = {'ips': ip_id}
        self.data_dic = {"desc": desc}
        return self._do_api()

    def deleteById(self, ip_id):
        self.http_verb = 'delete'
        self.url_dic = {"ips": ip_id}
        return self._do_api()

    def get_id_by_ip(self, eip):
        self.ext_get = {'project': self._project_id}
        self.ext_get.update({'type': 'STATIC'})
        all_fixedips = self._do_api()
        for ips in all_fixedips:
            if ips['address'] == eip and ips['status'] == 'AVAILABLE':
                return ips['id']
        return None


class LoadBalancers(CpuService):

    def __init__(self, debug=False):
        CpuService.__init__(self)
        self._func_ = "loadbalancers"
        self._csite_ = Session2._getClusterName("VCS")
        self.ch_vlb_temp_json = {
            "pools": [{
                "name": "TestPool (required)",
                "protocol": "TCP, HTTP, or HTTPS (required)",
                "members": [{
                    "ip": "string",
                    "port": 0,
                    "weight": 0
                }],
                "method":
                "ROUND_ROBIN, LEAST_CONNECTIONS, or SOURCE_IP (required)",
                "delay": "5 (optional)",
                "max_retries": "from 1 to 10 (optional)",
                "timeout": "5 (optional)",
                "monitor_type": "HTTP, HTTPS, PING, or TCP (optional)",
                "expected_codes": "200, 200,202 or 200-204 (optional)",
                "http_method":
                "CONNECT, DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT, or TRACE (optional)",
                "url_path": "/ (optional)"
            }],
            "listeners": [{
                "name":
                "TestListener (required)",
                "pool_name":
                "TestPool (required)",
                "protocol":
                "TCP, HTTP, HTTPS, or TERMINATED_HTTPS (required)",
                "protocol_port":
                "from 0 to 65535 (required)",
                "default_tls_container_ref":
                "The ID of a secret required by the listener if the listener uses TERMINATED_HTTPS protocol (optional)",
                "sni_container_refs": [
                    "A list of ID of secrets required by the listener if the listener uses TERMINATED_HTTPS protocol (optional)"
                ]
            }]
        }

    def create(self,
               vlb_name,
               pools,
               vnet_id,
               listeners,
               vlb_desc,
               json_data=None,
               eip_id=None):
        self.http_verb = 'post'
        self.data_dic = {
            'name': vlb_name,
            'private_net': vnet_id,
            'pools': pools,
            'listeners': listeners,
            'desc': vlb_desc
        }
        if not isNone(eip_id):
            self.data_dic.update({'ip': eip_id})
        if not isNone(json_data):
            self.data_dic = json_data
        return self._do_api()

    def update(self, vlb_id, listeners, pools, eip_id=None):
        self.http_verb = 'patch'
        self.url_dic = {"loadbalancers": vlb_id}
        for pool in pools:
            for col in ['expected_codes', 'http_method', 'url_path']:
                if isNone(pool[col]):
                    del pool[col]
        for listener in listeners:
            for col in ['default_tls_container_ref', 'sni_container_refs']:
                if isNone(listener[col]) or listener[col] == []:
                    del listener[col]
        self.data_dic = {'pools': pools, 'listeners': listeners}
        if not isNone(eip_id):
            self.data_dic.update({'ip': eip_id})
        return self._do_api()

    def isStable(self, site_id):
        site_info = self.queryById(site_id)
        return site_info['status'] == "ACTIVE"

    def list(self, vlb_id=None, isAll=False):
        if isNone(vlb_id):
            if isAll:
                self.ext_get = {'project': self._project_id, "all_users": 1}
                return self._do_api()
            else:
                self.ext_get = {'project': self._project_id}
                all_vlbs = self._do_api()
                my_username = Session2().twcc_username
                return [
                    x for x in all_vlbs if x["user"]['username'] == my_username
                ]

        else:
            self.http_verb = 'get'
            self.res_type = 'json'
            self.url_dic = {"loadbalancers": vlb_id}
            return self._do_api()

    def deleteById(self, vlb_id):
        self.http_verb = 'delete'
        self.url_dic = {"loadbalancers": vlb_id}
        return self._do_api()


class Secrets(CpuService):

    def __init__(self, debug=False):
        CpuService.__init__(self)
        self._func_ = "secrets"
        self._csite_ = Session2._getClusterName("VCS")

    def create(self, name, desc="", payload="", expire_time=""):
        self.http_verb = 'post'
        self.data_dic = {
            'project': self._project_id,
            "name": name,
            "desc": desc,
            "payload": payload
        }
        if not isNone(expire_time):
            self.data_dic.update({'expire_time': expire_time})
        return self._do_api()

    def deleteById(self, sys_vol_id):
        self.http_verb = 'delete'
        self.url_dic = {"secrets": sys_vol_id}
        return self._do_api()

    def list(self, ssl_id=None, isall=False):
        if isNone(ssl_id):
            self.http_verb = 'get'
            self.res_type = 'json'
            if isall:
                self.ext_get = {'project': self._project_id}
                all_volumes = self._do_api()
                return all_volumes
            else:
                self.ext_get = {'project': self._project_id}
                all_volumes = self._do_api()
                my_username = Session2().twcc_username
                return [
                    x for x in all_volumes
                    if x["user"]['username'] == my_username
                ]
        else:
            self.http_verb = 'get'
            self.res_type = 'json'
            self.url_dic = {"secrets": ssl_id}
            return self._do_api()


class Volumes(CpuService):

    def __init__(self, debug=False):
        CpuService.__init__(self)
        self._func_ = "volumes"
        self._csite_ = Session2._getClusterName("VCS")

    def create(self, name, size, desc="", volume_type="hdd"):
        self.http_verb = 'post'
        self.data_dic = {
            'project': self._project_id,
            "name": name,
            "size": size,
            "desc": desc,
            "volume_type": volume_type
        }
        return self._do_api()

    def deleteById(self, sys_vol_id):
        self.http_verb = 'delete'
        self.url_dic = {"volumes": sys_vol_id}
        return self._do_api()

    def update(self, sys_vol_id, vol_status, srvid, size, wait):
        self.http_verb = 'put'
        self.url_dic = {"volumes": sys_vol_id, "action": ""}
        if vol_status in ['attach', 'detach']:
            self.data_dic = {"status": vol_status, "server": srvid}
        elif vol_status == "extend":
            self.data_dic = {"status": vol_status, "server": 0, "size": size}
        else:
            raise ValueError("please provide -sts")
        return self._do_api()

    def list(self, sys_vol_id=None, isAll=False):
        if isNone(sys_vol_id):
            self.http_verb = 'get'
            self.res_type = 'json'
            if isAll:
                self.ext_get = {'project': self._project_id}
                all_volumes = self._do_api()
                return all_volumes
            else:
                self.ext_get = {'project': self._project_id}
                all_volumes = self._do_api()
                my_username = Session2().twcc_username
                return [
                    x for x in all_volumes
                    if x["user"]['username'] == my_username
                ]
        else:
            self.http_verb = 'get'
            self.res_type = 'json'
            self.url_dic = {"volumes": sys_vol_id}
            return self._do_api()


def getServerId(site_id):
    vcs = VcsSite()
    sites = vcs.queryById(site_id)
    if not 'id' in sites:
        raise ValueError("Site ID: {} is not found.".format(site_id))
    if len(sites['servers']) >= 1:
        server_info = sites['servers'][0]
        server_id = server_info['id']
        return server_id
    else:
        return None
        #raise ValueError("Site ID: {} , servers not found.".format(site_id))


def getSecGroupList(site_id):
    server_id = getServerId(site_id)
    if server_id == None:
        return []
    secg = VcsSecurityGroup()
    secg_list = secg.list(server_id=server_id)
    if len(secg_list) > 0:
        return secg_list[0]
    else:
        return []
