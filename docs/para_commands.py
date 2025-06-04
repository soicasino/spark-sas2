
def AddLeftBCD(numbers, leng):
    
    numbers=int(numbers)

    retdata=str(numbers)

    if len(retdata)%2==1:
        retdata="%s%s" % ("0", retdata)


    countNumber=len(retdata)/2 #1250 4
    kalan=(leng-countNumber)        #5-4 = 1

    retdata=AddLeftString(retdata, "00",kalan)

    return retdata



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
                #    Komut_Interragition("ImpossibleWrongTransaction Mevlut")

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





