import db_redis
from assist import get_current_time
from dbpool import OPMysql


# ======================================================================================================================

async def user_one(user_tg_id):
    opm = OPMysql()

    sql = "select id, tg_id, username, fullname from users_new where tg_id = '%s' limit 1" % user_tg_id

    result = opm.op_select_one(sql)

    opm.dispose()

    return result


async def user_one_by_username(username):
    opm = OPMysql()

    sql = "select id, tg_id, username, fullname from users_new where username = '%s' limit 1" % username

    result = opm.op_select_one(sql)

    opm.dispose()

    return result


async def user_group_get(user_tg_id):
    opm = OPMysql()

    sql = "select group_tg_id from user_group_new where user_tg_id = '%s' order by id desc" % user_tg_id

    result = opm.op_select_all(sql)

    opm.dispose()

    return result


async def official_one(user_tg_id):
    opm = OPMysql()

    sql = "select id from offical_user where tg_id = '%s' limit 1" % user_tg_id

    result = opm.op_select_one(sql)

    opm.dispose()

    return result


async def official_tg_ids():
    opm = OPMysql()

    sql = "select tg_id from offical_user"

    result = opm.op_select_all(sql)

    opm.dispose()

    tgIds = []
    for user in result:
        tgIds.append(user['tg_id'])

    return tgIds


async def white_one(user_tg_id):
    opm = OPMysql()

    sql = "select id from white_user where tg_id = '%s' limit 1" % user_tg_id

    result = opm.op_select_one(sql)

    opm.dispose()

    return result


async def admin_one(user_tg_id):
    opm = OPMysql()

    sql = "select id from group_admin where user_id = '%s'" % user_tg_id

    result = opm.op_select_one(sql)

    opm.dispose()

    return result


# ======================================================================================================================

async def cheat_one(user_tg_id):
    opm = OPMysql()

    sql = "select id from cheats where tgid = '%s'" % user_tg_id

    result = opm.op_select_one(sql)

    opm.dispose()

    return result


async def cheat_save(user_tg_id, reason, official_id):
    obj = await cheat_one(user_tg_id)
    if obj is not None:
        return

    opm = OPMysql()

    sql = "insert into cheats(tgid, created_at, reason, admin_id, official_id) values('%s', '%s', '%s', '%s', '%s')" % (
        user_tg_id, get_current_time(), reason, "-1", official_id)

    result = opm.op_update(sql)

    opm.dispose()

    return result


async def cheat_update(user_tg_id, reason):
    obj = await cheat_one(user_tg_id)
    if obj is None:
        return

    opm = OPMysql()

    sql = "update cheats set reason = %s where tgid = %s" % (reason, user_tg_id)

    result = opm.op_update(sql)

    opm.dispose()

    return result


# ======================================================================================================================

async def cheat_special_one(user_tg_id):
    opm = OPMysql()

    sql = "select id from cheats_special where tgid = '%s'" % user_tg_id

    result = opm.op_select_one(sql)

    opm.dispose()

    return result


async def cheat_special_save(user_tg_id, reason, official_id):
    obj = await cheat_special_one(user_tg_id)
    if obj is not None:
        return

    opm = OPMysql()

    sql = "insert into cheats_special(tgid, created_at, reason, admin_id, official_id) values('%s', '%s', '%s', '%s', '%s')" % (
        user_tg_id, get_current_time(), reason, "-1", official_id)

    result = opm.op_update(sql)

    opm.dispose()

    return result


async def cheat_special_update(user_tg_id, reason):
    obj = await cheat_special_one(user_tg_id)
    if obj is None:
        return

    opm = OPMysql()

    sql = "update cheats_special set reason = %s where tgid = %s" % (reason, user_tg_id)

    result = opm.op_update(sql)

    opm.dispose()

    return result


# ======================================================================================================================


async def cheat_coin_one(address):
    opm = OPMysql()

    sql = "select id from cheat_coin where address = '%s'" % address

    result = opm.op_select_one(sql)

    opm.dispose()

    return result


async def cheat_coin_save(address, official_id):
    obj = await cheat_coin_one(address)
    if obj is not None:
        return

    reason = "巡查机器人录入, %s" % official_id

    opm = OPMysql()

    sql = "insert into cheat_coin(address, created_at, reason) values('%s', '%s', '%s')" % (address, get_current_time(), reason)

    result = opm.op_update(sql)

    opm.dispose()

    return result


# ======================================================================================================================

def restrict_word_get(type_str, flag=False):
    type_str = int(type_str)

    restrict_words = db_redis.restrict_word_get(type_str)
    if restrict_words is None or flag:
        restrict_words = []

        opm = OPMysql()

        sql = "select name, level from words where type = %s" % type_str

        result = opm.op_select_all(sql)

        opm.dispose()

        for item in result:
            restrict_words.append(item)

        if flag:
            print("%s %s" % (sql, len(restrict_words)))

        db_redis.restrict_word_set(type_str, restrict_words)

    return restrict_words


def getMsgsByInfo(info):
    opm = OPMysql()
    sql = "select chat_id, user_id, message_id from msg where flag = 1 and info = '%s'" % info
    result = opm.op_select_all(sql)
    opm.dispose()

    return result
