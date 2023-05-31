from time import sleep
from picamera import PiCamera
from gpiozero import Servo
from gpiozero import PWMLED
from gpiozero import LED
from gpiozero import Button
import RPi.GPIO as GPIO
from threading import Thread
from threading import Event
import os
from fractions import Fraction

img_num = 0


def initHardware():
    camera = PiCamera(resolution=(1280, 720), framerate=Fraction(1, 3))
    pin_servo = Servo(27, initial_value=1)
    push_servo = Servo(12, initial_value=-0.1)  # requires offset
    led = LED(18)
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # IR pin
    button = Button(pin=22, pull_up=True)
    return (camera, pin_servo, push_servo, led, button)


def takePhoto(camera):
    global img_num
    filename = "foo" + str(img_num) + ".jpg"
    camera.capture(filename)
    img_num += 1
    return filename


def pushCard(servo, enable):
    value = 0.1 if enable else -0.1
    print("Setting Servo")
    servo.value = value


def dropCard(servo):
    print("dropCard")
    servo.value = -1
    sleep(2)
    servo.value = 1
    sleep(2)


def detectCard():
    if not GPIO.input(17):
        print("Card Detected")
        return True
    else:
        print("Card Not Detected")
        return False


def enableLED(led):
    led.on()


def handleButton(button):
    print("handleButton enter")
    button.wait_for_press()
    print("Button pressed")


def processPhoto():
    print("processPhoto")


def updateDatabase():
    print("updateDatabase")


def savePhoto():
    print("savePhoto")


def processCards(event):
    while True:
        pushCard(push_servos, True)
        while not detectCard():
            if event.is_set():
                return
            sleep(0.25)
        pushCard(push_servos, False)
        led.on()
        sleep(1)
        filename = takePhoto(camera)
        while detectCard():
            if event.is_set():
                return
            dropCard(pin_servo)
            sleep(1)
        led.off()


if __name__ == "__main__":
    print("Hello world")
    camera, pin_servo, push_servos, led, button = initHardware()
    event = Event()
    thread = Thread(target=processCards, args=(event,))
    thread.start()
    handleButton(button)
    event.set()
    print("Trying to join thread")
    thread.join()
    print("JOINED THREAD")
    handleButton(button)
    os.system("sudo shutdown now")
