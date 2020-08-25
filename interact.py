#from gpio_placeholder import read_gpio
#from gpio_placeholder import set_gpio

def read_gpio(which):
    return 1

def set_gpio(which, what):
    return None

class Trigger:
    def __init__(self, gpio_num, open=1, close=0):
        self.gpio = gpio_num
        self.open=open

    def open(self):
        set_gpio(self.gpio, self.open)
    
    def close(self):
        set_gpio(self.gpio, self.close)


class Sensor:
    def __init__(self, gpio_num):
        self.gpio = gpio_num

    def read(self):
        return read_gpio(self.gpio)