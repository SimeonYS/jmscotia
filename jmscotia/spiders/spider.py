import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import JmscotiaItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class JmscotiaSpider(scrapy.Spider):
	name = 'jmscotia'
	start_urls = ['https://jm.scotiabank.com/about-scotiabank/media-centre/news-releases.html']

	def parse(self, response):
		post_links = response.xpath('//div[@class="cmp cmp-text"]//a/@href').getall()
		for link in post_links:
			if not 'pdf' in link:
				yield response.follow(link, self.parse_post)


	def parse_post(self, response):
		date = response.xpath('//div[@class="cmp cmp-text"]/p[1]//text()').getall()
		try:
			date = re.findall(r'\w+\s\d+\,\s\d+', ''.join(date))
		except TypeError:
			date = ""

		# try:
		# 	title = response.xpath('//h2/b/text()|//h2/text()|//h1/text()').get().strip()
		# except AttributeError:
		# 	title = ''.join(response.xpath('//h1/p/b/text()').getall())
		# if not title:
		title = response.xpath('//h1/b/text()|//h1/p/b/text()|//h2/b/text()').get()
		if not title:
			title = response.xpath('//h1//text()|//h1//text()[last()]|//h2/text()').get()

		content = response.xpath('//div[@class="cmp cmp-text"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "", ' '.join(content))

		item = ItemLoader(item=JmscotiaItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
