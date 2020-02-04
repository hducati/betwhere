import scrapy
from os import getcwd
from os.path import join
from time import gmtime, strftime
from datetime import datetime, timedelta
from pandas import DataFrame, ExcelWriter, to_numeric, concat, read_excel
import itertools

df_global = DataFrame()

today_date = datetime.today().strftime('%d-%m-%Y')
fullpath = join(getcwd(), 'matches/csv/nba_matches_{}.xlsx'.format(today_date))

writer = ExcelWriter(fullpath)

class ScoreBSpider(scrapy.Spider):
    name = 'nba'

    def start_requests(self):
        today_date = datetime.today().strftime('%Y%m%d')
        start_urls = ['https://www.espn.com/nba/schedule/_/date/' + today_date]

        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if response.status == 200:
            games_url = response.css('#sched-container > div:nth-child(3) > table > tbody > tr > td:nth-child(1) > a::attr(href)').extract()
            at_games_url = response.css('#sched-container > div:nth-child(3) > table > tbody > tr > td.home > div > a::attr(href)').extract()

            for game in itertools.chain(games_url, at_games_url):
                team = game.split('/')[-2]

                url = 'https://www.espn.com/nba/team/stats/_/name/' + team

                yield scrapy.Request(url=url, callback=self.team_stats)
        else:
            scrapy.exceptions.CloseSpider('Connection failed. Closing spider...')

    def team_stats(self, response):
        if response.status == 200:
            player_extract = response.css('#fittPageContainer > div.StickyContainer > div.page-container.cf > div.layout.is-9-3 > div > section > div > section:nth-child(5) > div.flex > table > tbody > tr > td > span > a::attr(href)').extract()

            for player in player_extract:
                name = player.split('/')[-1]
                player_id = player.split('/')[-2]

                url = 'https://www.espn.com/nba/player/gamelog/_/id/{}/{}'.format(player_id, name)

                yield scrapy.Request(url=url, callback=self.player_stats)
        else:
            scrapy.exceptions.CloseSpider('Connection failed. Closing spider...')

    def player_stats(self, response):
        global df_global

        player_list = []
        player_main_list = []
        team_list = []
        name_player = []
        date_format = []

        if response.status == 200:
            date = response.css('#fittPageContainer > div.StickyContainer > div:nth-child(5) > div > div > div:nth-child(1) > div > div:nth-child(2) > div:nth-child(n+2):nth-child(-n+3) > div > section > div > div > div.Table__Scroller > table > tbody > tr > td:nth-child(1)::text').extract()
            last_team = response.css('#fittPageContainer > div.StickyContainer > div:nth-child(5) > div > div > div:nth-child(1) > div > div:nth-child(2) > div:nth-child(n+2):nth-child(-n+3) > div > section > div > div > div.Table__Scroller > table > tbody > tr > td:nth-child(2) > span > span > a::text').extract()
            status = response.css('#fittPageContainer > div.StickyContainer > div:nth-child(5) > div > div > div:nth-child(1) > div > div:nth-child(2) > div:nth-child(n+2):nth-child(-n+3) > div > section > div > div > div.Table__Scroller > table > tbody > tr > td:nth-child(3) > a > span > span.pr2 > div::text').extract()
            team = response.css('#fittPageContainer > div.StickyContainer > div:nth-child(1) > div > div > div.PlayerHeader__Left.flex.items-center.justify-start.overflow-hidden.brdr-clr-gray-09 > div.PlayerHeader__Main.flex.items-center > div.PlayerHeader__Main_Aside.min-w-0.flex-grow.flex-basis-0 > div > ul > li.truncate.min-w-0 > a::text').extract_first()
            stats = response.css('#fittPageContainer > div.StickyContainer > div:nth-child(5) > div > div > div:nth-child(1) > div > div:nth-child(2) > div:nth-child(n+2):nth-child(-n+3) > div > section > div > div > div.Table__Scroller > table > tbody > tr > td:nth-child(n+4):nth-child(-n+17)::text').extract()
            player = response.css('#fittPageContainer > div.StickyContainer > div:nth-child(1) > div > div > div.PlayerHeader__Left.flex.items-center.justify-start.overflow-hidden.brdr-clr-gray-09 > div.PlayerHeader__Main.flex.items-center > div.PlayerHeader__Main_Aside.min-w-0.flex-grow.flex-basis-0 > h1 > span.truncate.min-w-0.fw-light::text').extract_first()

            for i in range(0, len(last_team)):
                team_list.append(team)
                name_player.append(player)

            week_list = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

            for d in date:
                if d[0:3] not in week_list:
                    pass
                else:
                    date_format.append(d)
                    

            df = DataFrame({
                'Date': date_format,
                'Team': team_list,
                'Against': last_team,
                'Status': status,
                'Player': name_player
            })

            cont = 0
            for s in stats:
                player_list.append(s)
                cont += 1

                if cont == 14:
                    player_main_list.append(player_list)
                    player_list = []
                    cont = 0          

            df_stats = DataFrame(player_main_list, columns=(
                'MIN', 'FG', 'FG%', '3P', '3P%', 'FT', 'FT%', 'REB', 'AST', 'BLK', 'STL', 'PF', 'TO', 'PTS'))

            frames = [df, df_stats]

            result = concat(frames, axis=1)

            if result.empty:
                pass
            else:
                df_global = df_global.append(result, ignore_index=True)
        else:
            scrapy.exceptions.CloseSpider('Connection failed. Closing spider...')

    def closed(self, reason):
        global writer
        global df_global

        self.logger.info('Saving excel file...')

        df_global['PTS'] = to_numeric(df_global['PTS'], errors='coerce')
        df_global.sort_values(by=['PTS'], inplace=True, ascending=False)
        df_global.to_excel(writer, 'NBA - Player stats', index=True, header=True)
        writer.save()

        self.logger.info('Done!!')