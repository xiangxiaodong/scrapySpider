# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql


class ArticlespiderPipeline(object):
	def process_item(self, item, spider):
		return item


class MysqlPipeline(object):
	# 采用同步机制写入mysql
	def __init__(self):
		self.conn = pymysql.connect(
			host='localhost',
			port=3306,
			db='article_spider',
			user='root',
			passwd='123456',
			charset="utf8",
			use_unicode=True)
		self.cursor = self.conn.cursor()

	def process_item(self, item, spider):
		insert_sql = """
	        INSERT INTO jobble_article(title,create_date, url, fav_nums)
	        values(%s, %s,%s, %s)
	    """
		self.cursor.execute(insert_sql, (item["title"], item["create_date"], item["url"], item["fav_nums"]))
		self.conn.commit()
		return item

	def db_close(self):
		self.conn.close()
