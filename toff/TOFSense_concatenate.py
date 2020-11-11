# -*- coding: utf-8 -*-
"""
副程式包 TOFSense_concatenate
讀取TOFsence的UART串聯，此時模組應工作於UART被動模式

功能:
IDscan(TOFsence_ser)    掃描ID=0~255的TOFsence(藉由發送與讀取檢查有無反應)
                                 返回一個ID數字的list
ask(TOFsence_ser,ID)    對指定的ID發送讀取指令，無返回
read(TOFsence_ser)      讀取序列埠暫存中的資料並按照TOFsence的回傳數據剖析
                        返回一個字典，有以下等key，值皆為int，當讀取失敗時傳回字典{"id":-1}
                        "id" "systime" "distance" "status" "quality"
nbyte2int(data_list)    給予一個項目值為0~255地的list，以大端在前進行合併
                        返回一個int
dist_stat               一個狀態代號(數值)對應解釋(中文字串)的字典                             
"""

import time

dist_stat = {0:"有效", 1:"標準差偏大", 2:"低信號強度", 4:"相位出界",\
                      5:"HW或VCSEL出现故障", 7:"相位不匹配", 8:"內部算法下溢",\
                      14:"測量距離無效"}  #距離狀態指示

  #掃描可用的TOFsence的ID
def IDscan(TOFsence_ser):
   print("掃描TOFsence ID中")
   ID_list = []
   for ID in range(256):
       print(ID,end="")
       TOFsence_ser.flushInput()
       ask(TOFsence_ser,ID)    #呼叫同一個檔案中的函數ask_TOFsence發送讀取指令
       time.sleep(0.01)
       if TOFsence_ser.in_waiting == 16:    #如果接收到符合長度的數據
           data = TOFsence_ser.read(16)
           if (sum(data[:15]))%256 == data[15] and data[3] == ID:    #檢查校驗及ID
               ID_list.append(ID)
               print("y  ",end="")
       else:
           print("n",end="")
   print()
   print("掃描完畢")
   if len(ID_list):
       print("ID為 ",end="")
       for ID in ID_list:
           print(ID,end=" ")
   print()
   return ID_list

  #用來發送讀取TOFsence指令的函數(為了未來多工運作，發送前不清空接收緩存)
def ask(TOFsence_ser,ID):
    ask = bytearray(b"\x57\x10\xff\xff\x00\xff\xff\x63")    #ask指令\x00為ID，\x63為校驗碼=0x63(99)+ID
    ask[4] = ID    #詢問指令中的ID
    ask[7] = (99+ID)%256    #因為只有ID會變，所以校驗和其他先算完=99，再加上ID即可
    TOFsence_ser.write(ask)

  #用來讀取TOFsence回應的函數
def read(TOFsence_ser):
    data={"id":-1}
    if TOFsence_ser.in_waiting >= 16:
        if TOFsence_ser.read(1) == b'\x57':    #讀取到幀頭
            bytedata = [0x57]
            bytedata.extend(TOFsence_ser.read(15))
            if (sum(bytedata[:15]))%256 == bytedata[15] and bytedata[1]==0x00:  #檢查校驗及功能
                #返回 57   00  FF   10 58 E6 00 00  6A 07 00  04   00 00     FF  18
                #    幀頭 功能 保留 id 4byte系统时间 3byte距離 狀態 2byte品質 保留 校驗
                #複數byte合成的參數，低位在前
                data["id"] =bytedata[3]
                data["systime"] = nbyte2int(bytedata[4:8])
                data["distance"] = nbyte2int(bytedata[8:11])
                data["status"] = bytedata[11]
                data["quality"] = nbyte2int(bytedata[12:15])
    return data

  #將小端在前的byte組轉成int
def nbyte2int(data_list):
    data = 0
    for index, byte in enumerate (data_list):
        data += byte*16**(2*index)
    return data


def help_():
    print('副程式包 TOFSense_concatenate\n\
讀取TOFsence的UART串聯，此時模組應工作於UART被動模式\n\
\n\
功能:\n\
IDscan(TOFsence_ser)    掃描ID=0~255的TOFsence(藉由發送與讀取檢查有無反應)\n\
                                 返回一個ID數字的list\n\
ask(TOFsence_ser,ID)    對指定的ID發送讀取指令，無返回\n\
read(TOFsence_ser)      讀取序列埠暫存中的資料並按照TOFsence的回傳數據剖析\n\
                        返回一個字典，有以下等key，值皆為int，當讀取失敗時傳回字典{"id":-1}\n\
                        "id" "systime" "distance" "status" "quality"\n\
nbyte2int(data_list)    給予一個項目值為0~255地的list，以大端在前進行合併\n\
                        返回一個int\n\
dist_stat               一個狀態代號(數值)對應解釋(中文字串)的字典')