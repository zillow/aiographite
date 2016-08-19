import pytest
from aiographite import aiographitesend 
import socket
import unittest

DEFAULT_GRAPHITE_PLAINTEXT_PORT = 2003
DEFAULT_GRAPHITE_PICKLE_PORT = 2004




class TestAsyncioGraphiteSendService(unittest.TestCase):
	def setup_class(cls):
		cls.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		cls.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		cls.server.bind(('localhost', DEFAULT_GRAPHITE_PLAINTEXT_PORT))
		cls.server.listen(5)

	def teardown_class(cls):
		"""
			1. Destroy aiographite_send instance
			2. Close the server socket
		"""
		aiographitesend.destroy()

		try:
			cls.server.shutdown(socket.SHUT_RD)
			cls.server.close()
		except Exception:
			pass
		cls.server = None

		@pytest.mark.parametrize("metric, value, timestamp", [
		('zillow', 123, 89071),
		('velocity', 234, 9875),
		('rental', 124, 4533)
		])
		@pytest.mark.usefixtures("graphite_server_plaintext")
		def test_pickle_protocol_formatted_data(metric, value, timestamp):
			graphite_send_instance = aiographitesend.init('localhost', DEFAULT_GRAPHITE_PLAINTEXT_PORT, 'plaintext')
			assert graphite_send_instance.pickle_protocol_formatted_data(metric, value, timestamp) == (metric, (timestamp, value))

