import pytest
from aiographite.aiographitesend import AioGraphiteSendException
from aiographite.aiographitesend import PlaintextProtocol, PickleProtocol, AIOGraphite
import socket
import unittest
import asyncio
from asyncio import test_utils



DEFAULT_GRAPHITE_PLAINTEXT_PORT = 2003
DEFAULT_GRAPHITE_PICKLE_PORT = 2004



def setup_module(module):
	module.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	module.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	module.server.bind(('localhost', DEFAULT_GRAPHITE_PLAINTEXT_PORT))
	module.server.listen(20)


def teardown_module(module):
	"""
		1. Destroy aiographite_send instance
		2. Close the server socket
	"""
	try:
		module.server.shutdown(socket.SHUT_RD)
		module.server.close()
	except Exception:
		pass
	module.server = None



@pytest.fixture
def metric_dir_list():
	return ['sproc performance', 'velo@zillow.com', '::EH12']



@pytest.fixture
def metric_value_tuple_list():
	return [('zillow', 124), ('trulia', 223), ('hotpad', 53534), (streeteasy, 13424)]



@pytest.fixture
def metric_value_timestamp_list():
	return [('zillow', 124, 1471640958), ('trulia', 223, 1471640923), ('hotpad', 53534, 1471640943), (streeteasy, 13424, 1471640989)]



@pytest.fixture
def metric_dir_list_value_data_list():
	return [(['sproc performance', 'velo@zillow.com', '::EH12'], 342), (['aws_test', 'ads@zillow.com', 'disk_usage'], 132)]



@pytest.fixture
def metric_value_dict():
	return {
		'hello_world': 123,
		'velocity_zillow': 456,
		'sproc_performance': 789,
	}


################ Unit Tests ##################

@pytest.mark.parametrize("metric, value, timestamp", [
    ('zillow', 124, 234),
    ('trulia', 223, 435),
    ('hotpad', 53534, 32425),
])
def test_pickle_protocol_formatted_data(metric, value, timestamp):
	pickle = PickleProtocol()
	assert pickle.data_formate_function(metric, value, timestamp) == (metric, (timestamp, value))



@pytest.mark.parametrize("metric, value, timestamp", [
    ('M M M', 124, 234),
    ('python ruby java', 223, 435),
    ('C C++ Perl', 53534, 32425),
])
def test_plaintext_protocol_formatted_data(metric, value, timestamp):
	plaintext = PlaintextProtocol()
	assert plaintext.data_formate_function(metric, value, timestamp) == " ".join([metric, str(value), str(timestamp)]) + "\n"



def test_generate_message_for_pickle():
	pickle = PickleProtocol()
	tuple_list = [('a', (123, 456)), ('b', (123, 456)), ('c', (876, 987))]
	expected_message = b'\x00\x00\x00B\x80\x02]q\x00(X\x01\x00\x00\x00aq\x01K{M\xc8\x01\x86q\x02\x86q\x03X\x01\x00\x00\x00bq\x04K{M\xc8\x01\x86q\x05\x86q\x06X\x01\x00\x00\x00cq\x07Ml\x03M\xdb\x03\x86q\x08\x86q\te.'
	assert pickle.generate_message_function(tuple_list) == expected_message



def test_generate_message_for_plaintext():
	plaintext_list = ["metric1 value1 timestamp1\n", "metric2 value2 timestamp2\n", "metric3 value3 timestamp3\n"]
	expected_message = b'metric1 value1 timestamp1\nmetric2 value2 timestamp2\nmetric3 value3 timestamp3\n'
	plaintext = PlaintextProtocol()
	message = plaintext.generate_message_function(plaintext_list)
	assert message == expected_message



def test_open_connection():
	
	with test_utils.run_test_server() as httpd:
		loop = asyncio.get_event_loop()
		plaintext_protocol = PlaintextProtocol()
		aiographite = AIOGraphite(*httpd.address, plaintext_protocol, loop = loop)
		loop.run_until_complete(aiographite.connect_to_graphite())











