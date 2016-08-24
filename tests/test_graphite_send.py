import pytest
from aiographite.aiographite import AIOGraphite
from aiographite.protocol import PlaintextProtocol, PickleProtocol
import asyncio
from asyncio import test_utils

DEFAULT_GRAPHITE_PLAINTEXT_PORT = 2003
DEFAULT_GRAPHITE_PICKLE_PORT = 2004


# Unit Tests
@pytest.mark.parametrize("metric, value, timestamp", [
    ('zillow', 124, 234),
    ('trulia', 223, 435),
    ('hotpad', 53534, 32425),
])
def test_pickle_protocol_formatted_data(metric, value, timestamp):
    pickle = PickleProtocol()
    data = pickle.format_data(metric, value, timestamp)
    expected_data = (metric, (timestamp, value))
    assert data == expected_data


@pytest.mark.parametrize("metric, value, timestamp, expected_data", [
    ('M M M', 124, 234, 'M M M 124 234\n'),
    ('python ruby java', 223, 435, 'python ruby java 223 435\n'),
    ('C C++ Perl', 53534, 32425, 'C C++ Perl 53534 32425\n'),
])
def test_plaintext_protocol_formatted_data(metric, value,
                                           timestamp, expected_data):
    plaintext = PlaintextProtocol()
    data = plaintext.format_data(metric, value, timestamp)
    assert data == expected_data


def test_generate_message_for_pickle():
    pickle = PickleProtocol()
    tuple_list = [('a', (123, 456)), ('b', (123, 456)), ('c', (876, 987))]
    expected_message = (
        b'\x00\x00\x00B\x80\x02]q\x00(X\x01\x00\x00\x00aq\x01'
        b'K{M\xc8\x01\x86q\x02\x86q\x03X\x01\x00\x00\x00'
        b'bq\x04K{M\xc8\x01\x86q\x05\x86q\x06X\x01\x00\x00'
        b'\x00cq\x07Ml\x03M\xdb\x03\x86q\x08\x86q\te.')
    assert pickle.generate_message(tuple_list) == expected_message


def test_generate_message_for_plaintext():
    plaintext_list = ["metric1 value1 timestamp1\n",
                      "metric2 value2 timestamp2\n",
                      "metric3 value3 timestamp3\n"]
    expected_message = (
        b'metric1 value1 timestamp1\n'
        b'metric2 value2 timestamp2\n'
        b'metric3 value3 timestamp3\n')
    plaintext = PlaintextProtocol()
    message = plaintext.generate_message(plaintext_list)
    assert message == expected_message


@pytest.mark.parametrize("metric_parts, expected_metric_name", [
    (['sproc performance', 'velo@zillow.com', '::EH12'],
     'sproc%20performance.velo%40zillow%2Ecom.%3A%3AEH12'),
    (['dit_400', 'zpid@zillow.com', 'EHT::disk_usage_per_host'],
     'dit_400.zpid%40zillow%2Ecom.EHT%3A%3Adisk_usage_per_host')
])
def test_clean_and_join_metric_parts(metric_parts, expected_metric_name):
    with test_utils.run_test_server() as httpd:
        loop = asyncio.get_event_loop()
        plaintext_protocol = PlaintextProtocol()
        aiographite = AIOGraphite(*httpd.address,
                                  plaintext_protocol, loop=loop)
        metric_name = aiographite.clean_and_join_metric_parts(metric_parts)
        assert metric_name == expected_metric_name


def test_generate_message_for_data_list(metric_value_timestamp_list,
                                        timestamp):
    with test_utils.run_test_server() as httpd:
        loop = asyncio.get_event_loop()
        plaintext_protocol = PlaintextProtocol()
        aiographite = AIOGraphite(*httpd.address,
                                  plaintext_protocol, loop=loop)
        message = aiographite._generate_message_for_data_list(
            metric_value_timestamp_list,
            timestamp,
            plaintext_protocol.format_data,
            plaintext_protocol.generate_message
        )
        expected_message = (
            b'zillow 124 1471640958\ntrulia 223 1471640923\n'
            b'hotpad 53534 1471640943\nstreeteasy 13424 1471640989\n')
        assert message == expected_message


def test_open_connection():
    with test_utils.run_test_server() as httpd:
        loop = asyncio.get_event_loop()
        plaintext_protocol = PlaintextProtocol()
        aiographite = AIOGraphite(*httpd.address,
                                  plaintext_protocol, loop=loop)
        loop.run_until_complete(aiographite.connect())
        reader = aiographite._reader
        writer = aiographite._writer
        assert reader is not None
        assert writer is not None


def test_disconnect():
    with test_utils.run_test_server() as httpd:
        loop = asyncio.get_event_loop()
        plaintext_protocol = PlaintextProtocol()
        aiographite = AIOGraphite(*httpd.address,
                                  plaintext_protocol, loop=loop)
        loop.run_until_complete(aiographite.connect())
        aiographite.disconnect()
        reader = aiographite._reader
        writer = aiographite._writer
        assert reader is None
        assert writer is None


def test_send_message_and_send():
    loop = asyncio.get_event_loop()

    async def server_handler(reader, writer):
        data = (await reader.read())
        writer.write(data)
        await writer.drain()
        writer.close()

    async def test_send_message():
        plaintext_protocol = PlaintextProtocol()
        aiographite = AIOGraphite(
            '127.0.0.1', DEFAULT_GRAPHITE_PLAINTEXT_PORT,
            plaintext_protocol, loop=loop)
        message = "hello world !"
        await aiographite.connect()
        await aiographite._send_message(message.encode("ascii"))
        reader = aiographite._reader
        writer = aiographite._writer
        writer.write_eof()
        await  writer.drain()
        data = (await reader.read()).decode("utf-8")
        writer.close()
        aiographite.disconnect()
        assert message == data

    async def test_send():
        plaintext_protocol = PlaintextProtocol()
        aiographite = AIOGraphite('127.0.0.1', DEFAULT_GRAPHITE_PLAINTEXT_PORT,
                                  plaintext_protocol, loop=loop)
        await aiographite.connect()
        metric = 'sproc%20performance.velo%40zillow%2Ecom.%3A%3AEH12'
        value = 3232
        timestamp = 1471640923
        message = ('sproc%20performance.velo%40zillow%2E'
                   'com.%3A%3AEH12 3232 1471640923\n')
        await aiographite.send(metric, value, timestamp)
        reader = aiographite._reader
        writer = aiographite._writer
        writer.write_eof()
        await  writer.drain()
        data = (await reader.read()).decode("utf-8")
        writer.close()
        aiographite.disconnect()
        assert message == data

    async def test_send_multiple():
        pickle = PickleProtocol()
        aiographite = AIOGraphite('127.0.0.1', DEFAULT_GRAPHITE_PLAINTEXT_PORT,
                                  pickle, loop=loop)
        await aiographite.connect()
        dataset = [('sproc%20performance.velo%40zillow%2Ecom.%3A%3AEH12',
                    3233, 1471640923),
                   ('dit_400.zpid%40zillow%2Ecom.EHT%3A%3Adisk_usage_per_host',
                    2343, 1471640976)]
        await aiographite.send_multiple(dataset)
        reader = aiographite._reader
        writer = aiographite._writer
        writer.write_eof()
        await  writer.drain()
        data = (await reader.read())
        writer.close()
        aiographite.disconnect()
        message = (
            b"\x00\x00\x00\x9c\x80\x02]q\x00(X2\x00\x00\x00sproc"
            b"%20performance.velo%40zillow%2Ecom.%3A%3AEH12q\x01J[u\xb7WM"
            b"\xa1\x0c\x86q\x02\x86q\x03X8\x00\x00\x00dit_400.zpid%40zillow"
            b"%2Ecom.EHT%3A%3Adisk_usage_per_hostq\x04J\x90u\xb7WM'\t\x86q"
            b"\x05\x86q\x06e.")
        assert message == data

    def run(task, loop):
        return loop.run_until_complete(asyncio.ensure_future(task, loop=loop))

    make_server = asyncio.start_server(server_handler, '127.0.0.1',
                                       DEFAULT_GRAPHITE_PLAINTEXT_PORT)
    server = run(make_server, loop)
    run(test_send_message(), loop)
    run(test_send(), loop)
    run(test_send_multiple(), loop)
    server.close()
