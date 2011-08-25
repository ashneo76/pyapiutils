#!/usr/bin/python

import urllib2, re, sys, optparse
from BeautifulSoup import BeautifulSoup 

site_url = 'http://www.transitchicago.com/mobile/'
base_url = site_url + 'traintracker.aspx'
stop_url = site_url + 'traintrackerstops.aspx?rid='
seta_url = site_url + 'traintrackerarrivals.aspx?sid='

# Utility methods
def convertHtml(s):
    matches = re.findall("&#\d+;", s)
    if len(matches) > 0:
        hits = set(matches)
        for hit in hits:
            name = hit[2:-1]
            try:
                entnum = int(name)
                s = s.replace(hit, unichr(entnum))
            except ValueError:
                pass

    matches = re.findall("&\w+;", s)
    hits = set(matches)
    amp = "&amp;"
    if amp in hits:
        hits.remove(amp)
    for hit in hits:
        name = hit[1:-1]
        if htmlentitydefs.name2codepoint.has_key(name):
            s = s.replace(hit, unichr(htmlentitydefs.name2codepoint[name]))
    s = s.replace(amp, "&")
    return s

# API
def getTrains():
    rtlist_pg = urllib2.urlopen(base_url).read()
    soup = BeautifulSoup(rtlist_pg)
    routes = []

    # Get divs containing train info
    # These belong to CSS class ttsp_routes_rt
    rt_divs = soup.findAll('div','ttsp_routes_rt')
    for rt_div in rt_divs:
        route = {}
        rt_color = rt_div['style'] # background-color: #123456;
        rt_name = rt_div.findNext('span','routename')     #routename
        rt_info = rt_div.findNext('span','routesubtext')  #routesubtext
        route['name'] = rt_name.string.strip()
        route['info'] = convertHtml(rt_info.string.strip())
        route['color']= (rt_color.split(' ')[1])[:-1]
        route['code'] = (route['name'].split(' ')[0]).lower() # Red Line
        routes.append(route)
    return routes

def getStopsByColor(rtcode):
    color_map = { 'red':'307', 'blue':'310', 'brown':'313', 'green':'312', 
                'orange':'314', 'purple':'308', 'pink':'311', 'yellow':'309' }
    return getStopsById(color_map[rtcode])

def getStopsById(rid):
    query_url = stop_url + rid
    stop_pg = urllib2.urlopen(query_url).read()
    soup = BeautifulSoup(stop_pg)
    stops = []

    # Get all stops. These belong to 
    # a tags that belong to the class buttonlink
    # the url/href contains the stopid
    stop_as = soup.findAll('a', 'buttonlink')
    for stop_a in stop_as:
        stop = {}
        sid = (stop_a['href']).split('=')[1]
        sname = stop_a.findNext('span', 'stopname').string.strip()
        stop['id'] = sid
        stop['name'] = convertHtml(sname)
        stops.append(stop)
    return stops

def getStopETA(sid):
    query_url = seta_url + sid
    eta_pg = urllib2.urlopen(query_url).read()
    soup = BeautifulSoup(eta_pg)

    # Stuff is in id DIV ctl02_pnlMain
    pnlmain_div = soup.findNext(attrs={'id':re.compile('pnlMain$')})
    time = pnlmain_div.findNext('div', 'ttmobile_instruction').string
    station = pnlmain_div.findNext('div', 'ttmobile_stationname').string
    eta_div = pnlmain_div.findNext('div', attrs={'id':'ttmobile_arrivalbuttons'})
    etas = eta_div.findAll('div')

    stop_etas = []
    curr_direction = ''
    for eta in etas:
        seta = {}
        if eta['class'].startswith('ttmobile_'):
            train = eta.findNext('span', 'nexttraindesc')
            teta = eta.findNext('span', 'nexttrainarrv')
            trainstr = train.string.strip()
            tr_col,sep,tr_dest = trainstr.partition('&gt;')
            print " % % " % tr_col, tr_dest 
            seta['color'] = tr_col.strip()
            seta['dest'] = tr_col.strip()
            eta_time = teta.findNext('b').string
            eta_time_acc = teta.string
            seta['eta'] = eta_time + eta_time_acc
            stop_etas.append(seta)
        else:
            continue

    return stop_etas

# API interface
def printTrainList(pretty):
    routes = getTrains()

    if(pretty):
        for rt in routes:
            print rt['name'] + ': ' + rt['info'] + ' (' + rt['code'] + ')'
    else:
        for rt in routes:
            print rt['name'] + ',' + rt['info'] + ',' + rt['code'] + ',' + rt['color']

def printStops(rid, pretty):
    stops = getStopsByColor(rid)
    
    if(pretty):
        for stop in stops:
            print stop['name'] + ': ' + stop['id']
    else:
        for stop in stops:
            print stop['name'] + ',' + stop['id']

def printETA(sid, pretty):
    etas = getStopETA(sid)
    
    if(pretty):
        for eta in etas:
            print eta['color'] + ' to ' + eta['dest'] + ' arriving in ' + eta['eta']
    else:
        for eta in etas:
            print eta['color'] + ',' + eta['dest'] + ',' + eta['eta']

# Main method
if __name__ == '__main__':
    parser = optparse.OptionParser('''
CTA Train Tracker Interface
    An API to access the CTA Train tracker web interface. Uses BeautifulSoup to scrape the mobile website.''')

    parser.add_option('-r', '--routes', dest='routes', action='store_true',
                    help='Display system routes and route codes', default=False)
    parser.add_option('-s', '--stops', dest='stops', action='store_true',
                    help='Display stops on a given route', default=False)
    parser.add_option('-e', '--eta', dest='stops', action='store_false',
                    help='Display ETA on a given stop ID')
    parser.add_option('-p', '--pretty', dest='pretty', action='store_true',
                    help='Print nicely formatted output', default=True)
    parser.add_option('-c', '--csv', dest='pretty', action='store_false',
                    help='Print data as CSV')
    
    (options, args) = parser.parse_args()

    try:
        if options.routes:
            printTrainList(options.pretty)
        elif options.stops:
            printStops(args[0], options.pretty)
        else:
            printETA(args[0], options.pretty)
    except urllib2.URLError:
        print 'Unable to connect. No network connection?'
    except KeyboardInterrupt:
        print 'Interrupted. Quitting.'
    except SystemExit:
        print 'System exit.'
