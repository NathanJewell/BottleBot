#import RPi.GPIO as GPIO
#GPIO.setmode(GPIO.BOARD)

class GPIO:
    OUT = 1
    IN = 0
    low = 0
    high = 1
    def setup(gpio, status, initial=0):
        pass

    def output(gpio, signal):
        pass

    def input(gpio):
        return 1

class Trigger:
    def __init__(self, gpio_num, open=GPIO.high, close=GPIO.low):
        self.gpio = gpio_num
        self.open=open
        self.close=close

        self.status = 0
        GPIO.setup(self.gpio, GPIO.OUT, initial=self.close)

    def open(self):
        GPIO.output(self.gpio, self.open)
        self.status = 1
    
    def close(self):
        GPIO.output(self.gpio, self.close)
        self.status = 0
    
    def status(self):
        return self.status


class Sensor:
    def __init__(self, gpio_num):
        self.gpio = gpio_num

        GPIO.setup(self.gpio, GPIO.IN)

    def read(self):
        return GPIO.input(self.gpio)