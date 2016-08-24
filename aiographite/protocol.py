from typing import Tuple, List
import pickle
import struct


class PlaintextProtocol:

    def format_data(self, metric: str, value: int, timestamp: int) -> str:
        """
            @return: required data formate when sending data
                     through 'plaintext' protocol
            @return_type: String
        """
        formatted_data = " ".join([metric, str(value), str(timestamp)])
        return formatted_data + "\n"

    def generate_message(self, listOfPlaintext: List[str]) -> bytes:
        """
            return the required message formate for protocol 'plaintext'
            @param:
                listOfPlaintext:
                    ["metric1 value1 timestamp1",
                     "metric2 value2 timestamp2", ...]
                type: List of String
        """
        return "".join(listOfPlaintext).encode('ascii')


class PickleProtocol:

    def format_data(self, metric: str,
                    value: int,
                    timestamp: int) -> Tuple[str, Tuple[int, int]]:
        """
            @return: required data formate when sending data
                     through 'pickle' protocol
            @return_type: Tuple
        """
        return (metric, (timestamp, value))

    def generate_message(self, listOfMetricTuples: List[Tuple]) -> bytes:
        """
            @param:
                listOfMetricTuples: [(metric1, (timestamp1, value1),
                                     (metric2, (timestamp2, value2), ...]
        """
        payload = pickle.dumps(listOfMetricTuples, protocol=2)
        header = struct.pack("!L", len(payload))
        message = header + payload
        return message
