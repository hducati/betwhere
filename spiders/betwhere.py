# -*- coding: utf-8 -*-
import scrapy
from os import getcwd
from os.path import join
from time import gmtime, strftime

#file_name = 'match_' + strftime("%Y/%m/%d %H:%M:%S", gmtime()) + '.txt'
match_file = open(join(getcwd(), 'futmatchs.txt'), 'w')

class BetwhereSpider(scrapy.Spider):
    name = 'betwhere'
    # allowed_domains = ['https://www.fctables.com/']
    start_urls = ['https://www.fctables.com//']

    def parse(self, response):
        match_file.write("HOME TEAM      X       AWAY TEAM\n")
        for href in response.css("div.lm-container ul li a::attr(href)").extract():
            yield scrapy.FormRequest(url=response.url + href, callback=self.match_request)
            print(href)

    def match_request(self, response):
        all_matches = []

        for match_id in response.css("div.livescore_body div.game::attr(id)").extract():
            all_matches.append(match_id)

        for match in all_matches:
            css_path = "#{} div.name meta::attr(content)".format(match)
            content = response.css(css_path).extract_first()

            print(content)
            