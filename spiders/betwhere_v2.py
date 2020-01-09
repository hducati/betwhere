# -*- coding: utf-8 -*-
import scrapy
from os import getcwd
from os.path import join
from time import gmtime, strftime
from datetime import datetime, timedelta

today_date = datetime.today().strftime('%d-%m-%Y')
tomorrow = datetime.now() + timedelta(days=1)
tomorrow_formatted = tomorrow.strftime('%d-%m-%Y')

file_name = 'matches/txt/matchs_{}_{}.txt'.format(today_date, tomorrow_formatted) 
file_name_csv = 'matches/csv/matchs_{}_{}.csv'.format(today_date, tomorrow_formatted)

match_file = open(join(getcwd(), file_name), 'w')
match_file_csv = open(join(getcwd(), file_name_csv), 'w')

stats_overview = [
    'Partidas', 'Gols', 'Por jogo', 'Vitórias', 'Empates', 'Derrotas', 'Over 2.5', 'Over 1.5', 'CS', 'BTTS',
    'Partidas', 'Gols', 'Por jogo', 'Vitórias', 'Empates', 'Derrotas', 'Over 2.5', 'Over 1.5', 'CS', 'BTTS'
]

class BetwhereSpider(scrapy.Spider):
    today_date = datetime.today().strftime('%d-%m-%Y')
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_formatted = tomorrow.strftime('%d-%m-%Y')

    name = 'betwhere2'
    # allowed_domains = ['https://www.fctables.com/']
    start_urls = [
        'https://www.fctables.com/todays-match-predictions/' + today_date,
        'https://www.fctables.com/todays-match-predictions/' + tomorrow_formatted
    ]

    def parse(self, response):
        if response.status == 200:
            for href in response.css("td.match-name a::attr(href)").extract():
                try:
                    url = "https://www.fctables.com{}".format(href)

                    yield scrapy.Request(url=url, callback=self.match_request)
                except TypeError:
                    pass
        else:
            raise scrapy.exceptions.CloseSpider('Connection failed.')


    def match_request(self, response):
        global stats_overview

        self.logger.info('Extracting data from {}'.format(response.url))
        referrer = response.request.headers.get('Referer', None)
    
        referrer_formatted = referrer.decode().split('/')

        if len(referrer_formatted) == 5:
            request_date = datetime.today().strftime('%d-%m-%Y')
                        
        elif len(referrer_formatted) == 6:
            request_date = referrer_formatted[-2]

        match_file.write(str(request_date))
        match_file_csv.write(str(request_date))
        
        value_support = 0

        home_team = response.css("div.gnbox.home a span::text").extract_first()
        away_team = response.css("div.gnbox.away a span::text").extract_first()
        cup_name = response.css("div.h2h_league_name a::text").extract_first()
        status = response.css("div.round-cd span::text").extract_first()

        match_file.write(' | ' + cup_name + ' | '  + home_team + '   X   '  + away_team + '(' + status + ')' + '\n\n')
        match_file_csv.write(' | ' + cup_name + ' | '  + home_team + '   X   '  + away_team + '(' + status + ')' + '\n\n')
        
        last_stats = response.css("div.team_stats_forms ul li div::text").extract()
        # stats_setup = response.css("div.team_stats_forms ul li p::text").extract()

        overall_stats = response.css("div.team_stats_item ul li div::text").extract()
        # overall_stats_setup = response.css("div.team_stats_item ul li p::text").extract()

        match_file.write('        '+ home_team + '(Time de casa)\n')
        match_file_csv.write('        '+ home_team + '(Time de casa)\n')

        match_file.write('\n   Últimos 6 jogos     Todos os jogos\n\n')
        match_file_csv.write('\n   Últimos 6 jogos     Todos os jogos\n\n')

        for ls, ss in zip(last_stats, stats_overview):
            if value_support == 10:
                match_file.write('\n')
                match_file.write('        '+ away_team + '(Time de fora)\n')
                match_file.write('\n   Últimos 6 jogos     Todos os jogos\n\n')

                match_file_csv.write('\n')
                match_file_csv.write('        '+ away_team + '(Time de fora)\n')
                match_file_csv.write('\n   Últimos 6 jogos     Todos os jogos\n\n')

            match_file.write('   -{:9}: {:6} -{:9}: {:6}\n'.format(ss, ls, ss, overall_stats[value_support]))
            match_file_csv.write('   -{:9}: {:6} -{:9}: {:6}\n'.format(ss, ls, ss, overall_stats[value_support]))
        
            value_support += 1

        match_file.write('\n')
        match_file_csv.write('\n')
