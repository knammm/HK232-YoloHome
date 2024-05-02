import sys
from Adafruit_IO import MQTTClient
import time
from FaceAuth import face_auth
from SpeechToTextAssistant import *
import re
import requests

AIO_FEED_ID = ["fan", "led", "in-led", "announcement"]
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
    print(f"Received value {payload} from topic {feed_id}")
    if feed_id == "announcement" and payload == "true":
        # Call API
        response = requests.get("https://dadn.vercel.app/api/notify/door")
        if response.status_code == 200:
            print("API call successful.")
        else:
            print("API call failed. Status code:", response.status_code)



# Connect to Adafruit
myClient = MQTTClient(AIO_USERNAME, AIO_KEY)
myClient.on_connect = connected
myClient.on_disconnect = disconnected
myClient.on_message = message
myClient.on_subscribe = subscribe
myClient.connect()
myClient.loop_background()


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


while True:
    # Listen for speech input and convert it to text
    speech_text = recognize_speech_from_microphone()

    if priority == 0:
        # Check if the phrase "Face ID" is detected
        if speech_text.lower() == "face id":
            authenticated = face_auth()
            if authenticated:
                print(f"Authenticated...")
                myClient.publish("authentication", "true")
            else:
                print(f"Fail to authenticate...")
        # Check if the phrase "Turn on the light" is detected
        if speech_text.lower() == "turn on the light":
            speak("Which light, master?")
            status = 1
            priority = 1

        for light, commands in LIGHT_COMMANDS.items():
            for command in commands:
                if command in speech_text.lower():
                    action = "on" if "turn on" in speech_text else "off"
                    perform_action(light, action)

        if "turn on the fan at" in speech_text.lower():
            percentage = fan_process(speech_text.lower())
            percentage = percentage[0:len(percentage) - 1]
            percentage = int(percentage)
            if percentage > 100:
                percentage = 100
            elif percentage < 0:
                percentage = 0
            percentage = str(percentage)
            print(f"Turning on the fan at {percentage}...")
            myClient.publish("fan", percentage)

        elif speech_text.lower() == "turn off the fan":
            print(f"Turning off the fan...")
            myClient.publish("fan", 0)
    else:
        if "all" in speech_text.lower():
            myClient.publish("led", str(status))
            myClient.publish("in-led", str(status))

        elif "inside" in speech_text.lower():
            myClient.publish("in-led", str(status))

        elif "outside" in speech_text.lower():
            myClient.publish("led", str(status))

        else:
            speak("I did not recognize the command!")

        priority = 0
    time.sleep(1)
