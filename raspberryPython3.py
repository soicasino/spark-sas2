#011A
#011A00000000C3FC01
#011A000014513E4D01

#27: Legacy EFT pool
#6B: EGT Long Poll

#EFT POLLS
#22-25, 29, 62,63,64,65,67,69

#EFT'te surekli artirmak gerekiyor ID'yi

#Kredi Yuklemek:
#TX>= 01 69 04 00 12 34 56 78 5F 13
#TX>= 01 69 05 00 00 00 01 00 5C 69
#TX>= 01 69 06 00 00 00 01 00 21 65

#Request for cashout credit amount
#01 66 00 59 6B



#sudo pip install --upgrade pip
#sudo pip install cython
#sudo pip install pymssql --upgrade
#Kahverengi: RX    - Onlarin TX'i
#Kirmizi: TX - Onlarin RX
#Turuncu: GND
#01 1A 00 00 00 01 CRC (4AED) 1 Kredi ac.

#nextion: 7179
#sasport: 7275
#billacceptor: 7881


#yapilacaklar....
#oyun basladiktan sonra, kart cikartma islemi en azindan 4 sn sonra olsun.

#asagidaki mesaj gelince iyice sapitiyor. sas portu onlarca kez acip kapatsak bile birsey olmuyor
#01720200800D6DFC
#01720201026BD6C3.. allright!
#Raspberry

#sorular
#Cashout to Host Control: Soft - Hard - Host controlled farklari

#Cihazin destekledigi zimbirtilar. Ornegin Jackpot vs.
#sas:01A00000CRC
#Asagidaki sorgu Jackpotu kabul etmeyenleri bulmak icin
#SELECT MacAddress FROM T_ReceivedMessages where ReceivedMessage like '01A00000_0%'
#1 Lari Jackpot - Bonus (Kilitleme yok)
#sas:0172350000100000000100000000000000000000000301000000000000000000000000000000000000000000000002323008182017003000CRC

#1 Lari Jackpot - Bonus (Kilitleme olacak)
#sas:0172350000110000000100000000000000000000000301000000000000000000000000000000000000000000000002323008182017003000CRC


#Kart cikartma prosedurleri
#-Cashout basilinca
#	Komut_CollectButtonProcess
#		Card_RemoveCustomerInfo
#problemsiz
#-Kart cikartilinca
#	CardIsRemoved
#		Card_RemoveCustomerInfo


#from cefpython3 import cefpython as cef


#from pycallgraph import PyCallGraph
#from pycallgraph.output import GraphvizOutput



try:
    import wx
    from wx import html2
    WX_HTML2_AVAILABLE = True
    WX_AVAILABLE = True
except ImportError:
    print("[WARNING] wxPython not available or incomplete installation")
    print("[INFO] HTML GUI will be disabled")
    WX_HTML2_AVAILABLE = False
    WX_AVAILABLE = False
    wx = None
#import codecs

import webview
import gc

import math
import psutil
import signal

import serial
import re
import pymssql
#import _mssql
try:
    import psycopg2
    import psycopg2.extras
    import uuid
    POSTGRESQL_AVAILABLE = True
except ImportError:
    print("PostgreSQL dependencies not available")
    POSTGRESQL_AVAILABLE = False

# Missing imports for Raspberry Pi compatibility
try:
    import multiprocessing as mp
except ImportError:
    print("multiprocessing module not available")
    mp = None

try:
    from cefpython3 import cefpython as cef
except ImportError:
    print("CEF Python not available - using fallback")
    cef = None

# Initialize variables that might be undefined
wx = None
MyBrowser = None
struct = None
QtCore = None
import os
import array
import sys
import datetime
import socket
import threading
from threading import Timer,Thread,Event
import time
import sys, getopt

from sys import stdin
import configparser as ConfigParser
from decimal import Decimal

from uuid import getnode as get_mac
import platform
import random
from binascii import unhexlify
import subprocess

import hashlib

from crccheck.crc import CrcKermit

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QImage, QPalette, QBrush, QFont
from PyQt5.QtWidgets import *

# noinspection PyUnresolvedReferences
#from PyQt4.QtCore import *

QString = str

import sqlite3
try:
    conn = sqlite3.connect('asist.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE  TABLE  IF NOT EXISTS billacceptor ("billacceptorid" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL  UNIQUE ,  "machinelogid" INTEGER, "cardno" VARCHAR, "amount" DOUBLE, "amountcode" VARCHAR, "countrycode" VARCHAR, "piece" INTEGER, "issynced" INTEGER, "amountbase" DOUBLE)')
except Exception as esql:
    print("SQLite Err Init!")

import ctypes

import json

# Custom JSON encoder to handle Decimal objects
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)



import urllib as urllib2
os.putenv('DISPLAY', ':0.0')





Config = ConfigParser.ConfigParser()
ConfigFile="settings.ini"

def SaveConfigFile():
    global ConfigFile
    global Config
    cfgfile = open(ConfigFile,'w')
    Config.write(cfgfile)
    cfgfile.close()

Config.read(ConfigFile)

G_Program_LogAllSAS=0
for i in range(1, len(sys.argv)):
    print(sys.argv[i])
    if sys.argv[i]=="debugsas":
        G_Program_LogAllSAS=1
        print("DEBUG SAS LOG!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("DEBUG SAS LOG!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("DEBUG SAS LOG!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("DEBUG SAS LOG!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("DEBUG SAS LOG!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("DEBUG SAS LOG!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("DEBUG SAS LOG!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("DEBUG SAS LOG!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")


G_Machine_MachineName=""
try:
    G_Machine_MachineName=Config.get("machine","machinename")
except Exception as esql:
    print("---------")


G_Online_IsOnlinePlaying=0

G_Last_ScreenClick=datetime.datetime.now()
G_Device_IsReadyForOnlinePlaying=1
G_Device_IsForOnlinePlaying=1
if G_Device_IsForOnlinePlaying==1:
    try:
        from flask import Flask, request
        from flask_restful import Resource, Api
        from json import dumps
        from flask import request, jsonify
    except Exception as esql:
        print("Not ready for online playing")
        print("NO Flask")
        G_Device_IsReadyForOnlinePlaying=0



G_Device_AssetNo=0#Bunu cihaz acildiktan sonra sorguluyoruz.
G_Machine_GameStartEndNotifications=0
G_Machine_IsAutoNextVisit=0
G_Machine_CalcBetByTotalCoinIn=0
G_CardLastDate=datetime.datetime.now()
G_NetworkLastDate=datetime.datetime.now()
G_SASLastDate=datetime.datetime.now() + datetime.timedelta(minutes=1)
G_Machine_LastCardreaderTime=datetime.datetime.now()+ datetime.timedelta(minutes=1)
G_Machine_LastBillAcceptorTime=datetime.datetime.now()+ datetime.timedelta(minutes=1)
G_LastCashoutPressedDate=datetime.datetime.now()- datetime.timedelta(minutes=30)
G_LastAFTOperationDate=G_LastCashoutPressedDate
G_Machine_IsBonusCashable=0
G_LastMeterDate=datetime.datetime.now()


G_DebugPoint=0
LinuxVersion=1
try:
    import distro
    if str(distro.linux_distribution()).find("Ubuntu") != -1:
        LinuxVersion=2
    print("Linux", distro.linux_distribution(), LinuxVersion)
except Exception as esql:
    LinuxVersion=1



if platform.system().startswith("Window")==False and LinuxVersion!=2:
    import RPi.GPIO as GPIO


FilePathSO="/home/soi/dev/spark-sas2/crt_288B_UR.so"
if LinuxVersion==3:
    FilePathSO="/home/soi/dev/spark-sas2/crt_288B_UR.so"



if platform.system().startswith("Window")==False:
    import termios


G_Session_IsByOnline=0


def GetAssetBinary(d):
    HexaString=hex(int(d)).split('x')[-1].upper()
    if len(HexaString)%2!=0:
        HexaString="0" + HexaString
        
    ReversedHexaString=""
    i=len(HexaString)-2
    while i>=0:
        ReversedHexaString=ReversedHexaString+HexaString[i:i+2]
        i=i-2

    while len(ReversedHexaString)<8:
        ReversedHexaString=ReversedHexaString+"0"

    #print("HexaString", HexaString)
    #print("ReversedHexaString", ReversedHexaString)
    return ReversedHexaString

def ReadAssetToInt(d):
    HexaString=d
    if len(HexaString)%2!=0:
        HexaString="0" + HexaString
        
    ReversedHexaString=""
    i=len(HexaString)-2
    while i>=0:
        #print("lan")
        ReversedHexaString=ReversedHexaString+HexaString[i:i+2]
        i=i-2

    print("Read: HexaString", HexaString)
    print("Read: ReversedHexaString", ReversedHexaString)
    print("Int Read:" , int(ReversedHexaString, 16))
    return int(ReversedHexaString, 16)


import os, fnmatch
def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result



def ExecuteLinuxCommand(command):
    #print("Linux command", command)
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    return output

def ExecuteLinuxCommandWithoutPipe(command):
    process = subprocess.Popen(command)
    output = process.communicate()[0]
    return output


IsKillWifi=0

try:
    if IsKillWifi==1:
        ExecuteLinuxCommand("sudo rfkill block wifi")
        ExecuteLinuxCommand("sudo rfkill block bluetooth")
except Exception as e:
    G_DebugPoint=1

try:
    #sheder
    ExecuteLinuxCommand("rm licence.hashed")
except Exception as e:
    G_DebugPoint=1

#wifi
#try:
#    ExecuteLinuxCommand("sudo rm -r /etc/wpa_supplicant/wpa_supplicant.conf")
#except Exception as e:
#    G_DebugPoint=1


IsSystemLocked=0
IsDeviceLocked=0
def Kilitle(sender):
    global IsDeviceLocked
    IsDeviceLocked=1
    print("Kilitlenecek!" , sender)
    PrintAndSetAsStatuText("Locked")
    Command="01 01 51 08"
    Command=Command.replace(" ","")
    SAS_SendCommand("kilitle",Command,0)

    SQL_Safe_InsImportantMessage("EGM is locked by Cashless System " + sender,68)

    thread1 = Thread(target = SQL_UpdDeviceIsLocked, args = (1, ))
    thread1.name="Lock"
    thread1.start()

def Ac(sender):
    print("Kilit acilacak", sender)
    global IsDeviceLocked
    IsDeviceLocked=0

    if sender!="Ready for game":
        SQL_Safe_InsImportantMessage("EGM is unlocked by Cashless System ("+sender+")",68)

    #PrintAndSetAsStatuText("UnLocked")
    
    Command="01 02 CA 3A"
    Command=Command.replace(" ","")
    
    SAS_SendCommand("ac",Command,0)
    time.sleep(0.1)
    SAS_SendCommand("ac",Command,0)

    thread1 = Thread(target = SQL_UpdDeviceIsLocked, args = (0, ))
    thread1.name="Ac"
    thread1.start()



    print("G_User_CardNo C=> ",G_User_CardNo)
    if G_Machine_DeviceTypeId==7 and len(G_User_CardNo)==0 and G_Machine_IsCanPlayWithoutCard==0:
        time.sleep(0.5)
        print("Kontrol mevcut gambee bill acceptor kapat")
        Komut_DisableBillAcceptor("Acildiginda billacceptor acilmasin -1")
        time.sleep(0.5)
        Komut_DisableBillAcceptor("Acildiginda billacceptor acilmasin -1")

    Komut_CancelBalanceLock()
    #Komut cancel balance lock



if os.name != "nt":
    import fcntl
    import struct

    def get_interface_ip(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
                                ifname[:15]))[20:24])

def get_lan_ip():



    ip="1.1.1.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip=s.getsockname()[0]

        if 2==1:
            ip = socket.gethostbyname(socket.gethostname())
            if ip.startswith("127.") and os.name != "nt":
                interfaces = [
                    "eth0",
                    "eth1",
                    "eth2",
                    "wlan0",
                    "wlan1",
                    "wifi0",
                    "ath0",
                    "ath1",
                    "ppp0",
                    ]
                for ifname in interfaces:
                    try:
                        ip = get_interface_ip(ifname)
                        break
                    except IOError:
                        pass
    except Exception as esql:
        ip="1.1.1.1"
    return ip


########################################################################
# <GUI START>-----------------------------------------------------------

GUI_Static_WelcomeText="Please insert your card "

Screen_Width=480
Screen_Height=320

#drgt
Screen_Width=640
Screen_Height=240

Screen_Width=800
Screen_Height=480


Screen_Fontsize1=15
Screen_Fontsize2=20
if Screen_Width==800 and Screen_Height==480:
    Screen_Fontsize1=25
    Screen_Fontsize2=35

Screen_FontWeight1=31
if Screen_Fontsize1==25:
    Screen_FontWeight1=50


G_SAS_LastAFTOperation=""



########################################################################
# <HTML GENEL START>-----------------------------------------------------------

LastJS_Commands = []
def DoExecuteJS(textcmd=""):
    global G_Machine_ScreenTypeId
    global LastJS_Commands

    if G_Online_IsOnlinePlaying==1:
        return

    if G_Machine_ScreenTypeId==0:
        return

    try:
        #print("*********************JS textcmd", textcmd)
        if len(LastJS_Commands)>30:
            while len(LastJS_Commands)>20:
                del LastJS_Commands[0]
                #print("Silindi")

        #LastJS_Commands.append(textcmd[0:40])
    except Exception as esql:
        print("Execute JS Del Err", textcmd)

    try:
        window.evaluate_js(textcmd)
    except Exception as esql:
        print("Execute JS Command error", textcmd)


def timeout(func, args = (), kwds = {}, timeout = 1, default = None):
    pool = mp.Pool(processes = 1)
    result = pool.apply_async(func, args = args, kwds = kwds)
    try:
        val = result.get(timeout = timeout)
    except mp.TimeoutError:
        pool.terminate()
        return default
    else:
        pool.close()
        pool.join()
        return val

def ExecuteJS(textcmd):
    #print(timeout(DoExecuteJS, args = (textcmd,), timeout = 2, default = 'Sayonara'))
    ThreadName="ExJS"
    try:
        ThreadName=ThreadName + textcmd[0:22]
    except Exception as esql:
        print("SQLite Err Init!")

    thread1 = Thread(target = DoExecuteJS, args = (textcmd, ))
    thread1.name=ThreadName
    thread1.start()

def DecodeHTMLChars(para):
    para=para.replace("'","&rsquo;")
    para=para.replace("\"","&rdquo;")
    return para

def DecodeHTML(para):
    para=para.replace("'","\\'")
    para=para.replace("\"","\\\"")
    return para

def ExecuteJSFunction(function, para1):
    para1=DecodeHTML(para1)
    ExecuteJS(function + "('"+para1+"')")
    #main_window.cef_widget.browser.ExecuteFunction(first,second)

def ExecuteJSFunction2(function, para1, para2):
    para1=DecodeHTML(para1)
    para2=DecodeHTML(para2)
    ExecuteJS(function + "('"+str(para1)+"','"+str(para2)+"')")

def ExecuteJSFunction3(function, para1, para2, para3):
    para1=DecodeHTML(para1)
    para2=DecodeHTML(para2)
    para3=DecodeHTML(para3)
    ExecuteJS(function + "('"+str(para1)+"','"+str(para2)+"','"+str(para3)+"')")
    #main_window.cef_widget.browser.ExecuteFunction(first,second,third)

def ExecuteJSFunction4(function, para1, para2, para3, para4):
    para1=DecodeHTML(para1)
    para2=DecodeHTML(para2)
    para3=DecodeHTML(para3)
    para4=DecodeHTML(para4)
    ExecuteJS(function + "('"+para1+"','"+para2+"','"+para3+"','"+para4+"')")
    #wx.CallAfter(WXBrowser.RunScript,function + "('"+para1+"','"+para2+"','"+para3+"','"+para4+"')")

def ExecuteJSFunction5(function, para1, para2, para3, para4, para5):
    para1=DecodeHTML(para1)
    para2=DecodeHTML(para2)
    para3=DecodeHTML(para3)
    para4=DecodeHTML(para4)
    para5=DecodeHTML(para5)
    ExecuteJS(function + "('"+para1+"','"+para2+"','"+para3+"','"+para4+"','"+para5+"')")

def ExecuteJSFunction7(function, para1, para2, para3, para4, para5, para6, para7):
    para1=DecodeHTML(para1)
    para2=DecodeHTML(para2)
    para3=DecodeHTML(para3)
    para4=DecodeHTML(para4)
    para5=DecodeHTML(para5)
    para6=DecodeHTML(para6)
    para7=DecodeHTML(para7)
    ExecuteJS(function + "('"+para1+"','"+para2+"','"+para3+"','"+para4+"','"+para5+"','"+para6+"','"+para7+"')")

def ExecuteJSFunction12(function, para1, para2, para3, para4, para5, para6, para7, para8, para9, para10, para11, para12):
    para1=DecodeHTML(para1)
    para2=DecodeHTML(para2)
    para3=DecodeHTML(para3)
    para4=DecodeHTML(para4)
    para5=DecodeHTML(para5)
    para6=DecodeHTML(para6)
    para7=DecodeHTML(para7)
    para8=DecodeHTML(para8)
    para9=DecodeHTML(para9)
    para10=DecodeHTML(para10)
    para11=DecodeHTML(para11)
    para12=DecodeHTML(para12)
    ExecuteJS(function + "('"+para1+"','"+para2+"','"+para3+"','"+para4+"','"+para5+"','"+para6+"','"+para7+"','"+para8+"','"+para9+"','"+para10+"','"+para11+"','"+para12+"')")
# </HTML GENEL START>-----------------------------------------------------------
########################################################################



########################################################################
# <HTML GUI START>-----------------------------------------------------------
# GLOBALS
PYQT4 = False
PYQT5 = False


PYQT4 = True

# Fix for PyCharm hints warnings when using static methods
#WindowUtils = cef.WindowUtils()

# Platforms
WINDOWS = (platform.system() == "Windows")
LINUX = (platform.system() == "Linux")
MAC = (platform.system() == "Darwin")

# Configuration
WIDTH = 800
HEIGHT = 480


def HTMLGUI():
    #check_versions()
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    settings = {}
    if MAC:
        # Issue #442 requires enabling message pump on Mac
        # in Qt example. Calling cef.DoMessageLoopWork in a timer
        # doesn't work anymore.
        settings["external_message_pump"] = True

    cef.Initialize(settings)
    app = CefApplication(sys.argv)
    main_window = MainWindow()
    if WINDOWS==True:
        main_window.show()
    else:
        main_window.showFullScreen()#FullScreen
    main_window.activateWindow()
    main_window.raise_()
    app.exec_()



    if not cef.GetAppSetting("external_message_pump"):
        app.stopTimer()
    del main_window  # Just to be safe, similarly to "del app"
    del app  # Must destroy app object before calling Shutdown
    cef.Shutdown()


def check_versions():

    # CEF Python version requirement
    assert cef.__version__ >= "55.4", "CEF Python v55.4+ required to run this"






class LoadHandler(object):
    def __init__(self, navigation_bar):
        self.initial_app_loading = True
        self.navigation_bar = navigation_bar

    def OnLoadingStateChange(self, **_):
        self.navigation_bar.updateState()

    def OnLoadStart(self, browser, **_):
        self.navigation_bar.url.setText(browser.GetUrl())
        if self.initial_app_loading:
            self.navigation_bar.cef_widget.setFocus()
            # Temporary fix no. 2 for focus issue on Linux (Issue #284)
            if LINUX:
                print("[qt.py] LoadHandler.OnLoadStart:"
                      " keyboard focus fix no. 2 (Issue #284)")
                browser.SetFocus(True)
            self.initial_app_loading = False


class FocusHandler(object):
    def __init__(self, cef_widget):
        self.cef_widget = cef_widget

    def OnSetFocus(self, **_):
        pass

    def OnGotFocus(self, browser, **_):
        # Temporary fix no. 1 for focus issues on Linux (Issue #284)
        if LINUX:
            print("[qt.py] FocusHandler.OnGotFocus:"
                  " keyboard focus fix no. 1 (Issue #284)")
            browser.SetFocus(True)


# </HTML GUI START>-----------------------------------------------------------
########################################################################

#<GUI START>----------------------------------------


        


#</MAIN SCREEN BUTTONS>########################################################################################################










# </GUI START>-----------------------------------------------------------        
########################################################################



def Decode2Hex(input):
    return bytearray.fromhex(input)







def CalcLRC(input):
    input=Decode2Hex(input)
    lrc = 0
    i = 0
    message = bytearray(input)
    for b in message:
        if(i == 0):
            pass
        else:
            lrc ^= b
        i+=1;
    return lrc

def CalcLRCByte(message):
    lrc = 0
    i = 0

    for b in message:
        if(i == 0):
            pass
        else:
            lrc ^= b
        i+=1;
    return lrc



def AddLeftString(text, eklenecek,kacadet):
    while (kacadet>0):
        text=eklenecek+text
        kacadet=kacadet-1

    return text


def FillLeftZeroIfSingular(str):
    retdata=str

    if len(retdata)%2==1:
        retdata="%s%s" % ("0", retdata)

    return retdata


def StrLengthCeiling(str):
    
    retdata=len(str)

    if retdata%2==1:
        retdata=retdata+1

    retdata=retdata/2

    return retdata


def HEXNumberToInt(test1):
    return bytes.fromhex(test1).decode('utf-8')


def AddLeftBCD(numbers, leng):
    
    numbers=int(numbers)

    retdata=str(numbers)

    if len(retdata)%2==1:
        retdata="%s%s" % ("0", retdata)


    countNumber=len(retdata)/2 #1250 4
    kalan=(leng-countNumber)        #5-4 = 1

    retdata=AddLeftString(retdata, "00",kalan)

    return retdata




IsGUIFullScreen=0
GUI_CurrentPage=""

IsRealTimeReportingEnabled=1


IsSASPortOpened=0
IsCardReaderOpened=0


IsAvailableForCashoutButton=1
G_TrustBalance=datetime.datetime.now()
G_LastGameEnded=datetime.datetime.now()
G_LastGameStarted=datetime.datetime.now()
G_LastCardExit=datetime.datetime.now()
G_LastCardEnter=datetime.datetime.now()
G_LastGame_Action=datetime.datetime.now()
G_SessionStarted=datetime.datetime.now()
G_LastGame_IsFinished=1
G_Machine_ReservationDate=datetime.datetime.now() - datetime.timedelta(minutes=30)
G_Machine_ReservationCard=""
G_Machine_ReservationCustomername=""
G_Machine_ReservationOK=""


G_Machine_WagerBonusFactors=[]
G_Machine_WagerName=""
G_Machine_WagerIndex=0


IsGUIEnabled=0

#1: Normal, 2: Nextion, 3: HTML - 4: 800 HTML, 5: TEK SAYFA 
IsGUI_Type=0



IsWaitingAdminScreen=0

#1: Inturist
#2: Salamis
#3: Cashoutsuz
#4: Ambassador
#5: Savoy
#6: Malpas
#7: Corona
#8: Golden Palace
#9: Lords Palace
#10 Senator
#11: Golden Atlantik
#12: Viva
G_CasinoId=1

G_Machine_DeviceId=0
G_Machine_AssetNo=0

G_Machine_CurrencyId=0
G_Casino_CurrencyId=0
G_Machine_CurrencyRate=1

G_Machine_IsBonusGives=0

G_Machine_SASVersion="0"
G_Machine_PayBackPerc=Decimal(0)

G_Machine_Balance=Decimal(0)
G_Machine_Promo=Decimal(0)

#1: promo yaridan gitsin
G_Machine_CasinoPromoType=0


G_Machine_CardReaderType=1
G_Machine_CardReaderModel=""#Eject
if len(find('crt*.so', '/home/pi'))==0:
    G_Machine_CardReaderType=2
    print("CHINA CARD READER!!!!")




G_Machine_Currency="TRY"
G_Casino_Name="TEST"

def getMAC(interface='eth0'):
    # Return the MAC address of the specified interface
    try:
        if LinuxVersion==1:
            str = open('/sys/class/net/%s/address' %interface).read().upper()
        if LinuxVersion==2:
            from uuid import getnode as get_mac
            str = get_mac()
            str= ':'.join(("%012X" % str)[i:i+2] for i in range(0, 12, 2))
    except:
        str = "00:00:00:00:00:00"
    return str[0:17]



G_Machine_Mac=getMAC("eth0")
if platform.system().startswith("Window")==True:
    G_Machine_Mac=':'.join(("%012X" % get_mac())[i:i+2] for i in range(0, 12, 2))
G_Machine_MacAddress=G_Machine_Mac
try:
    assetNo=ReadAssetToInt(Config.get('sas','assetnumber'))
    G_Machine_Mac=str(assetNo)
    if G_Machine_Mac=="1" or len(G_Machine_Mac)==0:
        G_Machine_Mac=G_Machine_MacAddress
    print("G_Machine_Mac", G_Machine_Mac)
except:
    print("Exception G_Machine_Mac")




G_Machine_Ready=1

G_Machine_GameStartEndBalance=0



G_Machine_IsRulet=0

#1: AFT: Traditional, 2: AFT Fast  3: Online 4: EFT
G_Machine_ProtocolType=1

#0: Manuel, 1: Novomatic, 2: EGT, 3: IGT, 4: Octovian, 5:Inturist Alphastreet/Zuum roulette, 
#6: Megajack Casino Tech, 7: Gambee, 8: Bally, 9: Zoom 10: Apex (GameLocked problemliler), 11: Interblock
G_Machine_DeviceTypeId=8
try:
    G_Machine_DeviceTypeId=int(Config.get("machine","devicetypeid"))
except Exception as esql:
    print("---------")

print("G_Machine_DeviceTypeId", G_Machine_DeviceTypeId)

G_Machine_IsPromoAccepts=0

G_Machine_DeviceTypeGroupId=0


G_AutoCashoutTime=10


G_Machine_NoActivityTimeOutForBillAcceptor=0

G_Machine_NoActivityTimeForCashoutMoney=0
G_Machine_NoActivityTimeForCashoutSeconds=0

G_Machine_TicketPrinterTypeId=0
G_Machine_BillAcceptorTypeId=0
G_Casino_IsAssetNoAlwaysOne=0
G_Machine_NewGamingDay=0
G_Machine_IsLockedByAdmin=0
G_Machine_ScreenTypeId=8
G_Machine_ScreenRotate=0
G_Machine_CashInLimit=0
G_Machine_IsPartialTransfer=0
G_Machine_IsRecordAllSAS=0
G_Machine_IsCanPlayWithoutCard=0
G_Machine_IsCashless=1

G_Machine_NotifyWonLimit=999999
G_Machine_JackpotId=0
G_Machine_JackpotFactor=Decimal(1)

#Lock only on roulette
G_Machine_LockBeforeAFT=0



G_SelectedGameId=0
Log_TotalCoinInMeter=Decimal(0)
G_SelectedGameName=""



G_Machine_AdminCards=""

G_Machine_Statu="Started! Ready!!"



G_Machine_CardReaderPort='/dev/ttyUSB'


G_Machine_IsSASPortFound=0
G_Machine_IsNextionPortFound=0
G_Machine_IsBillacceptorPortFound=0

G_Machine_SASPort='/dev/ttyUSB0'#usb 1-1.3: FTDI USB Serial Device converter now attached to ttyUSB1
G_Machine_SASPort="COM2"
G_Machine_NextionPort='/dev/ttyUSB1'#usb 1-1.1.3: pl2303 converter now attached to ttyUSB2
G_Machine_BillacceptorPort="/dev/ttyUSB2"#usb 1-1.1.2: pl2303 converter now attached to ttyUSB3
G_Machine_USB_Ports=[]

def FindPorts(sender):
#<Find ports>--------------------------------------------------------------
    global G_Machine_USB_Ports
    try:
        G_Machine_USB_Ports=[]
        
        if platform.system().startswith("Window")==True:
            portDict =	{
                "portNo": "COM4",
                "isUsed": 0,
                "deviceName": ""
                }
            G_Machine_USB_Ports.append(portDict)

        if LinuxVersion>0 and LINUX==True:
            #output = subprocess.check_output("dmesg | grep ttyUSB", shell=True)
            output = str(subprocess.check_output("ls /dev/ttyUSB*", shell=True))

            output=output.replace("b'","").replace("'","").replace("\\n","|")

            print("output", output, type(output))
            for row in output.split('|'):
                if len(row)==0:
                    break

                deviceName=""
                isUsed=0
                PortNo=row#'/dev/' + row.split(" ")[len(row.split(" "))-1]


                try:
                    if sender!="sas" and sasport.port==PortNo and sasport.isOpen()==True:
                        isUsed=1
                        deviceName="sas"

                except Exception as e:
                    print("Is Used SAS")


                try:
                    if sender!="card" and cardreader.port==PortNo and cardreader.isOpen()==True:
                        isUsed=1
                        deviceName="cardreader"
                except Exception as e:
                    print("Is Used cardreader")

                try:
                    if G_Machine_BillAcceptorTypeId>0:
                        if sender!="bill" and billacceptorport.port==PortNo and billacceptorport.isOpen()==True:
                            isUsed=1
                            deviceName="billacceptorport"
                except Exception as e:
                    print("Is Used billacceptorport")


                if sender=="all":
                    isUsed=0


                if len(PortNo)>0:# and PortNo not in G_Machine_USB_Ports:
                    portDict =	{
                        "portNo": PortNo,
                        "isUsed": isUsed,
                        "deviceName": deviceName
                        }
                    G_Machine_USB_Ports.append(portDict)

        print("G_Machine_USB_Ports", G_Machine_USB_Ports, len(G_Machine_USB_Ports))
    except Exception as e:
        print("Port bulma error...")
        time.sleep(1)
#</Find ports>--------------------------------------------------------------
FindPorts("all")


if platform.system().startswith("Window")==True:
    portDict =	{
        "portNo": "COM4",
        "isUsed": 0,
        "deviceName": ""
        }
    G_Machine_USB_Ports.append(portDict)


#</Find ports>--------------------------------------------------------------


#<CARD READER RENKLI>---------------------------------


def CardReader_ColorCommand(cmd):
    try:
        if G_Machine_CardReaderModel=="Eject" or G_Machine_CardReaderType==1:
            return

        thread1 = Thread(target = CardReaderCommand, args = (cmd, ))
        thread1.name="CardR1"
        thread1.start()
    except Exception as e:
        print("Card reader error")

def CardReader_CardExitStart():
    # white LED always blink
    #CardReader_ColorCommand("02000580313702050385")
    #cok hizli CardReader_ColorCommand("02000580313701FF037C")
    CardReader_ColorCommand("020005803137026403E4")

def CardReader_CardProblem():
    # red LED always blink
    CardReader_ColorCommand("020005803131020A038C")

def CardReader_WaitingNewDay():
    # red Cyan always blink
    CardReader_ColorCommand("020005803136056403E2")


def CardReader_CardExitEnd():
    # enable gradient
    CardReader_ColorCommand("020005803200000003B6")


def CardReader_CardInsertStart():
    #255 Yesil
    CardReader_ColorCommand("020005803132023203B7")

def CardReader_CardInsertEnd():
    #Renksiz yap
    CardReader_ColorCommand("020005803300000003B7")

def CardReader_EjectCard():
    SQL_Safe_InsImportantMessage("Card ejected",68)
    thread1 = Thread(target = CardReaderCommand, args = ("02000232300301", ))
    thread1.name="EjCard"
    thread1.start()
    #CardReader_ColorCommand("02000232300301")
#</CARD READER RENKLI>---------------------------------

#<BILL ACCEPTOR HELPER>------------------------------------------------------------------------
billacceptorport = serial.Serial()



Mei_LastAckNack=""
def GetMeiACK():
    global Mei_LastAckNack
    if Mei_LastAckNack=="10" or len(Mei_LastAckNack)<2:
        Mei_LastAckNack="11"
    else:
        Mei_LastAckNack="10"
    

    return Mei_LastAckNack


G_LastBillAcceptor_AcKapaCommand=datetime.datetime.now()
IsBillacceptorOpen=0
def BillAcceptor_Inhibit_Open():
    global G_LastBillAcceptor_AcKapaCommand
    global IsBillacceptorOpen
    IsBillacceptorOpen=1

    LastBillAcDiff=(datetime.datetime.now()-G_LastBillAcceptor_AcKapaCommand).total_seconds()

    G_LastBillAcceptor_AcKapaCommand=datetime.datetime.now()
    if G_Machine_BillAcceptorTypeId==1:
        SendBillAcceptorCommand("FC06C30004D6")
    if G_Machine_BillAcceptorTypeId==2:
        SendBillAcceptorCommand(GetMEIMsgCRC("02 08 "+GetMeiACK()+" 7F 1C 10 03 6A"))


def BillAcceptor_Inhibit_Close():
    global G_LastBillAcceptor_AcKapaCommand
    global IsBillacceptorOpen
    IsBillacceptorOpen=0

    LastBillAcDiff=(datetime.datetime.now()-G_LastBillAcceptor_AcKapaCommand).total_seconds()

    G_LastBillAcceptor_AcKapaCommand=datetime.datetime.now()
    if G_Machine_BillAcceptorTypeId==1:
        #BillAcceptorCommand("FC06C3018DC7")
        SendBillAcceptorCommand("FC06C3018DC7")
    if G_Machine_BillAcceptorTypeId==2:
        SendBillAcceptorCommand(GetMEIMsgCRC("02 08 "+GetMeiACK()+" 00 1C 10 03 14"))

    print("Disable bill acceptor")

def BillAcceptor_Reset():
    if G_Machine_BillAcceptorTypeId==1:
        BillAcceptorCommand("FC 05 40 2B 15")
    if G_Machine_BillAcceptorTypeId==2:
        #BillAcceptorCommand("02 08 60 7F 7F 7F 03 17")
        #Eskisi BillAcceptorCommand("02 08 60 7F 7F 7F 03 17 02 08 10 7F 1C 12 03 69")
        BillAcceptorCommand("02 08 60 7F 7F 7F 03 17")




def BillAcceptor_Reject(sender):
    SQL_Safe_InsImportantMessage("Bill is rejected " + sender,80)
    print("****** REJECT YAP ******")
    if G_Machine_BillAcceptorTypeId==1:
        BillAcceptorCommand("FC 05 43 B0 27")
    if G_Machine_BillAcceptorTypeId==2:
        BillAcceptorCommand(GetMEIMsgCRC("02 08 "+GetMeiACK() +" 7F 5C 10 03 00"))


Count_StatusCheck=0
def BillAcceptor_Status_Check():
    global Count_StatusCheck
    Count_StatusCheck=Count_StatusCheck+1

    if G_Machine_BillAcceptorTypeId==1:
        BillAcceptorCommand("FC 05 11 27 56")

    if G_Machine_BillAcceptorTypeId==2:
        
        if IsBillacceptorOpen==1:

            BillAcceptorCommand(GetMEIMsgCRC("02 08 "+GetMeiACK()+" 7F 1C 10 03 00"))


            #Sondan ucuncuyu 10. Ama barkod icin 12 yapicaz.
            #if Count_StatusCheck%2==0:
            #    BillAcceptorCommand(GetMEIMsgCRC("02 08 "+GetMeiACK()+" 7F 1C 12 03 6B"))
            #else:
            #    BillAcceptorCommand(GetMEIMsgCRC("02 08 "+GetMeiACK()+" 7F 1C 12 03 6A"))


            

            #ACK=GetMeiACK()
            #LASTCRC="6B"
            #if ACK=="11":
            #    LASTCRC="6A"
            #if Count_StatusCheck%2==0:
            #    BillAcceptorCommand(GetMEIMsgCRC("02 08 "+ACK+" 7F 1C 10 03 " + LASTCRC))
            #else:
            #    BillAcceptorCommand(GetMEIMsgCRC("02 08 "+ACK+" 7F 1C 10 03" + LASTCRC))
            

            #Auto Stack:                                    02 08 10 7F 1C 10 03 6B 
        if IsBillacceptorOpen==0:
            BillAcceptorCommand(GetMEIMsgCRC("02 08 "+GetMeiACK()+" 00 1C 10 03 00"))

            #if Count_StatusCheck%2==0:
            #    BillAcceptorCommand(GetMEIMsgCRC("02 08 "+GetMeiACK()+" 00 1C 10 03 14"))
            #else:
            #    BillAcceptorCommand(GetMEIMsgCRC("02 08 "+GetMeiACK()+" 00 1C 10 03 15"))

        


def BillAcceptor_Stack1():
    SQL_Safe_InsImportantMessage("Bill Stack Cmd",100)
    if G_Machine_BillAcceptorTypeId==1:
        BillAcceptorCommand("FC 05 41 A2 04")
    if G_Machine_BillAcceptorTypeId==2:
        BillAcceptorCommand(GetMEIMsgCRC("02 08 "+GetMeiACK()+" 7F 3C 10 03 00"))
        

def BillAcceptor_Currency_Assign_Req():
    if G_Machine_BillAcceptorTypeId==1:
        BillAcceptorCommand("FC 05 8A 7D 7C")
    if G_Machine_BillAcceptorTypeId==2:
        print("Bisi yapmaya gerek yok currency assign")



def BillAcceptor_ACK():
    if G_Machine_BillAcceptorTypeId==1:
        BillAcceptorCommand("FC 05 50 AA 05")




IsBillAcceptorPoolingStarted=0
BillAcceptorCommandStr=""
def BillAcceptorCommand(data):
    if IsBillAcceptorPoolingStarted==0:
        return

    if G_Online_IsOnlinePlaying==1:
        return


    data=data.replace(" ","")
    if "ACK" in data:
        data=data.replace("ACK",GetMeiACK())
    if "CRC" in data:
        data=data.replace("CRC","")
        data=GetMEIMsgCRC(data)
        print("senddata", data)


    global BillAcceptorCommandStr

    CountryTry=0
    while len(BillAcceptorCommandStr)>0:

        CountryTry=CountryTry+1
        
        if CountryTry%10==0:
            print("Please wait.. Another command is being sent to bill acceptor Old", BillAcceptorCommandStr, "Current" , data)
        
        time.sleep(0.1)


        if CountryTry>5000:
            print("break bill acceptor while commandstr")
            break


    BillAcceptorCommandStr=data




def SendBillAcceptorCommand(senddata):

    try:
        try:
            senddata=senddata.replace(" ","")
            if "ACK" in senddata:
                senddata=senddata.replace("ACK",GetMeiACK())
            if "CRC" in senddata:
                senddata=senddata.replace("CRC","")
                senddata=GetMEIMsgCRC(senddata)
                print("senddata", senddata)
        except Exception as esql1:
            print("Err")


        IsShowDebugSent=0
        if IsShowDebugSent==1:
            print("Gonderilen mesaj", senddata)


        hex_data = Decode2Hex(senddata)
        billacceptorport.write(hex_data)
        #print("Sent data", hex_data)
    except Exception as esql:
        senddata=""

def SendBillAcceptorCommandIsExist():
    global BillAcceptorCommandStr
    if len(BillAcceptorCommandStr)==0:
        return
    try:
        senddata=BillAcceptorCommandStr.replace(" ","")
        
        
        IsShowDebugSent=1
        if senddata=="020811001C100315":
            IsShowDebugSent=0
        if senddata=="020810001C100314":
            IsShowDebugSent=0
        if senddata=="0208107F1C10036B":
            IsShowDebugSent=0
        if senddata=="0208117F1C10036A":
            IsShowDebugSent=0

        IsShowDebugSent=0
        if IsShowDebugSent==1:
            print("Gonderilen mesaj", senddata)


        hex_data = Decode2Hex(senddata)
        billacceptorport.write(hex_data)
        #if G_Machine_BillAcceptorTypeId==2:
        #    billacceptorport.flush()
    except Exception as esql:
        BillAcceptorCommandStr=""
        #print("BillAcceptorCommand command sent error")
    BillAcceptorCommandStr=""

#<Dictionary Currencies>--------------------------




def GetMEIMsgCRC(Orji):
    Orji=Orji.replace(" ","")
    Orji=Orji[0:len(Orji)-2] + "00"
    hex_data=Decode2Hex(Orji)

    for byte in range(1, len(hex_data)-2):
        hex_data[len(hex_data)-1] ^= hex_data[byte]

    tdata=hex_data.hex().upper()
    return tdata


def ParseMEICurrency(MoneyString):
    extDataIndex=20
    CurrencyCode=MoneyString[extDataIndex:extDataIndex+2]

    CountryCode=MoneyString[extDataIndex+2:extDataIndex+2+6]
    CountryCodeHex=MoneyString[extDataIndex+2:extDataIndex+2+6]
    CountryCode=bytearray.fromhex(CountryCode).decode()


    if CountryCodeHex=="000000":
        return "","", 0
    
    BillValue=MoneyString[extDataIndex+8:extDataIndex+8+6]
    BillValue=int(bytearray.fromhex(BillValue).decode())
    
    
    num3 = MoneyString[extDataIndex + 16:  extDataIndex + 16+4]
    num3=int(bytearray.fromhex(num3).decode())
    
    carpan= MoneyString[extDataIndex + 14:extDataIndex + 14+ 2]
    if carpan=="2B":
        num4=1
        while 1==1:
            if num4 > num3:
                break
            BillValue=BillValue*10
            num4=num4+1
    else:
        num5=1
        while 1==1:
            if num5>num3:
                break
            BillValue=BillValue/10
    
    
    return CurrencyCode, CountryCode, BillValue
    





dictCurrencies = []


def GetCurrencyDenom(currencyCode):
    if len(dictCurrencies)==0:
        return -1
    for member in dictCurrencies:
        if str(member['currencyCode'])==str(currencyCode):
            return member["denom"]
    return -1

def GetCurrencyCountryCode(currencyCode):
    if len(dictCurrencies)==0:
        return "-1"
    for member in dictCurrencies:
        if str(member['currencyCode'])==str(currencyCode):
            return member["countryCode"]
    return "-1"

def GetCurrencyDenomHex(currencyCode):
    if len(dictCurrencies)==0:
        return "-1"
    for member in dictCurrencies:
        if str(member['currencyCode'])==str(currencyCode):
            return member["denomHex"]
    return "-1"
#</Dictionary Currencies>--------------------------














Billacceptor_LastCredit=0
Billacceptor_LastDenom=0
Billacceptor_LastDenomHex=""
Billacceptor_LastCountryCode=""

Billacceptor_TotalAmount=0
Billacceptor_TotalCount=0
IsBillacceptorBusy_Stacking=0
IsBillacceptorBusy_Stacked=0

state_dict = {1:"Idling", 2:"Accepting", 4:"Escrowed", 8:"Stacking",16:"Stacked", 32:"Returning", 64:"Returned",17:"Stacked Idling ", 65:"Returned Idling"}
event_dict = {0:"", 1:"Cheated", 2:"Rejected", 4:"Jammed", 8:"Full"}
#16:"Casette Installed"


Last_Billacceptor_Message=""
Last_Billacceptor_Message_Handle=""
Last_Billacceptor_Meaning=""
IsBillacceptorBusy_Accepting=0
Prev_IsCashboxInstalled=1
IsBillAcceptorBusy=0
def DoBillAcceptorPooling():
    global Last_Billacceptor_Message
    global Last_Billacceptor_Message_Handle
    global G_Machine_LastBillAcceptorTime
    global Prev_IsCashboxInstalled
    global IsBillAcceptorBusy
    global IsCardReaderBusy
    global Last_Billacceptor_Meaning
    global IsBillAcceptorPoolingStarted
    IsBillAcceptorPoolingStarted=1

    global Billacceptor_TotalCount
    global Billacceptor_TotalAmount
    global sasport
    global IsBillacceptorBusy_Stacking
    global IsBillacceptorBusy_Stacked
    global Billacceptor_LastCredit
    global Billacceptor_LastDenom
    global Billacceptor_LastDenomHex
    global Billacceptor_LastCountryCode
    global IsBillacceptorBusy_Accepting
    global G_Machine_IsBillacceptorPortFound

    if len(BillAcceptorCommandStr)==0:
        BillAcceptor_Status_Check()
        SendBillAcceptorCommandIsExist()
    else:
        SendBillAcceptorCommandIsExist()


    time.sleep(0.2)

    tdata=""
    try:
        while 1:
            if billacceptorport.is_open==False:
                #print("BILLACCEPTOR PORT ACIK DEGIL KI!!!!")
                return



            #<Get message from port>-----------------------
            data_left = billacceptorport.inWaiting()
            if data_left==0:
                break
            while data_left>0:
                tdata+=billacceptorport.read_all().hex()
                #time.sleep(0.001)
                data_left = billacceptorport.inWaiting()

        out=Decode2Hex(tdata)
        if len(tdata)>0:
            tdata=tdata.upper()

            if G_Machine_IsBillacceptorPortFound==0:
                print("Billacceptor tdata", tdata)
            IsHandled=0
            Meaning=""




            #<MEI>------------------------------------------------
            if G_Machine_BillAcceptorTypeId==2:


                status=""
                # With the exception of Stacked and Returned, only we can
                # only be in one state at once
                try:
                    Meaning = state_dict[out[3]]
                except:
                    status = ''
                    #print("unknown state dic key", tdata)


                if len(Meaning)>0:
                    IsHandled=1

                if len(Meaning)==0:
                    print("Bill Acceptor Received Data", tdata)

                if Meaning=="Returned" or Meaning=="Returned Idling":
                    print("*** RETURNED!! **** ")


                IsEscrowed= out[3] & 4

                if tdata[0:2]=="02"  and tdata[0:4]!="021E" and IsBillAcceptorBusy==0 and IsEscrowed==0:
                    IsCashboxInstalled=out[4] & 16
                    if IsCashboxInstalled>0:
                        IsCashboxInstalled=1
                    else:
                        IsCashboxInstalled=0

                    if IsCashboxInstalled==1 and Prev_IsCashboxInstalled==0:
                        print("Cashbox is installed!", tdata)
                        HandleReceivedSASCommand("01FF1CF17F")
                
                    if IsCashboxInstalled==0 and Prev_IsCashboxInstalled==1:
                        print("Cashbox is removed!", tdata)
                        HandleReceivedSASCommand("01FF1B4E0B")

                    Prev_IsCashboxInstalled=IsCashboxInstalled

                # If there is no match, we get an empty string
                try:
                    status += event_dict[out[4] & 1]
                    status += event_dict[out[4] & 2]
                    status += event_dict[out[4] & 4]
                    status += event_dict[out[4] & 8]
                    status += event_dict[out[4] & 16]
                except KeyError:
                    status+=""
                    #print("unknown state dic key", tdata)

                if len(Meaning)>0 or tdata[0:4]=="020B":
                    G_Machine_IsBillacceptorPortFound=1


                if Last_Billacceptor_Meaning!=Meaning:
                    Last_Billacceptor_Meaning=Meaning
                    print("Last_Billacceptor_State", Last_Billacceptor_Meaning, "status", status)

                if Meaning=="Idling":
                    IsBillacceptorBusy_Accepting=0
                    G_Machine_IsBillacceptorPortFound=1
                    G_Machine_LastBillAcceptorTime=datetime.datetime.now()


                if Meaning=="Idling" and len(status)>0:
                    print("Bill Acceptor Meanin", Meaning, "status",status, "data", tdata)

                if Meaning!="Idling":
                    print("Bill Acceptor Meanin", Meaning, "status",status, "data", tdata)




                if Meaning=="Idling" and status=="Jammed":
                    extDataIndex=20
                    MoneyString=tdata

                    print("ValidationCode", ValidationCode)

                    ValidationCode=MoneyString[extDataIndex:extDataIndex+36]
                    ValidationCode=Decode2Hex(ValidationCode)
                    MoneyStr=Decimal(ValidationCode[len(ValidationCode)-4:len(ValidationCode)])/100
                    
                    Billacceptor_LastCredit=MoneyStr
                    Billacceptor_LastDenom=MoneyStr
                    Billacceptor_LastDenomHex=""
                    Billacceptor_LastCountryCode=""

                    print("GELEN PARA!", Billacceptor_LastCredit)

                if len(Meaning)>0:
                    G_Machine_IsBillacceptorPortFound=1
                
                if Meaning!="Idling":
                    G_Machine_IsBillacceptorPortFound=1
                    print("Bill Status",Meaning , status)




                if Meaning=="Stacked":
                    if IsBillacceptorBusy_Stacked==1:
                        SQL_Safe_InsImportantMessage("Bill is stacked! ",100)


                if Meaning=="Stacking" or (Meaning=="Accepting" and status=="Cheated"):

                    print("DB'ye KAYIT AT ")
                    if IsBillacceptorBusy_Stacking==1:
                        SQL_InsException("Bill-Stack",tdata)

                        print("RECEIVED STRING STACKING", tdata)

                        print("<MEI PARA YUKLE STARTED!>-------------------------------------------------")
                        IsCardReaderBusy=1
                        IsBillAcceptorBusy=1
                        
                        try:
                            #PARCAKomut_DisableBillAcceptor("MEI")

                            IsBillacceptorBusy_Stacking=0
                            Billacceptor_TotalCount=Billacceptor_TotalCount+1
                            Billacceptor_TotalAmount=Billacceptor_TotalAmount+Billacceptor_LastCredit
                            print("Atilan para", Billacceptor_LastCredit, Billacceptor_LastDenom, Billacceptor_LastDenomHex, Billacceptor_LastCountryCode, tdata)
                            print("Billacceptor_TotalAmount", Billacceptor_TotalAmount, "Billacceptor_TotalCount", Billacceptor_TotalCount)



                

                            cardmachinelogid=0
                            cardmachinelogid=Config.getint('customer','cardmachinelogid')
                            try:
                                cardmachinelogid=G_CardMachineLogId
                            except Exception as eCardLogId:
                                ExceptionHandler("cardmachinelogid",eCardLogId,0)
                            print("Billacceptor_LastCredit", Billacceptor_LastCredit)
                            print("Billacceptor_LastDenomHex", Billacceptor_LastDenomHex)
                            print("Billacceptor_LastCountryCode", Billacceptor_LastCountryCode)

                            BillAcceptorId=SQL_InsBillAcceptorMoneyEFT(cardmachinelogid, G_User_CardNo, Billacceptor_LastCredit, Billacceptor_LastDenomHex,Billacceptor_LastCountryCode,1,0,0,Billacceptor_LastDenom)

                            if IsCardInside==1:
                                ParaYukleSonuc=1
                                ParaYukleSonuc=Wait_ParaYukle(1)
                                if ParaYukleSonuc!=1:
                                    SQL_InsImportantMessageByWarningType("Can't upload bill acceptor money: " + str(Billacceptor_LastCredit),1,1)
                                else:
                                    SQL_UpdBillAcceptorMoney(BillAcceptorId,1)
                                    Wait_Bakiye(11,1,"para")
                                    SQL_Safe_InsImportantMessage("Bill is cashed in! ",100)


                            Komut_CancelBalanceLock()
                            #GetMeter(0,"bill")

                            #Bir daha yirtma olursa bunu ac.
                            if IsBillacceptorBusy_Accepting==1:
                                IsBillacceptorBusy_Accepting=0

                            #PARCAKomut_EnableBillAcceptor()
                        except Exception as eMEI:
                            ExceptionHandler("MEIParaYukle",eMEI,1)



                        IsCardReaderBusy=0#MEI PARA YUKLE
                        IsBillAcceptorBusy=0
                        print("</MEI PARA YUKLE FINISHED!>-------------------------------------------------")


                #</if IsBillacceptorBusy_Stacking==1:>----------------------------------


                if Meaning=="Accepting":
                    print("RECEIVED STRING ACCEPTING", tdata)

                if Meaning=="Escrowed":
                    IsBillacceptorBusy_Stacked=0
                    try:
                        print("ESCROWED!", tdata)
                    except Exception as esql:
                        print("Escrowed Read Err!")

                #if Meaning=="Accepting":
                #    SQL_Safe_InsImportantMessage("BE Meaning:" + Meaning + " status:" + status + " Stacking:" + str(IsBillacceptorBusy_Stacking) + " Accepting:" + str(IsBillacceptorBusy_Accepting), 101)


                if Meaning=="Accepting" and status=="Jammed" and IsBillacceptorBusy_Accepting==0:#2021-05-09 kaldirdim and IsBillacceptorBusy_Accepting==0:
                    IsBillacceptorBusy_Accepting=1
                    print("Gelen mesaj", tdata)

                    CurrencyCode, CountryCode, BillValue= ParseMEICurrency(tdata)
                    print("CurrencyCode", CurrencyCode, "CountryCode", CountryCode, "BillValue", BillValue)

                    if IsBillAcceptorBusy==1:
                        ShowNotifyScreen("BUSY", "Bill acceptor is busy",5)
                        SQL_Safe_InsImportantMessage("Billacceptor is busy",80)
                        BillAcceptor_Reject("busy")
                        return


                    if BillValue==0:
                        SQL_Safe_InsImportantMessage("Bill value is 0",80)
                        BillAcceptor_Reject("Val: 0")
                    
                    if BillValue>0:
                        Billacceptor_LastDenom=BillValue
                        Billacceptor_LastDenomHex=CurrencyCode
                        Billacceptor_LastCountryCode=CountryCode
            
                        Billacceptor_LastCredit=Billacceptor_LastDenom
                        
                        BankNoteCode=CurrencyCode

                        SQL_InsException("Bill-Accepting",tdata)



                        if 2==2:
                            print("SQL'DEN CEK BAKALIM MEI")
                            #<Here check billacceptor>#############################################
                            try:
                                cardmachinelogid=0
                                try:
                                    cardmachinelogid=Config.getint('customer','cardmachinelogid')
                                except Exception as eMachine:
                                    cardmachinelogid=0

                                try:
                                    cardmachinelogid=G_CardMachineLogId
                                except Exception as eCardLogId:
                                    ExceptionHandler("cardmachinelogid",eCardLogId,0)

                                # Use new database helper for bill acceptor validation (synchronous)
                                # Include SAS context for bill acceptor operations
                                sas_context = get_current_sas_context()
                                results = db_helper.execute_database_operation('tsp_CheckBillacceptorIn', 
                                    (G_Machine_Mac, G_Machine_BillAcceptorTypeId, cardmachinelogid, G_User_CardNo, BankNoteCode, Billacceptor_LastCountryCode,Billacceptor_LastDenom, Billacceptor_LastDenomHex),
                                    sas_context)

                                for row in results:
                                    Result=int(row["Result"])
                                    ErrorMessage=row['ErrorMessage']
                                    print("ErrorMessage", ErrorMessage)

                                    Billacceptor_LastCredit=Decimal(row["CreditAmount"])

                                    if Result==0:
                                        ShowNotifyScreen("BILL-IN ERROR!",ErrorMessage, 4)
                                        SQL_Safe_InsImportantMessage("Bill-In error " + ErrorMessage ,80)
                                        BillAcceptor_Reject(ErrorMessage)
                                        return

                                    if Result==1:
                                        ShowNotifyScreen("CASHLESS BILL-IN!",ErrorMessage, 4)
                                        print("Atilan para", Billacceptor_LastDenom, Billacceptor_LastDenomHex, Billacceptor_LastCountryCode, tdata)
                                        
                                        
                                        
                                        #Kilitle
                                        IsBalanceProblem=0
                                        DoStack=1
                                        if Wait_Bakiye(2,0,"BillAcceptor")==0:
                                           IsBalanceProblem=1

                                        if BalanceQuery_GameLockStatus=="FF":
                                            IsBalanceProblem=1

                                        if IsBalanceProblem==1:
                                            BillAcceptor_Reject("Transfer")
                                            ShowNotifyScreen("BILL ERROR!","System can't transfer money at the moment. Please try again later.",10)
                                            DoStack=0
                                            Komut_CancelBalanceLock()

                                        if DoStack==1:
                                            SQL_Safe_InsImportantMessage("Stack Bill " + str(Billacceptor_LastDenom) + "-" + str(Billacceptor_LastCountryCode),100)
                                            BillAcceptor_Stack1()
                                            SendBillAcceptorCommandIsExist()

                                            
                                            if IsBillacceptorBusy_Stacking==0:
                                                IsBillacceptorBusy_Stacking=1


                                # Connection handled by database helper
                            except Exception as ecardtype:
                                BillAcceptor_Reject("server connection")
                                SQL_Safe_InsImportantMessage("Bill is rejected because of no connection",80)
                                ExceptionHandler("tsp_CheckBillacceptorIn",ecardtype,0)
                            #</Here check billacceptor>#############################################


                    #if BillValue>0: bitti



            






            #    print("MEI", tdata)
            #</MEI>------------------------------------------------



            #if Meaning!="Idling" and G_Machine_IsBillacceptorPortFound==1:
            #    print(Meaning, tdata)

            Last_Billacceptor_Message=tdata
            if IsHandled==0:
                print("Meaning Data", Meaning, tdata)
                print("Bill acceptor handle edemedik!!" , tdata)
                Last_Billacceptor_Message_Handle=tdata
            if IsHandled==0 and G_Machine_IsBillacceptorPortFound==1:
                G_Machine_LastBillAcceptorTime=datetime.datetime.now()
    except Exception as e:
        ExceptionHandler("DoBillAcceptorPooling",e,0)




#</BILL ACCEPTOR HELPER>------------------------------------------------------------------------



G_Static_VersionId=41
G_Static_SasWait=0.2

IsShowEveryMessage=0
IsDebugAutoBakiyeYanit=0

# DEPRECATED MSSQL Configuration (migrated to PostgreSQL)
# G_DB_Host="172.16.23.1"
# G_DB_User="cashlessdevice" 
# G_DB_Password="Mevlut12!"
# G_DB_Database="TCASINO"

# PostgreSQL Configuration (Primary Database)
G_PG_Host="localhost"
G_PG_User="postgres"
G_PG_Password="password"
G_PG_Database="casino_db"
G_PG_Port=5432
G_PG_Schema="tcasino"
G_USE_POSTGRESQL=True  # Force PostgreSQL only - no MSSQL fallback



# DEPRECATED MSSQL Configuration Loading (migrated to PostgreSQL)
# Legacy configuration files are kept for backward compatibility but not used
try:
    file = open('casinoip.ini', 'r')
    legacy_db_host = file.read().replace('\n','')
    print("DEPRECATED: Legacy MSSQL Host found:", legacy_db_host, "- Using PostgreSQL instead")
except Exception as e:
    print("No legacy MSSQL configuration found (expected)")

try:
    file = open('db.ini', 'r') 
    legacy_db_database = file.read().replace('\n','')
    print("DEPRECATED: Legacy MSSQL Database found:", legacy_db_database, "- Using PostgreSQL instead")
except Exception as e:
    print("No legacy MSSQL database configuration found (expected)")

# PostgreSQL configuration from files
try:
    file = open('pg_host.ini', 'r')
    G_PG_Host=file.read().replace('\n','')
    print("PostgreSQL Host:", G_PG_Host)
except Exception as e:
    print("Using default PostgreSQL host")

try:
    file = open('pg_database.ini', 'r')
    G_PG_Database=file.read().replace('\n','')
    print("PostgreSQL Database:", G_PG_Database)
except Exception as e:
    print("Using default PostgreSQL database")

try:
    file = open('pg_user.ini', 'r')
    G_PG_User=file.read().replace('\n','')
except Exception as e:
    print("Using default PostgreSQL user")

try:
    file = open('pg_password.ini', 'r')
    G_PG_Password=file.read().replace('\n','')
except Exception as e:
    print("Using default PostgreSQL password")

try:
    file = open('pg_port.ini', 'r')
    G_PG_Port=int(file.read().replace('\n',''))
except Exception as e:
    print("Using default PostgreSQL port")

try:
    file = open('pg_schema.ini', 'r')
    G_PG_Schema=file.read().replace('\n','')
    print("PostgreSQL Schema:", G_PG_Schema)
except Exception as e:
    print("Using default PostgreSQL schema")

try:
    file = open('use_postgresql.ini', 'r')
    G_USE_POSTGRESQL=file.read().replace('\n','').lower() in ['1', 'true', 'yes']
    print("Use PostgreSQL:", G_USE_POSTGRESQL)
except Exception as e:
    print("Using default PostgreSQL setting")



try:
    # Network check now uses PostgreSQL host instead of legacy MSSQL host
    if (G_PG_Host.split('.')[0]+"." + G_PG_Host.split('.')[1])!=(get_lan_ip().split('.')[0]+"." + get_lan_ip().split('.')[1]):
        print("*******************************************************")
        print("Device is in the not same network.")
        NotSameIPCount=0
        while NotSameIPCount<10:
            NotSameIPCount=NotSameIPCount+1
            print("Device is in the not same network. Restart!", (G_PG_Host.split('.')[0]+"." + G_PG_Host.split('.')[1]), (get_lan_ip().split('.')[0]+"." + get_lan_ip().split('.')[1]), "-----")
        print("Device is in the not same network.")
        print("*******************************************************")
except Exception as e:
    print("IP ERR!!!")



IsCardRead=1
IsSasPooling=1

#Spark; Hizli
G_Machine_SasPoolingVersion=0

IsCardInside=0



G_User_CardNo=""
G_User_PrevCardNo=""
G_CardMachineLogId=0

IsDebugMachineNotExist=0
IsDebugAutoBakiyeYanit=0
IsDebugAutoBakiyeSifirlaYanit=0
IsDebugAutoParaYukleYanit=0
IsDebugNotControlAfterCardInserted=0




#<PYQT>--------------------------------------------------------------
class MainWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setGeometry(100,100,1280,480)
        
        oImage = QImage("bg.jpg")
        sImage = oImage.scaled(QSize(1280,480))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(sImage))                        
        self.setPalette(palette)
        
        
        #self.label = QLabel('Test aciklamasi', self)
        #self.label.setGeometry(300,300,200,50)


        self.labelM = QLabel(self)
        self.labelM.setGeometry(1175,20,1280,50)
        self.labelM.setFont(QFont('SansSerif', 30))
        self.labelM.setText("<font color='yellow'>"+G_Machine_MachineName+"</font>")
        


        self.labelA = QLabel(self)
        self.labelA.setGeometry(0,175,1280,50)
        self.labelA.setFont(QFont('SansSerif', 30))


        self.labelB = QLabel(self)
        self.labelB.setGeometry(0,225,1280,50)
        self.labelB.setFont(QFont('SansSerif', 35))
        #self.labelB.setText("<center><font color='white'>Sn. Spark (111111)</font></center>")

        self.labelC = QLabel(self)
        self.labelC.setGeometry(0,400,1280,50)
        self.labelC.setFont(QFont('SansSerif', 25))
        #self.labelC.setText("<center><font color='yellow'>Please insert your card</font></center>")

        #labelA.setStyleSheet("{color: #C0BBFE}");
        #labelA.move(100, 40)

        if WINDOWS==True:
            self.show()
        else:
            self.showFullScreen()

    def ShowCustomerPage(self, text1, text2):
        print("text1", text1, "text2", text2)
        self.labelA.setText("<center><font color='white'>"+text1+"</font></center>")
        self.labelB.setText("<center><font color='white'>"+text2+"</font></center>")

    def HideCustomerPage(self):
        self.labelA.setText("")
        self.labelB.setText("")

    def ChangeStatu(self, text1):
        self.labelC.setText("<center><font color='yellow'>"+text1+"</font></center>")

    def ChangeMachineName(self, text1):
        self.labelM.setText("<center><font color='yellow'>"+text1+"</font></center>")

print("Start")
oMainwindow=None
def CreateGUI():
    global oMainwindow
    app = QApplication(sys.argv)
    oMainwindow = MainWindow()
    #oMainwindow.ChangeMachineName(G_Machine_MachineName)
    sys.exit(app.exec_())

#</PYQT>-------------------------------------------------------------


G_IsDeviceTestPurpose=0
# MIGRATED: Use PostgreSQL host for test environment detection
if G_PG_Host=="admiral.gopizza.fi":
    G_IsDeviceTestPurpose=1

if G_PG_Host=="asist.sanaloyun.net":
    G_IsDeviceTestPurpose=1





#if WINDOWS==True:
# MIGRATED: Use PostgreSQL host for debug mode detection
if WINDOWS==True or G_IsDeviceTestPurpose==1 or G_PG_Host=="admiral.gopizza.fi" or G_PG_Host=="www.angora.fi" or G_PG_Host.startswith("192.168.1.3")==True or G_PG_Host.startswith("192.168.1.33")==True  or G_PG_Host.startswith("localhost")==True or G_PG_Host.startswith("127.0.0.1")==True or G_PG_Host.startswith("192.162.137.5")==True:
    #IsGUIEnabled=1

    print("*************************************************************************")
    print("DEBUG MODE IS ACTIVATED *************************************************")
    print("*************************************************************************")

    
    
    IsDebugAutoBakiyeYanit=1
    IsDebugMachineNotExist=1
    IsDebugAutoBakiyeYanit=1
    IsDebugAutoBakiyeSifirlaYanit=1
    IsDebugNotControlAfterCardInserted=1
    IsDebugAutoParaYukleYanit=1
    IsCardRead=1
    IsSasPooling=1
    #IsSasPooling=0


#eskiden config buradaydi.


# MIGRATED: Use PostgreSQL host for debug configuration
if G_PG_Host=="95.158.189.2":
    IsDebugMachineNotExist=0


#<DATABASE HELPER>--------------------------------------------------------------
class DatabaseHelper:
    """
    PostgreSQL-only database helper class.
    Migrated from MSSQL to PostgreSQL - all MSSQL dependencies removed.
    """
    def __init__(self):
        self.pg_conn = None
        self.last_pg_connect_attempt = None
        
        # Define operations that require immediate response (synchronous)
        # These procedures need immediate results for app functionality
        self.SYNC_OPERATIONS = {
            'tsp_getbalanceinfoongm',      # MSSQL: tsp_GetBalanceInfoOnGM (PROCEDURE)
            'tsp_cardread',                # MSSQL: tsp_CardRead (FUNCTION)
            'tsp_cardreadpartial',         # MSSQL: tsp_CardReadPartial (FUNCTION)
            'tsp_checkbillacceptorin',     # MSSQL: tsp_CheckBillacceptorIn (PROCEDURE)
            'tsp_devicestatu',             # MSSQL: tsp_DeviceStatu (PROCEDURE) - Device configuration data
            'tsp_checknetwork',            # MSSQL: tsp_CheckNetwork (needs verification)
            'tsp_getcustomeradditional',   # MSSQL: tsp_GetCustomerAdditional (needs verification)
            'tsp_getdevicegameinfo',       # MSSQL: tsp_GetDeviceGameInfo (needs verification)
            'tsp_getcustomercurrentmessages', # MSSQL: tsp_GetCustomerCurrentMessages (needs verification)
            'tsp_getcustomermessage',      # MSSQL: tsp_GetCustomerMessage (needs verification)
            'tsp_bonusrequestlist'         # MSSQL: tsp_BonusRequestList (needs verification)
        }
        
        # Procedure name mapping from MSSQL to PostgreSQL (verified from postgres-routines-in-sas.sql)
        self.PROCEDURE_NAME_MAP = {
            # ✓ VERIFIED PROCEDURES (CREATE OR REPLACE PROCEDURE)
            'tsp_CheckBillacceptorIn': 'tsp_checkbillacceptorin',
            'tsp_GetBalanceInfoOnGM': 'tsp_getbalanceinfoongm', 
            'tsp_DeviceStatu': 'tsp_devicestatu',
            'tsp_GetDeviceAdditionalInfo': 'tsp_getdeviceadditionalinfo',
            
            # ✓ VERIFIED FUNCTIONS (CREATE OR REPLACE FUNCTION)  
            'tsp_CardRead': 'tsp_cardread',
            'tsp_CardReadPartial': 'tsp_cardreadpartial', 
            'tsp_CardReadAddMoney': 'tsp_cardreadaddmoney',
            'tsp_UpdBillAcceptorMoney': 'tsp_updbillacceptormoney',
            'tsp_InsGameStart': 'tsp_insgamestart',
            'tsp_InsGameEnd': 'tsp_insgameend',
            'tsp_UpdDeviceAdditionalInfo': 'tsp_upddeviceadditionalinfo',
            'tsp_InsException': 'tsp_insexception',
            'tsp_InsDeviceDebug': 'tsp_insdevicedebug',
            'tsp_InsTraceLog': 'tsp_instracelog',
            'tsp_InsReceivedMessage': 'tsp_insreceivedmessage',
            'tsp_InsSentCommands': 'tsp_inssentcommands',
            'tsp_GetNextVisit': 'tsp_getnextvisit',
            'tsp_InsProductOrderBySlot': 'tsp_insproductorderbyslot',
            'tsp_GetProductCategories': 'tsp_getproductcategories',
            'tsp_GetSlotCustomerDiscountCalc': 'tsp_getslotcustomerdiscountcalc',
            'tsp_GetProductsAndSubCategoriesSlot': 'tsp_getproductsandsubcategoriesslot',
            
            # ⚠️ NEED VERIFICATION - Not found in postgres-routines-in-sas.sql yet
            # 'tsp_CheckNetwork': 'tsp_checknetwork',
            # 'tsp_GetCustomerAdditional': 'tsp_getcustomeradditional', 
            # 'tsp_GetDeviceGameInfo': 'tsp_getdevicegameinfo',
            # 'tsp_GetCustomerCurrentMessages': 'tsp_getcustomercurrentmessages',
            # 'tsp_GetCustomerMessage': 'tsp_getcustomermessage',
            # 'tsp_BonusRequestList': 'tsp_bonusrequestlist',
        }
    
    def validate_payload(self, payload):
        """Validate that payload contains all three mandatory elements:
        1. Procedure Parameters
        2. Device ID/MAC Address  
        3. SAS Message Information
        """
        required_fields = ['parameters', 'device_id']
        missing_fields = []
        
        for field in required_fields:
            if field not in payload:
                missing_fields.append(field)
        
        # SAS message should be attempted - if not present, try to get it
        if 'sas_message' not in payload:
            sas_context = get_current_sas_context()
            if sas_context:
                payload['sas_message'] = sas_context
                print("Auto-added SAS context to payload")
        
        if missing_fields:
            print(f"WARNING: Payload missing required fields: {missing_fields}")
            return False
        
        print(f"✓ Payload validated - contains all 3 mandatory elements")
        return True
    
    def get_postgresql_connection(self):
        """Get PostgreSQL connection with retry logic - PostgreSQL ONLY"""
        if not POSTGRESQL_AVAILABLE:
            print("ERROR: PostgreSQL dependencies not available!")
            return None
            
        # Don't retry too frequently
        if (self.last_pg_connect_attempt and 
            datetime.datetime.now() - self.last_pg_connect_attempt < datetime.timedelta(seconds=30)):
            return None
            
        try:
            if self.pg_conn is None or self.pg_conn.closed:
                self.pg_conn = psycopg2.connect(
                    host=G_PG_Host,
                    database=G_PG_Database,
                    user=G_PG_User,
                    password=G_PG_Password,
                    port=G_PG_Port,
                    connect_timeout=10
                )
                self.pg_conn.autocommit = True
                print("PostgreSQL connected successfully")
            return self.pg_conn
        except Exception as e:
            self.last_pg_connect_attempt = datetime.datetime.now()
            print(f"PostgreSQL connection failed: {e}")
            return None
    
    def normalize_procedure_name(self, procedure_name):
        """Convert MSSQL procedure names to PostgreSQL format"""
        # Check if we have a specific mapping
        if procedure_name in self.PROCEDURE_NAME_MAP:
            pg_name = self.PROCEDURE_NAME_MAP[procedure_name]
            print(f"MIGRATED: {procedure_name} -> {pg_name}")
            return pg_name
        
        # Default: convert to lowercase (PostgreSQL convention)
        pg_name = procedure_name.lower()
        print(f"AUTO-CONVERTED: {procedure_name} -> {pg_name}")
        return pg_name
    
    def is_postgresql_function(self, pg_procedure_name):
        """Determine if a PostgreSQL routine is a FUNCTION (vs PROCEDURE)"""
        # Based on verified postgres-routines-in-sas.sql analysis
        POSTGRESQL_FUNCTIONS = {
            'tsp_cardread', 'tsp_cardreadpartial', 'tsp_cardreadaddmoney',
            'tsp_updbillacceptormoney', 'tsp_insgamestart', 'tsp_insgameend',
            'tsp_upddeviceadditionalinfo', 'tsp_insexception', 'tsp_insdevicedebug',
            'tsp_instracelog', 'tsp_insreceivedmessage', 'tsp_inssentcommands',
            'tsp_getnextvisit', 'tsp_insproductorderbyslot', 'tsp_getproductcategories',
            'tsp_getslotcustomerdiscountcalc', 'tsp_getproductsandsubcategoriesslot',
            'tsp_devicestatu'  # Changed from PROCEDURE to FUNCTION since it returns data
        }
        
        POSTGRESQL_PROCEDURES = {
            'tsp_checkbillacceptorin', 'tsp_getbalanceinfoongm', 
            'tsp_getdeviceadditionalinfo'
        }
        
        if pg_procedure_name in POSTGRESQL_FUNCTIONS:
            return True
        elif pg_procedure_name in POSTGRESQL_PROCEDURES:
            return False
        else:
            # Default guess: most routines are functions in PostgreSQL
            print(f"WARNING: Unknown routine type for {pg_procedure_name}, assuming FUNCTION")
            return True
    
    def validate_procedure_exists(self, pg_procedure_name):
        """Check if procedure/function exists in PostgreSQL"""
        pg_conn = self.get_postgresql_connection()
        if not pg_conn:
            print(f"Cannot validate {pg_procedure_name} - no PostgreSQL connection")
            return False
            
        try:
            cursor = pg_conn.cursor()
            
            # Check both functions and procedures
            cursor.execute("""
                SELECT routine_name, routine_type 
                FROM information_schema.routines 
                WHERE routine_schema = %s AND routine_name = %s
            """, (G_PG_Schema, pg_procedure_name))
            
            result = cursor.fetchone()
            if result:
                routine_name, routine_type = result
                print(f"✓ VERIFIED: {pg_procedure_name} exists as {routine_type}")
                return True
            else:
                print(f"❌ MISSING: {pg_procedure_name} not found in {G_PG_Schema} schema")
                return False
                
        except Exception as e:
            print(f"Error validating {pg_procedure_name}: {e}")
            return False
    
    def queue_async_message(self, procedure_name, parameters, sas_message=None):
        """Queue asynchronous message to PostgreSQL - PostgreSQL ONLY"""
        # Normalize procedure name for PostgreSQL
        original_name = procedure_name
        pg_procedure_name = self.normalize_procedure_name(procedure_name)
        
        pg_conn = self.get_postgresql_connection()
        if not pg_conn:
            # Fallback to SQLite for offline storage
            self.queue_to_sqlite(original_name, parameters, sas_message)
            return False
        
        try:
            cursor = pg_conn.cursor()
            
            # MANDATORY PAYLOAD ELEMENTS:
            # 1. Procedure Parameters
            # 2. Device ID/MAC Address  
            # 3. SAS Message Information
            payload = {
                'procedure_name': pg_procedure_name,                         # Use PostgreSQL name
                'original_mssql_name': original_name,                        # Keep original for reference
                'parameters': parameters,                                    # ✓ REQUIRED: Procedure Parameters
                'device_id': getattr(self, 'device_id', G_Machine_Mac),     # ✓ REQUIRED: Device ID/MAC
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            # ✓ REQUIRED: SAS Message Context - always attempt to capture
            if not sas_message:
                sas_message = get_current_sas_context()
            if sas_message:
                payload['sas_message'] = sas_message
            
            # Validate payload has all required elements
            self.validate_payload(payload)
            
            cursor.execute("""
                INSERT INTO public.device_messages_queue (id, slot_machine_id, procedure_name, payload, status, created_at)
                VALUES (%s, %s, %s, %s, 'pending', NOW())
            """, (
                str(uuid.uuid4()),
                G_Machine_Mac,
                pg_procedure_name,
                json.dumps(payload, cls=DecimalEncoder)
            ))
            
            print(f"Queued async message: {original_name} -> {pg_procedure_name}")
            return True
            
        except Exception as e:
            print(f"Failed to queue async message: {e}")
            # Fallback to SQLite
            self.queue_to_sqlite(original_name, parameters, sas_message)
            return False
    
    def queue_to_sqlite(self, procedure_name, parameters, sas_message=None):
        """Fallback: store message in SQLite for later sync"""
        try:
            cursor = conn.cursor()  # Using global SQLite connection
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pending_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    procedure_name TEXT,
                    parameters TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # MANDATORY PAYLOAD ELEMENTS for SQLite fallback:
            # 1. Procedure Parameters
            # 2. Device ID/MAC Address  
            # 3. SAS Message Information
            payload_data = {
                'parameters': parameters,                            # ✓ REQUIRED: Procedure Parameters
                'device_id': G_Machine_Mac,                         # ✓ REQUIRED: Device ID/MAC
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            # ✓ REQUIRED: SAS Message Context - always attempt to capture
            if not sas_message:
                sas_message = get_current_sas_context()
            if sas_message:
                payload_data['sas_message'] = sas_message
            
            cursor.execute("""
                INSERT INTO pending_messages (procedure_name, parameters)
                VALUES (?, ?)
            """, (procedure_name, json.dumps(payload_data, cls=DecimalEncoder)))
            
            conn.commit()
            print(f"Stored in SQLite fallback: {procedure_name}")
            
        except Exception as e:
            print(f"SQLite fallback failed: {e}")
    
    def execute_sync_operation(self, procedure_name, parameters, sas_message=None):
        """Execute synchronous operation (immediate response needed) - PostgreSQL ONLY"""
        # Normalize procedure name for PostgreSQL
        original_name = procedure_name
        pg_procedure_name = self.normalize_procedure_name(procedure_name)
        
        result = None
        execution_success = False
        error_message = None
        
        # PostgreSQL ONLY - no MSSQL fallback
        pg_conn = self.get_postgresql_connection()
        if not pg_conn:
            error_message = "PostgreSQL connection not available"
            self.log_sync_procedure_call(original_name, parameters, None, "postgresql", error_message, sas_message)
            raise Exception(error_message)
        
        # Check if procedure is marked as synchronous
        if pg_procedure_name not in self.SYNC_OPERATIONS:
            print(f"WARNING: {original_name} ({pg_procedure_name}) not in SYNC_OPERATIONS - should this be async?")
        
        # Validate procedure exists in PostgreSQL
        if not self.validate_procedure_exists(pg_procedure_name):
            error_message = f"Procedure {pg_procedure_name} does not exist in PostgreSQL"
            self.log_sync_procedure_call(original_name, parameters, None, "postgresql", error_message, sas_message)
            raise Exception(error_message)
        
        try:
            cursor = pg_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Set search path to include tcasino schema for existing procedures
            cursor.execute(f"SET search_path TO {G_PG_Schema}, public;")
            
            # Call the procedure/function in tcasino schema using correct PostgreSQL syntax
            is_function = self.is_postgresql_function(pg_procedure_name)
            
            if len(parameters) > 0:
                placeholders = ','.join(['%s'] * len(parameters))
                
                if is_function:
                    # PostgreSQL FUNCTION: SELECT * FROM schema.function_name(params)
                    cursor.execute(f"SELECT * FROM {G_PG_Schema}.{pg_procedure_name}({placeholders})", parameters)
                    result = cursor.fetchall()
                    print(f"Called FUNCTION: {pg_procedure_name}")
                else:
                    # PostgreSQL PROCEDURE: CALL schema.procedure_name(params)
                    cursor.execute(f"CALL {G_PG_Schema}.{pg_procedure_name}({placeholders})", parameters)
                    result = []  # Procedures may not return data directly
                    print(f"Called PROCEDURE: {pg_procedure_name}")
            else:
                # No parameters
                if is_function:
                    cursor.execute(f"SELECT * FROM {G_PG_Schema}.{pg_procedure_name}()")
                    result = cursor.fetchall()
                    print(f"Called FUNCTION: {pg_procedure_name} (no params)")
                else:
                    cursor.execute(f"CALL {G_PG_Schema}.{pg_procedure_name}()")
                    result = []
                    print(f"Called PROCEDURE: {pg_procedure_name} (no params)")
            
            execution_success = True
            
            # Log the sync procedure call to message queue
            self.log_sync_procedure_call(original_name, parameters, result, "postgresql", None, sas_message)
            
            print(f"SUCCESS: {original_name} -> {pg_procedure_name} returned {len(result) if result else 0} rows")
            return result
            
        except Exception as e:
            error_message = str(e)
            print(f"PostgreSQL sync operation failed: {original_name} -> {pg_procedure_name}: {e}")
            
            # Log the failed sync procedure call
            self.log_sync_procedure_call(original_name, parameters, None, "postgresql", error_message, sas_message)
            raise Exception(f"PostgreSQL procedure call failed: {error_message}")
    
    def execute_database_operation(self, procedure_name, parameters, sas_message=None):
        """Main method to execute database operations - PostgreSQL ONLY"""
        # Normalize procedure name for PostgreSQL
        pg_procedure_name = self.normalize_procedure_name(procedure_name)
        
        # Check if this is a synchronous operation
        if pg_procedure_name in self.SYNC_OPERATIONS:
            return self.execute_sync_operation(procedure_name, parameters, sas_message)
        else:
            # Async operation - queue it
            self.queue_async_message(procedure_name, parameters, sas_message)
            return []  # No immediate result for async operations
    
    def log_sync_procedure_call(self, procedure_name, parameters, result, database_used, error_message=None, sas_message=None):
        """Log synchronous procedure calls to message queue for auditing"""
        try:
            pg_conn = self.get_postgresql_connection()
            if not pg_conn:
                # If can't log to PostgreSQL, store in SQLite for later sync
                self.log_sync_call_to_sqlite(procedure_name, parameters, result, database_used, error_message)
                return
            
            cursor = pg_conn.cursor()
            
            # Determine status based on success/failure
            if error_message:
                status = 'proc_failed'
            else:
                status = 'proc_called'
            
            # MANDATORY PAYLOAD ELEMENTS:
            # 1. Procedure Parameters
            # 2. Device ID/MAC Address  
            # 3. SAS Message Information
            payload = {
                'procedure_name': procedure_name,
                'parameters': parameters,                            # ✓ REQUIRED: Procedure Parameters
                'device_id': G_Machine_Mac,                         # ✓ REQUIRED: Device ID/MAC
                'timestamp': datetime.datetime.now().isoformat(),
                'database_used': database_used,
                'execution_type': 'synchronous',
                'result_count': len(result) if result else 0,
                'error_message': error_message
            }
            
            # ✓ REQUIRED: SAS Message Context - always attempt to capture
            if not sas_message:
                sas_message = get_current_sas_context()
            if sas_message:
                payload['sas_message'] = sas_message
            
            # If result is small enough, include it in payload for debugging
            if result and len(str(result)) < 1000:  # Limit result size to avoid huge payloads
                payload['result_sample'] = result[:5]  # First 5 rows max
            
            cursor.execute("""
                INSERT INTO public.device_messages_queue (id, slot_machine_id, procedure_name, payload, status, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (
                str(uuid.uuid4()),
                G_Machine_Mac,
                procedure_name,
                json.dumps(payload, cls=DecimalEncoder),
                status
            ))
            
            print(f"Logged sync procedure call: {procedure_name} -> {status}")
            
        except Exception as e:
            print(f"Failed to log sync procedure call: {e}")
            # Fallback to SQLite
            self.log_sync_call_to_sqlite(procedure_name, parameters, result, database_used, error_message, sas_message)
    
    def log_sync_call_to_sqlite(self, procedure_name, parameters, result, database_used, error_message=None, sas_message=None):
        """Fallback: log sync calls to SQLite when PostgreSQL unavailable"""
        try:
            cursor = conn.cursor()  # Using global SQLite connection
            
            status = 'proc_failed' if error_message else 'proc_called'
            
            # MANDATORY PAYLOAD ELEMENTS for SQLite sync logging:
            # 1. Procedure Parameters
            # 2. Device ID/MAC Address  
            # 3. SAS Message Information
            payload = {
                'procedure_name': procedure_name,
                'parameters': parameters,                            # ✓ REQUIRED: Procedure Parameters
                'device_id': G_Machine_Mac,                         # ✓ REQUIRED: Device ID/MAC
                'timestamp': datetime.datetime.now().isoformat(),
                'database_used': database_used,
                'execution_type': 'synchronous',
                'result_count': len(result) if result else 0,
                'error_message': error_message,
                'status': status
            }
            
            # ✓ REQUIRED: SAS Message Context - always attempt to capture
            if not sas_message:
                sas_message = get_current_sas_context()
            if sas_message:
                payload['sas_message'] = sas_message
            
            cursor.execute("""
                INSERT INTO pending_messages (procedure_name, parameters)
                VALUES (?, ?)
            """, (f"{procedure_name}_sync_log", json.dumps(payload, cls=DecimalEncoder)))
            
            conn.commit()
            print(f"Stored sync call log in SQLite: {procedure_name}")
            
        except Exception as e:
            print(f"SQLite sync call logging failed: {e}")

    def sync_pending_sqlite_messages(self):
        """Sync pending messages from SQLite to PostgreSQL when connection is restored"""
        pg_conn = self.get_postgresql_connection()
        if not pg_conn:
            return False
        
        try:
            sqlite_cursor = conn.cursor()  # Using global SQLite connection
            sqlite_cursor.execute("""
                SELECT id, procedure_name, parameters, created_at 
                FROM pending_messages 
                ORDER BY created_at
            """)
            
            pending_messages = sqlite_cursor.fetchall()
            if not pending_messages:
                return True
            
            print(f"Syncing {len(pending_messages)} pending messages to PostgreSQL")
            
            pg_cursor = pg_conn.cursor()
            synced_ids = []
            
            for row in pending_messages:
                msg_id, procedure_name, parameters_json, created_at = row
                try:
                    parameters = json.loads(parameters_json)
                    
                    payload = {
                        'procedure_name': procedure_name,
                        'parameters': parameters,
                        'device_id': G_Machine_Mac,
                        'timestamp': created_at,
                        'synced_from_sqlite': True
                    }
                    
                    pg_cursor.execute("""
                        INSERT INTO public.device_messages_queue (id, slot_machine_id, procedure_name, payload, status, created_at)
                        VALUES (%s, %s, %s, %s, 'pending', %s)
                    """, (
                        str(uuid.uuid4()),
                        G_Machine_Mac,
                        procedure_name,
                        json.dumps(payload, cls=DecimalEncoder),
                        created_at
                    ))
                    
                    synced_ids.append(msg_id)
                    
                except Exception as e:
                    print(f"Failed to sync message {msg_id}: {e}")
            
            # Remove synced messages from SQLite
            if synced_ids:
                placeholders = ','.join('?' * len(synced_ids))
                sqlite_cursor.execute(f"""
                    DELETE FROM pending_messages WHERE id IN ({placeholders})
                """, synced_ids)
                conn.commit()
                print(f"Synced and removed {len(synced_ids)} messages from SQLite")
            
            return True
            
        except Exception as e:
            print(f"Failed to sync pending SQLite messages: {e}")
            return False

# Initialize database helper
db_helper = DatabaseHelper()

def verify_postgresql_migration():
    """Verify that all critical procedures exist in PostgreSQL after migration"""
    print("=== VERIFYING POSTGRESQL MIGRATION ===")
    
    # Critical procedures that MUST exist for app functionality
    critical_procedures = [
        'tsp_GetBalanceInfoOnGM',    # Balance checking
        'tsp_CardRead',              # Card reading
        'tsp_CardReadPartial',       # Partial card read
        'tsp_CheckBillacceptorIn',   # Bill acceptor validation
        'tsp_DeviceStatu',           # Device status updates
        'tsp_InsGameStart',          # Game start logging
        'tsp_InsGameEnd',            # Game end logging
        'tsp_InsBillAcceptorMoney',  # Bill acceptor money insert
        'tsp_CardExit',              # Card exit handling
    ]
    
    missing_procedures = []
    verified_procedures = []
    
    for mssql_proc in critical_procedures:
        pg_proc = db_helper.normalize_procedure_name(mssql_proc)
        if db_helper.validate_procedure_exists(pg_proc):
            verified_procedures.append(f"{mssql_proc} -> {pg_proc}")
        else:
            missing_procedures.append(f"{mssql_proc} -> {pg_proc}")
    
    print(f"\n✓ VERIFIED PROCEDURES ({len(verified_procedures)}):")
    for proc in verified_procedures:
        print(f"  {proc}")
    
    if missing_procedures:
        print(f"\n❌ MISSING PROCEDURES ({len(missing_procedures)}):")
        for proc in missing_procedures:
            print(f"  {proc}")
        print("\n⚠️  WARNING: Some critical procedures are missing from PostgreSQL!")
        print("   Please check postgres-routines-in-sas.sql for these procedures.")
        return False
    else:
        print(f"\n🎉 ALL CRITICAL PROCEDURES VERIFIED! PostgreSQL migration ready.")
        return True

# Helper function to extract SAS message information
def get_current_sas_context():
    """Extract current SAS message context for logging"""
    sas_context = {}
    
    # Add common SAS-related variables that exist in your application
    try:
        if 'Last_Billacceptor_Message' in globals():
            sas_context['last_billacceptor_message'] = Last_Billacceptor_Message
    except:
        pass
    
    try:
        if 'Last_Billacceptor_Message_Handle' in globals():
            sas_context['last_billacceptor_message_handle'] = Last_Billacceptor_Message_Handle
    except:
        pass
    
    try:
        # Add any current SAS command being processed
        if 'G_LastSASCommand' in globals():
            sas_context['last_sas_command'] = G_LastSASCommand
    except:
        pass
    
    try:
        # Add SAS version info
        if 'G_Static_VersionId' in globals():
            sas_context['sas_version_id'] = G_Static_VersionId
    except:
        pass
    
    return sas_context if sas_context else None

#</DATABASE HELPER>-------------------------------------------------------------




if 'pi' not in Config.sections():
    Config.add_section('pi')    
    Config.set('pi','mac', str(G_Machine_Mac))


if 'machine' not in Config.sections():
    #print("machine eklendi")
    Config.add_section('machine')    
    Config.set('machine','tableno', '0')
    Config.set('machine','machineid', '')
    Config.set('machine','paytableid', '')
    Config.set('machine','screentypeid', "8")
    Config.set('machine','billacceptortypeid', "0")
    Config.set('machine','newgamingday', "0")
    Config.set('machine','islockedbyadmin', "0")
    Config.set('machine','admincards', '')

if 'payment' not in Config.sections():
    #print("payment eklendi")
    Config.add_section('payment')    
    Config.set('payment','transactionid', "0")

if 'sas' not in Config.sections():
    #print("sas eklendi")
    Config.add_section('sas')
    Config.set('sas','versionid', '')
    Config.set('sas','serialnumber', '0000000000')#eskiden bostu. igtlerden sonra 10 tane 0 yaptik.
    Config.set('sas','registrationkey', '0000000000000000000000000000000000000000')
    Config.set('sas','assetnumber', '00000000')#Config.set('sas','assetnumber', '01000000')
    Config.set('sas','address', '01')

if 'customer' not in Config.sections():
    #print("customer eklendi")
    Config.add_section('customer')    
    Config.set('customer','cardnumber', '')
    Config.set('customer','customerid', "0")
    Config.set('customer','gender', "0")
    Config.set('customer','customername', '')
    Config.set('customer','nickname', '')
    Config.set('customer','bonuspercentage', "0")
    Config.set('customer','currentbonus', "0")
    Config.set('customer','inserteddate', str(datetime.datetime.now()))
    Config.set('customer','iscardinside', "0")
    Config.set('customer','cardmachinelogid', "0")
    Config.set('customer','ismoneytransfered', "0")
    Config.set('customer','playcount', "0")
    Config.set('customer','totalbet', "0")
    Config.set('customer','totalwin', "0")
    Config.set('customer','selectedgameid', "0")

    Config.set('customer','customerbalance', "0")
    Config.set('customer','currentbalance', "0")
    
    Config.set('customer','customerpromo', "0")
    Config.set('customer','currentpromo', "0")
    Config.set('customer','isrestartedsafely', "0")

if 'collecting' not in Config.sections():
    print("collecting eklendi")
    Config.add_section('collecting')    
    Config.set('collecting','cashableamount', "0")
    Config.set('collecting','restrictedamount', "0")
    Config.set('collecting','nonrestrictedamount', "0")

if 'collectcmd' not in Config.sections():
    print("collectcmd eklendi")
    Config.add_section('collectcmd')    
    Config.set('collectcmd','transactionid', "0")

if 'game' not in Config.sections():
    #print("customer eklendi")
    Config.add_section('game')
    Config.set('game','wagered', "0")
    Config.set('game','gamepromo', "0")
    Config.set('game','totalcoinin', "0")
    Config.set('game','wagertype', '')
    Config.set('game','progressivegroup', "0")
    Config.set('game','starteddate', str(datetime.datetime.now()))


if 'casino' not in Config.sections():
    Config.add_section('casino')
    Config.set('casino','casinoid', "1")
    Config.set('casino','casinoname', "")
    Config.set('casino','minstorebootnonetwork', "0")
SaveConfigFile()





try:
    G_CasinoId=Config.getint('casino','casinoid')
    if G_CasinoId==3:#Ambassador
        G_Machine_CardReaderModel="Eject"

except Exception as e:
    G_CasinoId=1

IsGuiReady=1
try:
    G_Machine_ScreenTypeId=Config.getint('machine','screentypeid')
except Exception as e:
    G_Machine_ScreenTypeId=0



try:
    G_Machine_TicketPrinterTypeId=Config.getint('machine','ticketprintertypeid')
except Exception as e:
    G_Machine_TicketPrinterTypeId=0

try:
    G_Machine_BillAcceptorTypeId=Config.getint('machine','billacceptortypeid')
except Exception as e:
    G_Machine_BillAcceptorTypeId=0


try:
    G_Casino_IsAssetNoAlwaysOne=Config.getint('machine','IsAssetNoAlwaysOne')
except Exception as e:
    G_Casino_IsAssetNoAlwaysOne=0


try:
    G_Machine_NewGamingDay=Config.getint('machine','newgamingday')
except Exception as e:
    G_Machine_NewGamingDay=0

try:
    G_Machine_IsLockedByAdmin=Config.getint('machine','islockedbyadmin')
except Exception as e:
    G_Machine_IsLockedByAdmin=0

try:
    G_Machine_AdminCards=Config.get('machine','admincards')
except Exception as e:
    G_Machine_AdminCards=""




if G_Machine_ScreenTypeId>0:
    IsGUIEnabled=1
    IsGUI_Type=1    # Qt GUI (PyQt5) - Default and most reliable





#G_Machine_ScreenTypeId: 7: 480 8:1280
if G_Machine_ScreenTypeId==7 or G_Machine_ScreenTypeId==8:
    IsGUI_Type=3#WXPYTHON
    IsGUI_Type=4#PYWEBVIEW
    IsGuiReady=0

if G_Machine_ScreenTypeId==9:
    IsGUI_Type=5
    IsGUIFullScreen=0
    try:
        threadQT = Thread(target = CreateGUI)
        threadQT.name="ThreadQT"
        threadQT.start()
    except Exception as e11:
        print("Exception threadQT")

#print("IsGUI_Type", IsGUI_Type, "G_Machine_ScreenTypeId", G_Machine_ScreenTypeId, "G_Machine_DeviceTypeId", G_Machine_DeviceTypeId)


#<CEFPYTHON>--------------------------------------------------------------------------
main_window=None
def CreateCEFPython():
    global main_window

    if IsGUI_Type==3:#HTML
        #check_versions()
        sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
        settings = {}
        if MAC:
            # Issue #442 requires enabling message pump on Mac
            # in Qt example. Calling cef.DoMessageLoopWork in a timer
            # doesn't work anymore.
            settings["external_message_pump"] = True

        cef.Initialize(settings)
        app = CefApplication(sys.argv)
        main_window = MainWindow()
        main_window.show()

        main_window.activateWindow()

        main_window.raise_()



        app.exec_()



        if not cef.GetAppSetting("external_message_pump"):
            app.stopTimer()
        del main_window  # Just to be safe, similarly to "del app"
        del app  # Must destroy app object before calling Shutdown
        cef.Shutdown()
#<CEFPYTHON>--------------------------------------------------------------------------




G_Machine_BonusId=0
G_Machine_BonusAmount=0
G_NextVisit_WonAmount=Decimal(0)
G_NextVisit_KioskBonusId=0
#<JAVASCRIPT EVENTS>--------------------------------------------------------------------------
def HandleJSEvent(title):
    if 2==2:
        if len(title)>0:
            value=title

            print("HTML BUTTON TIKLANDI" + value)
            global GUI_CurrentPage
            global CurrentHTML_CurrentStep
            global HTML_MachineNo
            global HTML_MachineType
            global IsWaitingAdminScreen

            global G_Machine_ReservationDate
            global G_Machine_ReservationCard
            global G_Machine_ReservationCustomername
            global IsGuiReady
            global JackpotWonAmount
            global IsCardReaderBusy

            global G_Machine_BonusId
            global G_Machine_BonusAmount

            global G_NextVisit_WonAmount
            global G_NextVisit_KioskBonusId


            if value=="divAdmin":
                IPAddress=get_lan_ip()
                ExecuteJSFunction2("ChangeText", "divAdminIPAddress",str(IPAddress))

            if value=="HTMLStarted":
                IsGuiReady=1
                ExecuteJSFunction("ResponseHelloPython", "Python")
                print("******************HTML STARTED!***********************")

                IPAddress=get_lan_ip()
                PrintAndSetAsStatuText("Started! " + IPAddress)

                if G_Machine_ScreenRotate>0:
                    ExecuteJS("document.body.style.setProperty('-webkit-transform', 'rotate("+str(G_Machine_ScreenRotate)+"deg)', null);")

            if value=="divBonusRequest":
                #ShowNotifyScreen("NOT READY","OK",5)
                print("Request Bonus")

                LastGameDiff=(datetime.datetime.now()-G_LastGame_Action).total_seconds()

                IsShowBonusRequest=1
                #if G_LastGame_IsFinished==1 and LastGameDiff<10:
                #    ShowNotifyScreen("BONUS ERROR","You can't request bonus while you play. Last game was " + str(int(LastGameDiff)) + " seconds ago",10)


                if IsShowBonusRequest==1:
                    AvailableBonusHTML=""
                    result = SQL_BonusRequestList()
                    Adet=0
                    Result=0
                    ErrorMessage=""
                    for row in result:
                        Result=int(row["Result"])
                        ErrorMessage=row["ErrorMessage"]
                        if Result>0:
                            Adet=Adet+1
                            Amount=int(row["Amount"])
                            AvailableBonusHTML=AvailableBonusHTML+"<input type=\"button\" value=\""+str(Amount)+" "+G_Machine_Currency+"\" class=\"BonusButtons\" onclick=\"BonusSelected("+str(Amount)+")\" />"
                            if Adet==3:
                                AvailableBonusHTML=AvailableBonusHTML+"<br>"
                
                    if Result>0:
                        ExecuteJSFunction("ShowBonusOptions", AvailableBonusHTML)
                    else:
                        ShowNotifyScreen("BONUS ERROR!",ErrorMessage,10)


            if value.startswith("divBonusAmount:")==True:
                GUI_ShowCustomerWindow()
                if G_Machine_BonusId>0:
                    IsShowBonusWindow=0
                    SQL_Safe_InsImportantMessage("Please wait until previous bonus transfer is completed!",68)
                    ShowNotifyScreen("PLEASE WAIT","Please wait until previous bonus transfer is completed!",3)
                    return
                Amount=value.replace("divBonusAmount:","")
                SQL_Safe_InsImportantMessage("Bonus request: " + str(Amount),68)

                GetMeter(0,"bonus")
                ShowNotifyScreen("PLEASE WAIT!","Bonus Transfer is pending!",40000)
                if Wait_Bakiye(2,0,"BillAcceptor")==0:
                    ShowNotifyScreen("BONUS ERROR!","System can't transfer bonus at the moment. Please try again later.",10)
                    SQL_Safe_InsImportantMessage("System can't transfer bonus at the moment. Please try again later.",68)
                    Komut_CancelBalanceLock()
                    return

                IsCardReaderBusy=1
                print("Yuklenecek bonus", Amount)
                ShowNotifyScreen("PLEASE WAIT!","Bonus Transfer is pending! ",10)

                GetMeter(0,"bonus2")

                SQL_Safe_InsImportantMessage("Bonus amount: " + str(Amount),69)

                #Once Yukleme SP'si, sonra Yuklemeye calis. Sonuca gore de Yukleme Finish SP'si
                G_Machine_BonusId=0
                ErrorMessage=""
                result = SQL_InsBonusRequest(Amount)
                for row in result:
                    G_Machine_BonusId=int(row["Result"])
                    ErrorMessage=row["ErrorMessage"]
                    Amount=int(row["RequestedBonus"])
                    G_Machine_BonusAmount=Amount

                if G_Machine_BonusId<=0:
                    ShowNotifyScreen("BONUS ERROR",ErrorMessage,10)
                    SQL_Safe_InsImportantMessage("BONUS ERROR: " + ErrorMessage,68)
                    Komut_CancelBalanceLock()
                    G_Machine_BonusId=0
                    IsCardReaderBusy=0

                if G_Machine_BonusId>0:
                    GUI_ShowCustomerWindow()#2021-07-08

                    JackpotWonAmount=Decimal(Amount)
                    ParaYukleSonuc=1
                    SQL_UpdBonusAsUsed(G_Machine_BonusId)
                    ParaYukleSonuc=Wait_ParaYukle(13)
                    Wait_Bakiye(11,1,"bonus")
                    if ParaYukleSonuc==1:
                        #2020-02-10: Savoy Bonus icin actik
                        if G_Machine_BonusId>0:
                            GetMeter(0,"bonus2")
                            time.sleep(0.5)
                            currentbonus=Decimal(Config.get("customer","currentbonus"))-G_Machine_BonusAmount;
                            Config.set('customer','currentbonus', str(currentbonus))

                            ShowNotifyScreen("SUCCESS!","Bonus Transfer is successful. We wish you good luck!",10)
                            SQL_Safe_InsImportantMessage("Bonus SUCCESS! Amount:  " + str(G_Machine_BonusAmount),92)
                            #Wait_Bakiye(11,1,"bonus")


                            print("Set card reader free-1****************")
                            IsCardReaderBusy=0#Bonus
                            print("Set card reader free-2****************")
                            G_Machine_BonusId=0
                            GUI_ShowCustomerWindow()
                        #<endif G_Machine_BonusId>0:
                        GUI_ShowCustomerWindow()
                    else:
                        ShowNotifyScreen("UNABLE TO TRANSFER BONUS","Bonus transfer to GM is not available at the moment. Please try again.",10)
                        SQL_Safe_InsImportantMessage("Bonus FAIL! Amount:  " + str(Amount),70)
                        G_Machine_BonusId=0
                    Komut_CancelBalanceLock()
                    time.sleep(1)#10 i,mis. 1 yaptim
                    GetMeter(0,"bonus2")


            if value=="divAdminEFTRequest":
                print("divAdminEFTRequest")
                Komut_EFT_RequestTransferLog()

            if value=="divAdminEFTBalance":
                print("divAdminEFTBalance")
                Komut_EFT_RequestCashoutAmount()

            if value=="divAdminEFTMinus":
                print("divAdminEFTMinus")
                Komut_ParaSilEFT(1,1)

            if value=="divAdminEFTPlus":
                print("divAdminEFTPlus")
                Komut_ParaYukleEFT(1,1)

            if value=="divBonus":
                IsShowBonusWindow=1
                if G_Machine_IsBonusGives==0:
                    IsShowBonusWindow=0
                    GUI_ShowCustomerWindow()
                    ShowNotifyScreen("BONUS IS NOT ACTIVE","This GM doesn't support bonus",3)

                #if IsCardReaderBusy==1:
                #    print("Card reader is busy!******************************")
                #    IsShowBonusWindow=0
                #    GUI_ShowCustomerWindow()
                #    ShowNotifyScreen("PLEASE WAIT","Please wait until previous transaction is closed!",3)

                if G_Machine_BonusId>0:
                    IsShowBonusWindow=0
                    GUI_ShowCustomerWindow()
                    ShowNotifyScreen("PLEASE WAIT","Please wait until previous bonus transfer is completed!",3)


                if IsShowBonusWindow==1:
                    GUI_CurrentPage="GUI_ShowBonus"
                    #<Here get customer bonus>#############################################
                    #ExecuteJSFunction2("ChangeText", "txtBonus","")
                    GUI_UpdateBonus()




                    if 2==2:
                        print("*****************************************************************************************")
                        try:
                            MaxPercentage=0
                            BetMaxValue=Decimal(0)
                            currentIndex=0
                            StaticZones=""
                            Labels=""
                            PercentColors=""
                            while currentIndex<len(G_Machine_WagerBonusFactors):
                                Item=G_Machine_WagerBonusFactors[currentIndex]
                                currentIndex=currentIndex+1

                                if 1==1:
                                    if Decimal(Item['wager'])>BetMaxValue:
                                        BetMaxValue=Decimal(Item['wager'])

                                    AddVirgul=""
                                    if len(StaticZones)>0:
                                        AddVirgul=","

                                    StaticZones=StaticZones+AddVirgul+"{ strokeStyle: \"" + Item['htmlcolour'] + "\", min: " + str(Item['startpercentage']) + ", max: " + str(Item['nextpercentage']) +" }"
                                    Labels=Labels + AddVirgul+ str(Item['startpercentage']) + ""
                                    PercentColors=PercentColors+AddVirgul+"[" + str(Item['startpercentage']) + ", \"" + Item['htmlcolour'] + "\"] "

                                    MaxPercentage=Decimal(Item['nextpercentage'])

                            StaticZones="[" + StaticZones + "]"
                            Labels="[" + Labels + "]"
                            PercentColors="[" + PercentColors + "]"
                    
                            #print("**********************************************")
                            #print("StaticZones", StaticZones)
                            #print("Labels", Labels)
                            #print("PercentColors", PercentColors)
                            #print("******************************")

                            ExecuteJSFunction5("InitGadgetValues",StaticZones, Labels, PercentColors, str(BetMaxValue), str(MaxPercentage))
                        except Exception as eBonusFill:
                            ExceptionHandler("eBonusFill",eBonusFill,0)
                        print("*****************************************************************************************")


                    if 1==1:
                        try:
                            customerid = Config.getint('customer', 'customerid')
                            # Original MSSQL procedure: tsp_GetCustomerAdditional
                            # Note: This procedure was not found in postgres-routines-in-sas.sql
                            # Using hybrid approach - queue operation instead of direct call
                            result = db_helper.queue_database_operation(
                                'tsp_GetCustomerAdditional',
                                [customerid, G_Machine_DeviceId],
                                'get_customer_additional'
                            )

                            for row in result:
                                
                                
                                AvailableBonus=Decimal(row["AvailableBonus"])
                                EarnedBonus=Decimal(Config.get("customer","earnedbonus"))
                                AvailableBonus=AvailableBonus+EarnedBonus
                                AvailableBonus=round(AvailableBonus, 4)
                                AvailableBonusInt=math.floor(AvailableBonus)
                                BonusDecimalPart=AvailableBonus-AvailableBonusInt


                                Config.set('customer','currentbonus', str(AvailableBonus))

                                AvailableBonusText="%s %s" % (AvailableBonus, G_Machine_Currency)
                                ExecuteJSFunction5("ChangeBonusValue", str(AvailableBonus), str(AvailableBonusInt), str(BonusDecimalPart), G_Machine_Currency, AvailableBonusText)
                        except Exception as ecardtype:
                            ExceptionHandler("tsp_GetCustomerAdditional", ecardtype, 0)





                    #</Here get customer bonus>#############################################

            if value=="divBalance":
                GUI_CurrentPage="GUI_ShowBalance"
                GUI_ShowBalance()

            if value=="divJackpot":
                GUI_CurrentPage="GUI_ShowJackpot"
                SQL_DeviceStatu(2)

            if value=="divSettingsCashout":
                print("*************************************************")
                print("Cashout")
                DoHandUserInput("kartcikart:")


            if value=="divNextVisitSelectedButton":
                SQL_InsKioskBonusWon()

            if value=="divNextVisitSelected":
                print("*************************************************")
                print("divNextVisitSelected",G_NextVisit_WonAmount,"G_NextVisit_KioskBonusId", G_NextVisit_KioskBonusId)
                SQL_InsKioskBonusWon()
                ShowNotifyScreen("Congratulations", "You won " + str(G_NextVisit_WonAmount) + " " + G_Machine_Currency + "! Please re-insert your card to active your promo.",5)


            if value=="divNextVisit":
                CheckNextVisit()



            if value=="divSettingsReserve":
                print("*************************************************")
                print("Cashout and reserve")

                G_Machine_ReservationDate=datetime.datetime.now()
                G_Machine_ReservationCard=G_User_CardNo
                G_Machine_ReservationCustomername=str(Config.getint('customer','customerid')) + " " + Config.get('customer','nickname')

                ShowNotifyScreen("Reservation", "Please Reject your card in 30 seconds to reserve GM for 10 minutes",10)


            if value=="divMessages":
                GUI_CurrentPage="divMessages"
                result = SQL_GetCustomerCurrentMessages()
                Messages=""
                for row in result:
                    EkstraStyle=""
                    IsRead=int(row["IsRead"])
                    if IsRead==1:
                        EkstraStyle="MessageRowReaded"
                    Messages = Messages + "<div class='MessageRow "+EkstraStyle+"' onclick='ShowMessage("+str(row["MessageId"])+")'>"+ DecodeHTMLChars(str(row["MessageName"]))+"</div>";

                ExecuteJSFunction2("ChangeHTML", "divMessagesContent",Messages)


            if value.startswith("divMessagesAward")==True:
                AwardId=int(value.split('|')[1])
                MessageId=int(value.split('|')[2])
                print("AwardId", AwardId,"MessageId",MessageId)
                result=SQL_UpdMessageAwardAttempt(MessageId)
                for row in result:
                    Result=int(row["Result"])
                    ErrorMessage=row["ErrorMessage"]
                    if Result<0:
                        ShowNotifyScreenWithButtons(DecodeHTMLChars("ERROR!"),DecodeHTMLChars(ErrorMessage), 0,1,0)
                    else:
                        ShowNotifyScreenWithButtons(DecodeHTMLChars("PLEASE WAIT"),DecodeHTMLChars("Please wait while award is being credited..."), 0,1,0)
                        
                        #<Award Yukle>
                        if Wait_Bakiye(2,0,"oyun kilitlenesiye-1")==0:
                            ShowNotifyScreen("AWARD ERROR!","System can't transfer award at the moment. Please try again later.",10)
                            return
                        GetMeter(0,"award")

                        if 1==1:
                            JackpotWonAmount=Decimal(row["AwardAmount"])
                            ParaYukleSonuc=1
                            ParaYukleSonuc=Wait_ParaYukle(13)
                            if ParaYukleSonuc==1:
                                SQL_UpdMessageAwardAsUsed(MessageId)
                                ShowNotifyScreen("AWARD SUCCESSLY!","Successfully credited " + str(JackpotWonAmount) + ". Good luck!",10)
                            else:
                                ShowNotifyScreen("UNABLE TO TRANSFER Award","Award transfer to GM is not available at the moment. Please try again.",10)
                                SQL_Safe_InsImportantMessage("Award FAIL! Amount:  " + str(JackpotWonAmount),70)
                        #</Award Yukle>

            if value.startswith("divMessagesShow")==True:
                MessageId=int(value.split('|')[1])
                result=SQL_GetCustomerMessage(MessageId)

                MessageId=0
                AwardId=0
                AwardAmount=0
                IsAwardUsed=0
                IsAwardActive=0
                for row in result:
                    MessageName=str(row["MessageName"])
                    try:
                        MessageId=int(row["MessageId"])
                        AwardId=int(row["AwardId"])
                        AwardAmount=int(row["AwardAmount"])
                        IsAwardUsed=int(row["IsAwardUsed"])
                        IsAwardActive=int(row["IsAwardActive"])
                    except Exception as esql:
                        print("Exception Parse")
                    Message=""
                    if IsAwardUsed==0 and AwardAmount>0 and AwardId>0 and IsAwardActive==1:
                        Message="<br><div class='borderMessageAward' onclick='ShowMessageAwardClicked("+str(AwardId)+","+str(MessageId)+")'>"+str(AwardAmount)+" " + G_Machine_Currency + " AWARD</div>"
                    Message=DecodeHTMLChars(str(row["Message"])) + Message
                    ShowNotifyScreenWithButtons(DecodeHTMLChars(MessageName),Message, 0,1,0)

                

            if value=="divDiscountTake":
                result = SQL_GetSlotCustomerDiscountCalc(1)
                for row in result:
                    Result=int(row["AvailableDiscount"])
                    if Result>0:
                        GUI_ShowBonus()
                        ShowNotifyScreen("DISCOUNT SUCCESSLY!",row["ErrorMessage"],10)
                    else:
                        ShowNotifyScreen("DISCOUNT FAIL!",row["ErrorMessage"],10)
                

            if value=="divDiscount":
                GUI_CurrentPage="GUI_Discount"
                DiscountText="<span style='font-size:20px; font-weight:bold;'><br><br>NO DISCOUNT AVAILABLE</span>"

                result = SQL_GetSlotCustomerDiscountCalc(0)
                for row in result:
                    AvailableDiscount=Decimal(row["AvailableDiscount"])

                    DiscountText=""
                    DiscountText=DiscountText + "<table>"

                    DiscountText=DiscountText + "<tr><td><span style='font-size:35px; margin:5px;'>Net Result</span></td>"
                    DiscountText=DiscountText + "<td><span style='font-size:35px;font-weight:bold; margin:5px;'>"+str(row["NetResult"])+"</span></td></tr>"

                    DiscountText=DiscountText + "<tr><td><span style='font-size:35px; margin:5px;'>Given Discount</span></td>"
                    DiscountText=DiscountText + "<td><span style='font-size:35px;font-weight:bold';  margin:5px;>"+str(row["Discount"])+"</span></td></tr>"
                    
                    if AvailableDiscount>0:

                        DiscountText=DiscountText + "<tr><td><span style='font-size:35px; margin:5px;'>Discount %</span></td>"
                        DiscountText=DiscountText + "<td><span style='font-size:35px;font-weight:bold';  margin:5px;>"+str(row["DiscountPercentageInt"])+"</span></td></tr>"
                        
                        if AvailableDiscount>=5:
                            DiscountText=DiscountText + "<tr><td><span style='font-size:35px; margin:5px;'>Available</span></td><td>"
                            DiscountText=DiscountText + "<input type='button' value='"+ str(row["AvailableDiscount"]) +" "+G_Machine_Currency+"' class='BarButtons' style='font-size:35px;  margin:5px;' onclick=\"SendData2Python('divDiscountTake')\" />"
                            DiscountText=DiscountText + "</td>"

                    DiscountText=DiscountText + "</table>"
    


                ExecuteJSFunction2("ChangeHTML", "divDiscountText",DiscountText)

            if value=="divBar":
                GUI_CurrentPage="GUI_Bar"
                result = SQL_GetProductCategories()
                ProductCategories=""
                for row in result:
                    ProductCategories = ProductCategories + "<input type='button' value='"+ row["CategoryName"]+"' class='BarButtons' onclick='CategorySelected(" + str(row["CategoryId"]) + ")' />";



                ExecuteJSFunction2("ChangeHTML", "divBarCategoriesList",ProductCategories)

            if value.startswith("divBarOrder")==True:
                Products=value.split('|')[1]
                print("Products", Products)
                SQL_InsProductOrderBySlot(Products)
                GUI_ShowCustomerWindow()
                ShowNotifyScreen("ORDER IS PLACED","Your order will be ready soon.", 5)

            if value.startswith("divBarClicked")==True:
                Sender=value.split('|')[1]
                Id=value.split('|')[2]
                print("Sender", Sender + " ID", Id)

                if Sender=="Category":
                    resultProduct=SQL_GetProductsAndSubCategoriesSlot(Id,1)
                    resultCategory=SQL_GetProductsAndSubCategoriesSlot(Id,2)

                    ProductCategories=""
                    for row in resultCategory:
                        ProductCategories = ProductCategories + "<input type='button' value='"+ DecodeHTMLChars(str(row["CategoryName"]))+"' class='BarButtons' onclick='CategorySelected(" + str(row["CategoryId"]) + ")' />";       

                    if len(ProductCategories)>0:
                        ProductCategories=ProductCategories+ "<br />"

                    for row in resultProduct:
                        ProductCategories = ProductCategories + "<input type='button' value='"+ DecodeHTMLChars(str(row["ProductName"]))+"'  class='BarButtons'  onclick=\"ProductSelected(" + str(row["ProductId"]) + ",'" + DecodeHTMLChars(str(row["ProductName"])) + "','" + DecodeHTMLChars(str(row["CategoryName"])) + "','" + DecodeHTMLChars(str(row["FullCategoryName"])) + "')\" />";       


                    ExecuteJSFunction2("ChangeHTML", "divBarCategoriesList",ProductCategories)


            if value=="divSettings":
                GUI_CurrentPage="GUI_ShowSettings"

            if value=="divCustomer":
                GUI_CurrentPage="GUI_ShowCustomerWindow"




            if value.startswith("divKeyboard|cancel|")==True:
                if CurrentHTML_CurrentStep.startswith("adminconfiguration|")==True:
                    ExecuteJSFunction("CloseDiv", "divKeyboard")
                    ExecuteJSFunction("ShowDiv", "divAdmin")


            if value.startswith("divKeyboard|ok|")==True:
                enteredvalue=value.split("|")[2]
                print("enteredvalue:", enteredvalue)
            
                if CurrentHTML_CurrentStep=="adminconfiguration|machinename":
                    HTML_MachineNo=enteredvalue
                    print("Machine No", HTML_MachineNo)

                    CurrentHTML_CurrentStep="adminconfiguration|machinetype"
                    ExecuteJSFunction2("AskQuestion", "Please type Machine Type: 1:NOV, 2:EGT, 3: IGT 4:OCT","divAdminConfiguration")

                elif CurrentHTML_CurrentStep=="adminconfiguration|machinetype":
                    HTML_MachineType=enteredvalue
                    print("Machine Type", HTML_MachineType)
                    SQL_ChangeDeviceNameAndType(HTML_MachineNo,HTML_MachineType)
                    ExecuteJSFunction("CloseDiv", "divKeyboard")
                    ExecuteJSFunction("ShowDiv", "divAdmin")
                


            if value.startswith("divAdmin"):

                if value=="divAdminJackpot":
                    HandUserInput("jackpottest:")
                
                if value=="divAdminBonus":
                    HandUserInput("bonustest:")


                if value=="divAdminLock":
                    Kilitle("0")

                if value=="divAdminUnLock":
                    Ac("divAdminUnlock")

                if value=="divAdminRestart":
                    print("Reset At")
                    ExecuteCommand("restart")

                if value=="divAdminHandpay":
                    GetMeter(0,"handpay")
                    Komut_BakiyeSorgulama(11,1,"handpayadmin-1")
                    Wait_RemoteHandpay()
                    Komut_BakiyeSorgulama(11,1,"handpayadmin-2")
                    GetMeter(0,"handpay2")

                if value=="divAdminBalance":
                    Wait_Bakiye(11,1,"balanceadmin")

                if value=="divAdminMeter":
                    GUI_ShowIfPossibleMainStatu("Meter requested!")
                    GetMeter(0,"adminmeter")

            
                if value=="divAdminConfiguration":
                    ExecuteJSFunction("CloseDiv", "divAdmin")
                    CurrentHTML_CurrentStep="adminconfiguration|machinename"
                    ExecuteJSFunction2("AskQuestion", "Please type machine no","divAdminConfiguration")

                if value=="divAdminReadAsset":
                    Komut_ReadAssetNo()

                if value=="divAdminRegisterSAS":
                    Komut_RegisterAssetNo()

                if value=="divAdminClearBalance":
                    DoHandUserInput("sifirla:")

                if value=="divAdminExit":
                    IsWaitingAdminScreen=0
                    print("Exit admin card")
                    if IsCardInside==1:
                        GUI_ShowCustomerWindow()
                    else:
                        GUI_ShowIdleWindow()
                    

            if value=="divNotifyOk":
                print("Clicked To OK")
        
            if value=="divNotifyCancel":
                print("Clicked To Cancel")

            if value=="divNextVisitByTurnoverClicked":
                print("*************************************************")
                print("CheckNextVisit_ByTurnover")
    
                result = SQL_GetNextVisit_ByTurnover(1)
                ProductCategories=""
                for row in result:
                    Result=int(row["Result"])

                    BoxesHtml =""
                    if Result>0:
                        BoxesHtml += "<center><span style='font-size:25'>"+str(row["AvailablePrize"])+" is uploaded to your account. Please re-insert your card again</span></center><br><br>"
                        ShowNotifyScreenWithButtons("CONGRATULATIONS",BoxesHtml, 20,1,0)
                    else:
                        ShowNotifyScreenWithButtons("FAIL",row["ErrorMessage"], 20,1,0)

#</JAVASCRIPT EVENTS>-------------------------------------------------------------------------



#<PYWEBVIEW>--------------------------------------------------------------------------
class HtmlApi:
    def __init__(self):
        print("Inited HTML")

    def init(self):
        response = {
            'message': 'Hello from Python {0}'.format(sys.version)
        }
        return response

    def DoSomethingFromJavascript(self, parametre):
        print("DoSomethingFromJavascript params", parametre)
        HandleJSEvent(parametre)

        response = {
            'message': 'Hello {0}!'.format(parametre)
        }
        return response

    def error(self):
        raise Exception('This is a Python exception')
#</PYWEBVIEW>--------------------------------------------------------------------------



#<WXPYTHON>--------------------------------------------------------------------------

WXBrowser=None

# Only define MyBrowser class if wxPython is available
if WX_AVAILABLE and WX_HTML2_AVAILABLE:
    class MyBrowser(wx.Frame):#wx.Dialog
        
        #Function binding to the page loading 
        def OnPageTitleChanged(self, event):
            title = self.browser.GetCurrentTitle()

            HandleJSEvent(title)


        def __init__(self, *args, **kwds):
          global WXBrowser
          wx.Dialog.__init__(self, *args, **kwds)
          sizer = wx.BoxSizer(wx.VERTICAL)
          self.browser = wx.html2.WebView.New(self)
          sizer.Add(self.browser, 1, wx.EXPAND, 10)
          self.SetSizer(sizer)
          self.SetSize((850, 550))
          
          if platform.system().startswith("Window")==False:
              self.ShowFullScreen(True)

          WXBrowser=self.browser
        
          #Binding the function the event to the function. 
          self.Bind(wx.html2.EVT_WEBVIEW_TITLE_CHANGED, self.OnPageTitleChanged, self.browser)
else:
    # Dummy class when wxPython is not available
    class MyBrowser:
        def __init__(self, *args, **kwds):
            print("[ERROR] MyBrowser cannot be created - wxPython not available")

def CreateHTMLWX():
    if not WX_AVAILABLE or not WX_HTML2_AVAILABLE:
        print("[WARNING] HTML GUI cannot start - wxPython not available or incomplete")
        print("[INFO] Install wxPython with: pip install wxpython")
        return
        
    app = wx.App()
    dialog = MyBrowser(None, -1)
    if WINDOWS==True:
        dialog.browser.LoadURL("file:///D:/msvn/projectcasino/cardintegration/raspberry/guiwx.html")
    else:
        dialog.browser.LoadURL("file:///home/soi/dev/spark-sas2/guiwx.html")

    #dialog.browser.LoadURL("file:///home/soi/dev/spark-sas2/guiwx.html")
    #dialog.browser.LoadURL("http://www.youtube.com")
    dialog.Show()
    app.MainLoop()
#<WXPYTHON>--------------------------------------------------------------------------




def CheckNextVisit():
    global G_NextVisit_WonAmount
    global G_NextVisit_KioskBonusId
    print("*************************************************")
    print("divNextVisit")
    
    BoxesHtml = "";
    BoxesHtml += "<table style='width:100%'>";
    
    IsRightExist=0
    result = SQL_GetNextVisit()
    ProductCategories=""
    for row in result:
        IsWon=int(row["IsWon"])
        if IsWon==1:
            G_NextVisit_WonAmount=Decimal(row["Prize"])
            G_NextVisit_KioskBonusId=int(row["KioskBonusId"])
        IsRightExist=1
    
    if IsRightExist==1:
        ExecuteJSFunction("ParseRowBonusBoxesJSON",json.dumps(result, cls=DecimalEncoder))
        say=0
        for i in range(1, 13):
            say=say+1
    
            renk=random.randint(1, 5)
            Bg = "blue";
            #if renk == 2:
            #    Bg = "purple"
            #if renk == 3:
            #    Bg = "blue"
    
            #if renk == 4:
            #    Bg = "green"
    
            #if renk == 5:
            #    Bg = "#FB00FF"
    
    
            BoxesHtml += "<td>"
            BoxesHtml += "<center>"
    
    
            BoxesHtml += "<input type='button' class='ButtonNextVisit' style='height:85px; background-color:"+Bg+"' id='divBonusText" + str(i) + "'  OnClick=\"BoxSelected(this," + str(i) + ")\" value='" +G_Casino_Name + "' />"
    
    
            BoxesHtml += "</center>"
            BoxesHtml += "</td>"
    
    
            if say % 4 == 0:
                BoxesHtml += "</tr>";
        #for bitti
    #end if IsRightExist==1
    
    BoxesHtml += "</table>"
    if IsRightExist==1:
        ShowNotifyScreen("NEXT VISIT", BoxesHtml,60)





def CheckNextVisit_ByTurnover():
    print("*************************************************")
    print("CheckNextVisit_ByTurnover")
    
    result = SQL_GetNextVisit_ByTurnover(0)
    ProductCategories=""
    for row in result:
        Result=int(row["Result"])
        MaxPrizeAmount=int(row["MaxPrizeAmount"])
        TodayWon=int(row["TodayWon"])

        NextVisitMaxText=str(row["NextVisitMaxText"])

        if len(NextVisitMaxText)>0 and MaxPrizeAmount>0 and MaxPrizeAmount!=TodayWon:
            BoxesHtml =""
            BoxesHtml += "<center><span style='font-size:24'>"+str(row["NextVisitMaxText"])+"</span></center><br>"
            BoxesHtml += "<center><span style='font-size:26'>"+str(row["NextVisitCurrentText"])+"</span></center><br>"

            if Result>0:
                BoxesHtml += "<center><input type='button' class='ButtonNextVisit' style='height:65px; font-size:25px; background-color:green' OnClick=\"PythonCustomerNavIconClicked('divNextVisitByTurnoverClicked')\" value='Redeem " + str(row["AvailablePrize"]) + "' /></center>"

            ShowNotifyScreenWithButtons("NEXT VISIT",BoxesHtml, 60,1,0)




def CreateHTMLGui():
    # Use wxPython WebView as primary HTML GUI (works on all platforms including ARM)
    CreateHTMLWX()

    # CEF Python is only available on x86_64, not on ARM/Raspberry Pi
    #CreateCEFPython()

if IsGUI_Type==3:
    try:
        threadGUIHtml = Thread(target = CreateHTMLGui)
        threadGUIHtml.name="CreateHTMLGui"
        threadGUIHtml.start()
    except Exception as e11:
        print("Exception threadGUIHtml")



def SetMachineStatu(statumsg):
    global G_Machine_Statu
    G_Machine_Statu=statumsg


LastMessageImpLevel=0
def PrintAndSetAsStatuTextWithLevel(statumsg, level):
    try:
        global LastMessageImpLevel
        if LastMessageImpLevel>level:
            return
        LastMessageImpLevel=level

        SetMachineStatu(statumsg)
        #print(statumsg)
    except Exception as e11:
        print("Exception on PrintAndSetAsStatuTextWithLevel")

def PrintAndSetAsStatuText(statumsg):
    SetMachineStatu(statumsg)
    GUI_ShowIfPossibleMainStatu(statumsg)
    print(statumsg)


Global_ParaSifirla_84=0
Global_Count_YanitHandle=0
Yukle_FirstTransaction=0
Yukle_LastTransaction=0
Global_ParaYukleme_TransferStatus="0"
IsWaitingForParaYukle=0
CashIn_CompletedBy=""
def Wait_ParaYukle(transfertype):
    #LE:2020-09-08
    global IsWaitingForParaYukle
    IsWaitingForParaYukle=1
    global CashIn_CompletedBy

    global G_SAS_LastAFTOperation
    G_SAS_LastAFTOperation="Yukle"

    global Global_ParaYukleme_TransferStatus
    Global_ParaYukleme_TransferStatus="0";

    global Yukle_FirstTransaction
    Yukle_FirstTransaction=0
    
    global Yukle_LastTransaction
    Yukle_LastTransaction=0

    global Last_ParaYukle_TransferType
    Last_ParaYukle_TransferType=transfertype

    global Global_Count_YanitHandle
    Global_Count_YanitHandle=0

    WaitParaYukle_Date=datetime.datetime.now()

    try:
        Error_87=0
        Error_87_Tolerance=10


        #<Status'e yazdirmak icin>--------------------------------------------
        customerbalance=Decimal(Config.get("customer","customerbalance"))
        customerpromo=Decimal(Config.get("customer","customerpromo"))

        if transfertype==11 or transfertype==10:
            customerbalance=JackpotWonAmount
            customerpromo=0

        if transfertype==13:
            customerbalance=JackpotWonAmount

        if transfertype==1:#bill acceptordan atilan para!
            customerbalance=Billacceptor_LastCredit
            customerpromo=0
        #</Status'e yazdirmak icin>--------------------------------------------

        SQL_Safe_InsImportantMessage("Cashin is started C:" + str(customerbalance) + " P:" + str(customerpromo),71)

        SayKomutSent=0
        SayKomutBekliyor=0
        Komut_ParaYukle(1,transfertype)
        LastCommandDate_ParaYukle=datetime.datetime.now()

        PrintAndSetAsStatuText("%s" % ('Waiting for money upload'))
        while (IsWaitingForParaYukle==1):
            time.sleep(0.003)
            LastCommandDate_ParaYukle_Diff=(datetime.datetime.now()-LastCommandDate_ParaYukle).total_seconds()
            FirstCommandDate_ParaYukle_Diff=(datetime.datetime.now()-WaitParaYukle_Date).total_seconds()

            SayKomutBekliyor=SayKomutBekliyor+1

            LastCommandDiff=(datetime.datetime.now()-Last_ParaYukleDate).total_seconds()

            if IsDebugAutoParaYukleYanit==1:
                IsWaitingForParaYukle=0

            if Global_ParaYukleme_TransferStatus=="MT":
                #SQL_Safe_InsImportantMessage("Try Cash-In again MT",99)
                Komut_ParaYukle(0,transfertype)
                LastCommandDate_ParaYukle=datetime.datetime.now()
                Global_ParaYukleme_TransferStatus=""

            if Global_ParaYukleme_TransferStatus=="87":
                PrintAndSetAsStatuText("Money Upload Answer S:87")
                Error_87=Error_87+1
                
                #Igor!
                if Error_87>Error_87_Tolerance and transfertype!=1:
                    break;
                

            if Global_ParaYukleme_TransferStatus=="84":
                PrintAndSetAsStatuText("Cant transfer big money")
                time.sleep(1)
                break;

            if Global_ParaYukleme_TransferStatus=="FF":
                PrintAndSetAsStatuText("No transfer information available. Code: FF")
                time.sleep(1)
                break;

            if Global_ParaYukleme_TransferStatus=="93":
                PrintAndSetAsStatuText("Asset number zero or does not match.")
                time.sleep(1)
                break;

            if Global_ParaYukleme_TransferStatus=="82":
                PrintAndSetAsStatuText("Not a valid transfer function S:82")
                time.sleep(1)
                break;

            if Global_ParaYukleme_TransferStatus=="83":
                PrintAndSetAsStatuText("Not a valid transfer amount S:83")
                time.sleep(1)
                break;

            if Global_ParaYukleme_TransferStatus=="C0":
                Komut_Interragition("C0")
                #PrintAndSetAsStatuText("Not compatible with current transfer in progress")
                #time.sleep(0.5)
                break;





            #if IsWaitingForParaYukle==1 and ((SayKomutBekliyor%40==0 and G_Machine_IsRulet==0) or (G_Machine_IsRulet==1 and SayKomutBekliyor%100==0)):
            if IsWaitingForParaYukle==1 and LastCommandDate_ParaYukle_Diff>=2.5:
                print("Para yukle again")

                if IsWaitingForParaYukle==1:
                    Komut_Interragition("ParaYukle Timeout")
                    time.sleep(0.3)
                    Komut_Interragition("ParaYukle Timeout")
                    time.sleep(0.3)

                #2021-11-12 Apex degil ise and G_Machine_DeviceTypeId!=10
                if IsWaitingForParaYukle==1:
                    Komut_ParaYukle(0,transfertype)
                    LastCommandDate_ParaYukle=datetime.datetime.now()
                    SayKomutSent=SayKomutSent+1
                else:
                    print("*********** NO NEED TO FOR CASHIN 1*******************")
                    print("*********** NO NEED TO FOR CASHIN 2*******************")



            if (transfertype==10 or transfertype==11)==True and SayKomutSent>=80:
            
                Komut_ParaYukle(0,transfertype)
                LastCommandDate_ParaYukle=datetime.datetime.now()
                SayKomutSent=SayKomutSent+1

                Global_ParaYukleme_TransferStatus="-1"
                PrintAndSetAsStatuText("Jackpot screen check! Maybe Jackpot is not in balance!")
                SQL_InsImportantMessageByWarningType("Jackpot screen check! Maybe Jackpot is not in balance!",26,22)
                break;

            if SayKomutSent>30:
                Global_ParaYukleme_TransferStatus="-1"
                PrintAndSetAsStatuText("Cant transfer money")
                SQL_InsImportantMessage("Cant transfer money",26)
                break;

        # or Global_ParaYukleme_TransferStatus=="C0"'i silelim diye dusundum. 2019-01-30
        if (Global_ParaYukleme_TransferStatus=="87" and Error_87>Error_87_Tolerance) or Global_ParaYukleme_TransferStatus=="84" or Global_ParaYukleme_TransferStatus=="FF" or Global_ParaYukleme_TransferStatus=="-1" or Global_ParaYukleme_TransferStatus=="83" or Global_ParaYukleme_TransferStatus=="89" or Global_ParaYukleme_TransferStatus=="82" or Global_ParaYukleme_TransferStatus=="93":
            print("Return 0 yaptik...")
            SQL_Safe_InsImportantMessage("Cashin is failed S:" + str(Global_ParaYukleme_TransferStatus),72)
            return 0

        #print("Para yuklendi")
    
    
        PrintAndSetAsStatuText("%s" % ('Good luck!'))
        SetMachineStatu("OK-Money Upload")
        Config.set('customer','ismoneytransfered', "1")
        SaveConfigFile()
        AddParaYukleInfo=""
        if Global_ParaYukleme_TransferStatus=="MT":
            AddParaYukleInfo=" OK by " + CashIn_CompletedBy
        SQL_Safe_InsImportantMessage("Cashin is finished! " + str(Global_ParaYukleme_TransferStatus) + AddParaYukleInfo,73)

        return 1

    except Exception as eWaitParaYukle:
        ExceptionHandler("eWaitParaYukle",eWaitParaYukle,1)

    SQL_Safe_InsImportantMessage("Cashin is finished Exception",74)
    return 0


Sifirla_FirstTransaction=0
Sifirla_LastTransaction=0


Sifirla_Bakiye=0
Sifirla_Promo=0

G_Cashout_SOS=0
Step_Parasifirla="0"
Global_ParaSilme_TransferStatus=""
WaitingParaSifirla_PendingCount=0
FaultCount_WaitingParasifirla=0
IsWaitingForBakiyeSifirla=0
def Wait_ParaSifirla():
    try:
        global G_Cashout_SOS

        #LE: 2021-07-23
        global Sifirla_Bakiye
        Sifirla_Bakiye=0

        global Sifirla_Promo
        Sifirla_Promo=0


        global Step_Parasifirla
        Step_Parasifirla="0"

        global Global_ParaSilme_TransferStatus
        Global_ParaSilme_TransferStatus="0"
        global IsWarnedForTakeWin
        IsWarnedForTakeWin=0
        global G_SAS_LastAFTOperation
        G_SAS_LastAFTOperation="Sifirla"
        GUI_ShowIfPossibleMainStatu("Waiting for AFT cashout")
        print("************ Para sifirla ***************** ")
        global IsWaitingForBakiyeSifirla
        IsWaitingForBakiyeSifirla=1

        global WaitingParaSifirla_PendingCount
        WaitingParaSifirla_PendingCount=0

        global FaultCount_WaitingParasifirla
        FaultCount_WaitingParasifirla=0

        global Sifirla_FirstTransaction
        Sifirla_FirstTransaction=0

        global Sifirla_LastTransaction
        Sifirla_LastTransaction=0

        global Global_Count_YanitHandle
        Global_Count_YanitHandle=0

        #SQL_InsException("ParaSifirla Started","")

        Step_Parasifirla="1"
        try:
            SQL_Safe_InsImportantMessage("Cashout is started " + str(Yanit_BakiyeTutar),75)
        except Exception as eImporotant:
            print("Cashout is started err")

        AgainDrawCommandTolerance=40
        if G_Machine_DeviceTypeId==6:
            AgainDrawCommandTolerance=120

        if Cashout_Source==123:
            AgainDrawCommandTolerance=30


        Step_Parasifirla="2"

        SayKomutBekliyor=0
        Step_Parasifirla="2.1"
        Komut_ParaSifirla(1)
        Step_Parasifirla="2.2"
        Count_SentSifirlaCommand=1
        time.sleep(0.05)

        Step_Parasifirla="3"
        PrintAndSetAsStatuTextWithLevel("%s%s" % ('Waiting for Money Erase:', IsWaitingLoopOnSASPooling),10)
        Step_Parasifirla="3.1"
        while (IsWaitingForBakiyeSifirla==1):
            try:
                Step_Parasifirla="4." + str(Count_SentSifirlaCommand)
                time.sleep(0.05)
                SayKomutBekliyor=SayKomutBekliyor+1

                LastCommandDiff=(datetime.datetime.now()-Last_ParaSifirlaDate).total_seconds()

                Step_Parasifirla="5." + str(Count_SentSifirlaCommand)
                if SayKomutBekliyor%16==0:
                    Step_Parasifirla="6." + str(Count_SentSifirlaCommand)
                    print('Para sifirlama bekleniyor IsWaitingLoopOnSASPooling:', IsWaitingLoopOnSASPooling, datetime.datetime.now())

                Step_Parasifirla="7." + str(Count_SentSifirlaCommand)
                if IsDebugAutoBakiyeSifirlaYanit==1:
                    Step_Parasifirla="8"
                    IsWaitingForBakiyeSifirla=0
                    SQL_Safe_InsImportantMessage("Cashout is completed. AutoDebug",88)
                    #print('Para sifirlamayi beklemeye gerek yok ')


                

                if SayKomutBekliyor%AgainDrawCommandTolerance==0 and IsWaitingForBakiyeSifirla==1:
                    Step_Parasifirla="9." + str(Count_SentSifirlaCommand)
                    print('Sent sifirlama command again', datetime.datetime.now())
                    Step_Parasifirla="10." + str(Count_SentSifirlaCommand)

                    if IsWaitingForBakiyeSifirla==1:
                        Step_Parasifirla="11." + str(Count_SentSifirlaCommand)
                        Komut_Interragition("50!")
                        #2021-10-09  time.sleep(0.2)#2 idi

                        #2021-10-18: Tekrar para sifirlama gondersin eger cashout butonuna basilirsa...
                        if Cashout_Source==123:
                            Komut_ParaSifirla(0)

                    #2021-10-09 Kaldirdim...
                    #if IsWaitingForBakiyeSifirla==1 and SayKomutBekliyor%(AgainDrawCommandTolerance*2)==0:
                    #    Step_Parasifirla="12." + str(Count_SentSifirlaCommand)
                        
                    #    #2021-07-23 tekrardan kaldirdim.
                    #    #Komut_ParaSifirla(0) #20210127 'de kaldirmisim bunu. neden acaba?

                    #    Step_Parasifirla="13." + str(Count_SentSifirlaCommand)
                    #    Count_SentSifirlaCommand=Count_SentSifirlaCommand+1
                    #    if IsWaitingForBakiyeSifirla==1:
                    #        time.sleep(0.2)#2 idi
                    #        Step_Parasifirla="14." + str(Count_SentSifirlaCommand)
                    #        Komut_Interragition("50!.")
                    #        Step_Parasifirla="15." + str(Count_SentSifirlaCommand)
                    


                if SayKomutBekliyor%40==0 and IsWaitingForBakiyeSifirla==1:
                    Step_Parasifirla="16." + str(Count_SentSifirlaCommand)
                    if G_Machine_DeviceTypeId==6:
                        Step_Parasifirla="17." + str(Count_SentSifirlaCommand)
                        Komut_Interragition("MEGAJACK!")
                    else:
                        Step_Parasifirla="18." + str(Count_SentSifirlaCommand)
                        if SayKomutBekliyor>80:
                            Step_Parasifirla="19." + str(Count_SentSifirlaCommand)
                            Komut_Interragition("ENSON!")


                #2 dk suruyor burasi 
                #if (SayKomutBekliyor%400==0 and G_Machine_IsRulet==0):
                #if (Count_SentSifirlaCommand%25==0 and G_Machine_IsRulet==0) and IsWaitingForBakiyeSifirla==1:
                if Count_SentSifirlaCommand%25==0 and IsWaitingForBakiyeSifirla==1:
                    
                    #2021-10-06 Sadece alttakini ekledim.
                    OpenCloseSasPort(1,0)

                    Step_Parasifirla="20." + str(Count_SentSifirlaCommand)
                    SQL_Safe_InsImportantMessage("S.O.S. Money cannot be collected.",75)
                    Step_Parasifirla="20." + str(Count_SentSifirlaCommand)
                    PrintAndSetAsStatuTextWithLevel("S.O.S. Money cannot be collected.",11)
                    Step_Parasifirla="21." + str(Count_SentSifirlaCommand)
                    G_Cashout_SOS=G_Cashout_SOS+1
                    if G_Cashout_SOS>8:
                        SQL_InsImportantMessageByWarningType("Restart S.O.S.",0,0)
                        ExecuteCommand("restart")
                    #Komut_Interragition("SasPortIsOpenedAndClosed-x")

            except Exception as eSifirla:
                print("Exception on Sifirla")

        #SQL_InsException("ParaSifirla finished","")
        PrintAndSetAsStatuTextWithLevel("OK-Money Erase",11)

    except Exception as e1:
        ExceptionHandler("Error on Money Collect",e1,1)
        PrintAndSetAsStatuTextWithLevel("Error on Money Collect..",11)
        
    
    
def Wait_Safe_Bakiye(sender,isforbilgi,sendertext):
    processGameoperation = Thread(target=Wait_Bakiye, args=(sender,isforbilgi,sendertext))
    processGameoperation.name="SafeBakiye";
    processGameoperation.start()


Bakiye_WaitingForGameLockCount=0
IsWarnedForTakeWin=0
LastCommand_Bakiye_Sender=0
#sender: 1:cardin 2: cardout 3:restart 4:jackpot 5:87TS 6:81TS 7:9FTS   8:82TS  9:84TS   10:83TS   11:BakiyeSorgula  12:Restarttan sonra, 13: ekran wallet buton
def Wait_Bakiye(sender,isforbilgi,sendertext='UndefinedWaitBakiye'):
    print("***************************************************************")
    print("<Wait_Bakiye entered:>------------------------------------", isforbilgi, sendertext)
    global IsWaitingForBakiyeSorgulama
    global BalanceQuery_GameLockStatus
    global LastCommand_Bakiye_Sender
    global Yanit_BakiyeTutar
    global Yanit_RestrictedAmount
    global Yanit_NonRestrictedAmount
    global IsWarnedForTakeWin
    global Bakiye_WaitingForGameLockCount
    Bakiye_WaitingForGameLockCount=0

    IsWaitingForBakiyeSorgulama=1
    BalanceQuery_GameLockStatus=""
    LastCommand_Bakiye_Sender=sender


    WaitBakiye_Date=datetime.datetime.now()

    Yanit_BakiyeTutar=0
    Yanit_RestrictedAmount=0
    Yanit_NonRestrictedAmount=0

    Config.set("collecting","cashableamount", "0")
    Config.set("collecting","restrictedamount", "0")
    Config.set("collecting","nonrestrictedamount", "0")
    SaveConfigFile()

    try:
        Komut_BakiyeSorgulama(sender, isforbilgi,sendertext)
        LastCommandDate_Bakiye=datetime.datetime.now()
        #time.sleep(0.05)
        while (1==1):

            time.sleep(0.003)
            LastCommandDate_Bakiye_Diff=(datetime.datetime.now()-LastCommandDate_Bakiye).total_seconds()
            FirstCommandDate_Bakiye_Diff=(datetime.datetime.now()-WaitBakiye_Date).total_seconds()

            #print("LastCommandDate_Bakiye_Diff", LastCommandDate_Bakiye_Diff, "FirstCommandDate_Bakiye_Diff", FirstCommandDate_Bakiye_Diff)
            if IsWaitingForBakiyeSorgulama==0:
                print("************Do not wait for bakiye anymore. 0 *********")
                break

            if IsWaitingForBakiyeSorgulama==1 and LastCommandDate_Bakiye_Diff>=0.5:
                print("************ SEND COMMAND AGAIN ********************")
                LastCommandDate_Bakiye=datetime.datetime.now()
                Komut_BakiyeSorgulama(sender, isforbilgi,sendertext)

        
            if IsDebugAutoBakiyeYanit==1:
                HandUserInput("yanitbakiye")
                time.sleep(0.01)


            if sendertext=="BillAcceptor" or sendertext=="AddMoney" or sendertext=="asset":
                #print("FirstCommandDate_Bakiye_Diff", FirstCommandDate_Bakiye_Diff)
                if FirstCommandDate_Bakiye_Diff>2:
                    return 0

            if FirstCommandDate_Bakiye_Diff>60:
                SetMachineStatu("FAIL-No Answer balance query")
                print("**********BAKIYE SORGULAMA IS FAILED***********************")
                return 0;

    except Exception as ex9:
        ExceptionHandler("Error on Wait_Bakiye",ex9,0)
    
    print("</Wait_Bakiye entered:>---------------------------------------- FirstCommandDate_Bakiye_Diff", FirstCommandDate_Bakiye_Diff)
    print("***************************************************************")

    SetMachineStatu("OK-Answer to balance query")
    return 1;


def ChangeRealTimeReporting(isopened):


    #2021-10-06 kapatildi
    #if isopened==0:
    #    return

    if isopened==1:
        print("Real time reporting is on")
        GenelKomut=GetCRC("010E01")
        SAS_SendCommand("RTP-1",GenelKomut,0)
    else:
        print("Real time reporting is off")
        GenelKomut=GetCRC("010E00")
        SAS_SendCommand("RTP-0",GenelKomut,0)

#<GUI HELPER>-----------------------------------------------------------------

G_Last_NextionCommand=datetime.datetime.now()
NextionCommandStr = []
NextionCommandCount=0
def NextionCommand(data):
    global NextionCommandCount
    NextionCommandCount=NextionCommandCount+1

    global GUI_Static_WelcomeText
    GUI_Static_WelcomeText="Insert card"
    if NextionCommandCount>10000:
        NextionCommandCount=0

    #NextionCommandThread(data)

    thread1 = Thread(target = NextionCommandThread, args = (data, ))
    thread1.name="Nextion" + str(NextionCommandCount)
    thread1.start()

def NextionCommandThread(data):
    global nextionport
    global NextionCommandStr
    global G_Last_NextionCommand
    global Nextion_Busy
    global GUI_Static_WelcomeText
    GUI_Static_WelcomeText="Insert card"

    Nextion_Busy=1


    #G_Last_NextionCommand_Diff=(datetime.datetime.now()-G_Last_NextionCommand).total_seconds()
    #while G_Last_NextionCommand_Diff<0.3 and data[0]!="123456":
    #    #print("Wait nextion***************")
    #    time.sleep(0.13)
    #    G_Last_NextionCommand_Diff=(datetime.datetime.now()-G_Last_NextionCommand).total_seconds()

    try:

        

        CountryTry=0
        while len(NextionCommandStr)>0:

            CountryTry=CountryTry+1
        
            if CountryTry%10==0:
                print("Please wait.. Another command is being sent to nextion")
        
            time.sleep(0.05)

            if CountryTry>5000:
                print("break bill acceptor while commandstr")
                break
        if CountryTry>0:
            time.sleep(0.6)

        NextionCommandStr=data


        k=struct.pack('B', 0xff)



        for cmd in data:

            print("Nextion TX", cmd, nextionport.port)

     

            G_Last_NextionCommand=datetime.datetime.now()


            A_END_OF_CMD = [0xff, 0xff, 0xff]
            S_END_OF_CMD = bytearray(A_END_OF_CMD)
            CmdAll=bytearray(cmd, encoding="ISO-8859-1") + S_END_OF_CMD
            nextionport.write(CmdAll)
            time.sleep(0.1)
            

        NextionCommandStr = []
        Nextion_Busy=0
    except Exception as esql:
        Nextion_Busy=0
        print("Nextion command sent error")
        ExceptionHandler("Nextion Err",esql,0)

Nextion_Count_Cmd=0
def SendNextionCommandIfExist():
    return

    global Nextion_Count_Cmd
    Nextion_Count_Cmd=Nextion_Count_Cmd+1
    
    LocalVar=Nextion_Count_Cmd
    print("<Start Nextion>---------------------------------------------", LocalVar)
    global NextionCommandStr
    try:

        for cmd in NextionCommandStr:

            print("Nextion TX", cmd, nextionport.port)

            if nextionport.isOpen()==False:
                print("Error! not opened!" , NextionCommandStr)
                return

            #nextionport.flushInput

            #nextionport.flushInput()

            #cmd="page 1"
            EndCom = "\xff\xff\xff"
            RealCommand=(cmd.encode())
            RealCommand=bytearray(RealCommand)
            RealCommand.append(255)
            RealCommand.append(255)
            RealCommand.append(255)
            nextionport.write(RealCommand)
            time.sleep(0.2)
            

    
    except Exception as esql:
        print("Nextion command sent error")
        ExceptionHandler("Nextion Err",esql,0)

    NextionCommandStr = []
    print("</Start Nextion>---------------------------------------------", LocalVar)



def CloseCustomerInfo():
    try:

        if IsGUIEnabled==0:
            return
        debugpoint=0

        if IsGUI_Type==1:
            try:
                ui.emit(QtCore.SIGNAL('CloseCustomerWindow()'))
            except Exception as e:
                print("Close Customer Info failed")
                debugpoint=1


        if IsGUI_Type==2:
            GUI_ShowIdleWindow()

        if IsGUI_Type==3 or IsGUI_Type==4:
            GUI_ShowIdleWindow()

    except Exception as esql:
        print("Err on CloseCustomerInfo")






def ScreenUpdateTextStatu(message, resetsecond):
    if IsGUIEnabled==0:
        return

    if IsGUI_Type==1:
        try:
            ui.emit(QtCore.SIGNAL('ScreenUpdateTextStatu(QString)'),message)
        except Exception as e:
            ExceptionHandler("ScreenUpdateTextStatu Error",e,0)

    if IsGUI_Type==2:
        NextionCommand(["tMainStatu.txt=\""+message+"\""])


    if IsGUI_Type==3 or IsGUI_Type==4:
        ExecuteJSFunction2("ChangeText", "divMainStatu",message)
        ExecuteJSFunction2("ChangeText", "divCustomerStatu",message)
        ExecuteJSFunction2("ChangeText", "divAdminStatu",message)
        


    if resetsecond>0:
        threadTextStatu = Thread(target = ScreenResetTextStatu)
        threadTextStatu.name="txtStatu"
        threadTextStatu.start()


def ScreenResetTextStatu():
    if IsGUIEnabled==0:
        return

    if IsGUI_Type==1:
        try:
            time.sleep(3) 
            ui.emit(QtCore.SIGNAL('ScreenUpdateTextStatu(QString)'),GUI_Static_WelcomeText)
        except Exception as e:
            print("ScreenResetTextStatu Error")

    if IsGUI_Type==2:
        NextionCommand(["tMainStatu.txt=\""+GUI_Static_WelcomeText+"\""])

    #if IsGUI_Type==3 or IsGUI_Type==4:
    #    ExecuteJSFunction2("ChangeText", "divMainStatu",GUI_Static_WelcomeText)
    #    ExecuteJSFunction2("ChangeText", "divCustomerStatu",GUI_Static_WelcomeText)
    #    ExecuteJSFunction2("ChangeText", "divAdminStatu",GUI_Static_WelcomeText)


def ChangeJackpotLevelText(sira, yazi):
    if IsGUI_Type==1:
        ui.emit(QtCore.SIGNAL('ChangeJackpotLevelText(int, QString)'),sira,yazi)

    if IsGUI_Type==2:
        print("gui ok")

    if IsGUI_Type==3 or IsGUI_Type==4:
        print("gui ok")



def ChangeJackpotLevelTextValue(sira,yazi):
    if IsGUIEnabled==0:
        return

    if IsGUI_Type==2:
        if sira==1:
            NextionCommand(["tj0.txt=\""+yazi+"\""])
        if sira==2:
            NextionCommand(["tj1.txt=\""+yazi+"\""])
        if sira==3:
            NextionCommand(["tj2.txt=\""+yazi+"\""])
        if sira==4:
            NextionCommand(["tj3.txt=\""+yazi+"\""])

def ChangeJackpotLevelValue(sira, yazi):
    if IsGUI_Type==1:
        ui.emit(QtCore.SIGNAL('ChangeJackpotLevelValue(int, QString)'),sira,yazi)
    
    if IsGUI_Type==2:
        print("guifix ok")

    if IsGUI_Type==3 or IsGUI_Type==4:
        ExecuteJSFunction2("ChangeText", "divJackpotLine" + str(sira),yazi)


def ShowNotifyScreen(header, msg, duration):
    if IsGUIEnabled==0:
        return

    if IsGUI_Type==1:
        try:
            ui.emit(QtCore.SIGNAL('ShowNotifyScreen(QString,QString,int)'),header, msg, duration)
        except Exception as e:
            print("ShowNotifyScreen Error")

    if IsGUI_Type==2:
        NextionCommand(["page page_timer","tHeader.txt=\""+header+"\"","tText.txt=\""+msg+"\""])

    if IsGUI_Type==3 or IsGUI_Type==4:
        ExecuteJSFunction5("ShowNotify", "0", "0", header, msg, str(duration))

    try:
        if duration>0:
            processThread = Thread(target=CloseNotifyScreen, args=(duration,))
            processThread.Text="CloseNotifyScreen"
            processThread.start()
    except Exception as e:
        print("OTO KAPAT SORUN VAR")


def ShowNotifyScreenWithButtons(header, msg, duration, showOk, showCancel):
    if IsGUIEnabled==0:
        return

    if IsGUI_Type==1:
        try:
            ui.emit(QtCore.SIGNAL('ShowNotifyScreen(QString,QString,int)'),header, msg, duration)
        except Exception as e:
            print("ShowNotifyScreen Error")

    if IsGUI_Type==2:
        NextionCommand(["page page_timer","tHeader.txt=\""+header+"\"","tText.txt=\""+msg+"\""])

    if IsGUI_Type==3 or IsGUI_Type==4:
        ExecuteJSFunction5("ShowNotify", str(showOk), str(showCancel), header, msg, str(duration))

    try:
        if duration>0:
            processThread = Thread(target=CloseNotifyScreen, args=(duration,))
            processThread.name="ShowNotify1"
            processThread.start()
    except Exception as e:
        print("OTO KAPAT SORUN VAR")
    

def CloseNotifyScreen(seconds):

    time.sleep(seconds)


    if IsGUI_Type==1:
        ui.emit(QtCore.SIGNAL('CloseNotifyScreenCmd(int)'), seconds)

    if IsGUI_Type==2:
        GUI_ShowCurrentPage()

    if IsGUI_Type==3 or IsGUI_Type==4:
        GUI_ShowCurrentPage()


def ChangeCustomerScreenLine(lineNo, yazi):
    if IsGUIEnabled==0:
        return

    if IsGUI_Type==1:
        try:
            ui.emit(QtCore.SIGNAL('ChangeLineText(int, QString)'),lineNo,yazi)
        except Exception as e:
            print("Error : ChangeCustomerScreenLine")
    
    if IsGUI_Type==2:
        if lineNo==1:
            NextionCommand(["lblLine1.txt=\""+yazi+"\""])

        if lineNo==2:
            NextionCommand(["lblLine2.txt=\""+yazi+"\""])

        if lineNo==3:
            NextionCommand(["lblLine3.txt=\""+yazi+"\""])


    if IsGUI_Type==3 or IsGUI_Type==4:
        if lineNo==1:
            ExecuteJSFunction2("ChangeText", "divCustomerLine1",yazi)

        if lineNo==2:
            ExecuteJSFunction2("ChangeText", "divCustomerLine2",yazi)

        if lineNo==3:
            ExecuteJSFunction2("ChangeText", "divCustomerLine3",yazi)


def ChangeCustomerLineWithDelay(resetsecond,lineNo,yazi):
    if IsGUIEnabled==0:
        return
    time.sleep(resetsecond)

    ChangeCustomerScreenLine(lineNo,yazi)


def ChangeCustomerScreenLineTimed(lineNo, yazi, resetsecond, yazison):
    if IsGUIEnabled==0:
        return
    ChangeCustomerScreenLine(lineNo,yazi,)
    if resetsecond>0:
        try:
            processThread = Thread(target=ChangeCustomerLineWithDelay, args=(resetsecond,lineNo,yazison,));
            processThread.name="ChangeCustLine"
            processThread.start();
        except Exception as e:
            ExceptionHandler("ResetSecondProblem",e,0)


#sender: 1: Please wait until game ends, 2: Normal
def BlinkCustomerScreenLine(sender, lineno, text, howmanytimes):
    if IsGUIEnabled==0:
        return
    try:
        processThread = Thread(target=BlinkCustomerScreenLine_Thread, args=(sender, lineno, text, howmanytimes));
        processThread.name="BlinkCustLine"
        processThread.start();
    except Exception as e:
        ExceptionHandler("BlinkCustomerScreenLine",e,0)



def BlinkCustomerScreenLine_Thread(sender, lineno, text, howmanytimes):
    if IsGUIEnabled==0:
        return
    
    ChangeCustomerScreenLine(lineno,text)

    #2020-07-15 Kapattik
    #while (sender==1 and IsCardInside==1)==True or (sender!=1 and howmanytimes>0)==True:
    #    ChangeCustomerScreenLine(lineno,text)
    #    time.sleep(0.5)
    #    ChangeCustomerScreenLine(lineno,"")
    #    time.sleep(0.3)
    #    howmanytimes=howmanytimes-1

NoNetwork_Count=0
ErrorMessage_NoNetwork="NO NETWORK"
GUI_LastMainStatuMessage=""
def GUI_ShowIfPossibleMainStatu(msg):
    global GUI_LastMainStatuMessage

    if GUI_LastMainStatuMessage==msg:
        return

    GUI_LastMainStatuMessage=msg

    if IsGUIEnabled==0:
        return

    try:
        if IsGUI_Type==1:
            try:
                ui.emit(QtCore.SIGNAL('ScreenUpdateTextStatuMain(QString)'),msg)
            except Exception as e:
                print("msg", msg)
                ExceptionHandler("ScreenUpdateTextStatuMain Error",e,0)

        if IsGUI_Type==2:
            NextionCommand(["tMainStatu.txt=\""+msg+"\""])

        if IsGUI_Type==3 or IsGUI_Type==4:
            ExecuteJSFunction2("ChangeText", "AllStatus",msg)
            #ExecuteJSFunction2("ChangeText", "divMainStatu",msg)
            #ExecuteJSFunction2("ChangeText", "divCustomerStatu",msg)
            #ExecuteJSFunction2("ChangeText", "divAdminStatu",msg)
    except Exception as e2:
        print("ShowIfPossible........")




def GUI_ShowCurrentPage():
    isFoundPage=0
    if GUI_CurrentPage=="GUI_ShowIdleWindow":
        isFoundPage=1
        GUI_ShowIdleWindow()

    if GUI_CurrentPage=="GUI_ShowBonus":
        isFoundPage=1
        GUI_ShowBonus()

    if GUI_CurrentPage=="GUI_ShowJackpot":
        isFoundPage=1
        GUI_ShowJackpot()

    if GUI_CurrentPage=="GUI_ShowBalance":
        isFoundPage=1
        GUI_ShowBalance()

    if GUI_CurrentPage=="GUI_ShowSettings":
        isFoundPage=1
        GUI_ShowSettings()

    if GUI_CurrentPage=="GUI_ShowAdmin":
        isFoundPage=1
        GUI_ShowAdmin()

    if GUI_CurrentPage=="GUI_ShowCustomerWindow":
        isFoundPage=1
        if IsCardInside==1:
            GUI_ShowCustomerWindow()
        else:
            GUI_ShowIdleWindow()


    if isFoundPage==0:
        print("Page is not found", GUI_CurrentPage)
        if IsCardInside==1:
            GUI_ShowCustomerWindow()
        else:
            GUI_ShowIdleWindow()


    

def GUI_ShowIdleWindow():
    print("GUI_ShowIdleWindow")
    global GUI_CurrentPage
    GUI_CurrentPage="GUI_ShowIdleWindow"

    if IsGUIEnabled==0:
        return
    
    if IsGUI_Type==1:
        CloseCustomerWindow()

    if IsGUI_Type==2:
        #NextionCommand(["page page_idle","vis btnAdmin,0", "lblMachineName.txt=\""+G_Machine_MachineName+" \"","lblStatuText.txt=\""+GUI_Static_WelcomeText+"\""])
        NextionCommand(["page page_idle", "lblMachineName.txt=\""+G_Machine_MachineName+" \"","lblStatuText.txt=\""+GUI_Static_WelcomeText+"\""])


    if IsGUI_Type==3 or IsGUI_Type==4:
        ExecuteJSFunction("ShowIdleScreen", "a")
        ExecuteJSFunction2("ChangeText", "divMachineName",G_Machine_MachineName)
        ExecuteJSFunction2("ChangeText", "divMainMachineName",G_Machine_MachineName)
        ExecuteJSFunction2("ChangeText", "StatuText",GUI_Static_WelcomeText)
        ExecuteJSFunction("CloseVideo","")
        ExecuteJSFunction2("ChangeText", "divCustomerLine2","NO NAME")


def GUI_RefreshPage():
    ExecuteJSFunction("RefreshPage","Refresh")

    time.sleep(4)
    if IsCardInside==1:
        GUI_ShowCustomerWindow()
    else:
        GUI_ShowIdleWindow()








def GUI_ShowBonus():
    try:
        global GUI_CurrentPage
        GUI_CurrentPage="GUI_ShowBonus"
        if IsGUIEnabled==0:
            return

        if IsGUI_Type==2:
            NextionCommand(["page page_bonus"])

        if IsGUI_Type==3 or IsGUI_Type==4:
            ExecuteJSFunction("CustomerNavIconClicked", "divBonus")

        GUI_UpdateBonus()
    except Exception as e2:
        print("GUIShowBonus........")


def GUI_ShowJackpot():
    try:
        global GUI_CurrentPage
        GUI_CurrentPage="GUI_ShowJackpot"

        if IsGUIEnabled==0:
            return

        if IsGUI_Type==2:
            NextionCommand(["page page_jackpot"])

        if IsGUI_Type==3 or IsGUI_Type==4:
            ExecuteJSFunction("CustomerNavIconClicked", "divJackpot")

    except Exception as e2:
        print("ShowJackpot........")

def GUI_ShowBalance():
    try:
        global GUI_CurrentPage
        GUI_CurrentPage="GUI_ShowBalance"
        if IsGUIEnabled==0:
            return

        if IsCardReaderBusy==1:
            GUI_ShowIfPossibleMainStatu("Cashout is in progress")
            return

        #<Here check bank balance>#############################################
        BankBalanceText=""
        BankBalance=Decimal(0)
        if 1==1:
            try:
                # Original MSSQL procedure: tsp_GetBalanceInfoOnGM
                # Note: This procedure was not found in postgres-routines-in-sas.sql
                # Using hybrid approach - queue operation instead of direct call
                result = db_helper.queue_database_operation(
                    'tsp_GetBalanceInfoOnGM',
                    [G_Machine_Mac, G_User_CardNo],
                    'get_balance_info_on_gm'
                )

                for row in result:
                    BankBalance = Decimal(row["BankBalance"])
                    BankBalanceText = "%s %s" % (BankBalance, G_Machine_Currency)
            except Exception as ecardtype:
                ExceptionHandler("tsp_GetBalanceInfoOnGM", ecardtype, 0)
        #<Here check bank balance>#############################################

        if IsGUI_Type==2:
            NextionCommand(["page page_balance","tBank.txt=\""+BankBalanceText+"\""])
            Wait_Safe_Bakiye(13,1,"wait_safebakiye")

        if IsGUI_Type==3 or IsGUI_Type==4:
            ExecuteJSFunction2("ChangeText", "txtBank",BankBalanceText)
            Wait_Safe_Bakiye(13,1,"wait_safebakiye")



    except Exception as e2:
        print("ShowBalance........")


GUI_CountTimer=1
def GUI_ShowAdverts():


    global GUI_CountTimer

    try:
        if IsCardInside==1 or IsCardReaderBusy==1 or IsWaitingAdminScreen==1:
            return



        if IsGUI_Type==9999:
            sira=0
            if GUI_CountTimer==0:
                GUI_ShowIdleWindow()

            if GUI_CountTimer==5:
                sira=1

            if GUI_CountTimer==10:
                sira=2

            if GUI_CountTimer==15:
                sira=3

            if GUI_CountTimer>20:
                GUI_CountTimer=-1

            if sira>0:
                try:
                    ui.emit(QtCore.SIGNAL('ChangeAdvert(int)'),sira)
                except Exception as e:
                    print("Error : ChangeAdvert")



        if IsGUI_Type==2:
            if GUI_CountTimer==0:
                GUI_ShowIdleWindow()

            if GUI_CountTimer==20:
                NextionCommand(["page page_advert1"])
                #print("Reklam")

            if GUI_CountTimer==25:
                NextionCommand(["page page_advert2"])

            if GUI_CountTimer==30:
                NextionCommand(["page page_advert3"])

            if GUI_CountTimer>35:
                GUI_CountTimer=-1


        if (IsGUI_Type==3 or IsGUI_Type==4) and 2==1:
            if GUI_CountTimer==0:
                GUI_ShowIdleWindow()
                print("IDLE SHOW")

            if GUI_CountTimer==20:
                print("VIDEO SHOW")
                ExecuteJSFunction("ShowVideo","")

            if GUI_CountTimer>40:
                GUI_CountTimer=-1


        GUI_CountTimer=GUI_CountTimer+1

    except Exception as e2:
        print("ShowAdverts........")



def GUI_ShowSettings():
    try:
        global GUI_CurrentPage
        GUI_CurrentPage="GUI_ShowSettings"
        if IsGUIEnabled==0:
            return

        if IsGUI_Type==2:
            NextionCommand(["page page_settings"])


        if IsGUI_Type==3 or IsGUI_Type==4:
            ExecuteJSFunction("CustomerNavIconClicked", "divSettings")

    except Exception as e2:
        print("........")

def GUI_ShowAdmin():
    try:
        global GUI_CurrentPage
        GUI_CurrentPage="GUI_ShowAdmin"
        if IsGUIEnabled==0:
            return

        if IsGUI_Type==1:
            print("guix")

        if IsGUI_Type==2:
            NextionCommand(["page page_admin","tIP.txt=\""+get_lan_ip()+"\""])

        if IsGUI_Type==3 or IsGUI_Type==4:
            ExecuteJSFunction("CustomerNavIconClicked", "divAdmin")

    except Exception as e2:
        print("........")




def GUI_ShowCustomerWindow():
    try:
        global GUI_CurrentPage
        GUI_CurrentPage="GUI_ShowCustomerWindow"
        if IsGUIEnabled==0:
            print("GUI is not enabled")
            return


        CustomerNickname=Config.get("customer","customerid") + " - " + Config.get("customer","nickname")

        if IsGUI_Type==1:
            ui.emit(QtCore.SIGNAL('ShowCustomerWindow()'))
            ChangeCustomerScreenLine(1,"WELCOME")
            ChangeCustomerScreenLine(2,CustomerNickname)

        if IsGUI_Type==2:
            NextionCommand(["page page_customer","lblLine1.txt=\"WELCOME\"","lblLine2.txt=\""+CustomerNickname+"\""])
            

        if IsGUI_Type==3 or IsGUI_Type==4:
            customerid=Config.getint("customer","customerid")
            if customerid>0:
                ExecuteJSFunction("ShowCustomerPage", "GUI_ShowCustomerWindow")
                ExecuteJSFunction2("ChangeText", "divCustomerLine1","WELCOME")
                ExecuteJSFunction2("ChangeText", "divCustomerLine2",CustomerNickname)
                if CustomerNickname.startswith("0 -")==True:
                    print("Noluyor lan?")
            else:
                GUI_ShowIdleWindow()




        

    except Exception as e2:
        print("........")
    


    

def CloseCustomerWindow():
    if IsGUI_Type==1:
        ui.emit(QtCore.SIGNAL('CloseCustomerWindow()'))

    if IsGUI_Type==2:
        GUI_ShowIdleWindow()


def GUI_CloseCustomerBalance():
    if IsGUIEnabled==0:
        return

    if IsGUI_Type==1:
        try:
            ui.emit(QtCore.SIGNAL('CloseCustomerBalance()'))
        except Exception as e:
            print("Error on GUI_CloseCustomerBalance")
    
    if IsGUI_Type==2:
        if GUI_CurrentPage=="GUI_ShowBalance":
            GUI_ShowCustomerWindow()

    if IsGUI_Type==3 or IsGUI_Type==4:
        if GUI_CurrentPage=="GUI_ShowBalance":
            GUI_ShowCustomerWindow()




GUI_UpdateBonus_Count=0
Bonus_GameStart_Wagered=Decimal(0)
def GUI_UpdateBonus():
    if IsGUIEnabled==0:
        return
    global GameStart_Wagered
    global GUI_UpdateBonus_Count
    global Bonus_GameStart_Wagered




    GUI_UpdateBonus_Count=GUI_UpdateBonus_Count+1


    DoContinue=1

    if Bonus_GameStart_Wagered!=GameStart_Wagered:
        DoContinue=1

    if GUI_UpdateBonus_Count%3==1:
        DoContinue=1

    if DoContinue==0:
        return

    Bonus_GameStart_Wagered=GameStart_Wagered

    currentbonus=Decimal(Config.get("customer","currentbonus"));
    currentbonus=round(currentbonus, 4)
    yazi="%s %s" % (currentbonus, G_Machine_Currency)

    if IsGUI_Type==1:
        try:
            ui.emit(QtCore.SIGNAL('GUI_UpdateBonus(QString)'),yazi)
        except Exception as e:
            print("Error on GUI_Updatebonus")

    if IsGUI_Type==2:
        print("guifix bonus")

    if IsGUI_Type==3 or IsGUI_Type==4:
        AvailableBonus=currentbonus
        AvailableBonus=round(AvailableBonus, 4)
        AvailableBonusInt=math.floor(AvailableBonus)
        BonusDecimalPart=AvailableBonus-AvailableBonusInt
        
        AvailableBonusText="%s %s" % (AvailableBonus, G_Machine_Currency)
        #2020-07-07ExecuteJSFunction5("ChangeBonusValue", str(AvailableBonus),str(AvailableBonusInt),str(BonusDecimalPart),G_Machine_Currency,AvailableBonusText)

        startpercentage=0
        nextpercentage=0
        minwager=Decimal(0)
        maxwager=Decimal(0)


        for member in G_Machine_WagerBonusFactors:
            if GameStart_Wagered>=Decimal(member['wager']):
                startpercentage=Decimal(member['startpercentage'])
                nextpercentage=Decimal(member['nextpercentage'])
                minwager=Decimal(member['wager'])
                maxwager=Decimal(member['wagernext'])
        #ExecuteJSFunction7("FillBonusStars", str(len(G_Machine_WagerBonusFactors)), str(G_Machine_WagerIndex), str(GameStart_Wagered), str(startpercentage), str(nextpercentage), str(minwager), str(maxwager))
        ExecuteJSFunction12("FillBonusStarsAndBonusValue", str(len(G_Machine_WagerBonusFactors)), str(G_Machine_WagerIndex), str(GameStart_Wagered), str(startpercentage), str(nextpercentage), str(minwager), str(maxwager), str(AvailableBonus), str(AvailableBonusInt),str(BonusDecimalPart), G_Machine_Currency, AvailableBonusText)


def ChangeBalanceAmount(lineNo, yazi):
    if IsGUIEnabled==0:
        return


    if IsGUI_Type==1:
        try:
            ui.emit(QtCore.SIGNAL('ChangeBalanceAmount(int, QString)'),lineNo,yazi)
        except Exception as e:
            print("Error : ChangeBalanceAmount")
    
    if IsGUI_Type==2:
        if GUI_CurrentPage!="GUI_ShowBalance":
            return

        if lineNo==1:
            NextionCommand(["tCashable.txt=\""+yazi+"\""])

        if lineNo==2:
            NextionCommand(["tPromo.txt=\""+yazi+"\""])

    if (IsGUI_Type==3 or IsGUI_Type==4) and GUI_CurrentPage=="GUI_ShowBalance":
        if lineNo==1:
            ExecuteJSFunction2("ChangeText", "txtCashable",yazi)

        if lineNo==2:
            ExecuteJSFunction2("ChangeText", "txtPromo",yazi)
#<GUI HELPER>-----------------------------------------------------------------


G_User_CardType=0
G_Session_CardExitStatus=0
G_SAS_IsProblemOnCredit=0
G_SAS_Transfer_Warning_DoorIsLocked=0


def SQL_ReadCustomerInfo_Test(KartNo,CardRawData):
    """
    Test function that returns mock data for customer card reading
    Returns only the fields that are actually used in the main SQL_ReadCustomerInfo function
    """
    print("                                                                ")
    print("                                                                ")
    print("****************************************************************")
    print("<SQL_ReadCustomerInfo_Test>-------------------------------------")
    
    try:
        global G_User_CardType
        global G_LastGame_Action
        global G_SessionStarted
        global G_CardMachineLogId
        global G_User_CardNo
        global IsCardInside
        global G_Machine_Balance
        global G_Machine_Promo
        global G_LastCardExit
        global G_User_PrevCardNo
        global G_LastCardEnter
        global IsWaitAtLeastCardExistDbSaved
        global BillAcceptor_Amount
        global Global_ParaYuklemeFail_SQL
        global G_SAS_Transfer_Warning_DoorIsLocked
        global Nextion_CurrentStep
        global IsWaitingAdminScreen
        global G_SAS_IsProblemOnCredit
        global Cashout_Source
        global G_SAS_LastAFTOperation
        global G_Machine_ReservationDate
        global G_LastGameEnded
        global G_Session_CardExitStatus
        global G_MessageCount
        global Global_ParaSifirla_84
        
        # Initialize variables (same as original function)
        G_MessageCount=0
        Cashout_Source=0
        G_SAS_LastAFTOperation=""
        Global_ParaSifirla_84=0
        G_SAS_Transfer_Warning_DoorIsLocked=0
        
        # Learn Asset No
        if G_Device_AssetNo==0:
            Komut_ReadAssetNo()
        
        BillAcceptor_Amount=Decimal(0)
        
        # Check if card was just removed (same validation as original)
        LastCardExitDiff=(datetime.datetime.now()-G_LastCardExit).total_seconds()
        if LastCardExitDiff<=1:
            GUI_ShowIfPossibleMainStatu("Wait 2 seconds for new card")
            print("Wait 2 seconds for new card",LastCardExitDiff)
            return "Wait 2 seconds for new card"
        
        SQL_Safe_InsImportantMessage("Card is inserted (TEST MODE) " + KartNo,76)
        
        # Check if system already has a card
        if len(G_User_CardNo)>0:
            print("Sistemde zaten kart var. E:%s Y:%s"%(G_User_CardNo, KartNo))
            SQL_InsImportantMessage("GM already has card (TEST). E:%s Y:%s" % (G_User_CardNo, KartNo),3)
            return "Sistemde zaten kart var."
        
        if IsSystemLocked==1:
            PrintAndSetAsStatuText("System cant accept card-in")
            return "System cant accept card-in"
        
        # Mock successful database result with only used fields
        class MockRow:
            def __init__(self):
                # Create test data that matches what the real SQL procedure returns
                self.data = {
                    # Core result fields (ALWAYS USED)
                    'Result': True,
                    'ErrorMessage': 'Test mode - Good luck!',
                    
                    # Customer identification (USED)
                    'CustomerId': 12345,
                    'CardMachineLogId': 98765,
                    'Fullname': 'Test Customer',
                    'Nickname': 'TestUser',
                    'Gender': 1,  # 1=Male, 2=Female
                    
                    # Financial fields (USED)
                    'Balance': Decimal('100.50'),
                    'PromoBalance': Decimal('25.00'),
                    'BonusPercentage': Decimal('1.5'),
                    'CurrentBonus': Decimal('15.75'),
                    
                    # Card information (USED)
                    'CardType': 0,  # 0=Normal customer card
                    
                    # System control (USED)
                    'UploadMoney': 1,  # 1=Upload money to machine, 0=Don't upload
                    'IsLocked': 0,     # Device lock status (0=unlocked, 1=locked)
                }
            
            def __getitem__(self, key):
                return self.data.get(key)
            
            def get(self, key, default=None):
                return self.data.get(key, default)
        
        # Create mock result
        mock_result = [MockRow()]
        
        # Process the mock result (same logic as original function)
        IsExist = 0
        CardReaderSQLResult = "Normal"
        
        for row in mock_result:
            G_LastGame_Action=datetime.datetime.now()
            IsExist=1
            
            if row['Result']==True:
                # Process successful card read (same as original)
                G_SessionStarted=datetime.datetime.now()
                G_Session_CardExitStatus=0
                Global_ParaYuklemeFail_SQL=0
                IsWaitAtLeastCardExistDbSaved=0
                
                print("************************** TEST CARD INSIDE **************************")
                print("Result: %s, Message: %s, Kart No: %s Adi:%s, Bakiye:%s" % (
                    row['Result'], row['ErrorMessage'], KartNo, row['Fullname'], row['Balance']))
                
                UploadMoney=int(row["UploadMoney"])
                print("UploadMoney",UploadMoney)
                
                Balance=Decimal(row['Balance'])
                Promo=Decimal(row['PromoBalance'])
                
                G_CardMachineLogId=int(row["CardMachineLogId"])
                
                # Set global variables
                G_User_CardNo=KartNo
                G_User_PrevCardNo=KartNo
                IsCardInside=1
                G_User_CardType=int(row["CardType"])
                
                # Save to config (same as original)
                try:
                    Config.set('customer','cardnumber', G_User_CardNo)
                    Config.set('customer','customerid', str(int(row["CustomerId"])))
                    Config.set('customer','cardmachinelogid', str(int(row["CardMachineLogId"])))
                    Config.set('customer','gender', str(int(row["Gender"])))
                    Config.set('customer','customername', row['Fullname'])
                    Config.set('customer','nickname', row['Nickname'])
                    Config.set('customer','iscardinside', "1")
                    SaveConfigFile()
                    
                    Config.set('customer','bonuspercentage', str(Decimal(row['BonusPercentage'])))
                    Config.set('customer','currentbonus', str(Decimal(row['CurrentBonus'])))
                    Config.set('customer','earnedbonus', str(Decimal(0)))
                    
                    Config.set('customer','inserteddate', str(datetime.datetime.now()))
                    Config.set('customer','playcount', "0")
                    Config.set('customer','totalbet', "0")
                    Config.set('customer','totalwin', "0")
                    Config.set('customer','ismoneytransfered', "0")
                    
                    G_Machine_Balance=Balance
                    G_Machine_Promo=Promo
                    
                    Config.set('customer','customerbalance', str(G_Machine_Balance))
                    Config.set("customer","currentbalance",str(G_Machine_Balance))
                    Config.set("customer","customerpromo",str(G_Machine_Promo))
                    Config.set("customer","currentpromo",str(G_Machine_Promo))
                    
                except Exception as esql:
                    print("Config Set Err Init (TEST)!")
                
                SaveConfigFile()
                
                # Simulate money upload for cashless systems
                ParaYukleSonuc=1
                if G_Machine_IsCashless==1 and UploadMoney==1:
                    print("TEST MODE: Simulating money upload...")
                    ParaYukleSonuc=1  # Always successful in test mode
                    SQL_Safe_InsImportantMessage("Test Cashin Result:" + str(ParaYukleSonuc) ,78)
                
                try:
                    SQL_Safe_InsImportantMessage("Test session started: " + row['Fullname'] + " C:" + str(G_Machine_Balance) + " P:" +  str(G_Machine_Promo),79)
                except Exception as esql:
                    print("SQL_Safe 1 (TEST)")
                
                # Set timing variables
                G_LastCardEnter=datetime.datetime.now()
                G_LastGame_Action=datetime.datetime.now()
                G_LastGameEnded=datetime.datetime.now()
                G_SAS_IsProblemOnCredit=0
                
                print("TEST ParaYukleSonuc:" , ParaYukleSonuc)
                
                if ParaYukleSonuc==1:
                    ChangeRealTimeReporting(1)
                    Komut_EnableBillAcceptor()
                
                # Show customer window
                GUI_ShowCustomerWindow()
                
                if G_Machine_IsBonusGives==1 and IsGUI_Type!=2:
                    GUI_ShowBonus()
                
                # Screen updates
                ChangeCustomerScreenLineTimed(3,"Ready! (TEST)",2,"GOOD LUCK")
                G_LastCardExit=datetime.datetime.now()
                
                PrintAndSetAsStatuText("Ready for game! (TEST MODE)")
                Ac("Ready for game (TEST)")
                
                # Auto visit checks (same as original)
                print("G_Machine_IsAutoNextVisit", G_Machine_IsAutoNextVisit)
                if G_Machine_IsAutoNextVisit==1 and G_Machine_IsRulet==0:
                    CheckNextVisit()
                
                if G_Machine_IsAutoNextVisit==2 and G_Machine_IsRulet==0:
                    CheckNextVisit_ByTurnover()
                
                G_SessionStarted=datetime.datetime.now()
                
                # Device specific commands
                if G_Machine_DeviceTypeId==9:
                    Komut_CancelBalanceLock()
                else:
                    Komut_BakiyeSorgulama(1,1,"cardinstalled-test")
                
                G_LastCardExit=datetime.datetime.now()
                
            else:
                # Handle error case
                CardReaderSQLResult=row['ErrorMessage']
                try:
                    SQL_InsImportantMessageByWarningType(CardReaderSQLResult + " (TEST)", 1, 0)
                except Exception as eC1:
                    print("Message: " , eC1)
                print("Error - 1 (TEST)", row['ErrorMessage'])
                GUI_ShowIfPossibleMainStatu(row['ErrorMessage'])
                time.sleep(2)
                SetMachineStatu(row['ErrorMessage'])
        
        # Handle case where no card found
        if IsExist==0:
            ErrMsgCard="Card is not registered (TEST)"
            if KartNo=="735314E0":
                ErrMsgCard="Card reader error (TEST)"
            
            print("Card is not registered (TEST) :%s" % (KartNo))
            ScreenUpdateTextStatu(ErrMsgCard,5)
            GUI_ShowIfPossibleMainStatu(ErrMsgCard + "!")
            
            if G_Machine_CardReaderModel=="Eject":
                time.sleep(3)
            else:
                time.sleep(5)
            CardReaderSQLResult= "Card is not registered"
        
        print("</SQL_ReadCustomerInfo_Test>------------------------------------")
        return CardReaderSQLResult
        
    except Exception as e:
        ExceptionHandler("SQL_ReadCustomerInfo_Test",e,1)
        print("</SQL_ReadCustomerInfo_Test>------------------------------------")
        return "Test function error"


def SQL_ReadCustomerInfo(KartNo,CardRawData):
    print("                                                                ")
    print("                                                                ")
    print("****************************************************************")
    print("<SQL_ReadCustomerInfo>------------------------------------------")
    try:
        GUI_ShowIdleWindow()
        print("KartNo", KartNo, "IsCardReaderBusy", IsCardReaderBusy)
        global G_User_CardType
        global G_LastGame_Action
        global G_SessionStarted
        global G_CardMachineLogId
        global G_User_CardNo
        global IsCardInside
        global G_Machine_Balance
        global G_Machine_Promo
        global G_LastCardExit
        global G_User_PrevCardNo
        global G_LastCardEnter
        global IsWaitAtLeastCardExistDbSaved
        global BillAcceptor_Amount
        global Global_ParaYuklemeFail_SQL
        global G_SAS_Transfer_Warning_DoorIsLocked
        global Nextion_CurrentStep
        global IsWaitingAdminScreen
        global G_SAS_IsProblemOnCredit
        global Cashout_Source
        global G_SAS_LastAFTOperation
        global G_Machine_ReservationDate
        global G_LastGameEnded
        global G_Session_CardExitStatus
        global G_MessageCount
        global Global_ParaSifirla_84
        G_MessageCount=0
        Cashout_Source=0
        G_SAS_LastAFTOperation=""
        Global_ParaSifirla_84=0

        G_SAS_Transfer_Warning_DoorIsLocked=0


        #Learn Asset No
        if G_Device_AssetNo==0:
            Komut_ReadAssetNo()
        

        #<Here check card type>#############################################
        if 1==2:  # This section is disabled but converted for consistency
            try:
                print("Check card type")
                # Original MSSQL procedure: tsp_CardReadPartial
                result = db_helper.execute_database_operation(
                    'tsp_cardreadpartial',  # PostgreSQL lowercase name
                    [G_Machine_Mac, KartNo]
                )

                for row in result:
                    if 1==1:
                        CardTypeId = int(row["CardTypeId"])
                    
                    if CardTypeId == 0:
                        print("Normal musteri karti")
            except Exception as ecardtype:
                ExceptionHandler("tsp_CardReadPartial", ecardtype, 1)
        #</Here check card type>############################################
        

        BillAcceptor_Amount=Decimal(0)

        LastCardExitDiff=(datetime.datetime.now()-G_LastCardExit).total_seconds()
        if LastCardExitDiff<=1:
            GUI_ShowIfPossibleMainStatu("Wait 2 seconds for new card")
            print("Wait 2 seconds for new card",LastCardExitDiff)
            return "Wait 2 seconds for new card"


        SQL_Safe_InsImportantMessage("Card is inserted " + KartNo,76)

        if len(G_User_CardNo)>0:
            print("Sistemde zaten kart var. E:%s Y:%s"%(G_User_CardNo, KartNo))
            SQL_InsImportantMessage("GM already has card. E:%s Y:%s" % (G_User_CardNo, KartNo),3)
            return "Sistemde zaten kart var."


        if IsSystemLocked==1:
            PrintAndSetAsStatuText("System cant accept card-in")
            return "System cant accept card-in"

        #2020-06-24 Kapattim, 2020-07-02 Geri actim
        #2021-04-23 kapattim
        #2021-05-08 Actim.. Hep acik kalsin.
        OpenCloseSasPort(1,0)

        GetMeter(0,"readcustomer")

        if 1==1:#if G_Machine_IsCashless==1:
            GUI_ShowIfPossibleMainStatu("Waiting for balance answer")
            if Wait_Bakiye(1,1,"sqlreadcustomer")==0:
                GUI_ShowIfPossibleMainStatu("Unable to query balance on Card Read")
                PrintAndSetAsStatuText("Unable to query balance on Card Read")
                return "Unable to query balance on Card Read"




        IsCancelUploadMoney=0
        if IsDebugNotControlAfterCardInserted==0 and (Yanit_BakiyeTutar>0 or Yanit_RestrictedAmount>0 or Yanit_NonRestrictedAmount>0)==True:

            if KartNo!=G_User_PrevCardNo and len(G_User_PrevCardNo)>2 and Yanit_BakiyeTutar>=1:
                SQL_InsImportantMessageByWarningType("G.M. has money. Can't insert card. Balance: %s / %s / %s Card: %s / %s" % (Yanit_BakiyeTutar, Yanit_RestrictedAmount, Yanit_NonRestrictedAmount,  KartNo, G_User_PrevCardNo),4,2)
                Kilitle("GM has money")
                return "GM has money"
            else:
                if Yanit_BakiyeTutar>=1:
                    print("***********************************************")
                    print("MUSTAFA 1-2-3!!!!!!!!!!!!!!!!!!!!!!!!!")
                    IsCancelUploadMoney=1
                    print("***********************************************")


                Ac("User owned this money")
                print("******************G.M. had money. But allowed to put this money, K: %s Balance: %s / %s / %s" % (KartNo, Yanit_BakiyeTutar, Yanit_RestrictedAmount, Yanit_NonRestrictedAmount))
                SQL_InsImportantMessageByWarningType("G.M. had money.But allowed to put this money, K: %s Balance: %s / %s / %s" % (KartNo, Yanit_BakiyeTutar, Yanit_RestrictedAmount, Yanit_NonRestrictedAmount),4,3)
        #else:
        #    print("Merkurlerde otomatik play aktif ettiginde; makinada para oldugunda da oynatmaya basliyor")
        #    #2020-02-11
        #    #EnableDisableAutoPlay(1)
        #    #Merkurlerde otomatik play aktif ettiginde; makinada para oldugunda da oynatmaya basliyor

        if len(G_Machine_ReservationCard)>0:
            if G_Machine_ReservationCard!=KartNo:
                ReservationDiff=((G_Machine_ReservationDate + datetime.timedelta(minutes=10))-datetime.datetime.now()).total_seconds()
                if ReservationDiff>0 and ReservationDiff<600:
                    hours = int(ReservationDiff / 3600)
                    minutes = int(ReservationDiff / 60) % 60
                    secs=round(ReservationDiff-(minutes*60))

                    ReservationDateText = str(minutes) + " mins " + str(secs) + " sec. "
                    LocalText="GM is reserved for " + G_Machine_ReservationCustomername + "(" + ReservationDateText + ")" 
                    PrintAndSetAsStatuText(LocalText)
                    ShowNotifyScreen("RESERVED", LocalText ,5)
                    return "System is reserved"
            else:
                G_Machine_ReservationDate=datetime.datetime.now() - datetime.timedelta(minutes=30)
                Ac("Reservasyon back!")


        if IsDeviceLocked==1 and KartNo!=G_User_PrevCardNo:
            PrintAndSetAsStatuText("System is locked. Cant insert card")
            if IsGUI_Type!=3:
                ScreenUpdateTextStatu("System is locked. Cant insert card", 5)
            time.sleep(3)
            return "System is locked. Cant insert card"

        G_LastCardExit=datetime.datetime.now()
        print("CardNo:" , KartNo)




        SQL_StartDate=datetime.datetime.now()

        CustomCashable=0
        if G_Session_IsByOnline==1:
            CustomCashable=G_Online_CashInAmount
        CustomPromo=0
        NonameRequest=0

        print("tsp_CardRead", G_Machine_Mac, KartNo, CustomCashable, CustomPromo, NonameRequest, G_Machine_DeviceId)
        CardReaderSQLResult = "Normal"
        # Original MSSQL procedure: tsp_CardRead
        result = db_helper.execute_database_operation(
            'tsp_cardread',  # PostgreSQL lowercase name
            [G_Machine_Mac, KartNo, CustomCashable, CustomPromo, NonameRequest, G_Machine_DeviceId]
        )

        IsExist = 0
        for row in result:

            G_LastGame_Action=datetime.datetime.now()

            Diff=(datetime.datetime.now()-SQL_StartDate).total_seconds()
            print("SQL Diff", Diff)

           
            IsExist=1

            if row['Result']==True:

                #BillAcceptor_Reset()
                G_SessionStarted=datetime.datetime.now()
                G_Session_CardExitStatus=0

                Global_ParaYuklemeFail_SQL=0
                IsWaitAtLeastCardExistDbSaved=0
                
                print("************************** CARD INSIDE **************************")
                print("Result: %s, Message: %s, Kart No: %s Adi:%s, Bakiye:%s" % (row['Result'],row['ErrorMessage'], G_User_CardNo, row['Fullname'], row['Balance']))
            
                UploadMoney=int(row["UploadMoney"])
                print("UploadMoney",UploadMoney)
                if UploadMoney==0:
                    SQL_Safe_InsImportantMessageByWarningType("Settings.ini broken!",1,1)


                Balance=Decimal(row['Balance'])
                Promo=0
                try:
                    Promo=Decimal(row['PromoBalance'])
                except Exception as e2:
                    print("Promo yok")

                G_CardMachineLogId=int(row["CardMachineLogId"])


                #Makinada 1 TL'den fazla para var.
                if IsCancelUploadMoney==1:
                    print("*****************CANCELLED BALANCE INSERT!****************************")
                    Balance=0
                    Promo=0
                    if UploadMoney!=0:#Bunu 2020-11-27'de koydum. Settings.ini broken degilse
                        SQL_UpdInsertedBalance(G_CardMachineLogId, Balance, Promo)#hakanatici
                    SQL_Safe_InsImportantMessage("Cancelled balance insert because of GM has money",77)

                G_User_CardNo=KartNo
                G_User_PrevCardNo=KartNo
                IsCardInside=1

                G_User_CardType=0

                try:
                    G_User_CardType=int(row["CardType"])
                except Exception as esql:
                    print("Card Type!")

                try:
                    Config.set('customer','cardnumber', G_User_CardNo)
                    Config.set('customer','customerid', str(int(row["CustomerId"])))
                    Config.set('customer','cardmachinelogid', str(int(row["CardMachineLogId"])))
                    Config.set('customer','gender', str(int(row["Gender"])))
                    Config.set('customer','customername', row['Fullname'])
                    Config.set('customer','nickname', row['Nickname'])
                    Config.set('customer','iscardinside', "1")
                    SaveConfigFile()

                    Config.set('customer','bonuspercentage', str(Decimal(row['BonusPercentage'])))
                    Config.set('customer','currentbonus', str(Decimal(row['CurrentBonus'])))
                    Config.set('customer','earnedbonus', str(Decimal(0)))

                    Config.set('customer','inserteddate', str(datetime.datetime.now()))
                    
                    Config.set('customer','playcount', "0")
                    Config.set('customer','totalbet', "0")
                    Config.set('customer','totalwin', "0")
                    Config.set('customer','ismoneytransfered', "0")
                
                    G_Machine_Balance=Balance
                    G_Machine_Promo=Promo
                
                    Config.set('customer','customerbalance', str(G_Machine_Balance))
                    Config.set("customer","currentbalance",str(G_Machine_Balance))

                    Config.set("customer","customerpromo",str(G_Machine_Promo))
                    Config.set("customer","currentpromo",str(G_Machine_Promo))

                except Exception as esql:
                    print("Config Set Err Init!")

                #IsCardInside SaveConfigFile'dan sonraydi. Buraya koyduk.
                SaveConfigFile()


                ParaYukleSonuc=1
                if G_Machine_IsCashless==1 and UploadMoney==1:
                    ParaYukleSonuc=Wait_ParaYukle(0)
                    SQL_Safe_InsImportantMessage("Cashin Result:" + str(ParaYukleSonuc) ,78)
                    try:
                        if str(Global_ParaYukleme_TransferStatus)=="C0" and G_Machine_IsRulet==1:
                            Wait_Bakiye(2,1,"cardexit2")
                            if Yanit_BakiyeTutar==0:
                                SQL_Safe_InsImportantMessageByWarningType("Roulette cashin error",10,0)
                                ParaYukleSonuc=0
                    except Exception as eRoulette:
                        print("ebe")
                try:
                    SQL_Safe_InsImportantMessage("Session started: " + row['Fullname'] + " C:" + str(G_Machine_Balance) + " P:" +  str(G_Machine_Promo),79)
                except Exception as esql:
                    print("SQL_Safe 1")

                G_LastCardEnter=datetime.datetime.now()
                G_LastGame_Action=datetime.datetime.now()
                G_LastGameEnded=datetime.datetime.now()

                G_SAS_IsProblemOnCredit=0

                print("ParaYukleSonuc:" , ParaYukleSonuc)
                if ParaYukleSonuc==0:

                    #<2021-07-06 Mevcut para yuklendiyse diye kontrol et rulette>
                    try:
                        if G_Machine_IsRulet==1:
                            time.sleep(1)
                            Wait_Bakiye(1,1,"CheckParaYukle-Sonuc")
                            if Yanit_BakiyeTutar==G_Machine_Balance and Yanit_BakiyeTutar>0:
                                SQL_Safe_InsImportantMessageByWarningType("Roulette cashin OK! " + str(Yanit_BakiyeTutar) + "-" + str(G_Machine_Balance) ,10,0)
                                ParaYukleSonuc=1
                                G_SAS_IsProblemOnCredit=0
                    except Exception as eRoulette:
                        print("ebe")
                    #</2021-07-06 Mevcut para yuklendiyse diye kontrol et rulette>


                    if ParaYukleSonuc==0:
                        G_SAS_IsProblemOnCredit=1
                        try:
                            SQL_Safe_InsImportantMessageByWarningType("Cancelled card insert S:"+ Global_ParaYukleme_TransferStatus,10,20)
                        except Exception as exCancelled:
                            print("Cancelled card insert")


                        if ParaYukleSonuc==0:
                            print("Cancelled card insert")
                            CardIsRemoved(2)
                            return "Cancelled card insert. Cant upload money"
                else:
                    G_SAS_IsProblemOnCredit=0
                    
                
                if ParaYukleSonuc==1:
                    ChangeRealTimeReporting(1)
                    Komut_EnableBillAcceptor()#2020-08-31 Ishak ile duzeltildi.

                GUI_ShowCustomerWindow()



                if G_Machine_IsBonusGives==1 and IsGUI_Type!=2:
                    GUI_ShowBonus()

                #Komut_Interragition("ReadyForGame1")
                

                #ChangeCustomerScreenLineTimed(3,"%s %s Transfered" % (row['Balance'], G_Machine_Currency),5,"GOOD LUCK")
                ChangeCustomerScreenLineTimed(3,"Ready!",2,"GOOD LUCK")
                G_LastCardExit=datetime.datetime.now()

                PrintAndSetAsStatuText("Ready for game!")
                Ac("Ready for game")

                print("G_Machine_IsAutoNextVisit", G_Machine_IsAutoNextVisit)
                if G_Machine_IsAutoNextVisit==1 and G_Machine_IsRulet==0:
                    CheckNextVisit()

                if G_Machine_IsAutoNextVisit==2 and G_Machine_IsRulet==0:
                    CheckNextVisit_ByTurnover()
                
                G_SessionStarted=datetime.datetime.now()

                #Zuum rulet icin.
                if G_Machine_DeviceTypeId==9:
                    Komut_CancelBalanceLock()
                else:
                    Komut_BakiyeSorgulama(1,1,"cardinstalled-1")


                G_LastCardExit=datetime.datetime.now()

            else:
                CardReaderSQLResult=row['ErrorMessage']
                try:
                    SQL_InsImportantMessageByWarningType(CardReaderSQLResult, 1, 0)
                except Exception as eC1:
                    print("Message: " , eC1)
                print("Error - 1", row['ErrorMessage'])
                GUI_ShowIfPossibleMainStatu(row['ErrorMessage'])
                time.sleep(2)
                SetMachineStatu(row['ErrorMessage'])
                
                
                
        if IsExist==0:

            ErrMsgCard="Card is not registered"
            if KartNo=="735314E0":
                ErrMsgCard="Card reader error"

            print("Card is not registered :%s" % (KartNo))
            ScreenUpdateTextStatu(ErrMsgCard,5)
            GUI_ShowIfPossibleMainStatu(ErrMsgCard + "!")
            #SQL_InsImportantMessageByWarningType(ErrMsgCard + " :" + str(KartNo) + " Raw:" + CardRawData, 1, 4)

            if G_Machine_CardReaderModel=="Eject":
                time.sleep(3)
            else:
                time.sleep(5)
            CardReaderSQLResult= "Card is not registered"

    except Exception as e:
        ExceptionHandler("SQL_ReadCustomerInfo",e,1)

    print("</SQL_ReadCustomerInfo>------------------------------------------")
    print("****************************************************************")
    
    return CardReaderSQLResult


def ExceptionHandler(name, e, Insert2DB):
    try:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("Exception On ", name, exc_type, fname, exc_tb.tb_lineno)
        if Insert2DB==1:
            SQL_InsException(name,"%s %s %s" % (exc_type, fname, exc_tb.tb_lineno))
    except Exception as ex:
        print("Exception Handler Exploded: " , name)



def SQL_InsEventAfterNewGamingDateCommand(typeid):
    # Original MSSQL procedure: tsp_InsEventAfterNewGamingDateCommand
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    result = []
    try:
        result = db_helper.queue_database_operation(
            'tsp_InsEventAfterNewGamingDateCommand',
            [G_Machine_DeviceId, typeid],
            'insert_event_after_new_gaming_date_command'
        )
    except Exception as e:
        ExceptionHandler("tsp_EventsAfterNewGamingDateCommand", e, 1)
    GetMeter(1, "insevent")

    return result

def SQL_GetNextVisit():
    # Original MSSQL procedure: tsp_GetNextVisit
    result = []
    try:
        result = db_helper.execute_database_operation(
            'tsp_getnextvisit',  # PostgreSQL lowercase name
            [G_Machine_DeviceId, G_CardMachineLogId, G_User_CardNo, 1]
        )
    except Exception as e:
        ExceptionHandler("tsp_GetNextVisit", e, 1)

    return result


def SQL_GetNextVisit_ByTurnover(isTakePrize):
    # Original MSSQL procedure: tsp_GetNextVisit_ByTurnover
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    result = []
    try:
        result = db_helper.queue_database_operation(
            'tsp_GetNextVisit_ByTurnover',
            [G_Machine_DeviceId, G_CardMachineLogId, G_User_CardNo, isTakePrize],
            'get_next_visit_by_turnover'
        )
    except Exception as e:
        ExceptionHandler("tsp_GetNextVisit_ByTurnover", e, 1)

    return result

def SQL_InsKioskBonusWon():
    # Original MSSQL procedure: tsp_InsKioskBonusWon
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    try:
        return db_helper.queue_database_operation(
            'tsp_InsKioskBonusWon',
            [G_User_CardNo, G_NextVisit_KioskBonusId, G_NextVisit_WonAmount, 0],
            'insert_kiosk_bonus_won'
        )
    except Exception as e:
        ExceptionHandler("tsp_InsKioskBonusWon", e, 1)
        return []



#def SQL_test():
#    result = []
#    try:
#        conn = pymssql.connect(host=G_DB_Host, user=G_DB_User, password=G_DB_Password, database=G_DB_Database,tds_version='7.2')
#        conn.autocommit(True)
#        cursor = conn.cursor(as_dict=True)
#        cursor.callproc('tsp_test', (1, 1))
#        conn.close()
#    except Exception as e:
#        ExceptionHandler("SQL_test",e,1)


#    return result


#SQL_test()




def SQL_UpdDeviceEnablesGames(EnabledGameIds, FullMessage):
    # Original MSSQL procedure: tsp_UpdDeviceEnablesGames  
    try:
        return db_helper.execute_database_operation(
            'tsp_upddeviceenablesgames',  # PostgreSQL lowercase name
            [G_Machine_DeviceId, EnabledGameIds, FullMessage]
        )
    except Exception as e:
        ExceptionHandler("tsp_UpdDeviceEnablesGames", e, 1)
        return []



def SQL_UpdDeviceAdditionalInfo(Temperature, Throttle, ThreadCount, CPUUsage, MemoryUsage):
    # Original MSSQL procedure: tsp_UpdDeviceAdditionalInfo
    try:
        Last_G_SASLastDate_Diff = (datetime.datetime.now() - G_SASLastDate).total_seconds()
        return db_helper.execute_database_operation(
            'tsp_upddeviceadditionalinfo',  # PostgreSQL lowercase name
            [G_Machine_DeviceId, Temperature, Throttle, ThreadCount, CPUUsage, MemoryUsage, Last_G_SASLastDate_Diff]
        )
    except Exception as e:
        ExceptionHandler("tsp_UpdDeviceAdditionalInfo", e, 1)
        return []



def SQL_GetDeviceAdditionalInfo(deviceId):
    # Original MSSQL procedure: tsp_GetDeviceAdditionalInfo
    try:
        return db_helper.execute_database_operation(
            'tsp_getdeviceadditionalinfo',  # PostgreSQL lowercase name
            [deviceId]
        )
    except Exception as e:
        ExceptionHandler("tsp_GetDeviceAdditionalInfo", e, 1)
        return []


def SQL_UpdDeviceAdditionalInfoHash(HashKey):
    # Original MSSQL procedure: tsp_UpdDeviceAdditionalInfoHash
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    try:
        Last_G_SASLastDate_Diff = (datetime.datetime.now() - G_SASLastDate).total_seconds()
        return db_helper.queue_database_operation(
            'tsp_UpdDeviceAdditionalInfoHash',
            [G_Machine_DeviceId, HashKey],
            'update_device_additional_info_hash'
        )
    except Exception as e:
        ExceptionHandler("tsp_UpdDeviceAdditionalInfoHash", e, 0)
        return []



def SQL_UpdInsertedBalance(machinelogid, inputbalance, promoin):
    # Original MSSQL procedure: tsp_UpdInsertedBalance
    try:
        return db_helper.execute_database_operation(
            'tsp_updinsertedbalance',  # PostgreSQL lowercase name
            [machinelogid, inputbalance, promoin]
        )
    except Exception as e:
        ExceptionHandler("tsp_UpdInsertedBalance", e, 1)
        return []



def SQL_InsDeviceHandpay(ProgressiveGroup, HandpayLevel, Amount, PartialPay, ResetId, UnUsed, HandpayMessage):
    # Original MSSQL procedure: tsp_InsDeviceHandpay
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    try:
        return db_helper.queue_database_operation(
            'tsp_InsDeviceHandpay',
            [G_Machine_DeviceId, G_CardMachineLogId, ProgressiveGroup, HandpayLevel, Amount, PartialPay, ResetId, UnUsed, HandpayMessage],
            'insert_device_handpay'
        )
    except Exception as e:
        ExceptionHandler("tsp_EventsAfterNewGamingDateCommand", e, 1)
        return []



def SQL_UpdDeviceDenomPayBack(PayBackPerc, Denomination, GameId, MaxBet):
    # Original MSSQL procedure: tsp_UpdDeviceDenomPayBack
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    try:
        return db_helper.queue_database_operation(
            'tsp_UpdDeviceDenomPayBack',
            [G_Machine_DeviceId, PayBackPerc, Denomination, GameId, MaxBet],
            'update_device_denom_payback'
        )
    except Exception as e:
        ExceptionHandler("tsp_UpdDeviceDenomPayBack", e, 1)
        return []





def SQL_UpdAssetNoSMIB(assetno):
    # Original MSSQL procedure: tsp_UpdAssetNoSMIB
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    try:
        return db_helper.queue_database_operation(
            'tsp_UpdAssetNoSMIB',
            [G_Machine_DeviceId, assetno],
            'update_asset_no_smib'
        )
    except Exception as e:
        ExceptionHandler("tsp_UpdAssetNoSMIB", e, 1)
        return []


def SQL_InsProductOrderBySlot(Products):
    # Original MSSQL procedure: tsp_InsProductOrderBySlot
    try:
        customerid = Config.getint('customer', 'customerid')
        return db_helper.execute_database_operation(
            'tsp_insproductorderbyslot',  # PostgreSQL lowercase name
            [customerid, G_Machine_DeviceId, Products]
        )
    except Exception as e:
        ExceptionHandler("tsp_InsProductOrderBySlot", e, 1)
        return []


def SQL_GetProductCategories():
    # Original MSSQL procedure: tsp_GetProductCategories
    try:
        return db_helper.execute_database_operation(
            'tsp_getproductcategories',  # PostgreSQL lowercase name
            []
        )
    except Exception as e:
        ExceptionHandler("SQL_GetProductCategories", e, 1)
        return []



def SQL_CardReadAddMoney(customerid, amount, operationType):
    # Original MSSQL procedure: tsp_CardReadAddMoney
    try:
        cardmachinelogid = 0
        cardmachinelogid = Config.getint('customer', 'cardmachinelogid')
        return db_helper.execute_database_operation(
            'tsp_cardreadaddmoney',  # PostgreSQL lowercase name
            [cardmachinelogid, customerid, amount, operationType]
        )
    except Exception as e:
        ExceptionHandler("SQL_CardReadAddMoney", e, 1)
        return []


def SQL_GetCustomerCurrentMessages():
    # Original MSSQL procedure: tsp_GetCustomerCurrentMessages
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    try:
        customerid = Config.getint('customer', 'customerid')
        cardmachinelogid = Config.getint('customer', 'cardmachinelogid')
        return db_helper.queue_database_operation(
            'tsp_GetCustomerCurrentMessages',
            [customerid, cardmachinelogid],
            'get_customer_current_messages'
        )
    except Exception as e:
        ExceptionHandler("tsp_GetCustomerCurrentMessages", e, 1)
        return []



def SQL_GetSlotCustomerDiscountCalc(isAddDiscount):
    # Original MSSQL procedure: tsp_GetSlotCustomerDiscountCalc
    try:
        customerid = Config.getint('customer', 'customerid')
        cardmachinelogid = Config.getint('customer', 'cardmachinelogid')
        return db_helper.execute_database_operation(
            'tsp_getslotcustomerdiscountcalc',  # PostgreSQL lowercase name
            [customerid, cardmachinelogid, G_User_CardNo, isAddDiscount]
        )
    except Exception as e:
        ExceptionHandler("tsp_GetSlotCustomerDiscountCalc", e, 1)
        return []


def SQL_GetCustomerMessage(messageid):
    # Original MSSQL procedure: tsp_GetCustomerMessage
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    try:
        customerid = Config.getint('customer', 'customerid')
        cardmachinelogid = Config.getint('customer', 'cardmachinelogid')
        return db_helper.queue_database_operation(
            'tsp_GetCustomerMessage',
            [messageid, customerid, cardmachinelogid],
            'get_customer_message'
        )
    except Exception as e:
        ExceptionHandler("tsp_GetCustomerCurrentMessages", e, 1)
        return []



def SQL_UpdMessageAwardAttempt(messageid):
    # Original MSSQL procedure: tsp_UpdMessageAwardAttempt
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    try:
        customerid = Config.getint('customer', 'customerid')
        cardmachinelogid = Config.getint('customer', 'cardmachinelogid')
        return db_helper.queue_database_operation(
            'tsp_UpdMessageAwardAttempt',
            [messageid, customerid, cardmachinelogid],
            'update_message_award_attempt'
        )
    except Exception as e:
        ExceptionHandler("tsp_UpdMessageAwardAttempt", e, 1)
        return []


def SQL_UpdMessageAwardAsUsed(messageid):
    # Original MSSQL procedure: tsp_UpdMessageAwardAsUsed
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    try:
        customerid = Config.getint('customer', 'customerid')
        cardmachinelogid = Config.getint('customer', 'cardmachinelogid')
        return db_helper.queue_database_operation(
            'tsp_UpdMessageAwardAsUsed',
            [messageid, customerid, cardmachinelogid],
            'update_message_award_as_used'
        )
    except Exception as e:
        ExceptionHandler("tsp_UpdMessageAwardAsUsed", e, 1)
        return []


def SQL_BonusRequestList():
    # Original MSSQL procedure: tsp_BonusRequestList
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    try:
        customerid = Config.getint('customer', 'customerid')
        EarnedBonus = str(Config.get("customer", "earnedbonus"))
        cardmachinelogid = Config.getint('customer', 'cardmachinelogid')
        return db_helper.queue_database_operation(
            'tsp_BonusRequestList',
            [customerid, EarnedBonus, G_Machine_DeviceId, cardmachinelogid, G_User_CardNo, G_SelectedGameId],
            'bonus_request_list'
        )
    except Exception as e:
        ExceptionHandler("SQL_BonusRequestList", e, 1)
        return []



def SQL_GetLastSessionOfDevice(isinuse):
    # Original MSSQL procedure: tsp_GetLastSessionOfDevice
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    try:
        return db_helper.queue_database_operation(
            'tsp_GetLastSessionOfDevice',
            [G_Machine_DeviceId, isinuse],
            'get_last_session_of_device'
        )
    except Exception as e:
        ExceptionHandler("SQL_GetLastSessionOfDevice", e, 1)
        return []


def SQL_InsBonusRequest(amount):
    # Original MSSQL procedure: tsp_InsBonusRequest
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    global G_LastGame_IsFinished
    try:
        customerid = Config.getint('customer', 'customerid')
        EarnedBonus = str(Config.get("customer", "earnedbonus"))
        cardmachinelogid = Config.getint('customer', 'cardmachinelogid')
        LastGameDiff = (datetime.datetime.now() - G_LastGame_Action).total_seconds()
        return db_helper.queue_database_operation(
            'tsp_InsBonusRequest',
            [customerid, EarnedBonus, amount, G_Machine_DeviceId, cardmachinelogid, G_User_CardNo, G_SelectedGameId, G_LastGame_IsFinished, LastGameDiff],
            'insert_bonus_request'
        )
    except Exception as e:
        ExceptionHandler("tsp_InsBonusRequest", e, 1)
        return []


def SQL_UpdBonusAsUsed(bonusid):
    # Original MSSQL procedure: tsp_UpdBonusAsUsed
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    try:
        cardmachinelogid = Config.getint('customer', 'cardmachinelogid')
        return db_helper.queue_database_operation(
            'tsp_UpdBonusAsUsed',
            [bonusid, cardmachinelogid],
            'update_bonus_as_used'
        )
    except Exception as e:
        ExceptionHandler("tsp_UpdBonusAsUsed", e, 1)
        return []


def SQL_GetProductsAndSubCategoriesSlot(categoryId, type):
    # Original MSSQL procedure: tsp_GetProductsAndSubCategoriesSlot
    try:
        customerid = Config.getint('customer', 'customerid')
        return db_helper.execute_database_operation(
            'tsp_getproductsandsubcategoriesslot',  # PostgreSQL lowercase name
            [categoryId, customerid, type]
        )
    except Exception as e:
        ExceptionHandler("tsp_GetProductsAndSubCategoriesSlot", e, 1)
        return []



def SQL_ChangeDeviceNameAndType(machinename, devicetypeid):
    # Original MSSQL procedure: tsp_ChangeDeviceNameAndType
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    try:
        result = db_helper.queue_database_operation(
            'tsp_ChangeDeviceNameAndType',
            [G_Machine_Mac, machinename, devicetypeid],
            'change_device_name_and_type'
        )
        for row in result:
            print("OK")
    except Exception as e:
        ExceptionHandler("SQL_ChangeDeviceNameAndType", e, 1)



def SQL_UpdGameName(GameId, GameName):
    # Original MSSQL procedure: tsp_UpdGameName
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    try:
        result = db_helper.queue_database_operation(
            'tsp_UpdGameName',
            [G_Machine_DeviceId, GameId, GameName],
            'update_game_name'
        )
        for row in result:
            print("OK")
    except Exception as e:
        ExceptionHandler("tsp_UpdGameName", e, 1)

def SQL_UpdDeviceIsLocked(IsLocked):
    # Original MSSQL procedure: tsp_UpdDeviceIsLocked
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    try:
        result = db_helper.queue_database_operation(
            'tsp_UpdDeviceIsLocked',
            [G_Machine_DeviceId, IsLocked],
            'update_device_is_locked'
        )
        for row in result:
            IsLocked = IsLocked
    except Exception as e:
        ExceptionHandler("SQL_UpdDeviceIsLocked", e, 1)


def SQL_UpdBillAcceptorMoney(billAcceptorId, isUploaded):
    # Original MSSQL procedure: tsp_UpdBillAcceptorMoney
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    try:
        result = db_helper.queue_database_operation(
            'tsp_UpdBillAcceptorMoney',
            [billAcceptorId, isUploaded],
            'update_bill_acceptor_money'
        )
        for row in result:
            billAcceptorId = billAcceptorId
    except Exception as e:
        ExceptionHandler("SQL_UpdBillAcceptorMoney", e, 1)

def SQL_UpdDeviceSASSerial(SASVersion, SerialNo):
    # Original MSSQL procedure: tsp_UpdDeviceSASSerial
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    try:
        result = db_helper.queue_database_operation(
            'tsp_UpdDeviceSASSerial',
            [G_Machine_Mac, SASVersion, SerialNo],
            'update_device_sas_serial'
        )
        for row in result:
            print("OK")
    except Exception as e:
        ExceptionHandler("SQL_UpdDeviceSASSerial", e, 1)

def SQL_CheckSystemAfterCardExit(cardmachinelogid):
    # Original MSSQL procedure: tsp_CheckSystemAfterCardExit
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    try:
        result = db_helper.queue_database_operation(
            'tsp_CheckSystemAfterCardExit',
            [G_Machine_DeviceId, cardmachinelogid],
            'check_system_after_card_exit'
        )
        for row in result:
            print("OK")
    except Exception as e:
        ExceptionHandler("SQL_CheckSystemAfterCardExit", e, 1)



def SQL_InsDeviceWaiterCall():
    # Original MSSQL procedure: sp_InsDeviceWaiterCall
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    try:
        customerid = Config.getint('customer', 'customerid')
        result = db_helper.queue_database_operation(
            'sp_InsDeviceWaiterCall',
            [G_Machine_Mac, customerid],
            'insert_device_waiter_call'
        )
        for row in result:
            print("OK")
    except Exception as e:
        ExceptionHandler("SQL_InsDeviceWaiterCall", e, 1)



def SQLite_InsBillAcceptor(machinelogid, cardno, amount,amountcode,countrycode,piece, issynced, amountbase):
    try:
        SQLText="insert into billacceptor(machinelogid,cardno,amount,amountcode,countrycode,piece,issynced,amountbase)values('"+str(machinelogid)+"','"+str(cardno)+"','"+str(amount)+"','" + str(amountcode)+"','" + str(countrycode)+"','" + str(piece)+"','" + str(issynced)+"','"+str(amountbase)+"')"
        c.execute(SQLText)
        conn.commit()
    except Exception as e11:
        ExceptionHandler("SQLite_InsBillAcceptor",e11,0)


BillAcceptor_Amount=Decimal(0)
def SQL_InsBillAcceptorMoneyEFT(cardmachinelogid, cardno, amount, amountcode, countrycode, piece, islog,isUploaded, amountBase):
    piece=1

    try:
        global G_Machine_Balance
        global BillAcceptor_Amount

        try:
            BillAcceptor_Amount=Decimal(BillAcceptor_Amount)+Decimal(amount)
            G_Machine_Balance=Decimal(G_Machine_Balance)+Decimal(amount)
            Config.set("customer","currentbalance",str(G_Machine_Balance))
            SaveConfigFile()
        except Exception as e:
            ExceptionHandler(" Amount Update",e,1)

        if amount!=amountBase:
            SQL_Safe_InsImportantMessage("Bill is inserted: " + str(amountBase) + " " + countrycode + " (" + str(amount) + ")",80)
        else:
            SQL_Safe_InsImportantMessage("Bill is inserted: " + str(amount),80)

        # Original MSSQL procedure: tsp_InsBillAcceptorMoney
        result = db_helper.execute_database_operation(
            'tsp_insbillacceptormoney',  # PostgreSQL lowercase name
            [cardmachinelogid, cardno, amount, amountcode, G_Machine_Mac, countrycode, piece, G_Machine_DeviceId, islog, isUploaded, amountBase]
        )
        BillAcceptorId = 1
        try:
            for row in result:
                BillAcceptorId = int(row["Result"])
        except Exception as eCursor:
            ExceptionHandler("SQL_InsBillAc", eCursor, 0)

        return BillAcceptorId
    except Exception as e:
        SQLite_InsBillAcceptor(cardmachinelogid,cardno,amount,amountcode,countrycode,piece,0,amountBase)
        ExceptionHandler("SQL_InsBillAcceptorMoneyEFT",e,1)
        return 0


def ExecuteCommand(Command):
    global G_Machine_NewGamingDay

    Command=Command.replace("\n","")
    Command=Command.replace("\\n","")
    print("Execute to Command", Command)
    
    if Command=="customerreset":
        global G_User_CardNo
        G_User_CardNo=""
        RemoveCustomerInfoOnConfig()
        GUI_ShowIdleWindow()
        ExecuteCommand("sifirla:")


    
    if Command=="manualgamingdate" and IsGUIEnabled==1:
        G_Machine_NewGamingDay=0
        Config.set('machine','newgamingday', "0")
        SaveConfigFile()
        CardReader_CardExitEnd()
        GUI_ShowIfPossibleMainStatu("New gaming day is started!")

    if Command=="restart":
        SQL_Safe_InsImportantMessage("Card Remove Steps (Before Restart) " + Step_CardIsRemoved +"-" + Step_RemoveCustomerInfo +"-" + Step_Parasifirla,100)
        Config.set('customer','isrestartedsafely', "1")
        SaveConfigFile()
        PrintAndSetAsStatuText("Reset status")
        print("Restart edilecek")
        ExecuteLinuxCommand("/usr/bin/sudo /sbin/shutdown -r now")

    if Command=="restartprogram" or Command=="restartprogram:":
        print("Program Restart edilecek")
        RestartProgram()

    if Command=="removecard":
        print("Force card read")
        CardIsRemoved(1)

    if Command=="handpay":
        Wait_RemoteHandpay()
        
    if Command=="endgame":
        SQL_InsImportantMessage("Cashout is availabled by slot manager",20)
        PrintAndSetAsStatuText("Cashout is availabled by slot manager")
        IsAvailableForCashoutButton=1
        
    if Command=="eb:":
        Komut_EnableBillAcceptor()
        
    if Command=="db:":
        Komut_DisableBillAcceptor("command")


    if Command=="newgamingday":
        G_Machine_NewGamingDay=1
        Config.set('machine','newgamingday', "1")
        SaveConfigFile()
        GUI_ShowIfPossibleMainStatu("Waiting for new gaming date!")
        if IsCardInside==0:
            CardReader_WaitingNewDay()

        #if IsCardInside==1:
        #    while IsCardInside==1:
        #        time.sleep(1)
        #        print("Waiting customer to take card")
        #    if IsCardInside==0:
        #        Kilitle("LockForCashboxOut")
        #        time.sleep(2)
        #        CardReader_WaitingNewDay()

                



    if Command=="getmeter":
        GetMeter(0,"getmeter")

    if Command=="getmeter2" or Command=="getmeter2:":
        GetMeter(1,"getmeter")
        
    if Command.startswith("cmdline:"):
        Command=Command.replace("cmdline:","")
        try:
            HandUserInput(Command)
        except Exception as eX5:
            print("HandUserInput")
        
    if Command.startswith("cmd:"):
        Command=Command.replace("cmd:","")
        if Command.find("guncelle") != -1:
            try:
                print("Ekran guncellemesi************************************************************************")
                nextionport.close()
            except Exception as eGuncele:
                print("Nextion close error!!")


        ExecuteLinuxCommand(Command)
        
    if Command.startswith("sas:"):
        Command=Command.replace("sas:","")
        
        if "CRC" in Command:
            Command=Command.replace("CRC","")
            Command=GetCRC(Command)
            
        print("REMOTE COMMAND", len(Command), Command)
        SAS_SendCommand("REMOTE COMMAND",Command,1)
        time.sleep(0.9)


def Komut_GetMeter(isall,gameid):
    #time.sleep(G_Static_SasWait)
    
    IsNewMeter=0
    if G_CasinoId==8:#Golden
        IsNewMeter=1

    if G_CasinoId==11:#Atlantic
        IsNewMeter=1

    if G_CasinoId==7:#Corona
        IsNewMeter=1

    #if G_CasinoId==2:#Salamis
    #    IsNewMeter=1

    #A0: cardin
    #B8: cardout
    #02: jackpot credit
    #03: Handpay
    #1E: BONUS
    #00: turnover
    #01: turnout
    #0B: billacceptor
    #A2: restricted amount
    #BA: restricted amount end
    if isall==0 and IsNewMeter==0:
        SAS_SendCommand("getmeter2",GetCRC("012F0C0000A0B802031E00010BA2BA"),0)#yeni

    #A0: cardin
    #B8: cardout
    #02: jackpot credit
    #03: Handpay
    #1E: BONUS
    #00: turnover
    #01: turnout
    #0B: billacceptor
    #A2: restricted amount
    #BA: restricted amount end
    #05: Games Played
    #06: Games Won
    if isall==0 and IsNewMeter==1:
        #SAS_SendCommand("getmeter2",GetCRC("012F0C0000A0B802031E00010BA2BA"),1)#yeni
        #SAS_SendCommand("getmeter2",GetCRC("012F0C0000"),1)#yeni
        SAS_SendCommand("getmeter2",GetCRC("01AF1A0000A000B800020003001E00000001000B00A200BA0005000600"),0)#yeni
    

    #04: Total Cancelled Credits
    #05: Games Played
    #06: Games Won
    #0C: Current Credits
    #19: Total Restrictited Amount
    #1D: Total Machine paid progressive win (credits)
    #7F: Weighted average theoretical payback 
    #FA: Regular cashashle feyed on funds
    #FB: Restricted promotional keyed on funds
    #FC: Nonrestircted promotional keyed-on funds
    if isall==1:
        #SAS_SendCommand("getmeter2",GetCRC("012F0C0000A0B802031E00010BA2BA"),1)#yeni
        #SAS_SendCommand("getmeter2",GetCRC("012F0C0000"),1)#yeni
        SAS_SendCommand("getmeter2",GetCRC("012F0C00000405060C191D7FFAFBFC"),0)#yeni


    #A0: cardin
    #B8: cardout
    #02: jackpot credit
    #03: Handpay
    #1E: BONUS
    #00: turnover
    #01: turnout
    #0B: billacceptor
    #A2: restricted amount
    #BA: restricted amount end
    #05: Games Played
    #06: Games Won
    if isall==2:
        #SAS_SendCommand("getmeter2",GetCRC("012F0C0000A0B802031E00010BA2BA"),1)#yeni
        #SAS_SendCommand("getmeter2",GetCRC("012F0C0000"),1)#yeni
        SAS_SendCommand("getmeter2",GetCRC("01AF1A0000A000B800020003001E00000001000B00A200BA0005000600"),0)#yeni
    


IsWaitingForMeter=0
def GetMeter(isall,sender="Unknown", gameid=0):
    if IsDebugAutoBakiyeYanit==1:
        return

    L_OperationStartDate_Meter=datetime.datetime.now()
    try:
        if platform.system().startswith("Window")==True:
            print("Debug Meter")
            return


        print("Get meter",isall, sender)
        global IsWaitingForMeter
        IsWaitingForMeter=1

        Komut_GetMeter(isall,gameid)
        LastCommandDate_Meter=datetime.datetime.now()
        while IsWaitingForMeter==1:
            time.sleep(0.005)
            LastCommandDate_Diff=(datetime.datetime.now()-LastCommandDate_Meter).microseconds/1000
            FirstCommandDate_Meter_Diff=(datetime.datetime.now()-L_OperationStartDate_Meter).total_seconds()

            #2021-06-12 5 idi, 4 yaptim
            #2021-09-03: 0,5 SN'ye çektim.
            if IsWaitingForMeter==1 and (LastCommandDate_Diff/500)>1:
                Komut_GetMeter(isall,gameid)
                LastCommandDate_Meter=datetime.datetime.now()

            if IsWaitingForMeter==0:
                #print("Meter is received")
                break

            #2021-06-12 60 idi, 80 yaptim
            if FirstCommandDate_Meter_Diff>30:
                SQL_Safe_InsImportantMessage("System cant get meter from EGM",67)
                print("Cant learn meter!")
                break
        OperationDiff=(datetime.datetime.now()-L_OperationStartDate_Meter).total_seconds()*1000
        print("Get Meter completed", OperationDiff)
    except Exception as e:
        print("Getmeter error")




#<Create Bash Scripts for HDMI and Camera>----------------------------------------------------------
def CreateStreamingScriptHDMI(casinoId, deviceId, configId):
    
    BashScript=""
    
    BashScript=BashScript + "#!/usr/bin/env bash"
    BashScript=BashScript + "\n"
    BashScript=BashScript + "v4l2-ctl --set-edid=file=1080P50EDID.txt --fix-edid-checksums"
    BashScript=BashScript + "\n"
    BashScript=BashScript + "sleep 3"
    BashScript=BashScript + "\n"
    BashScript=BashScript + "v4l2-ctl --query-dv-timings"
    BashScript=BashScript + "\n"
    BashScript=BashScript + "sleep 3"
    BashScript=BashScript + "\n"
    BashScript=BashScript + "v4l2-ctl --set-dv-bt-timings query"
    BashScript=BashScript + "\n"
    BashScript=BashScript + "sleep 3"
    BashScript=BashScript + "\n"
    BashScript=BashScript + "v4l2-ctl -V"
    BashScript=BashScript + "\n"
    BashScript=BashScript + "sleep 3"
    BashScript=BashScript + "\n"
    BashScript=BashScript + "v4l2-ctl -v pixelformat=UYVY"
    BashScript=BashScript + "\n"
    BashScript=BashScript + "sleep 3"
    BashScript=BashScript + "\n"
    
    if configId==1:
        BashScript=BashScript + "gst-launch-1.0 -e v4l2src device=/dev/v4l/by-path/platform-fe801000.csi-video-index0 ! video/x-raw,format=UYVY,framerate=20/1 ! videoconvert ! videoscale ! video/x-raw, width=1280,height=720 ! videocrop top=0 left=0 right=800 bottom=0 ! videoflip method=counterclockwise ! omxh264enc ! h264parse!  flvmux name=mux streamable=true ! rtmpsink sync=true async=true location='rtmp://streaming.sanaloyun.net/LiveApp/"+ str(casinoId) + "-" + str(deviceId)+" live=true'"

    if configId==2:
        BashScript=BashScript + "gst-launch-1.0 -e v4l2src device=/dev/v4l/by-path/platform-fe801000.csi-video-index0 ! video/x-raw,format=UYVY,framerate=20/1 ! videoconvert ! videoscale ! video/x-raw, width=1280,height=720 ! videocrop top=0 left=0 right=800 bottom=0 ! videoflip method=counterclockwise ! omxh264enc ! h264parse!  flvmux name=mux streamable=true ! rtmpsink sync=true async=true location='rtmp://streaming.sanaloyun.net/LiveApp/"+ str(casinoId) + "-" + str(deviceId)+" live=true'"



    print("CREATE STREAMING!!!")
    textFile="/home/soi/dev/spark-sas2/streaming_hdmi.sh"
    CreateTextFile(textFile,BashScript)
    ExecuteLinuxCommand("sudo chmod +x " + textFile)
    ExecuteLinuxCommand("" + textFile)


def CreateStreamingScriptHDMIAudio(casinoId, deviceId, configId):
    BashScript=""
    
    BashScript=BashScript + "#!/usr/bin/env bash"
    BashScript=BashScript + "\n"
    
    if configId==1 and 2==1:
        BashScript=BashScript + "ffmpeg -ar 48000  -ac 1 -f alsa -i hw:1,0 -acodec aac -ab 128k -af 'highpass=f=200, lowpass=f=200' -f flv rtmp://streaming.sanaloyun.net/LiveApp/"+ str(casinoId) + "-" + str(deviceId)+"-Audio"

    BashScript=BashScript + "ffmpeg -ar 48000  -ac 1 -f alsa -i hw:1,0 -acodec aac -ab 128k -f flv rtmp://streaming.sanaloyun.net/LiveApp/"+ str(casinoId) + "-" + str(deviceId)+"-Audio"


    print("CREATE STREAMING!!!")
    textFile="/home/soi/dev/spark-sas2/streaming_hdmiaudio.sh"
    CreateTextFile(textFile,BashScript)
    time.sleep(0.5)
    ExecuteLinuxCommand("sudo chmod +x " + textFile)
    ExecuteLinuxCommand("" + textFile)
    
def CreateStreamingScriptCamera(casinoId, deviceId, cameraIp, configId):
    BashScript=""
    
    BashScript=BashScript + "#!/usr/bin/env bash"
    BashScript=BashScript + "\n"
    
    #BashScript=BashScript + "ffmpeg  -i "+cameraIp+" -c:v h264 -c:a:137 libvorbis -tune zerolatency -f flv rtmp://streaming.sanaloyun.net/LiveApp/"+ str(casinoId) + "-" + str(deviceId)+"-Camera"
    
    if configId==1:
        BashScript=BashScript + "gst-launch-1.0 -e rtspsrc location='"+cameraIp+"' protocols=tcp latency=0 ! rtph264depay ! h264parse ! flvmux name=mux streamable=true ! rtmpsink sync=true async=true location='rtmp://streaming.sanaloyun.net/LiveApp/"+ str(casinoId) + "-" + str(deviceId)+"-Camera' audiotestsrc is-live=true ! audioconvert ! audioresample ! audio/x-raw,rate=48000 ! voaacenc bitrate=96000 ! audio/mpeg ! aacparse ! audio/mpeg, mpegversion=4 ! mux."

    
    if configId==2:
        BashScript=BashScript + "gst-launch-1.0 -e rtspsrc location='"+cameraIp+"' protocols=tcp latency=0 ! rtph264depay ! h264parse ! flvmux name=mux streamable=true ! rtmpsink sync=true async=true location='rtmp://streaming.sanaloyun.net/LiveApp/"+ str(casinoId) + "-" + str(deviceId)+"-Camera' audiotestsrc is-live=true ! audioconvert ! audioresample ! audio/x-raw,rate=48000 ! voaacenc bitrate=96000 ! audio/mpeg ! aacparse ! audio/mpeg, mpegversion=4 ! mux."


    textFile="/home/soi/dev/spark-sas2/streaming_camera.sh"
    CreateTextFile(textFile,BashScript)
    ExecuteLinuxCommand("sudo chmod +x " + textFile)
    ExecuteLinuxCommand("" + textFile)
    
#</Create Bash Scripts for HDMI and Camera>----------------------------------------------------------


G_Config_IsCashoutSoft=0
def SetDeviceConfiguration(deviceTypeId):
    global G_Config_IsCashoutSoft
    if deviceTypeId==10:#APEX
        G_Config_IsCashoutSoft=1
        print("It is set as SOFT!!!***********************************************")





G_IsStreamingInit=0
G_MessageCount=0
G_Machine_OnlineCount=0
G_Machine_DefBetFactor=1
G_Machine_Failed_DeviceId_Zero=0
#MessageType: 0: Init 1: Program acildi, 2: Operation, 3: Online Message Interval
def SQL_DeviceStatu(MessageType):
    global NoNetwork_Count
    try:
        global G_Casino_IsAssetNoAlwaysOne
        global G_Online_IsOnlinePlaying
        global G_IsStreamingInit
        global G_Machine_IsBonusCashable
        global G_Machine_LastBillAcceptorTime
        global G_Device_AssetNo
        global G_Machine_OnlineCount
        global G_Machine_CardReaderPort
        global G_Machine_SASPort
        global G_Machine_DeviceTypeId
        global G_Machine_DeviceTypeGroupId
        global G_Machine_LockBeforeAFT
        global G_Machine_IsRulet
        global IsDeviceLocked
        global IsAvailableForCashoutButton
        global G_CasinoId
        global G_Machine_DeviceId
        global G_Machine_MachineName
        global G_Machine_Mac
        global G_Machine_Currency
        global G_Casino_Name
        global G_Machine_CardReaderType
        global IsCardReaderBusy
        global JackpotWonAmount
        global G_Machine_Failed_DeviceId_Zero
        global G_Machine_ScreenTypeId
        global G_Machine_BillAcceptorTypeId
        global G_Machine_CashInLimit
        global G_Machine_IsPartialTransfer
        global G_Machine_IsRecordAllSAS
        global G_Machine_IsCanPlayWithoutCard
        global G_Machine_IsCashless
        global G_Machine_AdminCards
        global G_Machine_DefBetFactor
        global G_Machine_NotifyWonLimit
        global G_Machine_JackpotId
        global G_Machine_JackpotFactor
        global G_Machine_TicketPrinterTypeId
        global G_Machine_IsBonusGives
        global G_Machine_NoActivityTimeOutForBillAcceptor
        global G_Machine_NoActivityTimeForCashoutMoney
        global G_Machine_NoActivityTimeForCashoutSeconds
        global G_Machine_NewGamingDay
        global G_Machine_WagerBonusFactors
        global G_Machine_AssetNo
        global G_Machine_ScreenRotate
        global G_NetworkLastDate
        global G_Machine_SASVersion
        global G_Machine_PayBackPerc
        global G_Machine_CalcBetByTotalCoinIn
        global G_Machine_GameStartEndNotifications
        global G_Machine_IsAutoNextVisit
        global G_Machine_ProtocolType
        global G_Machine_IsPromoAccepts
        global G_Machine_CurrencyId
        global G_Casino_CurrencyId
        global G_Machine_CurrencyRate
        global G_MessageCount

        
        if G_Machine_DeviceId==0 and MessageType>0 and 2==2:
            G_Machine_Failed_DeviceId_Zero=G_Machine_Failed_DeviceId_Zero+1
            GUI_ShowIfPossibleMainStatu("NO NETWORK! - Device Loop Statu")
            time.sleep(1)
            WarningMsg="%s %s Count: %s" % ("DeviceId cannot be zero!", MessageType, G_Machine_Failed_DeviceId_Zero)
            print(WarningMsg)
            SQL_DeviceStatu(0)
            #SQL_InsImportantMessage(WarningMsg, 0)
            SetMachineStatu(WarningMsg)          
            SQL_DeviceStatu(MessageType)

            print(WarningMsg)
            return


        playcount=0
        totalbet=0
        cardmachinelogid=0
        try:
            playcount=Config.getint("customer","playcount")
            totalbet=Decimal(Config.get("customer","totalbet"))
            cardmachinelogid=Config.getint('customer','cardmachinelogid')
        except Exception as exP:
            print("PlayCount")

        try:
            cardmachinelogid=G_CardMachineLogId
        except Exception as eCardLogId:
            ExceptionHandler("cardmachinelogid",eCardLogId,0)

        
        IPAddress=get_lan_ip()
        customerid=Config.getint('customer','customerid')
        
        IsSASLink=1
        Last_G_SASLastDate_Diff=(datetime.datetime.now()-G_SASLastDate).total_seconds()
        if Last_G_SASLastDate_Diff>=60:
            IsSASLink=0

        IsCardReader_Working=1
        LastCardreaderTimeDiff=(datetime.datetime.now()-G_Machine_LastCardreaderTime).total_seconds()
        if LastCardreaderTimeDiff>60:
            IsCardReader_Working=0

        IsBillAcceptor_Working=1
        LastBillAcceptorTimeDiff=(datetime.datetime.now()-G_Machine_LastBillAcceptorTime).total_seconds()
        if LastBillAcceptorTimeDiff>60 and G_Machine_BillAcceptorTypeId>0:
            IsBillAcceptor_Working=0
            
            
        if G_Device_AssetNo==0 and G_Machine_DeviceId==0 and MessageType==0:
            print("***********************************************************")
            print("<Learn Asset No>-------------------------------------------")
            AssetNoLearnCount=0
            while AssetNoLearnCount<10:
                if G_Device_AssetNo>0:
                    print("Asset No Ogrendik!")
                    break

                AssetNoLearnCount=AssetNoLearnCount+1

                if AssetNoLearnCount%2==0:
                    Wait_Bakiye(11,1,"asset")
                else:
                    Komut_ReadAssetNo()
                time.sleep(0.2)
            print("</Learn Asset No>-------------------------------------------", G_Device_AssetNo)

            if G_Device_AssetNo==0:
                print("Configten al")
                try:
                    G_Device_AssetNo=ReadAssetToInt(Config.get('sas','assetnumber'))
                except Exception as eAssetNo:
                    print("Confg'ten al no alirken sikinti!")

            print("***********************************************************")

            

        if G_Device_AssetNo>0:
            if G_Device_AssetNo==1 and G_Casino_IsAssetNoAlwaysOne==1:
                G_Device_AssetNo=G_Device_AssetNo
                #print("Asset No is always One.. like Salamis")
            else:
                G_Machine_Mac=str(G_Device_AssetNo)



        #print("DeviceStatu", G_Machine_MacAddress, MessageType, IPAddress, G_Static_VersionId, IsSASPortOpened, IsCardReader_Working, G_Machine_SASPort, G_Machine_CardReaderPort, G_Machine_Statu, IsDeviceLocked, G_Machine_DeviceId,playcount, totalbet,cardmachinelogid, GUI_CurrentPage, G_Machine_OnlineCount, IsSASLink, customerid, G_Device_AssetNo)

        # Original MSSQL procedure: tsp_DeviceStatu
        #print("G_DB_Host", G_PG_Host, "G_DB_User", G_PG_User, "G_DB_Database", G_PG_Database)
        result = db_helper.execute_sync_operation(
            'tsp_devicestatu',  # PostgreSQL lowercase name
            [G_Machine_MacAddress, MessageType, IPAddress, G_Static_VersionId, IsSASPortOpened, IsCardReader_Working, G_Machine_SASPort, G_Machine_CardReaderPort, G_Machine_Statu, IsDeviceLocked, G_Machine_DeviceId, playcount, totalbet, cardmachinelogid, GUI_CurrentPage, G_Machine_OnlineCount, IsSASLink, customerid, G_Device_AssetNo, IsBillAcceptor_Working]
        )
        print("result Mehmet", result)
        G_NetworkLastDate = datetime.datetime.now()
        for row in result:

            #print("DB *****************************************************************")

            if MessageType==0:
                IsNewRecord=int(row["IsNewRecord"])
                G_Machine_DeviceId=int(row["DeviceId"])

                print("G_Device_AssetNo", G_Device_AssetNo, "G_Machine_DeviceId", G_Machine_DeviceId, "G_Machine_MacAddress", G_Machine_MacAddress)

                G_Machine_MachineName=row["MachineName"]
                print("G_Machine_MachineName", G_Machine_MachineName)
                Config.set('machine','machinename', G_Machine_MachineName)
                G_Machine_IsBonusGives=int(row["IsBonusGives"])
                G_Machine_DeviceTypeId=int(row["DeviceTypeId"])
                Config.set("machine","devicetypeid", str(G_Machine_DeviceTypeId))
                SetDeviceConfiguration(G_Machine_DeviceTypeId)
                G_Machine_DeviceTypeGroupId=int(row["DeviceTypeGroupId"])


                G_Machine_ScreenTypeId=int(row["ScreenTypeId"])
                G_Machine_BillAcceptorTypeId=int(row["BillAcceptorTypeId"])
                G_Machine_CashInLimit=Decimal(row["CashInLimit"])
                G_Machine_IsPartialTransfer=int(row["IsPartialTransfer"])
                Config.set('machine','screentypeid', str(int(row["ScreenTypeId"])))
                Config.set('machine','billacceptorid', str(int(row["BillAcceptorTypeId"])))
                SaveConfigFile()

                G_Machine_IsRecordAllSAS=int(row["IsRecordAllSAS"])


                try:
                    G_Machine_AssetNo=int(row["AssetNo"])
                    if G_Machine_AssetNo==0:
                        print("********* Asset No is zero")
                except Exception as e:
                    G_Machine_AssetNo=G_Machine_AssetNo

                if G_Machine_AssetNo>0:
                    Config.set('sas','assetnumber', GetAssetBinary(G_Machine_AssetNo))

                if G_Machine_OnlineCount==0:
                    SaveConfigFile()



                try:
                    print("row Mehmet", row)
                    MachineType=int(row["MachineType"])
                except Exception as e:
                    print("Err on MachineType:", e)
                    MachineType=0  # Default value
                
                try:
                    G_Casino_Name=row['CasinoName']
                    #G_Machine_CardReaderType=int(row["CardReaderType"])
                    
                    G_Machine_IsCanPlayWithoutCard=int(row["IsCanPlayWithoutCard"])
                    G_Machine_IsCashless=int(row["IsCashless"])
                    #print("G_Machine_IsCashless", G_Machine_IsCashless, "G_Machine_IsCanPlayWithoutCard",G_Machine_IsCanPlayWithoutCard)

                    G_Machine_ScreenRotate=int(row["ScreenRotate"])

                except Exception as e:
                    print("Err on Casino Settings DeviceStatu")




                try:
                    G_Machine_IsBonusCashable=int(row['IsBonusCashable'])
                except Exception as e:
                    print("Err on Casino Settings DeviceStatu: G_Machine_IsBonusCashable")

                try:
                    G_Machine_Currency=row['CurrencyCode']
                except Exception as e:
                    print("Err on Casino Settings DeviceStatu: G_Machine_Currency")


                try:
                    G_Machine_CurrencyId=int(row["MachineCurrencyId"])
                    G_Casino_CurrencyId=int(row["CurrencyId"])
                except Exception as e:
                    print("CurrencyId")


                try:
                    G_Machine_CurrencyRate=Decimal(row["CurrencyRate"])
                    print("G_Machine_CurrencyRate", G_Machine_CurrencyRate)
                except Exception as e:
                    print("G_Machine_CurrencyRate")

                try:
                    G_Casino_IsAssetNoAlwaysOne=int(row["IsAssetNoAlwaysOne"])
                    print("G_Casino_IsAssetNoAlwaysOne", G_Casino_IsAssetNoAlwaysOne)
                    Config.set('machine','IsAssetNoAlwaysOne', str(int(row["IsAssetNoAlwaysOne"])))
                except Exception as e:
                    print("G_Casino_IsAssetNoAlwaysOne")


                try:
                    G_Machine_JackpotFactor=Decimal(row["JackpotFactor"])
                except Exception as e:
                    print("Err on G_Machine_JackpotFactor")


                

                try:
                    G_Machine_IsPromoAccepts=int(row["IsPromoAccepts"])
                except Exception as e:
                    print("Err on G_Machine_IsPromoAccepts")


                try:
                    G_Machine_ProtocolType=int(row["ProtocolType"])
                except Exception as e:
                    print("Err on G_Machine_ProtocolType")
                

                try:
                    G_Machine_CalcBetByTotalCoinIn=int(row["CalcBetByTotalCoinIn"])
                except Exception as e:
                    print("Err on CalcBetByTotalCoinIn")

                try:
                    G_Machine_GameStartEndNotifications=int(row["GameStartEndNotifications"])
                except Exception as e:
                    print("Err on GameStartEndNotifications")

                try:
                    G_Machine_IsAutoNextVisit=int(row["IsAutoNextVisit"])
                except Exception as e:
                    print("Err on IsAutoNextVisit")



                try:
                    G_Machine_SASVersion=row["SASVersion"]
                except Exception as e:
                    print("Err on G_Machine_SASVersion")

                try:
                    G_Machine_PayBackPerc=Decimal(row["PayBackPerc"])
                except Exception as e:
                    print("Err on G_Machine_PayBackPerc")

                try:
                    G_Machine_WagerBonusFactors=[]
                    WagerBonusFactors=row['WagerBonusFactors']
                    indexno=0
                    for rowWager in WagerBonusFactors.split('|'):
                        if len(rowWager)==0:
                            break
                        if len(rowWager)>0:
                            indexno=indexno+1
                            portDict =	{
                                "index": indexno,
                                "wagername": rowWager.split('~')[0],
                                "wager": Decimal(rowWager.split('~')[1]),
                                "bonusfactor": Decimal(rowWager.split('~')[2]),
                                "htmlcolour": rowWager.split('~')[3],
                                "wagernext": Decimal(rowWager.split('~')[4]),
                                "startpercentage": Decimal(rowWager.split('~')[5]),
                                "nextpercentage": Decimal(rowWager.split('~')[6]),
                                }
                            G_Machine_WagerBonusFactors.append(portDict)
                except Exception as e:
                    print("Err on G_Machine_WagerBonusFactors")

                try:
                    G_CasinoId=int(row["CasinoId"])
                    Config.set('casino','casinoid', str(G_CasinoId))
                    Config.set('casino','casinoname', str(row['CasinoName']))
                    Config.set('casino','minstorebootnonetwork', str(row['MinsToRebootNoNetwork']))
                except Exception as e:
                    print("Err on G_CasinoId")

                try:
                    G_Machine_AdminCards=row['AdminCards']+"|"
                    Config.set('machine','admincards', G_Machine_AdminCards)
                except Exception as e:
                    print("Err on AdminCards")

                try:
                    G_Machine_TicketPrinterTypeId=int(row["TicketPrinterTypeId"])
                    Config.set('machine','ticketprintertypeid', str(G_Machine_TicketPrinterTypeId))
                except Exception as e:
                    print("Err on ticketprintertypeid")



                try:
                    G_Machine_DefBetFactor=int(row["DefBetFactor"])
                except Exception as e:
                    print("Err on G_Machine_DefBetFactor")



                try:
                    G_Machine_NotifyWonLimit=Decimal(row['NotifyWonSlot'])
                    if MachineType==1:
                        G_Machine_NotifyWonLimit=Decimal(row['NotifyWonRoulette'])
                        G_Machine_IsRulet=1
                except Exception as e:
                    G_Machine_NotifyWonLimit=G_Machine_NotifyWonLimit


                try:
                    G_Machine_JackpotId=int(row["JackpotId"])
                    G_Machine_JackpotFactor=Decimal(row['JackpotFactor'])
                except Exception as e:
                    print("Err on G_Machine_JackpotId")

                try:
                    G_Machine_NoActivityTimeOutForBillAcceptor=int(row["NoActivityTimeOutForBillAcceptor"])
                    G_Machine_NoActivityTimeForCashoutMoney=int(row["NoActivityTimeForCashoutMoney"])
                    G_Machine_NoActivityTimeForCashoutSeconds=int(row["NoActivityTimeForCashoutSeconds"])
                    if G_Machine_IsRulet==1:
                        G_Machine_NoActivityTimeOutForBillAcceptor=G_Machine_NoActivityTimeOutForBillAcceptor*3

                except Exception as e:
                    print("Err on NoActivityTimeOut")


                if G_Machine_OnlineCount==0:
                    PrintAndSetAsStatuText("Device started!")
                    SetMachineStatu("Device started!")

                if G_Machine_OnlineCount==0 and G_IsStreamingInit==0:
                    #Yelena 2021-09-20
                    try:
                        print("<Streaming>---------------------------------------------------")
                        result = SQL_GetDeviceAdditionalInfo(G_Machine_DeviceId)
                        for rowOnline in result:
                            G_Online_StreamId=rowOnline["StreamId"]
                            G_Online_CamStreamId=rowOnline["CamStreamId"]
                            G_Online_IPCameraURL=rowOnline["IPCameraURL"]

                            #1: EGT Tek Screen
                            G_Online_ButtonConfigId=int(rowOnline["ButtonConfigId"])

                            G_Online_ResolutionX=rowOnline["ResolutionX"]
                            G_Online_ResolutionY=rowOnline["ResolutionY"]
                            G_Online_IsOnlinePlaying=int(rowOnline["IsOnlinePlaying"])
                            try:
                                if G_Online_IsOnlinePlaying==1 and G_IsStreamingInit==0:
                                    G_IsStreamingInit=1
                                    print("<CreateStreamingScript>---------------------------------------------------")
                                    
                                    #threadStreaming = Thread(target = CreateStreamingScriptHDMI, args = (G_CasinoId,G_Machine_DeviceId,G_Online_ButtonConfigId, ))
                                    #threadStreaming.name="StreamingHDMI"
                                    #threadStreaming.start()

                                    #threadStreaming = Thread(target = CreateStreamingScriptHDMIAudio, args = (G_CasinoId,G_Machine_DeviceId,G_Online_ButtonConfigId, ))
                                    #threadStreaming.name="StreamingAudio"
                                    #threadStreaming.start()
                                    
                                    #threadStreaming = Thread(target = CreateStreamingScriptCamera, args = (G_CasinoId,G_Machine_DeviceId,G_Online_IPCameraURL, G_Online_ButtonConfigId, ))
                                    #threadStreaming.name="StreamingCamera"
                                    #threadStreaming.start()
                                    

                                    print("</CreateStreamingScript>---------------------------------------------------")
                            except Exception as eOnline1:
                                print("Streaming Init Failed at x145")

                        print("</Streaming>---------------------------------------------------")
                    except Exception as eOnline:
                        print("Is OnlinePlaying Err!")



                G_Machine_OnlineCount=G_Machine_OnlineCount+1


                # Handle missing IsLocked field from database
                try:
                    IsDeviceLocked=int(row["IsLocked"])
                except KeyError:
                    # Default to unlocked if field is missing
                    IsDeviceLocked=0
                    print("Warning: IsLocked field missing from database result, defaulting to 0 (unlocked)")
                if IsNewRecord==1:
                    print("New device")
                    GetMeter(0,"new")
                    time.sleep(0.2)
                    GetMeter(1,"new")
                    Komut_ReadAssetNo()

                if G_Machine_OnlineCount==1:
                    SaveConfigFile()

            #<endif MessageType==0>

            if MessageType>0:
                RowType=row['RowType']
                if RowType=="oldgamingdate":
                    G_Machine_NewGamingDay=1
                    Config.set('machine','newgamingday', "1")
                    SaveConfigFile()
                    GUI_ShowIfPossibleMainStatu("Waiting for new gaming date Statu!")
                    if IsCardInside==0:
                        CardReader_WaitingNewDay()


                if RowType=="messagecount" and IsGUIEnabled==1 and IsCardInside==1:
                    TextValue=int(row['TextValue'])
                    ReceivedMessageCount=row['TextInfo']
                    
                    
                    if TextValue!=G_MessageCount:
                        G_MessageCount=TextValue
                        ExecuteJSFunction2("ShowHideMessageCountBox",str(TextValue), ReceivedMessageCount)

                if RowType=="jackpotinfo" and IsGUIEnabled==1 and IsCardInside==1:
                    try:
                        RowNo=int(row['RowNo'])
                        LevelName=row['TextInfo']
                        if G_Machine_ScreenTypeId>0:
                            LevelName=LevelName.rjust(10)

                        Money=Decimal(row['TextValue'])
                        
                        if IsGUI_Type==1:
                            ChangeJackpotLevelText(RowNo,"%s" % (LevelName))
                            ChangeJackpotLevelValue(RowNo,"%s %s" % (Money, G_Machine_Currency))

                        if IsGUI_Type==2:
                            ChangeJackpotLevelTextValue(RowNo,"%s %s %s" % (LevelName, Money, G_Machine_Currency))

                        if IsGUI_Type==3 or IsGUI_Type==4:
                            ChangeJackpotLevelValue(RowNo,"%s %s" % (Money, G_Machine_Currency))


                    except Exception as eJ:
                        ExceptionHandler("SQL_DeviceStatu Jackpot",eJ,0)


                if RowType=="prize":
                    try:
                        PrizeDescription=row['TextInfo']
                        Money=Decimal(row['TextValue'])
                        
                        if 1==1:
                            #kart cikartmaya izin vermemek icin IsCardReaderBusy yapacagiz...
                            IsCardReaderBusy=1
                            time.sleep(1)
                            Wait_Bakiye(4,0,"prize")
                            time.sleep(0.1)
                            JackpotWonAmount=Money
                            BlinkCustomerScreenLine(2, 3, "Prize: %s %s %s" % (PrizeDescription, JackpotWonAmount, G_Machine_Currency), 20)
                            ShowNotifyScreen("Congratulations!","Prize %s! %s %s" % (PrizeDescription, JackpotWonAmount, G_Machine_Currency),20)
                        
                            print("Prize %s! %s %s" % (PrizeDescription, JackpotWonAmount, G_Machine_Currency))
                            SQL_InsImportantMessageByWarningType("Prize %s! %s %s" % (PrizeDescription, JackpotWonAmount, G_Machine_Currency),20,21)

                            Wait_Bakiye(0,1,"prize2")
                            Wait_ParaYukle(10)
                            GetMeter(0,"prize")
                            time.sleep(0.1)
                            Wait_Bakiye(0,1,"prize2")
                            IsCardReaderBusy=0#prize icin

                    except Exception as eJ:
                        ExceptionHandler("SQL_DeviceStatu Prize",eJ,0)

                    IsCardReaderBusy=0#prize icin yine de burada saglama olsun


                if RowType=="cmd":
                    Command=row['Command']
                    print("Command",Command)
                    try:
                        ExecuteCommand(Command)
                    except Exception as eCommand:
                        print("Command Err:" + Command)



        NoNetwork_Count=0
        if GUI_LastMainStatuMessage==ErrorMessage_NoNetwork:
            GUI_ShowIfPossibleMainStatu("Connected to network")

        conn.close()
    except Exception as e:
        NoNetwork_Count=NoNetwork_Count+1
        GUI_ShowIfPossibleMainStatu(ErrorMessage_NoNetwork)
        print("NoNetwork_Count", NoNetwork_Count)
        if NoNetwork_Count>30:
            NoNetworkDiff=(datetime.datetime.now()-G_NetworkLastDate).total_seconds()

            GUI_ShowIfPossibleMainStatu("No network restart!")
            ExecuteCommand("restart")

        print("SQL: DeviceStatu exception NoNetwork_Count", NoNetwork_Count)
        print("****************************")
        print("G_Machine_Mac, " , G_Machine_Mac)
        print("MessageType, " , MessageType)
        print("G_Static_VersionId, " , G_Static_VersionId)
        print("IsSASPortOpened, " , IsSASPortOpened)
        print("IsCardReaderOpened, " , IsCardReaderOpened)
        print("G_Machine_SASPort, " , G_Machine_SASPort)
        print("G_Machine_CardReaderPort, " , G_Machine_CardReaderPort)
        print("G_Machine_Statu, " , G_Machine_Statu)
        print("IsDeviceLocked, " , IsDeviceLocked)
        print("G_Machine_DeviceId, " , G_Machine_DeviceId)
        print("playcount, " , playcount)
        print("totalbet, " , totalbet)
        print("cardmachinelogid, " , cardmachinelogid)
        print("GUI_CurrentPage, " , GUI_CurrentPage)
        print("****************************")
        ExceptionHandler("SQL_DeviceStatu",e,1)




def SQL_InsDeviceMoneyQuery(CashableAmount,RestrictedAmount,NonrestrictedAmount,Message):
    # Original MSSQL procedure: tsp_InsDeviceMoneyQuery
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    cardmachinelogid = 0
    cardmachinelogid = Config.getint('customer', 'cardmachinelogid')

    try:
        cardmachinelogid = G_CardMachineLogId
    except Exception as eCardLogId:
        ExceptionHandler("cardmachinelogid", eCardLogId, 0)

    try:
        db_helper.queue_database_operation(
            'tsp_InsDeviceMoneyQuery',
            [G_Machine_Mac, G_User_CardNo, cardmachinelogid, CashableAmount, RestrictedAmount, NonrestrictedAmount, Message, G_Machine_DeviceId],
            'insert_device_money_query'
        )
    except Exception as e:
        ExceptionHandler("SQL_InsDeviceMoneyQuery", e, 1)



def SQL_InsDeviceDebug(message):
    # Original MSSQL procedure: tsp_InsDeviceDebug
    cardmachinelogid = 0
    cardmachinelogid = Config.getint('customer', 'cardmachinelogid')

    try:
        cardmachinelogid = G_CardMachineLogId
    except Exception as eCardLogId:
        ExceptionHandler("cardmachinelogid", eCardLogId, 0)

    try:
        db_helper.execute_database_operation(
            'tsp_insdevicedebug',  # PostgreSQL lowercase name
            [cardmachinelogid, G_Machine_DeviceId, message]
        )
    except Exception as e:
        ExceptionHandler("SQL_InsDeviceDebug", e, 1)

def SQL_InsDeviceMeter(GameNumber, TotalCoinIn, TotalCoinOut,TotalJackpot ,GamesPlayed, TotalHandPaidCredit, TotalCreditsBillsAccepted, CurrentCredits_0C,TurnOver, TurnOut, NonCashableIn, NonCashableOut, TotalBonus, GamesWon, GamesLost):
    cardmachinelogid=0
    
    try:
        cardmachinelogid=Config.getint('customer','cardmachinelogid')
        print("G_CardMachineLogId", G_CardMachineLogId)
    except Exception as e:
        print("Meter CardMachineLogId")

    try:
        cardmachinelogid=G_CardMachineLogId
    except Exception as eCardLogId:
        ExceptionHandler("cardmachinelogid",eCardLogId,0)

    # Original MSSQL procedure: tsp_InsDeviceMeter
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    try:
        db_helper.queue_database_operation(
            'tsp_InsDeviceMeter',
            [G_Machine_Mac, GameNumber, TotalCoinIn, TotalCoinOut, TotalJackpot, GamesPlayed, TotalHandPaidCredit, TotalCreditsBillsAccepted, CurrentCredits_0C, G_Machine_DeviceId, 0, TurnOver, TurnOut, NonCashableIn, NonCashableOut, TotalBonus, cardmachinelogid, GamesWon, GamesLost],
            'insert_device_meter'
        )
    except Exception as e:
        ExceptionHandler("SQL_InsDeviceMeter", e, 1)


def SQL_InsDeviceMeter2(TotalCancelledCredits_04, GamesPlayed_05, GamesWon_06, CurrentCredits_0C, WeightedAverage_7F, RegularCashableKeyed_FA, RestrictedKeyed_FB, NonrestrictedKeyed_FC, TotalMachinePaidProgressive_1D):
    cardmachinelogid=0
    
    try:
        cardmachinelogid=Config.getint('customer','cardmachinelogid')
        print("G_CardMachineLogId", G_CardMachineLogId)
    except Exception as e:
        print("Meter CardMachineLogId")

    try:
        cardmachinelogid=G_CardMachineLogId
    except Exception as eCardLogId:
        ExceptionHandler("cardmachinelogid",eCardLogId,0)

    # Original MSSQL procedure: tsp_InsDeviceMeter2
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    try:
        db_helper.queue_database_operation(
            'tsp_InsDeviceMeter2',
            [G_Machine_Mac, G_Machine_DeviceId, cardmachinelogid, TotalCancelledCredits_04, GamesPlayed_05, GamesWon_06, CurrentCredits_0C, WeightedAverage_7F, RegularCashableKeyed_FA, RestrictedKeyed_FB, NonrestrictedKeyed_FC, TotalMachinePaidProgressive_1D],
            'insert_device_meter2'
        )
    except Exception as e:
        ExceptionHandler("tsp_InsDeviceMeter2", e, 1)

def SQL_InsDeviceMeterAll(GameNumber, ReceivedMessage):
    # Original MSSQL procedure: tsp_InsDeviceMeterAll
    # Note: This procedure was not found in postgres-routines-in-sas.sql
    # Using hybrid approach - queue operation instead of direct call
    try:
        db_helper.queue_database_operation(
            'tsp_InsDeviceMeterAll',
            [G_Machine_Mac, GameNumber, ReceivedMessage],
            'insert_device_meter_all'
        )
    except Exception as e:
        ExceptionHandler("SQL_InsDeviceMeterAll", e, 1)

def SQL_InsException(MethodName, ErrorMessage):
    # Original MSSQL procedure: tsp_InsException
    try:
        IPAddress = get_lan_ip()
        db_helper.execute_database_operation(
            'tsp_insexception',  # PostgreSQL lowercase name
            [G_Machine_Mac, MethodName, ErrorMessage]
        )
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("Yapilacak birsey yok.", MethodName, exc_type, fname, exc_tb.tb_lineno)




GameStart_IsWaitingGameEnd=0
GameStart_Wagered=Decimal(0)
GameStart_TotalCoinIn=Decimal(0)
GameStart_WagerType=""
GameStart_ProgressiveGroup=0
GameStart_GamePromo=Decimal(0)
GameStart_TotalPlayCount=0
GameStart_TotalCoinInMeter=Decimal(0)

JackpotWonAmount=0
GameStartId=0
def SQL_InsGameStart(Wagered, WonAmount, TotalCoinIn,WagerType,ProgressiveGroup,GamePromo, TotalPlayCount, TotalCoinInMeter):
    try:
        global IsCardReaderBusy
        global GameStartId
        global JackpotWonAmount
        global GameStart_IsWaitingGameEnd

        if GameStart_IsWaitingGameEnd==1:
            SQL_InsGameStartEnd(0)


        GameStart_IsWaitingGameEnd=1

        cardmachinelogid=0
        cardmachinelogid=Config.getint('customer','cardmachinelogid')
        
        global GameStart_Wagered
        global GameStart_TotalCoinIn
        global GameStart_WagerType
        global GameStart_ProgressiveGroup
        global GameStart_GamePromo
        global GameStart_TotalPlayCount
        global GameStart_TotalCoinInMeter

        GameStart_Wagered=Wagered
        GameStart_TotalCoinIn=TotalCoinIn
        GameStart_WagerType=WagerType
        GameStart_ProgressiveGroup=ProgressiveGroup
        GameStart_GamePromo=GamePromo
        GameStart_TotalPlayCount=TotalPlayCount
        GameStart_TotalCoinInMeter=TotalCoinInMeter


        return

        try:
            cardmachinelogid=G_CardMachineLogId
        except Exception as eCardLogId:
            ExceptionHandler("cardmachinelogid",eCardLogId,0)

        gender=Config.getint('customer','gender')
        customerid=Config.getint('customer','customerid')
        
        #kontrolet: gamestart

        # Original MSSQL procedure: tsp_InsGameStart
        result = db_helper.execute_database_operation(
            'tsp_insgamestart',  # PostgreSQL lowercase name
            [G_Machine_Mac, cardmachinelogid, Wagered, WonAmount, TotalCoinIn, WagerType, ProgressiveGroup, G_SelectedGameId, GamePromo, G_Machine_DeviceId, TotalPlayCount, gender, customerid, G_Machine_DeviceTypeGroupId, TotalCoinInMeter]
        )
        for row in result:
            GameStartId = int(row['Result'])
    except Exception as e:
        ExceptionHandler("SQL_InsGameStart",e,1)

def SQL_InsGameEnd(WinAmount):

    try:
        return

        cardmachinelogid=0
        cardmachinelogid=Config.getint('customer','cardmachinelogid')

        try:
            cardmachinelogid=G_CardMachineLogId
        except Exception as eCardLogId:
            ExceptionHandler("cardmachinelogid",eCardLogId,0)

        currentmoney=G_Machine_Balance
        try:
            currentmoney=Decimal(G_Machine_Balance)+Decimal(G_Machine_Promo)
        except Exception as ex1:
            print("......")



        # Original MSSQL procedure: tsp_InsGameEnd
        result = db_helper.execute_database_operation(
            'tsp_insgameend',  # PostgreSQL lowercase name
            [G_Machine_Mac, cardmachinelogid, WinAmount, G_SelectedGameId, GameStartId, currentmoney, G_Machine_DeviceId, G_Machine_Promo, G_Wagered, G_Machine_NotifyWonLimit]
        )

        for row in result:
           JWId = int(row['JWId'])
           #if JWId>0:
           #    BlinkCustomerScreenLine(2, 3, "%s Jackpot! %s %s" % (row['LevelName'], row['WonAmount'], G_Machine_Currency), 20)
    except Exception as e:
        ExceptionHandler("SQL_InsGameEnd",e,1)


def SQL_InsGameStartEnd(WinAmount):

    try:
        global JackpotWonAmount
        global IsCardReaderBusy
        global GameStartId
        global GameStart_IsWaitingGameEnd
        GameStart_IsWaitingGameEnd=0


        cardmachinelogid=0
        cardmachinelogid=Config.getint('customer','cardmachinelogid')

        try:
            cardmachinelogid=G_CardMachineLogId
        except Exception as eCardLogId:
            ExceptionHandler("cardmachinelogid",eCardLogId,0)

        currentmoney=G_Machine_Balance
        try:
            currentmoney=Decimal(G_Machine_Balance)+Decimal(G_Machine_Promo)
        except Exception as ex1:
            print("......")


        gender=Config.getint('customer','gender')
        customerid=Config.getint('customer','customerid')

        if GameStart_TotalPlayCount==1:
            if G_User_CardType==2:
                JackpotWonAmount=20000
                print("JackpotWonAmount", JackpotWonAmount)
                Wait_ParaYukle(10)

        # Original MSSQL procedure: tsp_InsGameStartEnd
        if G_Machine_CurrencyRate == 1:
            result = db_helper.execute_database_operation(
                'tsp_insgamestartend',  # PostgreSQL lowercase name
                [G_Machine_Mac, cardmachinelogid, GameStart_Wagered, GameStart_TotalCoinIn, GameStart_WagerType, GameStart_ProgressiveGroup, G_SelectedGameId, GameStart_GamePromo, G_Machine_DeviceId, GameStart_TotalPlayCount, gender, customerid, G_Machine_DeviceTypeGroupId, GameStart_TotalCoinInMeter, WinAmount, GameStartId, currentmoney, G_Machine_Promo, G_Machine_NotifyWonLimit, G_Machine_JackpotId, G_Machine_JackpotFactor, G_Machine_CurrencyId, G_Casino_CurrencyId]
            )
        else:
            result = db_helper.execute_database_operation(
                'tsp_insgamestartend',  # PostgreSQL lowercase name
                [G_Machine_Mac, cardmachinelogid, GameStart_Wagered, GameStart_TotalCoinIn, GameStart_WagerType, GameStart_ProgressiveGroup, G_SelectedGameId, GameStart_GamePromo, G_Machine_DeviceId, GameStart_TotalPlayCount, gender, customerid, G_Machine_DeviceTypeGroupId, GameStart_TotalCoinInMeter, WinAmount, GameStartId, currentmoney, G_Machine_Promo, G_Machine_NotifyWonLimit, G_Machine_JackpotId, G_Machine_JackpotFactor, G_Machine_CurrencyId, G_Casino_CurrencyId, G_Machine_CurrencyRate]
            )

        for row in result:
            GameStartId=int(row['Result'])
            JWId=int(row['JWId'])
            if JWId>0:
                IsLockNeeded=int(row['IsLockNeeded'])
                
                print("<Jackpot>**************************************************************************************")
                IsCardReaderBusy=1#Jackpot
                
                time.sleep(2)
                Wait_Bakiye(4,0,"jackpot1")
                time.sleep(0.1)
                JackpotWonAmount=Decimal(row['WonAmountLocal'])
                BlinkCustomerScreenLine(2, 3, "%s Jackpot! %s %s" % (row['LevelName'], row['WonAmountLocal'], G_Machine_Currency), 20)
                
                ShowNotifyScreen("Congratulations!","%s Jackpot! %s %s" % (row['LevelName'], row['WonAmountLocal'], G_Machine_Currency),20)
                
                print("%s Jackpot! %s %s" % (row['LevelName'], row['WonAmountLocal'], G_Machine_Currency))
                SQL_InsImportantMessageByWarningType("%s Jackpot! %s %s" % (row['LevelName'], row['WonAmountLocal'], G_Machine_Currency),20,21)
                
                if IsLockNeeded==0:
                    Wait_ParaYukle(10) #10 ile deneyelim bi. Sonuc: 
                    
                if IsLockNeeded==1:
                    Wait_ParaYukle(11)
                    #SQL_UploadMoney(JackpotWonAmount,3) buna gerek yok artik. silip yazilacak....

                GetMeter(0,"jackpot1.1")
                time.sleep(0.1)
                Wait_Bakiye(0,1,"jackpot2")
                IsCardReaderBusy=0#jackpot icin
                Komut_CancelBalanceLock()
                #EnableDisableAutoPlay(1)
                print("</Jackpot>**************************************************************************************")
    except Exception as e:
        ExceptionHandler("tsp_InsGameStartEnd", e, 1)


#Type: 1 Remote Handpay, 2 Money existed, 3: Jackpot, 4: Handpay Slip, 5# Slip
def SQL_UploadMoney(Amount,Type):
    try:
        cardmachinelogid=0
        cardmachinelogid=Config.getint('customer','cardmachinelogid')

        try:
            cardmachinelogid=G_CardMachineLogId
        except Exception as eCardLogId:
            ExceptionHandler("cardmachinelogid",eCardLogId,0)

        # Original MSSQL procedure: tsp_InsMoneyUpload
        # Note: This procedure was not found in postgres-routines-in-sas.sql
        # Using hybrid approach - queue operation instead of direct call
        db_helper.queue_database_operation(
            'tsp_InsMoneyUpload',
            [G_Machine_Mac, cardmachinelogid, G_SelectedGameId, GameStartId, Amount, Type],
            'insert_money_upload'
        )
    except Exception as e:
        ExceptionHandler("SQL_UploadMoney",e,1)

def SQL_InsImportantMessage(Message,MessageType):
    try:
        customerid=Config.getint('customer','customerid')
        # Use async messaging for important messages - no immediate response needed
        # Include SAS context for better debugging
        sas_context = get_current_sas_context()
        db_helper.execute_database_operation('tsp_InsImportantMessage', 
            (G_Machine_Mac, Message, MessageType, 0, customerid), sas_context)
    except Exception as e:
        print("Message: " , Message)
        ExceptionHandler("SQL_InsImportantMessage",e,1)


def SQL_InsTraceLog(LogType, Direction, Message, RowId):
    # Original MSSQL procedure: tsp_InsTraceLog
    try:
        db_helper.execute_database_operation(
            'tsp_instracelog',  # PostgreSQL lowercase name
            [G_Machine_Mac, LogType, Direction, Message, RowId]
        )
    except Exception as e:
        print("Message: ", Message)

Trace_LogId=0
def SQL_Safe_InsTraceLog(LogType, Direction, Message):
    if Message=="01FF001CA5" or Message=="FF001CA5":
        return

    global Trace_LogId
    Trace_LogId=Trace_LogId+1
    try:
        processGameoperation = Thread(target=SQL_InsTraceLog, args=(LogType, Direction, Message, Trace_LogId))
        processGameoperation.name="SQL_InsTraceLog"+ str(Trace_LogId)
        processGameoperation.start()
    except Exception as e:
        print("Err on SQL_Safe_InsImportantMessage")


#MessageType en son 103
def SQL_Safe_InsImportantMessage(Message,MessageType):
    #2020-06-20
    try:
        processGameoperation = Thread(target=SQL_InsImportantMessage, args=(Message,MessageType ,))
        processGameoperation.name="SafeImportantMsg"
        processGameoperation.start()
    except Exception as e:
        print("Err on SQL_Safe_InsImportantMessage")


def SQL_Safe_InsImportantMessageByWarningType(Message,MessageType, WarningType):
    try:
        processGameoperation = Thread(target=SQL_InsImportantMessageByWarningType, args=(Message,MessageType, WarningType ,))
        processGameoperation.name="SafeImportantWarning"
        processGameoperation.start()
    except Exception as e:
        print("Err on SQL_Safe_InsImportantMessage")

def SQL_InsImportantMessageByWarningType(Message,MessageType, WarningType):
    try:
        customerid=Config.getint('customer','customerid')
        # Use async messaging for important messages with warning type
        # Include SAS context for better debugging
        sas_context = get_current_sas_context()
        db_helper.execute_database_operation('tsp_InsImportantMessage', 
            (G_Machine_Mac, Message, MessageType, WarningType, customerid), sas_context)
    except Exception as e:
        print("Message: " , Message)
        ExceptionHandler("SQL_InsImportantMessage",e,1)


def SQL_InsReceivedMessage(ReceivedMessage, IsProcessed, AnswerCommandName):
    # Original MSSQL procedure: tsp_InsReceivedMessage
    try:
        if len(ReceivedMessage) > 500:
            return

        db_helper.execute_database_operation(
            'tsp_insreceivedmessage',  # PostgreSQL lowercase name
            [G_Machine_Mac, ReceivedMessage, IsProcessed, AnswerCommandName]
        )
    except Exception as e:
        print("ReceivedMessage: ", ReceivedMessage)
        ExceptionHandler("SQL_InsReceivedMessage", e, 1)


def SQL_Safe_InsSentCommands(CommandName, Command):
    processGameoperation = Thread(target=SQL_InsSentCommands, args=(CommandName, Command,))
    processGameoperation.name="SafeInsCmd"
    processGameoperation.start()

def SQL_InsSentCommands(CommandName, Command):
    try:

        cardmachinelogid=0
        cardmachinelogid=Config.getint('customer','cardmachinelogid')

        try:
            cardmachinelogid=G_CardMachineLogId
        except Exception as eCardLogId:
            ExceptionHandler("cardmachinelogid",eCardLogId,0)

        # Original MSSQL procedure: tsp_InsSentCommands
        db_helper.execute_database_operation(
            'tsp_inssentcommands',  # PostgreSQL lowercase name
            [G_Machine_Mac, cardmachinelogid, CommandName, Command]
        )
    except Exception as e:
        ExceptionHandler("SQL_InsSentCommands",e,1)


def TmrSASPooling():
    try:
        global IsSasPooling
        if IsSasPooling==1:
            DoSASPoolingMsg(0)
    except Exception as e:
        print("...")



def Wait_RemoteHandpay():

    Ac("remotehandpay")
    global IsWaitingForHandpayReset
    global IsHandpayOK
    IsWaitingForHandpayReset=1
    IsHandpayOK=0


    SayKomutBekliyor=0
    Komut_RemoteHandpay()
    while (IsWaitingForHandpayReset==1):
        PrintAndSetAsStatuText('Waiting for remote handpay')
        time.sleep(G_Static_SasWait)
        SayKomutBekliyor=SayKomutBekliyor+1
        if SayKomutBekliyor%10==0 and IsWaitingForHandpayReset==1:
            Komut_RemoteHandpay()

        if SayKomutBekliyor>10:
            PrintAndSetAsStatuText("Unable for remote handpay")
            SetMachineStatu("Unable to remotehandpay...")
            SQL_InsException("RemoteHandpay","Unable to remote handpay")
            return
            break

    
    if IsWaitingForHandpayReset==0:
        PrintAndSetAsStatuText("Remote Handpay is ok!")

    GetMeter(0,"remotehandpay")





def Komut_EFT_RequestCashoutAmount():
    print("Komut_EFT_RequestCashoutAmount")
    SAS_SendCommand("EFT_RequestCashoutAmount", "016600596B" ,0)

def Komut_EFT_RequestTransferLog():
    print("Transfer log")
    SAS_SendCommand("EFT_RequestTransferLog", "0128" ,0)
    

def Komut_RegisterAssetNo(): 
    print("Register Asset")
    SAS_SendCommand("RegisterAsset", GetCRC("01731D00"+Config.get("sas","assetnumber")+"000000000000000000000000000000000000000000000000"),0) #init register
    

def Komut_RegisterAssetNo2(): 
    print("Register Asset")
    SAS_SendCommand("RegisterAsset", GetCRC("01731D01"+Config.get("sas","assetnumber")+"000000000000000000000000000000000000000000000000"),0) #init register
    

def Komut_ReadAssetNo():
    print("Read Asset")
    #SAS_SendCommand("ReadAssetNo",GetCRC("01731DFF"+Config.get("sas","assetnumber")+"000000000000000000000000000000000000000000000000"),0) #Read Asset number
    SAS_SendCommand("RegisterAsset", "017301FFA765",0) #init register

def Komut_RemoteHandpay():
    GenelKomut=GetCRC("01A801")
    SAS_SendCommand("A8-HandPay2Credit",GenelKomut,1)

    GenelKomut=GetCRC("0194")
    print("REMOTE HAND PAY", len(GenelKomut), GenelKomut)
    SAS_SendCommand("handpay",GenelKomut,1)

    
G_BillAcceptorDisabled=datetime.datetime.now()
def Komut_DisableBillAcceptor(sender):
    global IsBillacceptorOpen
    global G_BillAcceptorDisabled
    IsBillacceptorOpen=0

    print("Komut_DisableBillAcceptor", sender)
    Diff=(datetime.datetime.now()-G_BillAcceptorDisabled).total_seconds()
    G_BillAcceptorDisabled=datetime.datetime.now()

    if sender!="Bill acceptor kapat tmr" and sender!="nosas" and Diff>2:
        SQL_Safe_InsImportantMessage("Billacceptor is disabled (" + sender +")" ,102)

    if G_Machine_IsCashless==0:
        return


    #print("Disable bill acceptor!", sender)
    if G_Machine_BillAcceptorTypeId==0:
        SAS_SendCommand("DisableBillAcceptor","0107676D",0)

    if G_Machine_BillAcceptorTypeId>0:
        BillAcceptor_Inhibit_Close()
    #GUI_ShowIfPossibleMainStatu("Disable bill acceptor")

def Komut_EnableBillAcceptor():
    global IsBillacceptorOpen
    IsBillacceptorOpen=1

    if G_Session_IsByOnline==1:
        return

    SQL_Safe_InsImportantMessage("Billacceptor is enabled",103)

    if G_Machine_BillAcceptorTypeId==0:
        SAS_SendCommand("EnableBillAcceptor","0106EE7C",0)

    if G_Machine_BillAcceptorTypeId>0:
        BillAcceptor_Inhibit_Open()
    #GUI_ShowIfPossibleMainStatu("Enable bill acceptor")

def EnableDisableAutoPlay(isenabled):
    if isenabled==1:
        SAS_SendCommand("EnableAutoPlay",GetCRC("01AA01"),0)
    else:
        SAS_SendCommand("DisableAutoPlay",GetCRC("01AA00"),0)

def DelayPlay():
    #SAS_SendCommand("DelayPlay","012E9000C616",0)
    #SAS_SendCommand("DisableAutoPlay",GetCRC("012E1000"),0)
    #SAS_SendCommand("DisableAutoPlay",GetCRC("012E2000"),0)
    SAS_SendCommand("DisableAutoPlay",GetCRC("012E9000"),0)

def UnDelayPlay():
    SAS_SendCommand("UnDelayPlay","012E00009B0F",0)



def Komut_ParaYukleEFT(doincreasetransactionid, amount):
    global IsWaitingForParaYukle

    transactionid=Config.getint("payment","transactionid")
    if transactionid==250:
        transactionid=0

    if doincreasetransactionid==1:
        transactionid=transactionid+1
        Config.set("payment","transactionid",str(transactionid))
        SaveConfigFile()


    CommandHeader=Config.get("sas","address")      #1-Address  01
    CommandHeader+="69"   #1-Command 

    Command=""
    TRANSACTIONID=hex(transactionid)[2:].upper()
    if len(TRANSACTIONID)==1:
        TRANSACTIONID="0" + TRANSACTIONID

    Command+=TRANSACTIONID   #1-TransactionId Length        03

    Command+="00"   #00

    customerbalanceint=int(amount*100);
    Command+=AddLeftBCD(customerbalanceint,4)

    GenelKomut="%s%s" % (CommandHeader, Command)


    #<CRC Hesapla>
    GenelKomut=GetCRC(GenelKomut)
    #</CRC Hesapla>
    #
    SAS_SendCommand("ParaYukle",GenelKomut,1)




def Komut_ParaSilEFT(doincreasetransactionid, amount):
    global IsWaitingForParaYukle

    transactionid=Config.getint("payment","transactionid")
    if transactionid==250:
        transactionid=0

    if doincreasetransactionid==1:
        transactionid=transactionid+1
        Config.set("payment","transactionid",str(transactionid))
        SaveConfigFile()
    transactionid=13

    CommandHeader=Config.get("sas","address")      #1-Address  01
    CommandHeader+="64"   #1-Command 

    Command=""
    TRANSACTIONID=hex(transactionid)[2:].upper()
    if len(TRANSACTIONID)==1:
        TRANSACTIONID="0" + TRANSACTIONID

    Command+=TRANSACTIONID   #1-TransactionId Length        03

    Command+="00"   #00



    GenelKomut="%s%s" % (CommandHeader, Command)


    #<CRC Hesapla>
    GenelKomut=GetCRC(GenelKomut)
    #</CRC Hesapla>

    SAS_SendCommand("ParaSil",GenelKomut,1)

Last_ParaYukle_TransferType=0
Last_ParaYukleDate=datetime.datetime.now()
def Komut_ParaYukle(doincreasetransactionid, transfertype):
    global G_Config_IsCashoutSoft
    global IsWaitingForParaYukle
    global Yukle_FirstTransaction
    global Yukle_LastTransaction
    global CashIn_CompletedBy
    global Last_ParaYukleDate
    Last_ParaYukleDate=datetime.datetime.now()

    #SQL_DeviceStatu(2)

    transactionid=Config.getint("payment","transactionid")
    if doincreasetransactionid==1:
        transactionid=transactionid+1
        if transactionid>1000:
            transactionid=1
        Config.set("payment","transactionid",str(transactionid))


    SQL_Safe_InsImportantMessage("AFT Cash-In TransactionId: " + str(transactionid) + "-" + str(doincreasetransactionid),0)

    #session icinde para sifirlama olayi
    if Yukle_FirstTransaction==0:
        Yukle_FirstTransaction=transactionid
    Yukle_LastTransaction=transactionid
    #session icinde para sifirlama olayi

    customerbalance=Decimal(Config.get("customer","customerbalance"))
    customerpromo=Decimal(Config.get("customer","customerpromo"))

    RealTransferType=0
    if transfertype==11 or transfertype==10:
        RealTransferType=transfertype
        customerbalance=JackpotWonAmount
        customerpromo=0

    #BONUS
    if transfertype==13:
        RealTransferType=10 #musteri tamam'a basmazsa problem oluyor
        customerbalance=JackpotWonAmount
        customerpromo=0
        if G_Machine_IsBonusCashable==0:
            RealTransferType=0



    if transfertype==1:#bill acceptordan atilan para!
        customerbalance=Billacceptor_LastCredit
        customerpromo=0
        transfertype=0


    #if customerpromo>1 and G_Machine_DeviceTypeId!=2:
    #    transfertype=10


    customerbalanceint=int(customerbalance*100);
    if customerbalance==0 and customerpromo==0:
        IsWaitingForParaYukle=0
        CashIn_CompletedBy="No-Money"
        print("Parasi yok zaten")
        #SQL_InsImportantMessage("Para yuklemek icin parasi yok K:%s" % (G_User_CardNo),21)
        return
    if doincreasetransactionid==1:
        SaveConfigFile()

    CommandHeader=Config.get("sas","address")      #1-Address  01
    CommandHeader+="72"   #1-Command  72
    CommandHeader+=""#1-Length       55

    
    Command=""
    Command+="00"   #1-Transfer Code    00
    Command+="00"   #1-Transfer Index   00
    
    if RealTransferType==10:
        Command+="10"   #1-Transfer Type    00
    elif RealTransferType==11:
        Command+="11"   #1-Transfer Type    00
    else:
        Command+="00"   #1-Transfer Type    00

    #2020-02-17 fixit savoy test
    if transfertype==13:
        if G_Machine_IsBonusCashable==1:
            Command+=AddLeftBCD(customerbalanceint,5)   #5-Cashable amount (BCD)
            Command+=AddLeftBCD(0,5)                    #5-Restricted amount  (BCD)
            Command+=AddLeftBCD(0,5)                    #5-Nonrestricted amount (BCD)

        #Bulgaria Promo olsun istedi....
        if G_Machine_IsBonusCashable==0:
            Command+=AddLeftBCD(0,5)       #5-Cashable amount (BCD)    00 00 50 00 00 --> 5000,00 TL
            Command+=AddLeftBCD(customerbalanceint,5)   #5-Restricted amount  (BCD)
            Command+=AddLeftBCD(0,5)                           #5-Nonrestricted amount (BCD)

        #Bulgaria idi
        #if G_Machine_IsBonusCashable==0:
        #    Command+=AddLeftBCD(0,5)       #5-Cashable amount (BCD)    00 00 50 00 00 --> 5000,00 TL
        #    Command+=AddLeftBCD(0,5)   #5-Restricted amount  (BCD)
        #    Command+=AddLeftBCD(customerbalanceint,5)                           #5-Nonrestricted amount (BCD)
    else:
        Command+=AddLeftBCD(customerbalanceint,5)       #5-Cashable amount (BCD)    00 00 50 00 00 --> 5000,00 TL
        Command+=AddLeftBCD(int(customerpromo*100),5)   #5-Restricted amount  (BCD)
        Command+="0000000000"                           #5-Nonrestricted amount (BCD)


    #cashout mode: hard olmali
    if G_Config_IsCashoutSoft==1:
        #Apexlerde 3 olacak
        Command+="03"                        #1-Transfer flag    cashout mode soft:
    else:
        #07 Olunca apexlerde problem yapiyor!!!
        Command+="07"                        #1-Transfer flag  cashout mode hard 2021-07-08 Cashout ile denedik

    Command+=Config.get("sas","assetnumber")          #4-Asset number     01 00 00 00
    Command+=Config.get("sas","registrationkey")   #20-Registration key
    

    
    TRANSACTIONID="".join("{:02x}".format(ord(c)) for c in str(transactionid))
    Command+=AddLeftBCD(int(len(TRANSACTIONID)/2),1)   #1-TransactionId Length        03
    Command+=TRANSACTIONID #X-TransactionID ( Max:20)      

    #Command+=(datetime.datetime.now()+datetime.timedelta(days=5)).strftime("%m%d%Y")     #4-ExpirationDate (BCD) MMDDYYYY            05 30 20 16
    Command+="00000000"#ExpirationDate (BCD) 

    if transfertype==13 or customerpromo>0:
        Command+="0030"         #2-Pool ID                                0C 00
    else:
        Command+="0000"         #2-Pool ID                                0C 00

    Command+="00"           #1-Receipt data length                      00
    Command+=""             #X-Recepipt Data
    Command+=""         #2-Lock Timeout - BCD   //Only used for Lock After Transfer request. KULLANMA
    CommandHeader+=hex(int(len(Command)/2)).replace("0x","")
    Command+=""             #2-CRC - altta hesapliyoruz


    GenelKomut="%s%s" % (CommandHeader, Command)

    #<CRC Hesapla>
    GenelKomut=GetCRC(GenelKomut)
    #</CRC Hesapla>

    print("ParaYukle TransactionId", transactionid, GenelKomut)

    #print('KOMUT PARA YUK017235000010000000010000000000000000000000030100000000000000000000000000000000000000000000000232300818201700300093A5LE', len(GenelKomut), GenelKomut, 'IsWaitingLoopOnSASPooling', IsWaitingLoopOnSASPooling)
    SAS_SendCommand("ParaYukle",GenelKomut,1)



def Yanit_LegacyBonusPay(Yanit):
    index=0
    try:
        Address=Yanit[ index : index+2]
        index=index+2
    
        Command=Yanit[ index : index+2]
        index=index+2
    
        LegacyBonusPay=Yanit[ index : index+2]
        index=index+2
    
        Multiplier=Yanit[ index : index+2]
        index=index+2
    
        MultiplierWin=Yanit[ index : index+8]
        index=index+8
    
        TaxStatus=Yanit[ index : index+2]
        index=index+2
    
        Bonus=Yanit[ index : index+8]
        index=index+8
    
        DBMessage="Legacy Bonus Multiplier: " + str(Multiplier) + " MultiplierWin: " + str(MultiplierWin) + " TaxStatus: " + str(TaxStatus) + " Bonus: " + str(Bonus)
        print(DBMessage)

        SQL_Safe_InsImportantMessage(DBMessage,68)

        CRC=Yanit[ index : index+4]
        index=index+4
    except Exception as e:
        print("Exception On Yanit_LegacyBonusPay " + str(index) + " " + Yanit)

def Yanit_EnabledGameNumbers(Yanit):
    index=0
    try:
        Address=Yanit[ index : index+2]
        index=index+2

        Command=Yanit[ index : index+2]
        index=index+2

        Length=Yanit[ index : index+2]
        index=index+2

        NumberOfGames=Yanit[ index : index+2]
        index=index+2

        GameNumbers=Yanit[ index : len(Yanit)-index-4]
        index=index+len(Yanit)-index-4

        EnabledGameIds=""
        i=0
        while len(GameNumbers)>i:
            GameId=str(int(GameNumbers[i:i+4]))
            if len(EnabledGameIds)>0:
                EnabledGameIds=EnabledGameIds + ","
            EnabledGameIds=EnabledGameIds+GameId
            i=i+4

        print("EnabledGameIds", EnabledGameIds)

        Crc=Yanit[ index : index+4]
        index=index+4

        if len(Crc)==4:
            print("Update Enabled Games")
            SQL_UpdDeviceEnablesGames(EnabledGameIds, Yanit)
        else:
            print("Can't update enabled games!")

    except Exception as e:
        print("Exception On Yanit_EnabledGameNumbers")


def Yanit_GameConfiguration(Yanit):
    index=0
    try:
        Address=Yanit[ index : index+2]
        index=index+2

        Command=Yanit[ index : index+2]
        index=index+2

        GameNumber=Yanit[ index : index+4]
        index=index+4

        GameNId=Yanit[ index : index+4]
        index=index+4

        AdditionalId=Yanit[ index : index+6]
        index=index+6

        Denomination=Yanit[ index : index+2]
        index=index+2

        if Denomination=="01":
            Denomination=0.01
        elif Denomination=="02":
            Denomination=0.05
        elif Denomination=="03":
            Denomination=0.10
        elif Denomination=="04":
            Denomination=0.25
        elif Denomination=="05":
            Denomination=0.50
        elif Denomination=="06":
            Denomination=1
        elif Denomination=="07":
            Denomination=5
        elif Denomination=="08":
            Denomination=10
        elif Denomination=="09":
            Denomination=20
        elif Denomination=="0A":
            Denomination=100
        elif Denomination=="0B":
            Denomination=0.20
        elif Denomination=="0C":
            Denomination=2
        elif Denomination=="0D":
            Denomination=2.5
        elif Denomination=="0E":
            Denomination=25
        elif Denomination=="0F":
            Denomination=50
        elif Denomination=="10":
            Denomination=200
        elif Denomination=="11":
            Denomination=250
        elif Denomination=="12":
            Denomination=500
        elif Denomination=="13":
            Denomination=1000
        elif Denomination=="14":
            Denomination=2000
        elif Denomination=="15":
            Denomination=2500
        elif Denomination=="16":
            Denomination=5000
        elif Denomination=="17":
            Denomination=0.02
        elif Denomination=="18":
            Denomination=0.03
        elif Denomination=="19":
            Denomination=0.15
        elif Denomination=="1A":
            Denomination=0.40
        elif Denomination=="1B":
            Denomination=0.005
        elif Denomination=="1C":
            Denomination=0.0025
        elif Denomination=="1D":
            Denomination=0.002
        elif Denomination=="1E":
            Denomination=0.001
        elif Denomination=="1F":
            Denomination=0.0005

        MaxBet=Yanit[ index : index+2]
        index=index+2
        
        ProgressiveGroup=Yanit[ index : index+2]
        index=index+2
        
        GameOptions=Yanit[ index : index+4]
        index=index+4
        
        PayTable=Yanit[ index : index+12]
        index=index+12
        PayTable=HEXNumberToInt(PayTable)#03TR00
        
        BasePercentage=Yanit[ index : index+8]
        index=index+8
        BasePercentage=Decimal(HEXNumberToInt(BasePercentage))/100
        
        Crc=Yanit[ index : index+4]
        index=index+4
        
        
        SQL_UpdDeviceDenomPayBack(BasePercentage, Denomination, int(GameNumber),MaxBet)
        
        if GameNumber=="0000":
            SQL_DeviceStatu(0)
        else:
            print("Update GameInfo")


    except Exception as e:
        print("Exception On Yanit_GameConfiguration")
        #ExceptionHandler("Yanit_GameInfo",e,0)

def Yanit_HandpayInfo(Yanit):
    index=0
    try:
        Address=Yanit[ index : index+2]
        index=index+2

        Command=Yanit[ index : index+2]
        index=index+2

        ProgressiveGroup=Yanit[ index : index+2]
        index=index+2
        
        HandpayLevel=Yanit[ index : index+2]
        index=index+2

        Amount=Decimal(Yanit[ index : index+10])/100
        index=index+10

        PartialPay=Decimal(Yanit[ index : index+4])/100
        index=index+4

        ResetId=Yanit[ index : index+2]
        index=index+2

        UnUsed=Yanit[ index : index+20]
        index=index+20

        Crc=Yanit[ index : index+4]
        index=index+4

        SQL_InsDeviceHandpay(ProgressiveGroup, HandpayLevel, Amount, PartialPay, ResetId, UnUsed, Yanit)
        print("Amount", Amount, "ProgressiveGroup", ProgressiveGroup ,"HandpayLevel", HandpayLevel, "PartialPay", PartialPay, "ResetId", ResetId, "Crc", Crc)

    except Exception as e:
        ExceptionHandler("Yanit_HandpayInfo",e,0)

def Yanit_GameInfo(Yanit):
    index=0
    try:
        Address=Yanit[ index : index+2]
        index=index+2

        Command=Yanit[ index : index+2]
        index=index+2

        Length=Yanit[ index : index+2]
        index=index+2

        GameNumber=Yanit[ index : index+4]
        index=index+4

        MaxBet=Yanit[ index : index+4]
        index=index+4

        ProgressiveGroup=Yanit[ index : index+2]
        index=index+2


        ProgressiveLevels=Yanit[ index : index+8]
        index=index+8

        GameNameLength=int(Yanit[ index : index+2],16)*2
        index=index+2


        GameName=Yanit[ index : index + int(GameNameLength)]
        index=index+int(GameNameLength)
        GameName=HEXNumberToInt(GameName)
    
        if len(GameName)>0:
            print("GameNumber", GameNumber, "GameName", GameName)
            SQL_UpdGameName(GameNumber, GameName)
            #tsp_UpdGameName	@DeviceId	bigint, @GameId		bigint, @GameName	varchar(max)


        PaytableNameLength=int(Yanit[ index : index+2],16)*2
        index=index+2

        PaytableName=Yanit[ index : index + int(PaytableNameLength)]
        index=index+int(PaytableNameLength)
        PaytableName=HEXNumberToInt(PaytableName)
        #print("PaytableName", PaytableName)

        WagerCategories=Yanit[ index : index+4]
        index=index+4
    except Exception as e:
        ExceptionHandler("Yanit_GameInfo",e,0)



#def Yanit_GetMeter(Yanit):
#    try:
#        global G_Machine_IsSASPortFound
#        G_Machine_IsSASPortFound=1

#        index=0
#        Address=Yanit[ index : index+2]
#        index=index+2

#        Command=Yanit[ index : index+2]
#        index=index+2

#        GameNumber=int(Yanit[ index : index+4])
#        index=index+4

#        TotalCoinIn=Decimal(Yanit[ index : index+8])/100
#        index=index+8

#        TotalCoinOut=Decimal(Yanit[ index : index+8])/100
#        index=index+8

#        TotalJackpot=Decimal(Yanit[ index : index+8])/100
#        index=index+8

#        GamesPlayed=int(Yanit[ index : index+8])
#        index=index+8

#        print("Get meter GameNumber:", GameNumber, " TotalCoinIn: " , TotalCoinIn, " TotalCoinOut:" , TotalCoinOut , " TotalJackpot:" , TotalJackpot, " GamesPlayed:" , GamesPlayed)
#        SQL_InsDeviceMeter(GameNumber, TotalCoinIn, TotalCoinOut,TotalJackpot ,GamesPlayed,0,0,0)

#    except Exception as e:
#        ExceptionHandler("Yanit_Getmeter",e,0)


def GetLengthByMeterCode(MeterCode):

    if MeterCode=="0D" or MeterCode=="0E" or MeterCode=="0F" or MeterCode=="10" or MeterCode=="80" or MeterCode=="82" or MeterCode=="84" or MeterCode=="86" or MeterCode=="88" or MeterCode=="8A" or MeterCode=="8C" or MeterCode=="8E" or MeterCode=="90" or MeterCode=="92" or MeterCode=="A0" or MeterCode=="A2" or MeterCode=="A4" or MeterCode=="A6" or MeterCode=="A8" or MeterCode=="AA" or MeterCode=="AC" or MeterCode=="AE" or MeterCode=="B0" or MeterCode=="B8" or MeterCode=="BA" or MeterCode=="BC":
        return 5

    return 4

AssetNumberInt=0

def Yanit_MeterAll(Yanit):
    global G_LastMeterDate
    global G_Device_AssetNo
    if AssetNumberInt==0:
        Wait_Bakiye(11,1,"asset")
        Komut_ReadAssetNo()
        print("Learn asset no first!")
        SQL_Safe_InsImportantMessage("Learn asset no first",67)
        Komut_GetMeter(0,0)
        return

    global IsWaitingForMeter

    global G_Machine_IsSASPortFound
    G_Machine_IsSASPortFound=1


    try:
        Last_G_LastMeterDate_Diff=(datetime.datetime.now()-G_LastMeterDate).total_seconds()
        if Last_G_LastMeterDate_Diff>(60*65):
            SQL_Safe_InsImportantMessage("Meter long " + str(Last_G_LastMeterDate_Diff) + ":" + Yanit,67)
    except Exception as esql:
        print("SQLite Err Init!")

    index=0
    Address=Yanit[ index : index+2]
    index=index+2

    Command=Yanit[ index : index+2]
    index=index+2

    #meter:
    Length=Yanit[ index : index+2]
    index=index+2

    messageLength=(int(Yanit[4:6], 16)*2)+10
    

    GameNumber=Yanit[ index : index+4]
    index=index+4




    TotalCoinIn=-1
    TotalCoinOut=-1
    TotalJackpotCredit=-1
    TotalHandPaidCredit=-1
    TotalCreditsBillsAccepted=-1
    TurnOver=-1
    TurnOut=-1
    NonCashableIn=-1
    NonCashableOut=-1
    TotalBonus=-1



    
    
    TotalElectronicIn_17=0
    TotalElectronicOut_18=0
    TotalTicketIn_15=0
    TotalTicketOut_16=0
    TotalAttendantHandPaid_17=0
    TotalCancelledCredits_04=0
    TotalHandpaidCredits_23=0

    TotalCancelledCredits_04=-1
    GamesPlayed_05=-1
    GamesWon_06=-1
    CurrentCredits_0C=-1
    WeightedAverage_7F=-1
    RegularCashableKeyed_FA=-1
    RestrictedKeyed_FB=-1
    NonrestrictedKeyed_FC=-1
    TotalMachinePaidProgressive_1D=-1
    
    GamesLost_07=-1

    #04: Total Cancelled Credits
    #05: Games Played
    #06: Games Won
    #0C: Current Credits
    #7F: Weighted average theoretical payback 
    #FA: Regular cashashle feyed on funds
    #FB: Restricted promotional keyed on funds
    #FC: Nonrestircted promotional keyed-on funds
    #19: Total Restrictited Amount                      --Sil
    #1D: Total Machine paid progressive win (credits)    --Silebiliriz.


    

    ReceivedAllMeter="%s|" % (Yanit)
    #ReceivedAllMeter=""

    MeterCode="XXXX"
    if Command=="2F":
        while len(MeterCode)>0:
            MeterCode=Yanit[ index : index+2]
            index=index+2

            NextGenislik=GetLengthByMeterCode(MeterCode)*2
            MeterVal=Yanit[ index : index+NextGenislik]
            index=index+NextGenislik

            try:
                MeterValue=Decimal(MeterVal)/100
                if (MeterCode=="A0") and TotalCoinIn==-1:
                    TotalCoinIn=MeterValue

                if (MeterCode=="B8") and TotalCoinOut==-1:
                    TotalCoinOut=MeterValue

                if (MeterCode=="00") and TurnOver==-1:
                    TurnOver=MeterValue

                if (MeterCode=="01") and TurnOut==-1:
                    TurnOut=MeterValue

                if MeterCode=="02" and TotalJackpotCredit==-1:
                    TotalJackpotCredit=MeterValue

                if MeterCode=="03" and TotalHandPaidCredit==-1:
                    TotalHandPaidCredit=MeterValue



                if MeterCode=="0B" and TotalCreditsBillsAccepted==-1:
                    TotalCreditsBillsAccepted=MeterValue

                if MeterCode=="A2" and NonCashableIn==-1:
                    NonCashableIn=MeterValue

                if MeterCode=="BA" and NonCashableOut==-1:
                    NonCashableOut=MeterValue

                if MeterCode=="1E" and TotalBonus==-1:
                    TotalBonus=MeterValue

                #<Second type meters>-----------------------
                if MeterCode=="04" and TotalCancelledCredits_04==-1:
                    TotalCancelledCredits_04=MeterValue

                if MeterCode=="05" and GamesPlayed_05==-1:
                    GamesPlayed_05=MeterValue*100

                if MeterCode=="06" and GamesWon_06==-1:
                    GamesWon_06=MeterValue*100

                if MeterCode=="0C" and CurrentCredits_0C==-1:
                    CurrentCredits_0C=MeterValue

                if MeterCode=="7F" and WeightedAverage_7F==-1:
                    WeightedAverage_7F=MeterValue

                if MeterCode=="FA" and RegularCashableKeyed_FA==-1:
                    RegularCashableKeyed_FA=MeterValue

                if MeterCode=="FB" and RestrictedKeyed_FB==-1:
                    RestrictedKeyed_FB=MeterValue

                if MeterCode=="FC" and NonrestrictedKeyed_FC==-1:
                    NonrestrictedKeyed_FC=MeterValue

                if MeterCode=="1D" and TotalMachinePaidProgressive_1D==-1:
                    TotalMachinePaidProgressive_1D=MeterValue
                #<Second type meters>-----------------------

                #print("MeterCode:" , MeterCode, " MeterVal:" , MeterValue)
                ReceivedAllMeter="%s%s-%s|" % (ReceivedAllMeter, MeterCode, MeterVal)
            except Exception as e:
                print("Meter is ok")
                print(MeterCode, MeterVal)
                break

    if Command=="AF":
        tryCount=0
        while tryCount<15:
            tryCount=tryCount+1
        
            MeterCode=""
            MeterLength=""
            MeterVal=""
            MeterValue=0
        
            try:
                MeterCode=Yanit[ index : index+2]
                index=index+4
            
                MeterLength=int(Yanit[ index : index+2])
                index=index+2
                MeterLength=MeterLength*2
            
                MeterVal=Yanit[ index : index+MeterLength]
                index=index+MeterLength
                MeterValue=Decimal(MeterVal)/100
            
            
                #<First type meters>-----------------------
                if (MeterCode=="A0") and TotalCoinIn==-1:
                    TotalCoinIn=MeterValue

                if (MeterCode=="B8") and TotalCoinOut==-1:
                    TotalCoinOut=MeterValue

                if (MeterCode=="00") and TurnOver==-1:
                    TurnOver=MeterValue

                if (MeterCode=="01") and TurnOut==-1:
                    TurnOut=MeterValue

                if MeterCode=="02" and TotalJackpotCredit==-1:
                    TotalJackpotCredit=MeterValue

                if MeterCode=="03" and TotalHandPaidCredit==-1:
                    TotalHandPaidCredit=MeterValue

                if MeterCode=="0B" and TotalCreditsBillsAccepted==-1:
                    TotalCreditsBillsAccepted=MeterValue

                if MeterCode=="A2" and NonCashableIn==-1:
                    NonCashableIn=MeterValue

                if MeterCode=="BA" and NonCashableOut==-1:
                    NonCashableOut=MeterValue

                if MeterCode=="1E" and TotalBonus==-1:
                    TotalBonus=MeterValue
                #</First type meters>-----------------------

                #<Second type meters>-----------------------
                if MeterCode=="04" and TotalCancelledCredits_04==-1:
                    TotalCancelledCredits_04=MeterValue

                if MeterCode=="05" and GamesPlayed_05==-1:
                    MeterValue=int(MeterValue*100)
                    GamesPlayed_05=MeterValue

                if MeterCode=="06" and GamesWon_06==-1:
                    MeterValue=int(MeterValue*100)
                    GamesWon_06=MeterValue

                    print("MeterCode", MeterCode, "MeterLength", MeterLength, "MeterVal", MeterVal, "MeterValue", MeterValue)
                    print("Break")
                    break

                if MeterCode=="0C" and CurrentCredits_0C==-1:
                    CurrentCredits_0C=MeterValue

                if MeterCode=="7F" and WeightedAverage_7F==-1:
                    WeightedAverage_7F=MeterValue

                if MeterCode=="FA" and RegularCashableKeyed_FA==-1:
                    RegularCashableKeyed_FA=MeterValue

                if MeterCode=="FB" and RestrictedKeyed_FB==-1:
                    RestrictedKeyed_FB=MeterValue

                if MeterCode=="FC" and NonrestrictedKeyed_FC==-1:
                    NonrestrictedKeyed_FC=MeterValue

                if MeterCode=="1D" and TotalMachinePaidProgressive_1D==-1:
                    TotalMachinePaidProgressive_1D=MeterValue
                #<Second type meters>-----------------------
            
                print("MeterCode", MeterCode, "MeterLength", MeterLength, "MeterVal", MeterVal, "MeterValue", MeterValue)
            except Exception as e:
                tryCount=tryCount
                print("Exception MeterCode", MeterCode, "MeterLength", MeterLength, "MeterVal", MeterVal, "MeterValue", MeterValue)


    #if NonCashableIn==-1 or NonCashableOut==-1 or (len(Yanit)<messageLength):
    if len(Yanit)<messageLength:
        if len(Yanit)<messageLength:
            print("********** METER GELDI AMA KABUL ETMEDIK! ***************")
        GetMeter(0,"again")
        return

    try:
        IsWaitingForMeter=0


        print(ReceivedAllMeter)


        if Command=="2F":
            if GamesPlayed_05<0:
                print("Meter 1st Version")
                SQL_Safe_MeterInsert(GameNumber,TotalCoinIn, TotalCoinOut, TotalJackpotCredit, GamesPlayed_05, TotalHandPaidCredit, TotalCreditsBillsAccepted,CurrentCredits_0C, TurnOver, TurnOut, NonCashableIn, NonCashableOut, TotalBonus, ReceivedAllMeter, GamesWon_06, GamesLost_07)
                G_LastMeterDate=datetime.datetime.now()
            else:
                print("Meter 2nd Version",GamesPlayed_05)
                print("TotalCancelledCredits_04", TotalCancelledCredits_04, "GamesPlayed_05", GamesPlayed_05, "GamesWon_06", GamesWon_06, "CurrentCredits_0C", CurrentCredits_0C, "WeightedAverage_7F", WeightedAverage_7F, "RegularCashableKeyed_FA", RegularCashableKeyed_FA, "RestrictedKeyed_FB", RestrictedKeyed_FB, "NonrestrictedKeyed_FC", NonrestrictedKeyed_FC, "TotalMachinePaidProgressive_1D", TotalMachinePaidProgressive_1D)
                SQL_Safe_MeterInsert2(TotalCancelledCredits_04, GamesPlayed_05, GamesWon_06, CurrentCredits_0C, WeightedAverage_7F, RegularCashableKeyed_FA, RestrictedKeyed_FB, NonrestrictedKeyed_FC, TotalMachinePaidProgressive_1D)

            if GamesPlayed_05>-1:
                SQL_InsDeviceMeterAll("-1",ReceivedAllMeter)

        if Command=="AF":
            print("Meter 3st Version")
            SQL_Safe_MeterInsert(GameNumber,TotalCoinIn, TotalCoinOut, TotalJackpotCredit, GamesPlayed_05, TotalHandPaidCredit, TotalCreditsBillsAccepted,CurrentCredits_0C, TurnOver, TurnOut, NonCashableIn, NonCashableOut, TotalBonus, ReceivedAllMeter, GamesWon_06, GamesLost_07)
            G_LastMeterDate=datetime.datetime.now()

        if IsCardReaderBusy!=1:
            PrintAndSetAsStatuText("Meter is received")
        SQL_Safe_InsImportantMessage("Meter is received",67)
    except Exception as e:
        print("Meter insert fail")
    

def SQL_Safe_MeterInsert(GameNumber,TotalCoinIn, TotalCoinOut, TotalJackpotCredit, GamesPlayed, TotalHandPaidCredit, TotalCreditsBillsAccepted,CurrentCredits_0C, TurnOver, TurnOut, NonCashableIn, NonCashableOut, TotalBonus, ReceivedAllMeter, GamesWon, GamesLost):
    processThread = Thread(target=SQL_MeterInsert, args=(GameNumber,TotalCoinIn, TotalCoinOut, TotalJackpotCredit, GamesPlayed, TotalHandPaidCredit, TotalCreditsBillsAccepted,CurrentCredits_0C, TurnOver, TurnOut, NonCashableIn, NonCashableOut, TotalBonus, ReceivedAllMeter,GamesWon, GamesLost,))
    processThread.name="SafeMeter"
    processThread.start()

def SQL_MeterInsert(GameNumber,TotalCoinIn, TotalCoinOut, TotalJackpotCredit, GamesPlayed, TotalHandPaidCredit, TotalCreditsBillsAccepted,CurrentCredits_0C, TurnOver, TurnOut, NonCashableIn, NonCashableOut, TotalBonus, ReceivedAllMeter,GamesWon, GamesLost):
    SQL_InsDeviceMeter(GameNumber,TotalCoinIn, TotalCoinOut, TotalJackpotCredit, GamesPlayed, TotalHandPaidCredit, TotalCreditsBillsAccepted,CurrentCredits_0C, TurnOver, TurnOut, NonCashableIn, NonCashableOut, TotalBonus,GamesWon, GamesLost)


def SQL_Safe_MeterInsert2(TotalCancelledCredits_04, GamesPlayed_05, GamesWon_06, CurrentCredits_0C, WeightedAverage_7F, RegularCashableKeyed_FA, RestrictedKeyed_FB, NonrestrictedKeyed_FC, TotalMachinePaidProgressive_1D):
    processThread = Thread(target=SQL_MeterInsert2, args=(TotalCancelledCredits_04, GamesPlayed_05, GamesWon_06, CurrentCredits_0C, WeightedAverage_7F, RegularCashableKeyed_FA, RestrictedKeyed_FB, NonrestrictedKeyed_FC, TotalMachinePaidProgressive_1D,))
    processThread.name="SafeMeter2"
    processThread.start()

def SQL_MeterInsert2(TotalCancelledCredits_04, GamesPlayed_05, GamesWon_06, CurrentCredits_0C, WeightedAverage_7F, RegularCashableKeyed_FA, RestrictedKeyed_FB, NonrestrictedKeyed_FC, TotalMachinePaidProgressive_1D):
    SQL_InsDeviceMeter2(TotalCancelledCredits_04, GamesPlayed_05, GamesWon_06, CurrentCredits_0C, WeightedAverage_7F, RegularCashableKeyed_FA, RestrictedKeyed_FB, NonrestrictedKeyed_FC, TotalMachinePaidProgressive_1D)


Global_ParaYuklemeFail_SQL=0

def Yanit_ParaYukle(Yanit):
    #2020-07-17
    global IsWaitingForParaYukle
    global Global_ParaYukleme_TransferStatus
    global Global_ParaYuklemeFail_SQL
    global CashIn_CompletedBy


    try:
        index=0
        Address=Yanit[ index : index+2]
        index=index+2

        Command=Yanit[ index : index+2]
        index=index+2

        Length=Yanit[ index : index+2]
        index=index+2

        TransactionBuffer=Yanit[ index : index+2]
        index=index+2

        TransferStatus=Yanit[ index : index+2]#Table 8.3e
        index=index+2


        print("Para yukleme yanit TransferStatus", TransferStatus)




        Amounts=""
        try:

            Amounts=Amounts + " ("
            Amounts=Amounts + "C:" + Yanit[14:24]
            Amounts=Amounts + " P:" + Yanit[24:34]
            Amounts=Amounts + ")"


        except Exception as eAmounts:
            print("Err on get amounts")

        SQL_InsImportantMessage("Cashin Transfer Status:" + str(TransferStatus),68)

        if TransferStatus=="00":
            PrintAndSetAsStatuText("%s" % ('Answer came for AFT-72 Up'))
            #2021-07-23 ekledim.
            Global_ParaYukleme_TransferStatus=TransferStatus
            #SQL_Safe_InsImportantMessage("Cashin is completed" + Amounts,81)
            #IsWaitingForParaYukle=0
        else:
            Global_ParaYukleme_TransferStatus=TransferStatus
            if Global_ParaYukleme_TransferStatus=="87":
                #Komut_BakiyeSorgulama(1,0,"parayukle87")
                Global_ParaYuklemeFail_SQL=Global_ParaYuklemeFail_SQL+1
                if Global_ParaYuklemeFail_SQL%6==1:
                    PrintAndSetAsStatuText("%s%s" % ('Cant Money Up. Door is opened, tilt or disabled! Statu: ', TransferStatus))
                    SQL_InsImportantMessageByWarningType("Door is opened, slot tilt or disabled! Can't upload money! Please check EGM! Statu: 87",1,5)
                    GUI_ShowIfPossibleMainStatu("Door is opened or slot tilt")
            elif Global_ParaYukleme_TransferStatus=="81" or Global_ParaYukleme_TransferStatus=="95":

                if G_Machine_DeviceTypeId==6:
                    PrintAndSetAsStatuText("%s%s" % ('Not unique Megajack Statu: ', TransferStatus))
                    if Wait_Bakiye(1,0,"parayukle6")==1 and Yanit_BakiyeTutar>0:
                        IsWaitingForParaYukle=0
                        CashIn_CompletedBy="Megajack"
                        PrintAndSetAsStatuText("%s%s" % ('Megajack money up ok! ', TransferStatus))
                else:
                    PrintAndSetAsStatuText("%s%s" % ('Money U. TransactionID is not unique. Statu: ', TransferStatus))

            elif Global_ParaYukleme_TransferStatus=="83":
                PrintAndSetAsStatuText("%s%s" % ('Not a valid transfer function. Statu: ', TransferStatus))
            elif Global_ParaYukleme_TransferStatus=="84":
                PrintAndSetAsStatuText("%s%s" % ('Cant transfer big money to GM: ', TransferStatus))
                SQL_InsImportantMessageByWarningType("Cant transfer big amount of money to GM. Statu: 84",1,14)
                GUI_ShowIfPossibleMainStatu("Can't transfer big amount of money")
                time.sleep(1)
            elif Global_ParaYukleme_TransferStatus=="FF":
                PrintAndSetAsStatuText("%s%s" % ('No transfer information available. Code:', TransferStatus))
                GUI_ShowIfPossibleMainStatu("No transfer information available. Code: FF")
                time.sleep(1)
            elif Global_ParaYukleme_TransferStatus=="89":
                Komut_ReadAssetNo()
                PrintAndSetAsStatuText("%s%s" % ('Registration key doesnt match. Statu: ', TransferStatus))
                time.sleep(1)
            elif Global_ParaYukleme_TransferStatus=="C1":
                PrintAndSetAsStatuText("%s%s" % ('Unsupported transfer code', TransferStatus))
                SQL_InsImportantMessageByWarningType("Unsupported transfer code Statu C1",1,14)
                GUI_ShowIfPossibleMainStatu("Unsupported transfer code")
                time.sleep(1)
            elif Global_ParaYukleme_TransferStatus=="93":
                Komut_ReadAssetNo()
                Wait_Bakiye(11,1,"asset")
                PrintAndSetAsStatuText("%s%s" % ('Asset number zero or does not match. Statu: ', TransferStatus))
                SQL_Safe_InsImportantMessageByWarningType("%s%s" % ('Asset number zero or does not match. Statu: ', TransferStatus),0,1)
                time.sleep(1)
            elif Global_ParaYukleme_TransferStatus=="94":
                Komut_BakiyeSorgulama(1,0,"Yukle:S94")
                PrintAndSetAsStatuText("%s%s" % ('Gaming machine not locked for transfer Statu: ', TransferStatus))
                SQL_Safe_InsImportantMessageByWarningType("%s%s" % ('Gaming machine not locked for transfer. Statu: ', TransferStatus),0,1)
                time.sleep(1)
            elif Global_ParaYukleme_TransferStatus=="85":
                PrintAndSetAsStatuText("%s%s" % ('Balance is not compatible with denomination! Statu: ', TransferStatus))
                SQL_Safe_InsImportantMessageByWarningType("%s%s" % ('Balance is not compatible with denomination! Statu: ', TransferStatus),0,1)
                time.sleep(1)
            elif Global_ParaYukleme_TransferStatus=="C0":
                PrintAndSetAsStatuText("%s%s" % ('Not compatible with current transfer in progress ', TransferStatus))
                Komut_BakiyeSorgulama(1,1,"")
            elif Global_ParaYukleme_TransferStatus=="40":
                Komut_Interragition("Mustafa40Wait!")
                PrintAndSetAsStatuText("%s%s" % ('Transfer pending Statu: ', TransferStatus))
            else:
                PrintAndSetAsStatuText("%s%s" % ('Answer Money Up. But Status:', TransferStatus))



        ReceiptStatus=Yanit[ index : index+2]
        index=index+2

        TransferType=Yanit[ index : index+2]
        index=index+2


        if Global_ParaYukleme_TransferStatus=="87" and (TransferType=="10" or TransferType=="11"):
            if G_Machine_BonusId==0:
                SQL_InsImportantMessageByWarningType("Cannot upload JACKPOT! Please card-out and write a slip for jackpot!",1,25)



        CashableAmount=Yanit[ index : index+10]
        index=index+10

        RestrictedAmount="0"
        NonrestrictedAmount="0"

        #serkan
        if G_Machine_IsPromoAccepts==0:
            index=index+10
            index=index+10
        else:
            RestrictedAmount=Yanit[ index : index+10]
            index=index+10

            NonrestrictedAmount=Yanit[ index : index+10]
            index=index+10


        TransferFlag=Yanit[ index : index+2]
        index=index+2

        AssetNumber=Yanit[ index : index+8]
        index=index+8

        TransactionId=0
        TransactionIdLength=0

        try:
            TransactionIdLength=int(Yanit[ index : index+2])*2
            index=index+2
    
            TransactionIdF=Yanit[ index : index+TransactionIdLength]
            TransactionId=HEXNumberToInt(TransactionIdF)
            index=index+TransactionIdLength
        except Exception as eTransactionId:
            index=index
            #print("Gelen Yanit cok kucuk! Buyuk bi ihtimal Merkur")


        IsTransactionIdOk=1
        #2020-03-13: 
        if (int(TransactionId)>=int(Yukle_FirstTransaction) and int(TransactionId)<=int(Yukle_LastTransaction))==False:
            IsTransactionIdOk=0
            print("**********************Impossible! Wrong transaction Id!!!!",Yukle_FirstTransaction,TransactionId ,Yukle_LastTransaction)
            TransferStatus="MT"
            Global_ParaYukleme_TransferStatus=TransferStatus
            SQL_Safe_InsImportantMessage("Wrong transaction Id " + str(TransactionId) + " - " + str(Yukle_FirstTransaction)+ " - " + str(Yukle_LastTransaction) ,81)

        if IsTransactionIdOk==1 and TransferStatus=="00":
            SQL_Safe_InsImportantMessage("Cashin is completed" + Amounts + " T:" + str(TransactionId),81)
            IsWaitingForParaYukle=0




    except Exception as e1:
        print("hata var...")




IsCollectButtonProcessInUse=0
def Komut_CollectButtonProcess():
    global IsCollectButtonProcessInUse
    global Cashout_Source
    global G_Session_CardExitStatus
    global IsCardInside
    Cashout_Source=123
    G_Session_CardExitStatus=2

    if IsWaitingForParaYukle==1:
        print("SESSION ACILMADI. HANDPAY'E DUSSUN")
        print("SESSION ACILMADI. HANDPAY'E DUSSUN")
        print("SESSION ACILMADI. HANDPAY'E DUSSUN")
        print("SESSION ACILMADI. HANDPAY'E DUSSUN")
        return

    if IsCardInside==0:
        Komut_CancelBalanceLock()


    

    if IsCollectButtonProcessInUse==1:
        print("Cashout is already in process")
        return

    IsCollectButtonProcessInUse=1

    ChangeRealTimeReporting(0)

    Cmd=Komut_BakiyeSorgulama(2,0,"cardexit-Komut_CollectButtonProcess")
    print("Start cashout process")
    

    try:
        SQL_Safe_InsImportantMessage("Cashout button is pressed",82)
        Card_RemoveCustomerInfo(123)
    except Exception as e:
        print("Card_RemoveCustomerInfo ERR")
        ExceptionHandler("Cashout button error",e,0)

    IsCollectButtonProcessInUse=0
    IsCardReaderBusy=0#Cashout is started



G_LastInterragition=datetime.datetime.now()
def Komut_Interragition(sender):
    global G_LastInterragition

    DoInAnyCase=0
    if sender.startswith("EraseMoney")==True or sender.startswith("C0")==True or sender.find("AFT") != -1:
        DoInAnyCase=1

    LastDiff=(datetime.datetime.now()-G_LastInterragition).total_seconds() * 1000

    if LastDiff<600 and DoInAnyCase==0:
        print("***********************************")
        print("No need for interrogation!!!", sender, LastDiff)
        print("***********************************")
        return

    G_LastInterragition=datetime.datetime.now()

    print("interragition**************", sender)
    Command="01 72 02 FF 00 0F 22";
    Command="017202FF000F22"
    Command=Command.replace(" ","")
    SAS_SendCommand("%s%s" % ("interragiton", sender),Command,1)
    #SQL_Safe_InsSentCommands("interragiton", Command + "-" + sender)


BalanceQuery_GameLockStatus=""
IsWaitingForBakiyeSorgulama=0


BakiyeSorgulama_Count=0
BakiyeSorgulama_Sender=0
IsBalanceQueryForInfo=1
#isForInfo-> 0: Needed, 1: Bilgi icin,
def Komut_BakiyeSorgulama(sender, isforinfo, sendertext='UndefinedBakiyeSorgulama'):
    if isforinfo==0:
        GUI_ShowIfPossibleMainStatu("Balance query cmd")
    #print("Bakiye sorgula command is executed.")
    global IsWaitingForBakiyeSorgulama
    global IsBalanceQueryForInfo
    global BakiyeSorgulama_Sender
    global BakiyeSorgulama_Count


    IsBalanceQueryForInfo=isforinfo
    BakiyeSorgulama_Sender=sender
    IsLockNeed=False
    if isforinfo==0:
        IsLockNeed=True

    if sender==1:
        IsLockNeed=False


    BakiyeSorgulama_Count=BakiyeSorgulama_Count+1
    if BakiyeSorgulama_Count>1000:
        BakiyeSorgulama_Count=0

    Command="017400000000"#kilitsiz
    if IsLockNeed==False:
        Command="017400000000"#kilitsiz

    #bilgi icin 
    #Command="017400019999" #Transfer to machine
    #Command="017400029999" #Transfer from machine
    #Command="017400039999" #Transfer from machine / to machine

    #<2018-12-28 Salamis>--------------------------------
    if IsLockNeed==True:
        Command="017400039000" #Transfer from machine / to machine
        
        Command="017400019999" #Transfer to machine

        if sender==1:#Para yukleme
            #Command="017400019999" #Transfer to machine
            Command="017400013000" #Transfer to machine

        if sender==2:#Para silme
            #Command="017400029999" #Transfer from machine
            Command="017400029000" #Transfer from machine
    #<2018-04-30>--------------------------------


    if IsLockNeed==False and (G_Machine_DeviceTypeId==5 or G_Machine_DeviceTypeId==9):
        Command="0174FF000000"#kilitsiz





    print("Komut_Bakiyesorgulama-",sendertext, Command)
    if G_Machine_DeviceTypeId==5:
        print("G_Machine_DeviceTypeId Balance",  Command)


    #if Cashout_Source==123:
    #    Command="0174FF000000"#kilitsiz
    #    print("CASHOUT!")

    Command=GetCRC(Command)
    #if sendertext=="cardexit-Komut_CollectButtonProcess" or BakiyeSorgulama_Count%2==0:#20200603
    #    print("Thread ile gonder")
    #    SendSASCommand(Command)

    SAS_SendCommand("MoneyQuery",Command,0)
    return Command
    
    #SQL_Safe_InsSentCommands("MoneyQuery", Command + "-" + sendertext)
    


def Komut_CancelBalanceLock():
    print("Close lock**********************")
    Command=GetCRC("017480030000")
    SAS_SendCommand("MoneyQuery",Command,1)

def Komut_CancelAFTTransfer():
    SQL_Safe_InsImportantMessage("Cancel AFT Transfer",68)
    print("Cancel AFT Transfer**********************")
    Command="017201800BB4"
    SAS_SendCommand("CancelAFT",Command,1)




Yanit_RestrictedPoolID=""
Yanit_BakiyeTutar=0
Yanit_RestrictedAmount=0
Yanit_NonRestrictedAmount=0
def Yanit_BakiyeSorgulama(Yanit):
    try:
        global G_Machine_IsSASPortFound
        global Yanit_BakiyeTutar
        global Yanit_RestrictedAmount
        global Yanit_NonRestrictedAmount
        global G_Machine_Balance
        global G_Machine_Promo
        global BalanceQuery_GameLockStatus
        global IsWaitingForBakiyeSorgulama
        global IsWarnedForTakeWin
        global Bakiye_WaitingForGameLockCount
        global G_LastGame_IsFinished
        global Yanit_RestrictedPoolID
        global Yanit_GameLockStatus
        global G_Device_AssetNo
        global AssetNumberInt


        G_Machine_IsSASPortFound=1

        #01 74 23 01 00 00 00 FF 03 01 9E 46 00 00 01 02 00 00 00 00 00 00 00 00 00 00 00 00 02 98 98 00 00 00 00 00 00 00 AB CF
        #$74 = AFT Game Lock and Status    = FF
        #$74 = Asset Number                = 01000000
        #$74 = Available Transfers         = 03
        #$74 = Host Cashout Status         = 01
        #$74 = AFT Status                  = 9E
        #$74 = Max History Index           = 46
        #$74 = Current Cashable            = 0000010200
        #$74 = Current Restricted          = 0000000000
        #$74 = Current Nonrestricted       = 0000000000
        #$74 = Transfer Limit              = 0002989800
        #$74 = Restricted Expiration       = 00000000
        #$74 = Restricted Pool ID          = 0000


        
        


        #
        #1-Address
        #1-Command 
        #1-Length
        #4-Asset Number
        #1-Game lock status
        #1-Availale transfers
        #1-Host cashout status
        #1-AFT Status
        #1-Max buffer index
        #5-Current cashable amount BCD
        #5-Current restricted amount BCD
        #5-Current non-restricted amount BCD
        #5-Gaming machine transfer limit BCD
        #4-Restricted Expiration - BCD
        #2-Restricted Pool ID
        #2-CRC


        index=0
        Address=Yanit[ index : index+2]
        index=index+2

        Command=Yanit[ index : index+2]
        index=index+2

        Length=Yanit[ index : index+2]
        index=index+2

        AssetNumber=Yanit[ index : index+8]
        index=index+8

        AssetNumberInt=ReadAssetToInt(AssetNumber)
        if G_Device_AssetNo==0:
            G_Device_AssetNo=AssetNumberInt
            SQL_UpdAssetNoSMIB(AssetNumberInt)

        GameLockStatus=Yanit[ index : index+2]
        index=index+2

        AvailableTransfers=Yanit[ index : index+2]
        index=index+2

        HostCashoutStatus=Yanit[ index : index+2]
        index=index+2




        BalanceQuery_GameLockStatus=GameLockStatus
        
        GameLockStatusMeaning=""
        if GameLockStatus=="00":
            GameLockStatusMeaning="Game locked"

        if GameLockStatus=="40":
            GameLockStatusMeaning="Game lock is pending"

        if GameLockStatus=="FF":
            GameLockStatusMeaning="Game not locked"

        print("GameLockStatusMeaning: " , GameLockStatusMeaning , "GameLockStatus: ", GameLockStatus, " AvailableTransfers: ",  AvailableTransfers, "HostCashoutStatus: " , HostCashoutStatus, "G_SelectedGameId: " , G_SelectedGameId)


        AFTStatus=Yanit[ index : index+2]
        index=index+2

        MaxBufferIndex=Yanit[ index : index+2]
        index=index+2

        CurrentCashableAmount=Yanit[ index : index+10]
        index=index+10
    
        if len(CurrentCashableAmount)!=10:
            print("Bakiye yanit eksik!!!!!")
            return



        if IsDebugMachineNotExist==1:
            newrakam=random.uniform(1, 10)
            newrakamint=int(newrakam*100);
            CurrentCashableAmount=AddLeftBCD(newrakamint,5)

        Tutar=Decimal(CurrentCashableAmount)/100
    
    
        if IsWaitingForBakiyeSorgulama==0:
            return

        #2020-01-06: Savoy Mustafa ile problemi cozduk insallah. Buradan silip, bakiyeyi kabul ettigimiz yerde set edelim.
        #Yanit_BakiyeTutar=Tutar


        CurrentRestrictedAmount="00"
        if G_Machine_IsPromoAccepts==0:
            index=index+10
        else:
            CurrentRestrictedAmount=Yanit[ index : index+10]
            index=index+10
        Y_RestrictedAmount=Decimal(CurrentRestrictedAmount)/100
        

        CurrentNonrestrictedAmount="00"
        if G_Machine_IsPromoAccepts==0:
            index=index+10
        else:
            CurrentNonrestrictedAmount=Yanit[ index : index+10]
            index=index+10


        Y_NonRestrictedAmount=Decimal(CurrentNonrestrictedAmount)/100


        ChangeBalanceAmount(1,"%s %s" % (Tutar, G_Machine_Currency))
        ChangeBalanceAmount(2,"%s %s" % ((Y_RestrictedAmount+Y_NonRestrictedAmount), G_Machine_Currency))



        GamingmachineTransferLimit=Yanit[ index : index+10]
        index=index+10

        RestrictedExpiration=Yanit[ index : index+8]
        index=index+8

        RestrictedPoolID=Yanit[ index : index+4]
        index=index+4
        Yanit_RestrictedPoolID=RestrictedPoolID




        CashableAmount=0
        RestrictedAmount=0
        NonrestrictedAmount=0
        try:
            CashableAmount=Decimal(CurrentCashableAmount)/100
            RestrictedAmount=Decimal(CurrentRestrictedAmount)/100
            NonrestrictedAmount=Decimal(CurrentNonrestrictedAmount)/100

            
            try:
                G_Machine_Balance=CashableAmount
                G_Machine_Promo=RestrictedAmount
            except Exception as ebx3221:
                print("Save Bakiye sorgulama problem")




            processThread = Thread(target=SQL_InsDeviceMoneyQuery, args=(CashableAmount, RestrictedAmount, NonrestrictedAmount, Yanit,))
            processThread.name="YanitBakiyeSorg1"
            processThread.start();
        except:
            print("InsDeviceMoneyQuery x5436")

        PrintAndSetAsStatuText("Balance is received - " +  GameLockStatusMeaning,)
        print("Balance", CashableAmount, RestrictedAmount, NonrestrictedAmount)

        if IsWaitingForBakiyeSorgulama==0:
            print("*************************************************************************")
            print("*************Bakiye'yi zaten ogrendik. Cik buradan***********************")
            print("*************************************************************************")






        LastGameDiff=(datetime.datetime.now()-G_LastGame_Action).total_seconds()

        #2021-09-06: Bunu kapattim Belki ruletlerde bundan dolayi oluyor...
        #if LastGameDiff>60 and G_Machine_IsRulet==1:
        #    G_LastGame_IsFinished=1
        #    GameLockStatus="00"


        #2020-09-01 Ilk bunu yapmistik zaten. Ama Apex'lerde GameLocked gelmiyor bazen. O yuzden bunu kabul edelim.
        #Last Game Diff 60snden buyukse; cashout asamasina gecmesine izin ver.
        if G_Machine_DeviceTypeId==10 and LastGameDiff>20 and G_Machine_IsRulet==0:
            G_LastGame_IsFinished=1
            GameLockStatus="00"


        #Makina kilitlendim diyorsa; oyun da bitti olarak set et.
        if GameLockStatus=="00":
            G_LastGame_IsFinished=1

        if Cashout_Source==123:
            G_LastGame_IsFinished=1

        if GameLockStatus!="00":
            Bakiye_WaitingForGameLockCount=Bakiye_WaitingForGameLockCount+1
            #print("Bakiye_WaitingForGameLockCount", Bakiye_WaitingForGameLockCount)

        #if GameLockStatus!="00" and G_LastGame_IsFinished==1 and Bakiye_WaitingForGameLockCount>10:
        #    if Bakiye_WaitingForGameLockCount%10==1:
        #        GUI_ShowSettings()
        #        if Bakiye_WaitingForGameLockCount==11:
        #            SQL_Safe_InsImportantMessage("We could accept balance Bakiye_WaitingForGameLockCount:" + str(Bakiye_WaitingForGameLockCount),83)


        AcceptZeroBalance=False
        #20200715: Sadece normal makinalarda olsun
        if (CashableAmount==0 and RestrictedAmount==0 and G_Machine_IsRulet==0) or G_SAS_IsProblemOnCredit==1:
            AcceptZeroBalance=True
        
        #20200715: Interblocklarda da illa oyun kilitlendi mesaji gelsin olaral degisti
        #if G_Machine_DeviceTypeId==11 and Tutar<1:
        #    AcceptZeroBalance=True



        #BalanceAccepted: Amount:479.04 LastCommand_Bakiye_Sender:2 CS:0 TrustBalanceDiff:21.95442 AcceptZeroBalance:False IsBalanceQueryForInfo:0 DeviceTypeId:2 LastCommand_Bakiye_Sender:2 SelectedGameId:2 IsRulet:0
        #TrustBalanceDiff:21.95442 AcceptZeroBalance:False IsBalanceQueryForInfo:0 DeviceTypeId:2 LastCommand_Bakiye_Sender:2 SelectedGameId:2 IsRulet:0
        #print("G_SelectedGameId", G_SelectedGameId)
        G_TrustBalanceDiff=(datetime.datetime.now()-G_TrustBalance).total_seconds()
        #if LastCommand_Bakiye_Sender==1 or Cashout_Source==123 or G_TrustBalanceDiff<40  or GameLockStatus=="00" or AcceptZeroBalance==True or IsBalanceQueryForInfo==1 or (G_Machine_DeviceTypeId==6 and LastCommand_Bakiye_Sender==1) or (G_SelectedGameId==0 and G_Machine_IsRulet==0):
        if LastCommand_Bakiye_Sender==1 or Cashout_Source==123 or G_TrustBalanceDiff<40  or GameLockStatus=="00" or AcceptZeroBalance==True or IsBalanceQueryForInfo==1 or (G_Machine_DeviceTypeId==6 and LastCommand_Bakiye_Sender==1) or (G_SelectedGameId==0 and G_Machine_IsRulet==0):
            
            #if (G_LastGame_IsFinished==0 and G_Machine_DeviceTypeId==10 and IsBalanceQueryForInfo==0) and GameLockStatus!="00":
            #    GUI_ShowIfPossibleMainStatu("Lutfen oyunun bitmesini bekleyin.")
            #    print("GAME IS PLAYING. PLEASE WAIT GAME TO FINISH!")
            #    return
            
            print("BALANCE SORGU KABUL ETTIK! Tutar", Tutar, "GameLockStatus", GameLockStatus, "LastCommand_Bakiye_Sender", LastCommand_Bakiye_Sender, "Cashout_Source", Cashout_Source, "G_TrustBalanceDiff",G_TrustBalanceDiff, "AcceptZeroBalance", AcceptZeroBalance, "IsBalanceQueryForInfo", IsBalanceQueryForInfo, "G_Machine_DeviceTypeId", G_Machine_DeviceTypeId,"LastCommand_Bakiye_Sender", LastCommand_Bakiye_Sender, "G_SelectedGameId",G_SelectedGameId, "G_Machine_IsRulet", G_Machine_IsRulet, "GameId", G_SelectedGameId)

            IsWaitingForBakiyeSorgulama=0

            Yanit_BakiyeTutar=Tutar
            Yanit_RestrictedAmount=Y_RestrictedAmount
            Yanit_NonRestrictedAmount=Y_NonRestrictedAmount

            try:
                strAcceptable="BalanceAccepted: Amount:" + str(Tutar) + "/" + str(Yanit_RestrictedAmount) + " GameLockStatus:" + str(GameLockStatus) + " RealLock:"+str(BalanceQuery_GameLockStatus)+" Sender:" + str(LastCommand_Bakiye_Sender) + " CashoutSource:" +  str(Cashout_Source) + " TrustBalanceDiff:" + str(G_TrustBalanceDiff) + " AcceptZeroBalance:" + str(AcceptZeroBalance) + " IsInfo:" + str(IsBalanceQueryForInfo) + " DeviceTypeId:" + str(G_Machine_DeviceTypeId) + " GameId:" + str(G_SelectedGameId) +  " IsRulet:" + str(G_Machine_IsRulet)
                SQL_Safe_InsImportantMessage(strAcceptable,84)
            except Exception as ebx3221:
                print("InsBakiye")


            try:
                Config.set("collecting","cashableamount", str(CurrentCashableAmount))
                Config.set("collecting","restrictedamount", str(CurrentRestrictedAmount))
                Config.set("collecting","nonrestrictedamount", str(CurrentNonrestrictedAmount))
                SaveConfigFile()
                #print("******SAVE BAKIYE**********",CurrentCashableAmount)
            except Exception as ebx3221:
                print("Save Bakiye sorgulama problem")


            if Cashout_Source==123:
                GUI_ShowIfPossibleMainStatu("Balance is accepted because of cashout")
                #SQL_Safe_InsImportantMessageByWarningType("Balance is accepted because of cashout",1,1)
            
            #if G_Machine_DeviceTypeId!=7:
            #    IsWaitingForBakiyeSorgulama=0

            #if G_Machine_DeviceTypeId==7:
            #    if LastCommand_Bakiye_Sender==2:
            #        if AvailableTransfers=="02" or AvailableTransfers=="03":
            #            IsWaitingForBakiyeSorgulama=0
            #        else:
            #            print("Makina kilitlendi ama kabul etme!!!!*********************")
            #    else:
            #        IsWaitingForBakiyeSorgulama=0
        else:
            print("BALANCE GELDI AMA KABUL ETMEDIK!")

        print("G_TrustBalanceDiff", G_TrustBalanceDiff, "GameLockStatus", GameLockStatus, "Tutar", Tutar, "IsBalanceQueryForInfo", IsBalanceQueryForInfo,"G_SelectedGameId", G_SelectedGameId, "G_Machine_DeviceTypeId",G_Machine_DeviceTypeId)


        if IsBalanceQueryForInfo==0 and GameLockStatus!="00" and IsWarnedForTakeWin==0 and G_LastGame_IsFinished==0 and G_Machine_DeviceTypeId!=10:
            IsWarnedForTakeWin=1
            ShowNotifyScreen("PRESS TAKE/WIN","Lutfen Take/Win yapiniz", 15)

    except Exception as exba:
        print("Bakiye yanit okumada hata!!!")
        #ExceptionHandler("Bakiye sorgulama",exba,1)
#Yanit bakiye sorgulama bitti

    



def GetCRC(komut):
    data = bytearray.fromhex(komut)
    crcinst = CrcKermit()
    crcinst.process(data)
    CRCsi = crcinst.finalbytes().hex()
    CRCsi=str(CRCsi).replace("0x","").upper().replace("\\X","").replace("B'","").replace("<","").replace("'","")

    if len(CRCsi)==1:
        CRCsi="0%s" % (CRCsi)

    if len(CRCsi)==2:
        CRCsi="00%s" % (CRCsi)

    if len(CRCsi)==3:
        CRCsi="0%s" % (CRCsi)
    retdata="%s%s%s" % (komut, CRCsi[2:4], CRCsi[0:2])


    #print("Before CRC", komut, " After CRC" , retdata)
    return retdata




def Komut_Handpay(doincreaseid):
    try:
        global Sifirla_FirstTransaction
        global Sifirla_LastTransaction

        global G_Session_CardExitStatus
        global Global_ParaSilme_TransferStatus
        #SQL_DeviceStatu(2)
        global IsWaitingForBakiyeSifirla
        transactionid=Config.getint("payment","transactionid")
        
        if doincreaseid==1:
            transactionid=transactionid+1
            Config.set("payment","transactionid",str(transactionid))
            Config.set('collectcmd','transactionid', str(transactionid))

        #session icinde para sifirlama olayi
        if Sifirla_FirstTransaction==0:
            Sifirla_FirstTransaction=transactionid
        Sifirla_LastTransaction=transactionid
        #session icinde para sifirlama olayi

        SaveConfigFile()
        print("Para Iade Et - Sifirla: transactionid:",transactionid, " bakiye: " , Yanit_BakiyeTutar, "promo", Yanit_RestrictedAmount);


        CommandHeader=Config.get("sas","address")      #1-Address  01
        CommandHeader+="72"   #1-Command  72
        CommandHeader+=""#1-Length       55

        
        

        BakiyeTutar=int(Yanit_BakiyeTutar*100);
        RestrictedTutar=int(Yanit_RestrictedAmount*100);
        NonRestrictedTutar=int(Yanit_NonRestrictedAmount*100);

        Command=""
        Command+="00"   #1-Transfer Code    00
        Command+="00"   #1-Transfer Index   00
        Command+="80"   #1-Transfer Type    80




        print("***********Komut parasifirla Global_ParaSilme_TransferStatus", Global_ParaSilme_TransferStatus, datetime.datetime.now())
        #2020-01-23: 0 olmasi gerekiyor normalde.
        IsHandpayNeeded=1



        if IsHandpayNeeded==0:
            Command+=AddLeftBCD(BakiyeTutar,5)       #5-Cashable amount (BCD)    00 00 50 00 00 --> 5000,00 TL
            Command+=AddLeftBCD(RestrictedTutar,5)   #Command+="0000000000"                  #5-Restricted amount  (BCD)
            Command+=AddLeftBCD(NonRestrictedTutar,5) #5-Nonrestricted amount (BCD)
        else:
            Command+="0000000000"
            Command+="0000000000"
            Command+="0000000000"

        if IsHandpayNeeded==1:
            print("*******************************")
            print("Handpay'e dusur!!!!")
            print("*******************************")
            Command+="0B"               #1-Transfer flag    03
        else:
            #Command+="03"               #1-Transfer flag    03 SOFT
            Command+="07"               #1-Transfer flag    03 HARD

        
        Command+=Config.get("sas","assetnumber")          #4-Asset number     01 00 00 00
        Command+=Config.get("sas","registrationkey")   #20-Registration key
        
        
        TRANSACTIONID="".join("{:02x}".format(ord(c)) for c in str(transactionid))
        Command+=AddLeftBCD(int(len(TRANSACTIONID)/2),1)   #1-TransactionId Length        03
        Command+=TRANSACTIONID #X-TransactionID ( Max:20)     

        #sifirla
        Command+=(datetime.datetime.now()+datetime.timedelta(days=5)).strftime("%m%d%Y")    #4-ExpirationDate (BCD) MMDDYYYY            05 30 20 16
        Command+="0030"         #2-Pool ID                                0C 00
        Command+="00"           #1-Receipt data length                      00

        

        Command+=""             #X-Recepipt Data
        Command+=""         #2-Lock Timeout - BCD
        CommandHeader+=hex(int(len(Command)/2)).replace("0x","")
        Command+=""             #2-CRC



        GenelKomut="%s%s" % (CommandHeader, Command)
        GenelKomut=GetCRC(GenelKomut)
        print("SAS TX Cashout", GenelKomut)


        SAS_SendCommand("Handpay",GenelKomut,1)
    except Exception as e:
        ExceptionHandler("Komut_Handpay",e,1)


Last_Draw_BakiyeTutar=0
Last_Draw_RestrictedAmount=0
Last_Draw_NonRestrictedAmount=0
Last_ParaSifirlaDate=datetime.datetime.now()
#2021-07-20
def Komut_ParaSifirla(doincreaseid):
    try:
        global G_Config_IsCashoutSoft
        global Sifirla_FirstTransaction
        global Sifirla_LastTransaction
        global Yanit_RestrictedPoolID
        
        global Global_ParaSifirla_84

        global Last_Draw_BakiyeTutar
        global Last_Draw_RestrictedAmount
        global Last_Draw_NonRestrictedAmount

        global Last_ParaSifirlaDate
        Last_ParaSifirlaDate=datetime.datetime.now()

        global G_Session_CardExitStatus
        global Global_ParaSilme_TransferStatus
        #SQL_DeviceStatu(2)
        global IsWaitingForBakiyeSifirla
        global Yanit_BakiyeTutar
        if (Yanit_BakiyeTutar==0 and Yanit_RestrictedAmount==0 and Yanit_NonRestrictedAmount==0)==True:
            IsWaitingForBakiyeSifirla=0
            SQL_Safe_InsImportantMessage("Cashout is completed. 0 Balance",88)
            print("Zaten parasi yok")

            if Yanit_BakiyeTutar==0 and Yanit_RestrictedAmount==0 and Yanit_NonRestrictedAmount==0:
                return

        transactionid=Config.getint("payment","transactionid")
        
        if doincreaseid==1:
            transactionid=transactionid+1
            Config.set("payment","transactionid",str(transactionid))
            Config.set('collectcmd','transactionid', str(transactionid))
            try:
                Last_Draw_BakiyeTutar=Yanit_BakiyeTutar
                Last_Draw_RestrictedAmount=Yanit_RestrictedAmount
                Last_Draw_NonRestrictedAmount=Yanit_NonRestrictedAmount
            except Exception as eDraw:
                print("Olmaz")


        SQL_Safe_InsImportantMessage("AFT Cash-Out TransactionId: " + str(transactionid) + "-" + str(doincreaseid),0)

        #session icinde para sifirlama olayi
        if Sifirla_FirstTransaction==0:
            Sifirla_FirstTransaction=transactionid
        Sifirla_LastTransaction=transactionid
        #session icinde para sifirlama olayi

        if doincreaseid==1:
            SaveConfigFile()
        print("Para Iade Et - Sifirla: transactionid:",transactionid, " bakiye: " , Yanit_BakiyeTutar, "promo", Yanit_RestrictedAmount);


        CommandHeader=Config.get("sas","address")      #1-Address  01
        CommandHeader+="72"   #1-Command  72
        CommandHeader+=""#1-Length       55

        
        

        BakiyeTutar=int(Yanit_BakiyeTutar*100);
        RestrictedTutar=int(Yanit_RestrictedAmount*100);
        NonRestrictedTutar=int(Yanit_NonRestrictedAmount*100);

        Command=""
        Command+="00"   #1-Transfer Code    00
        Command+="00"   #1-Transfer Index   00
        Command+="80"   #1-Transfer Type    80



        print("***********Komut parasifirla Global_ParaSilme_TransferStatus", Global_ParaSilme_TransferStatus, datetime.datetime.now())
        #2020-01-23: 0 olmasi gerekiyor normalde.
        IsHandpayNeeded=0
        #Simdilik 87'yi kaldirdim.
        #if Global_ParaSilme_TransferStatus=="84" or Global_ParaSilme_TransferStatus=="82" or Global_ParaSilme_TransferStatus=="86" or Global_ParaSilme_TransferStatus=="83":
        if Global_ParaSilme_TransferStatus=="84" and Global_ParaSifirla_84%5==0:
            G_Session_CardExitStatus=1
            IsHandpayNeeded=1
            SQL_InsImportantMessageByWarningType("Para silinemiyor. Makina handpay'e dusurulmeye calisilacak",1,1)


        if IsHandpayNeeded==0:
            Command+=AddLeftBCD(BakiyeTutar,5)       #5-Cashable amount (BCD)    00 00 50 00 00 --> 5000,00 TL
            Command+=AddLeftBCD(RestrictedTutar,5)   #Command+="0000000000"                  #5-Restricted amount  (BCD)
            Command+=AddLeftBCD(NonRestrictedTutar,5) #5-Nonrestricted amount (BCD)
        else:
            Command+="0000000000"
            Command+="0000000000"
            Command+="0000000000"

        if IsHandpayNeeded==1:
            print("*******************************")
            print("Handpay'e dusur!!!!")
            print("*******************************")
            Command+="0B"               #1-Transfer flag    03
        else:
            #Command+="03"              #1-Transfer flag    0F kullanabiliriz aslinda.
            #Command+="00"               #1-Transfer flag    EGT'nin gonderdigi seyde 00 yaziyordu. deneyeelim 2021-07-08
            

            #cashout mode: hard olmali. 1 olmali.
            if G_Config_IsCashoutSoft==1:
                #Apexlerde 3 olacak
                Command+="03"                        #1-Transfer flag    cashout mode soft:
            else:
                #07 Olunca apexlerde problem yapiyor!!!
                Command+="0F"              #1-Transfer flag    0F Rulet test et..
            




        
        
        Command+=Config.get("sas","assetnumber")          #4-Asset number     01 00 00 00
        Command+=Config.get("sas","registrationkey")   #20-Registration key
        
        
        TRANSACTIONID="".join("{:02x}".format(ord(c)) for c in str(transactionid))
        Command+=AddLeftBCD(int(len(TRANSACTIONID)/2),1)   #1-TransactionId Length        03
        Command+=TRANSACTIONID #X-TransactionID ( Max:20)     

        #sifirla
        #Command+=(datetime.datetime.now()+datetime.timedelta(days=5)).strftime("%m%d%Y")    #4-ExpirationDate (BCD) MMDDYYYY            05 30 20 16
        Command+="00000000"#ExpirationDate (BCD) 
        if len(Yanit_RestrictedPoolID)!=4:
            Yanit_RestrictedPoolID="0030"

        #Command+="0030"         #2-Pool ID                                0C 00
        Command+=Yanit_RestrictedPoolID

        Command+="00"           #1-Receipt data length                      00

        

        Command+=""             #X-Recepipt Data
        Command+=""         #2-Lock Timeout - BCD
        CommandHeader+=hex(int(len(Command)/2)).replace("0x","")
        Command+=""             #2-CRC



        GenelKomut="%s%s" % (CommandHeader, Command)
        GenelKomut=GetCRC(GenelKomut)
        print("SAS TX Cashout", GenelKomut)


        SAS_SendCommand("Cashout",GenelKomut,1)
    except Exception as e:
        ExceptionHandler("Komut_ParaSifirla",e,1)

    
Cashout_ImpossibleWrongTransaction=0
def Yanit_ParaSifirla(Yanit):
    #2020-09-08
    try:
        global Cashout_ImpossibleWrongTransaction
        global IsWaitingForBakiyeSifirla
        global G_SAS_Transfer_Warning_DoorIsLocked
        global WaitingParaSifirla_PendingCount
        global Global_ParaSilme_TransferStatus

        global Sifirla_Bakiye
        global Sifirla_Promo

        global Global_ParaSifirla_84

        global Yanit_BakiyeTutar
        global Yanit_RestrictedAmount
        global Yanit_NonRestrictedAmount

        index=0
        Address=Yanit[ index : index+2]
        index=index+2

        Command=Yanit[ index : index+2]
        index=index+2

        Length=Yanit[ index : index+2]
        index=index+2

        TransactionBuffer=Yanit[ index : index+2]
        index=index+2

        
        TransferStatus=Yanit[ index : index+2]#Table 8.3e
        index=index+2
        TransferStatusReal=TransferStatus

        print("First Para silme yanit TransferStatus:", TransferStatus)
        if TransferStatus=="":
            print("Parasifirla response length is not enough")
            Komut_Interragition("Not enough length!")
            return


        if IsWaitingForBakiyeSifirla==0:
            print("%s %s" % ("MoneyErase Message already came before" , TransferStatus))
            #PrintAndSetAsStatuText("%s %s" % ("MoneyErase Message already came before" , TransferStatus))
            return

        ReceiptStatus=Yanit[ index : index+2]
        index=index+2

        TransferType=Yanit[ index : index+2]
        index=index+2

        CashableAmount=Yanit[ index : index+10]
        index=index+10



        RestrictedAmount="00"
        NonrestrictedAmount="00"

        if G_Machine_IsPromoAccepts==0:
            index=index+10
            index=index+10
        else:
            RestrictedAmount=Yanit[ index : index+10]
            index=index+10

            NonrestrictedAmount=Yanit[ index : index+10]
            index=index+10




        TransferFlag=Yanit[ index : index+2]
        index=index+2

        AssetNumber=Yanit[ index : index+8]
        index=index+8


        TransactionId=0
        TransactionIdLength=0

        try:
            TransactionIdLength=int(Yanit[ index : index+2])*2
            index=index+2
    
            TransactionIdF=Yanit[ index : index+TransactionIdLength]
            TransactionId=HEXNumberToInt(TransactionIdF)
            index=index+TransactionIdLength
        except Exception as eTransactionId:
            index=index
            #print("Gelen Yanit cok kucuk! Buyuk bi ihtimal Merkur")



        if G_Machine_DeviceTypeId==6:
            try:
                testint=int(TransactionId)
            except Exception as eTransactionId:
                print("TransactionId sacma bisi geldi....")
                Komut_Interragition("Megajack")
                Komut_ParaSifirla(0)
                return
      
        print("TransactionId", TransactionId, "Sifirla_FirstTransaction", Sifirla_FirstTransaction, "Sifirla_LastTransaction", Sifirla_LastTransaction )


        if len(TransferType)>0 and TransferType!="80" and int(TransactionId)>0:
            print("***********************************************************************************")
            print("***********************************************************************************")
            print("ParaSifirlama islemine cash-in geldi. Tekrardan para sifirlama komutu gonder")
            Komut_ParaSifirla(0)
            #SQL_Safe_InsImportantMessage("ParaSifirlama islemine cash-in geldi. Tekrardan para sifirlama komutu gonder!",85)

        if 1==1 and int(TransactionId)>0:
            if (int(TransactionId)>=int(Sifirla_FirstTransaction) and int(TransactionId)<=int(Sifirla_LastTransaction))==False:
                print("**********************Impossible! Wrong transaction Id!!!!",Sifirla_FirstTransaction,TransactionId ,Sifirla_LastTransaction)
                TransferStatus="40"

                #2020-07-17 Savoy
                Cashout_ImpossibleWrongTransaction=Cashout_ImpossibleWrongTransaction+1
                if Cashout_ImpossibleWrongTransaction%5==0:
                    print("*******************************************")
                    print("TEKRAR PARA SILME KOMUTU GONDER!!!!")
                    Komut_ParaSifirla(0)
                    print("*******************************************")

                #if Cashout_ImpossibleWrongTransaction%5==0:
                #    Komut_Interragition("ImpossibleWrongTransaction Spark")

                #SQL_InsImportantMessageByWarningType("Impossible.. Wrong transaction id on cashout",18,18)
                #2018-01-02'de actim
                #SQL_InsImportantMessageByWarningType("Wrong Transaction! F: %s L: %s Current: %s" % (int(Sifirla_FirstTransaction), int(Sifirla_LastTransaction), int(TransactionId)),18,0)#Warning type 18 idi...
                


        Temp_Bakiye=Decimal(Yanit[14:24])/100
        Temp_Promo=(Decimal(Yanit[24:34])/100)+(Decimal(Yanit[34:44])/100)




        Amounts=""
        try:
            Amounts=Amounts + " ("
            Amounts=Amounts + "C:" + Yanit[14:24]
            Amounts=Amounts + " P:" + Yanit[24:34]
            Amounts=Amounts + ")"
        except Exception as eAmounts:
            print("Err on get amounts")

        print("Para silme yanit TransferStatus:", TransferStatus)
        
        SQL_InsImportantMessage("Cashout Transfer Status:" + str(TransferStatus),68)

        Global_ParaSilme_TransferStatus=TransferStatus
        if TransferStatus=="81":
            
            #2020-01-19
            if (int(TransactionId)>=int(Sifirla_FirstTransaction) and int(TransactionId)<=int(Sifirla_LastTransaction))==True:
                IsSendDrawCommandAgain=1
                Sifirla_Bakiye=Temp_Bakiye
                Sifirla_Promo=Temp_Promo

                EkInfo="D"
                try:
                    EkInfo="Draw: " + str(Last_Draw_BakiyeTutar) + "-"+ str(Last_Draw_RestrictedAmount) + "-"+ str(Last_Draw_NonRestrictedAmount)
                except Exception as eDraw:
                    print("Ek Info Err")

                SQL_Safe_InsImportantMessage("Cashout is completed by 81, But it is our transaction id C:" + str(Sifirla_Bakiye) + " P:" + str(Sifirla_Promo) + " " + Amounts + EkInfo,86)
                print("*******************************************************************")
                print("81 GELDI. AMA BIZIM TRANSACTION ARALIGINDA KABUL ET!!!!!")
                print("*******************************************************************")
                Wait_Bakiye(2,0,"parasifirla-81")
                if Yanit_BakiyeTutar==0:
                    time.sleep(1)
                    TransferStatus="00"
                    SQL_Safe_InsImportantMessage("Cashout is completed by 81, WE ACCEPTED TRANSID. Balance less than 1" + EkInfo,87)
                    Yanit_BakiyeTutar=Sifirla_Bakiye
                    Yanit_RestrictedAmount=Sifirla_Promo

                    #2021-06-07: Artik malfunction tarih olacak insallah
                    Yanit_BakiyeTutar=Last_Draw_BakiyeTutar
                    Yanit_RestrictedAmount=Last_Draw_RestrictedAmount+Last_Draw_NonRestrictedAmount
                    
                    #2021-08-02 Yukaridaki gibi yapmis olmama ragmen hala DB'ye Yanit_BakiyeTutar 0 olarak gidiyor
                    IsSendDrawCommandAgain=0
                    SQL_Safe_InsImportantMessage("Amount Info:" + str(Yanit_BakiyeTutar) + " / "  + EkInfo,87)
                else:
                    SQL_InsImportantMessageByWarningType("Lutfen son session kontrolu yapiniz. TransactionId not unique",1,1)
            
            
            #2020-01-12
            Komut_Interragition("Novomatic!!")
            

            PrintAndSetAsStatuText("%s %s" % ("Cant erase money. Collect Money: TransID is not unique T:" , TransferStatus))
            SQL_InsImportantMessage("%s %s" % ("Collect Money: TransID is not unique T:" , TransferStatus),9)
            
            #Tekrardan sifirla diyince 
            if IsSendDrawCommandAgain==1:
                Komut_ParaSifirla(1)

        if TransferStatus=="00" or (G_Machine_DeviceTypeId==6 and TransferStatus=="01"):
            print("Para sifirla yanit geldi" , TransferStatus)



            try:
                if G_Machine_IsRulet==1 and 2==2:
                    if Yanit_BakiyeTutar!=Temp_Bakiye:
                        SQL_Safe_InsImportantMessage("Roulette balances are different: B: " + str(Yanit_BakiyeTutar) + " C:" + str(Temp_Bakiye),68)
                    Yanit_BakiyeTutar=Temp_Bakiye
                    Yanit_RestrictedAmount=Temp_Promo
            except Exception as eAmounts:
                print("Err on get amounts")

            if (int(TransactionId)>=int(Sifirla_FirstTransaction) and int(TransactionId)<=int(Sifirla_LastTransaction))==True:
                print("**********************GERCEK PARA SIFIRLAMA GELDI!!!!",Sifirla_FirstTransaction,TransactionId ,Sifirla_LastTransaction)
                IsWaitingForBakiyeSifirla=0
                SQL_Safe_InsImportantMessage("Cashout is completed." + Amounts + " Statu:" + TransferStatusReal,88)
                
                Sifirla_Bakiye=Temp_Bakiye
                Sifirla_Promo=Temp_Promo

                #2021-08-29
                #2021-09-28 bunun hic bi anlami yok aq... niye yapmisim ki?
                #2021-09-28 Yok yok iyi yapmisim. Bi tek promoyu eklememisim IF'te.. Ondan dolayi.
                #Temp_Bakiye==0 and Temp_Promo==0: 
                if TransferStatusReal=="00" and Yanit[14:24]=="0000000000" and Yanit[24:34]=="0000000000":
                    #2021-09-27.. Yukarida bunu niye yaptik acaba? Eyup bak. Transfer status: 00 R:00 Cash: 0
                    SQL_Safe_InsImportantMessage("Transfer status: "+ TransferStatus + " R:" + TransferStatusReal+" Cash: 0 TempB:" + str(Temp_Bakiye) + "TempP:" + str(Temp_Bakiye) + " Amounts:" + Amounts,88)
                    SQL_Safe_InsImportantMessage("LogSAS:" + str(Yanit),88)
                    Yanit_BakiyeTutar=0
                    Yanit_RestrictedAmount=0
                    Yanit_NonRestrictedAmount=0
            else:
                print("FAKE TRANSACTION ID! Impossible!!!")
                TransferStatus="40"
            

            if G_Machine_DeviceTypeId==6:
                print("Megajack CashableAmount:", CashableAmount)

            cashableamount=Decimal(Config.get("collecting","cashableamount"))/100

            Config.set("collecting","cashableamount", str(CashableAmount))
            Config.set("collecting","restrictedamount", str(RestrictedAmount))
            Config.set("collecting","nonrestrictedamount", str(NonrestrictedAmount))
            SaveConfigFile()
            print("Sifirla Yanit:" , (Decimal(CashableAmount)/100),(Decimal(RestrictedAmount)/100),(Decimal(NonrestrictedAmount)/100))
            
            try:
                receivedcashableamount=Decimal(CashableAmount)/100

                if cashableamount!=receivedcashableamount and 2==1:
                    print("********************************************")
                    PrintAndSetAsStatuText("receivedcashableamount is less. Log: %s Received: %s" % (cashableamount, receivedcashableamount))
                    print("********************************************")
                    SQL_InsImportantMessage("receivedcashableamount is less. Log: %s Received: %s" % (cashableamount, receivedcashableamount),1)
            except Exception as ebx322:
                print("transactionid problem")

        elif TransferStatus=="40":
            Komut_Interragition("EraseMoney")
            
            

            #2021-11-22 Apex Ilyas
            try:
                if G_Machine_DeviceTypeId==10:
                    Last80=int((datetime.datetime.now()-G_Last_80).total_seconds() * 1000)
                    Last81=int((datetime.datetime.now()-G_Last_81).total_seconds() * 1000)
                    EkInfo=" 80(" + str(Last80) + ")/" + "81(" + str(Last81) + ")"
                    SQL_Safe_InsImportantMessage("Erase money is pending " + str(Sas_LastSent) + EkInfo, 93)
            except Exception as esql1:
                print("APEX ERR")


            PrintAndSetAsStatuTextWithLevel("%s %s" % ("Erase money is pending. T:" , TransferStatus),10)
            WaitingParaSifirla_PendingCount=WaitingParaSifirla_PendingCount+1
            


            if WaitingParaSifirla_PendingCount%10==0:
                SQL_InsImportantMessage("Restart SAS Port",0)
                OpenCloseSasPort(1,0)
                Komut_Interragition("EraseMoney")

            #if WaitingParaSifirla_PendingCount%12==0:
            #    SQL_InsImportantMessage("Restart because of many 40 - Pending",0)
            #    ExecuteCommand("restart")

            #if G_Machine_DeviceTypeId==8 and WaitingParaSifirla_PendingCount%4==0:
            #    time.sleep(0.05)
            #    GUI_ShowIfPossibleMainStatu("Bally special interrogation")
            #    Komut_Interragition("Bally!!")
            #    time.sleep(0.05)

        else:
            if TransferStatus=="87":

                if G_SAS_Transfer_Warning_DoorIsLocked==0 or G_SAS_Transfer_Warning_DoorIsLocked%5==0:
                    G_SAS_Transfer_Warning_DoorIsLocked=G_SAS_Transfer_Warning_DoorIsLocked+1
                    SQL_InsImportantMessageByWarningType("Door is opened, slot tilt or disabled! Can't erase money! Please close machine's door! Statu: 87",1,17)
                    GUI_ShowIfPossibleMainStatu("Door is opened or slot tilt")

                Komut_Interragition("87")
                PrintAndSetAsStatuTextWithLevel("%s %s" % ("Cant erase money. Door is open, disabled or cashout in progress T:" , TransferStatus),12)
                Komut_ParaSifirla(1)#2019-02-11 burasi 0 idi, 1 yaptim

                time.sleep(0.1)
            elif TransferStatus=="9F":
                Wait_Bakiye(7,0,"parasifirla-9f")
                PrintAndSetAsStatuTextWithLevel("%s %s" % ("Cant erase money. Unexpected Error T:" , TransferStatus),12)
                SQL_InsImportantMessage("%s %s" % ("Cant erase money. Unexpected Error T:" , TransferStatus),9)
                Komut_ParaSifirla(1)
            elif TransferStatus=="82" or TransferStatus=="86":
                time.sleep(0.1)
                PrintAndSetAsStatuTextWithLevel("%s %s" % ("Cant erase money. Partial Transfers are not supported. T:" , TransferStatus),12)
                Wait_Bakiye(8,0,"parasifirla-82")
                Komut_ParaSifirla(1)
            elif TransferStatus=="84":
                Global_ParaSilme_TransferStatus=TransferStatus
                print("Global_ParaSilme_TransferStatus", Global_ParaSilme_TransferStatus)
                SQL_InsImportantMessage("%s %s" % ("Cant erase money. Money is bigger than current balance. T:" , TransferStatus),9)
                PrintAndSetAsStatuTextWithLevel("%s %s" % ("Cant erase money. Money is bigger than current balance. T:" , TransferStatus),12)
                Global_ParaSifirla_84=Global_ParaSifirla_84+1
                Wait_Bakiye(1,1,"84")
                Komut_ParaSifirla(1)
                Komut_Interragition("84")
            elif TransferStatus=="C0":
                Komut_Interragition("C0")
            elif TransferStatus=="83":
                PrintAndSetAsStatuText("%s %s" % ("Cant erase money. Transfer amount is not bcd. T:" , TransferStatus))
                Wait_Bakiye(10,0,"parasifirla-83")
                Komut_ParaSifirla(1)
            elif TransferStatus=="94":
                Komut_BakiyeSorgulama(2,0,"Sifirla:S94")
                PrintAndSetAsStatuText("%s%s" % ('Gaming machine not locked for transfer Statu: ', TransferStatus))
                SQL_Safe_InsImportantMessageByWarningType("%s%s" % ('Gaming machine not locked for transfer. Statu: ', TransferStatus),0,1)
                time.sleep(1)
            else:
                GUI_ShowIfPossibleMainStatu("%s %s" % ("Cant erase money. TransferStatus:" , TransferStatus))
                PrintAndSetAsStatuTextWithLevel("%s %s" % ("Cant erase money. TransferStatus:" , TransferStatus),12)


    except Exception as e:
        ExceptionHandler("Error: Yanit_ParaSifirla",e,1)










def RemoveCustomerInfoOnConfig():
    Config.set('customer','cardnumber', '')
    Config.set('customer','customerid', "0")
    Config.set('customer','customername', '')
    Config.set('customer','nickname', '')
    Config.set('customer','iscardinside', "0")
    Config.set('customer','playcount', "0")
    Config.set('customer','totalbet', "0")
    Config.set('customer','totalwin', "0")
    Config.set('customer','bonuspercentage', "0")
    Config.set('customer','currentbonus', "0")
    Config.set('customer','earnedbonus', "0")

    Config.set('customer','customerbalance', "0")
    Config.set('customer','currentbalance', "0")
    Config.set('customer','customerpromo', "0")
    Config.set('customer','currentpromo', "0")

    if G_Machine_IsCanPlayWithoutCard==1:
        Config.set('customer','cardmachinelogid', "0")
    
    SaveConfigFile()

Step_CardExit=""
#sender: 0: realcard exit, 1:removecardcommand, 2: Cant upload money, 123: cashout button is pressed
def SQL_CardExit(sender):
    print("sender", sender)
    try:
        global G_LastCardExit
        global Yanit_BakiyeTutar
        global G_Machine_ReservationDate

        CardMachineLogId=0
        CardMachineLogId=Config.getint('customer','cardmachinelogid')

        try:
            cardmachinelogid=G_CardMachineLogId
        except Exception as eCardLogId:
            ExceptionHandler("cardmachinelogid",eCardLogId,0)

        playcount=0
        playcount=Config.getint('customer','playcount')

        totalbet=Decimal(Config.get("customer","totalbet"));
        totalwin=Decimal(Config.get("customer","totalwin"));

        userid=0

        global IsCardInside
        global G_User_CardNo




        EarnedBonus="0"
        try:
            EarnedBonus=str(Config.get("customer","earnedbonus"))
        except Exception as ebs:
            EarnedBonus="0"

        print("EarnedBonus", EarnedBonus)

        BakiyeTutar=Yanit_BakiyeTutar
        BakiyePromo=Yanit_RestrictedAmount+Yanit_NonRestrictedAmount

        if G_Machine_DeviceTypeId==6 and 2==3:
            BakiyeTutar=Sifirla_Bakiye
            BakiyePromo=Sifirla_Promo

        # Original MSSQL procedure: tsp_CardExit
        result = db_helper.execute_database_operation(
            'tsp_cardexit',  # PostgreSQL lowercase name
            [CardMachineLogId, G_Machine_Mac, G_User_CardNo, BakiyeTutar, playcount, userid, totalbet, totalwin, BakiyePromo, G_SAS_IsProblemOnCredit, EarnedBonus, G_Session_CardExitStatus]
        )

        print("CardMachineLogId:", CardMachineLogId, "BakiyeTutar", BakiyeTutar)

        for row in result:
           
            if row['Result']==True:

                SQL_Safe_InsImportantMessage("#" +str(CardMachineLogId)+ " Session ended C:" + str(BakiyeTutar) + " P:" +  str(BakiyePromo),89)


                print("Successfully db card exit is ok")
                if G_Machine_IsCanPlayWithoutCard==0:
                    Komut_DisableBillAcceptor("card exit ok success")
                else:
                    Komut_EnableBillAcceptor()
            else:
                try:
                    if int(row["ErrorMessageCode"])==-1:
                        IsCardInside=0
                        G_User_CardNo=""
                        RemoveCustomerInfoOnConfig()
                        CloseCustomerInfo()
                        SQL_Safe_InsImportantMessageByWarningType("ErrCode: No need for card exit again, IsCardInside=0", 66,0)
                except Exception as ex896:
                    print("Problem...")

                
                try:
                    PrintAndSetAsStatuText(row['ErrorMessage'])
                    SQL_InsImportantMessage(row['ErrorMessage'],66)
                    time.sleep(1)
                except Exception as ex896:
                    print("Problem On Insert Msg x524")

            if row['Result']==True:

                ##burada belki bakiye sorgulatabiliriz.
                try:

                    #Komut_DisableBillAcceptor("Card exit disable again")
                    DoCheckMoneyQueryAgain=True

                    if G_Machine_IsCashless==0:
                        DoCheckMoneyQueryAgain=False

                    #2018-12-30 Gerek yok artik.
                    DoCheckMoneyQueryAgain=False


                    if G_Machine_IsCashless==1 and IsDebugMachineNotExist==0:
                        try:
                            Wait_Bakiye(2,1,"cardexit1")
                            if Yanit_BakiyeTutar>0:
                                time.sleep(0.2)
                                Wait_Bakiye(2,1,"cardexit2")
                                if Yanit_BakiyeTutar>1:
                                    SQL_Safe_InsImportantMessageByWarningType("2nd Money is still existed after card out. Current Balance %s" % (Yanit_BakiyeTutar),20,6)

                                    if G_SAS_IsProblemOnCredit==1:
                                        Wait_ParaSifirla()


                                    #2021-11-19: Makinalarda kalan para, onceki cashout problemsiz ise; burada cashout yap ve musterinin session'ina ekle.
                                    if 2==2 and Yanit_BakiyeTutar>1 and G_Machine_DeviceTypeId==10 and Global_ParaSilme_TransferStatus=="00":
                                        print("Yap islemini!")
                                        SQL_Safe_InsImportantMessageByWarningType("Amount which is left from EGM " + str(Yanit_BakiyeTutar),1,0)
                                        Wait_Bakiye(2,1,"cardexit2")

                                    if 2==2 and Yanit_BakiyeTutar>1 and G_Machine_IsRulet==0:
                                        Kilitle("Moneyexisted")
                                        SQL_Safe_InsImportantMessageByWarningType("Lutfen session son session kontrolu yapiniz. Sistem kilitlendi.",1,1)
                                        Kilitle("Moneyexisted")
                                    #if G_Machine_IsRulet==1 and 2==3:
                                    #    Wait_ParaSifirla()

                        except Exception as exCardExitBakiye:
                            ExceptionHandler("exCardExitBakiye",exCardExitBakiye,1)

                except Exception as ex85:
                    ExceptionHandler("SQL_CardExit Money query",ex85,1)
                ##burada belki bakiye sorgulatabiliriz.


                
                G_User_CardNo=""
                RemoveCustomerInfoOnConfig()
    
                
                if G_Machine_IsRulet==0 and G_Machine_IsCanPlayWithoutCard==0:
                    Komut_DisableBillAcceptor("sql_cardexit isrulet=0")


                if G_Machine_LockBeforeAFT==1:
                    Ac("Yanit parasifirla novomatic")

                CloseCustomerInfo()


                #if G_Machine_NewGamingDay==1:
                #    CardReader_WaitingNewDay()
                #    Kilitle("NewGamingDayACE")
                #    GUI_ShowIfPossibleMainStatu("Locked due to new gaming day!")


                #Komut_Interragition("GetReadyForNewSession")
                G_User_CardNo=""
                G_LastCardExit=datetime.datetime.now()
                IsCardInside=0
                ChangeRealTimeReporting(1)



     
    except Exception as e:
        print("Exception SQL_CARD EXIT!!!! **********************")
        time.sleep(1)
        ExceptionHandler("SQL_CardExit", e, 1)



Step_RemoveCustomerInfo=""
Cashout_InProgress=0
Cashout_Source=0
#sender: 0: realcard exit, 1:removecardcommand, 2: Cant upload money, 3: Cashout and reserve 123: cashout button is pressed
def Card_RemoveCustomerInfo(isCardReaded):
    print("**************************************************************************")
    print("CARD EXIT STARTED!!!!")
    global G_Count_AFT_YanitHandle
    global Step_RemoveCustomerInfo
    global IsCollectButtonProcessInUse
    global Cashout_Source
    global Yanit_BakiyeTutar
    global G_Machine_ReservationDate
    global G_Machine_ReservationOK
    global Cashout_InProgress
    global Step_Parasifirla

    
    if Cashout_InProgress==1:
        SQL_Safe_InsImportantMessage("Cashout InProgress: " + Step_CardIsRemoved +"-" + Step_RemoveCustomerInfo + "-" + Step_Parasifirla,100)
        Step_RemoveCustomerInfo="1.1(Cashout InProgress)"
        print("********************************************************")
        print("Cashout is in progress! Sender", isCardReaded)
        print("********************************************************")
        return
    
    Step_RemoveCustomerInfo="1"
    Cashout_InProgress=1
    Step_RemoveCustomerInfo="2"
    if isCardReaded==123:
        Cashout_Source=isCardReaded

    try:

        if isCardReaded==123:
            print("*******************CARD EXIT STARTED BY CASHOUT BUTTON!!!!!! ")
            Komut_BakiyeSorgulama(2,0,"cardexit-started cashout-2")
            if IsCardInside==0:
                PrintAndSetAsStatuText("Cashless system is not active! CANCELLED!")
                Cashout_InProgress=0
                Step_RemoveCustomerInfo="3"
                return
            #SQL_InsImportantMessageByWarningType("Cashout button is pressed",1,1)
            


        IsCollectButtonProcessInUse=1

        Step_RemoveCustomerInfo="4"
        if G_Machine_LockBeforeAFT==1:
            Kilitle("AFT Locked")

        Step_RemoveCustomerInfo="5"
        if G_Machine_BillAcceptorTypeId>0:
            Step_RemoveCustomerInfo="6"
            BillAcceptor_Inhibit_Close()

        #2020-02-11: Savoy
        #if isCardReaded==0:
        #    EnableDisableAutoPlay(0)

        Step_RemoveCustomerInfo="7(LearnBalance)"
        Lock_StartDate=datetime.datetime.now()
        print("<OYUN KILITLENESIYE KADAR BEKLE 1!>-----------------------------------------")
        if 1==1:
            if Wait_Bakiye(2,0,"oyun kilitlenesiye-1")==0:
                PrintAndSetAsStatuText("Can't learn balance. try again")
                #SQL_InsImportantMessageByWarningType("Cant learn balance. try again",1,8)
                if Wait_Bakiye(2,0,"oyun kilitlenesiye-2")==0:
                    PrintAndSetAsStatuText("Can't learn balance. tried again")
                    #SQL_InsImportantMessageByWarningType("Cant learn balance. tried again",1,9)
                    if G_Machine_LockBeforeAFT==1:
                        Ac("Card_removecustomerinfo yok")
                    Cashout_InProgress=0
                    return
        Lock_StartDateDiff=(datetime.datetime.now()-Lock_StartDate).total_seconds()
        print("</OYUN KILITLENESIYE KADAR BEKLE 1!>-----------------------------------------", Lock_StartDateDiff)


        Step_RemoveCustomerInfo="8(LearnedBalance)"





        print("Active process: Card_RemoveCustomerInfo","G_User_CardNo", G_User_CardNo)
        Local_CardNo=G_User_CardNo

        Step_RemoveCustomerInfo="9"
        if len(G_User_CardNo)==0:
            print("Kart zaten yok ki?", IsCanReturn)
            
            if G_Machine_LockBeforeAFT==1:
                Ac("Card_removecustomerinfo yok")

            SQL_InsImportantMessage("Card is not inside! But check it out %s" %(isCardReaded),2)
            if IsCanReturn==1:
                Cashout_InProgress=0
                return##problem 2016-04-05: bunu sifirlama icin yapmisim aslinda. :) 2016-04-03 problem diye yazmisim ama aslinda bu olmasi lazim. kart yoksa cikartma islemine devam etmeye gerek yok!!!!


        playcount=0
        playcount=Config.getint('customer','playcount')

        cardmachinelogid=0
        cardmachinelogid=Config.getint('customer','cardmachinelogid')

        try:
            cardmachinelogid=G_CardMachineLogId
        except Exception as eCardLogId:
            ExceptionHandler("cardmachinelogid",eCardLogId,0)

        if G_SAS_IsProblemOnCredit==1:
            print("G_SAS_IsProblemOnCredit", G_SAS_IsProblemOnCredit)


        #network baglantisini kontrol et.
        #IsNetworkOn=1
        #try:
        #    IPAddress=get_lan_ip()
        #    conn = pymssql.connect(host=G_DB_Host, user=G_DB_User, password=G_DB_Password, database=G_DB_Database,tds_version='7.2')
        #    conn.autocommit(True)
        #    cursor = conn.cursor(as_dict=True)
        #    cursor.callproc('tsp_InsException', (G_Machine_Mac, "NETWORK", "TEST"))
        #    #conn.commit()
        #    conn.close()
        #except Exception as e:
        #    IsNetworkOn=0
        #    print("Yapilacak birsey yok.", MethodName, exc_type, fname, exc_tb.tb_lineno)

        #if IsNetworkOn==0:
        #    print("NO NETWORK!")
        #    ShowNotifyScreen("NO NETWORK!","Please connect to server",10)
        #    SQL_Safe_InsImportantMessage("No network on cashout!",75)
        #    time.sleep(2)
        #    Cashout_InProgress=0
        #    return




        Step_RemoveCustomerInfo="10"
        Step_Parasifirla="-1"
        if 1==1:#G_Machine_IsCashless==1:# and G_SAS_IsProblemOnCredit==0
            Step_Parasifirla="0"
            Wait_ParaSifirla()

        if G_Machine_IsCashless==0:
            SQL_Safe_InsImportantMessage("System is not for cashless",75)
        
        Step_RemoveCustomerInfo="11"
        SQL_CardExit(isCardReaded)
        while IsCardInside==1:
            SQL_Safe_InsImportantMessage("Card Remove Steps - FAILED" + Step_CardIsRemoved +"-" + Step_RemoveCustomerInfo,100)
            Step_RemoveCustomerInfo="12-SQLExit"
            SQL_CardExit(isCardReaded)

        
        Step_RemoveCustomerInfo="13.1"
        GetMeter(0,"removecard")
        Step_RemoveCustomerInfo="13.2"

        Yanit_BakiyeTutar=0

        if G_Machine_LockBeforeAFT==1:
            Ac("Card_removecustomerinfo")

        Step_RemoveCustomerInfo="14"

        IsCollectButtonProcessInUse=0
        PrintAndSetAsStatuTextWithLevel("Ready for new customer!",20)

        Step_RemoveCustomerInfo="15"
        if G_Machine_IsCanPlayWithoutCard==0:
            Komut_DisableBillAcceptor("remove customercardinfo")

        Komut_CancelBalanceLock()

        Step_RemoveCustomerInfo="16"
        

        
        Komut_DisableBillAcceptor("Card_RemoveCustomerInfo - 1")

        if G_Machine_IsRulet==1 and G_Machine_IsCanPlayWithoutCard==0:
            Komut_DisableBillAcceptor("remove customer info rulet")
        time.sleep(0.2)

        Step_RemoveCustomerInfo="17"




        Step_RemoveCustomerInfo="18"

        GUI_ShowIfPossibleMainStatu("")
        Step_RemoveCustomerInfo="19"

        CardReader_CardExitEnd()
        Step_RemoveCustomerInfo="20"
        if G_Machine_CardReaderModel=="Eject":
            CardReader_EjectCard()
        CardReader_CardExitEnd()

        Step_RemoveCustomerInfo="21"
        Step_RemoveCustomerInfo="22"
        Cashout_InProgress=0
        Step_RemoveCustomerInfo="23"

        thread1 = Thread(target = SQL_CheckSystemAfterCardExit, args = (cardmachinelogid, ))
        thread1.name="ChkSystemAfterExit"
        thread1.start()
        Step_RemoveCustomerInfo="24"

        #<Reservation>-----------------------------------------------------
        G_Machine_ReservationOK=""
        if len(G_Machine_ReservationCard)>0:
            if G_Machine_ReservationCard==Local_CardNo:
                ReservationDiff=(datetime.datetime.now() - G_Machine_ReservationDate).total_seconds()
                if ReservationDiff>0 and ReservationDiff<30:
                    G_Machine_ReservationOK="OK"
                    Kilitle("Reservation")
                    PrintAndSetAsStatuText("GM is reserved for " + G_Machine_ReservationCustomername)
                else:
                    G_Machine_ReservationDate=datetime.datetime.now() - datetime.timedelta(minutes=30)
        #</Reservation>-----------------------------------------------------


        Step_RemoveCustomerInfo="100"


    #except (NameError,),e:
    #    print re.findall("Card_RemoveCustomerInfo name '(\w+)' is not defined",str(e))[0]
    except Exception as e:
        print("************ Exception!!!!!!!!!!!!")
        Cashout_InProgress=0
        ExceptionHandler("Card_RemoveCustomerInfo",e,1)




def SyncDB():
    try:
        global c
        TotalRow=0
        TotalSynced=0
        InsertedIds=""
        for row in c.execute('SELECT * FROM billacceptor'):
            TotalRow=TotalRow+1

            billacceptorid=row[0]
            cardmachinelogid=row[1]
            cardno=row[2]
            amount=row[3]
            amountcode=row[4]
            countrycode=row[5]
            piece=row[6]
            amountBase=row[8]

            IsSynced=SQL_InsBillAcceptorMoneyEFT(cardmachinelogid, cardno, amount, amountcode, countrycode, piece, 1,1,amountBase)
            if IsSynced>0:
                if len(InsertedIds)>0:
                    InsertedIds=InsertedIds+","
                InsertedIds=InsertedIds+str(billacceptorid)
                c.execute("delete from billacceptor where billacceptorid=" + str(billacceptorid))
                conn.commit()
                print("Bu kayiti sil")
                TotalSynced=TotalSynced+1
            print("Billacceptorid", row[0])

        #if TotalSynced>0:
        #    c.execute("update billacceptor set issynced=1 where billacceptorid in (" + InsertedIds + ")")
        #    conn.commit()
        print("Bill acceptor Sync Finished! TotalRow" , TotalRow  , " TotalSynced" , TotalSynced, " InsertedIds" , InsertedIds )

    except Exception as e1tmr:
        print("Sync DB failed!")
        ExceptionHandler("SyncDB Failed",e1tmr,1)
#enddef SyncDB():



def CheckAndRestartPorts(sender):
    try:
        global cardreader
        global sasport
        global billacceptorport
        global G_SASLastDate

        Last_G_SASLastDate_Diff=(datetime.datetime.now()-G_SASLastDate).total_seconds()
        LastCardreaderTimeDiff=(datetime.datetime.now()-G_Machine_LastCardreaderTime).total_seconds()
        LastBillAcceptorTimeDiff=(datetime.datetime.now()-G_Machine_LastBillAcceptorTime).total_seconds()

        if sender=="sas" or sender=="cmd":
            print("sender", sender)
            #try:
            #    print(ExecuteLinuxCommand("sudo usbreset 'FT232R USB UART'"))
            #except Exception as ePorts:
            #    print("SAS")

            #try:
            #    print(ExecuteLinuxCommand("sudo usbreset 'TDO-USB-Touch-V1000'"))
            #except Exception as ePorts:
            #    print("TOUCH")

            #try:
            #    print(ExecuteLinuxCommand("sudo usbreset 'CP2102 USB to UART Bridge Controller'"))
            #except Exception as ePorts:
            #    print("CARD")

            #time.sleep(3)

        SystemCPUCheck(-1)


        #ilyas
        YeniPortlar="PORTS SAS: " + str(Last_G_SASLastDate_Diff) + " P:" + sasport.port + " - CR: ("+str(LastCardreaderTimeDiff)+")" + cardreader.port + ""
        try:
            if G_Machine_BillAcceptorTypeId>0:
                YeniPortlar=YeniPortlar + " - BA: ("+str(LastBillAcceptorTimeDiff)+")" + billacceptorport.port 
        except Exception as e1tmr:
            print("Spark 1", e1tmr)
        
        print("YeniPortlar", YeniPortlar)

        YeniPortlar=YeniPortlar+";NewPorts"

        try:
            output = str(subprocess.check_output("ls /dev/ttyUSB*", shell=True))
            output=output.replace("b'","").replace("'","").replace("\\n","|")
            for row in output.split('|'):
                if len(row)==0:
                    break
                YeniPortlar+=row + "|"
        except Exception as e1tmr:
            print("Spark-2", e1tmr)

        YeniPortlar=YeniPortlar+"sender:" + sender
        if sender=="bill":
            YeniPortlar=YeniPortlar+" Bill:" + Last_Billacceptor_Message + "-" + Last_Billacceptor_Message_Handle
        print("Check ports!" + YeniPortlar)
        SQL_InsImportantMessage(YeniPortlar,0)
    except Exception as e1tmr:
        print("OK!!!")

    try:
        print("<FIND NEW PORTS>-------------------------")
        try:
            if sender=="card" or sender=="cmd":
                cardreader.close()
        except:
            print("Card reader port close error")
        
        try:
            if sender=="sas" or sender=="cmd":
                sasport.close()
        except:
            print("Card reader port close error")

        try:
            if G_Machine_BillAcceptorTypeId>0:
                if sender=="bill" or sender=="cmd":
                    billacceptorport.close()
        except:
            print("Bill acceptor port close error")

        FindPorts(sender)
        if sender=="sas" or sender=="cmd":
            FindPortForSAS()
        if sender=="card" or sender=="cmd":
            FindPortForCardReader()
        if G_Machine_BillAcceptorTypeId>0:
            if sender=="bill" or sender=="cmd":
                FindPortForBillAcceptor()
        
        print("</FIND NEW PORTS>-------------------------")
    except Exception as e1tmr:
        print("SAS Portlari yeniden ac.")


def RestartProgram():
    ExecuteCommand("restart")
    #print(ExecuteLinuxCommand("./licencecontrol"))
    #print("Kill yourself")
    #os.kill(os.getpid(),signal.SIGKILL)



def SystemCPUCheck(restartNeeded):
    try:


        RunningJS=[]
        for jsCmd in LastJS_Commands:
            IsFound=0
            for member in RunningJS:
                if member['Name']==jsCmd:
                    IsFound=1
                    member['WorkingCount']=member['WorkingCount']+1
        
            if IsFound==0:
                threadDict = {
                        "Name": jsCmd,
                        "WorkingCount": 1
                        }
                RunningJS.append(threadDict)

        #print("RunningJS", RunningJS)



        output = str(subprocess.check_output("vcgencmd get_throttled", shell=True))
        output=output.replace("b'","").replace("'","").replace("\\n","")
        Throttle=output.split('x')[1]

        Throttle=gc.collect()

        output = str(subprocess.check_output("vcgencmd measure_temp", shell=True))
        output=output.replace("b'","").replace("'","").replace("\\n","")
        CPUTemp=Decimal(output.split('=')[1].replace("C\"",""))
        

        ThreadCount=int(threading.activeCount())
        CPUUsage=int(psutil.cpu_percent())
        MemoryUsage=int(psutil.virtual_memory().percent)
        #print("CPUTemp", CPUTemp,"ThreadCount", ThreadCount, "CPUUsage", CPUUsage, "MemoryUsage", MemoryUsage)
        
        if ThreadCount>40 or restartNeeded==-1:
            try:
                RunningThreads=[]
                for thread in threading.enumerate():
                    IsFound=0
                    for member in RunningThreads:
                        if member['Name']==thread.name:
                            IsFound=1
                            member['WorkingCount']=member['WorkingCount']+1
        
                    if IsFound==0:
                        threadDict = {
                                "Name": thread.name,
                                "WorkingCount": 1
                                }
                        RunningThreads.append(threadDict)
                
                WorkingThreadsText=""
                for member in RunningThreads:
                    WorkingThreadsText=WorkingThreadsText+member['Name']+"(" + str(member['WorkingCount']) +") "
                print("WorkingThreadsText", WorkingThreadsText)
                SQL_Safe_InsImportantMessage("THR: " + str(ThreadCount) + " MEM:" + str(MemoryUsage) + " All:" + WorkingThreadsText, 0)
            except Exception as e2:
                print("Exception on Get Thread names")

        #MemoryUsage>89 idi.. 2021-12-09
        if ThreadCount>115 or MemoryUsage>94:# and restartNeeded==1
            SQL_Safe_InsImportantMessage("Restart program TC:" + str(ThreadCount) + " Mem:" + str(MemoryUsage) ,0)
            RestartProgram()

        if restartNeeded==0:
            SQL_UpdDeviceAdditionalInfo(CPUTemp, Throttle, ThreadCount, CPUUsage, MemoryUsage)
    except Exception as e1tmr:
        print("Exception on SystemCPUCheck")


G_LastCheckPorts=datetime.datetime.now()
G_LastSystemCPUCheck=datetime.datetime.now()- datetime.timedelta(minutes=30)
Prev_HTMLWarning=""
PreviousIsGuiReady=0
Is_MD5Checksum=0
#5snde bir
def DoTmrIsOnline():
    global G_Machine_PayBackPerc
    global G_LastCheckPorts
    global G_LastSystemCPUCheck
    global IsCardInside
    global G_Count_IsOnline
    global Nextion_LastReceivedDate
    global G_Machine_ReservationOK
    global G_Machine_ReservationDate
    global PreviousIsGuiReady
    global IsGuiReady
    global G_Machine_LastCardreaderTime
    global G_Machine_LastBillAcceptorTime
    global Prev_HTMLWarning
    global G_LastGameEnded
    global G_SASLastDate
    global G_Machine_BillAcceptorTypeId
    global Is_MD5Checksum
    try:

        if PreviousIsGuiReady==0 and (IsGUI_Type==3 or IsGUI_Type==4):
            print("Check if HTML is loaded!")
            if IsGuiReady==1:
                PreviousIsGuiReady=IsGuiReady
                
                if IsCardInside==1:
                    GUI_ShowCustomerWindow()
                else:
                    GUI_ShowIdleWindow()

                if G_Machine_IsBonusGives==0:
                    ExecuteJSFunction("HideElement","btnBonus")


        try:
            MinsToRebootNoNetwork=0
            MinsToRebootNoNetwork=int(Config.get("casino","MinsToRebootNoNetwork"))
            if MinsToRebootNoNetwork>0:
                Diff_NetworkLastDate=(datetime.datetime.now()-G_NetworkLastDate).total_seconds()/60
                IsBootNeeded=(int(Diff_NetworkLastDate)>int(MinsToRebootNoNetwork))
                if IsBootNeeded==True:
                    print("1.5", Diff_NetworkLastDate, MinsToRebootNoNetwork)
                    SQL_Safe_InsImportantMessage("System will restart due to no network!" + str(Diff_NetworkLastDate) + "-" + str(MinsToRebootNoNetwork),99)
                    print("********************************************************")
                    print("********************************************************")
                    print("NO NETWORK! SYSTEM WILL RESTART ITSELF!!!!")
                    print("NO NETWORK! SYSTEM WILL RESTART ITSELF!!!!")
                    print("********************************************************")
                    print("********************************************************")
                    ShowNotifyScreen("ERROR","System will restart due to no network!",10)
                    time.sleep(10)
                    ExecuteCommand("restart")
        except:
            print("EXCEPTION MINS TO REBOOT")


        try:
            if Is_MD5Checksum==0 and G_Machine_DeviceId>0:
                md5Checksum=str(hashlib.md5(open('licence.hash','rb').read()).hexdigest())
                #print("CHECKSUM",md5Checksum,len(md5Checksum))
                Is_MD5Checksum=1
                SQL_UpdDeviceAdditionalInfoHash(md5Checksum)
        except:
            Is_MD5Checksum=0


        if G_Count_IsOnline%1==0:
            if G_Count_IsOnline%240==0 or (G_Device_AssetNo==0 and G_Count_IsOnline%10==0):
                SQL_DeviceStatu(0)
            else:
                SQL_DeviceStatu(3)

        G_Count_IsOnline=G_Count_IsOnline+1

        LastGameEndedDiff=(datetime.datetime.now()-G_LastGameEnded).total_seconds()
        LastSessionDiff=(datetime.datetime.now()-G_SessionStarted).total_seconds()


        




        LastCardreaderTimeDiff=(datetime.datetime.now()-G_Machine_LastCardreaderTime).total_seconds()
        if LastCardreaderTimeDiff>(60*5) and LastCardreaderTimeDiff%(60*5)<3 and G_Machine_ProtocolType!=3:
            SQL_Safe_InsImportantMessage("RealCardReaderProb:" + str(LastCardreaderTimeDiff),1)
            

        DiffLastSystemCPUCheck=(datetime.datetime.now()-G_LastSystemCPUCheck).total_seconds()
        if DiffLastSystemCPUCheck>120:
            G_LastSystemCPUCheck=datetime.datetime.now()
            SystemCPUCheck(0)



        try:
            if platform.system().startswith("Window")==True:
                return

            Last_G_NetworkLastDate_Diff=(datetime.datetime.now()-G_NetworkLastDate).total_seconds()
            Last_G_SASLastDate_Diff=(datetime.datetime.now()-G_SASLastDate).total_seconds()
            Last_LastBillAcceptorTime_Diff=(datetime.datetime.now()-G_Machine_LastBillAcceptorTime).total_seconds()
            Last_CheckPorts_Diff=(datetime.datetime.now()-G_LastCheckPorts).total_seconds()

            

            CheckPorts=""

            HTMLWarning=""
            if Last_LastBillAcceptorTime_Diff>60 and G_Machine_BillAcceptorTypeId>0:
                HTMLWarning=HTMLWarning+"NO-BILL<br>"
                CheckPorts="bill"
                
                #2021-05-11 Belki boyle reset attiraacagiz bill acceptora.. Bakalim.
                #if Last_LastBillAcceptorTime_Diff>600:
                #    SQL_Safe_InsImportantMessage("Reset Billacceptor!",1)
                #    time.sleep(20)

            if LastCardreaderTimeDiff>180 and G_Machine_ProtocolType!=3:
                HTMLWarning=HTMLWarning+"NO-CARD<br>"
                CheckPorts="card"
            if Last_G_NetworkLastDate_Diff>8:
                HTMLWarning=HTMLWarning+"NO-NET<br>"
            if Last_G_SASLastDate_Diff>20:
                print("*************************************************")
                Komut_DisableBillAcceptor("nosas")
                HTMLWarning=HTMLWarning+"NO-SAS<br>"
                CheckPorts="sas"
                DividedSas=Last_G_SASLastDate_Diff%60
                if DividedSas<5:
                    SQL_Safe_InsImportantMessage("NO SAS Connection!",1)
                #2021-11-29 Artik reset atmasin sas yok diye. Ne gerek var?
                #if Last_G_SASLastDate_Diff>90 and IsDebugAutoBakiyeYanit==0 and G_DB_Host!="172.16.0.57":
                #    SQL_Safe_InsImportantMessage("Restart because of no SAS!",1)
                #    if G_IsDeviceTestPurpose==0:
                #        ExecuteCommand("restart")

            CheckPorts_Tolerance=180
            if CheckPorts=="sas":
                CheckPorts_Tolerance=50

            if len(CheckPorts)>0 and Last_CheckPorts_Diff>CheckPorts_Tolerance:
                G_LastCheckPorts=datetime.datetime.now()
                CheckAndRestartPorts(CheckPorts)

            
            #print("Last_LastBillAcceptorTime_Diff", Last_LastBillAcceptorTime_Diff, "HTMLWarning", HTMLWarning)
            if G_Count_IsOnline%2==0 and HTMLWarning!=Prev_HTMLWarning:
                Prev_HTMLWarning=HTMLWarning
                ExecuteJSFunction2("ChangeHTML", "divStatuSASNetwork",str(HTMLWarning))

            #print("LastCardreaderTimeDiff", LastCardreaderTimeDiff,"Last_G_SASLastDate_Diff", Last_G_SASLastDate_Diff)
        except:
            print("HTML GUI ERROR")

        #2019-12-05: Rezervasyonu kapatma
        if G_Machine_ReservationOK=="OK" and IsCardInside==0:
            ReservationDiff=(datetime.datetime.now() - G_Machine_ReservationDate).total_seconds()
            if ReservationDiff>(90):
                G_Machine_ReservationOK=""
                Ac("Reservation Iptal")
                GUI_ShowIfPossibleMainStatu("Reservation is expired")

        #10 dk'dir aktif degilse cashout yap
        if LastGameEndedDiff>=(60*10) and G_Session_IsByOnline==1 and IsCardInside==1:
            G_LastGameEnded=datetime.datetime.now()
            SQL_Safe_InsImportantMessage("Close online session, for 10 minutes idle!",98)
            DoHandUserInput("kartcikart:")

        #Savoy: 2019-05-18. Kart takilali 60 sn oldu ve 30 sn'dir oyun yoksa billacceptoru kapat
        if G_Count_IsOnline%2 and LastSessionDiff>=120 and IsBillacceptorOpen==1 and LastGameEndedDiff>=G_Machine_NoActivityTimeOutForBillAcceptor and G_Machine_NoActivityTimeOutForBillAcceptor>0 and G_Machine_IsCashless==1 and G_LastGame_IsFinished==1:
            print("LastGameEndedDiff", LastGameEndedDiff, "G_LastGameEnded", G_LastGameEnded)
            Komut_DisableBillAcceptor("TmrIsOnlineBill")
            GUI_ShowIfPossibleMainStatu("NO GAME BILL ACCEPTOR IS CLOSED!")
            SQL_Safe_InsImportantMessage("Bill acceptor is closed (no game)",98)


        #2019-10-21: Ambassador eger makinadaki para 1 tl'nin asagisindaysa ve 10 sn oyun oynamadiysa; otomatik cashout olsun.
        if IsCardInside==1 and G_Machine_Balance<G_Machine_NoActivityTimeForCashoutMoney and G_Machine_NoActivityTimeForCashoutMoney>0 and G_LastGame_IsFinished==1:
            LastGameDiff=(datetime.datetime.now()-G_LastGame_Action).total_seconds()
            if LastGameDiff>=G_Machine_NoActivityTimeForCashoutSeconds and G_Machine_NoActivityTimeForCashoutSeconds>0:
                print("Otomatik cashout")
                SQL_Safe_InsImportantMessage("Start auto cashout due to low credit",90)
                CardIsRemoved(0)


        #2021-09-06 Spark Auto cashout for oynanmayan oyun...
        #if G_Session_IsByOnline==1 and IsCardInside==1:
        #    LastGameDiff=(datetime.datetime.now()-G_LastGame_Action).total_seconds()
        #    if LastGameDiff>=60 and G_LastGame_IsFinished==1:
        #        G_LastGame_Action=datetime.datetime.now()
        #        print("Otomatik cashout-1")
        #        SQL_Safe_InsImportantMessage("Start auto cashout due to not playing",90)
        #        CardIsRemoved(0)
                

        #2019-10-20: Eger rulet degilse ve son oyundan beri 4 sn'den fazla gectiyse makinanin statusunu Free Game olarak degistirelim
        if G_Machine_IsRulet!=1 and IsCardInside==1 and G_LastGame_IsFinished==0:
            GameStartedDiff=(datetime.datetime.now()-G_LastGameStarted).total_seconds()
            if GameStartedDiff>10:
                SetMachineStatu("Free game")

        if G_Count_IsOnline%10==0:
            if G_Machine_SASVersion=="0":
                print("Get SAS Version")
                SendSASCommand("0154")

            if G_Machine_PayBackPerc<1:
                G_Machine_PayBackPerc=G_Machine_PayBackPerc+1
                print("Get Game Configuration")
                SendSASCommand(GetCRC("01530000"))

        if IsGUI_Type==2:
            #if G_Count_IsOnline%3==0 and IsGUI_Type==2:
            #    NextionCommand(["sendme"])

            if G_Count_IsOnline%4==0 and IsGUI_Type==2:
                Nextion_LastReceivedDate_Diff=(datetime.datetime.now()-Nextion_LastReceivedDate).total_seconds()
                #print("Nextion_LastReceivedDate_Diff", Nextion_LastReceivedDate_Diff)
                #2021-12-05 Sildim
                #if Nextion_LastReceivedDate_Diff>60:
                #    try:
                #        Nextion_LastReceivedDate=datetime.datetime.now()
                #        #SQL_InsImportantMessage("Nextion notification error",2)
                #        nextionport.close()
                #        nextionport.open()
                #    except:
                #        print("Nextion_LastReceivedDate_Diff Failed")


        if G_Count_IsOnline%120==0:#1 dk
            if G_Machine_IsCanPlayWithoutCard==0 and IsCardInside==0:
                #print("Bill acceptor kapat")
                Komut_DisableBillAcceptor("Bill acceptor kapat tmr")

        #if G_Count_IsOnline%12==0:#1dk #if G_Count_IsOnline%30==0:#2,5 dk
        #    print("G_User_CardNo:", G_User_CardNo, " IsCardInside:" , IsCardInside, " IsCardReaderBusy" , IsCardReaderBusy, "IsWaitingForParaYukle", IsWaitingForParaYukle, "G_SASLastDate", G_SASLastDate)

        if G_Count_IsOnline%360==0:
            SyncDB()


        #saatte birdi. bunu 30 dk'ye cevirdim.
        if G_Count_IsOnline%360==0:
            GetMeter(0,"period")

        #Saatte bir
        if G_Count_IsOnline%725==0:
            GetMeter(1,"period")
            G_Count_IsOnline=0



    except:
        print("TmrIsOnline Failed")

G_Count_IsOnline=0
LastMeterDate=datetime.datetime.now()
def TmrIsOnline():
    threadIsOnline = Thread(target = DoTmrIsOnline)
    threadIsOnline.name="thrOnline"
    threadIsOnline.start()
    




Result_SQL_ReadCustomerInfo=""
def DoCardRead(tdata,CardRawData):
    global IsCardReaderBusy
    global IsWaitingAdminScreen
    global Result_SQL_ReadCustomerInfo
    KartNo=""

    print("Card is readed")
    try:
        if G_Machine_CardReaderType==0:
            tdata=tdata.replace("#","^")
            tdata=tdata.replace(";",":")
            KartNo = re.search('%:CARD:(.*?):', tdata).group(1)
            print("KartNo-1:" , KartNo)
            tdata=tdata.replace("\r","");

    except Exception as e:
        print("Buyuk kart olmadi")

    if G_Machine_CardReaderType==1 or G_Machine_CardReaderType==2:
        KartNo=tdata

    

    PrintAndSetAsStatuText("New card is inserted")
    #<Check if it is admin card or not>--------------------------
    #print("Okunan kart no:", tdata)
    if G_Machine_AdminCards.find(KartNo) != -1 and len(G_Machine_AdminCards)>4 and len(KartNo)>4:
        PrintAndSetAsStatuText("Admin card is inserted")



        IsCardReaderBusy=1
        print("Admin Card", tdata)
        if IsGUI_Type==2:
            NextionCommand(["vis btnAdmin,1"])

        GUI_ShowAdmin()
        IsWaitingAdminScreen=1
        while IsWaitingAdminScreen==1:
            time.sleep(1)
        IsCardReaderBusy=0#DoCardRead Admin card exit
        print("Admin card exited!")
        return
    #</Check if it is admin card or not>--------------------------

    try:

        L_CardRemoveDate=datetime.datetime.now()


        
        global G_User_CardNo
        global IsCardInside

        print("IsCardInside", IsCardInside)
        Result_SQL_ReadCustomerInfo=""
        if IsCardInside==0:
            CardReader_CardInsertStart()
            
            ChangeRealTimeReporting(0)#2021-11-28
            #Mehmet Test için ekledi . 
            Result_SQL_ReadCustomerInfo=SQL_ReadCustomerInfo_Test(KartNo,CardRawData)
            #Result_SQL_ReadCustomerInfo=SQL_ReadCustomerInfo(KartNo,CardRawData)
            ChangeRealTimeReporting(1)#2021-11-28

            print("Result_SQL_ReadCustomerInfo", Result_SQL_ReadCustomerInfo)
            if Result_SQL_ReadCustomerInfo=="Sistemde zaten kart var." or Result_SQL_ReadCustomerInfo=="System cant accept card-in"  or Result_SQL_ReadCustomerInfo=="System is reserved" or Result_SQL_ReadCustomerInfo=="Unable to query balance on Card Read" or Result_SQL_ReadCustomerInfo=="GM has money" or Result_SQL_ReadCustomerInfo=="System is locked. Cant insert card" or Result_SQL_ReadCustomerInfo=="Cancelled card insert. Cant upload money" or Result_SQL_ReadCustomerInfo=="Card is not registered":
                SQL_Safe_InsImportantMessage("Session problem: " +Result_SQL_ReadCustomerInfo ,91)
                CardReader_CardProblem()
                time.sleep(4)
                if G_Machine_CardReaderModel=="Eject":
                    CardReader_EjectCard()
                    time.sleep(1)
            else:
                CardReader_CardInsertEnd()

        ProcessSecondLength=(datetime.datetime.now()-L_CardRemoveDate).total_seconds()
        SQL_InsException("CardIsInserted", ("%s-%s" % (str(ProcessSecondLength), Result_SQL_ReadCustomerInfo)))

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("DoCardRead On ", name, exc_type, fname, exc_tb.tb_lineno)
    
    IsCardReaderBusy=0#DoCardRead
    #end DoCardRead



def Process_CardExitFailed():
    print("Card exit is failed")
    #UnDelayPlay()



DebugPicture=0
IsLocked_NetworkCheck=0
WaitingForGameEndDBInsert=0
G_Count_CardOut=0
#sender: 0: realcard exit, 1:removecardcommand, 2: Cant upload money, 3: Force handpay
def CardIsRemoved(sender):
    cardmachinelogid=Config.getint('customer','cardmachinelogid')

    try:
        cardmachinelogid=G_CardMachineLogId
    except Exception as eCardLogId:
        ExceptionHandler("cardmachinelogid",eCardLogId,0)

    if DebugPicture==0:
        Do_CardIsRemoved(sender)


    
    SQL_Safe_InsImportantMessage("Card Remove Steps " + Step_CardIsRemoved +"-" + Step_RemoveCustomerInfo,100)

    if DebugPicture==1:
        graphviz = GraphvizOutput()
        graphviz.output_file = "cashout"+str(cardmachinelogid)+".png"
        with PyCallGraph(output=graphviz):
            Do_CardIsRemoved(sender)


Step_CardIsRemoved=""
def Do_CardIsRemoved(sender):
    global IsCardReaderBusy
    try:
        global Step_CardIsRemoved
        global IsCollectButtonProcessInUse
        global IsLocked_NetworkCheck
        global WaitingForGameEndDBInsert
        WaitingForGameEndDBInsert=0
        global G_Count_CardOut
        G_Count_CardOut=0

        Step_CardIsRemoved="1"
        L_CardRemoveDate=datetime.datetime.now()

        if sender!=123:
            ChangeRealTimeReporting(0)#2021-11-04
            SystemCPUCheck(1)

        if G_Machine_IsCanPlayWithoutCard==0 or G_Machine_IsCashless==1:
            Komut_DisableBillAcceptor("card is removed first")
        Step_CardIsRemoved="2"
        CardReader_CardExitStart()

        SQL_Safe_InsImportantMessageByWarningType("Card exit is started",1,0)


        Step_CardIsRemoved="3"

        #2020-01-16
        if 2==1:
            if G_Machine_DeviceTypeId!=7:
                print("<OYUN KILITLENESIYE KADAR BEKLE 0!>-----------------------------------------")
                Wait_Bakiye(11,0,"oyunkilitnenesiye-0")
                print("</OYUN KILITLENESIYE KADAR BEKLE 0!>-----------------------------------------")


        Step_CardIsRemoved="4"

        #<Check if network is online>--------------------------------------------
        IsProblemNetwork=0
        if 1==1:
            try:
                Step_CardIsRemoved = "5"
                print("Check network connection")
                # Original MSSQL procedure: tsp_CheckNetwork
                # Note: This procedure was not found in postgres-routines-in-sas.sql
                # Using hybrid approach - queue operation instead of direct call
                result = db_helper.queue_database_operation(
                    'tsp_CheckNetwork',
                    [G_Machine_Mac, G_User_CardNo],
                    'check_network'
                )
                for row in result:
                    print("Network exists")
            except Exception as ecardtype:
                IsProblemNetwork=1

        if IsProblemNetwork==1:
            Step_CardIsRemoved="6"
            
            IsLocked_NetworkCheck=1
            #Kilitle("IsLocked_NetworkCheck")
            GUI_ShowIfPossibleMainStatu("No network!")
            ShowNotifyScreen("NO NETWORK!","Please make sure ethernet cable is plugged in.",10)
            SQL_InsImportantMessageByWarningType("No network tsp_CheckNetwork",1,0)
            time.sleep(10)
            ExceptionHandler("tsp_CheckNetwork",ecardtype,0)
            IsCardReaderBusy=0#Do_CardIsRemoved
            return


        if 2==1:#2021-07-05 Yaptim ama hic acmadim.
            IsSASLink=1
            Last_G_SASLastDate_Diff=(datetime.datetime.now()-G_SASLastDate).total_seconds()
            if Last_G_SASLastDate_Diff>=60:
                IsSASLink=0

            if IsSASLink==0:
                Step_CardIsRemoved="6.SASLink"
                GUI_ShowIfPossibleMainStatu("No SAS!")
                ShowNotifyScreen("NO SAS!","Please make sure SAS cable is plugged in.",10)
                time.sleep(10)
                ExceptionHandler("NO SAS",ecardtype,0)
                SQL_InsImportantMessageByWarningType("No SAS...",1,0)
                IsCardReaderBusy=0#Do_CardIsRemoved



        Step_CardIsRemoved="7"
        if IsLocked_NetworkCheck==1:
            IsLocked_NetworkCheck=0
            Ac("IsLocked_NetworkCheck")
        #</Check if network is online>-------------------------------------------



        Step_CardIsRemoved="8"
        if IsCardInside==0:
            Step_CardIsRemoved="9"
            print("Card is not inside. CardIsRemoved", sender)
            IsCardReaderBusy=0#Card is not inside Card Is Removed
            Process_CardExitFailed()
            return

        Step_CardIsRemoved="10"
        #SQL_InsException("CardExit is started 1/100","fixix")
        LastCardExitDiff=(datetime.datetime.now()-G_LastCardExit).total_seconds()
        if sender==0 and LastCardExitDiff<=2:
            Step_CardIsRemoved="11 (3 sec wait)"
            PrintAndSetAsStatuText("Wait 3 seconds for card exit")
            IsCardReaderBusy=0#Wait 5 Seconds for card exit
            Process_CardExitFailed()
            return

        Step_CardIsRemoved="12"
        GUI_ShowCustomerWindow()

        Step_CardIsRemoved="13"

        TempWaitInt=0

        #2020-06-05 Kaldirdik.
        #if IsAvailableForCashout(sender)==0 and G_Machine_LockBeforeAFT==1:
        #    Kilitle("Card Is Removed")
        
        Step_CardIsRemoved="15"

        if sender==0:
            print("***************REAL CARD EXIT*******************", sender)
        Step_CardIsRemoved="16"
        BlinkCustomerScreenLine(1, 3, "Please wait. Card exit is in process", 0)
        Step_CardIsRemoved="17"

        #2016-09-29 Eskiden oyunun bitip bitmedigini buradan anliyorduk. Bunu kaldiralim artik. 
        IsCheckForWaiting=True

        if G_Machine_IsCashless==0:
            IsCheckForWaiting=False

        #2018-12-27 artik bunu kullanmayalim. hadi bakalim
        IsCheckForWaiting=False

        Step_CardIsRemoved="18"

        if IsCheckForWaiting==True:
            AvailableWaitingDate=datetime.datetime.now()
            while IsAvailableForCashout(sender)==0:
                try:
                    if TempWaitInt%3==0:
                        PrintAndSetAsStatuText("Waiting for game end")
                        GUI_ShowIfPossibleMainStatu("Waiting for game end")

                    time.sleep(0.5)
                    TempWaitInt=TempWaitInt+1
                    if TempWaitInt>40 and TempWaitInt%150==0 and WaitingForGameEndDBInsert==0:
                        SQL_InsImportantMessageByWarningType("Waiting for game end. Please check gaming machine",155,10)
                        WaitingForGameEndDBInsert=WaitingForGameEndDBInsert+1


                    try:
                        AvailableWaitingDateDiff=(datetime.datetime.now()-AvailableWaitingDate).total_seconds()
                        if ((G_Count_CardOut>=4 and G_Machine_IsRulet==1) or (G_Count_CardOut%3==0 and G_Machine_IsRulet==0)) and AvailableWaitingDateDiff>70:
                            Komut_BakiyeSorgulama(2,0,"no need for game end")
                            SQL_InsImportantMessage("No need to wait for game end. Can cashout now.",131)
                            break

                    except Exception as ex:
                        ExceptionHandler("AvailableWaitingDateDiff",ex,1)

                
                except Exception as e:
                    print("Exception")

            print('Oyun bitti. Kart cikartma islemi baslasin')

        Step_CardIsRemoved="25-CardRemoveCustomer"
        #mevo
        Card_RemoveCustomerInfo(sender)
        Step_CardIsRemoved="26"

        ProcessSecondLength=(datetime.datetime.now()-L_CardRemoveDate).total_seconds()
        Step_CardIsRemoved="27"
        SQL_InsException("CardIsRemoved",str(ProcessSecondLength))
        Step_CardIsRemoved="100"

    except Exception as e:
        ExceptionHandler("CardIsRemoved",e,1)

    IsCardReaderBusy=0#Do_CardIsRemoved
    #end CardIsRemoved



IsInstantCardInside=0
IsCardReaderBusy=0

   
G_Sys_CardNotWorkingCount=0
def SetCardReaderIsNotWorking():
    global G_Sys_CardNotWorkingCount
    G_Sys_CardNotWorkingCount=G_Sys_CardNotWorkingCount+1
    SetMachineStatu("Card reader is not working")
    if G_Sys_CardNotWorkingCount%100==True:
        SQL_InsImportantMessageByWarningType("Card reader is not working. Please control card reader",4,12)


G_Sys_GetCardUID_Error=0
G_Sys_Card_LastStatus=0
G_Sys_LastCardSuccess=datetime.datetime.now()
CardReaderLib=None
def CardRead_CRT288B_Process():
    global G_Sys_Card_LastStatus
    global G_Sys_LastCardSuccess
    global G_Sys_GetCardUID_Error
    global CardReaderLib
    global G_Machine_LastCardreaderTime



    Result=0
    try:
        CardArrayType = ctypes.c_ubyte * 1024
        CardArray = CardArrayType()



        if CardReaderLib==None:
            CardReaderLib = ctypes.cdll.LoadLibrary(FilePathSO)

        CurrentCardReaderStatus=CardReaderLib.CRT288B_OpenDev(0,0,0)
        if CurrentCardReaderStatus==-5:
            if G_Sys_Card_LastStatus!=-5:
                G_Sys_Card_LastStatus=CurrentCardReaderStatus
                print("USB Kart okuyucusunda hata!!!**************************************")
                SetCardReaderIsNotWorking()
                GUI_ShowIfPossibleMainStatu("Card reader is not working")

            return ""
        G_Sys_Card_LastStatus=CurrentCardReaderStatus
        G_Machine_LastCardreaderTime=datetime.datetime.now()
        Result = CardReaderLib.CRT288B_GetCardUID(CardArray)
        CardReaderLib.CRT288B_CloseDev()


        if Result==-1:
            print("Python: ERROR ON GETCARDUID, it returned", Result, " G_Sys_LastCardSuccess: ", G_Sys_LastCardSuccess, " CurrentDate", datetime.datetime.now())
            if G_Sys_GetCardUID_Error==0:
                SetCardReaderIsNotWorking()
                G_Sys_GetCardUID_Error=-1

            return "-1"
        

        #Gelen=''.join([chr(i) for i in CardArray]).rstrip('\x00')
        #GelenStr=Gelen.encode('hex').upper()
        #print(GelenStr)
        GelenStr=bytearray(CardArray).hex().upper()
        while (GelenStr.startswith("590400")==True):
            GelenStr=GelenStr[6:len(GelenStr)]
            GelenStr=GelenStr[0:8]
        
        IsCardReadedOk=0
        if len(GelenStr)==8:
            #print("Result", Result, datetime.datetime.now(), " GelenStr", GelenStr)
            G_Sys_LastCardSuccess=datetime.datetime.now()
            G_Sys_GetCardUID_Error=0
            #print("Card read ok")
            return GelenStr
        else:
            return ""


    except:
        Result=2
        return ""




def CardRead_CRT288B():
    try:
        global G_Count_CardOut
        global IsInstantCardInside
        global IsCardRead
        global IsCardReaderBusy
        global IsWaitAtLeastCardExistDbSaved
        global IsWaitingAdminScreen

        if G_Machine_Ready==0:
            return

        tdata=CardRead_CRT288B_Process()
        


        
        if IsCardReaderBusy==1:
            return

        if IsCardRead==1:

            


            if tdata!=None:





                if len(tdata)>4 and IsCardInside==0 and IsCardReaderBusy==0:
                    IsCardReaderBusy=1

                    try:
                        GUI_ShowIfPossibleMainStatu("Card is inserted!")
                        if DebugPicture==0:
                            DoCardRead(tdata, tdata)
                        if DebugPicture==1:
                            graphviz = GraphvizOutput()
                            graphviz.output_file = "cashin"+str(G_CardMachineLogId)+".png"
                            with PyCallGraph(output=graphviz):
                                DoCardRead(tdata, tdata)
                    except Exception as ecard:
                        ExceptionHandler("DoCardRead Thread",ecard,0)


            if IsCardInside==1:
                DoCardExitProcess=0

                if tdata==None:
                    DoCardExitProcess=1

                if tdata!=None:


                    if tdata!=G_User_CardNo:
                        if len(tdata)>2:
                            print("***************************************************")
                            print("Su an makinanin icinde farkli bir kart var!!!")
                            print("***************************************************")
                        DoCardExitProcess=1


                if DoCardExitProcess==1:

                    #print("Card cikma proseduru")
                    
                    LastCardEnterDiff=(datetime.datetime.now()-G_LastCardEnter).total_seconds()
                    if LastCardEnterDiff<=3:
                        print("Wait at least 5 seconds for card exit",LastCardEnterDiff)
                        return
                    
                    IsCardReaderBusy=1
                    #Komut_BakiyeSorgulama(2,0,"cardexit-crt288b")

                    try:
                        CardIsRemoved(0)
                    except Exception as ecard:
                        ExceptionHandler("CardIsRemoved Thread",ecard,0)



    except Exception as e:
        ExceptionHandler("CRT288B",e,0)


#<Card Reader Fuheng>------------------
def print_time_stamp_ms():
    return

CardReaderCommandStr = ""

def CardReaderCommand(data):

    if G_Online_IsOnlinePlaying==1:
        return

    global CardReaderCommandStr

    TryCount=0
    while len(CardReaderCommandStr) > 0:
        print("Please wait.. Another command is being sent to card reader",
              CardReaderCommandStr)
        time.sleep(0.1)
        TryCount=TryCount+1
        if TryCount>10:
            break

    CardReaderCommandStr = data

def CardReaderSendCommandImmediately(sendstring, doPooling):
    try:
        cardreader.flushInput

        if platform.system() == "Windows":
            hex_data = Decode2Hex(sendstring)#.decode("hex")
            bytearray = map(ord, hex_data)
            cardreader.write(hex_data)
        else:
            hex_data = Decode2Hex(sendstring)
            cardreader.write(hex_data)

        if doPooling == 1 and 2 == 2:
            time.sleep(0.1)
            #DoCardReaderPooling(doPooling)
    except Exception as ecard:
        WINDOWS=WINDOWS
        #ExceptionHandler("CardReaderSendCommandImmediately Thread", ecard, 0)

G_LastCardRead=datetime.datetime.now()
def CardRead_rCloud(sender=0):
    global IsCardReaderBusy
    global G_User_CardNo
    global CardReaderCommandStr
    global G_CardLastDate
    global IsCardReaderOpened
    global G_Machine_LastCardreaderTime
    global G_LastCardRead
    global G_Session_IsByOnline

    IsSpecialyCommand = False
    # mifare S50 get uid
    senddata = "02000235310307"

    teststr="1"
    if len(CardReaderCommandStr) > 0:
        #print("-----------------------------------------")
        #print("Ozel komut", CardReaderCommandStr)
        IsSpecialyCommand = True
        senddata = CardReaderCommandStr
        CardReaderCommandStr = ""

    tdata = ""
    try:
        #print("-----------------------------------------")
        print_time_stamp_ms()

        CardReaderSendCommandImmediately(senddata, 0)
        #print("Sent data card", senddata)
        retry = 5

        # receive response, may be should wait like most 100ms
        while 1:
            data_left = cardreader.inWaiting()
            if data_left == 0:
                retry = retry - 1
                if retry <= 0:
                    break
                else:
                    time.sleep(0.02)
                    continue

            out = ''
            while cardreader.inWaiting() > 0:
                #out += str(cardreader.read(1)).replace("b'\\x","").replace("'","")
                out += '{:02X}'.format(cardreader.read(1)[0])
            if out == '':
                continue
            tdata += out

        if len(tdata) > 0:
            tdata = tdata.upper()
            print_time_stamp_ms()
            
            

            if tdata=="06":
                IsCardReaderOpened=1

            IsMessageHandled = 0
            if tdata == '15': # # receive NAK "16"
                 print("+++++++Receive NAK, send command BCC error+++++++",
                      IsSpecialyCommand, "sender", sender)
            elif tdata == "06" or IsSpecialyCommand == True or sender == 1: #receive ACK "06"
                IsMessageHandled = 1
                print_time_stamp_ms()
                #print("05 gonder IsSpecialyCommand",IsSpecialyCommand, "sender", sender)
                # send "05" ENQ
                CardReaderSendCommandImmediately("05", 0)

                tdata = ""
                # receive data 
                # we should modify the timeout depends diferent command
                # we should check frame start and calculate the whole frame size depend on frame length(data[1] << 8 + data[2])
                retry = 20
                while 1:
                    data_left = cardreader.inWaiting()
                    if data_left == 0:
                        retry = retry - 1
                        if retry <= 0:
                            break
                        else:
                            time.sleep(0.05)
                            continue
                    out = ''
                    while cardreader.inWaiting() > 0:
                        #out += str(cardreader.read(1)).replace("b'\\x","").replace("'","")
                        out += '{:02X}'.format(cardreader.read(1)[0])
                    if out == '':
                        continue
                    tdata += out

                if len(tdata) > 0:
                    tdata = tdata.upper()
                    print_time_stamp_ms()
                    #if len(tdata)>2:
                    #    print("tdata card", tdata)


                    if tdata.startswith("020003")==True:
                        IsCardReaderOpened=1


                    # we should check response frame valid
                    # check frame start
                    # check frame length
                    # check frame end
                    # check frame BCC
                    if tdata.startswith("02") != True: # check frame start
                         #print("+++++++Response frame error+++++++", tdata)
                         teststr="1"
                    else:
                        G_Machine_LastCardreaderTime=datetime.datetime.now()

                        if IsCardReaderBusy == 0:
                            DoCardExitProcess = 0

                            #2020-02-20  and IsWaitingForParaYukle==0 kaldirdim buradan
                            if tdata.startswith("020003") == True and tdata.find("02000380")==-1 and IsCardInside == 1:
                                IsMessageHandled = 1
                                DoCardExitProcess = 1


#tdata card 02000335314E0348
#tdata card 02000335314E0348
#tdata card 02000335314E0348
#tdata card 020007353159F88EBB4903DF
#tdata card 020007353159F88EBB4903DF
#tdata card 020007353159F88EBB4903DF


                            if tdata.startswith("020007") == True:

                                G_CardLastDate=datetime.datetime.now()
                                CardIndexLength = tdata.find("353159")+6
                                CardNo = tdata[CardIndexLength: CardIndexLength+8]

                                
                                LastCardReadDiff=(datetime.datetime.now()-G_LastCardRead).total_seconds()

                                #print("debug card", CardNo, "IsCardInside", IsCardInside, "IsCardReaderBusy", IsCardReaderBusy, "LastCardReadDiff", LastCardReadDiff)


                                # and LastCardReadDiff<2 bunu kaldirdik. neden?
                                #if IsCardInside == 0 and IsCardReaderBusy == 0 and LastCardReadDiff<2:
                                if IsCardInside == 0 and IsCardReaderBusy == 0:
                                    print("debug card - 2", CardNo)
                                    G_LastCardRead=datetime.datetime.now()
                                    IsCardReaderBusy = 1

                                    try:
                                        print("Readed card data", tdata)
                                        if G_Machine_IsRecordAllSAS==1:
                                            SQL_Safe_InsImportantMessage("RawCardData:" + tdata,1)
                                        G_Machine_LastCardreaderTime=datetime.datetime.now()

                                        G_Session_IsByOnline=0
                                        GUI_ShowIfPossibleMainStatu("Card is inserted!")
                                        
                                        if DebugPicture==0:
                                            processGameoperation = Thread(target=DoCardRead, args=(CardNo,tdata,))
                                            processGameoperation.name="DoCardRead2"
                                            processGameoperation.start()

                                        if DebugPicture==1:
                                            graphviz = GraphvizOutput()
                                            graphviz.output_file = "cashin"+str(G_CardMachineLogId)+".png"
                                            with PyCallGraph(output=graphviz):
                                                DoCardRead(CardNo,tdata)

                                    except Exception as ecard:
                                        ExceptionHandler("DoCardRead Thread", ecard, 0)

                                if IsCardInside == 1:
                                    if G_User_CardNo != CardNo and CardNo!="735314E0":
                                        print("Su an farkli bir kart var cihazda!", G_User_CardNo, CardNo)
                                        DoCardExitProcess = 1

                            if DoCardExitProcess == 1:
                                G_CardLastDate=datetime.datetime.now()

                                if G_Session_IsByOnline==1:
                                    return

                                LastCardEnterDiff = (datetime.datetime.now()-G_LastCardEnter).total_seconds()
                                if LastCardEnterDiff <= 3:
                                    print("Wait at least 5 seconds for card exit",LastCardEnterDiff)
                                    return

                                IsCardReaderBusy = 1

                                try:
                                    processGameoperation = Thread(target=CardIsRemoved, args=(0,))
                                    processGameoperation.name="CardIsRemoved"
                                    processGameoperation.start()

                                    #2019-12-30: Savoy'da kart ciktiginda belki thread'i calistirmiyordu. Onun icin thread'den function'a donuldu.
                                    #CardIsRemoved(0)

                                except Exception as ecard:
                                    ExceptionHandler("CardIsRemoved Thread", ecard, 0)

                        #endif IsCardReaderBusy==0:
                else :
                    #print("+++++++ Not receive data +++++++")
                    teststr="1"
            else :
                 #print("+++++++ Response frame error +++++++")
                 teststr="1"
        else :
            print("+++++++ Not receive data ++++++++")
    except Exception as e:
        IsCardReaderBusy=IsCardReaderBusy
        #ExceptionHandler("CardRead_rCloud", e, 0)
         

#<Card Reader Fuheng>------------------




def TmrCardRead():

    if G_Online_IsOnlinePlaying==1:
        return

    if platform.system().startswith("Window")==True:
        return

    #return #card iptal

    if G_Machine_CardReaderType==1:
        CardRead_CRT288B()

    if G_Machine_CardReaderType==2:
        CardRead_rCloud(0)

def XSendSASPORT(command):
    valsend=1
    try:
        #hex_data=Decode2Hex(command)
        #bytearray=map(ord, hex_data);
        #sasport.write("".join(map(chr, bytearray)))
        hex_data = Decode2Hex(command)
        sasport.write(hex_data)
        #print("SAS PORT SENT", hex_data)
    except:
        valsend=0
        #print("Err on SendSASPORT", sasport.port)



def SendSASPORT(command):
    valsend=1
    try:
        #hex_data=Decode2Hex(command)
        #bytearray=map(ord, hex_data);
        #sasport.write("".join(map(chr, bytearray)))
        hex_data = Decode2Hex(command)
        sasport.write(hex_data)
        #print("SAS PORT SENT", hex_data)

        #2021-10-18 Kapatildi....
        sasport.flushInput()

    except:
        valsend=0
        #print("Err on SendSASPORT", sasport.port)


G_Last_81=datetime.datetime.now()
G_Last_80=datetime.datetime.now()

G_IsComunicationByWindows=-1
def SendSASCommand(Command):
    global Sas_LastSent
    global G_Machine_DeviceTypeId
    global G_Last_81
    global G_Last_80
    global G_Program_LogAllSAS
    global G_IsComunicationByWindows
    if G_IsComunicationByWindows==-1:
        if platform.system().startswith("Window")==True:
            G_IsComunicationByWindows=1



    Command=Command.replace(" ","")
    
    if Command=="81":
        G_Last_81=datetime.datetime.now()

    if Command=="80":
        G_Last_80=datetime.datetime.now()


    if G_Program_LogAllSAS==1:
        try:
            SQL_Safe_InsTraceLog("SAS","TX",Command)
        except Exception as exLog:
            print("EX LOG")

    if len(Command)>=3:
        #print("SAS GIDEN", Command, "G_Machine_DeviceTypeId", G_Machine_DeviceTypeId, "port", sasport.port, "acik:", sasport.isOpen(),  datetime.datetime.now())
        print("TX: ", G_Machine_DeviceTypeId, Command, sasport.port, datetime.datetime.now())


    if G_Machine_DeviceTypeId==1 or G_Machine_DeviceTypeId==4:
        SendSASPORT(Command)
    else:
        try:

            IsNewSendingMsg=0
            if G_IsComunicationByWindows==1 or G_Machine_DeviceTypeId==11:
                IsNewSendingMsg=1

            if G_Machine_DeviceTypeId==6:
                IsNewSendingMsg=0


            if IsNewSendingMsg==1:#Windows veya Interblock
                sleeptime=0.005
                if G_Machine_DeviceTypeId==11:
                    sleeptime=0.003
                
                

                if sasport.parity!=serial.PARITY_MARK or 1==1:
                    sasport.parity=serial.PARITY_MARK
                SendSASPORT(Command[0:2])
                time.sleep(sleeptime)

                if sasport.parity!=serial.PARITY_SPACE or 1==1:
                    sasport.parity=serial.PARITY_SPACE

                try:
                    if len(Command)>2:

                        SendSASPORT(Command[2:len(Command)])
                except Exception as ex:
                    print("Exception-11-SAS")
                #sasport.flush()
            else:
                #saswaittime=0.01
                saswaittime=0.005


                saswaittime=0.001#2020-12-25 test ok gibi..


                #time.sleep(saswaittime)
                #sasport.parity=serial.PARITY_NONE
                iflag, oflag, cflag, lflag, ispeed, ospeed, cc = termios.tcgetattr(sasport)

                CMSPAR = 0x40000000

                #cflag |= termios.PARENB | termios.PARODD # to select MARK parity
                cflag |= termios.PARENB | CMSPAR | termios.PARODD # to select MARK parity


                termios.tcsetattr(sasport, termios.TCSANOW, [iflag, oflag, cflag, lflag, ispeed, ospeed, cc])

                SendSASPORT(Command[0:2])
                if len(Command)>2:
                    time.sleep(saswaittime)
                    #sasport.parity=serial.PARITY_EVEN
                    iflag, oflag, cflag, lflag, ispeed, ospeed, cc = termios.tcgetattr(sasport)

                    cflag |= termios.PARENB # To select SPACE parity
                    cflag &= ~termios.PARODD

                    termios.tcsetattr(sasport, termios.TCSANOW, [iflag, oflag, cflag, lflag, ispeed, ospeed, cc])
                    SendSASPORT(Command[2:len(Command)])
                    #sasport.flushInput()

        except Exception as e:
            ddsdf=11
            #print("SasSendErr")
            #ExceptionHandler("SendSASCommand xx",e,0)




def SendCommandIsExist():
    global GENEL_GonderilecekKomut
    try:
        if len(GENEL_GonderilecekKomut)>0:
            SendSASCommand(GENEL_GonderilecekKomut)

            GENEL_GonderilecekKomut=""

    except Exception as ex:
        GENEL_GonderilecekKomut=""
        #SQL_InsImportantMessage("Mesaj gonderilemedi M:%s" % (GENEL_GonderilecekKomut),22)



IsSendByThread=0
GENEL_GonderilecekKomut=""
def SAS_SendCommand(CommandName, Command, DoSaveDB):
    global SAS_SendCommand
    try:
        global GENEL_GonderilecekKomut

        while len(GENEL_GonderilecekKomut)>0:
            #print("SAS Baska bi mesa gonderilmek uzere bekleniliyor." , GENEL_GonderilecekKomut , Command)
            time.sleep(0.01)


        if len(Command) % 2 != 0:
            SQL_InsException("SAS_SendCommand","len(Command) % 2 != 0")
            print("PROBLEM BUYUK!!!")


        #while Sas_LastSent==81:
        #    #print("Once 81 olsun...")
        #    time.sleep(0.001)

        GENEL_GonderilecekKomut=Command
        #if GENEL_GonderilecekKomut[0:4]=="0172":#levent
        #    time.sleep(0.2)


        
        if IsDebugMachineNotExist==1:
            GENEL_GonderilecekKomut=""


        if IsSendByThread==0:
            try:
                SendCommandIsExist()
            except Exception as e:
                print("Gondermede hata")

        if DoSaveDB==1:
            SQL_Safe_InsSentCommands(CommandName, Command)
    except Exception as e:
        ExceptionHandler("SAS_SendCommand",e,0)




def ParseMessage(message):
    messageFound=""
    messageFoundCRC=""
    messageRestOfMessage=""
    messageImportant=0
    
    
    #2F: Meter
    #1F: Send gaming machine ID information
    #54: Send SAS VersionId and gaming machine serial number
    #14: Send Total Jackpot Meter
    #12: Send Total CoinOut Meter
    
    
    IsLengthExist=0
    if message[0:4]=="0172" or message[0:4]=="0174" or message[0:4]=="012F" or message[0:4]=="0154" or message[0:4]=="01AF":
        IsLengthExist=1
    
    if IsLengthExist==1:
        messageImportant=1
        messageLength=(int(message[4:6], 16)*2)

        
        messageFound=message[0:messageLength+6+4]
        messageFoundCRC=message[messageLength+6:messageLength+6+4]
        messageRestOfMessage=message[messageLength+6+4:len(message)]
        
        #print("<Parse Message>------------------------------------------------------")
        #print("PM. messageFound             ", messageFound)
        #print("PM. messageFoundCRC          ", messageFoundCRC)
        #print("PM. messageRestOfMessage     ", messageRestOfMessage)
        #print("</Parse Message>------------------------------------------------------")
        
    else:#Lengthi olmayan mesajlar
        if message[0:4]=="01FF":
            messageImportant=1
            messageLength=2
            
            messageFound=message[4:6]
            #print("bulunan:", messageFound)
            if messageFound=="4F":#Bill accepted
                messageLength=8

            #01FF69DB5B
            if messageFound=="69":#AFT TRANSFER COMPLETED
                messageLength=2

            if messageFound=="7C":#Legacy bonus pay was awared
                messageLength=12
                
            if messageFound=="7E":#Game started
                messageLength=10
                
            if messageFound=="7F":#Game end
                messageLength=6
                
            if messageFound=="88":#Reel stopped
                messageLength=4
                
            if messageFound=="8A":#Game recall entered
                messageLength=6
                
            if messageFound=="8B":#Card held
                messageLength=3
                
            if messageFound=="8C":#Game selected
                messageLength=4
                

            messageLength=((messageLength+1)*2)
            messageFound=message[0:messageLength+4]
            messageFoundCRC=message[messageLength:messageLength+4]
            try:
                messageRestOfMessage=message[messageLength+4+4:len(message)]
            except:
                print("01FF")
        else:
            #print("Bu ne?*********************")
            messageLength=len(message)
            messageFound=message[0:messageLength]
            messageFoundCRC=message[messageLength-4:messageLength]
            
        
        
        
    return messageFound, messageFoundCRC, messageRestOfMessage,messageImportant



def GetDataFromSasPort(IsMessageSent):
    global sasport

    istype=1

    if istype==1:
        data_left = sasport.inWaiting()
        if data_left==0:
            return ""
        
        TotalReaded=0
        out = ''
        ReadCountTimeOut=5
        
        #if IsMessageSent==1:
        #    ReadCountTimeOut=100

        #while ReadCountTimeOut>0:
        #    ReadCountTimeOut=ReadCountTimeOut-1
            
        #    while sasport.inWaiting() > 0:
        #        if IsMessageSent==1:
        #            ReadCountTimeOut=ReadCountTimeOut+1
                
        #        TotalReaded=TotalReaded+1
        #        out+=sasport.read_all().hex()
        #        time.sleep(0.005)

        #    time.sleep(0.005)


        out = ''
        ReadCountTimeOut=3
        while ReadCountTimeOut>0:
            ReadCountTimeOut=ReadCountTimeOut-1
            
            while sasport.inWaiting() > 0:
                out+=sasport.read_all().hex()
                time.sleep(0.005)
        
        return out.upper()
        
        if TotalReaded>5:
            print("Total Readed", TotalReaded, out)
        return out.upper()


        #data_left = sasport.inWaiting()
        #if data_left==0:
        #    return ""
        
        #out = ''
        #while sasport.inWaiting() > 0:
        #    out += sasport.read(1)
            
        #tdata=out.encode('hex').upper()
        #return tdata


    if istype==2:
        tdata=""
        #<Get message from port>-----------------------
        data_left = sasport.inWaiting()
        while data_left>0:
            tdata += sasport.read(data_left).encode('hex').upper()
            time.sleep(TimeSleepForInterByte)
            data_left = sasport.inWaiting()
        #</Get message from port>-----------------------
        return tdata

    return ""


TimeSleepForInterByte=0.005


G_SAS_LastAFTAnswerDate=datetime.datetime.now()- datetime.timedelta(minutes=30)
G_Sas_DoNotPool=0
LastStep_DoSASPoolingMsg="0"
WakeUpCount=0
IsWaitingLoopOnSASPooling=0
SendWakeUp=1
Sas_LastSent=81
Sas_Count_80=0
Sas_Count_81=0
def DoSASPoolingMsg(isInit):
    try:
        global G_SAS_LastAFTAnswerDate
        global G_Sas_DoNotPool
        global Sas_Count_80
        global Sas_Count_81
        global G_Program_LogAllSAS
        global LastStep_DoSASPoolingMsg
        #print("LastStep_DoSASPoolingMsg", LastStep_DoSASPoolingMsg)
        global G_SASLastDate
        global IsWaitingLoopOnSASPooling
        global sasport
        global SendWakeUp
        global Sas_LastSent
        global IsSendByThread
        global G_Machine_IsSASPortFound
        global G_LastAFTOperationDate
        global G_LastCashoutPressedDate

        SendWakeUp=1

        IsNewPooling=0
        IsSendByThread=1
        
        #2021-11-28
        #if G_Machine_DeviceTypeId==7:
        #    IsSendByThread=0
        #    IsNewPooling=1


        #2020-01-16 savoy apex
        #if G_Machine_DeviceTypeId==10:
        #    IsSendByThread=0

        LastStep_DoSASPoolingMsg="0"

        global WakeUpCount
        WakeUpCount=WakeUpCount+1


        if len(GENEL_GonderilecekKomut)>0 and IsSendByThread==0:
            return


        #Timer: 0,05-> 0,10 saniyede gelsin.... 80|81
        WakeUpCountDivider=3
        if G_Machine_DeviceTypeId==8:
            WakeUpCountDivider=2

        if G_Machine_DeviceTypeId==1:
            WakeUpCountDivider=1

        if G_Machine_SasPoolingVersion==1:
            WakeUpCountDivider=2


        #2021-09-13
        WakeUpCountDivider=2

        #2021-10-09
        WakeUpCountDivider=1




        if G_Machine_DeviceTypeId==11:
            WakeUpCountDivider=1
            IsNewPooling=1


        Send81=1

        LastAFTOperationDateDiff = (datetime.datetime.now()-G_LastAFTOperationDate).total_seconds()
        if (IsWaitingForBakiyeSifirla==1 or IsWaitingForParaYukle==1 or IsWaitingForBakiyeSorgulama==1 or IsWaitingForMeter==1)==True and LastAFTOperationDateDiff<3:
            G_LastAFTOperationDate=datetime.datetime.now()
            G_LastCashoutPressedDate=datetime.datetime.now()

        Diff_LastCashoutPressedDate=(datetime.datetime.now()-G_LastCashoutPressedDate).total_seconds()


        Last80=int((datetime.datetime.now()-G_Last_80).total_seconds() * 1000)
        Last81=int((datetime.datetime.now()-G_Last_81).total_seconds() * 1000)
        DoPoolingInAnyCase=0




        LastStep_DoSASPoolingMsg="0.1"



        DoPolling=1
        if Diff_LastCashoutPressedDate<4:
            Send81=0
            DoPolling=0
            if G_Sas_DoNotPool==0:
                print("Do not poll because of Diff_LastCashoutPressedDate", Diff_LastCashoutPressedDate)
                G_Sas_DoNotPool=1
            WakeUpCountDivider=4
        else:
            G_Sas_DoNotPool=0

        
        #2021-10-13: Yeni ekledim. 1 Dk'dan fazla ise;
        if Last80>(1000*60):
            DoPolling=1


        if (SendWakeUp==1 and len(GENEL_GonderilecekKomut)==0 and (WakeUpCount%WakeUpCountDivider==0)) or DoPoolingInAnyCase==1:
            LastStep_DoSASPoolingMsg="0.2"

            #if WakeUpCount%5==0:
            #    Send81=0



            Is81Sent=0

            if Sas_LastSent==80 and Send81==1 and DoPolling==1:
                SendSASCommand("81")#rte icin
                Sas_LastSent=81
                Is81Sent=1

            if Is81Sent==0 and DoPolling==1:
                SendSASCommand("80")#long pool
                Sas_LastSent=80



            if WakeUpCount>1000000:
                WakeUpCount=0

            time.sleep(0.02)






        LastStep_DoSASPoolingMsg="0.3"
        IsMessageSent=0
        if IsSendByThread==1 and len(GENEL_GonderilecekKomut)>0:
            SendCommandIsExist()
            IsMessageSent=1
            
            if G_Machine_DeviceTypeId==1:
                time.sleep(0.09)
            else:
                time.sleep(0.03)

            #if (GENEL_GonderilecekKomut[0:3]=="017")==True:
            #    time.sleep(0.019)
            #else:
            #    time.sleep(0.019)


        LastStep_DoSASPoolingMsg="0.4"
        SasReadingVersion=1

        #print("SAS", isInit, "G_Machine_SasPoolingVersion", G_Machine_SasPoolingVersion)
        if isInit==0 and SasReadingVersion==1:
            tFoundMessages = []
            LastStep_DoSASPoolingMsg="0.5"
            #SendWakeUp=1

            IsACKMessage=0

            while 1:
                data_left = sasport.inWaiting()
                LastStep_DoSASPoolingMsg="0.6"
                if data_left==0:
                    LastStep_DoSASPoolingMsg="0.7"
                    break

                tdata = GetDataFromSasPort(IsMessageSent)
                LastStep_DoSASPoolingMsg="2-" + tdata

                if (tdata=="01FF001CA5" or tdata=="01FF1F6A4D" or tdata=="00" or tdata=="1F")==False:
                    print("RXA", tdata)

                if tdata[0:10]=="01FF1F6A4D" and len(tdata)>10:
                    tdata=tdata.replace("01FF1F6A4D","")


                while tdata[0:4]=="0101":
                    print("fazla 1..")
                    #print("**********************************************")
                    #print("1. FAZLADAN GELEN 01'i silelim!!!", tdata)
                    tdata=tdata[2:len(tdata)]
                    #print("1. FAZLADAN GELEN 01'i sildik!!!", tdata)
                    #print("**********************************************")

                LastStep_DoSASPoolingMsg="3-" + tdata
                messageFound=""
                messageFoundCRC=""
                messageRestOfMessage=""
                messageImportant=0
                messageFound, messageFoundCRC, messageRestOfMessage , messageImportant= ParseMessage(tdata)
                LastStep_DoSASPoolingMsg="4-" + tdata


                if len(messageFoundCRC)==4:
                    G_SASLastDate=datetime.datetime.now()
                    if messageFound=="01FF001CA5" or messageFound=="01FF1F6A4D" or messageFound=="01FF5110E6":
                        G_Machine_IsSASPortFound=1
                        G_SASLastDate=datetime.datetime.now()
                    #else:
                    #    print("Gelen msg:", messageFound)
                else:
                    #<CRC'si yok. Yani daha mesajin hepsi gelmemis>
                    TryCountCRC=0
                    TryCountCRCTolerance=5
                    if messageFound[0:4]=="0172" or messageFound[0:4]=="0174" or messageFound[0:4]=="01AF":
                        TryCountCRCTolerance=10

                    while len(messageFoundCRC)<4 and TryCountCRC<TryCountCRCTolerance and (len(messageFound)>4 or messageFound=="01"):
                        TryCountCRC=TryCountCRC+1
                        if TryCountCRC>TryCountCRCTolerance:
                            print("CRC VAZGEC!*************************************")
                            break
                        time.sleep(TimeSleepForInterByte+0.002)
                        newreceivedmsg=GetDataFromSasPort(IsMessageSent)
                        tdata=tdata+newreceivedmsg

                        if tdata=="01FF885CAD":
                            break

                        while tdata[0:4]=="0101":
                            print("**********************************************")
                            print("FAZLADAN GELEN 01'i silelim!!!", tdata)
                            tdata=tdata[2:len(tdata)]
                            print("FAZLADAN GELEN 01'i sildik!!!", tdata)
                            print("**********************************************")

                        if len(tdata)>2:
                            print("***** CRC YOKTU! New message              ", tdata)
                        messageFound, messageFoundCRC, messageRestOfMessage, messageImportant = ParseMessage(tdata)
                        #if len(messageFoundCRC)==4:
                        #    print("Kalan mesaji aldik :)))")
                    #</CRC'si yok. Yani daha mesajin hepsi gelmemis>
                if len(tFoundMessages)<20:
                    tFoundMessages.append(messageFound)

                LastStep_DoSASPoolingMsg="5-" + tdata

                #print("messageFound             ", messageFound)
                #print("messageFoundCRC          ", messageFoundCRC)
                #print("messageRestOfMessage     ", messageRestOfMessage)
                #print("----------------")




               
                if len(tdata)==0:
                    return



                if len(tFoundMessages)>1:
                    print("Total Bulunan", len(tFoundMessages))
                i=0
                while i<len(tFoundMessages):
                    message=tFoundMessages[i]
                    i=i+1
                    
                    if IsShowEveryMessage==1:
                        print("Gelen msg ", message)

                    if G_Program_LogAllSAS==1 and message!="00":
                        try:
                            SQL_Safe_InsTraceLog("SAS","RX",message)
                        except Exception as exLog:
                            print("EX LOG")



                    if message=="00" or message=="1F" or message=="01FF001CA5" or message=="FF001CA5" or message=="01FF1F6A4D" or message=="01FF709BD6" or message=="01FF3B4C2A" or message=="01FF5110E6" or message=="01FF1F6A4D" or message=="01":
                        G_SASLastDate=datetime.datetime.now()
                        continue

                    if message[0:4]=="0172" or message[0:4]=="0173" or message[0:4]=="0174" or message[0:4]=="01FF":
                        IsACKMessage=1
                        G_SAS_LastAFTAnswerDate=datetime.datetime.now()

                    #GameStarted Ended Reel stopped
                    if message[0:6]=="01FF7E" or message[0:6]=="01FF7F" or message[0:6]=="01FF88" or message[0:6]=="01FF00":
                        IsACKMessage=0

                    #Ilk geleni 72 ama oncesi yoksa; bunun basina makina numarasini ekle... onemli
                    #FF4F: Bill acceptor
                    if (message.startswith("72")==True or message.startswith("73")==True or message.startswith("FF4F")==True or message.startswith("74")==True or message.startswith("7E")==True or message.startswith("7F")==True or message.startswith("2F")==True or message.startswith("B5")==True) and len(message)>50:
                        message="01"+ message

                    if IsShowEveryMessage==0:
                        print("SAS RX", message, datetime.datetime.now())
                    
                    G_SASLastDate=datetime.datetime.now()


                    thread1 = Thread(target = DoConsumeSASMessage, args = (message, ))
                    thread1.name="DoConsumeSASMessage2"
                    thread1.start()
                    time.sleep(0.009)#2021-11-17

                break;

            #2021-10-14 Actim yine ne gerek varsa
            #IsACKMessage=0#2021--10-05 Kapattim. Ne gerek var ya Ackekd vs.?
            if IsACKMessage==1:
                #time.sleep(0.02)#2021-11-22 Kaldirdim.
                print("ACK Spark ACKED!")
                SendSASCommand("80")
                #Is81Sent=0
            #burada gelen mesaji isle...
            #mevo


        if isInit==0 and SasReadingVersion==0:
            SendWakeUp=1
            
            tdata=""

            while 1:
                IsWaitingLoopOnSASPooling=1

                if IsNewPooling==1:

                    data_left = sasport.inWaiting()
                    if data_left==0:
                        break

                    out = ''
                    ReadCountTimeOut=4
                    while ReadCountTimeOut>0:
                        ReadCountTimeOut=ReadCountTimeOut-1
                        
                        while sasport.inWaiting() > 0:
                            out+=sasport.read_all().hex()
                            time.sleep(0.005)

                    if out == '':
                        continue
                    tdata=out




                if IsNewPooling==0:
                    data_left = sasport.inWaiting()
                    if data_left==0:
                        #print("BREAK!!!!!!")
                        break

                    readtry=0
                    #print("READ SAS PORT!!!")
                    #tdata = sasport.read().encode('hex')
                    tdata=tdata+sasport.read_all().hex()
                    
                    if G_Machine_DeviceTypeId!=11:
                        time.sleep(0.01)

                    data_left = sasport.inWaiting()
                    while data_left>0:
                        tdata=tdata+sasport.read_all().hex()

                        if G_Machine_DeviceTypeId==11:
                            time.sleep(0.005)
                        else:
                            time.sleep(0.04)
                        data_left = sasport.inWaiting()


                IsWaitingLoopOnSASPooling=0
                tdata=tdata.upper()

                if tdata[0:4]=="01FF":
                    G_SASLastDate=datetime.datetime.now()
                    G_Machine_IsSASPortFound=1

                if (tdata=="01FF1F6A4D" or tdata=="01FF001CA5" or tdata=="01FF1F6A4D")==False:
                    print("SAS GELEN", tdata)


                #Reel N has stopped
                if tdata.startswith("01FF88")==True and G_Machine_IsRulet==0:
                    return

                #Ilk geleni 72 ama oncesi yoksa; bunun basina makina numarasini ekle...
                if tdata.startswith("72")==True and len(tdata)>75:
                    tdata="01"+ tdata



                #01FF001CA5: No Activity    01FF709BD6:Exception buffer overflow
                if tdata=="01FF001CA5" or tdata=="FF001CA5" or tdata=="01" or tdata=="0101" or tdata=="01FF709BD6":
                    G_SASLastDate=datetime.datetime.now()
                    return

                #01FF1F6A4D: No activity and waiting for player input
                if tdata=="01FF1F6A4D":
                    G_SASLastDate=datetime.datetime.now()
                    return

                #01FF3B4C2A: Low backup battery detected
                if tdata=="01FF3B4C2A":
                    G_SASLastDate=datetime.datetime.now()
                    return


                
                while tdata.startswith("0101")==True:
                    print('x6')
                    tdata=tdata[2:len(tdata)]

                while tdata.startswith("8081")==True:
                    print('x3')
                    tdata=tdata[4:len(tdata)]

                while (tdata.startswith("01FF001CA5")==True):
                    tdata=tdata[10:len(tdata)]

                while (tdata.startswith("01FF5110E6")==True):
                    tdata=tdata[10:len(tdata)]

                while (tdata.startswith("01FF3B4C2A")==True):
                    print('x2')
                    tdata=tdata[10:len(tdata)]

                while (tdata.startswith("FF1F6A4D")==True):
                    print('x8')
                    tdata=tdata[8:len(tdata)]



                while (tdata.startswith("8001")==True or tdata.startswith("8101")==True or tdata.startswith("0101")==True or tdata.startswith("01010174")==True or tdata.startswith("010174")==True or tdata.startswith("01010172")==True or tdata.startswith("010172")==True or tdata.startswith("8101FF001CA5")==True or tdata.startswith("0101FF1F6A4D")==True or tdata.startswith("0101")==True or tdata.startswith("6A0174")==True or tdata.startswith("51")==True or tdata.startswith("00")==True or tdata.startswith("010174")==True or tdata.startswith("0100")==True or tdata.startswith("1F01")==True)==True and len(tdata)>9:
                    tdata=tdata[2:len(tdata)]

                if len(tdata)==0:
                    return

                if G_Machine_IsRecordAllSAS==1 and len(tdata)>3:
                    SQL_Safe_InsSentCommands("Sent",tdata)



                break;




            if tdata=="8081":
                G_SASLastDate=datetime.datetime.now()
                return

            if tdata=="80":
                G_SASLastDate=datetime.datetime.now()
                return

            if tdata=="81":
                G_SASLastDate=datetime.datetime.now()
                return

            
            if (tdata=="1F" or tdata=="00" or tdata=="01" or tdata=="55" or tdata=="51" or tdata=="0100" or tdata=="0151" or tdata=="51FF")==False and len(tdata)>0:


                if tdata.startswith("01FF")==False:
                    print("SAS GELEN:", tdata, datetime.datetime.now())


                if tdata.startswith("01FF001CA501"):#No activity
                    tdata=tdata.replace("01FF001CA5","")

                if tdata.startswith("01FF1F6A4D01"):#no activity and waiting for player input
                    tdata=tdata.replace("01FF1F6A4D","")

                G_SASLastDate=datetime.datetime.now()
                thread1 = Thread(target = DoConsumeSASMessage, args = (tdata, ))
                thread1.name="DoConsumeSASMessage1"
                thread1.start()


    except Exception as e:
        debugpointtt=1
        #ExceptionHandler("DoSASPoolingMsg",e,0)


def DoConsumeSASMessage(tdata):
    HandleReceivedSASCommand(tdata)


#sender: 0: realcard exit, 1:removecardcommand 4: Cashout button is pressed
def IsAvailableForCashout(sender):
    global IsAvailableForCashoutButton
    global G_LastGameEnded
    global IsSasPortJustOpened

    if IsSasPortJustOpened==1:#newx
        IsSasPortJustOpened=0
        #SQL_InsImportantMessage("SAS message came after new port opening",1)

    if sender==4:
        return 1


    LastGameEndedDiff=(datetime.datetime.now()-G_LastGameEnded).total_seconds()


    #2018-12-28 fasttransfer
    #if G_Machine_DeviceTypeId==1 and G_Machine_GameStartEndBalance>5:
    #    print("......")

    if IsAvailableForCashoutButton==1 and (IsCardInside==1 or sender==1) and LastGameEndedDiff>1:
        return 1

    if G_LastGame_IsFinished==1:
        return 1
    
    print("IsAvailableForCashoutButton " , IsAvailableForCashoutButton , "IsCardInside:" , IsCardInside, " LastGameEndedDiff:", LastGameEndedDiff)
    return 0


def CreateTextFile(filename,content):

    try:
        ExecuteLinuxCommand("rm " + filename)
    except Exception as esql:
        print("Delete File:" + filename)

    try:
        f = open(filename, "a")
        f.write(content)
        f.close()

        #strCommand="echo \""+content+"\" > " + filename
        #print("strCommand", strCommand)
        #ExecuteLinuxCommand(strCommand)
    except Exception as esql:
        print("Create File:" + filename)



def Yanit_RegisterAFT(Yanit):
    global G_Device_AssetNo
    global AssetNumberInt
    index=0
    Address=Yanit[ index : index+2]
    index=index+2
    
    Command=Yanit[ index : index+2]
    index=index+2
    
    Length=Yanit[ index : index+2]
    index=index+2
    
    RegistrationStatus=Yanit[ index : index+2]
    index=index+2
    RegistrationStatusText=""
    if RegistrationStatus=="00":
        RegistrationStatusText="Registration Ready"
    if RegistrationStatus=="01":
        RegistrationStatusText="Registered"
    if RegistrationStatus=="40":
        RegistrationStatusText="Registration Pending"
    if RegistrationStatus=="80":
        RegistrationStatusText="Not Registered"
    
    AssetNumber=Yanit[ index : index+8]
    index=index+8
    
    AssetNumberInt=ReadAssetToInt(AssetNumber)
    
    RegistrationKey=Yanit[ index : index+40]
    index=index+40

    # Mehmet 28.05.2025
    print("Yanit:", Yanit)
    print("RegistrationKey:", RegistrationKey)

    if len(RegistrationKey)>20:
        print("*****************ASSET NUMBER IS SET!")
        G_Device_AssetNo=AssetNumberInt

    #2020-11-27
    CreateTextFile("/home/soi/dev/spark-sas2/assetno.txt",str(AssetNumberInt))

    print("RegistrationStatus:", RegistrationStatus, "RegistrationStatusText: ", RegistrationStatusText, "AssetNumber:", AssetNumber, "AssetNumberInt:", AssetNumberInt, "RegistrationKey", RegistrationKey  )
    SQL_UpdAssetNoSMIB(AssetNumberInt)
    if RegistrationStatus=="80":
        Config.set('sas','assetnumber', AssetNumber)
        SaveConfigFile()
        #SQL_DeviceStatu(1)#AssetNumarasini ogrensin
        print("**************** Register yap!!!!!!!!!!!!!!")
        #Komut_RegisterAssetNo()


def Billacceptor_OpenThread(sender):
    global G_LastGameEnded
    LastGameEndedDiff=(datetime.datetime.now()-G_LastGameEnded).total_seconds()

    #billacceptor ac
    BillAcceptor_Inhibit_Open()

def BillAcceptor_GameEnded():
    global G_LastGameEnded
    LastGameEndedDiff=(datetime.datetime.now()-G_LastGameEnded).total_seconds()

    BillAcceptor_Inhibit_Open()

    #thread1 = Thread(target = SQL_UpdDeviceIsLocked, args = (1, ))
    #thread1.name="GameEnded"
    #thread1.start()



def BillAcceptor_GameStarted():
    global G_LastGameEnded
    LastGameEndedDiff=(datetime.datetime.now()-G_LastGameEnded).total_seconds()

    #Billacceptor Close
    BillAcceptor_Inhibit_Close()




G_Count_AFT_YanitHandle=0
G_Count_AFT_TransferIsCompleted=0
IsHandleReceivedSASCommand=0
G_Wagered=0
Last_SAS_AcceptedBillAcceptorMessage=""
IsHandpayOK=0
Prev_Wagered=Decimal(0)
def HandleReceivedSASCommand(tdata):
    try:
        global G_Count_AFT_YanitHandle
        global G_Count_AFT_TransferIsCompleted
        global IsHandleReceivedSASCommand
        IsHandleReceivedSASCommand=1
        global G_LastCashoutPressedDate
        global G_Wagered
        global G_Machine_IsSASPortFound
        global Log_TotalCoinInMeter
        global IsWaitingForParaYukle
        global IsWaitingForBakiyeSifirla
        global IsAvailableForCashoutButton
        global G_LastGameEnded
        global G_SelectedGameId
        global G_SelectedGameName
        global G_Machine_Balance
        global G_Machine_Promo
        global IsHandpayOK
        global G_Machine_GameStartEndBalance
        global Last_SAS_AcceptedBillAcceptorMessage
        global G_LastGame_Action
        global G_LastGameStarted
        global G_LastGame_IsFinished
        global G_Machine_SASVersion
        global G_TrustBalance
        global G_Machine_NewGamingDay
        global G_Machine_WagerName
        global G_Machine_WagerIndex
        global G_Machine_CalcBetByTotalCoinIn
        
        global IsCardReaderBusy
        global G_Machine_BonusId
        global G_Machine_BonusAmount

        global Prev_Wagered

        global Global_Count_YanitHandle

        MessageName=""
        AnswerCommandName=""

        tdata=tdata.replace(" ","")
        IsProcessed=0
        IsSave2DB=1

        EventId=0
        EventName=""


        if G_Machine_IsRecordAllSAS==1:
            SQL_InsReceivedMessage(tdata,0,"")
        
        if tdata.startswith("01720200C0C31B"):
            IsProcessed=0
            IsSave2DB=1
            #print("Yine geldi bu:" , tdata)
            #Komut_Interragition("Yine gelen 01720200C0C31B")
            #SQL_InsImportantMessage("01720200C0C31B Not compatible with current transfer in progress",1)

        if tdata=="01FF838F13":
            return

        if tdata=="01FF001CA501FF001CA5" or tdata=="01FF001CA501":
            return

        if tdata=="81":
            return

        if tdata=="01FF820602":
            print("Display meters or attendant menu has been entered")
            return

        if tdata=="01FF201E84":
            print("General tilt")
            return

        if tdata=="0101FF001CA5":
            return

        if tdata[0:6]=="01FF1F":    #01FF1F6A4D
            #print("send gaming machine id - information", tdata)
            return



        if tdata.startswith("01FF7C")==True:
            IsSave2DB=1
            IsProcessed=1
            Yanit_LegacyBonusPay(tdata)

        if tdata.startswith("01FF6B")==True:
            IsSave2DB=1
            IsProcessed=1
            print("AFT request for host to cash out win")
            SQL_InsImportantMessageByWarningType("AFT request for host to cash out win*********",8,0)

        if tdata.startswith("01FF6C")==True:
            IsSave2DB=1
            IsProcessed=1
            print("AFT request to register")
            SQL_InsImportantMessageByWarningType("AFT request to register",8,24)

        if tdata.startswith("011B")==True:
            IsSave2DB=1
            IsProcessed=1
            #2020-01-06
            print("HandpayInformation")
            SQL_InsImportantMessageByWarningType("HandpayInfo" + tdata,8,0)
            Yanit_HandpayInfo(tdata)
            GetMeter(0,"Handpay")


        if tdata.startswith("0153")==True:
            IsSave2DB=1
            IsProcessed=1
            #2020-01-26
            print("GameConfiguration")
            #SQL_InsImportantMessageByWarningType("GameConfiguration" + tdata,8,0)
            Yanit_GameConfiguration(tdata)
            return


        if tdata.startswith("01731D")==True:
            IsSave2DB=1
            IsProcessed=1
            print("Register Gaming Machine Response")
            Yanit_RegisterAFT(tdata)
            return

        if tdata.startswith("01FF6FED3E")==True:
            print("*****************Game locked!******************")
            #2020-01-30: Game Locked geldigi icin kabul ediyoruz bunu genelde. Kabul etme!!
            #G_TrustBalance=datetime.datetime.now()

            IsSave2DB=0
            IsProcessed=1

            if IsCardInside==0:
                print("<Komut_CancelBalanceLock> *********************************************************************")
                Komut_CancelBalanceLock()
                print("</Komut_CancelBalanceLock> *********************************************************************")
            return
            #SQL_InsImportantMessageByWarningType("Game locked",8,23)

        if tdata[0:10]=="01FF5110E6":#ogren
            #sor:bu nedir acaba? neden handpay is pending diyor. surekli bu geliyor.
            #PrintAndSetAsStatuText("Handpay is pending")
            IsSave2DB=0
            IsProcessed=1
            print("Handpay is pending")
            SQL_InsImportantMessageByWarningType("Handpay is pending",8,11)
            SAS_SendCommand("SendHandpayInfo",GetCRC("011B"),0)

        if tdata[0:10].startswith("01FF52")==True:
            #sor:bu nedir acaba? neden handpay is pending diyor. surekli bu geliyor.
            #savoy'da gordum ki, handpay yapildiktan sonra bi kac kez geliyor.
            PrintAndSetAsStatuText("Handpay was reset")
            IsSave2DB=1
            IsProcessed=1
            SQL_InsImportantMessageByWarningType("Handpay was reset",8,26)
            GetMeter(0,"Handpay")
            SAS_SendCommand("SendHandpayInfo",GetCRC("011B"),0)




        if tdata[0:4]=="012F" or tdata[0:4]=="01AF":
            IsSave2DB=0
            IsProcessed=1
            Yanit_MeterAll(tdata)

        if tdata[0:4]=="0172":


            IsNotCompatibleTransfer=0
            if tdata.startswith("01720200C0C31B")==True:
                print("Islem yap")
                IsNotCompatibleTransfer=1

                print("*******************************")
                print("*******************************")
                print("*******************************")
                print("*******************************")
                print("01720200C0C31B geldi!!!!!!!!!!")
                print("*******************************")
                print("*******************************")
                #GUI_ShowIfPossibleMainStatu("Not compatible with current transfer in progress")
                #time.sleep(1)

                #if IsWaitingForBakiyeSifirla==1 and IsWaitingForParaYukle==1:
                #    SQL_InsImportantMessageByWarningType("C0 Statu, Sifirla=1,Yukle=1",1,1)

                #if IsWaitingForBakiyeSifirla==0 and IsWaitingForParaYukle==1:
                #    SQL_InsImportantMessageByWarningType("C0 Statu, Sifirla=0,Yukle=1",1,1)
                #    ProcessType="Yukle"

                #if IsWaitingForBakiyeSifirla==1 and IsWaitingForParaYukle==0:
                #    SQL_InsImportantMessageByWarningType("C0 Statu, Sifirla=1,Yukle=0",1,1)
                #    ProcessType="Sifirla"

                #if IsWaitingForBakiyeSifirla==0 and IsWaitingForParaYukle==0:
                #    SQL_InsImportantMessageByWarningType("C0 Statu, Sifirla=0,Yukle=0",1,1)


            if tdata[12:14]=="80":
                print("********** Para sifirlama yanit")
            else:
                print("********** Para yukleme yanit")

            IsParaSilme=0
            if (tdata[12:14]=="80" or tdata[12:14]=="90" or IsNotCompatibleTransfer==1) and G_SAS_LastAFTOperation=="Sifirla":
                IsParaSilme=1
                print("Para silme yaniti", tdata)
                IsProcessed=1
                IsSave2DB=1
                #debug print("Para Sifirlama Yanit")
                MessageName="CashoutAnswer"
                AnswerCommandName="Cashout"
                Yanit_ParaSifirla(tdata)
            
            if (tdata[12:14]=="00" or tdata[12:14]=="10" or tdata[12:14]=="11" or IsNotCompatibleTransfer==1) and (G_SAS_LastAFTOperation=="Yukle" and IsParaSilme==0):
                #print("Para yukleme yaniti", tdata)
                IsProcessed=1
                IsSave2DB=1
                if tdata[12:14]=="00":
                    print("Para Yukleme Yanit", tdata)
                    
                if tdata[12:14]=="10" or tdata[12:14]=="11":
                    print("Para Yukleme / Bonus Jackpot Yanit", tdata)

                MessageName="ParaYuklemeYanit"
                AnswerCommandName="ParaYukle"
                Yanit_ParaYukle(tdata)



            if IsProcessed==0:

                try:
                    if G_SAS_LastAFTOperation=="Sifirla":

                        Last80=int((datetime.datetime.now()-G_Last_80).total_seconds() * 1000)
                        Last81=int((datetime.datetime.now()-G_Last_81).total_seconds() * 1000)
                        EkInfo=" 80(" + str(Last80) + ")/" + "81(" + str(Last81) + ")"
            
                        SQL_Safe_InsImportantMessage("Send erase command again! " + str(Sas_LastSent) + EkInfo,68)
                        print("Sifirla komutu gonder tekrar!!!!!!!!!!!! Yanit handle!" + str(Sas_LastSent) + EkInfo, "G_Count_AFT_YanitHandle", G_Count_AFT_YanitHandle)
                        G_Count_AFT_YanitHandle=G_Count_AFT_YanitHandle+1

                        time.sleep(0.0389)

                        if G_Count_AFT_YanitHandle%5==0:
                            SQL_Safe_InsImportantMessageByWarningType("Yanit handle 5 times!",10,0)
                            Komut_ParaSifirla(1)
                        else:
                            Komut_ParaSifirla(0)

                    if G_SAS_LastAFTOperation=="Yukle" and Global_Count_YanitHandle>9 and Global_Count_YanitHandle%10==0 and G_Machine_IsRulet==1:
                        Wait_Bakiye(2,1,"cardexit2")
                        if Yanit_BakiyeTutar==0:
                            SQL_Safe_InsImportantMessageByWarningType("Roulette cashin error-1",10,0)
                            SQL_Safe_InsImportantMessage("Send cashin command again!",68)
                            print("Para yukleme komutu gonder tekrar!!!!!!!!!!!")
                            Komut_ParaYukle(0, Last_ParaYukle_TransferType)

                    try:
                        Global_Count_YanitHandle=Global_Count_YanitHandle+1
                        SQL_InsImportantMessage("%s%s" % ("YanitHandle:", tdata),1)
                    except Exception as eYukle:
                        print("handle error!!!!")

                

                    if len(tdata)>127:
                        print("it might be answer to interragiton")
                        SQL_InsReceivedMessage(tdata,0,"interragiton")

                except Exception as eYukle2:
                    print("Eerr")


        if tdata[0:4]=="0174":
            IsProcessed=1
            #print("Bakiye Sorgulama Yanit")
            MessageName="MoneyQueryAnswer"
            AnswerCommandName="MoneyQuery"
            Yanit_BakiyeSorgulama(tdata)




        if tdata.startswith("01FF54BDB1")==True:
            IsProcessed=1
            IsSave2DB=0
            #Komut_BakiyeSorgulama(13,1,"bu ne acaba")
            #SQL_InsImportantMessageByWarningType("Progressive win!",1,15)
            

        if tdata=="01FF29DF19":
            EventId=1
            EventName="Bill acceptor hardware failure!"
            IsProcessed=0
            IsSave2DB=0
            SQL_InsImportantMessageByWarningType("Bill acceptor hardware failure!",1,16)

        if tdata=="00":
            IsProcessed=1
            IsSave2DB=0

        if tdata=="01":
            IsProcessed=1
            IsSave2DB=0

        if tdata=="51":
            IsProcessed=1
            IsSave2DB=1

        ##if tdata=="69" or tdata.startswith("01FF69DB5B")==True:
        if tdata.startswith("01FF69DB5B")==True or tdata=="FF69DB5B" or tdata=="69DB5B" or tdata=="69":
            IsProcessed=1
            IsSave2DB=1
            G_Count_AFT_TransferIsCompleted=G_Count_AFT_TransferIsCompleted+1
            if G_Count_AFT_TransferIsCompleted%10000000==0:
                G_Count_AFT_TransferIsCompleted=0

            #PrintAndSetAsStatuText("AFT Transfer is completed")
            print("AFT Transfer is completed******************************** AMA KABUL ETME!", tdata)
            
            #Sanki 81 gondermem gerekiyor.

            Last80=int((datetime.datetime.now()-G_Last_80).total_seconds() * 1000)
            Last81=int((datetime.datetime.now()-G_Last_81).total_seconds() * 1000)
            EkInfo=" 80(" + str(Last80) + ")/" + "81(" + str(Last81) + ")"
            
            SQL_Safe_InsImportantMessage("AFT Transfer is completed " + str(Sas_LastSent) + EkInfo, 93)



            #if IsWaitingForBakiyeSifirla==1:
            #    IsWaitingForBakiyeSifirla=0
            #    SQL_Safe_InsImportantMessage("Cashout is completed by AFT",93)

            ##2019-04-26 Zoom ruletlerde bazen double kredi acma oluyor transactionId yuzunden
            #if IsWaitingForParaYukle==1:# and G_Machine_DeviceTypeId==5:
            #    IsWaitingForParaYukle=0
            #    SQL_Safe_InsImportantMessage("Cashin is completed by AFT",94)
            #    #SQL_InsImportantMessageByWarningType("Zoom AFT Transfer is completed!",1,20)
            
            # and
            if 0==0 and (IsWaitingForParaYukle==1 or IsWaitingForBakiyeSifirla==1 or G_Count_AFT_TransferIsCompleted%2==0)==True:
                Komut_Interragition("Interragition- for AFT Comp.")

        #if tdata=="01FF66" or tdata=="4069" or tdata=="2CA3" or "01FF662CA3" in tdata:
        if tdata.find("01FF66") != -1:
            IsSave2DB=1
            IsProcessed=0
            #PrintAndSetAsStatuText("Cashout is pressed. EFT Request")
            print('*************************************')
            print("tdata", tdata)
            print("Cash out button pressed or Hopper Limit Reached is pressed",IsAvailableForCashoutButton,IsCardInside)
            #2020-06-05: Bakiye sorgulama gonderelim.


            #2020-06-01: Gerek yok.
            ##oyun oynadiysa ve sadece game ended geldiyse kabul et...
            
            #2021-07-09 Kapattik. 66'da degil, 6A'da yapicaz. Ama Apex'lerde acik
            if G_Machine_DeviceTypeId==10:
                print("Cashout yapilabilinir-EFT")
                Komut_CollectButtonProcess()


        if tdata[0:6]=="01FF8A":
            EventId=2
            EventName="Game Recall Entry Displayed"
            IsSave2DB=0
            IsProcessed=1
            print('Game Recall Entry Displayed')

        if tdata[0:4]=="0156":
            Yanit_EnabledGameNumbers(tdata)

        if tdata[0:6]=="01FF6A" or "01FF6A4069" in tdata:
            #AFT Request for host cashout
            Diff_LastCashoutPressedDate=(datetime.datetime.now()-G_LastCashoutPressedDate).total_seconds()
            if Diff_LastCashoutPressedDate>10:
                print("*****************************************************************")
                print("DO NOT POLL ANY MORE AT LEAST 10 SECOND **************************", Diff_LastCashoutPressedDate)
                print("*****************************************************************")
                print("*****************************************************************")
                G_LastCashoutPressedDate=datetime.datetime.now()

            IsSave2DB=1
            IsProcessed=1
            print('*************************************')
            PrintAndSetAsStatuText("Cashout is pressed")
            print("AFT request for host cashout.",IsAvailableForCashoutButton,IsCardInside)
            
            #20200605 kaldirdik
            #oyun oynadiysa ve sadece game ended geldiyse kabul et...
            #IsAvailableForCashout(4)
            if 1==1:
                Komut_CollectButtonProcess()


        if tdata[0:2]=="87":
            IsProcessed=0
            print("Gaming machine unable to perform transfers at this time")

        if tdata[0:4]=="011F" and len(tdata)>10:
            IsProcessed=0
            print("Send gaming machine ID & information")

        #00019400E124
        if tdata[0:6]=="019400":
            EventId=3
            EventName="Handpay is reseted"

            global IsWaitingForHandpayReset
            IsWaitingForHandpayReset=0
            IsProcessed=1
            IsHandpayOK=1
            print("Handpay is reseted")

        if tdata[0:4]=="0154":
            G_Machine_IsSASPortFound=1
            IsProcessed=0
            print("Makina seri no serial no ve sas versiyon")
            index=0
            Address=tdata[ index : index+2]
            index=index+2

            Command=tdata[ index : index+2]
            index=index+2

            Length=tdata[ index : index+2]
            index=index+2

            SASVersion=tdata[ index : index+6]
            index=index+6
            SASVersion=HEXNumberToInt(SASVersion)
            G_Machine_SASVersion=SASVersion
            print("SASVersion", SASVersion)

            LeftLength=len(tdata)-index-4
            SerialNumber=tdata[ index : index+LeftLength]
            index=index+LeftLength
            print("SerialNumber", SerialNumber)
            SerialNumber=HEXNumberToInt(SerialNumber)
            print("SerialNumber", SerialNumber)

            SQL_UpdDeviceSASSerial(SASVersion, SerialNumber)



        if tdata=="1F":
            IsSave2DB=0
            IsProcessed=1

 

        if tdata=="01FF001CA5" or tdata=="01FF1F6A4D" or tdata=="01FF709BD6":
            IsSave2DB=0
            IsProcessed=1
            #print("I dont know what it is... Real time reporting",tdata)
        
        if tdata[0:6]=="01FF88":
            IsSave2DB=0
            IsProcessed=1
            if G_Machine_DeviceTypeId>1:
                print("Reel N has stopped",tdata)


        if tdata[0:4]=="01B5":
            print("Game Info came!", tdata)
            Yanit_GameInfo(tdata)


        if tdata[0:6]=="01FF8C":
            try:
                G_SelectedGameId=int(tdata[6:10])
                G_SelectedGameName="MainScreen"
                #Log_TotalCoinInMeter=0
                Config.set("customer","selectedgameid",str(G_SelectedGameId))
                SaveConfigFile()
                #<Here get game info from db>#############################################
                if G_SelectedGameId>0:
                    try:
                        # Original MSSQL procedure: tsp_GetDeviceGameInfo
                        # Note: This procedure was not found in postgres-routines-in-sas.sql
                        # Using hybrid approach - queue operation instead of direct call
                        result = db_helper.queue_database_operation(
                            'tsp_GetDeviceGameInfo',
                            [G_Machine_DeviceId, G_SelectedGameId],
                            'get_device_game_info'
                        )

                        for row in result:
                            #2020-02-10 Oyun basina degil, genel TotalCoinIn'mis
                            #Log_TotalCoinInMeter=Decimal(row["TotalCoinIn"])
                            #print("Log_TotalCoinInMeter", Log_TotalCoinInMeter)

                            Config.set("customer","totalcoininmeter",str(round(Log_TotalCoinInMeter,2)))

                            try:
                                G_SelectedGameName=row['GameName']
                                print("G_SelectedGameName", G_SelectedGameName)
                                if len(G_SelectedGameName)==0:
                                    print("Learn game name command is sent!")
                                    SAS_SendCommand("GameName",GetCRC("01B5" + AddLeftBCD(G_SelectedGameId,2)),0)
                            except Exception as eGameName:
                                ExceptionHandler("Game Name Get Error!!",eGameName,0)

                    except Exception as ecardtype:
                        ExceptionHandler("tsp_GetDeviceGameInfo", ecardtype, 0)
                #<Here get game info from db>#############################################

                if len(G_SelectedGameName)==0:
                    G_SelectedGameName=str(G_SelectedGameId)
                SQL_Safe_InsImportantMessage("Game is selected: " + G_SelectedGameName ,95)

            except:
                print("Game selected error")

            IsSave2DB=0
            IsProcessed=1
            print("Game Selected", G_SelectedGameId)
            G_Machine_IsSASPortFound=1

        if tdata[0:4]=="01FF":
            G_Machine_IsSASPortFound=1

        if tdata[0:2]=="7E" or tdata[0:6]=="01FF7E":

            if tdata[0:2]=="7E" and len(tdata)>18:
                tdata="01FF" + tdata

            G_LastGame_IsFinished=0
            G_LastGame_Action=datetime.datetime.now()
            G_LastGameStarted=datetime.datetime.now()
            IsAvailableForCashoutButton=0
            playcount=0
            playcount=Config.getint("customer","playcount")
            playcount=playcount+1
            Config.set("customer","playcount",str(playcount))
        



            IsSave2DB=0
            IsProcessed=1
            G_Machine_GameStartEndBalance=G_Machine_GameStartEndBalance+1
            SetMachineStatu("Game started")
            G_Machine_IsSASPortFound=1
            if G_Machine_BillAcceptorTypeId>0 and IsBillAcceptorBusy==0:
                print("Bill acceptor kapat")
                BillAcceptor_GameStarted()
            
            if G_SelectedGameId==0:
                #print("Tek oyunlu makina galiba?**************************")
                G_SelectedGameId=1

            if tdata[0:6]!="01FF7E":
                print("RTE is not opened!")
                #2021-11-04 Kapattim ChangeRealTimeReporting(1)

            if tdata[0:6]=="01FF7E":
                try:
                    GamePromo=0
                    if G_Machine_IsRulet==1:
                        print("tdata[6:10] Wagered", tdata[6:10])
                    WagerType=tdata[18:20]
                    

                    BetFactor=1
                    try:
                        #Novomatikte 57,42,43 icin deneyelim olmazsa sadece
                        if WagerType=="41" or WagerType=="C1" or WagerType=="80":
                            BetFactor=1
                        if (WagerType=="57" or WagerType=="D7"):# and G_Machine_DeviceTypeId!=1:
                            BetFactor=2
                        if (WagerType=="42" or WagerType=="C2"):# and G_Machine_DeviceTypeId!=1:
                            BetFactor=5
                        if (WagerType=="43" or WagerType=="C3"):# and G_Machine_DeviceTypeId!=1:
                            BetFactor=10
                        if (WagerType=="40" or WagerType=="4B" or WagerType=="CB"):
                            BetFactor=20
                        if (WagerType=="45" or WagerType=="C5"):
                            BetFactor=50
                        if WagerType=="47":
                            BetFactor=500
                        if WagerType=="4C":
                            BetFactor=200
                        if WagerType=="46":
                            BetFactor=100




                        #2020-01-13: Factore bette gerek yok. Win'de gerek var. Novo: 0.05te gordum
                        #BetFactor=BetFactor*G_Machine_DefBetFactor

                        #2021-10-28
                        if G_Machine_Balance<0 or G_Machine_Promo<0:
                            Wait_Bakiye(11,1,"balancezero")

                    except Exception as e:
                        print('Hey you!!')



                    Wagered=(Decimal(tdata[6:10])*Decimal(BetFactor))/100
                    if Wagered<=0:
                        Wagered=0

                    G_Wagered=Wagered
                    

                    TotalCoinInMeter=tdata[10:18]
                    TotalCoinInMeterDecimal=0

                    Prev_Log_TotalCoinInMeter=0
                    try:
                        TotalCoinInMeterDecimal=(Decimal(TotalCoinInMeter)/100)*G_Machine_DefBetFactor
                        Prev_Log_TotalCoinInMeter=TotalCoinInMeterDecimal
                        if (Wagered==0 and Log_TotalCoinInMeter>0) or Wagered>999:
                            Wagered=TotalCoinInMeterDecimal-Log_TotalCoinInMeter
                            print("New Wagered", Wagered)
                            if Wagered>1000000:
                                Wagered=0
                            if Wagered<0:
                                Wagered=0

                        #mustafa
                        if G_Machine_CalcBetByTotalCoinIn==1 and TotalCoinInMeterDecimal>Log_TotalCoinInMeter and Log_TotalCoinInMeter>0:
                            NewWagered=TotalCoinInMeterDecimal-Log_TotalCoinInMeter
                            if NewWagered>0 and NewWagered<10001:
                                Wagered=NewWagered

                        Log_TotalCoinInMeter=TotalCoinInMeterDecimal
                    except Exception as e:
                        print("***** TOTAL COIN IN ERROR *****")

                    try:
                        if G_Machine_GameStartEndNotifications>0:
                            if G_Machine_DeviceTypeId==6 or G_Machine_DeviceTypeId==11:
                                GUI_ShowIfPossibleMainStatu("Game Started B:" + str(Wagered) + " WT:" + str(WagerType))
                            else:
                                GUI_ShowIfPossibleMainStatu("Game Started B:" + str(Wagered))
                    except Exception as eWager:
                        print('Hey you!!')

                    if G_Machine_CasinoPromoType==0:
                        if G_Machine_Promo>0:
                            if G_Machine_Promo<Wagered:
                                GamePromo=Decimal(G_Machine_Promo)
                                print("G_Machine_Promo", G_Machine_Promo, "Wagered", Wagered, "GamePromo", GamePromo)
                                G_Machine_Balance=Decimal(G_Machine_Balance)-Decimal(GamePromo)
                                G_Machine_Promo=0
                            else:
                                G_Machine_Promo=Decimal(G_Machine_Promo)-Wagered
                                GamePromo=Wagered
                        else:
                            G_Machine_Balance=Decimal(G_Machine_Balance)-Wagered
                    else:
                        if G_Machine_Promo>0:
                            WageredDivived=Wagered/2
                            if G_Machine_Promo<WageredDivived: # 5 lari, 2,5 divived. promo ise: 1 tl vardi.
                                GamePromo=Decimal(G_Machine_Promo)
                                G_Machine_Balance=Decimal(G_Machine_Balance)-(Decimal(Wagered)-Decimal(GamePromo))
                                G_Machine_Promo=0
                            else:
                                G_Machine_Promo=Decimal(G_Machine_Promo)-Decimal(WageredDivived)
                                G_Machine_Balance=Decimal(G_Machine_Balance)-Decimal(WageredDivived)
                                GamePromo=WageredDivived
                        else:
                            G_Machine_Balance=Decimal(G_Machine_Balance)-Wagered


                
                    Config.set("customer","currentbalance",str(round(G_Machine_Balance,2)))
                    Config.set("customer","currentpromo",str(G_Machine_Promo))
                    Config.set("customer","totalcoininmeter",str(round(Log_TotalCoinInMeter,2)))

                    TotalCoinIn=Decimal(tdata[10:18])/100
                    ProgressiveGroup=tdata[20:22]

                    try:
                        Config.set('game','wagered', str(Wagered))
                        Config.set('game','gamepromo', str(GamePromo))
                        Config.set('game','totalcoinin', str(TotalCoinIn))
                        Config.set('game','wagertype', str(WagerType))
                        Config.set('game','progressivegroup', str(ProgressiveGroup))
                        Config.set('game','starteddate', str(datetime.datetime.now()))
                    except:
                        print("Parse Error: ConfigSet Game")

                    totalbet=Decimal(Config.get("customer","totalbet"))
                    totalbet=totalbet+Wagered
                    Config.set("customer","totalbet",str(totalbet))

                
                    currentbonus=Decimal(Config.get("customer","currentbonus"))
                    bonuspercentage=Decimal(Config.get("customer","bonuspercentage"))
                    

                    try:
                        WagerBonusFactor=1
                        for member in G_Machine_WagerBonusFactors:
                            if Wagered>=Decimal(member['wager']):
                                WagerBonusFactor=Decimal(member['bonusfactor'])
                                G_Machine_WagerName=member['wagername']
                                G_Machine_WagerIndex=member['index']

                        #print("New Bonus Type!! "+G_Machine_WagerName+" Old:" , bonuspercentage, "Wagered", Wagered, "JackpotFactor", G_Machine_JackpotFactor, "WagerBonusFactor", WagerBonusFactor)

                        bonuspercentage=bonuspercentage*G_Machine_JackpotFactor*WagerBonusFactor
                        #print("New Bonus percentage", bonuspercentage)
                    except:
                        print("Err on new bonus type!!")

                    if G_Machine_IsBonusGives==1:
                        WonBonus=(bonuspercentage*Wagered/Decimal(1000))
                        currentbonus=currentbonus + WonBonus
                        earnedbonus=0
                        try:
                            earnedbonus=Decimal(Config.get("customer","earnedbonus"))
                        except:
                            print("Earned bonus error!")
                        earnedbonus=earnedbonus+WonBonus
                        Config.set("customer","earnedbonus",str(earnedbonus))
                
                    #print("currentbonus:" , currentbonus, "Wagered:" , Wagered, " Balance:", G_Machine_Balance , " Promo", G_Machine_Promo)
                    Config.set("customer","currentbonus",str(currentbonus))
                    print("Game started Wagered:", Wagered, tdata, "currentbonus,", currentbonus, "G_Machine_IsBonusGives", G_Machine_IsBonusGives, "bonuspercentage", bonuspercentage, "Wagered", Wagered, "G_Machine_CalcBetByTotalCoinIn", G_Machine_CalcBetByTotalCoinIn,"Log_TotalCoinInMeter", Log_TotalCoinInMeter, "Prev_Log_TotalCoinInMeter", Prev_Log_TotalCoinInMeter)
                    
                    #ExecuteJSFunction("KadranDegistir", str(int(Wagered)))

                    #TotalCoinIn gonderme, TotalWagered Gonder
                    SQL_InsGameStart(Wagered,0,totalbet,WagerType,ProgressiveGroup,GamePromo, playcount, TotalCoinInMeterDecimal)

                    DoUpdateBonus=0
                    if playcount%5==0:
                        DoUpdateBonus=1

                    if Wagered!=Prev_Wagered:
                        Prev_Wagered=Wagered
                        DoUpdateBonus=1

                    if GUI_CurrentPage=="GUI_ShowBonus" and DoUpdateBonus==1:
                        print("Update bonus")
                        GUI_UpdateBonus()
                    if GUI_CurrentPage=="GUI_ShowBalance":
                        GUI_CloseCustomerBalance()
                except:
                    print("Parse Error: GameStarted")

            #SaveConfigFile()

        

        if tdata[0:2]=="7F" or tdata[0:6]=="01FF7F":
            IsSave2DB=0
            IsProcessed=1
            IsAvailableForCashoutButton=1
            G_LastGameEnded=datetime.datetime.now()
            G_LastGame_Action=datetime.datetime.now()
            G_LastGame_IsFinished=1
            G_Machine_GameStartEndBalance=G_Machine_GameStartEndBalance-1

            if G_Machine_BillAcceptorTypeId>0 and IsBillAcceptorBusy==0:
                print("Bill acceptor ac")
                BillAcceptor_GameEnded()

            SetMachineStatu("Game is ended")
            G_Machine_IsSASPortFound=1
            
            if tdata[0:6]=="01FF7F":
                try:
                    WinAmount=Decimal(tdata[6:14])/100
                    WinAmount=WinAmount*G_Machine_DefBetFactor
                    
                    print("Game is ended WinAmount" , WinAmount, tdata)

                    if G_Machine_GameStartEndNotifications>0:
                        if WinAmount>0:
                            GUI_ShowIfPossibleMainStatu("Game is ended W:" + str(WinAmount))
                        else:
                            GUI_ShowIfPossibleMainStatu("Game is ended")

                    if IsHandpayOK==0:
                        G_Machine_Balance=Decimal(G_Machine_Balance)+WinAmount

                    if IsHandpayOK==1:
                        IsHandpayOK=0
                        if G_Machine_IsRulet==0:
                            SQL_UploadMoney(WinAmount,1)

                    Config.set("customer","currentbalance",str(G_Machine_Balance))
                    #print('WinAmount', WinAmount)
                    totalwin=Decimal(Config.get("customer","totalwin"));
                    totalwin=totalwin+WinAmount
                    Config.set("customer","totalwin",str(totalwin))

                    #isdebug print("Balance ", G_Machine_Balance , " Promo:", G_Machine_Promo)
                    SQL_InsGameEnd(WinAmount)
                    SQL_InsGameStartEnd(WinAmount)
                except:
                    print("Parse Error: GameStarted")

        if tdata[0:2]=="8C":
            IsSave2DB=0
            IsProcessed=0
            print("Oyun Ekranina girildi")


        #<POOL MESSAGES>--------------------------------------------------------------------
        IsPoolMsg=0
        if tdata=="11":
            IsPoolMsg=1
            PrintAndSetAsStatuText("Slot door was opened")

        if tdata=="12":
            IsPoolMsg=1
            PrintAndSetAsStatuText("Slot door was closed")

        if tdata=="13":
            IsPoolMsg=1
            PrintAndSetAsStatuText("Drop door was opened")

        if tdata=="14":
            IsPoolMsg=1
            PrintAndSetAsStatuText("Drop door was closed")

        if tdata=="15":
            IsPoolMsg=1
            PrintAndSetAsStatuText("Card cage was opened")

        if tdata=="16":
            IsPoolMsg=1
            PrintAndSetAsStatuText("Card cage was closed")

        if tdata=="17":
            IsPoolMsg=1
            PrintAndSetAsStatuText("AC power was applied to gaming machine")

        if tdata=="18":
            IsPoolMsg=1
            PrintAndSetAsStatuText("AC power was lost from gaming machine")

        if tdata=="19":
            IsPoolMsg=1
            PrintAndSetAsStatuText("Cashbox door was opened")

        if tdata=="1A":
            IsPoolMsg=1
            PrintAndSetAsStatuText("Cashbox door was closed")

        if tdata=="1B":
            IsPoolMsg=1
            PrintAndSetAsStatuText("Cashbox was removed")

        if tdata=="1C":
            IsPoolMsg=1
            PrintAndSetAsStatuText("Cashbox was installed")

        if tdata=="1D":
            IsPoolMsg=1
            PrintAndSetAsStatuText("Belly door was opened")

        if tdata=="1E":
            IsPoolMsg=1
            PrintAndSetAsStatuText("Belly door was closed")

        if tdata=="27":
            IsPoolMsg=1
            PrintAndSetAsStatuText("Cashbox full detected")

        if tdata=="29":
            IsPoolMsg=1
            PrintAndSetAsStatuText("Bill acceptor hardware failure")

        if tdata=="2A":
            IsPoolMsg=1
            PrintAndSetAsStatuText("Reserve bill detected")

        if tdata=="2B":
            IsPoolMsg=1
            PrintAndSetAsStatuText("Bill rejected")

        if tdata=="2E":
            IsPoolMsg=1
            PrintAndSetAsStatuText("Cashbox near full detected")

        if tdata=="6A":
            IsPoolMsg=1
            PrintAndSetAsStatuText("AFT request for host cashout")

        if tdata=="6B":
            IsPoolMsg=1
            PrintAndSetAsStatuText("AFT request for host to cash out win")

        if tdata=="6C":
            IsPoolMsg=1
            PrintAndSetAsStatuText("AFT request to register")

        if tdata=="6D":
            IsPoolMsg=1
            PrintAndSetAsStatuText("AFT registration acknowledged")

        if tdata=="6E":
            IsPoolMsg=1
            PrintAndSetAsStatuText("AFT registration cancelled")

        if tdata=="6F":
            IsPoolMsg=1
            PrintAndSetAsStatuText("Game locked")


        if IsPoolMsg==1:
            IsSave2DB=1
            IsProcessed=1

        #<POOL MESSAGES>--------------------------------------------------------------------

        #<DETAILED POOL MESSAGES>--------------------------------------------------------------------
        IsPoolMessageDetailed=0

        if tdata=="01FF862244":
            EventId=4
            EventName="Gaming machine is out of service (by attendant)"

            IsPoolMessageDetailed=1
            PrintAndSetAsStatuText("Gaming machine is out of service (by attendant)")
        
        if tdata=="01FF1114A4" or tdata=="11":
            GetMeter(0,"door open")
            EventId=5
            EventName="Slot door was opened"

            IsPoolMessageDetailed=1
            PrintAndSetAsStatuText("Slot door was opened")

            if G_Machine_BillAcceptorTypeId>0 and IsCardInside==1:
                BillAcceptor_Inhibit_Close()

        if tdata=="01FF128F96":
            EventId=6
            EventName="Slot door was closed"

            IsPoolMessageDetailed=1
            PrintAndSetAsStatuText("Slot door was closed")

            if G_Machine_BillAcceptorTypeId>0 and IsCardInside==1:
                BillAcceptor_Inhibit_Open()


        if tdata=="01FF130687":
            GetMeter(0,"door was opened")

            EventId=7
            EventName="Drop door was opened"

            IsPoolMessageDetailed=1
            PrintAndSetAsStatuText("Drop door was opened")

        if tdata=="01FF14B9F3":

            EventId=8
            EventName="Drop door was closed"

            IsPoolMessageDetailed=1
            PrintAndSetAsStatuText("Drop door was closed")
            

        if tdata=="01FF7B4868":
            EventId=9
            EventName="Bill validator period totals have been reset by an attendant"

            IsPoolMessageDetailed=1
            PrintAndSetAsStatuText("Bill validator period totals have been reset by an attendant")




        if tdata=="01FF820602":#82
            EventId=10
            EventName="Display meters or attendant menu has been entered"

            IsPoolMessageDetailed=1
            PrintAndSetAsStatuText("Display meters or attendant menu has been entered")

        if tdata=="01FF843067":#84
            EventId=11
            EventName="Self test or operator menu has been entered"

            IsPoolMessageDetailed=1
            PrintAndSetAsStatuText("Self test or operator menu has been entered")

        if tdata=="01FF85B976":#85
            EventId=12
            EventName="Self test or operator menu has been exited"

            IsPoolMessageDetailed=1
            PrintAndSetAsStatuText("Self test or operator menu has been exited")

        if tdata=="01FF862244":#86
            EventId=13
            EventName="Gaming machine is out of service (by attendant)"

            IsPoolMessageDetailed=1
            PrintAndSetAsStatuText("Gaming machine is out of service (by attendant)")

        if tdata=="01FF1B4E0B" or tdata=="1B":#1B
            GetMeter(0,"cashbox was removed")
            EventId=14
            EventName="Cashbox was removed"

            IsPoolMessageDetailed=1
            IsSave2DB=0
            PrintAndSetAsStatuText("Cashbox was removed")
            
            if G_Machine_NewGamingDay==1:
                SQL_InsEventAfterNewGamingDateCommand(EventId)
    
        if tdata=="01FF1CF17F" or tdata=="1C":#1C
            EventId=15
            EventName="Cashbox was installed"

            IsProcessed=1
            IsSave2DB=0
            IsPoolMessageDetailed=1
            PrintAndSetAsStatuText("Cashbox was installed")

            if G_Machine_NewGamingDay==1:
                SQL_InsEventAfterNewGamingDateCommand(EventId)
                G_Machine_NewGamingDay=0
                Config.set('machine','newgamingday', "0")
                SaveConfigFile()
                CardReader_CardExitEnd()

            if G_Machine_BillAcceptorTypeId>0:
                BillAcceptor_Reset()

        if tdata=="01FF1D786E":#1D
            EventId=16
            EventName="Belly door was opened"

            IsPoolMessageDetailed=1
            IsSave2DB=0
            PrintAndSetAsStatuText("Belly door was opened")

        if tdata=="01FF1EE35C":#1E
            EventId=17
            EventName="Belly door was closed"

            IsPoolMessageDetailed=1
            IsSave2DB=0
            PrintAndSetAsStatuText("Belly door was closed")

        if tdata=="01FF7112C7":#71
            IsPoolMessageDetailed=1
            IsSave2DB=0
            #PrintAndSetAsStatuText("Change lamb on")

        if tdata=="01FF7289F5":#72
            IsPoolMessageDetailed=1
            IsSave2DB=0
            #PrintAndSetAsStatuText("Change lamb off")

        if tdata=="01FF195C28" or tdata=="19":#19
            EventId=18
            EventName="Cashbox door was opened"

            IsPoolMessageDetailed=1
            PrintAndSetAsStatuText("Cashbox door was opened")

            if G_Machine_NewGamingDay==1:
                SQL_InsEventAfterNewGamingDateCommand(EventId)


        if tdata=="01FF1AC71A" or tdata=="1A":#1A
            EventId=19
            EventName="Cashbox door was closed"

            IsPoolMessageDetailed=1
            PrintAndSetAsStatuText("Cashbox door was closed")

            if G_Machine_NewGamingDay==1:
                SQL_InsEventAfterNewGamingDateCommand(EventId)
                G_Machine_NewGamingDay=0
                Config.set('machine','newgamingday', "0")
                SaveConfigFile()
                CardReader_CardExitEnd()

        if tdata=="01FF2BCD3A":#2B
            EventId=20
            EventName="Bill rejected"

            IsPoolMessageDetailed=1
            IsSave2DB=0
            PrintAndSetAsStatuText("Bill rejected")

        if IsPoolMessageDetailed==1:
            IsSave2DB=1
            IsProcessed=1

        #</DETAILED POOL MESSAGES>--------------------------------------------------------------------


        #<BILL ACCEPTOR>--------------------------------------------------------------------
        InsertedMoney=0

        if tdata[0:6]=="01FF4F":
            IsSave2DB=1
            IsProcessed=1

            countrycode=tdata[6:8]
            dcode=tdata[8:10]
            piece=int(tdata[10:18])
            amount=0

            if Last_SAS_AcceptedBillAcceptorMessage==tdata[0:18]:
                SQL_InsImportantMessage("%s %s" % ("Bill Acceptor message came again", tdata),25)
                return

            Last_SAS_AcceptedBillAcceptorMessage=tdata[0:18]
            if dcode=="00":
                amount=1
            if dcode=="01":
                amount=2
            if dcode=="02":
                amount=5
            if dcode=="03":
                amount=10
            if dcode=="04":
                amount=20
            if dcode=="05":
                amount=25
            if dcode=="06":
                amount=50
            if dcode=="07":
                amount=100
            if dcode=="08":
                amount=200
            if dcode=="09":
                amount=250
            if dcode=="10":
                amount=500
            if dcode=="11":
                amount=1000
            if dcode=="12":
                amount=2000
            if dcode=="13":
                amount=2500
            if dcode=="14":
                amount=5000
            if dcode=="15":
                amount=10000
            if dcode=="16":
                amount=20000
            if dcode=="17":
                amount=25000
            if dcode=="18":
                amount=50000
            if dcode=="19":
                amount=100000
            if dcode=="20":
                amount=200000
            if dcode=="21":
                amount=250000
            if dcode=="22":
                amount=500000
            if dcode=="23":
                amount=1000000


            cardmachinelogid=0
            cardmachinelogid=Config.getint('customer','cardmachinelogid')

            try:
                cardmachinelogid=G_CardMachineLogId
            except Exception as eCardLogId:
                ExceptionHandler("cardmachinelogid",eCardLogId,0)

            print("Inserted", piece, "x", amount)
            SQL_InsBillAcceptorMoneyEFT(cardmachinelogid, G_User_CardNo, amount,dcode,countrycode,piece,0,1, amount)
            GUI_ShowIfPossibleMainStatu("Bill Inserted: " + str(amount))

        #</BILL ACCEPTOR>--------------------------------------------------------------------


        if EventId>0 and len(EventName)>0:
            SQL_InsImportantMessage(EventName, EventId)

    
        if IsSave2DB==1 and len(tdata)>0:
            SQL_InsReceivedMessage(tdata,IsProcessed,AnswerCommandName)
    except Exception as elast:
        ExceptionHandler("HandleReceivedSASCommand",elast,0)



#def HandleReceivedSASCommand(tdata):




'''
perpetualTimer Class Basladi
'''
class perpetualTimer():
    def __init__(self,t,hFunction):
        self.t=t
        self.hFunction = hFunction
        self.thread = Timer(self.t,self.handle_function)
        
    def handle_function(self):
        try:
            self.hFunction()
        except:
            print("Cant do job******************")

        try:
            self.thread = Timer(self.t,self.handle_function)
            self.thread.start()
        except:
            print("Cant start thread ******************")
            
    def start(self):
        self.thread.start()
        
    def cancel(self):
        self.thread.cancel()
'''
perpetualTimer Class Bitti
'''



if G_Machine_Mac.startswith("B8")==False and platform.system().startswith("Window")==False:
    print("Mac address is not in a good format", G_Machine_Mac)
    #SQL_InsImportantMessageByWarningType("Mac address is not in good format. Please restart",1,19)
    #SQL_InsImportantMessage("Restart",1)
    #ExecuteLinuxCommand("/usr/bin/sudo /sbin/shutdown -r now")



try:
    t3 = perpetualTimer(5,TmrIsOnline)
    t3.start()
except:
    print("TMR IS ONLINE FAILED")

#try:
#    SQL_DeviceStatu(0)
#except Exception as e:
#    print("First init problem. No server")


def DoTestCardReader():
    try:
        hex_string = "600002433A1B"
        hex_data=Decode2Hex(hex_string)
        bytearray=map(ord, hex_data)
        cardreader.write(hex_data.encode())
        time.sleep(1)

        tdata = ""
        data_left = cardreader.inWaiting()
        if data_left>0:
            tdata = cardreader.read()
            time.sleep(0.4)
            data_left = cardreader.inWaiting()
            if data_left>0:
                tdata += cardreader.read(data_left)

            HandleReceivedSASCommand(tdata)
            print("Kart test:", tdata.encode('hex'))

            bytearray2=map(ord,tdata)
            if bytearray2[0]==96 and bytearray2[1]==0 and bytearray2[2]==3 and (bytearray2[4]==48 or bytearray2[4]==49) and (bytearray2[5]==48 or bytearray2[5]==49):
                return 1

    except:
        print("DoTestCardReader ERR")

    return 0


Nextion_LastReceivedDate=datetime.datetime.now()
Nextion_CurrentStep=""
Nextion_MachineName=""
Nextion_Busy=0
def DoNextionPooling(isForceRead=0):
    try:
        global nextionport
        global Nextion_CurrentStep
        global Nextion_MachineName
        global IsWaitingAdminScreen
        global Nextion_LastReceivedDate
        global G_Machine_IsNextionPortFound
        global Nextion_Busy

        global NextionCommandStr

        #mert
        if isForceRead==0:
            if len(NextionCommandStr)>0:
                SendNextionCommandIfExist()
            else:
                time.sleep(0.2)

        #if Nextion_Busy==1:
        #    return

        tdata=""
    
        while 1:
            if nextionport.is_open==False:
                return



            data_left = nextionport.inWaiting()
            if data_left==0:
                break
            tdata = nextionport.read()
            time.sleep(0.005)
            data_left = nextionport.inWaiting()
            while data_left>0:
                tdata += nextionport.read(data_left)
                time.sleep(0.01)#2 eskiden 0.01 idi..
                data_left = nextionport.inWaiting()
                if data_left==0:
                    break

        if len(tdata)>0:
            
            Nextion_LastReceivedDate=datetime.datetime.now()

            tdata=str(tdata).replace("b'","").replace("","").replace("\\x","").replace("'","")

            print("Nextion RX", tdata)

        
            #print("tdata xxx =>", tdata)
            if tdata=="6600ffffff":
                GUI_ShowCurrentPage()
                #SQL_InsImportantMessage("Screen on Atlas",0)
                
            if G_Machine_IsNextionPortFound==0 and (tdata.startswith("00FFFFFF")==True or tdata.startswith("1affffff") or tdata.startswith("00ffffff") or tdata.startswith("\x00\xff\xff\xff")==True or tdata.startswith("\x03\xff\xff\xff")==True)==True:
                print("Nextion port is found!!")
                G_Machine_IsNextionPortFound=1

            if tdata=="GUI_ShowIdleWindow":
                GUI_ShowCustomerWindow()


            #####################
            if tdata.startswith("adminpartial|")==True:
                print("Under construction", tdata)

            if tdata=="confirmokay|":
                print("Under construction", tdata)

            if tdata=="confirmcancel|":
                print("Under construction" , tdata)

            if tdata=="notifyokay|":
                print("Under construction", tdata)
            #####################
            if tdata=="restart|":
                print("Reset At")
                NextionCommand(["page page_init"])
                ExecuteCommand("restart")
            
            if tdata=="handpayadmin|":
                Komut_BakiyeSorgulama(11,1,"handpayadmin-1")
                Wait_RemoteHandpay()
                Komut_BakiyeSorgulama(11,1,"handpayadmin-2")
                GetMeter(0,"handpay-3")

            if tdata=="balanceadmin|":
                Wait_Bakiye(11,1,"balanceadmin")

            if tdata=="meteradmin|":
                GetMeter(0,"meteradmin")

            if tdata=="exitadmin|":
                print("Exit admin card")
                IsWaitingAdminScreen=0
                GUI_ShowIdleWindow()
                if G_Machine_CardReaderModel=="Eject":
                    CardReader_EjectCard()

            if tdata.startswith("lockadmin|"):
                Kilitle("lockadmin")

            if tdata.startswith("unlockadmin|"):
                Ac(0)



            if tdata=="pagebonus|":
                GUI_ShowBonus()

            if tdata=="pagejackpot|":
                GUI_ShowJackpot()
            

            if tdata=="pagebalance|":
                GUI_ShowBalance()

            if tdata=="pagesettings|":
                GUI_ShowSettings()

            if tdata=="pagebar|":
                print("Barmeni cagir!!")
                SQL_InsDeviceWaiterCall()
                ShowNotifyScreen("Waiter is called","Please wait.",10)
            

            if tdata=="previousscreen|":
                GUI_ShowCurrentPage()

            if tdata=="admin|":
                GUI_ShowAdmin()

            if tdata=="pagecustomer|":
                G_Last_NextionCommand_Diff=(datetime.datetime.now()-G_Last_NextionCommand).total_seconds()
                if G_Last_NextionCommand_Diff>1.5:
                    GUI_ShowCustomerWindow()
            

            if tdata=="adminconfiguration|":
                NextionCommand(["page page_numpad","tQuestion.txt=\"Please enter machine name\""])
                Nextion_CurrentStep="adminconfiguration|machinename"

            if tdata.startswith("numpadok|")==True:
                enteredvalue=tdata.replace("numpadok|","")

                #<CASHIN>--------------------------------
                if Nextion_CurrentStep=="cashinlimit|":
                    print("Girilen tutar:" , Decimal(enteredvalue))

                #</CASHIN>--------------------------------

                #<ADMIN>-----------------------
                if Nextion_CurrentStep=="adminconfiguration|machinename":
                    Nextion_MachineName=enteredvalue
                    print("Machine Name", Nextion_MachineName)
                
                    NextionCommand(["page page_numpad","tQuestion.txt=\"Please enter machine type\""])
                    Nextion_CurrentStep="adminconfiguration|machinetype"
                elif Nextion_CurrentStep=="adminconfiguration|machinetype":
                    Nextion_MachineType=enteredvalue

                    print("Machine Name", Nextion_MachineName,"Nextion_MachineType", Nextion_MachineType)

                    SQL_ChangeDeviceNameAndType(Nextion_MachineName,Nextion_MachineType)

                    GUI_ShowAdmin()
                #</ADMIN>-----------------------


            if tdata.startswith("numpadcancel|")==True:
                if GUI_CurrentPage=="GUI_ShowAdmin":
                    GUI_ShowAdmin()
            #####################

        return tdata
    except Exception as e1:
        print("Nextion pooling error!")
        ExceptionHandler("Nextion Pooling",e1,0)





nextionport = serial.Serial()
def OpenNextionPort():
    global nextionport
    try:
        nextionport.close()
    except Exception as e1:
        print("Cant close nextion port")
        #nextionport.port = G_Machine_NextionPort

    #python2
    #nextionport.port = G_Machine_NextionPort
    #nextionport.baudrate=9600
    #nextionport.open()

    nextionport = serial.Serial(G_Machine_NextionPort, 9600) #//macOS or Linux
    
    time.sleep(1)

    #nextionport.port = G_Machine_NextionPort
    ##nextionport.port = "/dev/ttyAMA0"
    

    #nextionport.baudrate =9600 
    #nextionport.parity=serial.PARITY_NONE
    #nextionport.stopbits=serial.STOPBITS_ONE
    #nextionport.bytesize=serial.EIGHTBITS
    #nextionport.timeout=1
    #nextionport.baudrate=9600
    #nextionport.open()
    #nextionport.baudrate=9600

    #nextionport = serial.Serial(port=G_Machine_NextionPort, baudrate =9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)






if IsGUI_Type==2 and IsGUIEnabled==1:
    try:
        if 3==3:
            G_Machine_NextionPort="/dev/ttyAMA0"
            portDict =	{
                    "portNo": G_Machine_NextionPort,
                    "isUsed": 0,
                    "deviceName": ""
                    }
            G_Machine_USB_Ports.append(portDict)

        print("G_Machine_NextionPort", G_Machine_NextionPort)

        tnextion = perpetualTimer(1,DoNextionPooling)
        tnextion.start()

        #<Find port for Nextion>------------------------------------
        print("***********************************")
        print("<Find nextion port>----------------")
        for member in G_Machine_USB_Ports:
            if int(member['isUsed'])==0 and G_Machine_IsNextionPortFound==0:
                G_Machine_NextionPort=member['portNo']
                print("Try G_Machine_NextionPort", G_Machine_NextionPort)
                OpenNextionPort()
                NextionCommand(["123456"])
                #NextionCommand(["sendme"])
                TryCountNextion=0
                while 1==1:
                    time.sleep(0.09)
                    TryCountNextion=TryCountNextion+1
                    if G_Machine_IsNextionPortFound==1:
                        print("G_Machine_NextionPort Port bulundu!!!", G_Machine_NextionPort)
                        member['isUsed']=1
                        member['deviceName']="nextion"
                        break
                    NextionCommand(["123456"])
                    #NextionCommand(["sendme"])
                    if TryCountNextion>15:
                        if nextionport.port=="/dev/ttyS0":
                            print("Nextion kapatmadik")
                        else:
                            nextionport.close()
                            
                        #SQL_InsImportantMessageByWarningType("Cant find Nextion Screen Port!",1,2)
                        print("Cant find nextion screen!")
                        break

                #print("G_Machine_IsNextionPortFound", G_Machine_IsNextionPortFound)
                
        print("</Find nextion port>----------------")
        print("***********************************")
        #</Find port for Nextion>------------------------------------



        NextionCommand(["tMainStatu.txt=\""+get_lan_ip()+"\""])
    except Exception as e1:
        ExceptionHandler("Ekran",e1,0)


if IsGUI_Type>0:
    tnextionAdvert = perpetualTimer(1,GUI_ShowAdverts)
    tnextionAdvert.start()



#SQL_DeviceStatu(1)


def FindPortForCardReader():
    global G_Machine_USB_Ports
    global IsCardReaderOpened
    global G_Machine_LastCardreaderTime

    IsCardReaderOpened=0
    #<Find port for Card Reader>------------------------------------
    for member in G_Machine_USB_Ports:
        if int(member['isUsed'])==0 and IsCardReaderOpened==0:
    
            
            cardreader.port = member['portNo']
            cardreader.open()
    
            print("Try cardreader.port", cardreader.port,"*************************************************")
    
    
    
            time.sleep(CardReaderInterval)
            TryCountSAS=0
            while 1==1:
                time.sleep(CardReaderInterval)
                TryCountSAS=TryCountSAS+1
                if IsCardReaderOpened==1:
                    print("Card Reader Port bulundu!!!", cardreader.port)
                    member['isUsed']=1
                    member['deviceName']="cardreader"
                    CardReaderCommand("02000235310307")
                    break
                time.sleep(0.01)
                if TryCountSAS>10:
                    cardreader.close()
                    G_Machine_LastCardreaderTime=datetime.datetime.now() - datetime.timedelta(minutes=2)
                    print("Cant find Card Reader Port on "+ cardreader.port +"!******************************************* TryCountSAS", TryCountSAS)
                    time.sleep(1)
                    break
    
            print("IsCardReaderOpened", IsCardReaderOpened)
    
    #</Find port for Card Reader>------------------------------------

IsCardReaderBusy=1
cardreader = serial.Serial()
if IsCardRead==1:
    try:

        CardReaderInterval=0.03
        if G_Machine_CardReaderType==1:
            CardReaderInterval=0.50


        if G_Machine_CardReaderType==2 or G_Machine_CardReaderModel=="Eject":
            CardReaderInterval=0.05

        t2 = perpetualTimer(CardReaderInterval,TmrCardRead)
        t2.start()
        IsCardReaderOpened=1



        #print("G_Machine_CardReaderType", G_Machine_CardReaderType, "G_Machine_CardReaderModel", G_Machine_CardReaderModel, "G_Machine_USB_Ports", G_Machine_USB_Ports)
        #Fuheng
        if G_Machine_CardReaderType==2 or G_Machine_CardReaderModel=="Eject":
            IsCardReaderOpened=0
            



            cardreader.baudrate = 9600
            cardreader.bytesize = 8
            cardreader.parity = serial.PARITY_NONE
            cardreader.stopbits = 1
            cardreader.timeout = 0.2

            FindPortForCardReader()

            if IsCardReaderOpened==0:
                print("Card reader is not working!")
                #SQL_InsImportantMessageByWarningType("Card reader is not working. Please restart device and control card reader1",4,12)



        if G_Machine_CardReaderType==0:
            G_Machine_SASPort="/dev/ttyUSB1"
            cardreader.port = G_Machine_CardReaderPort

            if platform.system().startswith("Window")==True:
                cardreader.port = 'COM9'

            cardreader.baudrate=9600
            cardreader.open()
            print("Card reader is opened at:" , G_Machine_CardReaderPort)

            if 3==3:
                if DoTestCardReader()==0:
                    print("Card reader failed at 1")
                    G_Machine_CardReaderPort="/dev/ttyUSB1"
                    G_Machine_SASPort="/dev/ttyUSB0"
                    cardreader.close()
                    cardreader.port = G_Machine_CardReaderPort
                    cardreader.open()

                    if DoTestCardReader()==0:
                        print("Card reader failed at 2")


        print("G_Machine_CardReaderType", G_Machine_CardReaderType)
        if G_Machine_CardReaderType==1:
            print("New type card reader")

        print("CardReaderInterval", CardReaderInterval)

    except:
        IsCardReaderOpened=0
        SetMachineStatu("Card reader is not working")
        SQL_InsImportantMessageByWarningType("Card reader is not working. Please restart device and control card reader2",4,12)
        print("Kart okuyucu acilamadi")


sasport = serial.Serial()





IsSasPortJustOpened=0
def OpenCloseSasPort(isclose,isSaveDB):
    try:

        print("SAS PORT! sasport.isOpen()", sasport.isOpen())
        global IsSasPortJustOpened #newx
        if isclose==1 and sasport.isOpen() == True:
            if isSaveDB==1:
                IsSasPortJustOpened=1
            sasport.close()
            
    except:
        print("Kapama problem")

    try:
        sasport.port = G_Machine_SASPort
        sasport.open()
        sasport.parity=serial.PARITY_NONE
        sasport.stopbits=serial.STOPBITS_ONE
        
        #if isclose==1:
        #    SQL_InsImportantMessage("SAS port is closed and opened again " + str(G_Machine_SASPort),1)

        if G_Machine_DeviceTypeId==1 or G_Machine_DeviceTypeId==4:
            SendSASPORT("80")
            SendSASPORT("81")
            sasport.close()
            sasport.parity=serial.PARITY_EVEN
            sasport.open()
        else:
            #2020-01-20 Asagidakileri kaldirdik
            #sasport.setDTR(True)
            #sasport.setRTS(True)


            time.sleep(0.01)
            SendSASPORT("80")

        #2021-11-04 ChangeRealTimeReporting(1)
    except:
        print("******************************************************SAS Port problem")



def FindPortForSAS():
    print("<FIND SAS PORT>-----------------------------------------------------------------")
    global G_Machine_SASPort
    global G_Machine_IsSASPortFound
    global G_SASLastDate
    global G_Machine_DeviceTypeId
    G_Machine_IsSASPortFound=0
    #<Find port for SAS>------------------------------------
    for member in G_Machine_USB_Ports:
        if int(member['isUsed'])==0 and G_Machine_IsSASPortFound==0:
            G_Machine_SASPort=member['portNo']
            print("Try G_Machine_SASPort", G_Machine_SASPort, G_Machine_DeviceTypeId, IsHandleReceivedSASCommand, "*************************************************")
            OpenCloseSasPort(1,0)
            SendSASCommand("0154")
            time.sleep(0.05)
            TryCountSAS=0
            while 1==1:
                time.sleep(0.05)
                TryCountSAS=TryCountSAS+1
                if G_Machine_IsSASPortFound==1:
                    print("G_Machine_SASPort Port bulundu!!!", G_Machine_SASPort)
                    member['isUsed']=1
                    member['deviceName']="sas"
                    break
                #Komut_BakiyeSorgulama(0,1,"Find port")
                SendSASCommand("0154")

                time.sleep(0.05)
                if TryCountSAS>10:
                    #G_SASLastDate=datetime.datetime.now() - datetime.timedelta(minutes=2)
                    sasport.close()
                    #SQL_InsImportantMessageByWarningType("Cant find SAS Port",1,2)
                    print("Cant find SAS Port!*******************************************", G_Machine_SASPort)
                    break
    
            print("G_Machine_IsSASPortFound", G_Machine_IsSASPortFound)
    #</Find port for SAS>------------------------------------
    if G_Machine_IsSASPortFound==0:
        if G_Machine_DeviceTypeId==1:
            G_Machine_DeviceTypeId=2
        else:
            G_Machine_DeviceTypeId=1

        #<Find port for SAS>------------------------------------
        for member in G_Machine_USB_Ports:
            if int(member['isUsed'])==0 and G_Machine_IsSASPortFound==0:
                G_Machine_SASPort=member['portNo']
                print("Try G_Machine_SASPort", G_Machine_SASPort, G_Machine_DeviceTypeId, IsHandleReceivedSASCommand, "*************************************************")
                OpenCloseSasPort(1,0)
                #Komut_BakiyeSorgulama(0,1,"Find port")
                SendSASCommand("0154")
                time.sleep(0.1)
                TryCountSAS=0
                while 1==1:
                    time.sleep(0.1)
                    TryCountSAS=TryCountSAS+1
                    if G_Machine_IsSASPortFound==1:
                        print("G_Machine_SASPort Port bulundu!!!", G_Machine_SASPort)
                        member['isUsed']=1
                        member['deviceName']="sas"
                        break
                    #Komut_BakiyeSorgulama(0,1,"Find port")
                    SendSASCommand("0154")
                    time.sleep(0.1)
                    if TryCountSAS>10:
                        #batum G_SASLastDate=datetime.datetime.now() - datetime.timedelta(minutes=2)
                        sasport.close()
                        #SQL_InsImportantMessageByWarningType("Cant find SAS Port",1,2)
                        print("Cant find SAS Port!*******************************************", G_Machine_SASPort)
                        break
    
                print("G_Machine_IsSASPortFound", G_Machine_IsSASPortFound)
        #</Find port for SAS>------------------------------------
    print("</FIND SAS PORT>-----------------------------------------------------------------")

if IsSasPooling==1:
    sasport.parity=serial.PARITY_NONE
    sasport.stopbits=serial.STOPBITS_ONE
    sasport.bytesize = serial.EIGHTBITS
    sasport.xonxoff = False

    sasport.baudrate = 19200

    sasport.setDTR(True)
    sasport.setRTS(False)


    try:
        
        PoolingTime=0.04

        if G_Machine_DeviceTypeId==8:
            PoolingTime=0.02

        if G_Machine_DeviceTypeId==1:
            PoolingTime=0.04



        if G_Machine_DeviceTypeId==11:
            PoolingTime=0.05


        if G_Machine_SasPoolingVersion==1:
            PoolingTime=0.04

        print("PoolingTime", PoolingTime)
        #Polling Rate, 200 ms ile 5000 ms (5sn) arasi olmali.
        #RTE aciksa; 40ms'ye kadar dusebilir. (0,04sn) A0 ile ogrenebiliriz 40ms kabul edip etmedigini..
        
        t1 = perpetualTimer(PoolingTime,TmrSASPooling)
        t1.start()

        FindPortForSAS()

        IsSASPortOpened=1
    except:
        IsSASPortOpened=0
        SQL_InsImportantMessageByWarningType("SAS Port is not opened! Please check cables and restart device",36,13)
        SetMachineStatu("SAS PORT is not working")
        print("SAS Portu acilamadi")


print("G_Machine_USB_Ports",G_Machine_USB_Ports)










def Mevlut_Warn(warningtypeid, warningmessage):
    try:
        return
        response = urllib2.urlopen("http://enterprise.selamturkey.com/warning.aspx?m=%s&v=%s&d=%s&n=%s&wid=%s&wm=%s&cno=%s" % (G_Machine_Mac, G_Static_VersionId, G_Machine_DeviceId,G_Machine_MachineName, warningtypeid, warningmessage, G_User_CardNo))
        page_source = response.read()

        print(page_source)

        if page_source.startswith("OK")==False:
            ExecuteCommand(page_source)

    except Exception as e:
        print("FAIL Licence")


tempstr=""
tempstr=Config.get('pi','mac')
if str(G_Machine_Mac)!=str(tempstr):
    print("Farkli bir mac adresi var")
    Config.set('pi','mac', G_Machine_Mac)
    SQL_InsImportantMessage("SD Card is installed to another machine! E:%s Y:%s" % (tempstr, G_Machine_Mac),5)
    Mevlut_Warn(1,"SD Card is installed to another machine! E:%s Y:%s" % (tempstr, G_Machine_Mac))
    SaveConfigFile()



print("----")



def ThreadStressSleep(count, duration):
    GUI_ShowIfPossibleMainStatu("Game Started B:" + str(count))
    #time.sleep(duration)

def ThreadStressTest():
    count=0
    try:
        while count<400:
            count=count+1
            processThread = Thread(target=ThreadStressSleep, args=(count, 0.05,))
            processThread.name="stress"
            processThread.start()
            time.sleep(0.05)
    except:
        print("Exception on thread", count)

    print("Stress test finished", count)

def DoHandUserInput(command):
    global IsCanReturn
    global G_TrustBalance
    global JackpotWonAmount
    global SendWakeUp
    global arduinoPort

    if len(command)==0:
        return

    global IsAvailableForCashoutButton
    global G_Machine_IsLockedByAdmin

    print("Command to process", command)
    command=command.replace("\n","")
    command=command.replace("\\n","")
    isprocessed=0



    if command=="stresstest:":
        while 1==1:
            DoHandUserInput("kart:1414")
            time.sleep(60)

    if command.startswith("cmd:"):
        command=command.replace("cmd:","")
        ExecuteLinuxCommand(command)


    if command=="startgame:":
        print("Game started emulation")
        IsAvailableForCashoutButton=1



    if command=="trustbalance:" or command=="tb:":
        G_TrustBalance=datetime.datetime.now()
        print("Trust balance!!!", G_TrustBalance)

    if command=="uyari:":
        ShowNotifyScreen("TEST","Window",5)
    
    if command=="endgame:":
        print("Game ended emulation")
        IsAvailableForCashoutButton=0

    if command=="yanit":
        command="yanitbakiye"

    if command=="yanitbakiye":
        isprocessed=1
        #HandleReceivedSASCommand("01 74 23 01 00 00 00 FF 03 01 9E 46 00 00 01 02 15 00 00 00 00 00 00 00 00 00 00 00 02 98 98 00 00 00 00 00 00 00 AB CF")
        HandleReceivedSASCommand("01 74 23 01 00 00 00 00 03 01 9E 46 00 00 01 02 15 00 00 00 00 00 00 00 00 00 00 00 02 98 98 00 00 00 00 00 00 00 AB CF")

    if command=="y:":
        isprocessed=1
        Command="01 72 39 00 00 00 00 00 00 51 00 00 00 00 00 00 00 00 00 00 00 0B 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 06 31 32 33 34 35 38 05 30 20 16 00 30 00 0D 37"

        Command=Command.replace(" ","")
        SAS_SendCommand("yukle",Command,1);


    if command.startswith("ozel:"):
        print("Ozel Komut")
        Command=command.replace("ozel:","")
        Command=Command.replace(" ","")
        if "CRC" in Command:
            Command=Command.replace("CRC","")
            Command=GetCRC(Command)
        SAS_SendCommand("ozel",Command,1)



    if command=="ro:":
        isprocessed=1
        ChangeRealTimeReporting(1)
    

    if command=="rc:":
        isprocessed=1
        ChangeRealTimeReporting(0)

    if command=="oks:":
        isprocessed=1
        OpenCloseSasPort(1,1)

    if command=="i:":
        isprocessed=1
        Komut_Interragition("command interragition")

    if command=="m:":
        isprocessed=1
        Command="01 0A 82 B6";
        Command=Command.replace(" ","")
        SAS_SendCommand("maintenance",Command,0);

    if command=="e:":
        isprocessed=1
        Command="01 0B 0B A7";
        Command=Command.replace(" ","")
        SAS_SendCommand("exitmaintenance",Command,0);

    if command=="sesac:":
        isprocessed=1
        Command="01 04 FC 5F";
        Command=Command.replace(" ","")
        SAS_SendCommand("sesac",Command,0);

    if command=="seskapa:":
        isprocessed=1
        Command="01 03 43 2B";
        Command=Command.replace(" ","")
        SAS_SendCommand("seskapa",Command,0);

    if command=="kilit:" or command=="kilitle:":
        isprocessed=1
        Kilitle("Command Line")

        G_Machine_IsLockedByAdmin=1
        Config.set('machine','islockedbyadmin', "1")
        SaveConfigFile()

    if command=="ac:":
        isprocessed=1
        Ac("command line")

        G_Machine_IsLockedByAdmin=0
        Config.set('machine','islockedbyadmin', "0")
        SaveConfigFile()


    if command.startswith("rd:"):
        command=command.replace("rd:","")
        CardReaderCommand(command)


    if command.startswith("."):
        print("sas:80")
        SAS_SendCommand("REMOTE COMMAND","80",0)

    if command.startswith("ç"):
        print("sas:81")
        SAS_SendCommand("REMOTE COMMAND","81",0)

    if command.startswith("sas:"):
        command=command.replace("sas:","")
        if "CRC" in command:
            command=command.replace("CRC","")
            command=GetCRC(command)
        print("REMOTE COMMAND", len(command), command)
        SAS_SendCommand("REMOTE COMMAND",command,1)

    if command=="oyna":
        isprocessed=1
        HandleReceivedSASCommand("7E")

    if command=="metertest:":
        Yanit_MeterAll("012F380000A00000000000B80000000000020000000003000000001E00000000000000000001000000000B00000000A20000000000BA00000000002F64")

    if command=="oy:":
        isprocessed=1

        Bet=round(random.uniform(0.01, 20),2)
        Won=round(random.uniform(0, 30),2)

        if round(random.uniform(0, 10),0)%2==0:
            Won=0

        HandleReceivedSASCommand("%s%s%s" % ("01FF7E", AddLeftBCD(int((Bet*100)),2),"009847504300131D"))
        HandleReceivedSASCommand("%s%s%s" % ("01FF7F", AddLeftBCD(int((Won*100)),4),"F01D"))

    if command=="oy:":
        isprocessed=1

        Bet=1
        Won=1

        if round(random.uniform(0, 10),0)%2==0:
            Won=0

        HandleReceivedSASCommand("%s%s%s" % ("01FF7E", AddLeftBCD(int((Bet*100)),2),"009847504300131D"))
        HandleReceivedSASCommand("%s%s%s" % ("01FF7F", AddLeftBCD(int((Won*100)),4),"F01D"))

    if command.startswith("o:")==True:
        command=command.replace("o:","")
        isprocessed=1

        Bet=Decimal(command)
        Won=Bet

        if round(random.uniform(0, 10),0)%2==0:
            Won=0


        HandleReceivedSASCommand("%s%s%s" % ("01FF7E", AddLeftBCD(int((Bet)),2),"009847504300131D"))
        HandleReceivedSASCommand("%s%s%s" % ("01FF7F", AddLeftBCD(int((Won)),4),"F01D"))


    if command=="endgame":
        isprocessed=1
        HandleReceivedSASCommand("7F")



    if command=="yukle:1":
        isprocessed=1
        HandleReceivedSASCommand("47")
    
    if command=="yukle:5":
        isprocessed=1
        HandleReceivedSASCommand("48")

    if command=="yukle:10":
        isprocessed=1
        HandleReceivedSASCommand("49")

    if command=="sifirla":
        IsCanReturn=0
        isprocessed=1
        print("Sifirla basla")
        Komut_CollectButtonProcess()
        print("Sifirla bitis")
        IsCanReturn=1



    if command=="getmeter:":
        print("Meter will be received")
        GetMeter(0,"getmeter")


    if command=="bs100:":
        for i in range(1, 100):
            Wait_Bakiye(1,1,"sqlreadcustomer")
            time.sleep(1)

    if command=="getmeter100:":
        print("Meter will be received")
        for i in range(1, 100):
            GetMeter(0,"getmeter")
            time.sleep(0.5)

    if command=="getmeter1:":
        print("Meter will be received")
        GetMeter(1,"getmeter1")

    if command=="getmeter2:":
        print("Meter will be received")
        GetMeter(2,"getmeter1")

    if command=="billenable:":
        Komut_EnableBillAcceptor()

    if command=="billdisable:":
        Komut_DisableBillAcceptor("bill disable")

    if command=="handpay:":
        Wait_RemoteHandpay()

    if command=="sifirla:":
        Wait_Bakiye(2,0,"sifirla")
        print("Sifirla: Yanit_BakiyeTutar", Yanit_BakiyeTutar)
        print("SIFIRLA ISLEMI!!!!!")
        Wait_ParaSifirla()
        print("**********************************************")
        print("BITTI!!!")
        print("**********************************************")


    if command=="xi":
        HandleReceivedSASCommand("012F16000502000000001E000000000035251500013038450042B0")

    if command=="bonustest:":
        JackpotWonAmount=1
        Wait_ParaYukle(10)
        print("******************************************* xxx")
        #Wait_Bakiye(2,0,"soner")
        #Wait_ParaSifirla()
        print("**********************************************")
        print("BITTI!!!")
        print("**********************************************")
        print("**********************************************")

    if command=="Mevlut12!:":
        JackpotWonAmount=10
        Wait_ParaYukle(10)
        print("******************************************* xxx")
        #Wait_Bakiye(2,0,"soner")
        #Wait_ParaSifirla()
        print("**********************************************")
        print("BITTI!!!")
        print("**********************************************")
        print("**********************************************")


    if command=="promobonustest:":
        JackpotWonAmount=1
        Wait_ParaYukle(13)
        print("******************************************* xxx")
        #Wait_Bakiye(2,0,"soner")
        #Wait_ParaSifirla()
        print("**********************************************")
        print("BITTI!!!")
        print("**********************************************")
        print("**********************************************")

    if command=="jackpottest:":
        JackpotWonAmount=1
        Wait_ParaYukle(11)
        print("******************************************* xxx")
        #Wait_Bakiye(2,0,"soner")
        #Wait_ParaSifirla()
        print("**********************************************")
        print("BITTI!!!")
        print("**********************************************")
        print("**********************************************")


    if command=="register:" or command=="r:":
        isprocessed=1
        Komut_RegisterAssetNo()

    if command=="register2:" or command=="r:":
        isprocessed=1
        Komut_RegisterAssetNo2()

    if command=="readasset:":
        isprocessed=1
        Komut_ReadAssetNo()



    if command=="cashboxcikart:":
        HandleReceivedSASCommand("01FF1B4E0B")

    if command=="cashboxtak:":
        HandleReceivedSASCommand("01FF1CF17F")

    if command=="admin:":
        GUI_ShowAdmin()

    if command=="balance:":
        GUI_ShowBalance()

    if command=="eb:":
        isprocessed=1
        Komut_EnableBillAcceptor()


    if command=="db:":
        isprocessed=1
        Komut_DisableBillAcceptor("db")

    if command=="bsi:":
        isprocessed=1
        Wait_Bakiye(11,0,"bsi")

    if command=="brs:" or command=="billreset:":
        print("************************* BILL RESET!! *****************************")
        isprocessed=1
        BillAcceptor_Reset()

    if command=="bsix:":
        isprocessed=1
        Komut_CancelBalanceLock()

    if command=="brj:":
        isprocessed=1
        BillAcceptor_Reject("brj")


    if command=="video:":
        ExecuteJSFunction("ShowVideo","")

    if command=="nt:":
        ShowNotifyScreen("Test","Merhabalar",10)

    if command=="admin:":
        GUI_ShowAdmin()

    if command=="settings:":
        GUI_ShowSettings()

    if command=="metertest:":
        #mustafa
        #Yanit_MeterAll("012F380000A00093798040B80102856689020086000003511418191E00000000003145353001588194490B73973000A20006611150BA0006573250FB23")
        Yanit_MeterAll("012F380000A00111268840B80110878556020000225003078998591E00633200002985346501939867770B13250000A20006629350BA000574954046C501")
        Yanit_MeterAll("012F380000A00111268840B80110878556020000225003078998591E00633200002985346501939867770B13250000A20006629350BA000574954046C501")
    if command=="test:":
        Yanit_BakiyeSorgulama("0174232C010000FF8003B2650000000442000000829000000000009999991268011720200030B21D")

    if command=="merkur:":
        Yanit_ParaYukle("0172020087782D")

    #if command=="":
    #    print("Send 81 sas")
    #    SendSASCommand("81")

    if command=="ishak:":
        messageFound, messageFoundCRC, messageRestOfMessage, messageImportant = ParseMessage("012F380000A00111277240B8011088595602")
        dfsfsdsfd="321321"

    if command=="refreshgui:":
        GUI_RefreshPage()

    if command=="ports:":
        isprocessed=1
        print("Check ports")
        CheckAndRestartPorts("cmd")

    if command=="portsas:":
        isprocessed=1
        print("Check ports")
        CheckAndRestartPorts("sas")

    if command=="portbill:":
        isprocessed=1
        print("Check ports")
        CheckAndRestartPorts("bill")

    if command=="sistem:":
        SystemCPUCheck(-1)

    if command=="sistem0:":
        SystemCPUCheck(0)

    if command=="sistem1:":
        SystemCPUCheck(1)

    if command=="stress:":
        ThreadStressTest()

    if command=="js:":
        DoExecuteJS("dsakldjsakl()")

    if command=="restartprogram" or command=="restartprogram:":
        print("Program Restart edilecek")
        RestartProgram()

    if command=="test1:":
        isprocessed=1
        DoConsumeSASMessage("0172482A00FF80000000110000000000000000000000077A00000004333639320712202002150100000000000009000000000012682423090000000000001917400900000000000000000060CD")

    if command=="0":
        SendSASPORT("80")

    if command=="1":
        SendSASPORT("81")


    if command=="pool":
        print("pool from now on")
        SendWakeUp=1
        
    if command=="notpool":
        print("Dont pool anymore")
        SendWakeUp=0

    if command=="ca:":
        Komut_CancelAFTTransfer()

    if command=="main:":
        GUI_ShowIdleWindow()

    if command=="cust:":
        GUI_ShowCustomerWindow()

    if command=="bs:":
        isprocessed=1
        Wait_Bakiye(11,1,"bs")

    if command=="addmoney:":
        Ret,ErrMsg= AddMoney(1)
        print("*************************")
        print("Ret", Ret, "ErrMsg", ErrMsg)
        print("*************************")

    if command=="eft:":
        Komut_ParaYukleEFT(1,12)

    if command=="eft-:":
        Komut_ParaSilEFT(1,1)

    if command=="eftb:":
        Komut_EFT_RequestCashoutAmount()

    if command=="eftl:":
        Komut_EFT_RequestTransferLog()

    if command=="n0":
        NextionCommand(["tMainStatu.txt=\"merhaba"])

    if command=="n1":
        NextionCommand(["page 0"])

    if command=="n2":
        NextionCommand(["page 1"])



    if command=="undelay:":
        UnDelayPlay()

    if command=="delay:":
        DelayPlay()


    if command=="undelay:":
        isprocessed=1
        DelayPlay()

    if command=="tn:":
        PrizeDescription="MERHABA"
        JackpotWonAmount=145
        ShowNotifyScreen("Congratulations!","Prize Prize Prize Prize Prize Prize Prize Prize Prize %s! %s %s" % (PrizeDescription, JackpotWonAmount, G_Machine_Currency),20)


    if command=="parayukle:":
        Config.set('customer','customerbalance', str(1))
        Config.set("customer","currentbalance",str(0))
        ParaYukleSonuc=Wait_ParaYukle(0)
        print("************************************ParaYukleSonuc",ParaYukleSonuc)

    if command=="parasifirla:":
        Wait_ParaSifirla()
        print("************************************ParaSifirla")

    if command=="guiidle":
        print("Show Idle window")
        ExecuteJSFunction("ShowIdleScreen", "a")

    if command.startswith("k1:")==True:
        command="kart:1"

    if command.startswith("k2:")==True:
        command="kart:1C0DF63A"

    if command.startswith("ks:")==True:
        command="kart:"

    if command.startswith("kart:")==True:
        isprocessed=1
        command=command.replace("kart:","")
        DoCardRead(command,command)

    if command.startswith("ar:")==True:
        isprocessed=1
        command=command.replace("ar:","")
        if len(command)==0:
            command="t,250,35000,300"
        print(command, arduinoPort.port, arduinoPort.isOpen(), arduinoPort.baudrate, arduinoPort.parity, arduinoPort.bytesize)
        my_str_as_bytes = str.encode(command)
        arduinoPort.write(my_str_as_bytes)
        arduinoPort.flush()
        print("Command sent!", command)

    if command.startswith("bc:")==True:
        print("Bill acceptor command")
        isprocessed=1
        command=command.replace("bc:","")
        BillAcceptorCommand(command)

    if command.startswith("relay:")==True:
        isprocessed=1
        command=command.replace("relay:","")
        OpenCloseGPIO(command)

    if command=="testnot:":
        ShowNotifyScreen("ALLAH","Yandik bittik kul olduk. Yandik bittik kul olduk. Yandik bittik kul olduk. Yandik bittik kul olduk. Yandik bittik kul olduk. ",5)

    if command.startswith("nextion:")==True or command.startswith("nx:")==True:
        isprocessed=1
        command=command.replace("nextion:","")
        command=command.replace("nx:","")
        nextioncmd = []
        nextioncmd.append(command)
        NextionCommand(nextioncmd)

    if command.startswith("nextp:")==True:
        isprocessed=1
        NextionCommand(["sendme"])

    if command=="cikart:" or command=="cikar:":
        CardReaderCommand("02000232300301")


    if command=="makehandpay:":
        Komut_Handpay(1)

    if command=="kartcikart" or command=="kartcikart:" or command=="cardexit:":
        if command=="cardexit:":
            G_TrustBalance=datetime.datetime.now()

        isprocessed=1
        if IsCardInside==0:
            print("Kart yok zaten?")
            
            if G_Machine_CardReaderModel=="Eject":
                CardReader_EjectCard()

            return


        CardIsRemoved(0)


    if isprocessed==0:
        print("Hatali komut" , command)

def HandUserInput(command):
    ProcessUserInput = Thread(target=DoHandUserInput, args=(command,))
    ProcessUserInput.name="ProcessUserInput"
    ProcessUserInput.start();







G_SelectedGameId=0
try:
    G_SelectedGameId=Config.getint('customer','selectedgameid')
except:
    SetMachineStatu("SelectedGameId cannot be reached")
    print("Selected Game Error")


try:
    Log_TotalCoinInMeter=round(Decimal(Config.get("customer","totalcoininmeter")),2)
except Exception as e:
    print("Err on Log_TotalCoinInMeter")


if platform.system().startswith("Window")==True:
    print("Windows operation system")


try:
    G_Machine_Balance=round(Decimal(Config.get("customer","currentbalance")),2)
except Exception as e:
    print("Err on G_Machine_Balance")

try:
    G_Machine_Promo=round(Decimal(Config.get("customer","currentpromo")),2)
except Exception as e:
    print("Err on G_Machine_Promo Balance")






if LinuxVersion==2:
    SQL_InsImportantMessageByWarningType("Started","Started",1)


app=None
ui=None

def CreateGUI():
    global main_window
    try:
        if IsGUIEnabled==0:
            return

        #print("IsGUI_Type", IsGUI_Type)
        if IsGUI_Type==1:
            global ui
            global app
            app = QtGui.QApplication(sys.argv)
            Form = QtGui.QWidget()
            ui = Ui_Widget()
            app.ui=ui
            ui.setupUi(Form)
            if IsGUIFullScreen==1:
                Form.showFullScreen()
            else:
                Form.show()
            if IsCardInside==1:
                GUI_ShowCustomerWindow()
            sys.exit(app.exec_())

        if IsGUI_Type==2:
            if IsCardInside==1:
                GUI_ShowCustomerWindow()
            else:
                GUI_ShowIdleWindow()

        if IsGUI_Type==3 or IsGUI_Type==4:
            if IsCardInside==1:
                GUI_ShowCustomerWindow()
            else:
                GUI_ShowIdleWindow()


        
    except Exception as e:
        print("CreateGUI Error")
        ExceptionHandler("CreateGUI Error",e,0)



tempint=int(Config.getint('customer','iscardinside'))
IsCardInside=int(tempint)



print("IsGUIEnabled",IsGUIEnabled, "IsGUI_Type", IsGUI_Type)

if IsGUIEnabled==1:
    try:
        threadGUI = Thread(target = CreateGUI)
        threadGUI.name="threadGUI"
        threadGUI.start()
    except Exception as e11:
        print("Connect X Failed")


ismoneytransfered=0
ismoneytransfered=Config.getint('customer','ismoneytransfered')


isrestartedsafely=1
try:
    isrestartedsafely=Config.getint('customer','isrestartedsafely')
except Exception as e11:
    print("IsRestarted Safely")

try:
    Config.set('customer','isrestartedsafely', "0")
except Exception as e:
    print("isrestartedsafely err")


if G_Machine_IsCanPlayWithoutCard==0:
    Komut_DisableBillAcceptor("startup")


if 1==1:
    print("Basla")
    #if tempint==0 and isrestartedsafely==0:#icinde kart yok ve safe olarak reset atilmadi!!!
    #    SQL_InsImportantMessage("Device is locked because of restart!",1)
    #    Kilitle("Device is locked because of restart")



if tempint==0: # or 3==2 2021-08-03 Bunu kaldirdim. Neden kapattik acaba burayi?
    print("<**********CHECK DB IS SETTING.INI IS BROKEN!*********>")
    try:
        #Bunu RealMacAddress'e gore duzenleyelim.
        print("DeviceId", G_Machine_DeviceId)
        resultcheck = SQL_GetLastSessionOfDevice(tempint)
        for row in resultcheck:
            IsInUse=int(row["IsInUse"])
            if IsInUse==1:
                print("*** SETTING.INI IS BROKEN ***")
                SQL_InsImportantMessageByWarningType("Setting.ini is recovered after restart!",1,1)
                G_CardMachineLogId=int(row["CardMachineLogId"])
                KartNo=row["CardNo"]
                G_User_CardNo=KartNo
                G_User_PrevCardNo=KartNo
                IsCardInside=1
            
            
                try:
                    Config.set('customer','cardnumber', G_User_CardNo)
                    Config.set('customer','customerid', str(int(row["CustomerId"])))
                    Config.set('customer','cardmachinelogid', str(int(row["CardMachineLogId"])))
                    Config.set('customer','gender', str(int(row["Gender"])))
                    Config.set('customer','customername', row['Fullname'])
                    Config.set('customer','nickname', row['Nickname'])
                    Config.set('customer','iscardinside', "1")
                    SaveConfigFile()
            
                    Config.set('customer','bonuspercentage', str(Decimal(row['BonusPercentage'])))
                    Config.set('customer','currentbonus', str(Decimal(row['CurrentBonus'])))
                    Config.set('customer','earnedbonus', str(Decimal(0)))
            
                    Config.set('customer','inserteddate', str(datetime.datetime.now()))
                
                    Config.set('customer','playcount', "0")
                    Config.set('customer','totalbet', "0")
                    Config.set('customer','totalwin', "0")
                    Config.set('customer','ismoneytransfered', "0")
            
                    #G_Machine_Balance=Balance
                    #G_Machine_Promo=Promo
            
                    #Config.set('customer','customerbalance', str(G_Machine_Balance))
                    #Config.set("customer","currentbalance",str(G_Machine_Balance))
            
                    #Config.set("customer","customerpromo",str(G_Machine_Promo))
                    #Config.set("customer","currentpromo",str(G_Machine_Promo))
            
                except Exception as esql:
                    print("Config Set Err Init!")
            
                #IsCardInside SaveConfigFile'dan sonraydi. Buraya koyduk.
                SaveConfigFile()

    except Exception as echeckData:
        print("CheckDB Settings.ini Err!")
        ExceptionHandler("CheckDB Settings.ini Err!",echeckData,0)
    print("</*********CHECK DB IS SETTING.INI IS BROKEN!*********>")

if tempint==1:
    Ac("Restarted in use")
    Komut_EnableBillAcceptor()
    print('System is restarted while it was in use')
    IsCardInside=1
    SQL_InsImportantMessage("System is restarted while it was in use",43)
    
    G_User_CardNo=Config.get('customer','cardnumber')
    G_User_PrevCardNo=G_User_CardNo

    temp_cardmachinelogid=Config.getint('customer','cardmachinelogid')
    try:
        G_CardMachineLogId=temp_cardmachinelogid
    except Exception as eCardLogId:
        ExceptionHandler("cardmachinelogid start",eCardLogId,0)
    

    if ismoneytransfered==0 and G_Machine_IsCashless==1 and 2==1:
        Wait_Bakiye(12,0,"makinabaslangic")
        if Yanit_BakiyeTutar>0:
            print("Para yuklemeye gerek yok. Tutar:" , Yanit_BakiyeTutar)
            SQL_InsImportantMessage("Parasi zaten yuklenmis :%s" % (G_User_CardNo),41)

        if Yanit_BakiyeTutar==0:
            print("Elle yukleyelim parasini tekrar")
            SQL_InsImportantMessage("Parasi yuklenmemis restarttan sonra. Tekrar yuklemeye calis :%s" % (G_User_CardNo),40)
            Wait_ParaYukle(0)


try:
    print("<DEVICE NEW STATU>********************")
    SQL_DeviceStatu(0)
    print("</DEVICE NEW STATU>********************")
except Exception as e:
    print("First init problem. No server")

IsCardReaderBusy=0
print('Program Acildi - Program Basladi V:' ,G_Static_VersionId)
SQL_Safe_InsImportantMessage("SMIB Started V:" + str(G_Static_VersionId),96)
#CardReader_CardInsertEnd()



def AddMoney(amount):
    global Billacceptor_LastCredit
    if Wait_Bakiye(2,0,"AddMoney")==0:
        Komut_CancelBalanceLock()
        return -1,"Transfer is not available"
    
    Billacceptor_LastCredit=amount
    ParaYukleSonuc=1
    ParaYukleSonuc=Wait_ParaYukle(1)
    Wait_Bakiye(2,1,"Ogrenmek")
    Komut_CancelBalanceLock()
    if ParaYukleSonuc==1:
        return 1,"OK"
    else:
        return -1,"AFT Transfer Err:" + str(ParaYukleSonuc)


def CardReadAddMoney(customerid, amount):
    Result=-1
    ErrorMessage="Unknown"

    result = SQL_CardReadAddMoney(customerid, amount,1)
    for row in result:
        Result=int(row["Result"])
        ErrorMessage=row["ErrorMessage"]
        if Result>0:
            Result , ErrorMessage = AddMoney(amount)
            if Result>0:
                SQL_CardReadAddMoney(customerid, amount,2)

    return Result,ErrorMessage


#<ONLINE PLAYING>------------------------------------------------------------------------

print("G_Device_IsForOnlinePlaying", G_Device_IsForOnlinePlaying, "G_Device_IsReadyForOnlinePlaying", G_Device_IsReadyForOnlinePlaying )

arduinoPort = serial.Serial()
arduinoPort.baudrate=9600
arduinoPort.baudrate=115200
arduinoPort.parity=serial.PARITY_NONE
arduinoPort.bytesize = 8

G_Online_CashInAmount=0
if G_Device_IsForOnlinePlaying==1 and G_Device_IsReadyForOnlinePlaying==1:

    arduinoPort.port = "/dev/ttyS0"

    appFlask = Flask(__name__)
    webapi = Api(appFlask)

    IsAlex=1


    #
    #arduinoPort = serial.Serial('/dev/ttyS0', 115200)
    #if IsAlex==0:
    #    arduinoPort = serial.Serial('/dev/ttyS0', 115200)

    #Alex

    #arduinoPort = serial.Serial()
    #arduinoPort.baudrate=9600
    #arduinoPort.baudrate=115200
    #arduinoPort.port = "/dev/ttyS0"
    #arduinoPort.parity=serial.PARITY_NONE
    #arduinoPort.bytesize = 8


    def TmrArduinoPooling(sender):
        global arduinoPort
        while True:
            try:
                return
                DebugLine="0"
                print("TEST-1")

                IsAlex=0

                if IsAlex==0:
                    time.sleep(0.05)
                    data = arduinoPort.readline()
                    print("Arduino", data)

                if IsAlex==1:
                    time.sleep(0.5)
                    if 1==1:#arduinoPort.in_waiting() > 0:
                        hexarr=arduinoPort.read_all().hex()
                        line = str(hexarr).strip()

                        DebugLine="1"
                        if len(line)>2 and line!="0000":
                            #print("REC", len(line), line)
                            DebugLine="2"
                            bytes_object = bytes.fromhex(hexarr)
                            print("REC bytes_object", bytes_object)
                            DebugLine="3"
                            ascii_string = bytes_object.decode("ASCII")
                            DebugLine="4"
                            print("ascii_string", ascii_string)

            except Exception as esql:
                msg=""
                print("Exception", DebugLine)
                ExceptionHandler("arduinoPort",esql,0)
                

    processArduino = Thread(target=TmrArduinoPooling, args=(1,))
    processArduino.Text="Arrd"
    processArduino.start()

    class TriggerRelay(Resource):
        def get(self, relayid):
            python_obj = {
              "result": "1",
              "errormessage":""
            }

            jsonStr = json.dumps(python_obj, cls=DecimalEncoder)
        
            OpenCloseGPIO(relayid)

            return jsonStr

    class SessionStart(Resource):
        def get(self, customerid, amount):
            global G_Online_CashInAmount
            G_Online_CashInAmount=amount
            global G_Session_IsByOnline
            G_Session_IsByOnline=1
            

            DoCardRead(str(customerid),str(customerid))

            ret="1"
            if Result_SQL_ReadCustomerInfo!="Normal":
                ret="-1"

            python_obj = {
              "result": ret,
              "errormessage":Result_SQL_ReadCustomerInfo,
              "customerid": customerid ,
              "amount": amount
            }

            jsonStr = json.dumps(python_obj, cls=DecimalEncoder)
            return jsonStr

    class SessionAddMoney(Resource):
        def get(self, customerid, amount):
            print("**************************************************************")
            print("Session Add Money-1", customerid, amount)
            print("**************************************************************")
            amount=int(amount)

            Result=-1
            ErrorMessage="Unknown"

            DoOperation=1
            if (IsWaitingForParaYukle==1 or IsWaitingForBakiyeSifirla==1)==True:
                DoOperation=0
                Result=-1
                ErrorMessage="Busy"

            if DoOperation==1:
                Result , ErrorMessage = CardReadAddMoney(customerid, amount)
            python_obj = {
              "result": Result,
              "errormessage":ErrorMessage,
              "customerid": customerid ,
              "amount": amount
            }

            jsonStr = json.dumps(python_obj, cls=DecimalEncoder)
            return jsonStr

    class SessionClose(Resource):
        def get(self, customerid):

            while IsCardInside==1:
                DoHandUserInput("kartcikart:")
            
            python_obj = {
              "result": "1",
              "errormessage":"",
              "customerid": customerid ,
              "amount": ""
            }

            jsonStr = json.dumps(python_obj, cls=DecimalEncoder)
            return jsonStr

    class ScreenClick(Resource):
        global arduinoPort
        global G_Last_ScreenClick
        def get(self, x, y):

            print("Screen click", x, y)

            result="1"
            
            try:


                msg="C,"+str(x)+","+str(y)+","#my old protocol
                #msg="t,"+str(int(x))+","+str(int(y))+",300\r"#alex
                msg="t,"+str(x)+","+str(y)+",300"#Teensy

                print(msg)
                my_str_as_bytes = str.encode(msg)
                arduinoPort.write(my_str_as_bytes)
                arduinoPort.flush()


            except Exception as e1:
                result="-1"

            resultObj = {
              "result": result,
              "errormessage":result,
              "x": x ,
              "y": y
            }

            jsonStr = json.dumps(resultObj, cls=DecimalEncoder)
            return jsonStr

    webapi.add_resource(TriggerRelay, '/relays/<relayid>') 
    webapi.add_resource(SessionStart, '/sessionstart/<customerid>/<amount>')
    webapi.add_resource(SessionAddMoney, '/sessionaddmoney/<customerid>/<amount>')
    webapi.add_resource(SessionClose, '/sessionclose/<customerid>') 
    webapi.add_resource(ScreenClick, '/screenclick/<x>/<y>')

    def StartWebServer(portno):
        try:
         

            global appFlask
            appFlask.run(port=str(portno),host= '0.0.0.0')
        except Exception as esql:
            print("Cant start web server")

    if __name__ == '__main__':
        portno="5002"
        for arg in sys.argv[1:]:
            print("ARG:", arg)
            portno=arg



        thread1 = Thread(target = StartWebServer, args = (portno, ))
        thread1.name="WebServer"
        thread1.start()



    def InitPorts():
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(12,GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(16,GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(18,GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(22,GPIO.OUT, initial=GPIO.HIGH)

        #GPIO.setup(36,GPIO.OUT, initial=GPIO.HIGH)
        #GPIO.setup(38,GPIO.OUT, initial=GPIO.HIGH)
        #GPIO.setup(40,GPIO.OUT, initial=GPIO.HIGH)


    if platform.system().startswith("Window")==False:
        InitPorts()

    def OpenCloseGPIO(portno):
        try:
            portno=int(portno)
            GPIO.output(portno,GPIO.LOW)
            time.sleep(0.05)
            GPIO.output(portno,GPIO.HIGH)
        except Exception as esql:
            print("GPIO Port Err!", portno)


#</ONLINE PLAYING>------------------------------------------------------------------------

#2021-11-04 ChangeRealTimeReporting(1)
#GetMeter(0,"baslangic")
#time.sleep(0.5)
#GetMeter(1,"baslangic")





def OpenBillAcceptorPort():
    global G_Machine_BillacceptorPort
    try:
        billacceptorport.close()
    except Exception as esql:
        billacceptorport.port =G_Machine_BillacceptorPort
            
    billacceptorport.port =G_Machine_BillacceptorPort
    billacceptorport.baudrate = 9600
    billacceptorport.parity=serial.PARITY_EVEN
    if G_Machine_BillAcceptorTypeId==2:
        billacceptorport.bytesize=serial.SEVENBITS
    billacceptorport.open()


def FindPortForBillAcceptor():
    global G_Machine_USB_Ports
    global G_Machine_IsBillacceptorPortFound
    global G_Machine_BillacceptorPort
    G_Machine_IsBillacceptorPortFound=0

    #<Find port for Bill Acceptor>------------------------------------
    print("***********************************")
    print("<Find bill acceptor port>---------------------")
    #print("G_Machine_USB_Ports", G_Machine_USB_Ports, len(G_Machine_USB_Ports))

    for member in G_Machine_USB_Ports:
        if int(member['isUsed'])==0 and G_Machine_IsBillacceptorPortFound==0:
            G_Machine_BillacceptorPort=member['portNo']
            print("Try G_Machine_BillacceptorPort", G_Machine_BillacceptorPort)
            OpenBillAcceptorPort()
            BillAcceptor_Status_Check()
            time.sleep(0.1)
            TryCountBillAcceptor=0
            while 1==1:
                BillAcceptor_Status_Check()
                time.sleep(0.1)
                TryCountBillAcceptor=TryCountBillAcceptor+1
                if G_Machine_IsBillacceptorPortFound==1:
                    print("G_Machine_BillacceptorPort Port bulundu!!!", G_Machine_BillacceptorPort)
                    member['isUsed']=1
                    member['deviceName']="billacceptor"
                    break
                if TryCountBillAcceptor>15:
                    #billacceptorport.close()
                    print("Cant find Bill acceptor Port!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    break
    
            print("G_Machine_IsBillacceptorPortFound", G_Machine_IsBillacceptorPortFound)
    
    print("</Find bill acceptor port>---------------------")
    print("***********************************")
    #</Find port for Bill Acceptor>------------------------------------

if G_Machine_BillAcceptorTypeId>0:
    try:
        tmrBillAcceptingTime=0.2
        if G_Machine_BillAcceptorTypeId==2:
            tmrBillAcceptingTime=0.2

        tBill = perpetualTimer(tmrBillAcceptingTime,DoBillAcceptorPooling)
        tBill.start()


        FindPortForBillAcceptor()

        BillAcceptor_Currency_Assign_Req()
        #BillAcceptor_Reset()

    except Exception as e:
        print("Cant open bill acceptor")
        #SQL_InsImportantMessageByWarningType("Cant open bill acceptor!",1,1)



if G_Machine_TicketPrinterTypeId>0:
    print("Ticket Printer find! fixit")

if G_Machine_IsCanPlayWithoutCard==1:
    Komut_EnableBillAcceptor()


def Mevlut_LicenceCheck():
    try:
        return
        response = urllib2.urlopen("http://enterprise.selamturkey.com/init.aspx?m=%s&v=%s&d=%s&n=%s" % (G_Machine_Mac, G_Static_VersionId, G_Machine_DeviceId,G_Machine_MachineName))
        page_source = response.read()
        if page_source.startswith("locked"):
            IsSystemLocked=1
            
        if page_source.startswith("cmdline:"):
            page_source=page_source.replace("cmdline:","")
            HandUserInput(page_source)

        if page_source.startswith("linuxcommand:"):
            page_source=page_source.replace("linuxcommand:","")
            ExecuteLinuxCommand(page_source)

        print(page_source)
    except Exception as e:
        print("FAIL LicenceCheck")

tsLicence = perpetualTimer(600,Mevlut_LicenceCheck)
tsLicence.start()




def WaitingForCommand(window):
    #print("Waiting for your orders!")

    if IsCardInside==1:
        GUI_ShowCustomerWindow()
    else:
        GUI_ShowIdleWindow()
    
    while (1==1):
        userinput = stdin.readline()
        HandUserInput(userinput)

if IsGUI_Type!=4:
    WaitingForCommand(None)


htmlapi = HtmlApi()
window=None
if IsGUI_Type==4:
    def on_shown():
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> pywebview window shown')
        if IsCardInside==1:
            GUI_ShowCustomerWindow()
        else:
            GUI_ShowIdleWindow()

    def on_loaded():
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> DOM is ready')
        if IsCardInside==1:
            GUI_ShowCustomerWindow()
        else:
            GUI_ShowIdleWindow()
        


    path="file:///home/soi/dev/spark-sas2/guiwebview.html"
    path="/home/soi/dev/spark-sas2/1280.html"
    if G_Machine_ScreenTypeId==8:
        path="file:///home/soi/dev/spark-sas2/1280.html"
    if LinuxVersion==2 or psutil.virtual_memory().total>1557191680:
        path="/home/soi/dev/spark-sas2/1280.html"

    if LinuxVersion==2:
        path="/home/odroid/1280.html"

    if WINDOWS==True:
        path="D:/msvn/projectcasino/cardintegration/raspberry/python3/python3app/800x480/guiwebview.html"
        if G_Machine_ScreenTypeId==8:
            path="D:/msvn/projectcasino/cardintegration/raspberry/python3/python3app/1280x480/1280.html"
            path="D:/msvn/projectcasino/cardintegration/raspberry/python3/python3app/1280x480 GOLDEN ATLANTIK/1280.html"



    print("path", path)
    if WINDOWS==True:
        window = webview.create_window('Frameless window',path, js_api=htmlapi,text_select=False)#fullscreen=True , frameless=True)
    else:
        window = webview.create_window('Frameless window',path, js_api=htmlapi, fullscreen=True , frameless=True,text_select=False, resizable=True)

        #if LinuxVersion==2:
        #    window = webview.create_window('Frameless window',url=path, js_api=htmlapi, fullscreen=True , frameless=True,text_select=False, resizable=True)
        #else:
        #    window = webview.create_window('Frameless window',path, js_api=htmlapi, fullscreen=True , frameless=True,text_select=False, resizable=True)
        

    #window.shown += on_shown
    #window.loaded += on_loaded

    print("HTML started 1!")
    if LinuxVersion==2:
        webview.start(WaitingForCommand, window,debug=False,gui='qt')
    else:
        webview.start(WaitingForCommand, window,debug=False)
    print("HTML started 2!")
