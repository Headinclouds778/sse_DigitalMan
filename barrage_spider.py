# import requests
# import time
# import io
# import sys
#
# # 设置标准输出为 UTF-8 编码，确保控制台可以正确显示中文
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
#
#
# class Danmu:
#     """
#     用于抓取B站直播间弹幕的类
#     """
#
#     def __init__(self):
#         # 弹幕获取的API地址
#         self.url = 'https://api.live.bilibili.com/xlive/web-room/v1/dM/gethistory'
#
#         # HTTP请求头，模拟浏览器发送请求，避免被服务器识别为爬虫
#         self.headers = {
#             'Host': 'api.live.bilibili.com',  # 指定目标主机
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0',  # 浏览器标识
#         }
#
#         # POST请求的数据，包含直播间ID和其他参数
#         self.data = {
#             'roomid': '597450',  # 目标直播间ID
#             'csrf_token': '',  # CSRF令牌，通常为空
#             'csrf': '',  # 同上
#             'visit_id': '',  # 访问ID，通常为空
#         }
#
#         # 存储已打印弹幕的集合
#         self.printed_danmu = set()
#
#     def get_danmu(self):
#         """
#         从目标API获取直播间弹幕并打印新的弹幕到控制台
#         """
#         try:
#             # 发送POST请求获取弹幕数据
#             response = requests.post(url=self.url, headers=self.headers, data=self.data)
#
#             # 设置响应编码为UTF-8，确保中文字符显示正确
#             response.encoding = 'utf-8'
#
#             # 将响应数据解析为JSON格式
#             html = response.json()
#
#             # 从响应数据中提取弹幕列表
#             for content in html.get('data', {}).get('room', []):
#                 # 获取发送弹幕的用户昵称
#                 nickname = content.get('nickname', '未知昵称')
#                 # 获取弹幕内容
#                 text = content.get('text', '未知内容')
#                 # 获取弹幕发送的时间
#                 timeline = content.get('timeline', '未知时间')
#
#                 # 生成弹幕的唯一标识符（这里使用时间戳和内容）
#                 unique_id = f"{timeline}-{nickname}"
#
#                 # 如果弹幕是新的，打印并记录
#                 if unique_id not in self.printed_danmu:
#                     # 格式化输出弹幕信息
#                     msg = f"{timeline} {nickname}: {text}"
#                     print(msg, flush=True)
#
#                     # 将弹幕的唯一标识符加入集合
#                     self.printed_danmu.add(unique_id)
#
#         except Exception as e:
#             # 捕获并打印异常
#             print(f"获取弹幕时发生错误: {e}", flush=True)
#
#
# if __name__ == '__main__':
#     # 创建 Danmu 类的实例
#     bDanmu = Danmu()
#
#     # 无限循环抓取弹幕
#     while True:
#         # 暂停0.5秒，避免请求过于频繁导致服务器压力过大
#         time.sleep(0.5)
#
#         # 调用 get_danmu 方法获取并打印新的弹幕
#         bDanmu.get_danmu()

import requests
import time
import io
import sys
from openai import OpenAI
import os

deepseek_api = os.environ.get("DEEPSEEK_API")
openai_api_key = os.environ.get("OPENAI_API_KEY")
deepseek_url = "https://api.deepseek.com"

# ANSI 转义码
RESET_COLOR = "\033[0m"
USER_COLOR = "\033[92m"    # 绿色
ASSISTANT_COLOR = "\033[94m"  # 蓝色

def send_request(messages, need_print=False):
    client = OpenAI(api_key=deepseek_api, base_url=deepseek_url)
    # client = OpenAI(api_key=openai_api_key)

    # Send request without streaming
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False  # Disable stream output
    )

    # Extract the response text
    response_text = response.choices[0].message.content

    # Optionally print the response
    if need_print:
        print(ASSISTANT_COLOR + response_text + RESET_COLOR, flush=True)

    return response_text

# 设置标准输出为 UTF-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class Danmu:
    def __init__(self, roomID):
        # 弹幕url
        self.url = 'https://api.live.bilibili.com/xlive/web-room/v1/dM/gethistory'
        # 请求头
        self.headers = {
            'Host': 'api.live.bilibili.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0',
        }
        # 定义POST传递的参数
        self.data = {
            'roomid': roomID,
            'csrf_token': '',
            'csrf': '',
            'visit_id': '',
        }
        # 初始化最新弹幕时间
        self.latest_time = None

    def get_danmu(self):
        """
        获取直播间弹幕并打印最新的弹幕。
        """
        try:
            # 获取弹幕数据
            response = requests.post(url=self.url, headers=self.headers, data=self.data)
            response.encoding = 'utf-8'  # 确保使用 UTF-8 编码解析
            html = response.json()

            # 获取弹幕列表
            room_data = html.get('data', {}).get('room', [])
            new_latest_time = self.latest_time

            for content in room_data:
                # 获取发言时间
                timeline = content.get('timeline', '未知时间')
                # 获取昵称
                nickname = content.get('nickname', '未知昵称')
                # 获取发言
                text = content.get('text', '未知内容')

                # 将时间字符串转换为时间戳
                timeline_timestamp = int(time.mktime(time.strptime(timeline, "%Y-%m-%d %H:%M:%S")))

                # 如果弹幕时间大于最新时间，则打印
                if self.latest_time is None or timeline_timestamp > self.latest_time:
                    msg = f"{timeline} {nickname}: {text}"
                    print(msg, flush=True)
                    # 更新最新时间
                    new_latest_time = max(new_latest_time or 0, timeline_timestamp)

            # 更新实例的最新时间
            self.latest_time = new_latest_time

        except Exception as e:
            print(f"获取弹幕时出错: {e}", flush=True)

    def get_danmu_api(self):
        """
        获取直播间弹幕并将每条弹幕作为问题向大模型提问并打印回答。
        """
        try:
            # 获取弹幕数据
            response = requests.post(url=self.url, headers=self.headers, data=self.data)
            response.encoding = 'utf-8'  # 确保使用 UTF-8 编码解析
            html = response.json()

            # 获取弹幕列表
            room_data = html.get('data', {}).get('room', [])
            new_latest_time = self.latest_time

            for content in room_data:
                # 获取发言时间
                timeline = content.get('timeline', '未知时间')
                # 获取昵称
                nickname = content.get('nickname', '未知昵称')
                # 获取发言
                text = content.get('text', '未知内容')

                # 将时间字符串转换为时间戳
                timeline_timestamp = int(time.mktime(time.strptime(timeline, "%Y-%m-%d %H:%M:%S")))

                # 如果弹幕时间大于最新时间，则进行模型调用并打印回答
                if self.latest_time is None or timeline_timestamp > self.latest_time:
                    msg = f"{timeline} {nickname}: {text}"
                    print(msg, flush=True)  # 打印原始弹幕

                    # 将弹幕作为消息传递给大模型，并获取回答
                    messages = [{"role": "user", "content": text + "请你根据上面的输出进行简短的回答（不要超过三句话）"}]
                    response_text = send_request(messages, need_print=True)

                    # 更新最新时间
                    new_latest_time = max(new_latest_time or 0, timeline_timestamp)

            # 更新实例的最新时间
            self.latest_time = new_latest_time

        except Exception as e:
            print(f"获取弹幕时出错: {e}", flush=True)

# if __name__ == '__main__':
#     # 创建 Danmu 实例
#     roomID = input("请输入B站直播房间号：")
#     # bDanmu = Danmu('597450')
#     bDanmu = Danmu(roomID)
#
#     # 定时获取弹幕
#     while True:
#         # 暂停1秒防止过于频繁
#         time.sleep(1)
#         # 获取弹幕
#         bDanmu.get_danmu()

