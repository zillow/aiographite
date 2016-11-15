===========
AIOGraphite
===========

AIOGraphite is a Graphite client class, ultilizing asyncio,
designed to help Graphite users to send data into graphite easily.


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


------------------
Full API Reference
------------------

.. autoclass:: aiographite.aiographite.AIOGraphite
