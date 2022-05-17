import scrapy
from general_use.items import LeetCodeItem
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
import re

from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError

class SpiderLeetCode(scrapy.Spider):
    name = 'spider_leetcode'

    def get_url(self, page):
        return f"https://leetcode.com/problemset/all/?page={page}"
    
    def start_requests(self):
        
        page_start = 1
        """
        index_process = getattr(self, 'index_process', None)

        if index_process:
            category = categories[int(index_process)]
            url = f"https://www2.javhdporn.net/category/{category}/page/1"
            yield scrapy.Request(
                url=url, 
                callback=self.parse_page,
                errback=self.errback
                )
        else:
            print("ERROR: no index_process -a")
        """
        yield scrapy.Request(url=self.get_url(page_start), callback=self.parse_page,errback=self.errback)

    def parse_page(self, response):
        

        category = response.xpath('//strong[contains(@class,"bread-current")]/text()').get()
        
        cards = response.xpath('//article[contains(@class,"thumb-block")]')
        
        for card in cards:
            url = card.xpath('./a/@href').get()
            views = 0
            query_views = card.xpath('.//span[@class="views"]/text()').get()
            if query_views:
                views = int(query_views.strip())
            duration = [0,0,0]
            query_duration = card.xpath('.//span[@class="duration"]/text()').get()
            if query_duration:
                duration = list(map(int,query_duration.strip().split(":")))
            time_minutes = duration[0] * 60 + duration[1]
            
            item_loader = ItemLoader(item=JavHDItem(), selector=card)
            item_loader.default_output_processor = TakeFirst()  # no save array
             
            item_loader.add_value('category', category)
            item_loader.add_value('url', url)
            item_loader.add_value('views', views)
            item_loader.add_value('time_minutes', time_minutes)
           
            item = item_loader.load_item()
            # go to video page and pass the current collected info
            yield response.follow(url, self.parse_video, meta={'item': item})
            
        next_page = response.xpath('//li[./a/text() = "Next"]/a/@href').get()
        if next_page:
            # if not "page/2" in next_page:
            yield response.follow(next_page, callback=self.parse_page)
        
        
        
        
    def parse_video(self, response):
        
        item = response.meta['item']
        item_loader = ItemLoader(item=item, response=response)
        item_loader.default_output_processor = TakeFirst()  # no save array
        
        score = response.xpath('.//strong[@class="kksr-score"]/text()').get()
        if score:
            score = float(score)
        else:
            score = 0
        
        votes = response.xpath('.//strong[@class="kksr-count"]/text()').get()
        if score:
            votes = int(votes)
        else:
            votes = 0
        
        response.xpath('.//div[@id="video-date"]/text()').get().split("Time")[0].strip()
                
        date_raw = response.xpath('.//div[@id="video-date"]').get()
        
        date_year = 0
        date_month = 0
        date_day = 0
        
        m = re.match(r'^[<>A-z"\/\s\-=;:#\d]*Date: (.*, \d{4})[<>A-z"\/\s\-=;:#\d]*$', date_raw)
        if m:
            date = m.groups()[0].strip().split(" ")
            date_year = int(date[2])
            
            dict_date = {
                "january": "01",
                "february": "02",
                "march": "03",
                "april": "04",
                "may": "05",
                "june": "06",
                "july": "07",
                "august": "08",
                "september": "09",
                "october": "10",
                "november": "11",
                "december": "12",
            }
            date_month = int(dict_date[date[0].lower()])
            date_day = int(date[1][:-1])
            
        
        participants = response.xpath('.//div[@id="video-actors"]')
        index_p = 0
        actors = "unknown"
        studio = "unknown"
        
                 
        
        if len(participants) > 1:
            
            actors = participants[index_p].xpath(".//a/@href").getall()
            if actors:
                actors = "|".join(list(map(lambda s: s.split("pornstar/")[1][:-1], filter(lambda s: "pornstar" in s, actors))))
            else:
                actors = "unknown"
            index_p += 1
        if len(participants) > 0:
            studio = participants[index_p].xpath(".//a/@href").getall()
            if studio:
                studio = "|".join(list(map(lambda s: s.split("studio/")[1][:-1], filter(lambda s: "studio" in s, studio))))
            else:
                studio = "unknown"
            index_p += 1
            
            
        tags = response.xpath('.//div[@class="tags-list"]//a/@href').getall()
        if tags:
            tags = "|".join(list(map(lambda s: s.split("tag/")[1][:-1], filter(lambda s: "tag" in s, tags))))
        else:
            tags = "unknown"
        
        data = {
            "title": response.xpath(".//header/h1/text()").get(),
            "img": response.xpath('.//div[@id="video-player"]/img/@src').get(),
            "score": score, # no always is
            "votes": votes, # no always is
            "date_year": date_year,
            "date_month": date_month,
            "date_day": date_day,
            "actors": actors,
            "studio": studio,
            "tags": tags
        }
        
        for key, value in data.items():
            item_loader.add_value(key, value)
        
        yield item_loader.load_item()
        
        
    
    def errback(self, failure):
        # log all errback failures,
        # in case you want to do something special for some errors,
        # you may need the failure's type
        self.logger.error(repr(failure))

        request = failure.request
            
        #if isinstance(failure.value, HttpError):
        if failure.check(HttpError):
            # you can get the response
            response = failure.value.response
            self.logger.error('APPERROR HttpError on %s', response.url)

        #elif isinstance(failure.value, DNSLookupError):
        elif failure.check(DNSLookupError):
            # this is the original request
            self.logger.error('APPERROR DNSLookupError on %s', request.url)

        #elif isinstance(failure.value, TimeoutError):
        elif failure.check(TimeoutError):
            self.logger.error('APPERROR TimeoutError on %s', request.url)
        else:
            self.logger.error('APPERROR OTHER %s', failure)
        