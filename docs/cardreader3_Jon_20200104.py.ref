import serial

import datetime
from time import sleep
import sys
import signal
from threading import Timer, Thread, Event
from sys import stdin
from decimal import Decimal
from time import sleep
import time
from sys import stdin
import socket
import os
import signal

#import pymssql
#import _mssql

IsCardInside = 0
IsCardReaderBusy = 0


G_CardLastDate=datetime.datetime.now()

G_LastCardExit = datetime.datetime.now()
G_LastCardEnter = datetime.datetime.now()


def GUI_ShowIfPossibleMainStatu(statumsg):
    print(statumsg)


def CardIsRemoved(sender):
    #return
    print("<Kart cikartma islemi baslasin.>---------------")
    global IsCardReaderBusy
    global IsCardInside
    global G_User_CardNo

    print("########################################Card is removed")
    # turn off LED
    #CardReaderCommand("020005803300000003B7")

    
    #255 Beyaz. OK
    # white LED always blink
    CardReaderCommand("02000580313702FF037F")
    time.sleep(3)

    IsCardReaderBusy = 0
    IsCardInside = 0
    G_User_CardNo = ""
    #Renksiz yap
    #CardReaderCommand("020005803300000003B7")

    # Our device will in reset which it will take like 2s before accept command! so we should use enalbe LED gradient
    #Reset yap
    #CardReaderCommand("02000230300303")
    #print("</Kart cikartma islemi baslasin.>---------------")
    #time.sleep(3)

    # enable gradient
    CardReaderCommand("020005803200000003B6")
    #print("</Enalbe LED gradient.>---------------")

    #CardReaderCommand("020005803300000003B7")
    print("</Kart cikartma islemi baslasin.>---------------")


G_LastCardEnter = datetime.datetime.now()

def CardReader_ColorCommand(cmd):
    print("cmd", cmd)
    thread1 = Thread(target = CardReaderCommand, args = (cmd, ))
    thread1.start()

def CardReader_CardExitStart():
    # white LED always blink
    CardReader_ColorCommand("02000580313702050385")


def CardReader_CardProblem():
    # red LED always blink
    CardReader_ColorCommand("020005803131020A038C")


def CardReader_CardExitEnd():
    # enable gradient
    CardReader_ColorCommand("020005803200000003B6")


def CardReader_CardInsertStart():
    #255 Yesil
    CardReader_ColorCommand("020005803132023203B7")


def CardReader_CardInsertEnd():
    #Renksiz yap
    CardReader_ColorCommand("020005803300000003B7")
#</CARD READER RENKLI>---------------------------------

def DoCardRead(tdata):
    #return
    print("<Kart takma islemi baslasin. cardno>", tdata)
    global IsCardReaderBusy
    global IsCardInside
    global G_User_CardNo
    global G_LastCardEnter

    G_User_CardNo = tdata

    IsCardInside = 1
    # turn off LED
    CardReaderCommand("020005803300000003B7")

    #255 Yesil
    CardReaderCommand("02000580313201FF0379")
    time.sleep(3)

    IsCardReaderBusy = 0

    G_LastCardEnter = datetime.datetime.now()

    #Renksiz yap
    #CardReaderCommand("020005803300000003B7")
    CardReaderCommand("020005803300000003B7")

    
    print("</Kart takma islemi bitti. cardno>", tdata)


'''
perpetualTimer Class Basladi
'''

class perpetualTimer():

   def __init__(self, t, hFunction):
      self.t = t
      self.hFunction = hFunction
      self.thread = Timer(self.t, self.handle_function)

   def handle_function(self):
      self.hFunction()
      self.thread = Timer(self.t, self.handle_function)
      self.thread.start()

   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()

'''
perpetualTimer Class Bitti
'''

def ExceptionHandler(name, e, Insert2DB):
    try:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("Exception On ", name, exc_type, fname, exc_tb.tb_lineno)
        if Insert2DB == 1:
            print("LAN")
    except Exception as ex:
        print("Exception Handler Exploded: ", name)


G_User_CardNo = ""

#<CARD READER HELPER>------------------------------------------------------------------------
def print_time_stamp_ms():
    return
    ct = time.time()
    local_time = time.localtime(ct)
    data_head = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    data_secs = (ct - int(ct)) * 1000
    time_stamp = "%s.%03d" % (data_head, data_secs)
    print(time_stamp)
    # = ("".join(time_stamp.split()[0].split("-"))+"".join(time_stamp.split()[1].split(":"))).replace('.', '')
    #print(stamp)

cardreader = serial.Serial()

def OpenCloseCardreaderport():
    cardreader.port = "/dev/cu.SLAB_USBtoUART"
    #cardreader.port = "COM4"
    cardreader.baudrate = 9600
    cardreader.bytesize = 8
    cardreader.parity = serial.PARITY_NONE
    cardreader.stopbits = 1
    cardreader.timeout = 0.2
    cardreader.open()

OpenCloseCardreaderport()


CardReaderCommandStr = ""


def CardReaderCommand(data):
    global CardReaderCommandStr

    while len(CardReaderCommandStr) > 0:
        print("Please wait.. Another command is being sent to card reader",
              CardReaderCommandStr)
        time.sleep(0.1)

    CardReaderCommandStr = data


def Decode2Hex(input):
    return bytearray.fromhex(input)


def CardReaderSendCommandImmediately(sendstring, doPooling):
    cardreader.flushInput
    hex_data = Decode2Hex(sendstring)#.decode("hex")
    bytearray = map(ord, hex_data)
    cardreader.write(hex_data)

    if doPooling == 1 and 2 == 2:
        time.sleep(0.1)
        #DoCardReaderPooling(doPooling)

Count_Total=0
Renk=0

def CardRead_rCloud(sender=0):
    global IsCardReaderBusy
    global G_User_CardNo
    global CardReaderCommandStr
    global Count_Total
    global Renk
    global G_CardLastDate

    print("G_CardLastDate=datetime.datetime.now()", G_CardLastDate, datetime.datetime.now())
    IsSpecialyCommand = False
    # mifare S50 get uid
    senddata = "02000235310307"

    '''
    Count_Total=Count_Total+1
    if Count_Total%4==0:
        Count_Total=0
        Renk=Renk+1
        #Renk=0
        if Renk==1:
            CardReader_CardExitStart()

        if Renk==2:
            CardReader_CardExitEnd()

        if Renk==3:
            CardReader_CardInsertStart()

        if Renk==4:
            CardReader_CardInsertEnd()

        if Renk==5:
            CardReader_CardProblem()
            Renk=0
    '''

    if len(CardReaderCommandStr) > 0:
        #print("-----------------------------------------")
        print("Ozel komut", CardReaderCommandStr)
        IsSpecialyCommand = True
        senddata = CardReaderCommandStr
        CardReaderCommandStr = ""

    tdata = ""
    try:
        #print("-----------------------------------------")
        print_time_stamp_ms()

        CardReaderSendCommandImmediately(senddata, 0)
        print("Sent data", senddata)
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
                    if len(tdata)>2:
                        print("tdata", tdata)
                        
                    # we should check response frame valid
                    # check frame start
                    # check frame length
                    # check frame end
                    # check frame BCC
                    if tdata.startswith("02") != True: # check frame start
                         print("+++++++Response frame error+++++++")
                    else:
                        if IsCardReaderBusy == 0:
                            DoCardExitProcess = 0

                            if tdata.startswith("020003") == True and tdata.find("02000380")==-1 and IsCardInside == 1:
                                IsMessageHandled = 1
                                DoCardExitProcess = 1

                            if tdata.startswith("020007") == True:

                                G_CardLastDate=datetime.datetime.now()
                                CardIndexLength = tdata.find("353159")+6
                                CardNo = tdata[CardIndexLength: CardIndexLength+8]
                                print("tdata1111111111111111111#################################", tdata)
                                print("CardNo222222222222222222#################################", CardNo)
                                
                                if IsCardInside == 0 and IsCardReaderBusy == 0:
                                    IsCardReaderBusy = 1

                                    try:
                                        GUI_ShowIfPossibleMainStatu("Card is inserted!")
                                        
                                        processGameoperation = Thread(target=DoCardRead, args=(CardNo,))
                                        processGameoperation.start()

                                    except Exception as ecard:
                                        ExceptionHandler("DoCardRead Thread", ecard, 0)

                                if IsCardInside == 1:
                                    if G_User_CardNo != CardNo:
                                        print("Su an farkli bir kart var cihazda!",
                                            G_User_CardNo, CardNo)
                                        DoCardExitProcess = 1

                            if DoCardExitProcess == 1:
                                G_CardLastDate=datetime.datetime.now()

                                LastCardEnterDiff = (
                                    datetime.datetime.now()-G_LastCardEnter).total_seconds()
                                if LastCardEnterDiff <= 5:
                                    print("Wait at least 5 seconds for card exit",
                                        LastCardEnterDiff)
                                    return

                                IsCardReaderBusy = 1
                               
                                try:
                                    processGameoperation = Thread(
                                        target=CardIsRemoved, args=(0,))
                                    processGameoperation.start()
                                    #CardIsRemoved(0)
                                except Exception as ecard:
                                    ExceptionHandler("CardIsRemoved Thread", ecard, 0)

                        #endif IsCardReaderBusy==0:
                else :
                    print("+++++++ Not receive data +++++++")
            else :
                 print("+++++++ Response frame error +++++++")
        else :
            print("+++++++ Not receive data ++++++++")
    except Exception as e:
        ExceptionHandler("CardRead_rCloud", e, 0)
         

#</CARD READER HELPER>------------------------------------------------------------------------

# we recomment uing thread doing the whole process and execute command which one by one, like below
# Tx: 020005803300000003B7
# Rx: 06  (max 100ms timeout)
# Tx: 05
# Rx: 02000380335903E8 (max 300ms timeout depend on response)
# ...
# Other command please reference communication protocol
#

t4 = perpetualTimer(0.1, CardRead_rCloud)
t4.start()


#Renksiz yap
# turn off LED light
#CardReaderCommand("020005803300000003B7")

# enable gradient
CardReader_ColorCommand("020005803200000003B6")

while True:
    userinput = stdin.readline()
    userinput = userinput.replace("\n", "")
    userinput = userinput.replace("\\n", "")

    if userinput == "k:": #red LED always light
        CardReaderCommand("02000580303100000385")

    if userinput == "cikart:" or userinput == "cikar:":
        CardReaderCommand("02000232300301")

    if userinput == "s:": #turn off LED light
        CardReaderCommand("020005803300000003B7")

    if userinput.startswith('q'):
        #t4.cancel
        #cardreader.close
        print("Exit...")
        break
    
    print("Command,", userinput)
