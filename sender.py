import asyncio
import cv2
import websockets

async def send_images():
    async with websockets.connect("ws://localhost:9999/sender") as websocket:
        cap = cv2.VideoCapture(0)

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                buffer = cv2.imencode('.jpg', frame)[1].tobytes()
                await websocket.send(buffer)
                await asyncio.sleep(0.05)
        finally:
            cap.release()

import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")
    #control logic here

client = mqtt.Client()

client.on_message = on_message

client.connect("localhost", 1883, 60)

topic = "joystick/data"
client.subscribe(topic)
client.loop_forever()

asyncio.get_event_loop().run_until_complete(send_images())