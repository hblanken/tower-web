#!/usr/bin/env python

from dronekit import connect, VehicleMode
from pymavlink import mavutil
from Queue import Queue
from flask import Flask, render_template, jsonify, Response, request
import time
import json
import urllib
import atexit
import os
import sys
import socket
from threading import Thread
from subprocess import Popen
from flask import render_template
from flask import Flask, Response
from datetime import datetime

vehicle = None

# Allow us to reuse sockets after the are bound.
# http://stackoverflow.com/questions/25535975/release-python-flask-port-when-script-is-terminated
socket.socket._bind = socket.socket.bind
def my_socket_bind(self, *args, **kwargs):
    self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return socket.socket._bind(self, *args, **kwargs)
socket.socket.bind = my_socket_bind

def sse_encode(obj, id=None):
    return "data: %s\n\n" % json.dumps(obj)

def state_msg():
    if vehicle.location.global_relative_frame.lat == None:
        raise Exception('no position info')
    if vehicle.armed == None:
        raise Exception('no armed info')
    return {
        "armed": vehicle.armed,
        "alt": vehicle.location.global_relative_frame.alt,
        "mode": vehicle.mode.name,
        "heading": vehicle.heading or 0,
        "lat": vehicle.location.global_relative_frame.lat,
        "lon": vehicle.location.global_relative_frame.lon
    }

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html', branding=False)

listeners_location = []
listeners_location

from threading import Thread
import time
def tcount():
    while True:
        time.sleep(0.25)
        try:
            msg = state_msg()
            for x in listeners_location:
                x.put(msg)
        except Exception as e:
            pass
t = Thread(target=tcount)
t.daemon = True
t.start()

@app.route("/api/sse/state")
def api_sse_location():
    def gen():
        q = Queue()
        listeners_location.append(q)
        try:
            while True:
                result = q.get()
                ev = sse_encode(result)
                yield ev.encode()
        except GeneratorExit: # Or maybe use flask signals
            listeners_location.remove(q)

    return Response(gen(), mimetype="text/event-stream")

# @app.route("/api/location", methods=['GET', 'POST', 'PUT'])
# def api_location():
#     if request.method == 'POST' or request.method == 'PUT':
#         try:
#             data = request.get_json()
#             (lat, lon) = (float(data['lat']), float(data['lon']))
#             goto(lat, lon)
#             return jsonify(ok=True)
#         except Exception as e:
#             print(e)
#             return jsonify(ok=False)
#     else:
#         return jsonify(**location_msg())


@app.route("/api/arm", methods=['POST', 'PUT'])
def api_location():
    if request.method == 'POST' or request.method == 'PUT':
        try:
            vehicle.armed = True
            vehicle.flush()
            return jsonify(ok=True)
        except Exception as e:
            print(e)
            return jsonify(ok=False)

@app.route("/api/mode", methods=['POST', 'PUT'])
def api_mode():
    if request.method == 'POST' or request.method == 'PUT':
        try:
            vehicle.mode = VehicleMode(request.json['mode'].upper())
            vehicle.flush()
            return jsonify(ok=True)
        except Exception as e:
            print(e)
            return jsonify(ok=False)

def connect_to_drone():
    global vehicle

    print 'connecting to drone...'
    while not vehicle:
        try:
            vehicle = connect(sys.argv[1], wait_ready=True, rate=10)
        except Exception as e:
            print 'waiting for connection... (%s)' % str(e)
            time.sleep(2)

    # if --sim is enabled...
    vehicle.parameters['ARMING_CHECK'] = 0
    vehicle.flush()

    print 'connected!'

# Hanno added       
@app.route("/api/takeoff", methods=['POST', 'PUT'])
def arm_and_takeoff():
    if request.method == 'POST' or request.method == 'PUT':
        try:
            print "Basic pre-arm checks"
            # Don't try to arm until autopilot is ready
            while not vehicle.is_armable:
                print " Waiting for vehicle to initialise..."
                time.sleep(1)

            print "Arming motors"
            # Copter should arm in GUIDED mode
            vehicle.mode    = VehicleMode("GUIDED")
            vehicle.armed   = True

            # Confirm vehicle armed before attempting to take off
            while not vehicle.armed:
                print " Waiting for arming..."
                time.sleep(1)

            print "Taking off!"
            vehicle.simple_takeoff(10) # Take off to target altitude
            vehicle.flush()
            return jsonify(ok=True)
            # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
            #  after Vehicle.simple_takeoff will execute immediately).
            #while True:
            #        print " Altitude: ", vehicle.location.global_relative_frame.alt
            #Break and return from function just below target altitude.
            #        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95:
            #            print "Reached target altitude"
            #            break
            #time.sleep(1)

        except Exception as e:
            print(e)
            return jsonify(ok=False)
        
def condition_yaw(heading, relative=False):
##    """
##    Send MAV_CMD_CONDITION_YAW message to point vehicle at a specified heading (in degrees).
##
##    This method sets an absolute heading by default, but you can set the `relative` parameter
##    to `True` to set yaw relative to the current yaw heading.
##
##    By default the yaw of the vehicle will follow the direction of travel. After setting 
##    the yaw using this function there is no way to return to the default yaw "follow direction 
##    of travel" behaviour (https://github.com/diydrones/ardupilot/issues/2427)
##
##    For more information see: 
##    http://copter.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/#mav_cmd_condition_yaw
##    """
    if relative:
        is_relative = 1 #yaw relative to direction of travel
    else:
        is_relative = 0 #yaw is an absolute angle
    # create the CONDITION_YAW command using command_long_encode()
    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_CONDITION_YAW, #command
        0, #confirmation
        heading,    # param 1, yaw in degrees
        0,          # param 2, yaw speed deg/s
        1,          # param 3, direction -1 ccw, 1 cw
        is_relative, # param 4, relative offset 1, absolute angle 0
        0, 0, 0)    # param 5 ~ 7 not used
    # send command to vehicle
    vehicle.send_mavlink(msg)
    
def send_ned_velocity(velocity_x, velocity_y, velocity_z, duration):
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, # frame
        0b0000111111000111, # type_mask (only speeds enabled)
        0, 0, 0, # x, y, z positions (not used)
        velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
        0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)


        # send command to vehicle on 1 Hz cycle
    for x in range(0,duration):
        vehicle.send_mavlink(msg)
        time.sleep(1)

#Set up velocity vector to map to each direction.
# vx > 0 => fly North
# vx < 0 => fly South
FORWARD = 2
BACK = -2

# Note for vy:
# vy > 0 => fly East
# vy < 0 => fly West
RIGHT = 2
LEFT = -2

# Note for vz: 
# vz < 0 => ascend
# vz > 0 => descend
UP = -0.5
DOWN = 0.5

DURATION = 10
                    
@app.route("/api/left", methods=['POST', 'PUT'])
def left():
    if request.method == 'POST' or request.method == 'PUT':    
        try:
            print("Set groundspeed to 2m/s.")
            vehicle.groundspeed=2
            print("Moving left for 10 sec.")
            send_ned_velocity(0,LEFT,0,DURATION)
            vehicle.flush()
            return jsonify(ok=True)
        except Exception as e:
            print(e)
            return jsonify(ok=False)
@app.route("/api/right", methods=['POST', 'PUT'])
def right():
    if request.method == 'POST' or request.method == 'PUT':    
        try:
            print("Set groundspeed to 2m/s.")
            vehicle.groundspeed=2
            print("Moving right for 10 sec.")
            send_ned_velocity(0,RIGHT,0,DURATION)
            vehicle.flush()
            return jsonify(ok=True)
        except Exception as e:
            print(e)
            return jsonify(ok=False)
@app.route("/api/forward", methods=['POST', 'PUT'])
def forward():
    if request.method == 'POST' or request.method == 'PUT':    
        try:
            print("Set groundspeed to 2m/s.")
            vehicle.groundspeed=2
            print("Moving forward for 10 sec.")
            send_ned_velocity(FORWARD,0,0,DURATION)
            vehicle.flush()
            return jsonify(ok=True)
        except Exception as e:
            print(e)
            return jsonify(ok=False)
@app.route("/api/back", methods=['POST', 'PUT'])
def back():
    if request.method == 'POST' or request.method == 'PUT':    
        try:
            print("Set groundspeed to 2m/s.")
            vehicle.groundspeed=2
            print("Moving back for 10 sec.")
            send_ned_velocity(BACK,0,0,DURATION)
            vehicle.flush()
            return jsonify(ok=True)
        except Exception as e:
            print(e)
            return jsonify(ok=False)
@app.route("/api/up", methods=['POST', 'PUT'])
def up():
    if request.method == 'POST' or request.method == 'PUT':    
        try:
            print("Set groundspeed to 0.5m/s.")
            vehicle.groundspeed=0.5
            print("Moving up for 1 sec.")
            send_ned_velocity(0,0,UP,1)
            vehicle.flush()
            return jsonify(ok=True)
        except Exception as e:
            print(e)
            return jsonify(ok=False)
@app.route("/api/down", methods=['POST', 'PUT'])
def down():
    if request.method == 'POST' or request.method == 'PUT':    
        try:
            print("Set groundspeed to 0.5m/s.")
            vehicle.groundspeed=0.5
            print("Moving down for 1 sec.")
            send_ned_velocity(0,0,DOWN,1)
            vehicle.flush()
            return jsonify(ok=True)
        except Exception as e:
            print(e)
            return jsonify(ok=False)
@app.route("/api/yaw", methods=['POST', 'PUT'])
def yaw():
    if request.method == 'POST' or request.method == 'PUT':    
        try:
            print("Yaw 5 relative (to previous yaw heading)")
            condition_yaw(5,relative=True)
            vehicle.flush()
            return jsonify(ok=True)
        except Exception as e:
            print(e)
            return jsonify(ok=False)
        
        
# End add Hanno

# Never cache
@app.after_request
def never_cache(response):
    response.headers['Last-Modified'] = datetime.now()
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

t2 = Thread(target=connect_to_drone)
t2.daemon = True
t2.start()

def main():
    app.run(threaded=True, host='0.0.0.0', port=24403)

if __name__ == "__main__":
    main()
