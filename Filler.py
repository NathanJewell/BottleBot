from FillStatus import FillStatus as FS
from interact import Sensor, Trigger, jsonify, abort
import time

class Filler:

    def __init__(self, name, config, force_calibration=True):
        self.name = name
        self.config = config  
        self.calibrated = not force_calibration

    def configure_gpio(self, 
        proximity_GPIO, fill_GPIO,
        co2_GPIO, beer_GPIO):

        self.proximity_sensor = Sensor(proximity_GPIO)
        self.fill_sensor = Sensor(fill_GPIO)
        self.co2_selenoid = Trigger(co2_GPIO)
        self.beer_selenoid = Trigger(beer_GPIO)


        self.cans_filled = 0
        self.operating_start = time.time()
        self.operating_time = 0
        self.status = FS.OFFLINE

    def calibrate(self):
        self.status = FS.CALIBRATING
        self.config.nominal_proximity_cutoff = .1
        self.config.nominal_fill_resistivity = 600

    def start(self):
        if not self.calibrated:
            self.calibrate()
        
        while self.status != FS.OFFLINE:
            has_can = True if self.proximity_sensor.read() > self.config.nominal_proximity_cutoff else False
            if has_can and self.status==FS.READY:
                self.fill_once()
                self.cans_filled += 1
        
            operating_time = time.time() - self.operating_start
    
    def fill_once(self):
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
        return self.fill_sensor.read()

    def status_json(self):
        json = jsonify({
            "status" : self.status.__str__(),
            "cans_filled" : str(self.cans_filled),
            "operating_time" : str(self.operating_time),
            "name" : self.name
        })
        return json

    def set_status(self, status_str):
        try:
            self.status = FS['status']
        except Exception as e:
            return "Invalid Status String"
        return 1
