
import serial
import time

# Update this with the Arduino's COM port.
ARDUINO_PORT = "COM5"
BAUD_RATE = 9600

arduino = None


def send_command(command):
    """Send a command to the Arduino Uno."""
    if arduino and arduino.is_open:
        arduino.write(f"{command}\n".encode("ascii"))
        arduino.flush()
        print(f"Sent command: {command}")


try:
    print(f"Connecting to Arduino on {ARDUINO_PORT}...")

    arduino = serial.Serial(
        port=ARDUINO_PORT,
        baudrate=BAUD_RATE,
        timeout=1,
        write_timeout=2
    )

    # Arduino Uno resets when serial is opened.
    time.sleep(4)
    arduino.reset_input_buffer()

    print("Connected successfully.")

    # Set motor speed to 160.
    send_command("V160")
    time.sleep(0.5)

    # Demonstrate left motor actuation.
    send_command("L")
    time.sleep(1)

    send_command("S")
    time.sleep(1)

    # Demonstrate right motor actuation.
    send_command("R")
    time.sleep(1)

    send_command("S")
    print("Actuation test completed.")

except serial.SerialException as error:
    print(f"Serial connection error: {error}")
    print("Check the COM port, USB cable, and Arduino connection.")

except KeyboardInterrupt:
    print("\nTest interrupted by user.")

finally:
    if arduino and arduino.is_open:
        # Always attempt to stop the motors before disconnecting.
        try:
            arduino.write(b"S\n")
            arduino.flush()
            time.sleep(0.1)
        except serial.SerialException:
            pass

        arduino.close()

    print("Serial connection closed.")
