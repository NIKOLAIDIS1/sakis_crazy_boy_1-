#  The server reads sensor data (humidity, temperature, and pressure) from a serial port,
# updates a shared dictionary, and serves this data via CoAP endpoints (/humidity, /temperature, /pressure).

# The client interacts with the user, allowing them to select a sensor using numeric options (1, 2, or 3) 
# mapped in a dictionary, and fetches the corresponding data by making GET requests to the server.

# The server responds with JSON data, and the client parses and displays the sensor's value and unit to the user.



# SERVER CODE
#Dependencies:

#    asyncio: For asynchronous programming.
 #   serial: For serial port communication.
  #  aiocoap: For building and handling CoAP resources and messages.
  #  json: For parsing and generating JSON data.'

import asyncio
import serial
from aiocoap import resource, Context, Message
import json
#-------------------------------------------------------------------------------------------
# Serial port configuration
#These constants configure the serial port where the server reads sensor data.
SERIAL_PORT = '/dev/ttyV0'
BAUD_RATE = 9600
#-----------------------------------------------------------------------------------------------
# Dictionary to store sensor data
sensor_data = {
    "humidity": {"value": 0.0, "unit": "%"},
    "temperature": {"value": 0.0, "unit": "C"},
    "pressure": {"value": 0.0, "unit": "hPa"}
}

#--------------------------------------------------------------------------

# SensorResource Class:
#Each instance of the class represents a single sensor, such as "humidity," "temperature," or "pressure."
class SensorResource(resource.Resource):
    """Resource to serve individual sensor data."""
    def __init__(self, sensor_name):
        super().__init__()
        self.sensor_name = sensor_name

 
# handle incoming GET requests to retrieve sensor data via a
# CoAP (Constrained Application Protocol) server.
    async def render_get(self, request):
        data = sensor_data.get(self.sensor_name)
        if data:
            payload = json.dumps({self.sensor_name: data}).encode('utf-8')
            print(f"[INFO] Responding to GET on /{self.sensor_name}: {payload.decode('utf-8')}")
            return Message(payload=payload)
        else:
            print(f"[ERROR] Resource '{self.sensor_name}' not found.")
            return Message(payload=b"Resource not found", code=404)

async def read_serial_data():
    """Read data from the serial port and update sensor_data."""
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"[INFO] Connected to serial port {SERIAL_PORT} at {BAUD_RATE} baud.")

        while True:
            if ser.in_waiting > 0:
                # Read and decode data from the serial port
                raw_data = ser.readline().decode('utf-8').strip()
                print(f"[INFO] Received serial data: {raw_data}")

                # Parse the data
                try:
                    for sensor_name in sensor_data:
                        if sensor_name in raw_data.lower():
                            value = float(raw_data.split(":")[1].strip().split(",")[0])
                            sensor_data[sensor_name]["value"] = value
                except Exception as e:
                    print(f"[ERROR] Failed to parse data: {e}")

            await asyncio.sleep(0.1)
    except serial.SerialException as e:
        print(f"[ERROR] Serial port error: {e}")
    finally:
        if ser.is_open:
            ser.close()

async def main():
    """Setup and run the CoAP server."""
    root = resource.Site()

    # Add resources for individual sensors
    root.add_resource(("humidity",), SensorResource("humidity"))
    root.add_resource(("temperature",), SensorResource("temperature"))
    root.add_resource(("pressure",), SensorResource("pressure"))

    # Start reading from the serial port
    asyncio.create_task(read_serial_data())

    # Start the CoAP server
    await Context.create_server_context(root)
    print("[INFO] CoAP server is running. Waiting for incoming requests...")

    # Keep the server running
    await asyncio.get_running_loop().create_future()

import asyncio
from aiocoap import Context, Message, GET
import json

# Define the server address and available sensors
SERVER_URL = "coap://localhost"    #SERVER_URL = "coap://localhost" specifies the server location.
SENSORS = {
    "1": "humidity",
    "2": "temperature",
    "3": "pressure"
}

async def fetch_sensor_data(sensor_key):
    """Fetch the data of the selected sensor from the server."""
    if sensor_key not in SENSORS:
        print("Invalid selection. Please try again.")
        return

    sensor_endpoint = SENSORS[sensor_key]
    uri = f"{SERVER_URL}/{sensor_endpoint}"
    context = await Context.create_client_context()

    try:
        # Send a GET request to the server
        request = Message(code=GET, uri=uri)
        response = await context.request(request).response

        # Parse the JSON response
        payload = response.payload.decode('utf-8')
        if not payload.strip():
            print(f"[ERROR] Empty response from server for {sensor_endpoint}.")
            return

        try:
            data = json.loads(payload)
            sensor_info = data.get(sensor_endpoint, {})
            value = sensor_info.get("value", "N/A")
            unit = sensor_info.get("unit", "unknown")
            print(f"Sensor: {sensor_endpoint.upper()} - Value: {value} {unit}")
        except json.JSONDecodeError:
            print(f"[ERROR] Invalid JSON received: {payload}")
    except Exception as e:
        print(f"Failed to fetch data from {sensor_endpoint}: {e}")
#-------------------------------------------------------------------------------------------
async def main():
    """Main function to interact with the user."""
    print("Available sensors:")
    for key, sensor in SENSORS.items():
        print(f"{key}. {sensor.capitalize()}")

    while True:
        choice = input("Select a sensor by number (or type 'exit' to quit): ").strip()
        if choice.lower() == "exit":
            print("Exiting client...")
            break

        await fetch_sensor_data(choice)

if __name__ == "__main__":
    asyncio.run(main())

