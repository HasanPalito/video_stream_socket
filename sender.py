import asyncio
import cv2
import websockets
import numpy as np

async def send_frames(uri):
    async with websockets.connect(uri) as websocket:
        cap = cv2.VideoCapture(0)
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Encode the frame as a JPEG
                buffer = cv2.imencode('.jpg', frame)[1].tobytes()

                # Send the frame to the WebSocket server
                await websocket.send(buffer)

                # Small delay to control frame rate
                await asyncio.sleep(0.05)

        finally:
            cap.release()

if __name__ == "__main__":
    uri = "ws://localhost:9999"  # Update this with your server's address
    asyncio.run(send_frames(uri))