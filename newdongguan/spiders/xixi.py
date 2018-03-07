# -*- coding: utf-8 -*-
import scrapy
from newdongguan.items import NewdongguanItem


class DongdongSpider(scrapy.Spider):
    name = 'xixi'
    # allowed_domains = ['wz.sun0769.com']
    allowed_domains = ['www.zhcw.com']
    url = 'http://www.zhcw.com/xinwen/caizhongxinwen/'
    offset = 2
    start_urls = [url + "index.shtml"]


    def parse(self, response):
        # 每一页里的所有帖子的链接集合
        # links = response.xpath('//div[@class="greyframe"]/table//td/a[@class="news14"]/@href').extract()
        links = response.xpath('//div[@class="news_left"]//span[@class="Nlink"]//a/@href').extract()
        # 迭代取出集合里的链接
        for link in links:
            if link != '':
                # 提取列表里每个帖子的链接，发送请求放到请求队列里,并调用self.parse_item来处理
                # ../../xinwen/caizhongxinwen-ssq/500159.shtml
                if "../.." in link:
                    link = link.replace("../..","")
                print link
                yield scrapy.Request("http://www.zhcw.com"+link, callback = self.parse_item)

        # 页面终止条件成立前，会一直自增offset的值，并发送新的页面请求，调用parse方法处理
        if self.offset <= 320:
            self.offset += 1
            # 发送请求放到请求队列里，调用self.parse处理response
            # http: // www.zhcw.com / xinwen / caizhongxinwen / index_6.shtml
            yield scrapy.Request(self.url + "index_"+str(self.offset)+".shtml", callback = self.parse)

    # 处理每个帖子的response内容
    def parse_item(self, response):
        item = NewdongguanItem()
        # 标题
        # item['title'] = response.xpath('//div[contains(@class, "pagecenter p3")]//strong/text()').extract()[0]
        item['title'] = response.xpath('//div[@id = "news_main"]//div[@class = "news_content"]/h2[@class = "newsTitle"]/text()').extract()[0]
        # 编号
        item['number'] = response.xpath('//div[@id = "news_main"]//div[@class = "news_content"]//div[@class = "message"]/text()').extract()[0]

        # 内容，先使用有图片情况下的匹配规则，如果有内容，返回所有内容的列表集合
        contents = response.xpath('//div[@id = "news_main"]//div[@class = "news_content"]//p/text()').extract()
        content =""
        for cont in contents:
            content = content+cont
        item['content']= content

        item['url'] = response.url

        # 交给管道
        yield item

