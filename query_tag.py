import requests
import json
import logging
from config import tag_url


def get_element(list, rst_list):
    """
    递归遍历标签树
    """
    # 获取列表中标签
    for val_list in list:
        # 有子标签递归处理
        if val_list.get("children"):
            children = val_list["children"]
            get_element(children, rst_list)

        # 将当前标签信息保存（除了子标签信息）
        val_list["children"] = []
        rst_list[val_list["id"]] = val_list


def get_tag_data(token):
    """
    获取标签树
    """
    try:
        url_info = tag_url.url_info
        params = {"id": "",
                  "tagType": ""}
        headers = {'Content-Type': 'application/json', 'token': token}
        rst_list = {}
        resp = requests.post(url_info, data=json.dumps(params), headers=headers)
        # logging.info("resp text:{}".format(resp.text))
        if resp.status_code == 200:
            response = json.loads(resp.text)
            if response.get("data"):
                data = response["data"]
                # 解析list
                if data.get("list"):
                    list = data["list"]
                    get_element(list, rst_list)
        logging.info("get_tag_data:" + json.dumps(rst_list, ensure_ascii=False))
    except Exception as ex:
        logging.error("get_tag_data: {}".format(str(ex)))
    finally:
        return rst_list


def get_tag_data_info():
    """
    获取资讯标签
    """
    try:
        url_information = tag_url.url_information
        params = {}
        headers = {'Content-Type': 'application/json'}
        rst_list = {}
        resp = requests.post(url_information, data=json.dumps(params), headers=headers)

        logging.info("resp text:{}".format(resp.text))
        if resp.status_code == 200:
            response = json.loads(resp.text)
            if response.get("data"):
                rst_list = response["data"]
        logging.info("get_tag_data_info:" + json.dumps(rst_list, ensure_ascii=False))
    except Exception as ex:
        logging.error("get_tag_data_info: {}".format(str(ex)))
    finally:
        return rst_list
