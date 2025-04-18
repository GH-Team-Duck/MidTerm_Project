# -*- coding: utf-8 -*-
"""GitHub_Scraper.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1PtR92ItjQFXo9Av0hFBiJzehkAOQ23kp
"""

pip install scrapy

# Commented out IPython magic to ensure Python compatibility.
!scrapy startproject github_scraper
# %cd github_scraper

# Commented out IPython magic to ensure Python compatibility.
# %%writefile github_scraper/spiders/github_spider.py
# import scrapy
# from datetime import datetime
# 
# class GitHubSpider(scrapy.Spider):
#     name = 'github'
#     start_urls = ['https://github.com/YOUR_USERNAME?tab=repositories']  # Replace with your GitHub username
# 
#     def parse(self, response):
#         for repo in response.css('li.source'):
#             repo_url = response.urljoin(repo.css('a::attr(href)').get())
#             yield scrapy.Request(repo_url, callback=self.parse_repo)
# 
#         next_page = response.css('a.next_page::attr(href)').get()
#         if next_page:
#             yield response.follow(next_page, self.parse)
# 
#     def parse_repo(self, response):
#         item = {
#             'url': response.url,
#             'about': self.get_about(response),
#             'last_updated': self.get_last_updated(response),
#             'languages': self.get_languages(response),
#             'commits': self.get_commits(response)
#         }
#         yield item
# 
#     def get_about(self, response):
#         about = response.css('div.Layout-sidebar p.f4.mb-3::text').get()
#         if not about or about.strip() == '':
#             if not self.is_repo_empty(response):
#                 about = response.css('strong.mr-2.flex-self-stretch a::text').get().strip()
#             else:
#                 about = None
#         return about
# 
#     def is_repo_empty(self, response):
#         return bool(response.css('div.Box.Box--condensed h3::text').re(r'This repository is empty.'))
# 
#     def get_last_updated(self, response):
#         updated_str = response.css('relative-time::attr(datetime)').get()
#         if updated_str:
#             return datetime.fromisoformat(updated_str).strftime('%Y-%m-%d %H:%M:%S')
#         return None
# 
#     def get_languages(self, response):
#         if self.is_repo_empty(response):
#             return None
#         languages = response.css('span.color-fg-default.text-bold.mr-1::text').getall()
#         return [lang.strip() for lang in languages] if languages else None
# 
#     def get_commits(self, response):
#         if self.is_repo_empty(response):
#             return None
#         commits_link = response.css('a.Link--primary.no-underline::attr(href)').re_first(r'.*/commits')
#         if commits_link:
#             return response.urljoin(commits_link)
#         return None

# Commented out IPython magic to ensure Python compatibility.
# %%writefile github_scraper/pipelines.py
# from itemadapter import ItemAdapter
# from scrapy.exporters import XmlItemExporter
# 
# class XmlExportPipeline:
#     def __init__(self):
#         self.file = None
#         self.exporter = None
# 
#     def open_spider(self, spider):
#         self.file = open('github_repos.xml', 'wb')
#         self.exporter = XmlItemExporter(self.file, item_element='repository', root_element='repositories')
#         self.exporter.start_exporting()
# 
#     def close_spider(self, spider):
#         self.exporter.finish_exporting()
#         self.file.close()
# 
#     def process_item(self, item, spider):
#         self.exporter.export_item(item)
#         return item

# Commented out IPython magic to ensure Python compatibility.
# %%writefile github_scraper/settings.py
# BOT_NAME = 'github_scraper'
# SPIDER_MODULES = ['github_scraper.spiders']
# NEWSPIDER_MODULE = 'github_scraper.spiders'
# ROBOTSTXT_OBEY = True
# ITEM_PIPELINES = {
#     'github_scraper.pipelines.XmlExportPipeline': 300,
# }

!scrapy crawl github -o output.xml

from google.colab import files
files.download('github_repos.xml')

scrapy crawl github -a user=GH-Team-Duck