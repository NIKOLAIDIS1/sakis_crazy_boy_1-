import random
import time
import serial
#  sudo socat PTY,link=/dev/ttyV0,mode=777 PTY,link=/dev/ttyV1,mode=777
# Ρύθμιση της σειριακής θύρας (αντικαταστήστε με τη σωστή θύρα, π.χ. /dev/ttyS3)
try:
    ser = serial.Serial('/dev/ttyV0', 9600)  # Αντικαταστήστε με τη σωστή θύρα
    print("Σύνδεση με σειριακή θύρα επιτυχής.")
except Exception as e:
    print(f"Σφάλμα κατά τη σύνδεση στη σειριακή θύρα: {e}")
    exit()

# Συνάρτηση για τη δημιουργία τυχαίων τιμών αισθητήρων
def generate_sensor_data():
    humidity = random.uniform(5, 10)  # Τιμές υγρασίας μεταξύ 5 και 10
    temperature = random.uniform(5, 10)  # Τιμές θερμοκρασίας μεταξύ 5 και 10
    pressure = random.uniform(5, 10)  # Τιμές πίεσης μεταξύ 5 και 10
    return humidity, temperature, pressure

try:
    while True:
        # Δημιουργία δεδομένων
        humidity, temperature, pressure = generate_sensor_data()

        # Διαμόρφωση των δεδομένων σε string για αποστολή
        data = f"Humidity: {humidity:.2f}, Temperature: {temperature:.2f}, Pressure: {pressure:.2f}\n"

        # Αποστολή των δεδομένων στη σειριακή θύρα
        ser.write(data.encode())

        # Εμφάνιση των δεδομένων στο τερματικό
        print(f"Αποστολή δεδομένων: {data.strip()}")

        # Καθυστέρηση για 1 δευτερόλεπτο (προσομοίωση ροής δεδομένων)
        time.sleep(1)

except KeyboardInterrupt:
    print("\nΔιακοπή από τον χρήστη.")

finally:
    ser.close()  # Κλείσιμο της σειριακής θύρας
    print("Σειριακή θύρα έκλεισε.")
