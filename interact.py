#import RPi.GPIO as GPIO
#GPIO.setmode(GPIO.BCM)

#offboard testing placeholder gpio class
class GPIO:
    OUT = 0
    IN = 1
    LOW = 0
    HIGH = 1
    @staticmethod
    def setup(pin, mode, initial=None):
        pass
    @staticmethod
    def output(pin, state):
        pass
    @staticmethod
    def input(pin):
        return 0

class Trigger:
    def __init__(self, gpio_num, open_=GPIO.LOW, close_=GPIO.HIGH):
        self.gpio = gpio_num
        self.open_=open_
        self.close_=close_

        GPIO.setup(self.gpio, GPIO.OUT, initial=self.close_)

    def open(self):
        GPIO.output(self.gpio, self.open_)
    
    def close(self):
        GPIO.output(self.gpio, self.close_)


class Sensor:
    def __init__(self, gpio_num):
        self.gpio = gpio_num
        GPIO.setup(self.gpio, GPIO.IN)

        GPIO.setup(self.gpio, GPIO.IN)

    def read(self):
        return GPIO.input(self.gpio)