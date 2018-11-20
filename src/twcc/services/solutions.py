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
