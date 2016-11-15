Example
=======

A simple example.

.. code::

    from aiographite.protocol import PlaintextProtocol
    from aiographite.aiographite import AIOGraphite
    import time
    import asyncio


    LOOP = asyncio.get_event_loop()
    SERVER = '127.0.0.1'
    PORT = 2003


    def test_send_data():
      # Initiazlize an aiographite instance
      plaintext_protocol = PlaintextProtocol()
      aiographite_instance = AIOGraphite(SERVER, PORT, plaintext_protocol, loop = LOOP)

      # Connect to graphite server
      LOOP.run_until_complete(aiographite_instance.connect())

      # Send data
      tasks = []
      timestamp = time.time()
      for i in range(10):
        tasks.append(asyncio.ensure_future(aiographite_instance.send("yun_test.aiographite", i, timestamp + 60 * i)))
      LOOP.run_until_complete(asyncio.gather(*tasks))
      LOOP.close()  


    def main():
      test_send_data()


    if __name__ == '__main__':
      main()
