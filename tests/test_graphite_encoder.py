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
    '汉 字.汉*字',
    '%2D%2Ea bcd',
    '_hello world.%2E',
    'www.zillow.com.%2Ehello%2D',
    '',
    ('a' * 128)     # test for very long string
])
def test_consistency(name):
    assert GraphiteEncoder.decode(GraphiteEncoder.encode(name)) == name


@pytest.mark.parametrize("name", [
    None,
    1
])
def test_encode_invalid_input(name):
    with pytest.raises(Exception):
        GraphiteEncoder.encode(name)


@pytest.mark.parametrize("name", [
    None,
    1
])
def test_decode_invalid_input(name):
    with pytest.raises(Exception):
        GraphiteEncoder.decode(name)
