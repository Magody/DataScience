from ScrapperPlusvalia import ScrapperPlusvalia
import sys

args = sys.argv

if len(args) <= 1:
    sys.exit()

page_from = int(args[1])
page_to = int(args[2])
waiting_time = 1
batch = 500

while page_from <= page_to:
    
    batch_begin = page_from
    batch_end = min(batch_begin + batch - 1, page_to)

    scrapper = ScrapperPlusvalia()
    urls, _ = scrapper.collect_urls(batch_begin,batch_end,waiting_time=waiting_time)
    scrapper.close()
    print(f"SOLVED UNTIL PAGE {batch_end}")
    page_from = batch_end + 1