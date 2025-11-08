-- PostgreSQL schema for inverted index

CREATE TABLE IF NOT EXISTS inverted_index (
    id SERIAL PRIMARY KEY,
    token VARCHAR(255) NOT NULL,
    document_id VARCHAR(255) NOT NULL,
    frequency INT DEFAULT 1,
    positions JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(token, document_id)
);

CREATE INDEX idx_token ON inverted_index(token);
CREATE INDEX idx_document_id ON inverted_index(document_id);
CREATE INDEX idx_token_freq ON inverted_index(token, frequency DESC);
