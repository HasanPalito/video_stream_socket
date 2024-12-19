import asyncio
import cv2
import websockets

async def send_images():
    async with websockets.connect("ws://3.129.58.174:9999/sender") as websocket:
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
