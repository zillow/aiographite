Example
=======

A simple example.

.. code::

    from aiographite.protocol import PlaintextProtocol
    from aiographite.aiographite import connect
    import time
    import asyncio


    LOOP = asyncio.get_event_loop()
    SERVER = '127.0.0.1'
    PORT = 2003


    async def test_send_data():
      # Initiazlize an aiographite instance
      plaintext_protocol = PlaintextProtocol()
      graphiteConn = await connect(SERVER, PORT, plaintext_protocol, loop=LOOP)

      # Send data
      timestamp = time.time()
      for i in range(10):
        await graphiteConn.send("yun_test.aiographite", i, timestamp + 60 * i)))


    def main():
      LOOP.run_until_complete(test_send_data())
      LOOP.close()


    if __name__ == '__main__':
      main()
