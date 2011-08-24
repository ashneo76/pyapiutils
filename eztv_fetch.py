#!/usr/bin/env python

import urllib2
import sys

search_url = 'http://eztv.it/search'
postdata = None

query = ''

request = urllib2.Request(search_url, postdata)
data = urllib2.open(request)
results = data.read()
