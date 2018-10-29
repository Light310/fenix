import picamera

def camera_shot(image):
    camera = picamera.PiCamera()
    camera.capture(image)
