import asyncio
import cv2
import websockets

# Fungsi untuk mengirimkan gambar melalui WebSocket
async def send_images():
    async with websockets.connect("ws://192.168.195.49:9999/sender") as websocket:
        cap = cv2.VideoCapture(0)  # Ganti dengan ID kamera yang sesuai

        if not cap.isOpened():
            print("Kamera tidak terdeteksi! Pastikan kamera USB terhubung.")
            return

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Tidak dapat membaca frame dari kamera!")
                    break

                # Mengonversi frame menjadi JPEG dan mengirimkan melalui WebSocket
                _, buffer = cv2.imencode('.jpg', frame)
                await websocket.send(buffer.tobytes())
                print("Frame terkirim.")
                await asyncio.sleep(0.05)  # Sekitar 20 fps
        finally:
            cap.release()
            print("Kamera dilepas.")

# Fungsi utama untuk menjalankan pengiriman video
async def main():
    await send_images()

# Jalankan event loop asyncio
asyncio.get_event_loop().run_until_complete(main())
