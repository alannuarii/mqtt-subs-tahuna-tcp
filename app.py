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

            # Kunci-kunci 5 parameter engine lama yang hanya untuk Unit 6 dan 7
            old_engine_keys = ["oilPressure", "coolantTemp", "chargeAlt", "chargeAltVoltage", "batteryVoltage", "engineRpm"]

            # Hanya izinkan 5 parameter engine lama jika dari Unit 6 atau Unit 7
            if key in old_engine_keys and measurement.lower() not in ["engine-dg6", "engine-dg7"]:
                return  # Abaikan untuk engine 1, 8, 9

            # Mengubah kunci menjadi format yang diinginkan
            key_mapping = {
                # =============================================================
                # --- 1. PARAMETER EKSISTING ASLI (TIDAK DIUBAH SAMA SEKALI) ---
                # =============================================================
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
                "oilPressure": "Oil Pressure",
                "coolantTemp": "Coolant Temp",
                "chargeAlt": "Charge Alt",
                "batteryVoltage": "Battery Voltage",
                "engineRpm": "Engine RPM",
                "timestamp": "Timestamp",

                # =============================================================
                # --- 2. PENAMBAHAN STATUS & KONTROL (DSE 7310) ---
                # =============================================================
                "controlMode": "Control Mode",
                "globalAlarmStatus": "Global Alarm Status",
                "engineState": "Engine State",
                "chargeAltVoltage": "Charge Alt",

                # =============================================================
                # --- 3. PENAMBAHAN TEGANGAN & ARUS LENGKAP ---
                # =============================================================
                "voltageL1N": "Voltage L1 N",
                "voltageL2N": "Voltage L2 N",
                "voltageL3N": "Voltage L3 N",
                "voltageLN_Avg": "Voltage L N Avg",
                "voltageLL_Avg": "Voltage L L Avg",
                "currentN": "Current Neutral",
                "currentG": "Current Ground",
                "currentAvg": "Current Avg",
                "currentEarth": "Current Earth",
                "phaseRotation": "Phase Rotation",

                # =============================================================
                # --- 4. PENAMBAHAN DAYA PER FASA & TOTAL (kW & kVAR) ---
                # =============================================================
                "activePowerL1_kW": "Active Power L1 kW",
                "activePowerL2_kW": "Active Power L2 kW",
                "activePowerL3_kW": "Active Power L3 kW",
                "activePowerTotal_kW": "Active Power",
                "reactivePowerL1_kVAr": "Reactive Power L1 kVAr",
                "reactivePowerL2_kVAr": "Reactive Power L2 kVAr",
                "reactivePowerL3_kVAr": "Reactive Power L3 kVAr",
                "reactivePowerTotal_kVAr": "Reactive Power",

                # =============================================================
                # --- 5. PENAMBAHAN POWER FACTOR PER FASA & TOTAL ---
                # =============================================================
                "powerFactorL1": "Power Factor L1",
                "powerFactorL2": "Power Factor L2",
                "powerFactorL3": "Power Factor L3",
                "powerFactorTotal": "Power Factor",
                "generatorFreq": "Frequency",

                # =============================================================
                # --- 6. PENAMBAHAN AKUMULASI ENERGI & JAM KERJA ---
                # =============================================================
                "engineRunTimeHours": "Engine Run Time Hours",
                "energyActiveKWh": "Energy Active kWh",
                "energyReactiveKVArh": "Energy Reactive kVARh",
                "startCount": "Start Count"
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
            elif not formatted_key:
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