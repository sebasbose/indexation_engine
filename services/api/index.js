const express = require('express');
const cors = require('cors');
const mysql = require('mysql2/promise');
const { Client: PgClient } = require('pg');
const { MongoClient } = require('mongodb');

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Database connections
let mysqlPool;
let pgClient;
let mongoDb;

// Initialize database connections
async function initDatabases() {
  // MySQL
  mysqlPool = mysql.createPool({
    host: process.env.MYSQL_HOST || 'localhost',
    user: process.env.MYSQL_USER || 'searchuser',
    password: process.env.MYSQL_PASSWORD || 'searchpass',
    database: process.env.MYSQL_DATABASE || 'searchdb',
    waitForConnections: true,
    connectionLimit: 10
  });
  
  // PostgreSQL
  pgClient = new PgClient({
    host: process.env.POSTGRES_HOST || 'localhost',
    user: process.env.POSTGRES_USER || 'searchuser',
    password: process.env.POSTGRES_PASSWORD || 'searchpass',
    database: process.env.POSTGRES_DATABASE || 'indexdb'
  });
  
  await pgClient.connect();
  
  // MongoDB
  const mongoUri = process.env.MONGODB_URI || 'mongodb://root:rootpass@localhost:27017/';
  const mongoClient = new MongoClient(mongoUri);
  await mongoClient.connect();
  mongoDb = mongoClient.db('contentdb');
  
  console.log('All databases connected');
}

// Search endpoint
app.get('/api/search', async (req, res) => {
  const query = req.query.q || '';
  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 10;
  const offset = (page - 1) * limit;
  
  if (!query) {
    return res.json({ results: [], total: 0, page, limit });
  }
  
  try {
    console.log(`Searching for: ${query}`);
    
    // Tokenize query (simple lowercase split)
    const tokens = query.toLowerCase().split(/\s+/).filter(t => t.length > 2);
    
    if (tokens.length === 0) {
      return res.json({ results: [], total: 0, page, limit });
    }
    
    // Step 1: Query PostgreSQL index to find matching documents
    const indexQuery = `
      SELECT document_id, SUM(frequency) as score
      FROM inverted_index
      WHERE token = ANY($1)
      GROUP BY document_id
      ORDER BY score DESC
      LIMIT $2 OFFSET $3
    `;
    
    const indexResult = await pgClient.query(indexQuery, [tokens, limit, offset]);
    const documentIds = indexResult.rows.map(row => row.document_id);
    
    if (documentIds.length === 0) {
      return res.json({ results: [], total: 0, page, limit });
    }
    
    // Step 2: Get metadata from MySQL
    const metadataQuery = `
      SELECT document_id, url, title, description, keywords, crawl_timestamp, source
      FROM documents
      WHERE document_id IN (?)
    `;
    
    const [metadataRows] = await mysqlPool.query(metadataQuery, [documentIds]);
    
    // Step 3: Get content snippets from MongoDB
    const contentDocs = await mongoDb.collection('documents')
      .find({ document_id: { $in: documentIds } })
      .project({ document_id: 1, content: 1 })
      .toArray();
    
    // Create a map for quick lookup
    const metadataMap = {};
    metadataRows.forEach(row => {
      metadataMap[row.document_id] = row;
    });
    
    const contentMap = {};
    contentDocs.forEach(doc => {
      contentMap[doc.document_id] = doc.content;
    });
    
    // Step 4: Combine results
    const results = indexResult.rows.map(row => {
      const metadata = metadataMap[row.document_id] || {};
      const content = contentMap[row.document_id] || '';
      
      // Generate snippet (first 200 chars)
      const snippet = content.substring(0, 200) + (content.length > 200 ? '...' : '');
      
      return {
        document_id: row.document_id,
        url: metadata.url || '',
        title: metadata.title || 'Untitled',
        description: metadata.description || snippet,
        snippet: snippet,
        score: row.score,
        source: metadata.source || '',
        crawl_timestamp: metadata.crawl_timestamp
      };
    });
    
    // Get total count
    const countQuery = `
      SELECT COUNT(DISTINCT document_id) as total
      FROM inverted_index
      WHERE token = ANY($1)
    `;
    const countResult = await pgClient.query(countQuery, [tokens]);
    const total = parseInt(countResult.rows[0].total);
    
    res.json({
      results,
      total,
      page,
      limit,
      query,
      tokens
    });
    
  } catch (error) {
    console.error('Search error:', error);
    res.status(500).json({ 
      error: 'Search failed', 
      message: error.message,
      results: [],
      partial: true
    });
  }
});

// Stats endpoint
app.get('/api/stats', async (req, res) => {
  try {
    // Get document count from MySQL
    const [mysqlResult] = await mysqlPool.query('SELECT COUNT(*) as count FROM documents');
    const documentCount = mysqlResult[0].count;
    
    // Get token count from PostgreSQL
    const pgResult = await pgClient.query('SELECT COUNT(DISTINCT token) as count FROM inverted_index');
    const tokenCount = pgResult.rows[0].count;
    
    // Get MongoDB stats
    const mongoStats = await mongoDb.collection('documents').countDocuments();
    
    res.json({
      documents: documentCount,
      tokens: tokenCount,
      content_docs: mongoStats
    });
  } catch (error) {
    console.error('Stats error:', error);
    res.status(500).json({ error: 'Failed to get stats' });
  }
});

// Health check
app.get('/api/health', async (req, res) => {
  const health = {
    status: 'ok',
    databases: {}
  };
  
  try {
    await mysqlPool.query('SELECT 1');
    health.databases.mysql = 'connected';
  } catch (e) {
    health.databases.mysql = 'disconnected';
    health.status = 'degraded';
  }
  
  try {
    await pgClient.query('SELECT 1');
    health.databases.postgres = 'connected';
  } catch (e) {
    health.databases.postgres = 'disconnected';
    health.status = 'degraded';
  }
  
  try {
    await mongoDb.command({ ping: 1 });
    health.databases.mongodb = 'connected';
  } catch (e) {
    health.databases.mongodb = 'disconnected';
    health.status = 'degraded';
  }
  
  res.json(health);
});

// Initialize and start server
async function start() {
  try {
    await initDatabases();
    app.listen(PORT, () => {
      console.log(`API server running on port ${PORT}`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
}

start();
