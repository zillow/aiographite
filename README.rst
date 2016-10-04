aiographite
===========

.. image:: https://travis-ci.org/zillow/aiographite.svg?branch=master
    :alt: build status
    :target: https://travis-ci.org/zillow/aiographite

An asyncio library for graphite.

---------------------
What is aiographite ?
---------------------

aiographite is Python3 library ultilizing asyncio, designed
to help Graphite users to send data into graphite easily.


----------------------
Installing it globally
----------------------

You can install aiographite globally with any Python package manager:

.. code::

    pip install aiographite


----------------------
Quick start
----------------------

Let's get started.

.. code::

    """
      Initialize a aiographite instance
    """
    loop = asyncio.get_event_loop()
    plaintext_protocol = PlaintextProtocol()
    aiographite = AIOGraphite(*httpd.address, plaintext_protocol, loop = loop)
    await aiographite.connect()


    """
      Send a tuple (metric, value , timestamp)
    """
    aiographite.send(metric, value, timestamp)


    """
      Send a list of tuples List[(metric, value , timestamp)]
    """
    aiographite.send_multiple(list)


    """
      aiographite library also provides GraphiteEncoder module,
      which helps users to send valid metric name to graphite.
      For Example: (metric_parts, value ,timestamp)
    """
    metric = aiographite.clean_and_join_metric_parts(metric_parts)
    aiographite.send(metric, value, timestamp)


----------------------
Example
----------------------

A simple example.

.. code::

    from aiographite.protocol import PlaintextProtocol
    from aiographite.aiographite import AIOGraphite
    import time
    import asyncio


    LOOP = asyncio.get_event_loop()
    SERVER = '127.0.0.1'
    PORT = 2003


    async def send_data(metric, timestamp, value):
      plaintext_protocol = PlaintextProtocol()
      aiographite_instance = AIOGraphite(SERVER, PORT, plaintext_protocol, loop = LOOP)
      await aiographite_instance.connect()
      await aiographite_instance.send(metric, value, timestamp)


    def main():
      tasks = []
      timestamp = int(time.time())
      for i in range(10):
        tasks.append(asyncio.ensure_future(send_data("yun_test.aiographite", timestamp + 60 * i, i)))
      LOOP.run_until_complete(asyncio.gather(*tasks))
      LOOP.close()

    if __name__ == '__main__':
      main()


----------------------
Graphite setup
----------------------

Do not have graphite instances ? Set up a graphite instance on your local machine! 

Please refer:

* https://github.com/yunstanford/MyGraphite
* https://github.com/yunstanford/GraphiteSetup
