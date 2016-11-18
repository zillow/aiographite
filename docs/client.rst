===========
AIOGraphite
===========

AIOGraphite is a Graphite client class, ultilizing asyncio,
designed to help Graphite users to send data into graphite easily.


.. code::

    from aiographite.aiographite import connect

    """
      Initialize a aiographite instance
    """
    loop = asyncio.get_event_loop()
    plaintext_protocol = PlaintextProtocol()
    graphiteConn = await aiographite.connect(*httpd.address, plaintext_protocol, loop=loop)


    """
      Send a tuple (metric, value , timestamp)
    """
    graphiteConn.send(metric, value, timestamp)


    """
      Send a list of tuples List[(metric, value , timestamp)]
    """
    graphiteConn.send_multiple(list)


    """
      aiographite library also provides GraphiteEncoder module,
      which helps users to send valid metric name to graphite.
      For Example: (metric_parts, value ,timestamp)
    """
    metric = graphiteConn.clean_and_join_metric_parts(metric_parts)
    graphiteConn.send(metric, value, timestamp)


    """
      Close connection
    """
    graphiteConn.close()


------------------
Full API Reference
------------------

.. autoclass:: aiographite.aiographite.AIOGraphite
    :members: send, send_multiple, close, clean_and_join_metric_parts
