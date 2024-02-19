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
    powerDown,
)
from camera import takePhoto
from sf_price_fetcher import fetcher
import os
import sys
import signal
import scrython

img_num = 0


def signal_handler(signal_number, frame):
    powerDown(pin_servo, push_servos)
    sys.exit()


def cleanUpCardName(card_name):
    print(f"Cleaning up card name: {card_name}")
    index = 0
    for c in card_name:
        if c.isalpha():
            first_slice = card_name[index:]
            break
        index = index + 1
    try:
        index = len(first_slice)
        # print(f"First Pass: {first_slice}")
    except:
        return None

    for c in first_slice[::-1]:
        if c.isalpha():
            final_slice = first_slice[:index]
            break
        index = index - 1
    try:
        # print(f"Last Pass: {final_slice}")
        return final_slice
    except:
        return None


def processPhoto(filename):
    global img_num
    current_working_directory = os.getcwd()
    image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
    image = cv2.medianBlur(image, 5)
    # thresh = (
    #     255 - cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # )
    thresh = cv2.adaptiveThreshold(
        image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 3
    )

    x, y, w, h = 3820, 150, 180, 2000
    ROI = thresh[y : y + h, x : x + w]
    rotated = cv2.rotate(ROI, cv2.ROTATE_90_COUNTERCLOCKWISE)
    cv2.imwrite(current_working_directory + "/" + "images/current_card.jpg", rotated)
    cv2.imwrite(
        current_working_directory + "/" + "images/name_" + str(img_num) + ".jpg",
        rotated,
    )
    img_num = img_num + 1
    card_name_detected = pytesseract.image_to_string(
        rotated, lang="eng", config="--psm 7"
    )
    if card_name_detected is None or card_name_detected == "":
        print("No Card Name Detected")
        return None
    card_name_modified = cleanUpCardName(card_name_detected)
    if card_name_modified is None:
        print("Card Name Completely Stripped")
        return None
    try:
        scrython_card = scrython.cards.Named(fuzzy=card_name_modified)
    except Exception as e:
        print(f"Scrython {e}: {card_name_modified}")
        return None
    return scrython_card.name()


def pushCardDB(card_name):
    if card_name is None:
        return
    try:
        price = fetcher.get(card_name)
    except:
        print("Could not fetch price")
        return
    if price is not None:
        print(f"Writing to file {card_name} {price}")
        with open("cardList.txt", "a") as cardFile:
            cardFile.writelines("Found: " + card_name + ":" + str(price) + "\n")


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
    signal.signal(signal.SIGINT, signal_handler)
    processCards(None)
    # event = Event()
    # thread = Thread(target=processCards, args=(event,))
    # thread.start()
    # handleButton(button)
    # event.set()
    # print("Trying to join thread")
    # thread.join()
    # print("JOINED THREAD")
    # handleButton(button)
