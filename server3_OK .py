#The server reads sensor data from a serial port and updates a shared dictionary (sensor_data) in real-time.
#Each sensor (humidity, temperature, pressure) is exposed as a CoAP resource via the SensorResource class.
#Clients send GET requests to sensor endpoints, and the server responds with JSON data or an error if the resource is not found.
#The read_serial_data function parses and updates sensor values continuously in an asynchronous loop.
#The server operates a CoAP context to handle client requests while running non-blocking serial data reading.



import asyncio
import serial

#mports essential components 
#from the aiocoap library, which is a Python implementation
#of the Constrained Application Protocol (CoAP).
#
from aiocoap import resource, Context, Message
import json

# Serial port configuration
SERIAL_PORT = '/dev/ttyV0'
BAUD_RATE = 9600

# Dictionary to store sensor data
#The dictionary sensor_data serves as a centralized storage for 
#the latest values and units of different sensors

sensor_data = {
    "humidity": {"value": 0.0, "unit": "%"},
    "temperature": {"value": 0.0, "unit": "C"},
    "pressure": {"value": 0.0, "unit": "hPa"}
}
#------------------------------------------------------------------------
#Declares that SensorResource is a subclass of resource.
#Resource, making it a custom CoAP resource that inherits the functionality provided by aiocoap.
#
class SensorResource(resource.Resource):
    def __init__(self, sensor_name):
        super().__init__()
        self.sensor_name = sensor_name
# render_get, is part of the SensorResource class 
# and is responsible for handling incoming GET requests for a specific sensor resource. 
    async def render_get(self, request):
        data = sensor_data.get(self.sensor_name)
        if data:
            payload = json.dumps({self.sensor_name: data}).encode('utf-8')
            print(f"[INFO] Responding to GET on /{self.sensor_name}: {payload.decode('utf-8')}")
            return Message(payload=payload)
        else:
            print(f"[ERROR] Resource '{self.sensor_name}' not found.")
            return Message(payload=b"Resource not found", code=404)
#---------------------------------------------------------------------

#The function read_serial_data reads and parses data from a serial port asynchronously and updates a global dictionary sensor_data


async def read_serial_data():
    """Read data from the serial port and update sensor_data."""
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"[INFO] Connected to serial port {SERIAL_PORT} at {BAUD_RATE} baud.")

        while True:
            if ser.in_waiting > 0:
                raw_data = ser.readline().decode('utf-8').strip()
                print(f"[INFO] Received serial data: {raw_data}")

                # Parse the data
                try:
                    # Split the raw data into key-value pairs
                    for entry in raw_data.split(","):
                        key, value = entry.split(":")
                        key = key.strip().lower()
                        value = float(value.strip())
                        if key in sensor_data:
                            sensor_data[key]["value"] = value
                except Exception as e:
                    print(f"[ERROR] Failed to parse data: {e}")

            await asyncio.sleep(0.1)
    except serial.SerialException as e:
        print(f"[ERROR] Serial port error: {e}")
    finally:
        if ser.is_open:
            ser.close()

#-------------------------------------------------------------------------------------
# setting up a CoAP server and integrating sensor data handling.

async def main():
    root = resource.Site()    #  create the root for CoAP resources.

    # Register resources for individual sensors
    root.add_resource(("humidity",), SensorResource("humidity"))
    root.add_resource(("temperature",), SensorResource("temperature"))
    root.add_resource(("pressure",), SensorResource("pressure"))

    print("[DEBUG] Registered resources: /humidity, /temperature, /pressure")

    # Start reading from the serial port
    asyncio.create_task(read_serial_data())

    # Start the CoAP server
    await Context.create_server_context(root)
    print("[INFO] CoAP server is running...")

    # Keep the server running
    await asyncio.get_running_loop().create_future()
#----------------------------------------------------------------------------------------------

# This construct serves as the entry point for the script and ensures the main() 
# function is executed only when the script is run directly, 
# not when it is imported as a module into another script.
if __name__ == "__main__":
    asyncio.run(main())
