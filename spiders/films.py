import scrapy

class FilmSpider(scrapy.Spider):
    name = "films"

    def start_requests(self):
        URL = "https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту"
        yield scrapy.Request(url=URL, callback=self.parse)

    def parse(self, response):
        for film_link in response.css('div.mw-category-group > ul > li > a::attr(href)').getall():
            url = response.urljoin(film_link)
            yield scrapy.Request(url, callback=self.parse_film)

        next_page = response.css('a[title="Категория:Фильмы по алфавиту"]:contains("Следующая страница")::attr(href)').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_film(self, response):
        # Жанр
        genre_selectors = [
            'td.plainlist span[data-wikidata-property-id="P136"] a::text',
            'span.wikidata-snak.wikidata-main-snak a::text',
            'a[href*="/wiki/"]:contains("фильм")::text'
        ]
        genre = self.extract_with_selectors(response, genre_selectors)

        # Режиссёр
        director_selectors = [
            'td.plainlist span[data-wikidata-property-id="P57"] a::text',
            'span.wikidata-snak a::text',
            'a[href*="/w/index.php?title="]::text'
        ]
        director = self.extract_with_selectors(response, director_selectors)

        # Страна
        country_selectors = [
            'a[title="Россия"] span::text',
            'a[href*="/wiki/"]:contains("Россия")::text',
            'span.country-name a::text',
            'td.plainlist span[data-wikidata-property-id="P495"] span.wrap::text',
            'td.plainlist span[data-wikidata-property-id="P495"]::text',
            'th:contains("Страна") + td a:last-of-type::text'
        ]
        country = self.extract_with_selectors(response, country_selectors)

        # Год
        year_selectors = [
            'a[title$="в кино"] span::text',
            'a[href*="/wiki/"]:contains("год")::text'
        ]
        year = self.extract_with_selectors(response, year_selectors)

        # Извлечение информации
        film_info = {
            'title': response.css('.infobox-above::text').extract_first(),
            'genre': genre,
            'director': director,
            'country': country,
            'year': year
        }
        yield film_info

    def extract_with_selectors(self, response, selectors):
        for selector in selectors:
            results = response.css(selector).extract()
            if results:

                return ', '.join(result.strip() for result in results if result.strip())
        return None



