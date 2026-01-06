import scrapy


class AmbitoSpider(scrapy.Spider):
    name = "ambito"
    allowed_domains = ["ambito.com"]
    start_urls = ["https://www.ambito.com/economia"]

    # 👉 Precauciones “humanas” y tolerantes (punto 2)
    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_TIMEOUT": 60,
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 8,
        "RETRY_HTTP_CODES": [500, 502, 503, 504, 408],
        "DOWNLOAD_DELAY": 2,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    }

    # 👉 Permite que 504 y similares lleguen a parse()
    handle_httpstatus_list = [504, 502, 503, 429, 403]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_page = 0

    def parse(self, response):
        # Si la página del paginado falla, NO cortamos la cadena
        if response.status != 200:
            self.logger.warning(
                f"Página {self.current_page} devolvió status {response.status}. "
                f"Salteando y avanzando."
            )
        else:
            news_links = response.css(
                "h2.news-article__title a::attr(href)"
            ).getall()

            self.logger.info(
                f"Página {self.current_page}: {len(news_links)} links encontrados"
            )

            if not news_links:
                self.logger.info(
                    "No hay más noticias, finalizando scraper"
                )
                return

            for link in news_links:
                yield response.follow(link, callback=self.parse_noticia)

        # Avanzar SIEMPRE al siguiente número de página
        self.current_page += 1
        next_page_url = f"https://www.ambito.com/economia/{self.current_page}"
        self.logger.info(f"Avanzando a la página {self.current_page}")
        yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_noticia(self, response):
        titulo = response.css(
            "h1.news-headline__title::text"
        ).get()
        fecha = response.css(
            "span.news-headline__publication-date::text"
        ).get()

        cuerpo = response.xpath(
            "string(//article[contains(@class,'article-body')])"
        ).get()

        if cuerpo:
            cuerpo = " ".join(cuerpo.split())

        if titulo and cuerpo:
            yield {
                "url": response.url,
                "titulo": titulo.strip(),
                "fecha": " ".join(fecha.split()) if fecha else None,
                "cuerpo": cuerpo,
            }
