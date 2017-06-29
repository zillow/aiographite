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
    graphite_conn = await aiographite.connect(*httpd.address, plaintext_protocol, loop=loop, timeout=None)


    """
      Send a tuple (metric, value , timestamp)
    """
    graphite_conn.send(metric, value, timestamp)


    """
      Send a list of tuples List[(metric, value , timestamp)]
    """
    graphite_conn.send_multiple(list)


    """
      aiographite library also provides GraphiteEncoder module,
      which helps users to send valid metric name to graphite.
      For Example: (metric_parts, value ,timestamp)
    """
    metric = graphite_conn.clean_and_join_metric_parts(metric_parts)
    graphite_conn.send(metric, value, timestamp)


    """
      Close connection
    """
    graphite_conn.close()


------------------
Full API Reference
------------------

.. autoclass:: aiographite.aiographite.AIOGraphite
    :members: send, send_multiple, close, clean_and_join_metric_parts
