# module imports
import machine
import network
import ssl
import time
import ubinascii

from umqttsimple import MQTTClient


#Wifi setup
SSID = " "
WIFI_PASSWORD = ""

#device name 
MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id())

### Replace with the names of the files from your certs and keys
MQTT_CLIENT_KEY = "PrivateKEY.private.pem.key"
MQTT_CLIENT_CERT = "CRT.pem.crt"

### You can find this URL by going into the AWS IoT Core Settings under "Endpoint"
MQTT_BROKER = "ENDPOINT/DOMAIN NAME.amazonaws.com"
MQTT_BROKER_CA = "AmazonRootCA1.pem"

led = True


# function that reads PEM file and return byte array of data
def read_pem(file):
    with open(file, "r") as input:
        text = input.read().strip()
        split_text = text.split("\n")
        base64_text = "".join(split_text[1:-1])
        return ubinascii.a2b_base64(base64_text)


def connect_internet():
    try:
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        sta_if.connect(SSID, WIFI_PASSWORD)

        for i in range(0, 10):
            if not sta_if.isconnected():
                time.sleep(1)
        print("Connected to Wi-Fi")
    except Exception as e:
        print('There was an issue connecting to WIFI')
        print(e)


# callback function to handle received MQTT messages
def on_mqtt_msg(topic, msg):
    # convert topic and message from bytes to string
    topic_str = topic.decode()
    msg_str = msg.decode()

    print(f"RX: {topic_str}\n\t{msg_str}")

    # process message
    if topic_str is 'Hello_bye':
        if msg_str is "Hi":
            print("Hi")
        elif msg_str is "Bye":
            print("Bye")
            
    elif topic_str is 'Door':
        if msg_str is "Open":
            print("Door is opened")
        elif msg_str is "Close":
            print("Door is opened")
        


connect_internet()
# read the data in the private key, public certificate, and
# root CA files
key = read_pem(MQTT_CLIENT_KEY)
cert = read_pem(MQTT_CLIENT_CERT)
ca = read_pem(MQTT_BROKER_CA)

# create MQTT client that use TLS/SSL for a secure connection
mqtt_client = MQTTClient(
    MQTT_CLIENT_ID,
    MQTT_BROKER,
    keepalive=60,
    ssl=True,
    ssl_params={
        "key": key,
        "cert": cert,
        "server_hostname": MQTT_BROKER,
        "cert_reqs": ssl.CERT_REQUIRED,
        "cadata": ca,
    },
)

print(f"Connecting to MQTT broker")
# register callback to for MQTT messages, connect to broker and
# subscribe to LED topic
mqtt_client.set_callback(on_mqtt_msg)
mqtt_client.connect()
mqtt_client.subscribe('LED')


# main loop, continuously check for incoming MQTT messages
print("Connection established, awaiting messages")
while True:
    mqtt_client.check_msg()
    
    
# Refrences 
# https://shillehtek.com/blogs/news/pico-w-aws-iot-core-led-control
#https://community.element14.com/products/raspberry-pi/b/blog/posts/connecting-a-raspberry-pi-to-aws-iot-core
#https://docs.aws.amazon.com/iot/latest/developerguide/connecting-to-existing-device.html