import asyncio
import cv2
import websockets
import numpy as np

# Global list to store all connected WebSocket clients
connected_clients = set()

async def broadcast_frames():
    cap = cv2.VideoCapture(0)
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Encode the frame as a JPEG
            buffer = cv2.imencode('.jpg', frame)[1].tobytes()

            # Create a list of tasks to send frames to all connected clients
            if connected_clients:  # Only try to send if there are connected clients
                tasks = [client.send(buffer) for client in connected_clients]
                await asyncio.gather(*tasks)  # Use gather to wait for all send tasks

            # Small delay to control frame rate
            await asyncio.sleep(0.05)

    finally:
        cap.release()

async def handle_client(websocket, path):
    # Register the new client
    connected_clients.add(websocket)
    print(f"Client connected: {len(connected_clients)} clients total.")

    try:
        # Keep connection open for this client
        await websocket.wait_closed()
    finally:
        # Unregister the client when they disconnect
        connected_clients.remove(websocket)
        print(f"Client disconnected: {len(connected_clients)} clients remaining.")

start_server = websockets.serve(handle_client, "0.0.0.0", 9999)

# Start the WebSocket server and the frame broadcasting loop
loop = asyncio.get_event_loop()
loop.run_until_complete(start_server)
loop.create_task(broadcast_frames())
loop.run_forever()