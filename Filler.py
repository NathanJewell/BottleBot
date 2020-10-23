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
        self.message_content = ""

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

    def countdown_message(self, text, seconds):
        for x in range(seconds):
            self.message_content = text.format(seconds-x)
            time.sleep(1)

    def calibrate(self):
        #start calibration
        calibration_stage_delay_seconds = 10 #how long for human to check machine state
        calibration_stage_time = 1 #how long to average input over

        self.message_content = "Prepare to begin calibration"
        time.sleep(calibration_stage_delay_seconds)
        self.message_content = "Prepare to yeet calibration"

        #LOW PROXIMITY 
        self.countdown_message(
            "Remove all obstructions from proximity sensor: {}", 
            calibration_stage_delay_seconds)
        self.message_content = "Calibrating..."
        start = time.time()
        detect_max = 0
        while (time.time() - start) < calibration_stage_time:
            read = self.proximity_sensor.read()
            if read > detect_max:
                detect_max = read
        proximity_detect_low_max = input_sum / detect_count

        #HIGH PROXIMITY
        self.countdown_message(
            "Place can in proximity sensor: {}",
            calibration_stage_delay_seconds)
        self.message_content = "Calibrating..."
        start = time.time()
        detect_min = 0
        while (time.time() - start) < calibration_stage_time:
            read = self.proximity_sensor.read()
            if read < detect_min:
                detect_min = read
        proximity_detect_high_min = input_sum / detect_count

        self.config['nominal_proximity_cutoff'] = proximity_detect_low_max + (proximity_detect_high_min - proximity_detect_low_max) * .2


        start = time.time()
        detect_max = 0
        while (time.time() - start) < calibration_stage_time:
            read = self.fill_sensor.read()
            if read > detect_max:
                detect_max = read
        fill_detect_low_max = input_sum / detect_count

        self.message_content = "Filling to default detection level."
        #trigger beer fill
        self.beer_selenoid.open()
        while self.fill_sensor.read() < self.config['nominal_fill_resistivity']:
            pass
        self.beer_selenoid.close()
        self.countdown_message(
            "Validate that the can is full to fill sensor: {}",
            calibration_stage_delay_seconds)
        #wait for fill sensor
        start = time.time()
        detect_min = 0
        while (time.time() - start) < calibration_stage_time:
            read = self.fill_sensor.read()
            if read < detect_min:
                detect_min = read
        fill_detect_high_min = input_sum / detect_count
        #validate that the can is full to sensor
        self.config['nominal_fill_resistivity'] = 600
        #adjust timings as necessary
        self.message_content = "Calibration Complete. Adjust delay timings as necessary."

    def start(self):
        #if not self.calibrated:
            #self.status = FS.CALIBRATING
            #self.calibrate()
            #self.status = FS.READY
        
        proximity_sensitivity = 10 #number of readings before we consider reading
        proximity_decision_count = 10
        proximity_last_read = None
        proximity_decision_ratio = .8 #x% of readings in timeframe must match
        proximity_pos_cnt = 0 #in proximity
        proximity_read_cnt = 0 #detections

        while self.status != FS.ERROR:
            if self.status == FS.OFFLINE: #force thread exit
                return
            proximity_reading = True if self.proximity_sensor.read() < self.config['nominal_proximity_cutoff'] else False
            if proximity_reading == proximity_last_read:
                proximity_decision_count += 1
            else:
                proximity_decision_count = 1
                proximity_last_read = proximity_reading

            if proximity_decision_count >= proximity_sensitivity:
                has_can = proximity_last_read
                proximity_decision_count = 0
                proximity_last_read = None

                if has_can and self.status==FS.READY:
                    self.fill_once()
                    self.cans_filled += 1
                elif not has_can and self.status==FS.COMPLETE:
                    #can was removed and we can start to look for a new one
                    self.status = FS.READY

        
            operating_time = time.time() - self.operating_start
        
    def clean(self):
        self.message_content = "Starting Cleaning Cycle"
        time.sleep(1)
        message = "Cleaning time remaining: {}"
        #self.co2_selenoid.open()
        self.beer_selenoid.open()
        time.sleep(self.config['clean_time_seconds'])
        self.countdown_message(message, self.config['clean_time_seconds'])
        #self.co2_selenoid.close()
        self.beer_selenoid.close()
        self.message_content = "Cleaning Complete"
        self.status = FS.COMPLETE
        return

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
        self.topoff_time = self.config['topoff_time']
        topping_off = False
        start_topoff = 0
        fillcycle = True
        while fillcycle: 
            if (self.fill_sensor.read() < self.config['nominal_fill_resistivity']):
                self.beer_selenoid.close()
            else:
                self.beer_selenoid.open()
                if not topping_off:
                    start_topoff = time.time()
                elif time.time() - start_topoff > self.topoff_time:
                    fillcycle = False
        time.sleep(self.config['overfill_delay'])
        self.beer_selenoid.close()
        #fill is complete
        self.status = FS.COMPLETE
        return self.fill_sensor.read()

    def status_json(self):
        print(self.message_content)
        json = {
            "status" : self.status.name,
            "cans_filled" : str(self.cans_filled),
            "operating_time" : str(self.operating_time),
            "name" : self.name,
            "message_content" : self.message_content
        }
        return json

    def set_status(self, status_str):
        try:
            new_status = FS[status_str.upper()]
            
            #starting canning process for this filler
            if self.status == FS.OFFLINE and new_status == FS.READY:
                self.status = FS.READY
                self.run_thread = threading.Thread(target=self.start)
                self.run_thread.start()
            elif new_status == FS.TESTING and self.status == FS.OFFLINE:
                self.status = FS.TESTING
                self.run_thread = threading.Thread(target=self.test)
                self.run_thread.start()
            elif new_status == FS.CLEANING and self.status == FS.OFFLINE:
                self.status = FS.CLEANING
                self.run_thread = threading.Thread(target=self.clean)
                self.run_thread.start()
            elif new_status == FS.CALIBRATING and self.status == FS.OFFLINE:
                self.status = FS.CALIBRATING
                self.run_thread = threading.Thread(target=self.calibrate)
                self.run_thread.start()
            elif new_status == FS.OFFLINE:
                self.beer_selenoid.close()
                self.co2_selenoid.close()
                self.status = FS.OFFLINE
                self.run_thread.join(1000)
                if self.run_thread.is_alive():
                    self.status = FS.ERROR
                    return "Could not kill filler thread."
        except Exception as e:
            return "Invalid Status String"
        return 1
