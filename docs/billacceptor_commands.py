

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



