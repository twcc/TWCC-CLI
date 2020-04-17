# -*- coding: utf-8 -*-
from click.testing import CliRunner
from ..twcc.util import name_validator, resource_id_validater


def test_name_validator():

    rules = {
        "twcc_cli9": True,
        "twcc-cli": True,
        "twcc.cli": False,
        "Twccli": False,
        "9twccli": False,
        "abcdefghijklmnopqrstuvwxyz": False,
    }

    for val_name in rules:
        print("checking", val_name)
        assert name_validator(val_name) == rules[val_name]


def test_res_name_validator():

    rules = {
        "9999": True,
        "asdfg": False,
        "a123": False,
    }

    for val_name in rules:
        print("checking", val_name)
        assert resource_id_validater(val_name) == rules[val_name]
