#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib

"""
	Graphite expects everything to be just ASCII to split/processing them, and then make directories based on metric name.
	So any special name not allow to appear in directory/file name is not supported by Graphite.
"""

"""
	Naming metrics schema:
		<namespace>.<instrumented section>.<target (noun)>.<action (past tense verb)>
"""

"""
	Limitation and explaination:

	Since we are using IDNA(International Domain Name in Application) rules, there are several limitations we should pay attention to.

	The conversions between ASCII and non-ASCII forms of a domain name are accomplished by algorithms called ToASCII and ToUnicode. 
	These algorithms are not applied to the domain name as a whole, but rather to individual labels. For example, 
	if the domain name is www.example.com, then the labels are www, example, and com. ToASCII or ToUnicode are applied 
	to each of these three separately.

	The details of these two algorithms are complex, and are specified in RFC 3490. The following gives an overview of their function.

	ToASCII leaves unchanged any ASCII label, but will fail if the label is unsuitable for the Domain Name System. 
	If given a label containing at least one non-ASCII character, ToASCII will apply the Nameprep algorithm, which converts the 
	label to lowercase and performs other normalization, and will then translate the result to ASCII using Punycode[16] before 
	prepending the four-character string "xn--".[17] This four-character string is called the ASCII Compatible Encoding (ACE) prefix, 
	and is used to distinguish Punycode encoded labels from ordinary ASCII labels. The ToASCII algorithm can fail in several ways; 
	for example, the final string could exceed the 63-character limit of a DNS name. A label for which ToASCII fails cannot be used 
	in an internationalized domain name.

	FAIL CASES:
	'.fd': starting with 'dot'
	'a..a': continuous 'dot'
	very long string: exceed the 63-character

"""


"""
	For special characters :
	1. 	The dot (.) is a special character because it delineates each metric’s path component, 
		but this is an easy fix; just substitute all dots for underscores or '%2E'. 
		For example, www.zillow.com => www_zillow_com
	2   For the rest of the special characters(except dot), just URL any metric name with 
		special characters to make it valid for Graphite, and then URL decode it when we need to
		reconstruct the information
"""




# Naming Metrics:
# <section_name>.<section_name>.<section_name>.<section_name>
def metrics_name_to_graphite(section_name):
	"""
		@param:   Section Name  (could include any character)
		@return:  valid metric name for graphite
	"""
	valid_graphite_metric_name = ""
	try:
		valid_graphite_metric_name = urllib.quote(unicode(section_name, 'utf-8').encode('idna')).replace(".", "%2E")
	except Exception, e:
		raise e
	return valid_graphite_metric_name
	

def metrics_name_from_graphite(idna_str):
	"""
		@param: valid metric name of graphite
		@return: the original name
	"""
	display_metric_name = ""
	try:
		display_metric_name = urllib.unquote(idna_str).decode('idna').encode('utf-8')
	except Exception, e:
		raise e
	return display_metric_name


def dummy_data():
	print '=== This is a simple example ===='
	name = 'sproc performance.test*feature_velocity@zillow.com hello world'
	print name
	print '=== Convert to Graphite valid metric name >>>'
	to_graphite = metrics_name_to_graphite(name)
	print to_graphite
	print '=== Convert the Graphite valid metric name back to the original name >>>'
	from_graphite = metrics_name_from_graphite(to_graphite)
	print from_graphite
	print '============= Test Consistency ===============', name == from_graphite

def main():
	dummy_data()

if __name__ == '__main__':
	main()


