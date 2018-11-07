import picamera

def camera_shot(image):
    camera = picamera.PiCamera()
    try:        
        camera.capture(image)    
    finally:
        camera.close()
    
