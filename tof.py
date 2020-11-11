# -*- coding: utf-8 -*-
"""
Created on Sat Oct 31 14:24:25 2020

@author: willy

鮑率115200 讀取TOFSence UART被動模式

         0  1  3  4  5      6  7  8
查詢指令 57 10 FF FF 00(ID) FF FF 63(校驗)  #ID為0
查詢指令 57 10 FF FF 10(ID) FF FF 73(校驗)  #ID為0x10
      0    1   2    3  4  5  6  7  8  9  10  11   12 13     14  15
返回 57   00  FF   10 58 E6 00 00  6A 07 00  04   00 00     FF  18
    幀頭 功能 保留 id 4byte系统时间 3byte距離 狀態 2byte品質 保留 校驗
"""
#引用模組、套件
import serial  # 引用pySerial模組
import serial.tools.list_ports
import time

#輸入固定參數
ask0 = bytearray(b"\x57\x10\xff\xff\x00\xff\xff\x63")    #ask指令\x00為ID，\x63為校驗碼=0x63(99)+ID
askid = 4    #ID的索引
askcheck = 7    #校驗的索引
readid = 3
TOFsence_dist_stat = {0:"有效", 1:"標準差偏大", 2:"低信號強度", 4:"相位出界",\
                      5:"HW或VCSEL出现故障", 7:"相位不匹配", 8:"內部算法下溢",\
                      14:"測量距離無效"}  #距離狀態指示

#自訂函數
  #輸入COM port 返回值為 "COMn" n為數字
def input_COMport():
    print("請選擇COM Ports")
    #列出裝置中可選的USB
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        print(p)
    #選擇序列埠
    COM_PORT = input("COM Ports= ")    # 輸入通訊埠名稱
    COM_PORT = COM_PORT.upper()    #小寫轉大寫
    if 'COM' in COM_PORT:   # 使用in運算子檢查
        pass 
    else:
        COM_PORT = "COM"+COM_PORT
        print("已選擇",COM_PORT)
    return COM_PORT

  #輸入鮑率
def input_Baud():
    Baud = input("請輸入鮑率\nBaud Rate = ")
    Baud = int(Baud)
    return Baud

"""
  #輸入在線上的TOFsence的id  #可用程式掃描的方式取得ID
def input_TOFsenceID():
    print('此為UART查詢模式用，請輸入所需TOFsence的"10進位"id\n輸入完畢請輸入OK')
    flag = 0
    ID_list=[]
    while flag == 0:
        ID_list.append(input("ID="))
        if ID_list[-1].upper() == "OK":
            ID_list.pop()
            break
    for index, data in enumerate (ID_list):
        ID_list[index] = int(data)
    return ID_list
"""

  #掃描可用的TOFsence的ID
def TOFsence_IDscan(TOFsence_ser):
   print("掃描TOFsence ID中  稍等約10秒")
   ID_list = []
   for ID in range(256):
       print(ID,end="")
       TOFsence_ser.flushInput()
       ask = ask0
       ask[askid] = ID
       ask[askcheck] = (99+ID)%256
       TOFsence_ser.write(ask)
       time.sleep(0.05)
       if TOFsence_ser.in_waiting == 16:    #如果接收到符合長度的數據
           data = TOFsence_ser.read(16)
           if (sum(data[:15]))%256 == data[15] and data[readid ] == ID:    #檢查校驗
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
def ask_TOFsence(TOFsence_ser,ID):
    ask = ask0
    ask[askid] = ID
    ask[askcheck] = (99+ID)%256    #因為只有ID會變，所以校驗和其他先算完=99，再加上ID即可
    TOFsence_ser.write(ask)

  #用來讀取TOFsence回應的函數
def read_TOFsence(TOFsence_ser):
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
            
def nbyte2int(data_list):    #將小端在前的byte組轉成int
    data = 0
    for index, byte in enumerate (data_list):
        data += byte*16**(2*index)
    return data




#主程式 
COM_PORT = input_COMport()
BAUD_RATES = input_Baud()    # 設定傳輸速率
#TOFsenceID = input_TOFsenceID()    #改以掃描方式取得
ser = serial.Serial(COM_PORT, BAUD_RATES)   # 初始化序列通訊埠
print("連線成功!  可按 ctrl + C 關閉程式\n")
time.sleep(0.1)
ser.flushInput()  #清空接收緩存

try:
    ID_list = TOFsence_IDscan(ser)  #自動取得線上的感測器ID
    data = {}
    while True:
        for ID in ID_list:
            ask_TOFsence(ser,ID)    #發送偵測指令
            time.sleep(1)
            
            #print("ser.in_waiting",ser.in_waiting)    #顯示緩存中的字節數
            gotbata = read_TOFsence(ser)
            data[gotbata["id"]] = gotbata    #依照ID存入
            if gotbata["id"] !=-1:
                print("ID:",gotbata["id"],"  distance =",gotbata["distance"])
            gotbata = read_TOFsence(ser)
            data[gotbata["id"]] = gotbata    #依照ID存入
            if gotbata["id"] !=-1:
                print("ID:",gotbata["id"],"  distance =",gotbata["distance"])
            
except KeyboardInterrupt:
    ser.close()    # 清除序列通訊物件
    print('斷開連線\n再見！')
except:
    ser.close()    # 清除序列通訊物件
    print('發生錯誤，斷開連線')


