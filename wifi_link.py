import network
import time

"""
Get the list of sensors values via HTTP request:
http://192.168.1.100/return_sensors

Set the datetime of the RTC via HTTP request:
http://192.168.1.100/settime=2025-12-09-02-15-40-00
curl "http://192.168.1.100:80/settime?timestamp=$(date +%Y-%m-%d-%w-%H-%M-%S)"
"""

def init_wifi():
    """
    Initialize the WiFi in station mode.
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # Remove previous connections for testing purposes
    wlan.disconnect()
    time.sleep(2)
    return wlan



def make_handler(state, params):
    async def handler(reader, writer):
        await handle_client(reader, writer, state, params)
    return handler



async def handle_client(reader, writer, state, params):
    request = await reader.readline()
    print('Request:', request)

    # Get the content length from request details
    content_length = 0
    while True:
        line = await reader.readline()
        if 'Content-Length:' in line:
            content_length = int(line.split(b':')[1].strip())
            print(f"Content length: {content_length}")
        if not line or line == b'\r\n':
            break

    # Get the content (key/value pair for params dictionnary)
    post_body = b''
    if content_length:
        post_body = await reader.read(content_length)
        # Now post_body contains the full form data, e.g., b'IdleLimit=600&param=IdleLimit'
        print("POST body:", post_body.decode())

    
    
    # Process the request and update stateiables
    if 'settime' in request:
        try:
            datestr= request.decode().split('=')[1]
            datestr= datestr.split(' ')[0]
            print(f"Setting time to: {datestr}")
            parts = [int(x) for x in datestr.split('-')]
            # rtc format: (year, month, day, weekday, hour, minute, second, subsecond)
            rtc_time = (parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6], 0)
            print(f"RTC time tuple: {rtc_time}")
            state['RTC'].datetime(rtc_time)
            print(f"RTC time set to: {rtc_time}") 
        except Exception as e:
            print(f"Couldn't parse datetime in request: {request} ({e})")
    if 'update' in request:
        try:
            param_name= post_body.decode().split('=')[2].strip()
            param_value= ( post_body.decode().split('&')[0] ).split('=')[1]
            print(f"Updating parameter: {param_name} to value: {param_value}")
            if param_name in params:
                # Attempt to convert to float or int if possible
                try:
                    if '.' in param_value:
                        params[param_name] = float(param_value)
                    else:
                        params[param_name] = int(param_value)
                    print(f"Parameter {param_name} updated to {params[param_name]}")
                except ValueError:
                    print(f"Cant convert {param_name} to number")
            else:
                print(f"Parameter {param_name} not found in params")
        except Exception as e:
            print(f"Error updating parameter from request: {request}, Error: {e}")
    
    if 'return_sensors' in request:
        try:
            print("Sensor read request received")
            values= f"{state['Temperature']};{state['Humidity']};{state['Pressure']}\n"
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n')
            writer.write(values)
        except Exception as e:
            print(f"Error returning sensor values: {e}")

    else:
        try:
            # Refresh the web page with current state and params
            page = generate_html_page("Station Météo Carrels", state, params)  

            # Send the HTTP response and close the connection
            writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            writer.write(page)
        except Exception as e:
            print(f"Error generating HTML page: {e}")
    
    await writer.drain()
    await writer.wait_closed()


def generate_html_page(title, data_dict, params):
    html = ['<!DOCTYPE html>', '<html>', '<head>']
    html.append('<meta charset="UTF-8">')
    html.append(f'<title>{title}</title>')

    html.append('''
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      :root {
        --bg: #f4f7fb;
        --panel: #ffffff;
        --panel-alt: #eef5ff;
        --primary: #1d4ed8;
        --primary-strong: #163ea8;
        --text: #1f2937;
        --muted: #6b7280;
        --border: #dfe7f5;
        --shadow: rgba(15, 23, 42, 0.08);
        --success-bg: #dcfce7;
        --success-text: #166534;
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        font-family: Arial, sans-serif;
        background: linear-gradient(180deg, #edf5ff 0%, var(--bg) 100%);
        color: var(--text);
      }
      .container {
        max-width: 980px;
        margin: 0 auto;
        padding: 24px 16px 40px;
      }
      .card {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 16px;
        box-shadow: 0 8px 24px var(--shadow);
        padding: 20px;
        margin-bottom: 18px;
      }
      h1 {
        margin: 0 0 8px;
        font-size: clamp(1.8rem, 3vw, 2.6rem);
        color: var(--primary-strong);
      }
      h2 {
        margin: 0 0 14px;
        font-size: 1.2rem;
        color: var(--text);
      }
      .subtitle {
        color: var(--muted);
        margin-bottom: 18px;
        font-size: 0.95rem;
      }
      .status {
        display: inline-block;
        border-radius: 999px;
        padding: 5px 10px;
        font-size: 0.82rem;
        background: var(--success-bg);
        color: var(--success-text);
        border: 1px solid #bbf7d0;
      }
      .table-wrapper {
        overflow-x: auto;
      }
      table {
        width: 100%;
        border-collapse: collapse;
        min-width: 320px;
      }
      th, td {
        text-align: left;
        padding: 12px 14px;
        border-bottom: 1px solid var(--border);
      }
      th {
        background: var(--panel-alt);
        color: var(--primary-strong);
        font-weight: bold;
      }
      tbody tr:nth-child(even) {
        background: #fafcff;
      }
      form {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 10px;
        margin: 12px 0;
        padding: 10px 12px;
        border: 1px solid var(--border);
        border-radius: 10px;
        background: #fbfdff;
      }
      label {
        min-width: 150px;
        font-weight: bold;
      }
      input[type=text] {
        flex: 1 1 180px;
        padding: 10px 12px;
        border: 1px solid var(--border);
        border-radius: 8px;
        font-size: 1rem;
        background: white;
        color: var(--text);
      }
      button {
        border: none;
        border-radius: 8px;
        background: linear-gradient(180deg, var(--primary) 0%, var(--primary-strong) 100%);
        color: white;
        padding: 10px 16px;
        font-weight: bold;
        cursor: pointer;
      }
      button:hover {
        filter: brightness(1.05);
      }
      @media (max-width: 640px) {
        .container { padding: 16px 12px 32px; }
        .card { padding: 16px; }
        form { display: block; }
        label { display: block; margin-bottom: 6px; }
        input[type=text], button { width: 100%; }
      }
    </style>
    ''')

    html.append('</head><body>')
    html.append('<div class="container">')
    html.append(f'<div class="card"><h1>{title}</h1><div class="subtitle">Station météo locale / telemetry</div><div class="status">System online</div></div>')
    html.append('<div class="card"><h2>Capteurs et variables</h2>')
    html.append('<div class="table-wrapper"><table><thead><tr><th>Parameter</th><th>Value</th></tr></thead><tbody>')
    for key, val in sorted(data_dict.items()):
        html.append(f'<tr><td>{key}</td><td>{val}</td></tr>')
    html.append('</tbody></table></div></div>')

    html.append('<div class="card"><h2>Constantes ajustables</h2>')
    for key, val in sorted(params.items()):
        html.append(f'''
        <form method="POST" action="/update">
        <label for="{key}">{key}:</label>
        <input type="text" id="{key}" name="{key}" value="{val}">
        <input type="hidden" name="param" value="{key}">
        <button type="submit">Update</button>
        </form>
        ''')
    html.append('</div></div></body></html>')

    return '\n'.join(html)

