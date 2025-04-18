import scrapy
import json
from urllib.parse import urljoin

class GithubRepoItem(scrapy.Item):
    URL = scrapy.Field()
    About = scrapy.Field()
    Last_Updated = scrapy.Field()
    Languages = scrapy.Field()
    Stars = scrapy.Field()  # Added basic public metrics
    Forks = scrapy.Field()

class GithubSpider(scrapy.Spider):
    name = 'github'
    allowed_domains = ['github.com']
    
    # Scrape public user pages instead of API
    start_urls = ['https://github.com/Mikel0101lab?tab=repositories']  # Replace with your username
    
    custom_settings = {
        'FEEDS': {
            'repositories.xml': {
                'format': 'xml',
                'encoding': 'utf8',
                'indent': 4,
                'overwrite': True,
            },
        },
        'DOWNLOAD_DELAY': 2,  # Be polite to GitHub's servers
        'USER_AGENT': 'Mozilla/5.0'  # Avoid looking like a bot
    }

    def parse(self, response):
        # Extract basic repo info from HTML
        for repo in response.css('li.source'):
            item = GithubRepoItem()
            item['URL'] = urljoin(response.url, repo.css('a::attr(href)').get())
            item['About'] = repo.css('p::text').get('').strip()
            
            # Get metadata from the right sidebar
            metadata = repo.css('.mr-3')
            item['Stars'] = metadata.xpath('.//a[contains(@href, "stargazers")]/text()').get('0').strip()
            item['Forks'] = metadata.xpath('.//a[contains(@href, "network")]/text()').get('0').strip()
            
            # Last updated is in relative-time tag
            item['Last_Updated'] = repo.css('relative-time::attr(datetime)').get()
            
            # Languages require visiting the repo page
            yield response.follow(
                item['URL'],
                callback=self.parse_languages,
                meta={'item': item}
            )

    def parse_languages(self, response):
        item = response.meta['item']
        # Languages appear at the top of the code tab
        item['Languages'] = ', '.join(
            response.css('.language-color[aria-label]::attr(aria-label)').getall()
        ) or 'None'
        
        yield item