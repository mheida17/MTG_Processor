from time import sleep
from picamera2 import Picamera2, Preview
from gpiozero import Servo
from gpiozero import PWMLED
from gpiozero import LED
from gpiozero import Button

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print(
        "Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script"
    )
from threading import Thread
from threading import Event
import os
from fractions import Fraction

img_num = 1


def initHardware():
    camera = Picamera2()
    config = camera.create_still_configuration()
    camera.configure(config)
    pin_servo = Servo(27, initial_value=1)
    push_servo = Servo(12, initial_value=-0.1)  # requires offset
    led1 = LED(18)  # bottom
    led2 = LED(19)  # top
    button = Button(pin=22, pull_up=True)
    ir_sensor = Button(pin=17, pull_up=True)
    return (camera, pin_servo, push_servo, led1, led2, button, ir_sensor)


def takePhoto(camera):
    global img_num
    filename = "foo" + str(img_num) + ".jpg"
    print(f"Capturing image {filename}")
    sleep(3)
    camera.start_and_capture_file(show_preview=False)
    # camera.stop()
    img_num += 1
    return filename


def pushCard(servo, enable):
    value = 0.2 if enable else -0.1
    print(f"Setting Servo {value}")
    servo.value = value


def lowerCardPin(servo):
    print("dropCard")
    servo.value = -1


def raiseCardPin(servo):
    print("Raise Card Pin")
    servo.value = 1


def detectCard(ir_sensor):
    if ir_sensor.value == 1:
        print("Card Detected")
        return True
    else:
        print("Card Not Detected")
        return False


def enableLED(led1, led2):
    led1.on()
    led2.on()


def disableLED(led1, led2):
    led1.off()
    led2.off()


def handleButton(button):
    print("handleButton enter")
    button.wait_for_press()
    print("Button pressed")


def processPhoto(filename):
    print(f"processPhoto {filename}")


def updateDatabase():
    print("updateDatabase")


def savePhoto():
    print("savePhoto")


def processCards(event):
    while True:
        pushCard(push_servos, True)
        while not detectCard(ir_sensor):
            if event.is_set():
                return
            sleep(0.25)
        pushCard(push_servos, False)
        enableLED(led1, led2)
        sleep(1)
        filename = takePhoto(camera)
        disableLED(led1, led2)
        processPhoto(filename)
        lowerCardPin(pin_servo)
        while detectCard(ir_sensor):
            if event.is_set():
                return
            sleep(1)
        raiseCardPin(pin_servo)


if __name__ == "__main__":
    camera, pin_servo, push_servos, led1, led2, button, ir_sensor = initHardware()
    # filename = takePhoto(camera)
    # print(f"took a picture named {filename}")
    event = Event()
    thread = Thread(target=processCards, args=(event,))
    thread.start()
    handleButton(button)
    event.set()
    print("Trying to join thread")
    thread.join()
    print("JOINED THREAD")
    handleButton(button)
