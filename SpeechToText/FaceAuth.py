import threading
import cv2
from deepface import DeepFace
from SpeechToTextAssistant import *


# Setup face identification
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

face_match = False

# Get all image files in the directory
ref_image_dir = "public/auth"
ref_image_paths = [os.path.join(ref_image_dir, f) for f in os.listdir(ref_image_dir) if os.path.isfile(os.path.join(ref_image_dir, f))]


def face_auth_process(frame):
    global face_match
    try:
        for ref_img_path in ref_image_paths:
            ref_img = cv2.imread(ref_img_path)
            if DeepFace.verify(frame, ref_img.copy())['verified']:
                face_match = True
                return  # Exit the loop if a match is found
        face_match = False  # If no match is found
    except ValueError:
        face_match = False


def face_auth():
    global face_match
    face_match = False
    counter = 0
    print(f"Authenticating by face ID...")
    while True:
        ret, frame = cap.read()

        if ret:
            if counter % 30 == 0:
                try:
                    thread = threading.Thread(target=face_auth_process, args=(frame.copy(),))
                    thread.start()
                except ValueError:
                    pass
            counter += 1

            if face_match:
                cv2.putText(frame, "MATCH!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
                cv2.imshow('video', frame)
                cv2.waitKey(2000)  # Wait for 2 seconds
                break
            else:
                cv2.putText(frame, "NO MATCH!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                cv2.imshow('video', frame)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    cv2.destroyAllWindows()
    return face_match
