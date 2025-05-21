#!/usr/bin/python

import datetime
import time
from threading import Timer,Thread,Event
from sys import stdin

import ctypes


'''
perpetualTimer Class Basladi
'''
class perpetualTimer():

   def __init__(self,t,hFunction):
      self.t=t
      self.hFunction = hFunction
      self.thread = Timer(self.t,self.handle_function)

   def handle_function(self):
      self.hFunction()
      self.thread = Timer(self.t,self.handle_function)
      self.thread.start()

   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()
'''
perpetualTimer Class Bitti
'''









def main():

    CheckCardDevice()

    t2 = perpetualTimer(0.5,CheckCardDevice)
    t2.start()




G_Sys_Card_LastStatus=0
G_Sys_LastCardSuccess=datetime.datetime.now()
def CheckCardDevice():
    global G_Sys_Card_LastStatus
    global G_Sys_LastCardSuccess


    Result=0
    try:
        CardArrayType = ctypes.c_ubyte * 1024
        CardArray = CardArrayType()

        
        CardReaderLib = ctypes.cdll.LoadLibrary('/home/pi/crt_288B_UR.so')
        CurrentCardReaderStatus=CardReaderLib.CRT288B_OpenDev(0,0,0)
        if CurrentCardReaderStatus==-5:
            if G_Sys_Card_LastStatus!=-5:
                G_Sys_Card_LastStatus=CurrentCardReaderStatus
                print("USB Kart okuyucusunda hata!!!**************************************")
                #SetMachineStatu("Card reader is not working")
                #SQL_InsImportantMessageByWarningType("Card reader is not working. Please control card reader",4,12)

            return
        G_Sys_Card_LastStatus=CurrentCardReaderStatus


        Result = CardReaderLib.CRT288B_GetCardUID(CardArray)
        CardReaderLib.CRT288B_CloseDev()



        
        if Result==-1:
            print("Python: ERROR ON GETCARDUID, it returned", Result, " G_Sys_LastCardSuccess: ", G_Sys_LastCardSuccess, " CurrentDate", datetime.datetime.now())
        

        #Gelen=''.join([chr(i) for i in CardArray]).rstrip('\x00')
        GelenStr=bytearray(CardArray).hex().upper()


        #59040077FBE3F30
        while (GelenStr.startswith("590400")==True):
            GelenStr=GelenStr[6:len(GelenStr)]
            GelenStr=GelenStr[0:8]
        
        IsCardReadedOk=0
        if len(GelenStr)==8:

            print("Result", Result, datetime.datetime.now(), " GelenStr", GelenStr)
            G_Sys_LastCardSuccess=datetime.datetime.now()


    except:
        print("Exception oldu....")
        Result=2





while (1==1):
    main()
    userinput = stdin.readline()
    print(userinput)
