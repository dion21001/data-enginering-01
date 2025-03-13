from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from kafka import KafkaProducer, KafkaConsumer
import json
import pymysql

# Konfigurasi MySQL
MYSQL_CONN_STR = "mysql+pymysql://root:Pramuka123@mysql:3306/tugas_akhir"

# Konfigurasi Kafka
KAFKA_TOPIC = 'my_topic'
KAFKA_SERVER = 'kafka:9092'

# Default args DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

# Fungsi untuk ambil data dari MySQL
def extract_data_from_mysql(ti, **kwargs):
    engine = create_engine(MYSQL_CONN_STR)
    query = "SELECT * FROM sumber_data;"  # Pastikan tabel ini ada
    with engine.connect() as conn:
        result = conn.execute(query)
        data = [dict(row._mapping) for row in result]  # Convert ke dict
    ti.xcom_push(key='extracted_data', value=data)  # Simpan XCom
    print("Data extracted:", data)

# Fungsi untuk kirim data ke Kafka
def send_data_to_kafka(ti, **kwargs):
    data = ti.xcom_pull(key='extracted_data', task_ids='extract_from_mysql')
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_SERVER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    for row in data:
        print(f"Sending row: {row}")
        producer.send(KAFKA_TOPIC, row)
    producer.flush()
    print(f"Data sent to Kafka topic {KAFKA_TOPIC}")

# Fungsi konsumsi dari Kafka ke MySQL
def consume_kafka_and_store_to_mysql(**kwargs):
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        group_id='airflow-group',
        enable_auto_commit=True
    )
    connection = pymysql.connect(
        host='mysql',
        user='root',
        password='Pramuka123@',
        database='tugas_akhir'
    )
    cursor = connection.cursor()
    for message in consumer:
        data = message.value
        print(f"Received data: {data}")
        try:
            insert_query = """
                INSERT INTO hasil_data (id, name, value)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE name=VALUES(name), value=VALUES(value);
            """
            cursor.execute(insert_query, (data['id'], data['name'], data['value']))
            connection.commit()
        except Exception as e:
            print("Error inserting data:", e)
    consumer.close()
    cursor.close()
    connection.close()

# Definisi DAG
with DAG(
    'mysql_to_kafka_to_mysql',
    default_args=default_args,
    description='ETL sederhana dari MySQL ke Kafka ke MySQL lagi',
    schedule_interval='@daily',  # Bisa diganti misal '*/5 * * * *' untuk 5 menit sekali
    start_date=datetime(2023, 1, 1),
    catchup=False
) as dag:

    extract = PythonOperator(
        task_id='extract_from_mysql',
        python_callable=extract_data_from_mysql,
        provide_context=True
    )

    send_kafka = PythonOperator(
        task_id='send_to_kafka',
        python_callable=send_data_to_kafka,
        provide_context=True
    )

    consume_kafka = PythonOperator(
        task_id='consume_and_store',
        python_callable=consume_kafka_and_store_to_mysql
    )

    # Urutan task
    extract >> send_kafka >> consume_kafka
