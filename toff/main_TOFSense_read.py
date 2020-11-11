# -*- coding: utf-8 -*-
"""
主程式  main_TOFSense_read
讀取UART串聯應用的nooploop TOFsence雷射模組
需要檔案 TOFSense_concatenate.py  serial_select.py

朱津嶙 20201111
"""

import serial
import time
import TOFSense_concatenate as tof    #自己寫的
import serial_select as serset    #自己寫的

#====================主程式====================
    #連上序列埠  Rpi中應更改
com = serset.input_COMport()
baud = serset.input_Baud()
ser = serial.Serial(com, baud)
print("連線成功!  可按 ctrl + C 關閉程式\n")
time.sleep(0.1)
ser.flushInput()  #清空接收緩存

try:
    ID_list = tof.IDscan(ser)  #自動取得線上的感測器ID
    data = {}
    while True:
        time.sleep(1)
        #發送要求
        for ID in ID_list:
            tof.ask(ser,ID)    #發送指令要求模組回傳
            time.sleep(0.001)    #要求之間要有暫停，不然不會回覆
        #讀取回傳
        for ID in ID_list:
            if ser.in_waiting:    #如果緩存中有資料
                gotbata = tof.read(ser)    #讀取回傳的資料(如果已經回傳了)
                data[gotbata["id"]] = gotbata    #依照讀取到的資料中的'id'作為Key存入字典型變數"data"中
                if gotbata["id"] !=-1:  #讀取失敗時
                    print("ID:",gotbata["id"],"  distance =",gotbata["distance"])
                gotbata = tof.read(ser)    #多讀一次，以免有漏
                data[gotbata["id"]] = gotbata
                if gotbata["id"] !=-1:
                    print("ID:",gotbata["id"],"  distance =",gotbata["distance"])
        #print("ser.in_waiting",ser.in_waiting)    #顯示緩存中的字節數(在此，代表有資料沒讀乾淨)
        
    """
資料儲存成雙重字典"data"，第一層以id(數字)為key選擇感測器
第二層則是有"id" "systime" "distance" "status" "quality"等key，可以獲得所選感測器的各個參數
data[id]              返回一個字典
data[id]['id']        返回id(數字)
data[id]["systime"]   返回模組的系統時間(數字)
data[id]["distance"]  返回距離(數字)
data[id]["status"]    返回狀態代號(數字)
data[id]["quality"]   返回回波強度(數字)

代號的意思可以使用如下方法查詢
TOFsence_dist_stat[data[1]["status"]]  可以得到距離狀態代號的意思(中文字串)
"""
            
except KeyboardInterrupt:
    ser.close()    # 清除序列通訊物件
    print('斷開連線\n再見！')
except:
    ser.close()    # 清除序列通訊物件
    print('發生錯誤，斷開連線')

