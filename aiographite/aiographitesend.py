import asyncio
from graphite_escaping import metrics_name_to_graphite, metrics_name_from_graphite
import pickle
import struct
import socket
import os
import time


DEFAULT_GRAPHITE_PLAINTEXT_PORT = 2003
DEFAULT_GRAPHITE_PICKLE_PORT = 2004
SUPPORT_PROTOCOLS = ["plaintext", "pickle"]


class AioGraphiteSendException(Exception):
    pass


class AsyncioGraphiteSendService(object):

	def __init__(self, graphite_server, graphite_port, protocol = "pickle"):
		"""
			Must call __init__ before use
		"""
		# Graphite Server Address
		self.graphite_server_address = (graphite_server, graphite_port)

		# Connect to Graphite Server
		self.connect_to_graphite()

		# protocol
		self.protocol = protocol

		# Get Event Loop
		self.loop = asyncio.get_event_loop()


	def connect_to_graphite(self):
		"""
			Connect to Graphite Server based on Provided Server Address
		"""
		self.socket = socket.socket()
		self.socket.setblocking(False)
		try:
			self.socket.create_connection(self.graphite_server_address)
		except InterruptedError, e:
			raise e
		except socket.gaierror:
			raise AioGraphiteSendException("Unable to connect to the provided server address %s:%s" % self.graphite_server_address)
		except Exception, e:
			raise AioGraphiteSendException("Unexpected exception while connecting to %s:%s" % self.graphite_server_address)
		return self.socket



	def send_single_data(self, metric_dir_list, value, timestamp = None):
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
		valid_metric_name = self.to_graphite_valid_metric_name(metric_dir_list)
		self.send_single_valid_data(valid_metric_name, value, timestamp)



	def send_dataset_list(self, dataset, timestamp = None):
		"""
			@param: 
				Support two kinds of dataset

				1)	dataset = [(metric_dir_list, value1), (metric_dir_list, value2), ...] 

				or 

				2)	dataset = [(metric_dir_list1, value1, timestamp1), (metric_dir_list1, value2, timestamp2), ...]

			If you're very confident that the metric name is valid, then use <method: send_valid_dataset_list> instead.

		"""
		if not dataset:
			return 

		if len(dataset[0]) == 2:
			valid_dataset = [(self.to_graphite_valid_metric_name(metric_dir_list), value) for metric_dir_list, value in dataset]
		else:
			valid_dataset = [(self.to_graphite_valid_metric_name(metric_dir_list), value, timestamp) for metric_dir_list, value, timestamp in dataset]

		self.send_valid_dataset_list(valid_dataset, timestamp)



	def send_single_valid_data(self, metric, value, timestamp = None):
		"""
			@metric: String
			@value: int
			@timestamp: int
			Send a single data(metric value timestamp) to graphite
		"""
        timestamp = int(time.time()) if timestamp is None else int(timestamp)
		message = ""
		if self.protocol == "plaintext":
			message = plaintext_protocol_formatted_data(metric, value, timestamp)
		else:
			listOfMetricTuples = [pickle_protocol_formatted_data(metric, value, timestamp)]
			message = generate_message_for_pickle(listOfMetricTuples)
		self.loop.run_until_complete(asyncio.ensure_future(self.send_message(message)))



	def send_valid_dataset_list(self, dataset, timestamp = None):
		"""
			@param: 
			Support two kinds of dataset
				1)	dataset = [(metric1, value1), (metric2, value2), ...] 
				or 
				2)	dataset = [(metric1, value1, timestamp1), (metric2, value2, timestamp2), ...]
		"""
		timestamp = int(time.time()) if timestamp is None else int(timestamp)
		message = ""

		# Generate message based on protocol
		# 1. plaintext
		# 2. pickle
		if self.protocol == "plaintext":
			message = self.generate_message_for_data_list(dataset, timestamp, self.plaintext_protocol_formatted_data, self.generate_message_for_plaintext)
		else:
			message = self.generate_message_for_data_list(dataset, timestamp, self.pickle_protocol_formatted_data, self.generate_message_for_pickle)

		# Sending Data
		self.loop.run_until_complete(asyncio.ensure_future(self.send_message(message)))



	def send_valid_dataset_dict(self, dataset, timestamp = None):
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



	def generate_message_for_data_list(self, dataset, timestamp, formate_function, generate_message_function):
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



	def generate_message_for_plaintext(self, listOfPlaintext):
		"""
			return the required message formate for protocol 'plaintext'
			@param: 
				listOfPlaintext: ["metric1 value1 timestamp1", "metric2 value2 timestamp2", ...]
				type: List of String
		"""
		return "\n".join(listOfPlaintext)



	def generate_message_for_pickle(self, listOfMetricTuples):
		"""
			@param: 
				listOfMetricTuples: [(metric1, (timestamp1, value1), (metric2, (timestamp2, value2), ...]
		"""
		payload = pickle.dumps(listOfMetricTuples, protocol=2)
		header = struct.pack("!L", len(payload))
		message = header + payload
		return message


	def plaintext_protocol_formatted_data(self, metric, value, timestamp):
		"""
			@return: required data formate when sending data through 'plaintext' protocol
			@return_type: String
		"""
		return " ".join([metric, value, timestamp])



	def pickle_protocol_formatted_data(self, metric, value, timestamp):
		"""
			@return: required data formate when sending data through 'pickle' protocol
			@return_type: Tuple
		"""		
		return (metric, (timestamp, value))



	def send_message(self, message):
		"""
			@message: data ready to sent to graphite server
		"""
		total_sent = 0
		message_size = len(message)
		while total_sent < message_size:
			try:
				sent = self.socket.send(message[total_sent:])
				if sent == 0:
					raise RuntimeError("socket connection broken")
				total_sent = total_sent + sent
			except socket.gaierror as e:
				raise AioGraphiteSendException("Fail to send data to %s, Error: %s" % (self.graphite_server_address, e)) 
			except Exception, e:
				raise AioGraphiteSendException("Unexpected exception while sending data to %s:%s" % self.graphite_server_address)
		return total_sent



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



	def to_graphite_valid_metric_name(self, metric_dir_list):
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
	return "."join([metrics_name_to_graphite(dir_name) for dir_name in metric_dir_list])

#########################################################
#########################################################
#########################################################

# Module Instance Variable
aiographite_send_instance = None



def init(graphite_server, graphite_port = DEFAULT_GRAPHITE_PICKLE_PORT, protocol_type = 'pickle'):
	global aiographite_send_instance
	if aiographite_send_instance:
		destory()

	# Check Init Protocol Type
	if protocol_type not in SUPPORT_PROTOCOLS:
		raise AioGraphiteSendException("%s is not Support Protocol Type!", protocol_type)

	# Construct an aiographite sending service instance
	aiographite_send_instance = AsyncioGraphiteSendService(graphite_server, graphite_port, protocol_type)
	return aiographite_send_instance



def send_single_data(metric_dir_list, value, timestamp = None):
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
	global aiographite_send_instance

	if not aiographite_send_instance:
		raise AioGraphiteSendException("Must call init before use!")

	# Sending data
	aiographite_send_instance.send_single_data(metric_dir_list, value, timestamp)



def send_single_valid_data(metric, value, timestamp = None):
	"""
		@metric: metric name, type: String
		@timestamp: type should be int
	"""
	global aiographite_send_instance

	if not aiographite_send_instance:
		raise AioGraphiteSendException("Must call init before use!")

	# Sending data
	aiographite_send_instance.send_single_valid_data(metric, value, timestamp)



def send_data_list(dataset, timestamp = None):
	"""
		@param: 
			Support two kinds of dataset

			1)	dataset = [(metric_dir_list, value1), (metric_dir_list, value2), ...] 

			or 

			2)	dataset = [(metric_dir_list1, value1, timestamp1), (metric_dir_list1, value2, timestamp2), ...]

		If you're very confident that the metric name is valid, then use <method: send_valid_dataset_list> instead.

		"""
	global aiographite_send_instance

	if not aiographite_send_instance:
		raise AioGraphiteSendException("Must call init before use!")

	# Sending Data
	aiographite_send_instance.send_dataset_list(dataset, timestamp)



def send_valid_dataset_list(dataset, timestamp = None):
	"""
		@param: 
		Support two kinds of dataset
			1)	dataset = [(metric1, value1), (metric2, value2), ...] 
			or 
			2)	dataset = [(metric1, value1, timestamp1), (metric2, value2, timestamp2), ...]
	"""

	global aiographite_send_instance

	if not aiographite_send_instance:
		raise AioGraphiteSendException("Must call init before use!")

	# Sending Data
	self.send_valid_dataset_list(dataset, timestamp)



def send_valid_dataset_dic(dataset, timestamp):
	"""
		Send data to graphite server when incoming data is in 'dict' format
		@param: dataset = {
								metric1 : value1,      // type ( string: int )
								metric2 : value2, 
								...
						  }

		metric1 (metric2, ...) are valid name for Graphite
	"""
	global aiographite_send_instance

	if not aiographite_send_instance:
		raise AioGraphiteSendException("Must call init before use!")

	# Sending Data
	self.send_valid_dataset_dic(dataset, timestamp)



def destory():
	"""
		Close TCP connection and destory the instance
	"""
	global aiographite_send_instance
	if not aiographite_send_instance:
		return False
	aiographite_send_instance.disconnect()
	aiographite_send_instance = None
	return True




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







