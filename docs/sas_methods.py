import time

# --- Asset Number Utilities ---
def ReadAssetToInt(d):
    HexaString = d
    if len(HexaString) % 2 != 0:
        HexaString = "0" + HexaString
    ReversedHexaString = ""
    i = len(HexaString) - 2
    while i >= 0:
        ReversedHexaString = ReversedHexaString + HexaString[i:i+2]
        i = i - 2
    return int(ReversedHexaString, 16)

# Minimal CRC placeholder (replace with real implementation if needed)
def GetCRC(komut):
    # This is a placeholder. Use the real CRC16 Kermit as in the reference for production.
    # For now, just append '0000' as CRC for testing.
    return komut + '0000'

# --- Read asset number from SAS at startup ---
def print_asset_number_from_sas():
    try:
        # SAS command for AFT registration status: 0x73, reg_code=0xFF
        # Format: [address][73][01][FF][CRC]
        # Assume address is '01' (can be changed if needed)
        command = '017301FF'
        command_crc = GetCRC(command)
        SAS_SendCommand('ReadAssetNo', command_crc, 0)
        # Wait for response (simulate, in real code this should be event/callback driven)
        for _ in range(10):
            time.sleep(0.2)
            # Assume GetDataFromSasPort(0) returns the hex string response
            response = GetDataFromSasPort(0)
            if response and response.startswith('0173'):
                # Parse asset number from response
                # Response: [address][73][status][asset_number(8)][registration_key(40)]...
                asset_hex = response[6:14]
                asset_dec = ReadAssetToInt(asset_hex)
                print(f"[ASSET NO] HEX: {asset_hex}  DEC: {asset_dec}")
                return
        print("[ASSET NO] Could not read asset number from SAS.")
    except Exception as e:
        print(f"[ASSET NO] Error reading from SAS: {e}")

# Print asset number from SAS at startup
print_asset_number_from_sas()




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
                        conn = pymssql.connect(host=G_DB_Host, user=G_DB_User, password=G_DB_Password, database=G_DB_Database,tds_version='7.2')
                        conn.autocommit(True)
                        cursor = conn.cursor(as_dict=True)
                        cursor.callproc('tsp_GetDeviceGameInfo', (G_Machine_DeviceId,  G_SelectedGameId))

                        for row in cursor:
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

                        conn.close()
                    except Exception as ecardtype:
                        ExceptionHandler("tsp_GetDeviceGameInfo",ecardtype,0)
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






-------------------



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




-------------------------

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






#--------------------------


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

                                conn = pymssql.connect(host=G_DB_Host, user=G_DB_User, password=G_DB_Password, database=G_DB_Database,tds_version='7.2')
                                conn.autocommit(True)
                                cursor = conn.cursor(as_dict=True)
                                cursor.callproc('tsp_CheckBillacceptorIn', (G_Machine_Mac, G_Machine_BillAcceptorTypeId, cardmachinelogid, G_User_CardNo, BankNoteCode, Billacceptor_LastCountryCode,Billacceptor_LastDenom, Billacceptor_LastDenomHex ))

                                for row in cursor:
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


                                conn.close()
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







#--------------------------------



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

    
Cas

# --- Asset Number Utilities ---
def ReadAssetToInt(d):
    HexaString = d
    if len(HexaString) % 2 != 0:
        HexaString = "0" + HexaString
    ReversedHexaString = ""
    i = len(HexaString) - 2
    while i >= 0:
        ReversedHexaString = ReversedHexaString + HexaString[i:i+2]
        i = i - 2
    print("Read: HexaString", HexaString)
    print("Read: ReversedHexaString", ReversedHexaString)
    print("Int Read:", int(ReversedHexaString, 16))
    return int(ReversedHexaString, 16)


def print_asset_number_at_startup():
    try:
        import config_manager
        config = config_manager.ConfigManager()
        asset_hex = config.get('sas', 'assetnumber', fallback='00000000')
        asset_dec = ReadAssetToInt(asset_hex)
        print(f"[ASSET NO] HEX: {asset_hex}  DEC: {asset_dec}")
    except Exception as e:
        print(f"[ASSET NO] Could not read asset number: {e}")

# Print asset number at startup
print_asset_number_at_startup()