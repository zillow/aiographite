import pytest
from aiographite import aiographitesend 
import socket
import unittest

DEFAULT_GRAPHITE_PLAINTEXT_PORT = 2003
DEFAULT_GRAPHITE_PICKLE_PORT = 2004

@pytest.fixture(scope="class")
def graphite_server_plaintext():
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server.bind(('localhost', DEFAULT_GRAPHITE_PLAINTEXT_PORT))
	server.listen(5)
	return server


@pytest.fixture
def graphite_send_instance():
	return aiographitesend.init('localhost', DEFAULT_GRAPHITE_PLAINTEXT_PORT, 'plaintext')



@pytest.mark.parametrize("metric, value, timestamp", [
	('zillow', 123, 89071),
	('velocity', 234, 9875),
	('rental', 124, 4533)
])
def test_pickle_protocol_formatted_data(metric, value, timestamp, graphite_send_instance):
	assert graphite_send_instance.pickle_protocol_formatted_data(metric, value, timestamp) == (metric, (timestamp, value))


# @pytest.mark.usefixtures("graphite_server_plaintext")
# class TestAsyncioGraphiteSendService(unittest.TestCase):
# 	def test_connec