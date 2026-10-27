# Pico 2W Weather Station

A MicroPython weather station for Raspberry Pi Pico W with BME280 and DHT22 sensors. Reads temperature, humidity, and pressure, exposes data over HTTP, and includes relay-controlled watering logic. Compatible with existing collector programs.

## Features

- BME280 pressure sensor
- DHT22 temperature and humidity sensor
- Pico W Wi‑Fi connectivity
- HTTP polling for sensor values
- RTC date/time synchronization
- relay output for watering control
- local HTML dashboard for debugging and parameter tuning

## Hardware

- Raspberry Pi Pico W
- Bosch BME280 on I2C
- DHT22 on GPIO 28
- relay/pump output on GPIO 16
- status LED on GPIO 10

## Project structure

- `main.py` — asynchronous runtime and task scheduler
- `config.py` — pin map, timing, Wi‑Fi credentials, static IP settings
- `device.py` — hardware initialization for the BME280, DHT22, relay, and LED
- `wifi_link.py` — Wi‑Fi management and HTTP server logic
- `bme280_float.py` — third-party Bosch BME280 driver retained without modification
- `PicoDHT22.py` — DHT22 driver used by the active sensor path

## HTTP API

The existing collector protocol is intentionally preserved. Do not change the request/response format unless the upstream collector is updated at the same time.

### Read current sensor values

Request:

```text
http://<pico-ip>/return_sensors
```

Response body:

```text
temperature;humidity;pressure
```

Example:

```text
21.6;47.3;101380.0
```

### Set RTC time

The firmware accepts a timestamp in the existing format used by the data collection software.

```text
http://<pico-ip>/settime?timestamp=YYYY-MM-DD-HH-MM-SS
```

## Wi‑Fi behavior

The Pico W reconnect logic attempts to recover from temporary Wi‑Fi loss by resetting the network interface and re-establishing the connection automatically, without requiring a full device power cycle.

## Notes

- This is designed for a local network environment and not a cloud-connected deployment.
- The DHT22 is part of the active measurement path and remains in use.
- The BME280 driver is third-party code and should be treated as such.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
