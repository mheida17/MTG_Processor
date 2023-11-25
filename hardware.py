from picamera2 import Picamera2, Preview
from gpiozero import Servo
from gpiozero import PWMLED
from gpiozero import LED
from gpiozero import Button
from time import sleep


def initHardware():
    camera = Picamera2()
    config = camera.create_still_configuration()
    camera.configure(config)
    pin_servo = Servo(13, initial_value=1)
    push_servo = Servo(12, initial_value=None)
    led1 = PWMLED(18)  # bottom
    led2 = LED(19)  # top
    button = Button(pin=22, pull_up=True)
    ir_sensor = Button(pin=17, pull_up=True)
    return (camera, pin_servo, push_servo, led1, led2, button, ir_sensor)


def lowerCardPin(servo):
    servo.value = -1


def raiseCardPin(servo):
    servo.value = 1


def enableLED(led1, led2):
    led1.value = 0.1
    led2.on()


def disableLED(led1, led2):
    led1.off()
    led2.off()


def detectCard(ir_sensor):
    if ir_sensor.value == 1:
        print(f"Card Detected {ir_sensor.value}")
        return True
    else:
        print(f"Card Not Detected {ir_sensor.value}")
        return False


def pushCard(ir_sensor, servo, enable):
    while not detectCard(ir_sensor) and enable:
        #if event.is_set():
        #    return
        value = 0.6
        print(f"Setting Servo {value}")
        servo.value = value
        sleep(1)
        servo.value = None
        sleep(0.1)
        value = -0.1
        print(f"Setting Servo {value}")
        servo.value = value
        sleep(0.2)
        servo.value = None
        sleep(0.1)
    value = None
    print(f"Setting Servo {value}")
    servo.value = value


def dropCard(pin_servo, ir_sensor):
    print("Dropping Card")
    lowerCardPin(pin_servo)
    while detectCard(ir_sensor):
        #if event.is_set():
        #    return
        sleep(1)
    raiseCardPin(pin_servo)

def handleButton(button):
    print("handleButton enter")
    button.wait_for_press()
    print("Button pressed")
