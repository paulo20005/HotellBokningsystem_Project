from kafka import KafkaConsumer
import json
import pandas as pd

consumer = KafkaConsumer(
    'bokningar',
    bootstrap_servers='127.0.0.1:9092',
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)
# Lista för att lagra bokningar
bokningar = []

print("Väntar på bokningar från Kafka...")
for message in consumer:
    data = message.value
    bokningar.append(data)
    print(f"Mottagen: Bokning {data['boknings_id']} - Rum {data['rum_id']}")

    # ETL med Pandas
    df = pd.DataFrame(bokningar)
    
    print(f"\nAntal bokningar: {len(df)}")
    print(f"Bokningar per rum:\n{df.groupby('rum_id').size()}")
    
    # Spara resultat
    df.to_csv('bokningsstatistik.csv', index=False)
    print("Sparad i bokningsstatistik.csv")
    print("-" * 40)