-- MySQL schema for metadata storage

CREATE DATABASE IF NOT EXISTS searchdb;
USE searchdb;

CREATE TABLE IF NOT EXISTS documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id VARCHAR(255) UNIQUE NOT NULL,
    url TEXT NOT NULL,
    title TEXT,
    description TEXT,
    keywords TEXT,
    crawl_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(255),
    INDEX idx_document_id (document_id),
    INDEX idx_crawl_timestamp (crawl_timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
