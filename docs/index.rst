.. aiographite documentation master file, created by
   sphinx-quickstart on Wed Aug 17 13:50:33 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to aiographite's documentation!
=======================================

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

Contents:

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

