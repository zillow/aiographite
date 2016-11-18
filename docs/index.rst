.. aiographite documentation master file, created by
   sphinx-quickstart on Wed Aug 17 13:50:33 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

aiographite
===========

.. image:: https://travis-ci.org/zillow/aiographite.svg?branch=master
    :alt: build status
    :target: https://travis-ci.org/zillow/aiographite

.. image:: https://coveralls.io/repos/github/zillow/aiographite/badge.svg?branch=master
    :alt: coverage status
    :target: https://coveralls.io/github/zillow/aiographite?branch=master


An asyncio library for graphite.


---------------------
What is aiographite ?
---------------------

aiographite is Python3 library ultilizing asyncio, designed
to help Graphite users to send data into graphite easily.


----------------------
Quick start
----------------------

Let's get started.

.. code::

    from aiographite.aiographite import connect

    """
      Initialize a aiographite instance
    """
    loop = asyncio.get_event_loop()
    plaintext_protocol = PlaintextProtocol()
    graphite_conn = await aiographite.connect(*httpd.address, plaintext_protocol, loop=loop)


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


Contents:

.. toctree::
   :maxdepth: 2

   installation
   client
   protocols
   encoder
   example
   development

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
