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

import serial
import re

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
import sys
import datetime
import socket
import threading
from threading import Timer,Thread
import time
import sys

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


import urllib as urllib2
os.putenv('DISPLAY', ':0.0')





Config = ConfigParser.ConfigParser()
ConfigFile="settings.ini"


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


FilePathSO="/home/soi/crt_288B_UR.so"
if LinuxVersion==3:
    FilePathSO="/home/soi/dev/spark-sas2/crt_288B_UR.so"



if platform.system().startswith("Window")==False:
    import termios


G_Session_IsByOnline=0




import os, fnmatch


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





if os.name != "nt":
    import fcntl
    import struct

    def get_interface_ip(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
                                ifname[:15]))[20:24])


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






# </HTML GUI START>-----------------------------------------------------------
########################################################################

#<GUI START>----------------------------------------


        


#</MAIN SCREEN BUTTONS>########################################################################################################










# </GUI START>-----------------------------------------------------------        
########################################################################





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



    SQL_Safe_InsImportantMessage("Card ejected",68)
    thread1 = Thread(target = CardReaderCommand, args = ("02000232300301", ))
    thread1.name="EjCard"
    thread1.start()
    #CardReader_ColorCommand("02000232300301")
#</CARD READER RENKLI>---------------------------------

#<BILL ACCEPTOR HELPER>------------------------------------------------------------------------
billacceptorport = serial.Serial()



Mei_LastAckNack=""


G_LastBillAcceptor_AcKapaCommand=datetime.datetime.now()
IsBillacceptorOpen=0


Count_StatusCheck=0


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





#<Dictionary Currencies>--------------------------





dictCurrencies = []


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





print("Start")
oMainwindow=None

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
if G_PG_Host=="10.0.0.59":
    IsDebugMachineNotExist=0


#<DATABASE HELPER>--------------------------------------------------------------

# Initialize database helper
db_helper = DatabaseHelper()


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

#<CEFPYTHON>--------------------------------------------------------------------------




G_Machine_BonusId=0
G_Machine_BonusAmount=0
G_NextVisit_WonAmount=Decimal(0)
G_NextVisit_KioskBonusId=0







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




if IsGUI_Type==3:
    try:
        threadGUIHtml = Thread(target = CreateHTMLGui)
        threadGUIHtml.name="CreateHTMLGui"
        threadGUIHtml.start()
    except Exception as e11:
        print("Exception threadGUIHtml")



Global_ParaSifirla_84=0
Global_Count_YanitHandle=0
Yukle_FirstTransaction=0
Yukle_LastTransaction=0
Global_ParaYukleme_TransferStatus="0"
IsWaitingForParaYukle=0
CashIn_CompletedBy=""


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


Bakiye_WaitingForGameLockCount=0
IsWarnedForTakeWin=0
LastCommand_Bakiye_Sender=0
#sender: 1:cardin 2: cardout 3:restart 4:jackpot 5:87TS 6:81TS 7:9FTS   8:82TS  9:84TS   10:83TS   11:BakiyeSorgula  12:Restarttan sonra, 13: ekran wallet buton


#<GUI HELPER>-----------------------------------------------------------------

G_Last_NextionCommand=datetime.datetime.now()
NextionCommandStr = []
NextionCommandCount=0


Nextion_Count_Cmd=0



NoNetwork_Count=0
ErrorMessage_NoNetwork="NO NETWORK"
GUI_LastMainStatuMessage=""




GUI_CountTimer=1



GUI_UpdateBonus_Count=0
Bonus_GameStart_Wagered=Decimal(0)


G_User_CardType=0
G_Session_CardExitStatus=0
G_SAS_IsProblemOnCredit=0
G_SAS_Transfer_Warning_DoorIsLocked=0





BillAcceptor_Amount=Decimal(0)



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






G_Config_IsCashoutSoft=0




G_IsStreamingInit=0
G_MessageCount=0
G_Machine_OnlineCount=0
G_Machine_DefBetFactor=1
G_Machine_Failed_DeviceId_Zero=0
#MessageType: 0: Init 1: Program acildi, 2: Operation, 3: Online Message Interval


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


#Type: 1 Remote Handpay, 2 Money existed, 3: Jackpot, 4: Handpay Slip, 5# Slip

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

G_BillAcceptorDisabled=datetime.datetime.now()


Last_ParaYukle_TransferType=0
Last_ParaYukleDate=datetime.datetime.now()


AssetNumberInt=0

Global_ParaYuklemeFail_SQL=0


IsCollectButtonProcessInUse=0



G_LastInterragition=datetime.datetime.now()


BalanceQuery_GameLockStatus=""
IsWaitingForBakiyeSorgulama=0


BakiyeSorgulama_Count=0
BakiyeSorgulama_Sender=0
IsBalanceQueryForInfo=1
#isForInfo-> 0: Needed, 1: Bilgi icin,



Yanit_RestrictedPoolID=""
Yanit_BakiyeTutar=0
Yanit_RestrictedAmount=0
Yanit_NonRestrictedAmount=0


Last_Draw_BakiyeTutar=0
Last_Draw_RestrictedAmount=0
Last_Draw_NonRestrictedAmount=0
Last_ParaSifirlaDate=datetime.datetime.now()
#2021-07-20


Cashout_ImpossibleWrongTransaction=0


Step_CardExit=""
#sender: 0: realcard exit, 1:removecardcommand, 2: Cant upload money, 123: cashout button is pressed


Step_RemoveCustomerInfo=""
Cashout_InProgress=0
Cashout_Source=0
#sender: 0: realcard exit, 1:removecardcommand, 2: Cant upload money, 3: Cashout and reserve 123: cashout button is pressed


G_LastCheckPorts=datetime.datetime.now()
G_LastSystemCPUCheck=datetime.datetime.now()- datetime.timedelta(minutes=30)
Prev_HTMLWarning=""
PreviousIsGuiReady=0
Is_MD5Checksum=0
#5snde bir


G_Count_IsOnline=0
LastMeterDate=datetime.datetime.now()

Result_SQL_ReadCustomerInfo=""



DebugPicture=0
IsLocked_NetworkCheck=0
WaitingForGameEndDBInsert=0
G_Count_CardOut=0
#sender: 0: realcard exit, 1:removecardcommand, 2: Cant upload money, 3: Force handpay



Step_CardIsRemoved=""

IsInstantCardInside=0
IsCardReaderBusy=0

   
G_Sys_CardNotWorkingCount=0


G_Sys_GetCardUID_Error=0
G_Sys_Card_LastStatus=0
G_Sys_LastCardSuccess=datetime.datetime.now()
CardReaderLib=None


CardReaderCommandStr = ""


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




G_Last_81=datetime.datetime.now()
G_Last_80=datetime.datetime.now()

G_IsComunicationByWindows=-1


IsSendByThread=0
GENEL_GonderilecekKomut=""


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


#sender: 0: realcard exit, 1:removecardcommand 4: Cashout button is pressed



G_Count_AFT_YanitHandle=0
G_Count_AFT_TransferIsCompleted=0
IsHandleReceivedSASCommand=0
G_Wagered=0
Last_SAS_AcceptedBillAcceptorMessage=""
IsHandpayOK=0
Prev_Wagered=Decimal(0)


#def HandleReceivedSASCommand(tdata):





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


Nextion_LastReceivedDate=datetime.datetime.now()
Nextion_CurrentStep=""
Nextion_MachineName=""
Nextion_Busy=0



nextionport = serial.Serial()




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










tempstr=""
tempstr=Config.get('pi','mac')
if str(G_Machine_Mac)!=str(tempstr):
    print("Farkli bir mac adresi var")
    Config.set('pi','mac', G_Machine_Mac)
    SQL_InsImportantMessage("SD Card is installed to another machine! E:%s Y:%s" % (tempstr, G_Machine_Mac),5)
    Mevlut_Warn(1,"SD Card is installed to another machine! E:%s Y:%s" % (tempstr, G_Machine_Mac))
    SaveConfigFile()



print("----")





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
                #msg="t,"+str(int(x))+","+str(y)+",300\r"#alex
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
