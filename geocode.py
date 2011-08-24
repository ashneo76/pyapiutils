#!/usr/bin/python

# Depends:
#   urllib2
#   simplejson
#
# Author: Ashish Shah (ashneo76@gmail.com)

import urllib, urllib2
import simplejson as sj
import sys, optparse

latlon='0,0'
address=''
geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json?sensor=true&'

def geoencode(address):
    global geocode_url
    query = geocode_url + 'address=' + urllib.quote_plus(address)
    resp_file = urllib2.urlopen(query)
    resp_str = resp_file.read()
    # print resp_str
    resp_j = sj.loads(resp_str)
    status = resp_j['status']

    if(status == 'OK'):
        results = resp_j['results']
        matches = ""
        for res in results:
            # types: same as below
            # formatted_address
            # address_components is an [] of
            #   { long_name, short_name, types }
            # geometry is
            #   location: { "lat"/"lng" }
            #   viewport:
            #       southwest: { "lat"/"lng" }
            #       northeast: { "lat"/"lng" }
            l = (res['geometry'])['location']
            latlng = repr(l["lat"]) + ',' + repr(l["lng"])
            matches = matches + res['formatted_address'] + ' [' + latlng  + ']\n'
        return matches[:-1]
    elif(status == 'ZERO_RESULTS'):
        return '0 results'
    else:
        return status

def geodecode(latlng):
    global geocode_url
    query = geocode_url+'latlng='+latlng
    resp_file = urllib2.urlopen(query)
    resp_str = resp_file.read()
    # print resp_str
    resp_j = sj.loads(resp_str)
    status = resp_j['status']

    if(status == 'OK'):
        results = resp_j['results']
        matches = ""
        for res in results:
            # address_components is an [] of
            #   { "long_name": "Illinois",
            #     "short_name": "IL",
            #     "types": [ street_number/route/locality/administrative_area_level_2/
            #                administrative_area_level_1/country/postal_code/neighborhood,
            #                (implies .../street name/city/county/state/.../zipcode/hood)
            #                "political" (optional)
            #              ]
            #   }
            # formatted_address is string
            # geometry is a tuple
            #   { "bounds": { "northeast"/"southwest": { "lat"/"lng": <float> } }
            #     "location": { "lat"/"lng": <float> }
            #     "location_type": "ROOFTOP"/"RANGE_INTERPOLATED"/
            #                       "GEOMETRIC_CENTER"/"APPROXIMATE"
            #     "viewport": { "northeast"/"southwest": { "lat"/"lng": <float> } }
            #   }
            # types is an []
            #   [ "neighborhood", "political"]
            matches = matches + res['formatted_address'] + '\n'
        return matches[:-1]
        #print results
    elif(status == 'ZERO_RESULTS'):
        return '0 results'
    else:
        return status

if __name__ == '__main__':
    parser = optparse.OptionParser('''
Google Geocode API Interface
        Geocodes an address or reverse geocodes a location using Google Maps API.
        Example: geocode -l <lat,long> OR geocode -a <address>''')
    parser.add_option("-l","--location", dest="loc", action="store_true",
                        help="Comma separated <latitude,longitude> pair")
    parser.add_option("-a","--address", dest="loc", action="store_false", default=False,
                        help="Address string")
    (options, args) = parser.parse_args()
    #print args

    try:
        if options.loc:
            print geodecode(args[0])
        else:
            print geoencode(args[0])
    except urllib2.URLError:
        print 'Unable to connect. No network connection?'
    except KeyboardInterrupt:
        print "Interrupted. Quitting."
    except SystemExit:
        print "System exit."
