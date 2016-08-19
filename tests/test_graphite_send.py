import pytest
from aiographite import aiographitesend 
import socket
import unittest

DEFAULT_GRAPHITE_PLAINTEXT_PORT = 2003
DEFAULT_GRAPHITE_PICKLE_PORT = 2004




# class TestAsyncioGraphiteSendService:
# @classmethod
def setup_module(module):
	module.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	module.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	module.server.bind(('localhost', DEFAULT_GRAPHITE_PLAINTEXT_PORT))
	module.server.listen(20)

# @classmethod
def teardown_module(module):
	"""
		1. Destroy aiographite_send instance
		2. Close the server socket
	"""
	aiographitesend.destroy()

	try:
		module.server.shutdown(socket.SHUT_RD)
		module.server.close()
	except Exception:
		pass
	module.server = None



@pytest.mark.parametrize("metric, value, timestamp", [
    ('zillow', 124, 234),
    ('trulia', 223, 435),
    ('hotpad', 53534, 32425),
])
def test_pickle_protocol_formatted_data(metric, value, timestamp):
	graphite_send_instance = aiographitesend.init('localhost', DEFAULT_GRAPHITE_PLAINTEXT_PORT, 'plaintext')
	assert graphite_send_instance.pickle_protocol_formatted_data(metric, value, timestamp) == (metric, (timestamp, value))



@pytest.mark.parametrize("metric, value, timestamp", [
    ('M M M', 124, 234),
    ('python ruby java', 223, 435),
    ('C C++ Perl', 53534, 32425),
])
def test_plaintext_protocol_formatted_data(metric, value, timestamp):
	graphite_send_instance = aiographitesend.init('localhost', DEFAULT_GRAPHITE_PLAINTEXT_PORT, 'plaintext')
	assert graphite_send_instance.plaintext_protocol_formatted_data(metric, value, timestamp) == " ".join([metric, str(value), str(timestamp)]) + "\n"



@pytest.mark.parametrize("message", [
    "hello world baby\n",
    "baby@zillow.com\n",
    "123 456 789"
])
def test_send_message(message):
	graphite_send_instance = aiographitesend.init('localhost', DEFAULT_GRAPHITE_PLAINTEXT_PORT, 'plaintext')
	assert graphite_send_instance.send_message(message) == len(message)



def test_disconnect():
	graphite_send_instance = aiographitesend.init('localhost', DEFAULT_GRAPHITE_PLAINTEXT_PORT, 'plaintext')
	graphite_send_instance.disconnect()
	assert graphite_send_instance.socket is None



def test_send_data_fail_after_disconnect():
	graphite_send_instance = aiographitesend.init('localhost', DEFAULT_GRAPHITE_PLAINTEXT_PORT, 'plaintext')
	graphite_send_instance.disconnect()
	with pytest.raises(Exception):
		graphite_send_instance.send_message("hello_world\n")











