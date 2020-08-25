
from interact import Trigger, Sensor
from flask import Flask, request, jsonify, abort
import threading
import time

#TODO load gpio + params config from yaml

#circuit configurations
proximity_GPIO = 1
co2_GPIO = 2
beer_GPIO = 3
fill_GPIO = 4

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
    "offline" : 2
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
    print("Flushing O2")
    co2_selenoid.open()
    co2_selenoid.close()
    print("Now filling...")
    beer_selenoid.open()
    while fill.read() < nominal_fill_pressure:
        pass
    beer_selenoid.close()
    print("Fill complete")

    return fill.read()

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

threading.Thread(target=app.run).start()