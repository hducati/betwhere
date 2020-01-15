import scrapy


class ScoreBSpider(scrapy.Spider):
    name = 'scoreb'

    def start_requests(self):
        start_urls = ['https://www.scorebing.com/']

        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
        league_url = response.css('div.panel-body ul.panelList2Item1.MBBlock li a::attr(href)').extract()

        self.logger.info('Preparing to extract data from {}...'.format(league_url))

        for url in league_url:
            url = response.url + url

            yield scrapy.Request(url=url, callback=self.game_league_extract)

    def game_league_extract(self, response):
        if response.status == 200:
            league = response.css('tbody > tr.page-1 > td.bg1 > a::text').extract()
            date = response.css('tbody > tr.page-1 > td:nth-child(2)::text').extract()

            home_team = response.css('tbody > tr.page-1 > td.text-right.BR0 > a::text').extract()
            away_team = response.css('tbody > tr.pagae-1 > td.text-left a::href').extract()

            handicap_home = response.css('tbody > tr.page-1 > td:nth-child(7)::text').extract()
            handicap =  response.css('tbody > tr.page-1 > td:nth-child(8)::text').extract()
            handicap_away = response.css('tbody > tr.page-1 > td:nth-child(9)::text').extract()

            goals_home = response.css('tbody > tr.page-1 > td:nth-child(10)::text')
            goals = response.css('tbody > tr.page-1 > td:nth-child(11) > a::text').extract()
            goals_away = response.css('tbody > tr.paage-1 > td:nth-child(12)::text').extract()

            corners_home = response.css('tbody > tr.page-1 > td:nth-child(13)::text')
            corners = response.css('tbody > tr.page-1 > td:nth-child(14) > a::text').extract()
            corners_away = response.css('tbody > tr.page-1 > td:nth-child(15)::text').extract()

            game_url = response.css('tbody > tr.page-1 > td.text-right.BR0 > a::attr(href)').extract()

            for url in game_url:
                url = 'https://scorebing.com' + url
                yield scrapy.Request(url=url, callback=self.team_extract)

            match_dict = {
                'League': league, 'Date': date, 'Home team': home_team, 'Away team': away_team, 'Handicap home': handicap_home, 'Handicap': handicap,
                'Handicap away': handicap_away, 'Goals home': goals_home, 'Goals': goals, 'Goals away': goals_away, 'Corners home': corners_home, 
                'Corners': corners, 'Corners away': corners_away}
        else:
            raise scrapy.exceptions.CloseSpider('Connection to {} failed'.format(response.url))

    def team_extract(self, response):
        all_first_corners = []

        if response.status == 200:
            for i in response.css('tbody > tr > td.bg1 > a::text').extract():
                first_corner = response.css('#race_timeLine span.timeLineCorner::attr(title)').extract()[0]
                self.logger.info(first_corner)
                all_first_corners.append(first_corner)

            return all_first_corners  
        else:
            raise scrapy.exceptions.CloseSpider('Connection to {} failed'.format(response.url))