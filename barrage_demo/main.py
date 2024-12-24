from barrage_spider import *
import time

if __name__ == "__main__":
    # 创建 Danmu 实例
    roomID = input("请输入B站直播房间号：")
    # bDanmu = Danmu('597450')
    bDanmu = Danmu(roomID)

    # 定时获取弹幕
    while True:
        # 暂停1秒防止过于频繁
        time.sleep(1)
        # 获取弹幕
        bDanmu.get_danmu_api()

