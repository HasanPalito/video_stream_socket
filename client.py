import asyncio
import websockets

# Global sets to store WebSocket connections
sender_client = None
viewer_clients = set()

async def handle_sender(websocket, path):
    """Handle incoming image data from the sender."""
    global sender_client
    sender_client = websocket
    print("Sender connected.")
    
    try:
        while True:
            # Receive binary image data from the sender
            image_data = await websocket.recv()

            # Broadcast the image to all connected viewers
            if viewer_clients:
                tasks = [client.send(image_data) for client in viewer_clients]
                await asyncio.gather(*tasks)

    except websockets.exceptions.ConnectionClosed:
        print("Sender disconnected.")
    
    finally:
        sender_client = None

async def handle_viewer(websocket, path):
    """Handle image viewers (clients)."""
    viewer_clients.add(websocket)
    print(f"Viewer connected: {len(viewer_clients)} clients total.")
    
    try:
        await websocket.wait_closed()  # Keep connection open for this client
    
    finally:
        viewer_clients.remove(websocket)
        print(f"Viewer disconnected: {len(viewer_clients)} clients remaining.")

async def main():
    # Create a WebSocket server handling both sender and viewer clients
    server = websockets.serve(handle_sender, "0.0.0.0", 9997)  # For the sender
    viewer_server = websockets.serve(handle_viewer, "0.0.0.0", 9998)  # For viewers

    # Wait until both servers are up
    await asyncio.gather(server, viewer_server)

# Start the WebSocket server
asyncio.get_event_loop().run_until_complete(main())
asyncio.get_event_loop().run_forever()
