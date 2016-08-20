import asyncio
from aiographite.graphite_escaping import metrics_name_to_graphite, metrics_name_from_graphite
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


class PlaintextProtocol(object):

	def data_formate_function(self, metric: str, value: int, timestamp: int):
		"""
			@return: required data formate when sending data through 'plaintext' protocol
			@return_type: String
		"""
		formatted_data = " ".join([metric, str(value), str(timestamp)])
		return formatted_data + "\n"


	def generate_message_function(self, listOfPlaintext: List[str]):
		"""
			return the required message formate for protocol 'plaintext'
			@param: 
				listOfPlaintext: ["metric1 value1 timestamp1", "metric2 value2 timestamp2", ...]
				type: List of String
		"""
		return "".join(listOfPlaintext).encode('ascii')
		


class PickleProtocol(object):

	def data_formate_function(self, metric: str, value: int, timestamp: int):
		"""
			@return: required data formate when sending data through 'pickle' protocol
			@return_type: Tuple
		"""		
		return (metric, (timestamp, value))	


	def generate_message_function(self, listOfMetricTuples: List[Tuple]):
		"""
			@param: 
				listOfMetricTuples: [(metric1, (timestamp1, value1), (metric2, (timestamp2, value2), ...]
		"""
		payload = pickle.dumps(listOfMetricTuples, protocol=2)
		header = struct.pack("!L", len(payload))
		message = header + payload
		return message





class AIOGraphite(object):

	def __init__(self, graphite_server, graphite_port, protocol = PickleProtocol()):

		self._graphite_server_address = (graphite_server, graphite_port)

		self._connect_to_graphite()

		self.protocol = protocol

		self.loop = asyncio.get_event_loop()



	def send_single_data(self, metric_dir_list: List[str], value: int, timestamp = None):
		"""
			@example: 
				Assuming that 

					Expected_Metric_Name  =  metaccounts.authentication.password.attempted

				Then input metric_dir_list should be

					metric_dir_list = [metaccounts, authentication, password, attempted]

			@metric_dir_list: List of string
			@timestamp: the type should be int

			If you're very confident that the metric name is valid, then use <method: send_single_valid_data> instead.

		"""		
		valid_metric_name = self._to_graphite_valid_metric_name(metric_dir_list)
		self.send_single_valid_data(valid_metric_name, value, timestamp)



	def send_dataset_list(self, dataset:List[Tuple] , timestamp = None):
		"""
			@param: 
				Support two kinds of dataset

				1)	dataset = [(metric_dir_list1, value1), (metric_dir_list2, value2), ...] 

				or 

				2)	dataset = [(metric_dir_list1, value1, timestamp1), (metric_dir_list1, value2, timestamp2), ...]

			If you're very confident that the metric name is valid, then use <method: send_valid_dataset_list> instead.

		"""
		if not dataset:
			return 

		if len(dataset[0]) == 2:
			valid_dataset = [(self._to_graphite_valid_metric_name(metric_dir_list), value) for metric_dir_list, value in dataset]
		else:
			valid_dataset = [(self._to_graphite_valid_metric_name(metric_dir_list), value, timestamp) for metric_dir_list, value, timestamp in dataset]

		self.send_valid_dataset_list(valid_dataset, timestamp)



	def send_single_valid_data(self, metric: str, value: int, timestamp = None):
		"""
			@metric: String
			@value: int
			@timestamp: int
			Send a single data(metric value timestamp) to graphite
		"""
		timestamp = int(timestamp or time.time())

		# Generate message based on protocol
		listOfMetricTuples = [self.protocol.data_formate_function(metric, value, timestamp)]
		message = self.protocol.generate_message_function(listOfMetricTuples)

		# Sending Data
		self.loop.run_until_complete(asyncio.ensure_future(self._send_message(message)))



	def send_valid_dataset_list(self, dataset: List[Tuple], timestamp = None):
		"""
			@param: 
			Support two kinds of dataset
				1)	dataset = [(metric1, value1), (metric2, value2), ...] 
				or 
				2)	dataset = [(metric1, value1, timestamp1), (metric2, value2, timestamp2), ...]
		"""
		timestamp = int(timestamp or time.time())

		# Generate message based on protocol
		message = self._generate_message_for_data_list(dataset, timestamp, self.protocol.data_formate_function, self.protocol.generate_message_function)

		# Sending Data
		self.loop.run_until_complete(asyncio.ensure_future(self._send_message(message)))



	def send_valid_dataset_dict(self, dataset: Dict, timestamp = None):
		"""
			Send data to graphite server when incoming data is in 'dict' format
			@param: dataset = {
									metric1 : value1,      // type ( string: int )
									metric2 : value2, 
									...
							  }

			metric1 (metric2, ...) are valid metric name for Graphite
		"""
		self.send_valid_dataset_list(dataset.items(), timestamp)



	def disconnect(self):
	"""
		Close the TCP connection 
	"""
	try:
		self.socket.shutdown(1)
	except AttributeError:
		self.socket = None
	except Exception:
		self.socket = None
	finally:
		self.socket = None



	def close_event_loop(self):
		"""
			Close Event Loop. 
			No call should be made after event loop closed
		"""
		self.loop.close()



	@asyncio.coroutine
	async def _send_message(self, message: str) -> int:
		"""
			@message: data ready to sent to graphite server
		"""
		total_sent = 0
		message_size = len(message)
		while total_sent < message_size:
			try:
				sent = yield from self.socket.send(message[total_sent:])
				if sent == 0:
					raise RuntimeError("socket connection broken")
				total_sent = total_sent + sent
			except socket.gaierror as e:
				raise AioGraphiteSendException("Fail to send data to %s, Error: %s" % (self._graphite_server_address, e)) 
			except Exception as e:
				raise e
		return total_sent



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
			listOfData.append(formate_function(metric, value, timestamp))
		message =  generate_message_function(listofData)
		return message	


		
	def _to_graphite_valid_metric_name(self, metric_dir_list: List[str]):
		"""
			@purpose:
				Make metric name valid for graphite in case that the metric name includes 
				any special character which is not supported by Graphite
			@example: 
				Assuming that 

					Expected_Metric_Name  =  metaccounts.authentication.password.attempted

				Then input metric_dir_list should be

					metric_dir_list = [metaccounts, authentication, password, attempted]

			@metric_dir_list: List of String
		"""
		return ".".join([metrics_name_to_graphite(dir_name) for dir_name in metric_dir_list])



	def _connect_to_graphite(self):
		"""
			Connect to Graphite Server based on Provided Server Address
		"""
		try:
			self.socket = socket.create_connection(self._graphite_server_address)
			self.socket.setblocking(False)
		except socket.gaierror:
			raise AioGraphiteSendException("Unable to connect to the provided server address %s:%s" % self._graphite_server_address)
		except Exception as e:
			raise e
		return self.socket


#########################################################
#########################################################
#########################################################



def _dummy_message_plaintext_formate():
	print("Message formate for plaintext protocol")
	print("Metric1 Value TimeStamp1\n Metric2 Value2 Timestamp2")



def _dummy_message_pickle_formate():
	print("Message formate for pickle protocol")
	print("[(path1, (timestamp1, value1)), (path2, (timestamp2, value2)), ...]")



def main():
	_dummy_message_plaintext_formate()



if __name__ == '__main__':
	main()







