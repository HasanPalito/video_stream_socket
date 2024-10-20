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

                # Encode frame as JPEG
                buffer = cv2.imencode('.jpg', frame)[1].tobytes()

                # Send binary image data to the middleman
                await websocket.send(buffer)

                # Small delay to control frame rate
                await asyncio.sleep(0.05)

        finally:
            cap.release()

asyncio.get_event_loop().run_until_complete(send_images())