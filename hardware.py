from picamera2 import Picamera2
from gpiozero import PWMLED
from gpiozero import Button
from gpiozero import OutputDevice
from time import sleep


def initHardware():
    camera = Picamera2()
    config = camera.create_still_configuration()
    camera.configure(config)
    pin_servo = OutputDevice(4, active_high=True, initial_value=False)
    push_servo = OutputDevice(25, active_high=True, initial_value=False)
    led1 = PWMLED(18)  # bottom
    led2 = PWMLED(19)  # top
    button = Button(pin=22, pull_up=True)
    ir_sensor = Button(pin=17, pull_up=True)
    return (camera, pin_servo, push_servo, led1, led2, button, ir_sensor)


def lowerCardPin(servo):
    servo.on()


def raiseCardPin(servo):
    servo.off()
    sleep(1)


def enableLED(led1, led2):
    led1.value = 0.2  # bottom values 0 to 1
    led2.value = 0.48  # top


def disableLED(led1, led2):
    led1.off()
    led2.off()


def detectCard(ir_sensor):
    if ir_sensor.value == 1:
        return True
    else:
        return False


def pushCard(ir_sensor, servo, enable):
    while not detectCard(ir_sensor) and enable:
        servo.on()
    servo.off()


def dropCard(pin_servo, ir_sensor):
    lowerCardPin(pin_servo)
    while detectCard(ir_sensor):
        sleep(1)
    raiseCardPin(pin_servo)


def powerDown(pin_servo, card_servo):
    lowerCardPin(pin_servo)
    card_servo.off()
