import re

from telethon import TelegramClient

import db
import db_redis
import helpp
from assist import is_address, create_index, get_chinese_len


async def kick_and_delete_operation(user_tg_id, groups, official_tg_id, username, fullname, message_id, special=True):
    group_tg_ids = []
    for group in groups:
        group_tg_ids.append(group["group_tg_id"])

    if special:
        db_redis.hwxcData_set({
            "ope_user_tg_id": official_tg_id,
            "ope_msg_tg_id": message_id,

            "user_tg_id": user_tg_id,
            "username": username,
            "fullname": fullname,
            "group_tg_ids": group_tg_ids,
        })
    else:
        db_redis.hwxcData_xc_set({
            "ope_user_tg_id": official_tg_id,
            "ope_msg_tg_id": message_id,

            "user_tg_id": user_tg_id,
            "username": username,
            "fullname": fullname,
            "group_tg_ids": group_tg_ids,
        })


async def kick_and_delete(bot, event, user, official_tg_id):
    user_tg_id = user["tg_id"]

    groups = await db.user_group_get(user_tg_id)

    text_basic = "用户tgid: %s\n" % user_tg_id
    text_basic += "用户名：@%s\n" % user["username"]
    text_basic += "用户昵称: %s\n" % user["fullname"]
    text_basic += "群组：%s个\n" % len(groups)
    text_basic += "正在执行：删除所有信息、踢出所在群组、加入黑名单\n"

    text = text_basic + "状态：执行中...\n"
    text_over = text_basic + "状态：<b>已完成</b>"

    if official_tg_id == 2075404587:
        pass
    else:
        data_len = db_redis.hwxcData_xc_len()
        text += "\n待处理数据 %s" % data_len

    m = await event.reply(message=text)
    message_id = None
    if m is not None:
        message_id = int(m.id)

    official_tg_id = int(official_tg_id)

    # if official_tg_id == 5156229400 or official_tg_id == 2075404587:
    if official_tg_id == 2075404587:
        await kick_and_delete_operation(user_tg_id, groups, official_tg_id, user["username"], user["fullname"], message_id, True)
    else:
        await kick_and_delete_operation(user_tg_id, groups, official_tg_id, user["username"], user["fullname"], message_id, False)


async def check_and_save_cheat(bot, event, user, official_tg_id):
    user_tg_id = user["tg_id"]

    official = await db.official_one(user_tg_id)
    if official is not None:
        await event.reply(message="尝试操作的用户为官方账号，无法将其添加到骗子库，请核对后重新操作")
        return

    white = await db.white_one(user_tg_id)
    if white is not None:
        await event.reply(message="尝试操作的用户为白名单账号，无法将其添加到骗子库，请核对后重新操作")
        return

    admin = await db.admin_one(user_tg_id)
    if admin is not None:
        await event.reply(message="尝试操作的用户为群管理，无法将其添加到骗子库，请核对后重新操作")
        return

    await db.cheat_save(user_tg_id, "汇旺巡查机器人添加", official_tg_id)

    await kick_and_delete(bot, event, user, official_tg_id)


async def index(bot: TelegramClient, event, sender_id, text, fwd_from):
    official_tg_id = sender_id

    if fwd_from is not None:
        fwd_from_from_id = fwd_from.from_id
        if fwd_from_from_id is not None:
            if hasattr(fwd_from_from_id, "user_id") and (fwd_from_from_id.user_id is not None):
                fwd_from_user_id = fwd_from_from_id.user_id
                fwd_from_user_id = int(fwd_from_user_id)

                if int(official_tg_id) == 2075404587:
                    pass
                else:
                    msg_restrict_word = helpp.has_msg_restrict_word(text)
                    if msg_restrict_word is not None:
                        name = msg_restrict_word["name"]
                        level = int(msg_restrict_word["level"])

                        text_show = "该信息中包含违禁词：<b>%s</b>，请核对qunguan机器人是否正常" % name

                        await event.reply(message=text_show, parse_mode="HTML")

                user = await db.user_one(fwd_from_user_id)
                if user is not None:
                    await check_and_save_cheat(bot, event, user, official_tg_id)
                else:
                    await event.reply(message="没有找到该用户在公群中")
        else:
            await event.reply(message="该用户为隐私用户")
            return
    elif event.message.reply_to is not None:
        replyMessages = await bot.get_messages(event.chat_id, ids=[event.message.reply_to.reply_to_msg_id])
        if replyMessages is not None and len(replyMessages) > 0:
            replyMessage = replyMessages[0]
            pattern = r'用户tgid: (\d+)'
            result = re.match(pattern, replyMessage.message)
            if result is not None:
                userTgId = result.group(1)

                await db.cheat_update(userTgId, text)
                await db.cheat_special_update(userTgId, text)
    else:
        if text == "/start":
            await event.respond(message="欢迎使用巡查助理")
            return

        if text[0:4] == "/fdz":
            text = text.replace("/fdz", "")
            text = text.replace(" ", "")

            if is_address(text):
                cheat_coin = await db.cheat_coin_one(text)
                if cheat_coin is not None:
                    await event.reply(message="该地址已经在虚拟币骗子库中")
                else:
                    await db.cheat_coin_save(text, sender_id)
                    await event.reply(message="加入虚拟币骗子库成功")
            else:
                await event.respond(message="请输入正确的地址")

            return

        if text[0:4] == "/fid":
            tg_id = text.replace("/fid", "")
            tg_id = tg_id.replace(" ", "")
            tg_id = tg_id.replace("@", "")

            user = await db.user_one(tg_id)
            if user is not None:
                await check_and_save_cheat(bot, event, user, official_tg_id)
            else:
                await event.reply(message="没有找到该用户在公群中")

            return

        if text[0:2] == "/f":
            username = text.replace("/f", "")
            username = username.replace(" ", "")
            username = username.replace("@", "")
            username = username.lower()

            user = await db.user_one_by_username(username)
            if user is not None:
                await check_and_save_cheat(bot, event, user, official_tg_id)
            else:
                await event.reply(message="没有找到使用该用户名的用户在公群中")

            return

        if text[0:5] == "/mgc+":
            word = text.replace("/mgc+", "")

            pattern_name = "(.+)\\+(.+)"
            result = re.match(pattern_name, word)
            if result is None:
                await event.reply(message="命令有误，请去除特殊符号和空格后重新输入")
                return
            else:
                name = None
                level = None
                try:
                    name = result.group(1)
                    level = result.group(2)
                except:
                    pass

                if name is not None and level is not None:
                    result = create_index(name, level)
                    if result is not None:
                        await event.reply(message=result["message"])
                        return
                    else:
                        await event.reply(message="添加失败")
                else:
                    await event.reply(message="命令有误，请去除特殊符号和空格后重新输入")
        else:
            if text.find("mgc") != -1:
                await event.reply(message="命令有误，请去除特殊符号和空格后重新输入")

        if get_chinese_len(text) >= 6:
            msgs = db.getMsgsByInfo(text)
            msgCount = len(msgs)
            if msgCount > 0:
                officialTgIds = await db.official_tg_ids()
                users = {}
                groups = {}

                data = {}
                for msg in msgs:
                    if msg['user_id'] in officialTgIds:
                        msgCount = msgCount - 1
                        continue

                    users[msg['user_id']] = msg['user_id']
                    groups[msg['chat_id']] = msg['chat_id']

                    if msg['chat_id'] not in data:
                        data[msg['chat_id']] = {}

                    if msg['user_id'] not in data[msg['chat_id']]:
                        data[msg['chat_id']][msg['user_id']] = []

                    data[msg['chat_id']][msg['user_id']].append(msg['message_id'])

                if msgCount > 0:
                    text_basic = "待处理用户： %s个\n" % len(users)
                    text_basic += "待处理群组：%s个\n" % len(groups)
                    text_basic += "待删除消息: %s条\n" % len(msgs)
                    text_basic += "状态：\n"

                    m = await event.reply(message=text_basic + "执行中...")
                    db_redis.hwxcData_set({"type": "delete", "official": official_tg_id, 'notice_id': m.id, 'notice': text_basic, 'userIds': users, "data": data})
