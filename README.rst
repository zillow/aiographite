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

Simple example for quick start.

.. code::

    """
      Initialize a aiographite instance
    """
    loop = asyncio.get_event_loop()
    plaintext_protocol = PlaintextProtocol()
    aiographite = AIOGraphite(*httpd.address, plaintext_protocol, loop = loop)
    await aiographite.connect_to_graphite()

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
