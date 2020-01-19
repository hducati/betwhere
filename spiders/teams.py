import scrapy
import itertools
import pandas as pd
from os import getcwd
from os.path import join


class ScoreBSpider(scrapy.Spider):
    name = 'ft_teams'

    def start_requests(self):
        start_urls = ['https://www.fctables.com/tables']

        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        if response.status == 200:
            for url in response.css('div.panel-body > ul.countries_list.tournaments_list > li > a::attr(href)').extract():
                yield scrapy.Request(url='https://www.fctables.com/' + url, callback=self.tournament_extract)
        else:
            scrapy.exceptions.CloseSpider('Connection failed. Closing spider...')

    def tournament_extract(self, response):
        if response.status == 200:
            self.logger.info('Extracting data from {}'.format(response.url))
            data_sid = response.css('div.col-xs-12 > div::attr(data-id)').extract_first()
            print(data_sid)
            template = response.css('div.col-xs-12 > div::attr(data-template)').extract_first()
            print(template)
            yield scrapy.Request(url=response.url + '?id={}&template={}&type={}&lang_id={}&short={}'.format(
              data_sid, template, 'corners', '2', ''), callback=self.corner_table)
        else:
            scrapy.exceptions.CloseSpider('Connection to {} failed. Closing spider...'.format(response.url))

    def corner_table(self, response):
        if response.status == 200:
            for stats in response.css('div.panel-body.pn > div.table-responsive > table > tbody > tr').extract():
                teste = response.css()
        else:
            scrapy.exceptions.CloseSpider('Connection to {} failed. Closing spider...'.format(response.url))
