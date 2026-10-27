"""
Constants and Pin definitions
"""

DELAY=30 # cycle time in seconds
BLINK=1 # connected blink time in seconds
SAMPLES=100 # number of samples to average for one reading

LED_PIN = 10  # GPIO pin for the LED
PUMP_PIN = 16  # GPIO pin for the pump

# Pin definitions for the DHT22 sensor
DHTI2C2C_PIN = 28

# Wifi credentials
ssid = 'ssid'
password = 'pass'

# Static IP configuration
ip='192.168.1.100'
mask='255.255.255.0'
gateway='192.168.1.1'
dns='8.8.8.8'