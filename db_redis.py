import json

from redis import Redis

conn = Redis(host='127.0.0.1', port=6379, db=1)
prefix = "welcome_"


def hwxcData_set(data):
    key = prefix + "hwxcData_qq"

    conn.rpush(key, json.dumps(data))


def hwxcData_xc_set(data):
    key = prefix + "hwxcData_xc_qq"

    conn.rpush(key, json.dumps(data))


def hwxcData_xc_len():
    key = prefix + "hwxcData_xc_qq"

    return conn.llen(key)


# ----------------------------------------------------------------------------------------------------------------------

def restrict_word_get(type_str):
    key = prefix + "restrict_word_" + str(type_str)

    val = conn.get(key)
    if val is None:
        return None
    else:
        return json.loads(val)


def restrict_word_set(type_str, val):
    key = prefix + "restrict_word_" + str(type_str)

    conn.set(key, json.dumps(val), 3600)  # 1小时
