# -*- coding: utf-8 -*-
import re
import scrapy
import datetime
from scrapy.http import Request
from urllib import parse
from scrapy.loader import ItemLoader

from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals

from ArticleSpider.items import JobBoleArticleItem, ArticleItemLoader
from ArticleSpider.utils.common import get_md5


class JobboleSpider(scrapy.Spider):
	name = 'jobbole'
	allowed_domains = ['blog.jobbole.com']
	start_urls = ['http://blog.jobbole.com/all-posts']

	def __init__(self, **kwargs):
		self.fail_urls = []
		dispatcher.connect(self.handle_spider_closed, signals.spider_closed)

	def handle_spider_closed(self, spider, reason):
		self.crawler.stats.set_value("failed_urls", ",".join(self.fail_urls))

	def parse(self, response):
		if response.status == 404:
			self.fail_urls.append(response.url)
			self.crawler.stats.inc_value("failed_url")

		post_nodes = response.css("#archive .floated-thumb .post-thumb a")
		for post_node in post_nodes:
			image_url = post_node.css("img::attr(src)").extract_first("")
			post_url = post_node.css("::attr(href)").extract_first("")
			yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url},
			              callback=self.parse_detail)  # 域名需要连接

		# 提取下一页并且交给scrapy进行下载
		next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
		if next_url:
			yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse)

	def parse_detail(self, response):
		article_item = JobBoleArticleItem()
		front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
		# 使用自定义的ArticleItemLoader这个类来实现需用每个函数中都添加TakeFirst（）这个函数
		item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
		item_loader.add_css("title", ".entry-header h1::text")
		item_loader.add_value("url", response.url)
		item_loader.add_value("url_object_id", get_md5(response.url))
		item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
		item_loader.add_value("front_image_url", [front_image_url])
		item_loader.add_css("praise_nums", ".vote-post-up h10::text")
		item_loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
		item_loader.add_css("fav_nums", ".bookmark-btn::text")
		item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
		item_loader.add_css("content", "div.entry")

		article_item = item_loader.load_item()

		yield article_item
