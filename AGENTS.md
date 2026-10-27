# AGENTS.md

## Project overview

This repository contains a MicroPython weather station for a Raspberry Pi Pico W. It reads temperature, humidity, and pressure, exposes the readings over HTTP, and drives a relay-based watering function.

## Design constraints

- Preserve the existing HTTP request and response format used by the collector program.
- Do not modify the vendor BME280 driver in `bme280_float.py` unless explicitly requested.
- Keep changes small and focused; prefer surgical fixes over broad rewrites.
- The DHT22 remains part of the active sensor path and should not be removed without a clear requirement change.

## Validation

Before finalizing a change, validate the project as far as the environment allows, with a focus on syntax and basic runtime consistency.

```bash
python3 -m compileall .
```

## Practical guidance

- Prefer minimal edits when debugging the Wi‑Fi reconnect path.
- Keep the project compatible with low-power MicroPython constraints.
- Maintain compatibility with the existing HTTP polling behavior and RTC timestamp format.
