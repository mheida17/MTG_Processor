from time import sleep
from picamera2 import Picamera2, Preview
from gpiozero import Servo
from gpiozero import PWMLED
from gpiozero import LED
from gpiozero import Button
from libcamera import controls  # Needed for focus controls
from threading import Thread
from threading import Event
import cv2
import pytesseract

img_num = 1


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


def takePhoto(camera):
    global img_num
    filename = "images/foo" + str(img_num) + ".jpg"
    print(f"Capturing image {filename}")
    camera.start()
    camera.stop_preview()
    camera.start_preview(False)
    camera.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 10.0})
    sleep(2)
    camera.capture_file(filename)
    img_num += 1
    return filename


def pushCard(ir_sensor, servo, enable):
    while not detectCard(ir_sensor) and enable:
        if event.is_set():
            return
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


def lowerCardPin(servo):
    servo.value = -1


def raiseCardPin(servo):
    servo.value = 1


def detectCard(ir_sensor):
    if ir_sensor.value == 1:
        print("Card Detected")
        return True
    else:
        print("Card Not Detected")
        return False


def enableLED(led1, led2):
    led1.value = 0.1
    led2.on()


def disableLED(led1, led2):
    led1.off()
    led2.off()


def handleButton(button):
    print("handleButton enter")
    button.wait_for_press()
    print("Button pressed")


def dropCard(pin_servo, ir_sensor, event):
    print("Dropping Card")
    lowerCardPin(pin_servo)
    while detectCard(ir_sensor):
        if event.is_set():
            return
        sleep(1)
    raiseCardPin(pin_servo)


def processPhoto(filename):
    image = cv2.imread(filename, 0)
    thresh = (
        255 - cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    )

    x, y, w, h = 3750, 100, 250, 1250
    ROI = thresh[y : y + h, x : x + w]
    rotated = cv2.rotate(ROI, cv2.ROTATE_90_COUNTERCLOCKWISE)
    card_name = pytesseract.image_to_string(rotated, lang="eng", config="--psm 7")
    print(f"Card Name {card_name}")
    return card_name


def pushCardDB(card_name):
    with open("cardList.txt", "a") as cardFile:
        cardFile.writelines(card_name)


def processCards(event):
    # Clear any old cards if program stopped unexpectedly
    if detectCard(ir_sensor):
        dropCard(pin_servo, ir_sensor, event)
    while True:
        pushCard(ir_sensor, push_servos, True)
        while not detectCard(ir_sensor):
            if event.is_set():
                return
            sleep(0.25)
        pushCard(ir_sensor, push_servos, False)
        enableLED(led1, led2)
        sleep(1)
        filename = takePhoto(camera)
        disableLED(led1, led2)
        card_name = processPhoto(filename)
        pushCardDB(card_name)
        dropCard(pin_servo, ir_sensor, event)


if __name__ == "__main__":
    camera, pin_servo, push_servos, led1, led2, button, ir_sensor = initHardware()
    event = Event()
    thread = Thread(target=processCards, args=(event,))
    thread.start()
    handleButton(button)
    event.set()
    print("Trying to join thread")
    thread.join()
    print("JOINED THREAD")
    handleButton(button)
