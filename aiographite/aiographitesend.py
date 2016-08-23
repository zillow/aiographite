from .protocol import PlaintextProtocol, PickleProtocol
from .graphiteencoder import GraphiteEncoder
import asyncio
import pickle
import struct
import socket
import os
import time
from typing import Dict, Tuple, List


DEFAULT_GRAPHITE_PLAINTEXT_PORT = 2003
DEFAULT_GRAPHITE_PICKLE_PORT = 2004
SUPPORT_PROTOCOLS = ["plaintext", "pickle"]


class AioGraphiteSendException(Exception):
    pass


class AIOGraphite:

	def __init__(self, graphite_server, graphite_port, protocol, loop = None):

		self._graphite_server = graphite_server

		self._graphite_port = graphite_port

		self._graphite_server_address = (graphite_server, graphite_port)

		self._reader, self._writer = None, None

		self.protocol = protocol

		self.loop = loop or asyncio.get_event_loop()


	@asyncio.coroutine
	async def send(self, metric: str, value: int, timestamp = None):
		"""
			@metric: String, valid metric name for Graphite
			@value: int
			@timestamp: int
			Send a single data(metric value timestamp) to graphite
		"""
		if not metric:
			return
		timestamp = int(timestamp or time.time())
		# Generate message based on protocol
		listOfMetricTuples = [self.protocol.data_format(metric, value, timestamp)]
		message = self.protocol.generate_message(listOfMetricTuples)
		# Sending Data
		await self._send_message(message)



	@asyncio.coroutine
	async def send_multiple(self, dataset: List[Tuple], timestamp = None):
		"""
			@param: 
			Support two kinds of dataset
				1)	dataset = [(metric1, value1), (metric2, value2), ...] 
				or 
				2)	dataset = [(metric1, value1, timestamp1), (metric2, value2, timestamp2), ...]
		"""
		if not dataset:
			return 
		timestamp = int(timestamp or time.time())
		# Generate message based on protocol
		message = self._generate_message_for_data_list(dataset, timestamp, self.protocol.data_format, self.protocol.generate_message)
		# Sending Data
		await self._send_message(message)


	@asyncio.coroutine
	async def close_event_loop(self):
		"""
			Close Event Loop. 
			No call should be made after event loop closed
		"""
		self.loop.close()


	@asyncio.coroutine
	async def connect_to_graphite(self):
		"""
			Connect to Graphite Server based on Provided Server Address
		"""
		try:
			self._reader, self._writer = await asyncio.open_connection(self._graphite_server, self._graphite_port, loop = self.loop)
		except socket.gaierror:
			raise AioGraphiteSendException("Unable to connect to the provided server address %s:%s" % self._graphite_server_address)


	def disconnect(self):
		"""
			Close the TCP connection 
		"""
		try:
			self._writer.close()
		except (AttributeError, Exception):
			self._writer = None
		finally:
			self._writer = None
			self._reader = None	


	def clean_and_join_metric_parts(self, metric_parts: List[str]) -> str:
		"""
			@purpose:
				Make metric name valid for graphite in case that the metric name includes 
				any special character which is not supported by Graphite
			@example: 
				Assuming that 

					Expected_Metric_Name  =  metaccounts.authentication.password.attempted

				Then input metric_parts should be

					metric_parts = [metaccounts, authentication, password, attempted]

			@metric_parts: List of String
		"""
		return ".".join([GraphiteEncoder.encode(dir_name) for dir_name in metric_parts])


	@asyncio.coroutine
	async def _send_message(self, message: bytes) -> int:
		"""
			@message: data ready to sent to graphite server
		"""
		self._writer.write(message)
		await self._writer.drain()


	def _generate_message_for_data_list(self, dataset: List[Tuple], timestamp, formate_function, generate_message_function):
		"""
			generate proper formatted message 
			@param:
			Support two kinds of dataset
				1)	dataset = [(metric1, value1), (metric2, value2), ...] 
				or 
				2)	dataset = [(metric1, value1, timestamp1), (metric2, value2, timestamp2), ...]
		"""
		listofData = []
		for data in dataset:
			# unpack metric data
			if len(data) == 2:
				(metric, value) = data
			else:
				(metric, value, data_timestamp) = data
				timestamp = data_timestamp
			listofData.append(formate_function(metric, value, timestamp))
		message =  generate_message_function(listofData)
		return message	

		






