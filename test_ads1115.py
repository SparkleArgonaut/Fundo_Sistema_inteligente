import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import time

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)

# Canal 0
canal = AnalogIn(ads, 0)

print("Monitoreando canal 0...")
try:
    while True:
        v = canal.value
        volt = canal.voltage
        print(f"Raw: {v:6d} | Voltaje: {volt:.3f}V")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\nSaliendo")
