import os
import scrapy
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime

class WebSpider(scrapy.Spider):
    name = 'web_spider'
    
    # Lista de URLs semilla para comenzar el crawling
    start_urls = [
        'https://en.wikipedia.org/wiki/Web_search_engine',
        'https://en.wikipedia.org/wiki/Database',
        'https://en.wikipedia.org/wiki/Distributed_computing',
        'https://www.python.org/',
        'https://nodejs.org/',
    ]
    
    # Límite de páginas a crawlear
    custom_settings = {
        'CLOSESPIDER_PAGECOUNT': 500,
        'DEPTH_LIMIT': 3,
    }
    
    def parse(self, response):
        # Extraer información de la página
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Extraer título
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ''
        
        # Extraer meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '').strip() if meta_desc else ''
        
        # Extraer keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        keywords = meta_keywords.get('content', '').strip() if meta_keywords else ''
        
        # Extraer contenido del body
        body = soup.find('body')
        if body:
            # Remover scripts y estilos
            for script in body(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()
            content = body.get_text(separator=' ', strip=True)
        else:
            content = ''
        
        # Generar document_id único
        document_id = hashlib.md5(response.url.encode()).hexdigest()
        
        # Crear item con la información extraída
        item = {
            'document_id': document_id,
            'url': response.url,
            'title': title_text,
            'description': description,
            'keywords': keywords,
            'content': content[:10000],  # Limitar contenido a 10000 caracteres
            'crawl_timestamp': datetime.utcnow().isoformat(),
            'source': response.url.split('/')[2] if len(response.url.split('/')) > 2 else 'unknown'
        }
        
        yield item
        
        # Seguir enlaces en la página
        for href in response.css('a::attr(href)').getall():
            yield response.follow(href, self.parse)
