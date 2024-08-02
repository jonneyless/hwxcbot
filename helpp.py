import re

import db


def handle_text(text):
    text = text.replace("𝅹", "")
    text = text.replace(" ", "")
    text = text.replace(",", "")
    text = text.replace(".", "")
    text = text.replace("，", "")
    text = text.replace("。", "")
    text = text.replace("+", "")
    text = text.replace("-", "")
    text = text.replace("*", "")
    text = text.replace("/", "")
    text = text.replace("(", "")
    text = text.replace("（", "")
    text = text.replace(")", "")
    text = text.replace("）", "")
    text = text.replace("、", "")

    text = text.lower()

    return text


def has_restrict_word(text, type_str):
    text = handle_text(text)

    restrict_words = db.restrict_word_get(type_str)

    pattern_name = "(.+)\(\.\*\)(.+)"

    # type_str
    # 1msg, 9username, 4fullname
    # 1一级限制词 2三级限制词 4二级限制词
    # 其实二级限制词4限制最大, 只有msg有二级限制词

    restrict_word = None
    for item in restrict_words:
        name = item["name"]

        level = int(item["level"])

        replace_flag = False

        result_name = re.match(pattern_name, name)

        if result_name is None:
            name = handle_text(name)

            if text.find(name) >= 0:
                if restrict_word is None:
                    replace_flag = True
                else:
                    if restrict_word["level"] < level:
                        replace_flag = True

            if replace_flag:
                restrict_word = {
                    "name": name,
                    "level": level,
                }

                if int(type_str) == 1:
                    if level == 4:
                        # print("%s，%s | msg 4" % (name, text))
                        return restrict_word
                else:
                    if level == 2:
                        # print("%s，%s | msg 2" % (name, text))
                        return restrict_word
        else:
            pattern1 = name
            pattern1 = "(.*)" + pattern1
            pattern1 = pattern1 + "(.*)"

            pattern1 = pattern1.lower()

            match_result = None
            try:
                match_result = re.match(pattern1, text)
            except:
                print("%s is error" % name)

            if match_result is not None:

                if restrict_word is None:
                    replace_flag = True
                else:
                    if restrict_word["level"] < level:
                        replace_flag = True
            if replace_flag:
                restrict_word = {
                    "name": item["name"],
                    "level": level,
                }

                if int(type_str) == 1:
                    if level == 4:
                        # print("%s，%s | msg 4" % (name, text))
                        return restrict_word
                else:
                    if level == 2:
                        # print("%s，%s | msg 2" % (name, text))
                        return restrict_word

    return restrict_word


def has_fullname_restrict_word(fullname):
    type_str = "4"
    return has_restrict_word(fullname, type_str)


def has_username_restrict_word(username):
    type_str = "9"
    return has_restrict_word(username, type_str)


def has_msg_restrict_word(text):
    type_str = "1"
    return has_restrict_word(text, type_str)
