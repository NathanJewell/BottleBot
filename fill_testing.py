from interact import Sensor

# 23      16    FS1
# 24      18    FS2
# 25      22    FS3
# 8       24    FS4

fill_a = Sensor(23)
fill_b = Sensor(24)
fill_c = Sensor(25)
fill_d = Sensor(8)

sensors_ordered = [fill_a, fill_b, fill_c, fill_d]



while True:
    output_str = ""
    for idx, sensor in enumerate(sensors_ordered):
        output_str += f"IDX: {sensor.Read()} \t"


         