#!/usr/bin/python
# -*- coding: utf-8 -*-

import pytest
from aiographite.graphite_encoder import GraphiteEncoder


@pytest.mark.parametrize("name", [
    'abc_edf',
    'abc @edf#',
    'abc.@edf#',
    'abc_ @ e_df#',
    'a.b.c_ @ e_df#',
    'a.b.___c d _feg',
    '_ . .fda',
    '_.',
    '汉 字.汉*字'
])
def test_consistency(name):
    assert GraphiteEncoder.decode(GraphiteEncoder.encode(name)) == name
