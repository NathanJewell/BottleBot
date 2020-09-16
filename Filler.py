from FillStatus import FillStatus as FS
from interact import Sensor, Trigger
import time
import threading

class Filler:

    def __init__(self, name, config, pins=[1,2,3,4], force_calibration=True):
        self.name = name
        self.config = config  
        self.calibrated = not force_calibration

        self.cans_filled = 0
        self.operating_start = time.time()
        self.operating_time = 0
        self.status = FS.OFFLINE

        self.proximity_sensor = None
        self.fill_sensor = None
        self.co2_selenoid = None
        self.beer_selenoid = None
        self.configure_gpio(*pins)

    def configure_gpio(self, 
        proximity_GPIO, fill_GPIO,
        co2_GPIO, beer_GPIO):

        self.proximity_sensor = Sensor(proximity_GPIO)
        self.fill_sensor = Sensor(fill_GPIO)
        self.co2_selenoid = Trigger(co2_GPIO)
        self.beer_selenoid = Trigger(beer_GPIO)

    def calibrate(self):
        print(self.config)
        self.config['nominal_proximity_cutoff'] = .1
        self.config['nominal_fill_resistivity'] = 600

    def start(self):
        if not self.calibrated:
            self.status = FS.CALIBRATING
            self.calibrate()
            self.status = FS.READY
        
        proximity_sensitivity = 10 #number of readings before we consider reading
        proximity_decision_ratio = .8 #x% of readings in timeframe must match
        proximity_pos_cnt = 0 #in proximity
        proximity_read_cnt = 0 #detections

        while self.status != FS.ERROR:
            if self.status == FS.OFFLINE: #force thread exit
                return
            proximity_reading = True if self.proximity_sensor.read() > self.config['nominal_proximity_cutoff'] else False
            if proximity_read_cnt < proximity_sensitivity:
                proximity_read_cnt += 1
                proximity_pos_cnt += proximity_reading
            else:
                ratio = (proximity_pos_cnt / proximity_read_cnt)
                has_can = None
                if ratio > proximity_decision_ratio:
                    has_can = True
                elif ratio < (1-proximity_decision_ratio):
                    has_can = False
                else:
                    break

                if has_can and self.status==FS.READY:
                    self.fill_once()
                    self.cans_filled += 1
                elif not has_can and self.status==FS.COMPLETE:
                    #can was removed and we can start to look for a new one
                    self.status == FS.READY

        
            operating_time = time.time() - self.operating_start
        
    def test(self):
        time.sleep(self.config['can_delay'])
        #purging o2
        self.co2_selenoid.open()
        self.status = FS.PURGING
        time.sleep(self.config['purge_time_seconds'])
        self.co2_selenoid.close()
        time.sleep(self.config['post_purge_delay'])
        #filling beer
        self.beer_selenoid.open()
        self.status = FS.FILLING
        time.sleep(self.config['overfill_delay'] + 8)
        self.beer_selenoid.close()
        #fill is complete
        self.status = FS.COMPLETE
        return

    
    def fill_once(self):
        time.sleep(self.config['can_delay'])
        #purging o2
        self.co2_selenoid.open()
        self.status = FS.PURGING
        time.sleep(self.config['purge_time_seconds'])
        self.co2_selenoid.close()
        time.sleep(self.config['post_purge_delay'])
        #filling beer
        self.beer_selenoid.open()
        self.status = FS.FILLING
        while self.fill_sensor.read() < self.config['nominal_fill_resistivity']:
            pass
        time.sleep(self.config['overfill_delay'])
        self.beer_selenoid.close()
        #fill is complete
        self.status = FS.COMPLETE
        return self.fill_sensor.read()

    def status_json(self):
        json = {
            "status" : self.status.name,
            "cans_filled" : str(self.cans_filled),
            "operating_time" : str(self.operating_time),
            "name" : self.name
        }
        return json

    def set_status(self, status_str):
        try:
            new_status = FS[status_str.upper()]
            
            print("HERE BRO {}".format(new_status))
            #starting canning process for this filler
            if self.status == FS.OFFLINE and new_status == FS.READY:
                self.status = FS.READY
                self.run_thread = threading.Thread(target=self.start)
                self.run_thread.start()
            elif new_status == FS.TESTING:
                self.status = FS.TESTING
                self.run_thread = threading.Thread(target=self.test)
                self.run_thread.start()
            elif new_status == FS.OFFLINE:
                self.status = FS.OFFLINE
                self.run_thread.join(1000)
                if self.run_thread.is_alive():
                    self.status = FS.ERROR
                    return "Could not kill filler thread."
        except Exception as e:
            return "Invalid Status String"
        return 1
