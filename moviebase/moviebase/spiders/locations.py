import scrapy

# XPATH
# movies link: '//h3[@class="lister-item-header"]/a/@href'
# Title: //h1
# Year: //span[@id="titleYear"]/a/text()
# Locations link: //*[@id="titleDetails"]/div[6]/span/a
# Rating: //span[@itemprop="ratingValue"]/text()'
# Locations: //div[@class="soda sodavote odd" or @class="soda sodavote even"]/dt/a/text()' 
# Locations Option 2: //*[text()[contains(.,"Filming Locations")]]/../span/a/@href')
# Gross worlwide: '//*[text()[contains(.,"Worldwide")]]/..'   (cant separate text)
# Genres : '//div[@class="title_wrapper"]/div[@class="subtext"]/a[position()<3]/text()'

class FilmLocation(scrapy.Spider):
    name = 'locations'
    start_urls = [
        'https://www.imdb.com/'
    ]
    custom_settings = {
        'FEED_URI':'locations.csv',
        'FEED_FORMAT':'csv',
        'FEED_EXPORT_ENCODING':'utf-8',
        'USER_AGENT': 'Mozilla/5.0' 
    }

    def parse(self, response):
        query = getattr(self, 'query', None)
        query = str(query)
        if query:
            query_urls = 'https://www.imdb.com/search/title/?countries='+ query + '&count=100'

            yield response.follow(query_urls, callback=self.parse_query)

    def parse_query(self, response):
        movies_links = response.xpath('//h3[@class="lister-item-header"]/a/@href').getall()
        for link in movies_links:
            yield response.follow(link, callback=self.parse_link)

    def parse_link(self, response):
        title  = response.xpath('//h1/text()').get()
        rating = response.xpath('//span[@itemprop="ratingValue"]/text()').get()
        year = response.xpath('//span[@id="titleYear"]/a/text()').get()
        genres = response.xpath('//div[@class="title_wrapper"]/div[@class="subtext"]/a[position()<3]/text()').getall()
        #Corregir xpath de location links
        location_links = response.xpath('//*[text()[contains(.,"Filming Locations")]]/../span/a/@href').get()
        if location_links:
            yield response.follow('locations', callback=self.parse_locations, cb_kwargs={'title':title, 'rating':rating, 'year':year, 'genres':genres})
        
        else:
            yield {
            'title': title,
            'year': year,
            'rating': rating,
            'genres': genres,
            'locations': 'Not available'   
        }


    def parse_locations(self, response, **kwargs):
        if kwargs:
            title = kwargs['title']
            rating = kwargs['rating']
            year = kwargs['year']
            genres = kwargs['genres']
        locations = response.xpath('//div[@class="soda sodavote odd" or @class="soda sodavote even"]/dt/a/text()').getall()

        yield { 
            'title': title,
            'year': year,
            'rating': rating,
            'genres': genres,
            'locations': locations
            }

