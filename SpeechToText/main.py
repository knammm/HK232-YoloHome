import sys
import threading
import cv2
from deepface import DeepFace
from Adafruit_IO import MQTTClient
import time
from SpeechToTextAssistant import *
import re

AIO_FEED_ID = ["fan", "led", "in-led"]
AIO_USERNAME = "olkmphy"
AIO_KEY = "aio_nPtu8489JWRI74FLwGoCysDRbnxX"


def connected(client):
    for topic in AIO_FEED_ID:
        print("Ket noi thanh cong toi topic " + topic)
        client.subscribe(topic)


def subscribe(client, userdata, mid, granted_qos):
    print("Subscribe thanh cong ...")


def disconnected(client):
    print("Ngat ket noi ...")
    sys.exit(1)


def message(client, feed_id, payload):
    print("Receive Data from: " + feed_id + "_" + payload)


# Connect to Adafruit
myClient = MQTTClient(AIO_USERNAME, AIO_KEY)
myClient.on_connect = connected
myClient.on_disconnect = disconnected
myClient.on_message = message
myClient.on_subscribe = subscribe
myClient.connect()
myClient.loop_background()


# Setup face identification
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

counter = 0
face_match = False
ref_img = cv2.imread("public/auth/khanh.jpg")


def face_auth(frame):
    global face_match
    try:
        if DeepFace.verify(frame, ref_img.copy())['verified']:
            face_match = True
        else:
            face_match = False
    except ValueError:
        face_match = False


while True:
    ret, frame = cap.read()

    if ret:
        if counter % 30 == 0:
            try:
                thread = threading.Thread(target=face_auth, args=(frame.copy(),)).start()
            except ValueError:
                pass
        counter +=1

        if face_match:
            cv2.putText(frame, "MATCH!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        else:
            cv2.putText(frame, "NO MATCH!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

        cv2.imshow('video', frame)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cv2.destroyAllWindows()


def fan_process(text):
    # Define a regular expression pattern to match percentage values
    pattern = r'\b(\d+)%'

    # Use re.search() to find the percentage value in the text
    match = re.search(pattern, text)

    if match:
        percentage = match.group(0)
        return percentage
    else:
        return "0%"


priority = 0
status = 0

time.sleep(3)

LIGHT_COMMANDS = {
    "inside": ["inside light", "in light", "light inside"],
    "outside": ["outside light", "out light", "light outside"],
    "both": ["both lights", "all lights", "both", "all"]
}


# Function to perform action based on speech command
def perform_action(light, action):
    print(f"Turning {action} the {light}...")
    value_light = "0" if action == "off" else "1"

    if light == "inside":
        key_light = "in-led"
        myClient.publish(key_light, value_light)
    elif light == "outside":
        key_light = "led"
        myClient.publish(key_light, value_light)
    elif light == "both":
        myClient.publish("in-led", value_light)
        myClient.publish("led", value_light)


# while True:
#     # Listen for speech input and convert it to text
#     speech_text = recognize_speech_from_microphone()
#
#     if priority == 0:
#         # Check if the phrase "Turn on the light" is detected
#         if speech_text.lower() == "turn on the light":
#             speak("Which light, master?")
#             status = 1
#             priority = 1
#
#         for light, commands in LIGHT_COMMANDS.items():
#             for command in commands:
#                 if command in speech_text.lower():
#                     action = "on" if "turn on" in speech_text else "off"
#                     perform_action(light, action)
#
#         if "turn on the fan at" in speech_text.lower():
#             percentage = fan_process(speech_text.lower())
#             percentage = percentage[0:len(percentage) - 1]
#             percentage = int(percentage)
#             if percentage > 100:
#                 percentage = 100
#             elif percentage < 0:
#                 percentage = 0
#             percentage = str(percentage)
#             print(f"Turning on the fan at {percentage}...")
#             myClient.publish("fan", percentage)
#
#         elif speech_text.lower() == "turn off the fan":
#             print(f"Turning off the fan...")
#             myClient.publish("fan", 0)
#     else:
#         if "all" in speech_text.lower():
#             myClient.publish("led", str(status))
#             myClient.publish("in-led", str(status))
#
#         elif "inside" in speech_text.lower():
#             myClient.publish("in-led", str(status))
#
#         elif "outside" in speech_text.lower():
#             myClient.publish("led", str(status))
#
#         else:
#             speak("I did not recognize the command!")
#
#         priority = 0
#     time.sleep(1)
