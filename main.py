import sys
sys.path.append("")

from config import *
from device import *
from wifi_link import *
import asyncio
from machine import RTC

async def read_sensors(state):
    while True:
        try:
            t, h, p=[0,0,0]
            for _ in range(SAMPLES):
                await asyncio.sleep(int(DELAY/SAMPLES))
                
                # Read BME280 sensor for pressure
                try:
                    sample = bme.read_compensated_data()
                    if sample[1] is not None and p is not None:
                        p += sample[1]
                    else:
                        print("BME280 returned P = None")
                        p= None
                except Exception as e:
                    print("BME280 sensor read error:", e)

                # Read DHT22 sensor for humidity and pressure
                try:
                    sample= dht22.read()
                    if sample[0] is not None and t is not None:
                        t += sample[0]
                    else:
                        print("DHT22 returned T = None")
                        t= None
                    if sample[1] is not None and h is not None:
                        h += sample[1]
                    else :
                        print("DHT22 returned H = None")
                        h= None
                except Exception as e:
                    print("DHT22 sensor read error:", e)

            # Compute final values
            state['Temperature']= None
            state['Humidity']= None
            state['Pressure']= None
            if t is not None:
                t/= SAMPLES
                state['Temperature']= t
            if h is not None:
                h/= SAMPLES
                state['Humidity']= h
            if p is not None:
                p/= SAMPLES
                state['Pressure']= p           

            #get the time from the RTC
            dt_tuple = state['RTC'].datetime()
            dt = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                dt_tuple[0], dt_tuple[1], dt_tuple[2], dt_tuple[4], dt_tuple[5], dt_tuple[6]
            )

            state['Temperature']= t
            state['Humidity']= h
            state['Pressure']= p
            state['Time']= dt

            print(f"{dt}, T: {t}, H: {h}, P: {p}")
            await asyncio.sleep(DELAY)
        except KeyboardInterrupt:
            break


async def blink(state):
    print("LED starts flashing...")
    while True:
        try:
            led.toggle()
            if state['Connected']:
                await asyncio.sleep(BLINK)
            else:
                await asyncio.sleep(BLINK/8)
        except KeyboardInterrupt:
            break
    led.off()


async def wifi_manager(state):
    """
    Attempt to connect to wifi. If connection is lost, try to reconnect.
    """
    print("Starting WiFi manager...")
    wlan = init_wifi()
    reconnect_attempts = 0

    while True:
        try:
            if wlan.isconnected():
                if not state['Connected']:
                    print("Connected to WiFi !")
                    state['Connected'] = True
                reconnect_attempts = 0
                await asyncio.sleep(DELAY)
                continue

            state['Connected'] = False
            reconnect_attempts += 1
            print(f"WiFi not connected. Reconnect attempt #{reconnect_attempts}...")

            try:
                wlan.disconnect()
                await asyncio.sleep(1)
                wlan.active(False)
                await asyncio.sleep(1)
                wlan.active(True)
                await asyncio.sleep(1)
                print(f'Attempting to connect to {ssid}...')
                wlan.connect(ssid, password)
            except Exception as e:
                print("WiFi connection error:", e)

            timeout = 20
            while not wlan.isconnected() and timeout > 0:
                await asyncio.sleep(1)
                timeout -= 1
                print('Waiting for connection...')

            if wlan.isconnected():
                wlan.ifconfig((ip, mask, gateway, dns))
                print('Network config:', wlan.ifconfig())
                state['Connected'] = True
                reconnect_attempts = 0
            else:
                print('Failed to connect to WiFi; retrying next cycle.')

            await asyncio.sleep(DELAY)
        except KeyboardInterrupt:
            break
    wlan.disconnect()
        

async def update_counter(state, params):
    """
    This function manage the counter that triggers the watering.
    The increment speed depends on temperature and humidity. (T*T/H)
    """

    print("Starting counter update task")
    while True:
        await asyncio.sleep(DELAY)
        try:
            print("Counter value:", params['WateringCounter'])
            T= state['Temperature']
            H= state['Humidity']
            
            if T is None or H is None or H==0:
                print("Invalid sensor values for counter update. Skipping...")
                continue
            
            increment= DELAY*T*T/H
            params['WateringCounter'] += increment
            state['NextWateringMinutes']= (params['WateringTrigger'] - params['WateringCounter'])/increment*DELAY/60  # in minutes
            if params['WateringCounter'] > params['WateringTrigger']:
                print("Watering plants!")
                # Activate the pump
                pump.off()
                await asyncio.sleep(params['WateringDuration'])  # Pump for 5 seconds
                pump.on()
                print("Pump turned off")
                params['WateringCounter'] = 0
                write_backup(params)
        except KeyboardInterrupt:
            write_backup(params)
            break
        except Exception as e:
            print("Error updating counter:", e)


def write_backup(params):
    try:
        with open("backup.txt", "w") as f:
            # Save the params dictionary as key-value pairs
            for key in params:
                f.write(f"{key} : {params[key]}\n")
                print(f"Saved {key} : {params[key]}")
        print("Backup saved successfully.")
    except Exception as e:
        print("Error saving backup:", e)


def read_backup(params):
    try:
        with open("backup.txt", "r") as f:
            print("Reading backup.txt")
            for line in f:
                key, value = line.strip().split(" : ")
                if key in params:
                    params[key] = float(value)
                    print(f"Loaded {key} : {params[key]}")
        print("Backup loaded successfully.")
    except Exception as e:
        print("Error loading backup:", e)



async def main():
    print("Starting the main loop...")

    state={
        'Temperature': None,
        'Humidity': None,
        'Pressure': None,
        'Time': None,
        'RTC': RTC(),
        'Connected': False,
        'NextWateringMinutes': None
    }
    params={
        'WateringTrigger': 3000,
        'WateringCounter': 0,
        'WateringDuration': 5
    }

    read_backup(params)

    asyncio.create_task(read_sensors(state))
    asyncio.create_task(wifi_manager(state))
    asyncio.create_task(blink(state))
    asyncio.create_task(update_counter(state, params))
    asyncio.create_task(asyncio.start_server(make_handler(state, params), "0.0.0.0", 80))


# Create an Event Loop
loop = asyncio.get_event_loop()
# Create a task to run the main function
loop.create_task(main())

try:
    # Run the event loop indefinitely
    loop.run_forever()
except Exception as e:
    print('Error occurred: ', e)
except KeyboardInterrupt:
    print('Program Interrupted by the user')