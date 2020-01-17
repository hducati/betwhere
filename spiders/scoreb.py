import scrapy
import itertools
import pandas as pd
from os import getcwd
from os.path import join


all_matches_stats = []
all_first_corners = []
corner_team_formatted = []


class ScoreBSpider(scrapy.Spider):
    name = 'scoreb'

    def start_requests(self):
        start_urls = ['https://www.scorebing.com']

        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'proxy': 'https://72.169.67.101:87'})
    
    def parse(self, response):
        print(response.url)
        league_url = response.css('div.panel-body > ul.panelList2Item1.MBBlock > li > a::attr(href)').extract()
        print(response.status)

        for url in league_url:
            url = response.url + url
            self.logger.info('Preparing to extract data from {}...'.format(url))
            yield scrapy.Request(url=url, callback=self.game_league_extract, meta={'proxy': 'https://72.169.67.101:87'})

    def game_league_extract(self, response):
        global all_matches_stats

        print(response.url)
        home_formatted = []

        if response.status == 200:
            league = response.css('tbody > tr.page-1 > td.bg1 > a::text').extract()
            date = response.css('tbody > tr.page-1 > td:nth-child(2)::text').extract()

            home_team = response.css('tbody > tr.page-1 > td.text-right.BR0 > a::text').extract()

            if len(home_team) == 0:
                home_formatted = []
            else:
                for home in home_team:
                    home_format = home.strip()
                    home_formatted.append(home_format)

            away_team = response.css('tbody > tr.page-1 > td.text-left a::text').extract()

            handicap_home = response.css('tbody > tr.page-1 > td:nth-child(7)::text').extract()
            handicap =  response.css('tbody > tr.page-1 > td:nth-child(8) a::text').extract()
            handicap_away = response.css('tbody > tr.page-1 > td:nth-child(9)::text').extract()

            goals_home = response.css('tbody > tr.page-1 > td:nth-child(10)::text').extract()
            goals = response.css('tbody > tr.page-1 > td:nth-child(11) > a::text').extract()
            goals_away = response.css('tbody > tr.page-1 > td:nth-child(12)::text').extract()

            corners_home = response.css('tbody > tr.page-1 > td:nth-child(13)::text').extract()
            corners = response.css('tbody > tr.page-1 > td:nth-child(14) > a::text').extract()
            corners_away = response.css('tbody > tr.page-1 > td:nth-child(15)::text').extract()

            game_home_url = response.css('tbody > tr.page-1 > td.text-right.BR0 > a::attr(href)').extract()
            game_away_url = response.css('tbody > tr.page-1 > td.text-left > a::attr(href)').extract()

            match_dict = {
                'League': league, 'Date': date, 'Home team': home_formatted, 'Away team': away_team, 'Handicap home': handicap_home, 'Handicap': handicap,
                'Handicap away': handicap_away, 'Goals home': goals_home, 'Goals': goals, 'Goals away': goals_away, 'Corners home': corners_home, 
                'Corners': corners, 'Corners away': corners_away}
            all_matches_stats.append(match_dict)

            for url in itertools.chain(game_home_url, game_away_url):
                url = 'https://scorebing.com' + url
                yield scrapy.Request(url=url, callback=self.team_extract, meta={'proxy': 'https://72.169.67.101:87'})
        else:
            raise scrapy.exceptions.CloseSpider('Connection to {} failed'.format(response.url))

    def team_extract(self, response):
        global all_first_corners
        global corner_team_formatted

        if response.status == 200:
            corner_home_team = response.css('#ended > table > tbody > tr > td.text-right.BR0 > a::text').extract()
            corner_away_team = response.css('#ended > table > tbody > tr > td.text-left > a::text').extract()

            for c_home, c_away in zip(corner_home_team, corner_away_team):
                c_home_format = c_home.strip()
                corner_team_formatted.append(c_home_format + ' X ' + c_away)

            for i in response.css('#race_timeLine > span:nth-child(22)::attr(title)').extract():   
                all_first_corners.append(i)
            
            corner_team_formatted.append('\n')
            all_first_corners.append('\n')

        else:
            raise scrapy.exceptions.CloseSpider('Connection to {} failed'.format(response.url))

    def closed(self, reason):
        global all_matches_stats
        global all_first_corners
        global corner_team_formatted

        df_games = pd.DataFrame()
    
        sup_index = 1
        index = 1

        for i in all_matches_stats:
            sup_index = index
            for key, value in i.items():
                if key == 'League' and sup_index == 1:
                    index = 1
                else:
                    index = sup_index
                for x in value:
                    df_games.set_value(index=index, col=key, value=x)
                    index += 1
        
        df_first_corners = pd.DataFrame({
            'Teams': corner_team_formatted,
            'Corners': all_first_corners})

        fullpath = join(getcwd(), 'matches/csv/upcoming_matches.xlsx')

        writer = pd.ExcelWriter(fullpath)
        
        df_games.to_excel(writer, 'Upcoming matches', index=True, header=True)
        df_first_corners.to_excel(writer, '1st corner', index=True, header=True)

        writer.save()