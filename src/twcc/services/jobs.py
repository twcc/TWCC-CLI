# -*- coding: utf-8 -*-
from __future__ import print_function
from twcc.services.generic import GenericService

class jobs(GenericService):
    def __init__(self, api_key_tag, debug=False):
        GenericService.__init__(self, debug=debug)

        self._csite_ = "k8s-taichung-default"
        self._api_key_ = api_key_tag

