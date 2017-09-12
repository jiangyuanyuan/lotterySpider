# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs
import json
import MySQLdb
from twisted.enterprise import adbapi
from scrapy.http import Request

import MySQLdb.cursors

class NewdongguanPipeline(object):
    def __init__(self,dbpool):
        # 创建一个文件
        # self.filename = codecs.open("donggguan.json", "w", encoding = "utf-8")
        # self.dbpool = adbapi.ConnectionPool('MySQLdb',
        #                                     host='59aeb05f83aa4.gz.cdb.myqcloud.com',  # 本地
        #                                     db='jyy',
        #                                     user='jyy',
        #                                     passwd='jyy123',
        #                                     port=5916,
        #                                     charset='utf8',  # 防止中文乱码
        #                                     cursorclass=MySQLdb.cursors.DictCursor,
        #                                     use_unicode=True
        #                                     )
        # self.conn = MySQLdb.connect(host="59aeb05f83aa4.gz.cdb.myqcloud.com", user="jyy", passwd="jyy123", db="jyy" ,port= int("5916"))
        # self.cursor = conn.cursor()

        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        '''1、@classmethod声明一个类方法，而对于平常我们见到的则叫做实例方法。
           2、类方法的第一个参数cls（class的缩写，指这个类本身），而实例方法的第一个参数是self，表示该类的一个实例
           3、可以通过类来调用，就像C.f()，相当于java中的静态方法'''
        dbparams = dict(
            host=settings['MYSQL_HOST'],  # 读取settings中的配置
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            port=settings['MYSQL_PORT'],
            charset='utf8',  # 编码要加上，否则可能出现中文乱码问题
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=False,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparams)  # **表示将字典扩展为关键字参数,相当于host=xxx,db=yyy....
        return cls(dbpool)  # 相当于dbpool付给了这个类，self中可以得到

    def process_item(self, item, spider):
        # 中文默认使用ascii码来存储，禁用后默认为Unicode字符串
        # content = json.dumps(dict(item), ensure_ascii=False) + "\n"
        # self.filename.write(content)
        # self.cursor.execute("select count(*) from douban")
        # self.cursor.execute("INSERT INTO `jyy`.`lottery_info` (`url`, `num`, `title`, `content`) VALUES (%s,%s,%s,%s);",(item["url"],item["number"],item["title"],item["content"]))
        query = self.dbpool.runInteraction(self._conditional_insert, item)  # 调用插入的方法

        query.addErrback(self._handle_error, item, spider)  # 调用异常处理方法
        return item


    def _conditional_insert(self, tx, item):
            # print item['name']
        # sql = "insert into lottery_info(name,url) values(%s,%s)"
        try:
            # sql = "insert into lottery_info(url,num,title,content) values(%s,%s,%s,%s)"
            sql = "INSERT INTO `jyy`.`lottery_info` (`url`, `num`, `title`, `content`) VALUES (%s,%s,%s,%s);"
            params = (item["url"], item["number"],item["title"],item["content"])
            # tx.execute("INSERT INTO `jyy`.`lottery_info` (`url`, `num`, `title`, `content`) VALUES (%s,%s,%s,%s);",(item["url"],item["number"],item["title"],item["content"]))
            # tx.execute("insert into lottery_info(url,num,title,content) values('10','10','10','10')")
            tx.execute(sql,params)
            # self.dbpool.commit()

        except MySQLdb.Error, e:
            print "failue"

    def _handle_error(self, failue, item, spider):
        print failue

    # def close_spider(self, spider):
    #     self.filename.close()
