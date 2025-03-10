import time
import json
import OPi.GPIO as GPIO
import paho.mqtt.client as mqtt

# Fungsi untuk mengonversi nilai kecepatan (0-100) ke duty cycle (46-50%)
def speed_to_duty_cycle(speed_percent):
    """Mengonversi kecepatan dalam persen (0-100%) ke duty cycle (46-50%)."""
    if speed_percent <= 0:
        return 46.0  # Duty cycle minimum
    elif speed_percent >= 100:
        return 50.0  # Duty cycle maksimum
    else:
        # Hitung duty cycle linier antara 46% dan 50%
        return 46.0 + (speed_percent * (50.0 - 46.0) / 100.0)

# Variabel global untuk PWM
pwm = None

# Fungsi untuk menangani pesan yang diterima dari MQTT
def on_message(client, userdata, msg):
    global pwm  # Gunakan variabel global pwm
    try:
        # Decode payload sebagai JSON
        payload = json.loads(msg.payload.decode())

        # Ambil nilai speed dari JSON
        if "speed" in payload:
            speed_percent = int(payload["speed"])
            
            # Validasi kecepatan (0-100%)
            if 0 <= speed_percent <= 100:
                duty_cycle = speed_to_duty_cycle(speed_percent)
                print(f"Motor bergerak dengan kecepatan {speed_percent}% (Duty Cycle {duty_cycle:.2f}%)")
                pwm.duty_cycle(duty_cycle)  # Atur motor ke kecepatan yang diterima
            else:
                print("Masukkan kecepatan antara 0 dan 100%.")
        else:
            print("Pesan tidak memiliki kunci 'speed'.")

    except json.JSONDecodeError:
        print("Pesan yang diterima bukan format JSON valid.")
    except ValueError:
        print("Nilai speed bukan angka valid.")

# Fungsi utama untuk setup dan menjalankan MQTT
def main():
    global pwm  # Gunakan variabel global pwm
    print("Menginisialisasi PWM untuk kontrol motor...")

    # Setup GPIO
    GPIO.setmode(GPIO.BOARD)  # Atur nomor pin berdasarkan board
    PWM_chip = 0              # Chip PWM (biasanya 0 pada Orange Pi)
    PWM_pin = 1               # Pin yang digunakan (sesuaikan dengan pin yang Anda gunakan)
    frequency_Hz = 50         # Frekuensi PWM untuk motor (50 Hz)
    duty_cycle_percent = 46.0  # Mulai dengan duty cycle minimum

    try:
        # Konfigurasi PWM
        pwm = GPIO.PWM(PWM_chip, PWM_pin, frequency_Hz, duty_cycle_percent)
        pwm.start_pwm()  # Mulai PWM dengan duty cycle awal
        print(f"PWM dimulai pada frekuensi {frequency_Hz}Hz dengan duty cycle {duty_cycle_percent}%.")

        # Setup MQTT
        mqtt_broker = "192.168.195.49"  # Ganti dengan alamat broker MQTT Anda
        mqtt_port = 1883
        mqtt_topic = "slider/data"  # Topik untuk menerima data kecepatan motor

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
            pwm.duty_cycle(46.0)  # Set duty cycle ke nilai minimum sebelum mematikan
            pwm.stop_pwm()        # Matikan PWM
            pwm.pwm_close()       # Tutup pin PWM
        GPIO.cleanup()            # Bersihkan konfigurasi GPIO
        print("PWM dimatikan, GPIO bersih.")
        client.loop_stop()  # Berhenti mendengarkan pesan MQTT

if __name__ == "__main__":
    main()
