# -*- coding: utf-8 -*-
from __future__ import print_function
from twcc.services.generic import GenericService

class users(GenericService):
    def __init__(self, api_key_tag, debug=False):
        GenericService.__init__(self, debug=debug)

        self._csite_ = "goc"
        self._api_key_ = api_key_tag

    def getInfo(self):
        return self.list()

class acls(GenericService):
    """ This Class is for ACL api call
    """

    def __init__(self, api_key_tag, debug=False):
        """ constractor for this ACL class

        Args:
            api_key_tag (str): see YAML for detail
        """
        GenericService.__init__(self, debug=debug)

        self._csite_ = "admin"
        self._api_key_ = api_key_tag
        self.res_type = "json"

    def getSites(self):
        res = self.list()
        #if 'data' in res:
        return sorted([ x['group'] for x in res['data'] ])
        #else:
        #    return sorted([ (x, y['group']) for x in res for y in res[x]])

    def listGroup(self):
        """ this api is the same with acl

        """
        self._func_ = "acls-g"
        return self._do_api()

class keypairs(GenericService):
    """ This Class is for keypairs api call
    """

    def __init__(self, api_key_tag, debug=False):
        """ constractor for this keypairs class

        Args:
            api_key_tag (str): see YAML for detail
        """
        GenericService.__init__(self)
        # current working information
        self._csite_ = "openstack-taichung-suse"
        self._api_key_ = api_key_tag
        self._debug_ = debug

    def list(self):
        return self._do_api()

class projects(GenericService):
    def __init__(self, api_key_tag, debug=False):
        GenericService.__init__(self, debug=debug)

        self._csite_ = "openstack-taichung-suse"
        self._api_key_ = api_key_tag
