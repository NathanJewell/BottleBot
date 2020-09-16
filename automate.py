
from interact import Trigger, Sensor
from flask import Flask, request, jsonify, abort
import threading
import time
import logging
logging.basicConfig(
    format='%(asctime)s || %(message)s',
    filename='machine.log', level=logging.INFO)

#TODO load gpio + params config from yaml

#circuit configurations
proximity_GPIO = 14
co2_GPIO = 8
beer_GPIO = 17
fill_GPIO = 24

#loop parameters
tick_time_ms = 100 #ms
nominal_fill_pressure = 130 #ohm
end_can = 0

#interface definitions
proximity = Sensor(proximity_GPIO)
co2_selenoid = Trigger(co2_GPIO)
beer_selenoid = Trigger(beer_GPIO)
fill = Sensor(fill_GPIO)

#statistics
cans_filled = 0
operating_start = time.time()
operating_time = 0
machine_status = 1

status_map = {
    "canning" : 0,
    "ready" : 1,
    "offline" : 2,
    "cleaning" : 3
}

inv_status_map = {v: k for k, v in status_map.items()}

def start():
    global cans_filled
    global operating_time
    global machine_status
    machine_status = status_map['ready']
    ticks_no_can = 0
    while machine_status != status_map['offline']:
        has_can = proximity.read()
        if has_can and machine_status == status_map['canning']:
            print("Can detected, fill triggered.")
            ticks_no_can = 0
            fill_level = can_once()
            cans_filled += 1

        operating_time = time.time() - operating_start

def can_once():
    logging.info("Flushing O2")
    co2_selenoid.open()
    co2_selenoid.close()
    logging.info("Now filling...")
    beer_selenoid.open()
    while fill.read() < nominal_fill_pressure:
        pass
    beer_selenoid.close()
    logging.info("Fill complete")

    return fill.read()

def clean_cycle():
    logging.info("Starting clean cycle.")
    beer_selenoid.open()
    time.sleep(clean_time)
    beer_selenoid.close()
    logging.info("Clean Cycle Completed.")

def status_json():
    json = jsonify({
        "status" : inv_status_map[machine_status],
        "cans_filled" : str(cans_filled),
        "operating_time" : str(operating_time)
    })
    return json

app = Flask(__name__, static_url_path='', static_folder='site/static')
@app.route('/stats')
def stats():
    return status_json()

@app.route('/status', methods=['POST'])
def onoff():
    global machine_status
    if not request.json or not 'status' in request.json:
        abort(400, "No request data.")
    try:
        canner_status = status_map[request.json['status']]
        machine_status = canner_status
    except Exception as e:
        abort(400, "Desired status not recognized")

    return status_json()

@app.route('/logs', methods=['POST'])
def getlogs():
    maxlines = 10
    timestamp = False
    if request.json:
        if 'maxlines' in request.json:
            try:
                maxlines = int(request.json['lines'])
                if maxlines <= 0:
                    raise Exception("Cannot have negative number of lines.")
            except Exception as e:
                abort(400, "Could not interpret requested number of log lines.")
        if 'timestamp' in request.json:
            try:
                timestamp = bool(request.json['timestamp'])
            except Exception as e:
                abort(400, "Could not interpret log timestamp requirement as bool.")


    with open("machine.log", "r") as logfile:
        lines = logfile.readlines()
        lines = lines[:min(maxlines, len(lines))]
        if timestamp:
            lines = [l.split('||')[1] for l in lines]
        lines = jsonify({
            'logs' : lines
        })
        return lines

threading.Thread(target=app.run).start()