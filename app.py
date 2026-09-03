import config
import json
import paho.mqtt.client as mqtt

# 🚀 IMPORT fungsi baru yang super cepat
from db import write_multiple_to_influxdb  

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Berhasil terhubung ke broker MQTT")
        client.subscribe(f"{config.MQTT_TOPIC}#")  
    else:
        print(f"Gagal terhubung dengan kode hasil: {rc}")

def on_message(client, userdata, msg):
    try:
        topic_parts = msg.topic.split("/")
        if len(topic_parts) >= 2:
            measurement = topic_parts[1]  
            
            try:
                payload_json = json.loads(msg.payload.decode('utf-8'))
            except json.JSONDecodeError:
                print(f"Bukan format JSON yang valid: {msg.payload.decode('utf-8')}")
                return

            old_engine_keys = ["oilPressure", "coolantTemp", "chargeAlt", "chargeAltVoltage", "batteryVoltage", "engineRpm"]

            key_mapping = {
                "currentL1": "Current L1", "currentL2": "Current L2", "currentL3": "Current L3",
                "voltageL1L2": "Voltage L1 L2", "voltageL2L3": "Voltage L2 L3", "voltageL3L1": "Voltage L3 L1",
                "activePower": "Active Power", "reactivePower": "Reactive Power", "powerFactor": "Power Factor",
                "frequency": "Frequency", "oilPressure": "Oil Pressure", "coolantTemp": "Coolant Temp",
                "chargeAltVoltage": "Charge Alt", "batteryVoltage": "Battery Voltage", "engineRpm": "Engine RPM",
                "timestamp": "Timestamp",
                "controlMode": "Control Mode", "globalAlarmStatus": "Global Alarm Status", "engineState": "Engine State",
                "voltageL1N": "Voltage L1 N", "voltageL2N": "Voltage L2 N", "voltageL3N": "Voltage L3 N",
                "currentN": "Current Neutral", "currentG": "Current Ground", "currentEarth": "Current Earth",
                "activePowerL1_kW": "Active Power L1 kW", "activePowerL2_kW": "Active Power L2 kW",
                "activePowerL3_kW": "Active Power L3 kW", "activePowerTotal_kW": "Active Power",
                "reactivePowerL1_kVAr": "Reactive Power L1 kVAr", "reactivePowerL2_kVAr": "Reactive Power L2 kVAr",
                "reactivePowerL3_kVAr": "Reactive Power L3 kVAr", "reactivePowerTotal_kVAr": "Reactive Power",
                "powerFactorL1": "Power Factor L1", "powerFactorL2": "Power Factor L2",
                "powerFactorL3": "Power Factor L3", "powerFactorTotal": "Power Factor",
                "generatorFreq": "Frequency",
                "engineRunTimeHours": "Engine Run Time Hours", "energyActiveKWh": "Energy Active kWh",
                "energyReactiveKVArh": "Energy Reactive kVARh", "startCount": "Start Count"
            }
            
            # 🚀 WADAH PENAMPUNG PARAMETER
            fields_to_write = {}
            
            for key, raw_value in payload_json.items():
                if key == "timestamp_local": continue 
                if key in old_engine_keys and measurement.lower() not in ["engine-dg6", "engine-dg7"]: continue  

                formatted_key = key_mapping.get(key, None)

                try:
                    value = float(raw_value)
                except (ValueError, TypeError):
                    value = None  

                if formatted_key and formatted_key != "Timestamp" and value is not None:
                    # MASUKKAN KE DALAM WADAH PENAMPUNG (Tanpa memanggil InfluxDB)
                    fields_to_write[formatted_key] = value
            
            # 🚀 TEMBAKKAN SEMUA DATA SEKALIGUS (1x HTTP Request)
            if fields_to_write:
                write_multiple_to_influxdb(measurement, fields_to_write)
                print(f"[{measurement}] Berhasil menyimpan {len(fields_to_write)} parameter sekaligus tanpa delay.")

        else:
            print(f"Format topik tidak dikenali: {msg.topic}")
    except Exception as e:
        print(f"Error memproses pesan: {e}")

client = mqtt.Client(client_id="", protocol=mqtt.MQTTv311, transport="tcp")
client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

print("Menghubungkan ke broker MQTT...")
client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
client.loop_forever()
