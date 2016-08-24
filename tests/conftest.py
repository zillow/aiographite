import pytest


@pytest.fixture
def metric_parts():
    return ['sproc performance', 'velo@zillow.com', '::EH12']


@pytest.fixture
def timestamp():
    return 1471640923


@pytest.fixture
def metric_value_tuple_list():
    return [
        ('zillow', 124), ('trulia', 223),
        ('hotpad', 53534), ('streeteasy', 13424)]


@pytest.fixture
def metric_value_timestamp_list():
    return [
        ('zillow', 124, 1471640958), ('trulia', 223, 1471640923),
        ('hotpad', 53534, 1471640943), ('streeteasy', 13424, 1471640989)]
