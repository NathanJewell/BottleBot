import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
#from gpio_placeholder import read_gpio
#from gpio_placeholder import set_gpio

class Trigger:
    def __init__(self, gpio_num, open_=GPIO.high, close_=GPIO.low):
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

    def read(self):
        return GPIO.input(self.gpio)