# -*- coding: utf-8 -*-
import logging
import logging.config
import sys
import os
import json
import re
from tornado.escape import json_decode
import tornado
from tornado.concurrent import run_on_executor
from tornado.web import RequestHandler

import yaml
from tornado.options import define, options
import article_key_words
import similiarity
import query_tag
import time
import spacy

define("port", default=10000, help="run on the given port", type=int)


class tag(tornado.web.RequestHandler):
    def filter_tags_blank(self, str):
        """
        去掉html标签和空格
        """
        p = re.compile('<[^>]+>').sub("", str)
        return "".join(p.split())

    def post(self):
        try:
            # 解析text和token字段
            str_data = self.request.body.decode("utf-8")
            text = self.filter_tags_blank(json.loads(str_data)["text"])
            token = self.request.headers.get("Token")
            logging.info("text:{}".format(text))
            logging.info("token:{}".format(token))

            # 获取标签树
            tag_time_start = time.time()
            tag_data = query_tag.get_tag_data(token)
            tag_time_end = time.time()
            # 获取文章关键字
            key_words_time_start = time.time()
            key_words = article_key_words.get_key_words(text)
            key_words_time_end = time.time()
            logging.info("get_key_word:{}".format(key_words))
            # 计算相识度
            similiarity_time_start = time.time()
            result = similiarity.get_similarity(tag_data, key_words)
            similiarity_time_end = time.time()

            rst = {"code": "1000", "message": "接口调用成功", "list": result}
            logging.info("result tag:{}".format(rst))
            logging.info('----------------获取标签树所需时间: ' + str(tag_time_end - tag_time_start) + '---------------')
            logging.info('------------------标签数量：' + str(len(tag_data)))
            logging.info(
                '----------------获取文章关键字所需时间: ' + str(key_words_time_end - key_words_time_start) + '---------------')
            logging.info(
                '----------------计算相识度所需时间: ' + str(similiarity_time_end - similiarity_time_start) + '---------------')

            self.write(json.dumps(rst, ensure_ascii=False).encode('utf8'))
        except Exception as e:
            rst = {"code": "500", "message": e, "list": []}
            logging.info("result tag:{}".format(rst))
            self.write(json.dumps(rst, ensure_ascii=False).encode('utf8'))


class information(tornado.web.RequestHandler):
    def filter_tags_blank(self, str):
        """
        去掉html标签和空格
        """
        p = re.compile('<[^>]+>').sub("", str)
        return "".join(p.split())

    def post(self):
        try:
            # 解析text和token字段
            str_data = self.request.body.decode("utf-8")
            text = self.filter_tags_blank(json.loads(str_data)["text"])
            # token = self.request.headers.get("Token")
            logging.info("text:{}".format(text))
            # logging.info("token:{}".format(token))

            # 获取标签树
            # tag_time_start = time.time()
            # tag_data = query_tag.get_tag_data_info()
            # tag_time_end = time.time()
            # 获取文章关键字
            key_words_time_start = time.time()
            key_words = article_key_words.get_key_words(text)
            key_words_time_end = time.time()
            logging.info("get_key_word:{}".format(key_words))
            # 计算相识度
            similiarity_time_start = time.time()
            result = similiarity.get_similarity_info(key_words, tag_nlp_dict)
            similiarity_time_end = time.time()

            rst = {"code": "1000", "message": "接口调用成功", "list": result}
            logging.info("result tag:{}".format(rst))
            logging.info(
                '----------------获取文章关键字所需时间: ' + str(key_words_time_end - key_words_time_start) + '---------------')
            logging.info(
                '----------------计算相识度所需时间: ' + str(similiarity_time_end - similiarity_time_start) + '---------------')

            self.write(json.dumps(rst, ensure_ascii=False).encode('utf8'))
        except Exception as e:
            rst = {"code": "500", "message": e, "list": []}
            logging.info("result tag:{}".format(rst))
            self.write(json.dumps(rst, ensure_ascii=False).encode('utf8'))


if __name__ == "__main__":
    nlp = spacy.load(".//vec")
    # 获取标签树
    tag_time_start = time.time()
    tag_data = query_tag.get_tag_data_info()
    tag_time_end = time.time()
    tag_nlp_dict = {}

    # 遍历文章关键字与后边标签树，做相识度对比
    for i in tag_data:
        tag_nlp = nlp(i['tagName'])
        tag_nlp_dict[i['id']] = {"nlp": tag_nlp, "name": i["tagName"], "tag_initial": i}

    if not os.path.exists("./logs/"):
        os.makedirs("./logs/")

    args = sys.argv
    tornado.options.parse_command_line(args=args)
    logging.config.dictConfig(yaml.load(open('logging.yaml', 'r')))


    logging.info(tag_nlp_dict)
    logging.info('----------------获取标签树所需时间: ' + str(tag_time_end - tag_time_start) + '---------------')
    logging.info("tag log")
    handlers = [(r"/tag", tag), (r"/tag/information", information)]

    app = tornado.web.Application(handlers)

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
