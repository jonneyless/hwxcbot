import json
import string
import time

import requests
from zhon.hanzi import punctuation


# ======================================================================================================================

def create_index(name, level):
    tg_url = "http://welcome.huionedanbao.com:8639/api/createWord"

    data = {
        "name": name,
        "type": 1,
        "level": level,
    }

    response = requests.post(tg_url, params=data, timeout=5)

    if (response is None) or not hasattr(response, "text"):
        return False

    return json.loads(response.text)


# ======================================================================================================================


def is_number(s):
    if len(s) == 0:
        return False

    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        for i in s:
            unicodedata.numeric(i)
        return True
    except (TypeError, ValueError):
        pass
    return False


def to_num(num, temp=0):
    if int(num) == float(num):
        return int(num)

    if temp == 0:
        return round(num, 1)
    else:
        num = float(num)
        return round(num, temp)


def to_num2(num):
    num = float(num)
    return round(num, 2)


def get_num_len(num):
    num = float(num)
    if int(num) == num:
        return 0

    num = str(num)
    temp = num.find(".")
    if temp > -1:
        return len(num[(temp + 1):])
    else:
        return 0


def get_current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def get_today_time():
    return time.strftime("%Y-%m-%d", time.localtime())


def get_24_time():
    today = get_current_timestamp()
    yesterday = today - 86400

    return timestamp2time(yesterday)


def get_current_six_time():
    today = time.strftime("%Y-%m-%d", time.localtime())
    return today + " 06:00:00"


def get_yesterday_six_time():
    today = get_today_timestamp()
    yesterday = today - 3600 * 18

    return timestamp2time(yesterday)


def get_simple_time(created_at):
    created_at = str(created_at)
    space = created_at.find(" ")
    return created_at[(space + 1):]


def time2timestamp(t, flag=True):
    if flag:
        return int(time.mktime(time.strptime(t, '%Y-%m-%d %H:%M:%S')))
    else:
        return int(time.mktime(time.strptime(t, '%Y-%m-%d')))


def timestamp2time(t):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))


def get_today_timestamp():
    return time2timestamp(get_today_time(), False)


def get_current_timestamp():
    return int(time.time())


# ======================================================================================================================

def replace_string(text):
    punctuation_str = string.punctuation
    for i in punctuation_str:
        text = text.replace(i, "")

    punctuation_str = punctuation
    for i in punctuation_str:
        text = text.replace(i, "")

    return text


def is_address(text):
    text = replace_string(text)

    text_len = len(text)

    flag = False

    if text[0] == "T" and text_len == 34:
        flag = True

    if text[0] == "0" and text[1] == "x" and text_len == 42:
        flag = True

    return flag
