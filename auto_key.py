#!/usr/bin/env python3

import RPi.GPIO as GPIO # RPi.GPIOモジュールを使用
import time
import subprocess
import requests

# LEDのGPIO番号
gpio_red = 7
gpio_green = 5
gpio_orange = 13

#GPIO番号指定の準備
GPIO.setmode(GPIO.BCM)

# LEDピンを出力に設定
GPIO.setup(gpio_red, GPIO.OUT)
GPIO.setup(gpio_green, GPIO.OUT)
GPIO.setup(gpio_orange, GPIO.OUT)

# GPIOのテスト
GPIO.output(gpio_red, 1)
GPIO.output(gpio_green, 1)
GPIO.output(gpio_orange, 1)
time.sleep(2)
GPIO.output(gpio_red, 0)
GPIO.output(gpio_green, 0)
GPIO.output(gpio_orange, 0)

# 解錠条件初期化
# RTX1210上で振るIPアドレスを端末ごとに固定しておく
Client_list = {"Pixel6a": {"host": "192.168.1.XX", "status": 0, "count": 0}, "Motog53y": {"host": "192.168.1.XX", "status": 0, "count":0}}

# 無限ループ設定
while True:
        print("処理クライアントリスト")
        print(Client_list)
        # 解錠条件の辞書を繰り返し判定
        for key, value in Client_list.items():
                hostname = key
                host = value["host"]
                status = value["status"]
                count = value["count"]
                # 前回statusが15回以上外出または、count0のとき、Ping実行
                if status > 15 or count == 0:
                        # Ping実行、実行中オレンジランプ点灯
                        GPIO.output(gpio_orange, 1)
                        print("ping実行 " + key)
                        res = subprocess.run(["ping",host,"-c","2", "-w", "3"],stdout=subprocess.PIPE)
                        GPIO.output(gpio_orange, 0)
                        # 在宅・帰宅判定
                        if res.returncode == 0:
                                print("ping成功　在宅判定")
                                # ping成功→在宅
                                if status > 15:
                                        # 今回在宅、前回外出→今回帰宅、解錠
                                        # 解錠中赤ランプ点灯
                                        GPIO.output(gpio_red, 1)
                                        # 解錠API叩く
                                        unlock_url = "https://script.google.com/macros/s/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
					                              # アンロック時に端末名を足す
                                        unlock_url = unlock_url + key
                                        requests.get(unlock_url)
                                        print("解錠実行")
                                        # 解錠表示灯点灯
				                              	# 解錠表示灯はRaspberry Pi Picoで別途作っておく
                                        requests.get("http://192.168.1.XX/?led=on")
                                        # 解錠後600秒待機
                                        time.sleep(600)
                                        # 施錠API叩く
                                        lock_url = "https://script.google.com/macros/s/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
                                        requests.get(lock_url)
                                        print("施錠実行")
                                        # 施錠、赤ランプ消灯
                                        GPIO.output(gpio_red, 0)
                                        # 解錠表示灯消灯
                                        requests.get("http://192.168.1.XX/?led=off")
                                        # 解錠条件初期化(しないと同時帰宅のとき再度解錠してしまう)
                                        Client_list = {"Pixel6a": {"host": "192.168.1.XX", "status": 0, "count": 0}, "Motog53y": {"host": "192.168.1.XX", "status": 0, "count":0}}
                                else:
                                        # 外出statusが15以下→今回在宅、一時的な疎通不良と判断、解錠せず
                                        Client_list[hostname]["status"] = 0
                                        Client_list[hostname]["count"] = 75
                        else:
                                print("ping不達　外出判定")
                                # 外出判定
                                if status < 16:
                                        Client_list[hostname]["status"] = Client_list[hostname]["status"] + 1
                elif count >= 1:
                        # 前回在宅の場合、75カウント約5分はpingを打たない
                        Client_list[hostname]["count"] -= 1
        # 4秒待機、緑ランプ点滅
        for i in range(2):
                GPIO.output(gpio_green, 1)
                time.sleep(0.1)
                GPIO.output(gpio_green, 0)
                time.sleep(0.1)
                GPIO.output(gpio_green, 1)
                time.sleep(0.1)
                GPIO.output(gpio_green, 0)
                time.sleep(1.7)
