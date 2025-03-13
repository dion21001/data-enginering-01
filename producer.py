from kafka import KafkaProducer

# Inisialisasi KafkaProducer
producer = KafkaProducer(
    bootstrap_servers='192.168.43.213:9093',  # Sesuaikan dengan Kafka di docker-compose kamu
    value_serializer=lambda v: str(v).encode('utf-8')  # Biar otomatis jadi byte string
)

# Kirim pesan ke topic
producer.send('my-first-topic', value="Halo Kafka dari Python!")
producer.send('my-first-topic', value="Pesan kedua dari Python!")
producer.send('my-first-topic',value='jangan tinggalin abang dek')
producer.send('my-first-topic',value='aku sayang kamu dek')

# Wajib flush supaya dikirim
producer.flush()
print("Pesan berhasil dikirim!")

# Tutup koneksi (opsional)
producer.close()
