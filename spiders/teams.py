import scrapy
import itertools
import pandas as pd
from os import getcwd
from os.path import join


fullpath = join(getcwd(), 'matches/csv/analyze_corner.xlsx')

writer = pd.ExcelWriter(fullpath)
value = 1

class ScoreBSpider(scrapy.Spider):
    name = 'ft_teams'

    def start_requests(self):
        start_urls = ['https://www.fctables.com']

        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        if response.status == 200:
            for url in response.css('div.alphabet > ul > li > ul > li.popular > span::attr(data-href)').extract():
                yield scrapy.Request(url='https://www.fctables.com' + url, callback=self.tournament_extract)
        else:
            scrapy.exceptions.CloseSpider('Connection failed. Closing spider...')

    def tournament_extract(self, response):
        if response.status == 200:
            self.logger.info('Extracting data from {}'.format(response.url))
            data_sid = response.css('div.col-xs-12 > div::attr(data-id)').extract_first()
            template = response.css('div.col-xs-12 > div::attr(data-template)').extract_first()

            yield scrapy.Request(url='https://www.fctables.com/xml/table_type/' + '?id={}&template={}&type={}&lang_id={}&short={}'.format(
              data_sid, template, 'corners', '2', ''), callback=self.corner_table)
        else:
            scrapy.exceptions.CloseSpider('Connection to {} failed. Closing spider...'.format(response.url))

    def corner_table(self, response):
        global value
        global writer

        stats = []
        stats_format = []
     
        if response.status == 200:
            position = response.css('tbody > tr > td:nth-child(1)::text').extract()
            teams = response.css('tbody > tr > td:nth-child(2) > a::text').extract()
            stats = response.css('tbody > tr > td:nth-child(n+3):nth-child(-n+18)::text').extract()
            
            n = 1
            stats_temp = []

            for i in stats:
                stats_temp.append(i)
                n +=1

                if n == 16:
                    stats_format.append(stats_temp)
                    stats_temp = []
                    n = 1

            df = pd.DataFrame(columns=(
                'Position', 'Team', 'FT', 'HT', '37-45', '80-90',
                'Team FT', 'Team HT', 'Team 37-45', 'Team 80-90', 'Team R3', 'Team R5', 'Team R7', 'Team R9',
                'Opponent FT', 'Opponent HT', 'Opponent 37-45', 'Opponent 80-90'))

            df.to_excel(writer, value, index=True, header=True)
            value += 1

        else:
            scrapy.exceptions.CloseSpider('Connection to {} failed. Closing spider...'.format(response.url))

    def closed(self, reason):
        global writer
        self.logger.info('Saving excel file...')
        writer.save()
        self.logger.info('Done!!')