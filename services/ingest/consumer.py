import os
import json
import time
import re
from confluent_kafka import Consumer, KafkaError
import pymysql
import psycopg2
from pymongo import MongoClient

class IngestService:
    def __init__(self):
        # Kafka configuration
        self.consumer = Consumer({
            'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
            'group.id': 'ingest-consumer-group',
            'auto.offset.reset': 'earliest'
        })
        self.consumer.subscribe([os.getenv('KAFKA_TOPIC', 'pages.raw')])
        
        # Database connections
        self.init_databases()
        
    def init_databases(self):
        # MySQL connection
        max_retries = 10
        retry_count = 0
        while retry_count < max_retries:
            try:
                self.mysql_conn = pymysql.connect(
                    host=os.getenv('MYSQL_HOST', 'localhost'),
                    user=os.getenv('MYSQL_USER', 'searchuser'),
                    password=os.getenv('MYSQL_PASSWORD', 'searchpass'),
                    database=os.getenv('MYSQL_DATABASE', 'searchdb'),
                    charset='utf8mb4'
                )
                print("MySQL connected successfully")
                break
            except Exception as e:
                retry_count += 1
                print(f"MySQL connection attempt {retry_count}/{max_retries} failed: {e}")
                time.sleep(5)
        
        # PostgreSQL connection
        retry_count = 0
        while retry_count < max_retries:
            try:
                self.pg_conn = psycopg2.connect(
                    host=os.getenv('POSTGRES_HOST', 'localhost'),
                    user=os.getenv('POSTGRES_USER', 'searchuser'),
                    password=os.getenv('POSTGRES_PASSWORD', 'searchpass'),
                    database=os.getenv('POSTGRES_DATABASE', 'indexdb')
                )
                print("PostgreSQL connected successfully")
                break
            except Exception as e:
                retry_count += 1
                print(f"PostgreSQL connection attempt {retry_count}/{max_retries} failed: {e}")
                time.sleep(5)
        
        # MongoDB connection
        retry_count = 0
        while retry_count < max_retries:
            try:
                mongo_uri = os.getenv('MONGODB_URI', 'mongodb://root:rootpass@localhost:27017/')
                self.mongo_client = MongoClient(mongo_uri)
                self.mongo_db = self.mongo_client['contentdb']
                self.mongo_collection = self.mongo_db['documents']
                print("MongoDB connected successfully")
                break
            except Exception as e:
                retry_count += 1
                print(f"MongoDB connection attempt {retry_count}/{max_retries} failed: {e}")
                time.sleep(5)
        
        # Initialize schemas
        self.init_schemas()
    
    def init_schemas(self):
        # MySQL schema
        try:
            with self.mysql_conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS documents (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        document_id VARCHAR(255) UNIQUE NOT NULL,
                        url TEXT NOT NULL,
                        title TEXT,
                        description TEXT,
                        keywords TEXT,
                        crawl_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        source VARCHAR(255),
                        INDEX idx_document_id (document_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                self.mysql_conn.commit()
                print("MySQL schema initialized")
        except Exception as e:
            print(f"Error initializing MySQL schema: {e}")
        
        # PostgreSQL schema
        try:
            with self.pg_conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS inverted_index (
                        id SERIAL PRIMARY KEY,
                        token VARCHAR(255) NOT NULL,
                        document_id VARCHAR(255) NOT NULL,
                        frequency INT DEFAULT 1,
                        positions JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(token, document_id)
                    )
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_token ON inverted_index(token)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_document_id ON inverted_index(document_id)")
                self.pg_conn.commit()
                print("PostgreSQL schema initialized")
        except Exception as e:
            print(f"Error initializing PostgreSQL schema: {e}")
    
    def tokenize(self, text):
        """Simple tokenization: lowercase, remove punctuation, split by whitespace"""
        if not text:
            return []
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = [token for token in text.split() if len(token) > 2]
        return tokens
    
    def store_metadata(self, data):
        """Store metadata in MySQL"""
        try:
            with self.mysql_conn.cursor() as cursor:
                sql = """
                    INSERT INTO documents (document_id, url, title, description, keywords, source)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        url=VALUES(url), 
                        title=VALUES(title),
                        description=VALUES(description),
                        keywords=VALUES(keywords)
                """
                cursor.execute(sql, (
                    data['document_id'],
                    data['url'],
                    data.get('title', ''),
                    data.get('description', ''),
                    data.get('keywords', ''),
                    data.get('source', '')
                ))
                self.mysql_conn.commit()
            print(f"Stored metadata for {data['document_id']}")
        except Exception as e:
            print(f"Error storing metadata: {e}")
            self.mysql_conn.rollback()
    
    def store_content(self, data):
        """Store full content in MongoDB"""
        try:
            doc = {
                'document_id': data['document_id'],
                'url': data['url'],
                'content': data.get('content', ''),
                'title': data.get('title', ''),
                'crawl_timestamp': data.get('crawl_timestamp')
            }
            self.mongo_collection.update_one(
                {'document_id': data['document_id']},
                {'$set': doc},
                upsert=True
            )
            print(f"Stored content for {data['document_id']}")
        except Exception as e:
            print(f"Error storing content: {e}")
    
    def store_index(self, data):
        """Store inverted index in PostgreSQL"""
        try:
            # Tokenize title, description, and content
            all_text = f"{data.get('title', '')} {data.get('description', '')} {data.get('content', '')}"
            tokens = self.tokenize(all_text)
            
            # Count token frequencies
            token_freq = {}
            for token in tokens:
                token_freq[token] = token_freq.get(token, 0) + 1
            
            # Store in database
            with self.pg_conn.cursor() as cursor:
                for token, freq in token_freq.items():
                    cursor.execute("""
                        INSERT INTO inverted_index (token, document_id, frequency)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (token, document_id) 
                        DO UPDATE SET frequency = EXCLUDED.frequency
                    """, (token, data['document_id'], freq))
                self.pg_conn.commit()
            print(f"Stored index for {data['document_id']} ({len(token_freq)} unique tokens)")
        except Exception as e:
            print(f"Error storing index: {e}")
            self.pg_conn.rollback()
    
    def process_message(self, message):
        """Process a single message from Kafka"""
        try:
            data = json.loads(message.value().decode('utf-8'))
            print(f"Processing: {data['url']}")
            
            # Store in all three databases
            self.store_metadata(data)
            self.store_content(data)
            self.store_index(data)
            
            print(f"Successfully processed: {data['url']}")
        except Exception as e:
            print(f"Error processing message: {e}")
    
    def run(self):
        """Main consumer loop"""
        print("Ingest service started, waiting for messages...")
        try:
            while True:
                msg = self.consumer.poll(1.0)
                
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        print(f"Consumer error: {msg.error()}")
                        continue
                
                self.process_message(msg)
                
        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            self.consumer.close()
            self.mysql_conn.close()
            self.pg_conn.close()
            self.mongo_client.close()

if __name__ == '__main__':
    service = IngestService()
    service.run()
