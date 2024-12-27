Description of the CoAP System with Arduino Sensor Simulation

    Arduino Sensor Simulation:
        The simulation arduino.py script simulates an Arduino device by generating random values for humidity, temperature, and pressure.
        These values are formatted into a string and sent over a simulated serial port (/dev/ttyV0) to mimic real sensor data output.

    CoAP Server:
        The coap server .py script listens to the simulated serial port for incoming data from the Arduino simulation.
        It reads and decodes the sensor data and sends it asynchronously to a CoAP endpoint (/sensor_data) on the local server using the POST method.

    CoAP Client:
        The client coap .py script acts as a client that interacts with the CoAP server.
        The client allows a user to select a specific sensor (e.g., sensora, sensorb, sensorc) and sends a GET request to fetch the corresponding data from the server.
        The response is parsed and displayed, showing the sensor name and its latest value.

Workflow:

    The Arduino simulation continuously generates and sends sensor data over a serial port.
    The CoAP server reads this data, processes it, and makes it available via CoAP resources.
    The client queries the server for specific sensor data, providing an interactive interface for users to monitor the sensors.

