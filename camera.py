from libcamera import controls  # Needed for focus controls
from time import sleep
import os

img_num = 0
current_working_directory = os.getcwd()


def takePhoto(camera):
    global img_num
    global current_working_directory
    filename = current_working_directory + "/" + "images/card_" + str(img_num) + ".jpg"
    print(f"Capturing image {filename}")
    camera.start()
    camera.stop_preview()
    camera.start_preview(False)
    camera.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 10.0})
    sleep(2)
    camera.capture_file(filename)
    img_num += 1
    return filename
