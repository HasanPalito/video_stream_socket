import time
import json
import OPi.GPIO as GPIO
import paho.mqtt.client as mqtt

# Deklarasi variabel global untuk PWM
pwm = None

# Fungsi untuk mengonversi sudut (0-180) ke duty cycle (1 ms - 2 ms)
def angle_to_duty_cycle(angle):
    """Mengonversi sudut (0-180) ke duty cycle (1ms - 2ms) untuk motor servo"""
    duty_cycle = 4 + (angle / 180) * 7  # 5% duty cycle untuk 0 derajat dan 10% untuk 180 derajat
    return duty_cycle

# Fungsi untuk menangani pesan yang diterima dari MQTT
def on_message(client, userdata, msg):
    global pwm  # Gunakan variabel global pwm
    try:
        # Ambil payload pesan MQTT dan ubah ke dictionary
        data = json.loads(msg.payload.decode())

        # Ambil nilai sudut untuk servo1
        if "servo1" in data:
            angle_servo1 = int(data["servo1"])
            
            # Validasi sudut (0 - 180 derajat)
            if 0 <= angle_servo1 <= 180:
                duty_cycle = angle_to_duty_cycle(angle_servo1)
                print(f"Servo1 bergerak ke {angle_servo1} derajat dengan duty cycle {duty_cycle:.2f}%")
                pwm.duty_cycle(duty_cycle)  # Atur servo ke sudut yang diterima
            else:
                print("Masukkan sudut antara 0 dan 180 derajat untuk servo1.")
        else:
            print("Payload tidak memiliki data untuk 'servo1'.")
    
    except json.JSONDecodeError:
        print("Pesan yang diterima bukan format JSON valid.")
    except ValueError:
        print("Data untuk servo1 bukan angka valid.")

# Fungsi untuk mengkalibrasi servo
def calibrate_servo(pwm):
    """Kalibrasi servo ke sudut 0 dan 180 derajat"""
    print("Memulai kalibrasi servo...")

    # Menggerakkan servo ke sudut 0 derajat
    print("Posisi 0 derajat...")
    pwm.duty_cycle(angle_to_duty_cycle(0))
    time.sleep(2)

    # Menggerakkan servo ke sudut 180 derajat
    print("Posisi 180 derajat...")
    pwm.duty_cycle(angle_to_duty_cycle(180))
    time.sleep(2)

    # Kembali ke posisi 90 derajat
    print("Posisi 90 derajat (netral)...")
    pwm.duty_cycle(angle_to_duty_cycle(90))
    time.sleep(1)

    print("Kalibrasi selesai! Servo siap digunakan.")

# Fungsi utama untuk setup dan menjalankan MQTT
def main():
    global pwm  # Gunakan variabel global pwm
    print("Menginisialisasi PWM untuk kontrol servo...")

    # Setup GPIO
    GPIO.setmode(GPIO.BOARD)  # Atur nomor pin berdasarkan board
    PWM_chip = 0              # Chip PWM (biasanya 0 pada Orange Pi)
    PWM_pin = 2               # Pin yang digunakan (sesuaikan dengan pin yang Anda gunakan)
    frequency_Hz = 50         # Frekuensi PWM untuk servo (50 Hz)
    duty_cycle_percent = 7.5  # Mulai dengan posisi netral (~1.5 ms pulsa)

    try:
        # Konfigurasi PWM
        pwm = GPIO.PWM(PWM_chip, PWM_pin, frequency_Hz, duty_cycle_percent)
        pwm.start_pwm()  # Mulai PWM dengan duty cycle awal
        print(f"PWM dimulai pada frekuensi {frequency_Hz}Hz dengan duty cycle {duty_cycle_percent}%.")

        # Kalibrasi servo
        calibrate_servo(pwm)

        # Setup MQTT
        mqtt_broker = "192.168.195.49"  # Ganti dengan alamat broker MQTT Anda
        mqtt_port = 1883
        mqtt_topic = "joystick/data"  # Topik untuk menerima data sudut

        client = mqtt.Client()  # Membuat objek client MQTT
        client.on_message = on_message  # Menetapkan fungsi callback untuk pesan MQTT

        print(f"Menghubungkan ke broker MQTT di {mqtt_broker}...")
        client.connect(mqtt_broker, mqtt_port, 60)

        # Subscribe ke topik
        client.subscribe(mqtt_topic)
        print(f"Mendengarkan topik {mqtt_topic}...")

        # Loop utama untuk mendengarkan pesan MQTT
        client.loop_start()  # Mulai loop MQTT

        while True:
            time.sleep(1)  # Program berjalan sambil menunggu pesan MQTT

    except Exception as e:
        print(f"Terjadi error: {e}")
    
    finally:
        print("Menutup PWM dan GPIO...")
        if pwm:  # Pastikan pwm telah diinisialisasi sebelum mencoba mematikannya
            pwm.duty_cycle(0)  # Matikan motor dengan duty cycle 0%
            pwm.stop_pwm()     # Matikan PWM
            pwm.pwm_close()    # Tutup pin PWM
        GPIO.cleanup()         # Bersihkan konfigurasi GPIO
        print("PWM dimatikan, GPIO bersih.")
        client.loop_stop()  # Berhenti mendengarkan pesan MQTT

if __name__ == "__main__":
    main()
