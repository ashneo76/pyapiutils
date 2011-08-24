#!/usr/bin/python

import location
import gobject

ACC_COARSE = 1000

prev_loc = [0,0]		# Previous fix
static_sample_cnt = 5	# Indicates the number of same gps values required.
gps_interval = 5		# GPS_FIX interval in seconds 
accuracy = ACC_COARSE

def on_error(control, error, data):
    if error == location.ERROR_USER_REJECTED_DIALOG:
        print "User didn't enable requested methods"
    elif error == location.ERROR_USER_REJECTED_SETTINGS:
        print "User changed settings, which disabled location"
    elif error == location.ERROR_BT_GPS_NOT_AVAILABLE:
        print "Problems with BT GPS"
    elif error == location.ERROR_METHOD_NOT_ALLOWED_IN_OFFLINE_MODE:
        print "Requested method is not allowed in offline mode"
    elif error == location.ERROR_SYSTEM:
        print "System error"
    data.quit()

def on_changed(device,control):
    global prev_loc
    global static_sample_cnt, accuracy

    if not device:
        return
    if device.fix:
        if device.fix[1] & location.GPS_DEVICE_LATLONG_SET:
            # print "lat = %f, long = %f" % device.fix[4:6]
            dla = (prev_loc[0]-device.fix[4])*accuracy
            dlo = (prev_loc[1]-device.fix[5])*accuracy
            if (dla>-1 and dla<1) and (dlo>-1 and dlo<1):
                static_sample_cnt = static_sample_cnt - 1
            else:
                static_sample_cnt = 5
            # print "%d" % static_sample_cnt
            prev_loc = device.fix[4:6]
            if static_sample_cnt == 0:
                # print "STABLE!!! @ %f,%f" % prev_loc
                control.stop()
        #if device.fix[1] & location.GPS_DEVICE_ALTITUDE_SET:
        #   print "alt = %f" % device.fix[7]
        # control.stop() commented out to allow continuous loop for a reliable fix - press ctrl c to break the loop, or program your own way of exiting)

def on_stop(control, data):
    #print "quitting"
    data.quit()
 
def start_location(control):
    control.start()
    return False
    
def getDevLocation():
    global prev_loc
    loop = gobject.MainLoop()
    control = location.GPSDControl.get_default()
    device = location.GPSDevice()
    control.set_properties(preferred_method=location.METHOD_USER_SELECTED,
                           preferred_interval=location.INTERVAL_DEFAULT)
     
    control.connect("error-verbose", on_error, loop)
    device.connect("changed", on_changed, control)
    control.connect("gpsd-stopped", on_stop, loop)
     
    gobject.idle_add(start_location, control)
     
    loop.run()
    return "%f,%f"%prev_loc

if __name__ == "__main__":
    print getDevLocation()
