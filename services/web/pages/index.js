import { useState, useEffect } from 'react';
import Head from 'next/head';
import styles from '../styles/Home.module.css';

export default function Home() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);
  const [searchInfo, setSearchInfo] = useState(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

  useEffect(() => {
    // Load stats on mount
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_URL}/api/stats`);
      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/api/search?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      
      setResults(data.results || []);
      setSearchInfo({
        total: data.total,
        query: data.query,
        tokens: data.tokens
      });
    } catch (err) {
      setError('Error al realizar la búsqueda. Por favor, intenta de nuevo.');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <Head>
        <title>Motor de Búsqueda Distribuido</title>
        <meta name="description" content="Sistema de búsqueda distribuido" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        <h1 className={styles.title}>
          Motor de Búsqueda Distribuido
        </h1>

        {stats && (
          <div className={styles.stats}>
            <span>{stats.documents} documentos indexados</span>
            <span>{stats.tokens} tokens únicos</span>
          </div>
        )}

        <form onSubmit={handleSearch} className={styles.searchForm}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Buscar..."
            className={styles.searchInput}
          />
          <button type="submit" className={styles.searchButton} disabled={loading}>
            {loading ? 'Buscando...' : 'Buscar'}
          </button>
        </form>

        {error && (
          <div className={styles.error}>
            {error}
          </div>
        )}

        {searchInfo && (
          <div className={styles.searchInfo}>
            Encontrados {searchInfo.total} resultados para "{searchInfo.query}"
            {searchInfo.tokens && searchInfo.tokens.length > 0 && (
              <span> (tokens: {searchInfo.tokens.join(', ')})</span>
            )}
          </div>
        )}

        <div className={styles.results}>
          {results.map((result, index) => (
            <div key={result.document_id || index} className={styles.resultItem}>
              <a href={result.url} target="_blank" rel="noopener noreferrer" className={styles.resultTitle}>
                {result.title || 'Sin título'}
              </a>
              <p className={styles.resultUrl}>{result.url}</p>
              <p className={styles.resultDescription}>
                {result.description || result.snippet || 'Sin descripción disponible'}
              </p>
              <div className={styles.resultMeta}>
                <span>Score: {result.score}</span>
                <span>Fuente: {result.source}</span>
                {result.crawl_timestamp && (
                  <span>Crawled: {new Date(result.crawl_timestamp).toLocaleDateString()}</span>
                )}
              </div>
            </div>
          ))}
        </div>

        {results.length === 0 && !loading && searchInfo && (
          <div className={styles.noResults}>
            No se encontraron resultados para tu búsqueda.
          </div>
        )}
      </main>

      <footer className={styles.footer}>
        <p>Sistema de Búsqueda Distribuido - Base de Datos Avanzadas</p>
      </footer>
    </div>
  );
}
