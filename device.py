from config import *
from machine import Pin, I2C
import bme280_float as bme280

pump = Pin(PUMP_PIN, Pin.OUT)
pump.on() # pump is after an inverter
led = Pin(LED_PIN, Pin.OUT)

# Initialize I2C (use correct pins if not using defaults)
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
bme = bme280.BME280(i2c=i2c)

# Initialize the DHT22 sensor (temperature + humidity)
from PicoDHT22 import PicoDHT22
dht22 = PicoDHT22(
    Pin(
        DHTI2C2C_PIN,
        Pin.IN,
        Pin.PULL_UP
    ),
    powerPin=None,
    dht11=False,
    smID=7
)