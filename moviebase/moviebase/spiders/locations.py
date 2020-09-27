import scrapy

# XPATH
# movies link: '//h3[@class="lister-item-header"]/a/@href'
# Title: //h1
# Locations link: //*[@id="titleDetails"]/div[6]/span/a
# Rating: //span[@itemprop="ratingValue"]/text()'
# Locations: //div[@class="soda sodavote odd" or @class="soda sodavote even"]/dt/a/text()'

class FilmLocation(scrapy.Spider):
    name = 'locations'
    start_urls = [
        'https://www.imdb.com/'
    ]
    custom_settings = {
        'FEED_URI':'locations.json',
        'FEED_FORMAT':'json',
        'FEED_EXPORT_ENCODING':'utf-8',
        'USER_AGENT': 'Mozilla/5.0' 
    }

    def parse(self, response):
        query = getattr(self, 'query', None)
        query = str(query)
        if query:
            query_urls = 'https://www.imdb.com/search/title/?countries='+ query

            yield response.follow(query_urls, callback=self.parse_query)

    def parse_query(self, response):
        movies_links = response.xpath('//h3[@class="lister-item-header"]/a/@href').getall()
        for link in movies_links:
            yield response.follow(link, callback=self.parse_link)

    def parse_link(self, response):
        title  = response.xpath('//h1/text()').get()
        rating = response.xpath('//span[@itemprop="ratingValue"]/text()').get()
                        
        #Corregir xpath de location links
        location_links = response.xpath('//*[@id="titleDetails"]/div[5]/span/a/@href').get()
        if location_links:
            yield response.follow('locations', callback=self.parse_locations, cb_kwargs={'title':title, 'rating':rating})
        
        else:
            yield {
            'title': title,
            'rating': rating,
            'locations': 'Not available'   
        }


    def parse_locations(self, response, **kwargs):
        if kwargs:
            title = kwargs['title']
            rating = kwargs['rating']
        locations = response.xpath('//div[@class="soda sodavote odd" or @class="soda sodavote even"]/dt/a/text()').getall()

        yield { 
            'title': title,
            'rating': rating,
            'locations': locations
            }

