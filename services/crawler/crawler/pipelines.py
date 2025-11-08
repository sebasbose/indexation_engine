import os
import json
from confluent_kafka import Producer

class KafkaPipeline:
    def __init__(self):
        self.producer = None
        self.kafka_topic = os.getenv('KAFKA_TOPIC', 'pages.raw')
        
    def open_spider(self, spider):
        kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        conf = {
            'bootstrap.servers': kafka_servers,
            'client.id': 'scrapy-crawler'
        }
        self.producer = Producer(conf)
        spider.logger.info(f"Kafka producer initialized: {kafka_servers}")
        
    def close_spider(self, spider):
        if self.producer:
            self.producer.flush()
            spider.logger.info("Kafka producer flushed and closed")
            
    def process_item(self, item, spider):
        if self.producer:
            try:
                # Convertir item a JSON
                message = json.dumps(dict(item))
                
                # Enviar a Kafka
                self.producer.produce(
                    self.kafka_topic,
                    value=message.encode('utf-8'),
                    key=item['document_id'].encode('utf-8')
                )
                
                self.producer.poll(0)
                spider.logger.info(f"Sent to Kafka: {item['url']}")
                
            except Exception as e:
                spider.logger.error(f"Error sending to Kafka: {e}")
                
        return item
