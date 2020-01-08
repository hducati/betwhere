# -*- coding: utf-8 -*-
import scrapy
from os import getcwd
from os.path import join
from time import gmtime, strftime

#file_name = 'match_' + strftime("%Y/%m/%d %H:%M:%S", gmtime()) + '.txt'
match_file = open(join(getcwd(), 'futmatchs.txt'), 'w')

class BetwhereSpider(scrapy.Spider):
    name = 'betwhere2'
    # allowed_domains = ['https://www.fctables.com/']
    start_urls = ['https://www.fctables.com/todays-match-predictions/']

    def parse(self, response):
        match_file.write("CUP            HOME       x       AWAY\n\n")
        for href in response.css("td.match-name a::attr(href)").extract():
            try:
                url = "https://www.fctables.com{}".format(href)
                print(url)
                yield scrapy.Request(url=url, callback=self.match_request)
            except TypeError:
                pass

    def match_request(self, response):
        value_support = 0

        home_team = response.css("div.gnbox.home a span::text").extract_first()
        away_team = response.css("div.gnbox.away a span::text").extract_first()
        cup_name = response.css("div.h2h_league_name a::text").extract_first()
        status = response.css("div.round-cd span::text").extract_first()

        match_file.write(cup_name + '  '  + home_team + '   X   '  + away_team + '(' + status + ')' + '\n\n')
        match_file.write('   Last 6 matches stats\n\n')
        
        last_stats = response.css("div.team_stats_forms ul li div::text").extract()
        stats_setup = response.css("div.team_stats_forms ul li p::text").extract()

        match_file.write('   '+ home_team + '(Home team)\n')

        for ls, ss in zip(last_stats, stats_setup):
            if value_support == 10:
                match_file.write('\n')
                match_file.write('   '+ away_team + '(Away team)\n')

            match_file.write('   -'+ ss + ': ' + ls + '\n')
            value_support += 1

        match_file.write('\n')