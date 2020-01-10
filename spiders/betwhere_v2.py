# -*- coding: utf-8 -*-
import scrapy
from os import getcwd
from os.path import join
from time import gmtime, strftime
from datetime import datetime, timedelta
from pandas import DataFrame, ExcelWriter

today_date = datetime.today().strftime('%d-%m-%Y')
tomorrow = datetime.now() + timedelta(days=1)
tomorrow_formatted = tomorrow.strftime('%d-%m-%Y')

file_name = 'matches/txt/matchs_{}_{}.txt'.format(today_date, tomorrow_formatted) 

match_file = open(join(getcwd(), file_name), 'w')

URL_EXTRACT = ['https://www.fctables.com/todays-match-predictions/' + tomorrow_formatted]
last_index = 1
overall_index = 1
all_games = 1

df = DataFrame(columns=('Data jogo', 'Jogo', 'Times', 'Partidas', 'Gols', 'Por jogo', 'Vitórias', 'Empates', 'Derrotas', 'Over 2.5', 'Over 1.5', 'CS', 'BTTS'))
df_overall = DataFrame(columns=('Data jogo', 'Jogo', 'Times','Partidas', 'Gols', 'Por jogo', 'Vitórias', 'Empates', 'Derrotas', 'Over 2.5', 'Over 1.5', 'CS', 'BTTS'))


class BetwhereSpider(scrapy.Spider):
    today_date = datetime.today().strftime('%d-%m-%Y')
    
    name = 'betwhere2'
    # allowed_domains = ['https://www.fctables.com/']
    start_urls = [
        'https://www.fctables.com/todays-match-predictions/' + today_date]

    def parse(self, response):
        global URL_EXTRACT
    
        if response.status == 200:
            for href in response.css("td.match-name a::attr(href)").extract():
                try:
                    url = "https://www.fctables.com{}".format(href)

                    yield scrapy.Request(url=url, callback=self.match_request)
                except TypeError:
                    pass
        else:
            raise scrapy.exceptions.CloseSpider('Connection failed.')
        
        for url in URL_EXTRACT:
            yield scrapy.Request(url=url, callback=self.parse)

    def match_request(self, response):
        global today_date
        global tomorrow_formatted
        global df
        global df_overall
        global index
        global all_games

        self.logger.info('Extracting data from {}'.format(response.url))

        referrer = response.request.headers.get('Referer', None)
        referrer_formatted = referrer.decode().split('/')

        if len(referrer_formatted) == 5:
            request_date = datetime.today().strftime('%d-%m-%Y')
                        
        elif len(referrer_formatted) == 6:
            request_date = referrer_formatted[-2]

        match_file.write(str(request_date))

        home_team = response.css("div.gnbox.home a span::text").extract_first()
        away_team = response.css("div.gnbox.away a span::text").extract_first()
        cup_name = response.css("div.h2h_league_name a::text").extract_first()
        status = response.css("div.round-cd span::text").extract_first()
        
        last_stats = response.css("div.team_stats_forms ul li div::text").extract()

        overall_stats = response.css("div.team_stats_item ul li div::text").extract()

        self.write_txt_file(home_team, away_team, cup_name, status, last_stats, overall_stats)
        self.write_excel_file(request_date, home_team, away_team, last_stats, overall_stats)

    def write_txt_file(self, home_team, away_team, cup_name, status, last_stats, overall_stats):
        
        stats_overview = [
            'Partidas', 'Gols', 'Por jogo', 'Vitórias', 'Empates', 'Derrotas', 'Over 2.5', 'Over 1.5', 'CS', 'BTTS',
            'Partidas', 'Gols', 'Por jogo', 'Vitórias', 'Empates', 'Derrotas', 'Over 2.5', 'Over 1.5', 'CS', 'BTTS'
        ]

        match_file.write(' | ' + cup_name + ' | '  + home_team + '   X   '  + away_team + '(' + status + ')' + '\n\n')
        
        match_file.write('        '+ home_team + '(Time de casa)\n')

        match_file.write('\n   Últimos 6 jogos     Todos os jogos\n\n')
        value_support = 0

        for ls, ss in zip(last_stats, stats_overview):
            if value_support == 10:
                match_file.write('\n')
                match_file.write('        '+ away_team + '(Time de fora)\n')
                match_file.write('\n   Últimos 6 jogos     Todos os jogos\n\n')

            match_file.write('   -{:9}: {:6} -{:9}: {:6}\n'.format(ss, ls, ss, overall_stats[value_support]))
        
            value_support += 1

        match_file.write('\n')

    def write_excel_file(self, match_date, home_team, away_team, last_stats, overall_stats):
        global last_index
        global overall_index
        global df
        global df_overall
        global all_games

        stats_overview = [
            'Data jogo', 'Jogo', 'Times', 'Partidas', 'Gols', 'Por jogo', 'Vitórias', 'Empates', 'Derrotas', 'Over 2.5', 'Over 1.5', 'CS', 'BTTS',
            'Data jogo', 'Jogo', 'Times', 'Partidas', 'Gols', 'Por jogo', 'Vitórias', 'Empates', 'Derrotas', 'Over 2.5', 'Over 1.5', 'CS', 'BTTS'
        ]

        overall_stats_overview = [
            'Data jogo', 'Jogo', 'Times', 'Partidas', 'Gols', 'Por jogo', 'Vitórias', 'Empates', 'Derrotas', 'Over 2.5', 'Over 1.5', 'CS', 'BTTS',
            'Data jogo', 'Jogo', 'Times', 'Partidas', 'Gols', 'Por jogo', 'Vitórias', 'Empates', 'Derrotas', 'Over 2.5', 'Over 1.5', 'CS', 'BTTS'
        ]

        value_support = 0

        last_stats.insert(0, home_team)
        last_stats.insert(11, away_team)

        last_stats.insert(0, 'Jogo ' + str(all_games))
        last_stats.insert(12, 'Jogo ' + str(all_games))

        last_stats.insert(0, str(match_date))
        last_stats.insert(13, '')

        overall_stats.insert(0, home_team)
        overall_stats.insert(11, away_team)

        overall_stats.insert(0, 'Jogo ' + str(all_games))
        overall_stats.insert(12, 'Jogo ' + str(all_games))

        overall_stats.insert(0, str(match_date))
        overall_stats.insert(13, '')

        for ls, ss in zip(last_stats, stats_overview):

            if value_support == 13:
                last_index += 1
        
            df.set_value(index=last_index, col=ss, value=ls)
            value_support += 1

        value_support = 0
      
        for overall, overview in zip(overall_stats, overall_stats_overview):
            if value_support == 13:
                overall_index += 1

            df_overall.set_value(index=overall_index, col=overview, value=overall)
            value_support += 1

        last_index += 1
        overall_index += 1
        all_games += 1

    def closed(self, reason):
        global df
        global df_overall 

        path = 'matches/csv/matchs_{}_{}.xlsx'.format(today_date, tomorrow_formatted) 
        excel_path = join(getcwd(), path)

        writer = ExcelWriter(excel_path)
        
        self.logger.info('Started writing in excel file...')

        # df.sort_values('Data jogo', ascending=True,  inplace=True)

        # df_overall.sort_values('Data jogo', ascending=True, inplace=True)

        df.to_excel(writer, "Últimos 6 jogos", index=True, header=True)
        df_overall.to_excel(writer, "Todos os jogos", index=True, header=True)

        writer.save()

        self.logger.info('Done!!')