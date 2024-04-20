import sys
from Adafruit_IO import MQTTClient
import time
from SpeechToTextAssistant import *
import re

AIO_FEED_ID = ["fan", "led", "in-led"]
AIO_USERNAME = "olkmphy"
AIO_KEY = "aio_Ukvq13BJAgCESTDC6Stf9D1EfZaR"


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

while True:
    # Listen for speech input and convert it to text
    speech_text = recognize_speech_from_microphone()

    if priority == 0:
        # Check if the phrase "Turn on the light" is detected
        if speech_text.lower() == "turn on the light":
            speak("Which light, master?")
            status = 1
            priority = 1

        elif speech_text.lower() == "turn off the light":
            speak("Which light, master?")
            status = 0
            priority = 1

        elif "turn on the fan at" in speech_text.lower():
            percentage = fan_process(speech_text.lower())
            percentage = percentage[0:len(percentage) - 1]
            percentage = int(percentage)
            if percentage > 100:
                percentage = 100
            elif percentage < 0:
                percentage = 0
            percentage = str(percentage)
            myClient.publish("fan", percentage)

        elif speech_text.lower() == "turn off the fan":
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