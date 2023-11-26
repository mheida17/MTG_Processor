from time import sleep
from threading import Thread
from threading import Event
import cv2
import pytesseract
from hardware import (
    initHardware,
    enableLED,
    disableLED,
    detectCard,
    handleButton,
    pushCard,
    dropCard,
)
from camera import takePhoto
from sf_price_fetcher import fetcher


def cleanUpCardName(card_name):
    index = 0
    for c in card_name:
        if c.isalpha():
            first_slice = card_name[index:]
            break
        index = index + 1
    if first_slice is None:
        return "Empty"
    index = len(first_slice) - 1

    for c in first_slice[::-1]:
        if c.isalpha():
            final_slice = first_slice[:index]
            break
        index = index - 1
    if final_slice is None:
        return "Empty"
    return final_slice


def processPhoto(filename):
    image = cv2.imread(filename, 0)
    thresh = (
        255 - cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    )

    x, y, w, h = 3750, 100, 450, 1250
    ROI = thresh[y : y + h, x : x + w]
    rotated = cv2.rotate(ROI, cv2.ROTATE_90_COUNTERCLOCKWISE)
    cv2.imwrite("name.jpg", rotated)
    card_name_detected = pytesseract.image_to_string(
        rotated, lang="eng", config="--psm 7"
    )
    if card_name_detected is None:
        return "Empty"
    card_name_modified = cleanUpCardName(card_name_detected)
    print(f"Card Name {card_name_detected}")
    print(f"Modified Card Name {card_name_modified}")
    return card_name_modified


def pushCardDB(card_name):
    price = fetcher.get(card_name)
    if price is not None:
        print(f"Found price: {price}")
        with open("cardList.txt", "a") as cardFile:
            cardFile.writelines(card_name)


def processCards(event):
    # Clear any old cards if program stopped unexpectedly
    if detectCard(ir_sensor):
        dropCard(pin_servo, ir_sensor)
    while True:
        pushCard(ir_sensor, push_servos, True)
        while not detectCard(ir_sensor):
            # if event.is_set():
            #    return
            sleep(0.25)
        pushCard(ir_sensor, push_servos, False)
        enableLED(led1, led2)
        sleep(1)
        filename = takePhoto(camera)
        disableLED(led1, led2)
        card_name = processPhoto(filename)
        pushCardDB(card_name)
        dropCard(pin_servo, ir_sensor)


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
