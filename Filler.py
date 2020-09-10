from FillStatus import FillStatus as FS

app = Flask(__name__, static_url_path='', static_folder='site/static')
class Filler:

    def __init__(self, name, api, force_calibration=True):
        self.name = name
        self.calibrated = not force_calibration
        self.api = api

    def configure_gpio(self, 
        proximity_GPIO, fill_GPIO
        co2_GPIO, beer_GPIO):

        self.proximity_sensor = Sensor(proximity_GPIO)
        self.fill_sensor = Sensor(fill_GPIO)
        self.co2_selenoid = Trigger(co2_GPIO)
        self.beer_selenoid = Trigger(beer_GPIO)


        self.cans_filled = 0
        self.operating_start = time.time()
        self.operating_time = 0
        self.status = FS.OFFLINE

    def calibrate():
        self.status = FS.CALIBRATING
        self.config.nominal_proximity_cutoff = .1
        self.config.nominal_fill_resistivity = 600

    def start():
        if not self.calibrated:
            self.calibrate()
        
        while self.status != FS.OFFLINE:
            has_can = True if self.proximity_sensor.read() > self.config.nominal_proximity_cutoff else False
            if has_can and self.status=FS.READY:
                self.fill_once()
                self.cans_filled += 1
        
            operating_time = time.time() - operating_start
    
    def fill_once():
        time.sleep(self.config.can_delay)
        #purging o2
        self.co2_selenoid.open()
        self.status = FS.PURGING
        time.sleep(self.config.purge_time_seconds)
        self.co2_selenoid.close()
        time.sleep(self.config.post_purge_delay)
        #filling beer
        self.beer_selenoid.open()
        self.status = FS.FILLING
        while self.fill_sensor.read() < self.config.nominal_fill_resistivity:
            pass
        time.sleep(self.config.overfill_delay)
        self.beer_selenoid.close()
        #fill is complete
        self.status = FS.COMPLETE
        return fill.read()

    def status_json(self):
        json = jsonify({
            "status" : inv_status_map[machine_status],
            "cans_filled" : str(cans_filled),
            "operating_time" : str(operating_time)
        })
        return json

    def set_status(self, status_str):
        try:
            self.status = FS['status']
        except Exception as e:
            return "Invalid Status String"
        return 1


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
