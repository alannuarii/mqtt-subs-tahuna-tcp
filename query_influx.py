from influxdb_client import InfluxDBClient
import config

client = InfluxDBClient(url=config.INFLUXDB_URL, token=config.INFLUXDB_TOKEN, org=config.INFLUXDB_ORG)
query_api = client.query_api()

query = f"""
import "influxdata/influxdb/schema"
schema.measurementFieldKeys(bucket: "{config.INFLUXDB_BUCKET}", measurement: "PM-DG6", start: -5m)
"""
result = query_api.query(query)
fields = []
for table in result:
    for record in table.records:
        fields.append(record.get_value())
print("Fields in PM-DG6:", fields)
