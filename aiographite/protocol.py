from typing import Tuple, List
import pickle
import struct


class PlaintextProtocol:

    def _format_data(self, metric: str, value: int, timestamp: int) -> str:
        """
            @return: required data formate when sending data
                     through 'plaintext' protocol
            @return_type: String
        """
        formatted_data = " ".join([metric, str(value), str(timestamp)])
        return formatted_data + "\n"

    def generate_message(self,
                         listOfTuples: List[Tuple[str, int, int]]) -> bytes:
        """
            return the required message formate for protocol 'plaintext'
            @param:
                listOfTuples:
                    [(metric1, value1, timestamp1),
                     (metric2, value2, timestamp2), ...]
        """
        listOfPlaintext = []
        for metric, value, timestamp in listOfTuples:
            listOfPlaintext.append(self._format_data(metric, value, timestamp))
        return "".join(listOfPlaintext).encode('ascii')


class PickleProtocol:

    def _format_data(self, metric: str,
                     value: int,
                     timestamp: int) -> Tuple[str, Tuple[int, int]]:
        """
            @return: required data formate when sending data
                     through 'pickle' protocol
            @return_type: Tuple
        """
        return (metric, (timestamp, value))

    def generate_message(self,
                         listOfTuples: List[Tuple[str, int, int]]) -> bytes:
        """
            @param:
                listOfTuples: [(metric1, value1, timestamp1),
                               (metric2, value2, timestamp2), ...]
        """
        listOfTargetTuples = []
        for metric, value, timestamp in listOfTuples:
            listOfTargetTuples.append(
                    self._format_data(metric, value, timestamp)
                )
        payload = pickle.dumps(listOfTargetTuples, protocol=2)
        header = struct.pack("!L", len(payload))
        message = header + payload
        return message
