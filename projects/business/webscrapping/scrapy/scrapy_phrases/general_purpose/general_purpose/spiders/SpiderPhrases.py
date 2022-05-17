import scrapy
import pandas as pd
import re
 
class SpiderPhrases(scrapy.Spider):
   name = "spider_phrases_01"
   urls = ['https://psicologiaymente.com/reflexiones/frases-filosoficas']
  
   def start_requests(self):
       for url in self.urls:
           yield scrapy.Request(url=url)
 
   def parse(self, response):
      
        df = pd.DataFrame(columns=["Author", "Cite"])
        pattern = r"\d*\.?\s+([A-z\”\“\"\'\sáéíóú;\-\_,\.ñ:!¿¡?]+)\((.+)\)"
        authors = []
        cites = []
        for quote in response.xpath('//div[contains(@class,"prose")]//h3/text()').extract():
           
           m = re.match(pattern, quote)
           
           if m:
               g = m.groups()
               authors.append(g[1].strip())
               cites.append(g[0].strip())
           else:
               authors.append("Unknown")
               cites.append(quote)
               print("NOT MATCH", quote)
               
        df = df.from_dict(data={
            "Author": authors,
            "Cite": cites
        })   
      
        df.to_csv(f"out/{self.name}.csv", index=False)
