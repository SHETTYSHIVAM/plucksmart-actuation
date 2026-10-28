
import time
import serial

# ---------- Configuration ----------
ARDUINO_PORT = "COM3"  # Change to your Arduino COM port
BAUD_RATE = 9600

IMAGE_WIDTH = 704
IMAGE_HEIGHT = 704

CONFIDENCE_THRESHOLD = 0.50
DEAD_BAND = 40           # Pixels around image center
MOVE_DURATION = 0.5      # Motor movement pulse in seconds
MOTOR_SPEED = 160

arduino = None


def send_command(command):
    """Send a command to Arduino."""
    arduino.write(f"{command}\n".encode("ascii"))
    arduino.flush()
    print(f"Arduino command: {command}")


def process_detection(cherry_class, confidence, x, y):
    """
    Simulate Raspberry Pi 4 processing a detection
    received from Raspberry Pi 5.
    x, y represent the bounding-box center in pixels.
    """

    print("\n--- Detection received ---")
    print(f"Class: {cherry_class}")
    print(f"Confidence: {confidence:.2f}")
    print(f"Target pixel coordinates: ({x}, {y})")

    if cherry_class.lower() != "ripe":
        print("Target rejected: cherry is not ripe.")
        send_command("S")
        return

    if confidence < CONFIDENCE_THRESHOLD:
        print("Target rejected: confidence below threshold.")
        send_command("S")
        return

    if not (0 <= x < IMAGE_WIDTH and 0 <= y < IMAGE_HEIGHT):
        print("Invalid coordinates.")
        send_command("S")
        return

    center_x = IMAGE_WIDTH / 2
    offset_x = x - center_x

    print(f"Image center X: {center_x:.1f}")
    print(f"Horizontal offset: {offset_x:.1f} pixels")

    # Direction mapping for demonstration only.
    if offset_x < -DEAD_BAND:
        command = "L"
        direction = "LEFT"

    elif offset_x > DEAD_BAND:
        command = "R"
        direction = "RIGHT"

    else:
        command = "S"
        direction = "CENTER"

    print(f"Selected direction: {direction}")

    if command == "S":
        send_command("S")
        print("Target is centered; motors stopped.")
        return

    # Move briefly, then stop.
    send_command(command)
    time.sleep(MOVE_DURATION)
    send_command("S")

    print("Movement pulse completed.")


def main():
    global arduino

    try:
        arduino = serial.Serial(
            ARDUINO_PORT,
            BAUD_RATE,
            timeout=1,
            write_timeout=2
        )

        # Allow Arduino Uno to reset after opening serial.
        time.sleep(2)
        arduino.reset_input_buffer()

        print("Connected to Arduino Uno.")
        send_command(f"V{MOTOR_SPEED}")

        print("\nCoordinate-based actuation simulator")
        print("Image size: 704 x 704")
        print("Enter: class,confidence,x,y")
        print("Example: ripe,0.92,200,350")
        print("Type 'q' to quit.")

        while True:
            user_input = input("\nDetection> ").strip()

            if user_input.lower() == "q":
                break

            try:
                parts = [p.strip() for p in user_input.split(",")]

                if len(parts) != 4:
                    print("Use: class,confidence,x,y")
                    continue

                cherry_class = parts[0]
                confidence = float(parts[1])
                x = int(parts[2])
                y = int(parts[3])

                if not 0 <= confidence <= 1:
                    print("Confidence must be between 0 and 1.")
                    continue

                process_detection(cherry_class, confidence, x, y)

            except ValueError:
                print("Invalid input. Check the confidence and coordinates.")

    except serial.SerialException as error:
        print(f"Arduino connection error: {error}")

    except KeyboardInterrupt:
        print("\nInterrupted.")

    finally:
        if arduino and arduino.is_open:
            try:
                send_command("S")
            except serial.SerialException:
                pass

            arduino.close()

        print("Arduino connection closed.")


if __name__ == "__main__":
    main()
