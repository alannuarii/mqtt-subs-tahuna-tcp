import config
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Konfigurasi InfluxDB
influxdb_url = config.INFLUXDB_URL
influxdb_token = config.INFLUXDB_TOKEN
influxdb_org = config.INFLUXDB_ORG
influxdb_bucket = config.INFLUXDB_BUCKET

# Inisialisasi klien InfluxDB
client_influxdb = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)
write_api = client_influxdb.write_api(write_options=SYNCHRONOUS)
query_api = client_influxdb.query_api()

# Fungsi LAMA (dipertahankan untuk berjaga-jaga jika masih ada skrip lain yang memakainya)
def write_to_influxdb(measurement, key, value):
    point = Point(measurement).field(key, value)
    write_api.write(bucket=influxdb_bucket, org=influxdb_org, record=point)

# 🚀 FUNGSI BARU (SUPER CEPAT): Menulis puluhan parameter dalam 1 tembakan (1 Point)
def write_multiple_to_influxdb(measurement, fields_dict):
    if not fields_dict:
        return
    
    point = Point(measurement)
    
    # Masukkan semua field ke dalam 1 gerbong (1 stempel waktu InfluxDB)
    for key, value in fields_dict.items():
        point.field(key, value)

    # Tembakkan ke database (Hanya 1x HTTP Request untuk puluhan parameter)
    write_api.write(bucket=influxdb_bucket, org=influxdb_org, record=point)

# Fungsi untuk mengambil data dari InfluxDB
def get_data_from_influxdb(query):
    tables = query_api.query(query)
    results = []
    
    for table in tables:
        for record in table.records:
            results.append((record.get_time(), record.get_value()))
    
    return results
