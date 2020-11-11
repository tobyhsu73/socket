# -*- coding: utf-8 -*-
"""
副程式包  serial_select
讓使用者選擇序列埠及鮑率(電腦用)

功能:
input_COMport()  掃瞄並列出電腦的USB裝置，請使用者選擇(可以輸入數字，大小寫的com)
                 返回字串"COMn"  n為數字
input_Baud()  請使用者輸入鮑率，並返回填入的數字

"""
import serial.tools.list_ports

    #----------輸入COM port----------
def input_COMport():
    print("請選擇COM Ports")
    #列出裝置中可選的USB
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        print(p)
    COM_PORT = input("COM Ports= ")    # 輸入通訊埠名稱
    COM_PORT = COM_PORT.upper()    #小寫轉大寫
    if 'COM' in COM_PORT:   # 使用in運算子檢查
        pass 
    else:
        COM_PORT = "COM"+COM_PORT
        print("已選擇",COM_PORT)
    return COM_PORT

  #----------輸入鮑率----------
def input_Baud():
    Baud = input("請輸入鮑率\nBaud Rate = ")
    Baud = int(Baud)
    return Baud


def help_():
    print('副程式包  serial_select\n\
讓使用者選擇序列埠及鮑率(電腦用)\n\
\n\
功能:\n\
input_COMport()  掃瞄並列出電腦的USB裝置，請使用者選擇(可以輸入數字，大小寫的com)\n\
                 返回字串"COMn"  n為數字\n\
input_Baud()     請使用者輸入鮑率，並返回填入的數字') 