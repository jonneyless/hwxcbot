import re

from telethon import TelegramClient, events

import db
import db_redis
import handle_message
from assist import get_current_time
from config import *

bot = TelegramClient('hwxcbot1', 25957341, 'd78e20c41b8eecb6014bbeb6ba7aa6ec', auto_reconnect=True).start(
    bot_token=bot_token)


@bot.on(events.NewMessage(incoming=True))
async def new_message(event):
    message = event.message
    text = message.text

    chat_id = event.chat_id
    sender_id = event.sender_id

    if chat_id == sender_id and sender_id > 0:
        print("%s %s: %s" % (sender_id, get_current_time(), text))

        official = await db.official_one(sender_id)
        if official is not None:
            await handle_message.index(bot, event, sender_id, text, message.fwd_from)
            # try:
            #     await handle_message.index(bot, event, sender_id, text, message.fwd_from)
            # except:
            #     pass
        else:
            await event.reply(message="没有权限")
    else:
        if text == "hwxcQwerasdf":
            await event.reply(message="hwxcSuccess")


@bot.on(events.CallbackQuery())
async def callback(event):
    chat_id = event.chat_id
    sender_id = event.sender_id
    msg_id = event.query.msg_id

    official = await db.official_one(sender_id)
    if official is None:
        return

    callback_data = event.query.data
    callback_data = callback_data.decode('utf-8')

    args = {}
    info = callback_data
    if callback_data.find("?") >= 0:
        arr = callback_data.split("?")
        if len(arr) == 2:
            info = arr[0]
            args_temp = arr[1]

            args_temp = args_temp.split("&")
            for item in args_temp:
                item = item.split("=")
                if len(item) == 2:
                    args[item[0]] = item[1]

    if info == "cheat":
        await db.cheat_special_save(args["user_tg_id"], "汇旺巡查机器人添加", sender_id)
        await event.answer(message="添加成功", alert=True)
        return

    if info == "cheat_from_msg":
        async with bot.conversation(event.sender_id) as conv:
            await conv.send_message('请输入原因!')
            response = conv.get_response()
            response = await response

            msg = await event.get_message()
            text = msg.text

            patten = re.compile(r"\[(\d+)]")
            userIds = patten.findall(text)
            reason = response.text

            for userId in userIds:
                await db.cheat_special_save(userId, reason, sender_id)

            await bot.edit_message(entity=event.chat_id, message=msg, text=text, buttons=None)
            m = await bot.send_message(entity=event.chat_id, message="已加入骗子库，正在尝试从所有群中踢出…")
            db_redis.hwxcData_set({"type": "kick", "official": sender_id, 'notice_id': m.id, 'notice': "", 'userIds': userIds, 'data': userIds})


if __name__ == '__main__':
    print("init...")
    try:
        bot.run_until_disconnected()
    except:
        print("bot error...")
