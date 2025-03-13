from kafka import KafkaConsumer

# Inisialisasi KafkaConsumer
consumer = KafkaConsumer(
    'my-first-topic',
    bootstrap_servers='192.168.43.213:9093',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-python-group',
    value_deserializer=lambda x: x.decode('utf-8')
)

print("Menunggu pesan...")

# Loop terus untuk membaca pesan
for message in consumer:
    print(f"Pesan diterima: {message.value}")
