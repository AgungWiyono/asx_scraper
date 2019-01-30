# -*- coding: utf-8 -*-
import scrapy


class TestingSpider(scrapy.Spider):
    name = 'testing'
    allowed_domains = ['https://www.asx.com.au/']
    start_urls = ['http://https://www.asx.com.au//']

    def parse(self, response):
        pass
