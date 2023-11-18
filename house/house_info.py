import json
import dbm
import re
import os
import httpx


def read_config(filename: str) -> dict:
    with open(filename, "r", encoding="utf8") as file:
        config_dict = json.load(file)
    return config_dict


DIR_NAME = os.path.dirname(os.path.abspath(__file__))
CONFIG_DICT = read_config(f"{DIR_NAME}/house.json")


def chatbot_send_msg(msg: str) -> None:
    """企业微信发送群消息"""
    post_data = {
        "msgtype": "text",
        "text": {"content": msg},
    }
    response = httpx.post(CONFIG_DICT["CHATBOT_URL"], json=post_data)
    print(response.json())


def record_exists(url: str, name: str) -> bool:
    """检查本地数据库是否存在url"""
    with dbm.open(f"{DIR_NAME}/data", "c") as db:
        if url in db:
            return True
        else:
            db[url] = name
            return False


def process_response(row_txt: str) -> str:
    data = re.findall(r'<caption><a href="(.+?)" target="_blank" class="F14">(.+?)</a>', row_txt)
    msg_lines = [f"{name}:{url}" for url, name in data if not record_exists(url, name)]
    if msg_lines:
        msg = "\n".join(msg_lines) + "\n详细信息:http://gycq.zjw.beijing.gov.cn/enroll/home.jsp"
    else:
        msg = ""
    return msg


def craw_house_info() -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
        "Cookie": CONFIG_DICT["Cookie"],
    }
    url = "http://gycq.zjw.beijing.gov.cn/enroll/dyn/enroll/viewEnrollHomePager.json"
    post_data = {"currPage": 1, "pageJSMethod": "goToPage"}
    response = httpx.post(url, json=post_data, headers=headers, timeout=10)
    j_data = response.json()
    if j_data.get("flag") == 1:
        # cookie alive
        msg = process_response(j_data["data"])
    elif j_data.get("flag") == -22:
        # cookie expired
        msg = "Aliyun共有产权房程序Cookie expired:通过http://gycq.zjw.beijing.gov.cn/enroll/home.jsp更新cookie"
    else:
        msg = "key flag not exist!"
    return msg


if __name__ == "__main__":
    try:
        msg = craw_house_info()
    except Exception as e:
        msg = f"craw_house_info exception:{e}"

    if msg:
        # 当没有消息内容为空(project_urls为空)的时候，不发送
        chatbot_send_msg(msg)
