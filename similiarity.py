import spacy
import logging
import copy
import time

nlp = spacy.load(".//vec")
max_num = 10  # 返回标签个数
weight_threshold = 0.60  # 相识度阈值


def similarity(a, b):
    print("similarity: ", nlp(a).similarity(nlp(b)))


def get_similarity(tag_data, key_words):
    """
    比较标签和文章关键字相识度，超过给定阀值的，得到最高的10个，
    """
    tag_lists = {}
    key_lists = {}
    tmp_tag_list = {}
    tag_nlp_dict = {}

    # 遍历文章关键字与后边标签树，做相识度对比
    for (k, v) in tag_data.items():
        tag_nlp = nlp(v["name"])
        tag_nlp_dict[k] = {"nlp": tag_nlp, "name": v["name"]}

    for val in key_words:
        key_nlp = nlp(val)
        for (k, v) in tag_nlp_dict.items():
            similarity_value = key_nlp.similarity(v["nlp"])
            # 相识度低于阈值就不要这个标签
            if similarity_value < weight_threshold:
                continue
            # 取相识度最高的并且不重复
            if (key_lists.get(val) is None or similarity_value > key_lists[val]) \
                    and k not in tag_lists:
                # 同一个标签只会被取一次
                tag_lists[k] = similarity_value
                tmp_tag_list[v["name"]] = similarity_value

                # 文章中关键字只取对应的一个标签，相识度最高的，被取过之后就取相识度第二的依此类推
                key_lists[val] = similarity_value

    logging.info("get_similarity:{}".format(tmp_tag_list))
    # 排序  取指定返回的标签
    tag_lists = sorted(tag_lists.items(), key=lambda item: item[1], reverse=True)
    rst = tag_lists[:max_num] if len(tag_lists) > max_num else tag_lists
    # 组织返回数据
    dictdata = []
    for l in rst:
        cur_tag = copy.deepcopy(tag_data[l[0]])
        cur_tag["weight"] = format(l[1] * 100, '.2f')
        # 有父标签的将父标签加上
        while cur_tag["parentId"] != "0":
            tmp_tag = cur_tag
            cur_tag = copy.deepcopy(tag_data[cur_tag["parentId"]])
            cur_tag["children"] = [tmp_tag]
        logging.info("cur_tag:{}".format(cur_tag))
        dictdata.append(cur_tag)
    return dictdata


# 资讯相识度计算
def get_similarity_info(key_words, tag_nlp_dict):
    """
    比较标签和文章关键字相识度，超过给定阀值的，得到最高的10个，
    """
    tag_lists = {}
    key_lists = {}
    tmp_tag_list = {}
    # tag_nlp_dict = {}

    # for i in tag_data:
    #     tag_nlp = nlp(i['tagName'])
    #     tag_nlp_dict[i['id']] = {"nlp": tag_nlp, "name": i["tagName"], "tag_initial": i}

    for val in key_words:
        key_nlp = nlp(val)
        for (k, v) in tag_nlp_dict.items():
            similarity_value = key_nlp.similarity(v["nlp"])
            # 相识度低于阈值就不要这个标签
            if similarity_value < weight_threshold:
                continue
            # 取相识度最高的并且不重复
            if (key_lists.get(val) is None or similarity_value > key_lists[val]) \
                    and k not in tag_lists:
                # 同一个标签只会被取一次
                tag_lists[k] = similarity_value
                tmp_tag_list[v["name"]] = similarity_value

                # 文章中关键字只取对应的一个标签，相识度最高的，被取过之后就取相识度第二的依此类推
                key_lists[val] = similarity_value

    logging.info("get_similarity:{}".format(tmp_tag_list))
    # 排序  取指定返回的标签
    tag_lists = sorted(tag_lists.items(), key=lambda item: item[1], reverse=True)
    rst = tag_lists[:max_num] if len(tag_lists) > max_num else tag_lists
    # 组织返回数据
    dictdata = []
    for l in rst:
        # cur_tag = copy.deepcopy(tag_nlp_dict[l[0]])
        cur_tag = tag_nlp_dict[l[0]]['tag_initial']
        # cur_tag["weight"] = format(l[1] * 100, '.2f')
        dictdata.append(cur_tag)
    return dictdata
