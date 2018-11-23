# -*- coding: utf-8 -*-
from __future__ import print_function
from os import sys, path
sys.path.append(path.dirname(path.abspath(__file__)))
from generic import GenericService


class solutions(GenericService):
    """ This Class is for solutions api call
    """

    def __init__(self, api_key_tag, debug=False):
        """ constractor for this solutions class

        Args:
            api_key_tag (str): see YAML for detail
        """
        GenericService.__init__(self, debug=debug)
        self._csite_ = "goc"
        self._api_key_ = api_key_tag

    @staticmethod
    def getPatchFields():
        fields = ['desc', 'name', 'category', 'is_public']
        return dict([ (x, '') for x in fields])

    def download(self, sol_id):
        self.url_dic = { "solutions": sol_id, "file": ""}
        self.res_type='octet-stream'
        return self._do_api()

    def create(self, sol_name, upload_fn):
        self.http_verb = 'post'
        self.data_dic = { "name" : sol_name,
                "category" : "Aug-SpecialRecipe",
                "desc" : "This is Aug Sepcial build",
                "is_tenant_admin_only": 'false'}
        ans = self._do_api()
        self.uploadFile(ans['id'], upload_fn)
        #self.setPublic(ans['id'])
        return ans

    def uploadFile(self, sol_id, upload_fn):
        self.res_type = 'txt'
        self.http_verb = 'put'
        self.url_dic = { "solutions": sol_id, "file" : "" }
        self.twcc.file_cnt = { 'data': ("foobar.gsp", open(upload_fn, 'rb')) }
        self.content_type = 'file'
        return self._do_api()

    def setPublic(self, sol_id, attrs=None):
        import datetime
        current_sol = self.queryById(sol_id)
        if not 'desc' in current_sol.keys():
            return None
        attrs = solutions.getPatchFields()
        attrs['desc'] += "{0}, update: {1}".format(current_sol['desc'], datetime.datetime.now())
        attrs['is_public'] = 'true'

        del_attr = []
        for attr_k in attrs.keys():
            if not len(attrs[attr_k])>0:
                del_attr.append(attr_k)
        for attr_k in del_attr:
            del attrs[attr_k]

        self.http_verb = 'patch'
        self.url_dic = { "solutions": sol_id }
        self.res_type = 'txt'
        self.data_dic = attrs
        self.content_type = "json"

        return self._do_api()


