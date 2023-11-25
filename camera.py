from picamera2 import Picamera2, Preview
from libcamera import controls  # Needed for focus controls
from time import sleep

img_num = 1


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
