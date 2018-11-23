# -*- coding: utf-8 -*-
from __future__ import print_function
from os import sys, path
sys.path.append(path.dirname(path.abspath(__file__)))
from generic import GenericService
"""
never use
"""

class projects(GenericService):
    """ This Class is for projects api call
    """

    def __init__(self, api_key_tag, debug=False):
        """ constractor for this projects class

        Args:
            api_key_tag (str): see YAML for detail
        """
        GenericService.__init__(self)
        # current working information
        self._csite_ = "goc"
        self._api_key_ = api_key_tag
        self.res_type = "json"
        self._debug_ = debug
        self.twcc._debug = debug

    def list(self):
        return self._do_api()


