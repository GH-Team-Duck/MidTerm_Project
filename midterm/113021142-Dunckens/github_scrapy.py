# -*- coding: utf-8 -*-
import scrapy

class GithubTrendingSpider(scrapy.Spider):
    
    name = 'github_trending'
    allowed_domains = ['github.com']
    start_urls = ['https://github.com/Duckens03']

    def parse(self, response):
        
        self.log(f"Scraping trending repositories from {response.url}")

        repositories = response.css('article.Box-row')

        if not repositories:
            self.log("No repositories found. GitHub page structure might have changed.")
            return

        self.log(f"Found {len(repositories)} repositories on the page.")

        for repo in repositories:
            repo_link_element = repo.css('h2 a::attr(href)')
            if not repo_link_element:
                self.log("Could not find repository link element. Skipping.")
                continue 

            relative_url = repo_link_element.get()
            absolute_url = response.urljoin(relative_url)
            repo_name = " ".join(repo.css('h2 a ::text').getall()).strip()
            
            
            description = repo.xpath('string(./p)').get('').strip()
            if not description:
                description = "No description provided." 

            
            language_element = repo.css('span[itemprop="programmingLanguage"]::text')
            language = language_element.get() if language_element else "N/A" 

            
            yield {
                'name': repo_name,
                'url': absolute_url,
                'description': description,
                'language': language.strip(), 
            }

        
