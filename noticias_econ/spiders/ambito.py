import scrapy


class AmbitoSpider(scrapy.Spider):
    name = "ambito"
    allowed_domains = ["ambito.com"]
    start_urls = ["https://www.ambito.com/economia"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_page = 0

    def parse(self, response):
        news_links = response.css("h2.news-article__title a::attr(href)").getall()
        self.logger.info(f"Página {self.current_page}: {len(news_links)} links encontrados")

        # Si no hay links, detener el scraper
        if not news_links:
            self.logger.info("No hay más noticias, finalizando scraper")
            return

        # Scrapear cada noticia encontrada
        for link in news_links:
            yield response.follow(link, callback=self.parse_noticia)

        # Continuar a la siguiente página automáticamente
        self.current_page += 1
        next_page_url = f"https://www.ambito.com/economia/{self.current_page}"
        self.logger.info(f"Avanzando a la página {self.current_page}")
        yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_noticia(self, response):
        titulo = response.css("h1.news-headline__title::text").get()
        fecha = response.css("span.news-headline__publication-date::text").get()

        # Extraer todo el cuerpo del artículo como texto continuo
        cuerpo = response.xpath(
            "string(//article[contains(@class,'article-body')])"
        ).get()

        # Limpiar espacios múltiples y saltos de línea
        if cuerpo:
            cuerpo = " ".join(cuerpo.split())

        # Solo retornar si tiene contenido válido
        if titulo and cuerpo:
            yield {
                "url": response.url,
                "titulo": titulo.strip() if titulo else None,
                "fecha": " ".join(fecha.split()) if fecha else None,
                "cuerpo": cuerpo,
            }