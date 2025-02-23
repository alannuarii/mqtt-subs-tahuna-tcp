import config
import paho.mqtt.client as mqtt
from db import write_to_influxdb  


# Definisikan callback untuk event ketika terhubung ke broker MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Berhasil terhubung ke broker MQTT")
        client.subscribe(f"{config.MQTT_TOPIC}#")  # Menerima pesan dari semua topik 
    else:
        print(f"Gagal terhubung dengan kode hasil: {rc}")

# Definisikan callback untuk event ketika pesan diterima
def on_message(client, userdata, msg):
    try:
        topic_parts = msg.topic.split("/")
        if len(topic_parts) == 3:
            measurement = topic_parts[1]  
            key = topic_parts[2]  
            value = msg.payload.decode()  

            # Mengubah kunci menjadi format yang diinginkan
            key_mapping = {
                "currentL1": "Current L1",
                "currentL2": "Current L2",
                "currentL3": "Current L3",
                "voltageL1L2": "Voltage L1 L2",
                "voltageL2L3": "Voltage L2 L3",
                "voltageL3L1": "Voltage L3 L1",
                "activePower": "Active Power",
                "reactivePower": "Reactive Power",
                "powerFactor": "Power Factor",
                "frequency": "Frequency",
                "timestamp": "Timestamp"
            }
            # Mencocokkan kunci dengan key_mapping
            formatted_key = key_mapping.get(key, None)

            # Cek apakah value bisa dikonversi menjadi float
            try:
                value = float(value)
            except ValueError:
                value = None  # Jika tidak bisa dikonversi, set value menjadi None

            # Simpan data hanya jika formatted_key ada dalam daftar yang diizinkan
            if formatted_key and formatted_key != "Timestamp":
                write_to_influxdb(measurement, formatted_key, value)
                print(f"Data berhasil disimpan: {measurement} -> {formatted_key}: {value}")
            else:
                print(f"Kunci tidak valid: {key}. Data tidak disimpan.")
        else:
            print(f"Format topik tidak dikenali: {msg.topic}")
    except Exception as e:
        print(f"Error memproses pesan: {e}")

# Membuat client MQTT dengan transport TCP
client = mqtt.Client(client_id="", protocol=mqtt.MQTTv311, transport="tcp")

# Menambahkan autentikasi username dan password
client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)

# Tetapkan callback
client.on_connect = on_connect
client.on_message = on_message

# Hubungkan ke broker MQTT melalui TCP 
client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)

# Jalankan loop untuk memproses callback secara terus-menerus
client.loop_forever()
