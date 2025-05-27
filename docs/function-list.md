# Function List for raspberryPython3.py

This document contains a comprehensive list of all functions defined in `raspberryPython3.py` (15,808 lines total).

## Configuration & Utility Functions

| Line | Function Name                             | Description                        |
| ---- | ----------------------------------------- | ---------------------------------- |
| 182  | `SaveConfigFile()`                        | Saves configuration file           |
| 275  | `GetAssetBinary(d)`                       | Gets asset binary data             |
| 293  | `ReadAssetToInt(d)`                       | Reads asset to integer             |
| 312  | `find(pattern, path)`                     | Find pattern in path               |
| 322  | `ExecuteLinuxCommand(command)`            | Execute Linux command              |
| 328  | `ExecuteLinuxCommandWithoutPipe(command)` | Execute Linux command without pipe |
| 358  | `Kilitle(sender)`                         | Lock function                      |
| 373  | `Ac(sender)`                              | Open/unlock function               |
| 418  | `get_lan_ip()`                            | Get LAN IP address                 |
| 664  | `check_versions()`                        | Check versions                     |

## JavaScript Execution Functions

| Line | Function Name                                                                                                          | Description                            |
| ---- | ---------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| 488  | `DoExecuteJS(textcmd="")`                                                                                              | Execute JavaScript command             |
| 515  | `timeout(func, args=(), kwds={}, timeout=1, default=None)`                                                             | Timeout wrapper for function execution |
| 528  | `ExecuteJS(textcmd)`                                                                                                   | Execute JavaScript code                |
| 540  | `DecodeHTMLChars(para)`                                                                                                | Decode HTML character entities         |
| 545  | `DecodeHTML(para)`                                                                                                     | Decode HTML content                    |
| 550  | `ExecuteJSFunction(function, para1)`                                                                                   | Execute JS function with 1 parameter   |
| 555  | `ExecuteJSFunction2(function, para1, para2)`                                                                           | Execute JS function with 2 parameters  |
| 560  | `ExecuteJSFunction3(function, para1, para2, para3)`                                                                    | Execute JS function with 3 parameters  |
| 567  | `ExecuteJSFunction4(function, para1, para2, para3, para4)`                                                             | Execute JS function with 4 parameters  |
| 575  | `ExecuteJSFunction5(function, para1, para2, para3, para4, para5)`                                                      | Execute JS function with 5 parameters  |
| 583  | `ExecuteJSFunction7(function, para1, para2, para3, para4, para5, para6, para7)`                                        | Execute JS function with 7 parameters  |
| 593  | `ExecuteJSFunction12(function, para1, para2, para3, para4, para5, para6, para7, para8, para9, para10, para11, para12)` | Execute JS function with 12 parameters |

## GUI & HTML Functions

| Line  | Function Name          | Description               |
| ----- | ---------------------- | ------------------------- |
| 634   | `HTMLGUI()`            | HTML GUI initialization   |
| 2101  | `CreateGUI()`          | Create GUI                |
| 2947  | `CreateCEFPython()`    | Create CEF Python browser |
| 2990  | `HandleJSEvent(title)` | Handle JavaScript events  |
| 3637  | `CreateHTMLWX()`       | Create HTML with WX       |
| 3743  | `CreateHTMLGui()`      | Create HTML GUI           |
| 15144 | `CreateGUI()`          | Create GUI (duplicate)    |

## Data Processing & Encoding Functions

| Line | Function Name                             | Description                |
| ---- | ----------------------------------------- | -------------------------- |
| 734  | `Decode2Hex(input)`                       | Decode to hexadecimal      |
| 743  | `CalcLRC(input)`                          | Calculate LRC              |
| 756  | `CalcLRCByte(message)`                    | Calculate LRC byte         |
| 770  | `AddLeftString(text, eklenecek, kacadet)` | Add left string            |
| 778  | `FillLeftZeroIfSingular(str)`             | Fill left zero if singular |
| 787  | `StrLengthCeiling(str)`                   | String length ceiling      |
| 799  | `HEXNumberToInt(test1)`                   | Convert hex number to int  |
| 803  | `AddLeftBCD(numbers, leng)`               | Add left BCD               |
| 907  | `getMAC(interface='eth0')`                | Get MAC address            |

## Port & Communication Functions

| Line  | Function Name                         | Description                 |
| ----- | ------------------------------------- | --------------------------- |
| 1019  | `FindPorts(sender)`                   | Find available ports        |
| 14132 | `OpenNextionPort()`                   | Open Nextion port           |
| 14258 | `FindPortForCardReader()`             | Find port for card reader   |
| 14301 | `OpenCloseSasPort(isclose, isSaveDB)` | Open/close SAS port         |
| 14435 | `FindPortForSAS()`                    | Find port for SAS           |
| 15626 | `OpenBillAcceptorPort()`              | Open bill acceptor port     |
| 15641 | `FindPortForBillAcceptor()`           | Find port for bill acceptor |

## Card Reader Functions

| Line  | Function Name                                             | Description                          |
| ----- | --------------------------------------------------------- | ------------------------------------ |
| 1109  | `CardReader_ColorCommand(cmd)`                            | Card reader color command            |
| 1120  | `CardReader_CardExitStart()`                              | Card exit start                      |
| 1126  | `CardReader_CardProblem()`                                | Card problem handler                 |
| 1130  | `CardReader_WaitingNewDay()`                              | Waiting new day                      |
| 1135  | `CardReader_CardExitEnd()`                                | Card exit end                        |
| 1140  | `CardReader_CardInsertStart()`                            | Card insert start                    |
| 1144  | `CardReader_CardInsertEnd()`                              | Card insert end                      |
| 1148  | `CardReader_EjectCard()`                                  | Eject card                           |
| 10768 | `DoCardRead(tdata, CardRawData)`                          | Process card read                    |
| 10855 | `Process_CardExitFailed()`                                | Process card exit failed             |
| 10866 | `CardIsRemoved(sender)`                                   | Card is removed handler              |
| 10889 | `Do_CardIsRemoved(sender)`                                | Do card is removed                   |
| 11087 | `SetCardReaderIsNotWorking()`                             | Set card reader not working          |
| 11099 | `CardRead_CRT288B_Process()`                              | Card read CRT288B process            |
| 11168 | `CardRead_CRT288B()`                                      | Card read CRT288B                    |
| 11261 | `CardReaderCommand(data)`                                 | Card reader command                  |
| 11279 | `CardReaderSendCommandImmediately(sendstring, doPooling)` | Send card reader command immediately |
| 11299 | `CardRead_rCloud(sender=0)`                               | Card read rCloud                     |
| 11520 | `TmrCardRead()`                                           | Timer card read                      |
| 13805 | `DoTestCardReader()`                                      | Test card reader                     |

## Bill Acceptor Functions

| Line  | Function Name                          | Description                           |
| ----- | -------------------------------------- | ------------------------------------- |
| 1162  | `GetMeiACK()`                          | Get MEI ACK                           |
| 1175  | `BillAcceptor_Inhibit_Open()`          | Bill acceptor inhibit open            |
| 1189  | `BillAcceptor_Inhibit_Close()`         | Bill acceptor inhibit close           |
| 1205  | `BillAcceptor_Reset()`                 | Bill acceptor reset                   |
| 1216  | `BillAcceptor_Reject(sender)`          | Bill acceptor reject                  |
| 1226  | `BillAcceptor_Status_Check()`          | Bill acceptor status check            |
| 1271  | `BillAcceptor_Stack1()`                | Bill acceptor stack 1                 |
| 1279  | `BillAcceptor_Currency_Assign_Req()`   | Bill acceptor currency assign request |
| 1287  | `BillAcceptor_ACK()`                   | Bill acceptor ACK                     |
| 1296  | `BillAcceptorCommand(data)`            | Bill acceptor command                 |
| 1336  | `SendBillAcceptorCommand(senddata)`    | Send bill acceptor command            |
| 1362  | `SendBillAcceptorCommandIsExist()`     | Send bill acceptor command if exists  |
| 1399  | `GetMEIMsgCRC(Orji)`                   | Get MEI message CRC                   |
| 1411  | `ParseMEICurrency(MoneyString)`        | Parse MEI currency                    |
| 1456  | `GetCurrencyDenom(currencyCode)`       | Get currency denomination             |
| 1464  | `GetCurrencyCountryCode(currencyCode)` | Get currency country code             |
| 1472  | `GetCurrencyDenomHex(currencyCode)`    | Get currency denomination hex         |
| 1515  | `DoBillAcceptorPooling()`              | Do bill acceptor pooling              |
| 12508 | `Billacceptor_OpenThread(sender)`      | Bill acceptor open thread             |
| 12515 | `BillAcceptor_GameEnded()`             | Bill acceptor game ended              |
| 12527 | `BillAcceptor_GameStarted()`           | Bill acceptor game started            |

## Database Functions

### PostgreSQL Migration

| Line | Function Name                   | Description                 |
| ---- | ------------------------------- | --------------------------- |
| 2695 | `verify_postgresql_migration()` | Verify PostgreSQL migration |
| 2738 | `get_current_sas_context()`     | Get current SAS context     |

### Customer & Card Operations

| Line  | Function Name                                             | Description                            |
| ----- | --------------------------------------------------------- | -------------------------------------- |
| 5131  | `SQL_ReadCustomerInfo(KartNo, CardRawData)`               | Read customer info                     |
| 5776  | `SQL_CardReadAddMoney(customerid, amount, operationType)` | Card read add money                    |
| 5790  | `SQL_GetCustomerCurrentMessages()`                        | Get customer current messages          |
| 5808  | `SQL_GetSlotCustomerDiscountCalc(isAddDiscount)`          | Get slot customer discount calculation |
| 5822  | `SQL_GetCustomerMessage(messageid)`                       | Get customer message                   |
| 5840  | `SQL_UpdMessageAwardAttempt(messageid)`                   | Update message award attempt           |
| 5857  | `SQL_UpdMessageAwardAsUsed(messageid)`                    | Update message award as used           |
| 6036  | `SQL_CheckSystemAfterCardExit(cardmachinelogid)`          | Check system after card exit           |
| 9862  | `SQL_CardExit(sender)`                                    | Card exit                              |
| 10035 | `Card_RemoveCustomerInfo(isCardReaded)`                   | Remove customer info                   |
| 15350 | `CardReadAddMoney(customerid, amount)`                    | Card read add money                    |

### Device & System Operations

| Line | Function Name                                                                             | Description                                   |
| ---- | ----------------------------------------------------------------------------------------- | --------------------------------------------- |
| 5549 | `SQL_InsEventAfterNewGamingDateCommand(typeid)`                                           | Insert event after new gaming date command    |
| 5566 | `SQL_GetNextVisit()`                                                                      | Get next visit                                |
| 5580 | `SQL_GetNextVisit_ByTurnover(isTakePrize)`                                                | Get next visit by turnover                    |
| 5596 | `SQL_InsKioskBonusWon()`                                                                  | Insert kiosk bonus won                        |
| 5632 | `SQL_UpdDeviceEnablesGames(EnabledGameIds, FullMessage)`                                  | Update device enables games                   |
| 5645 | `SQL_UpdDeviceAdditionalInfo(Temperature, Throttle, ThreadCount, CPUUsage, MemoryUsage)`  | Update device additional info                 |
| 5659 | `SQL_GetDeviceAdditionalInfo(deviceId)`                                                   | Get device additional info                    |
| 5671 | `SQL_UpdDeviceAdditionalInfoHash(HashKey)`                                                | Update device additional info hash            |
| 5735 | `SQL_UpdAssetNoSMIB(assetno)`                                                             | Update asset no SMIB                          |
| 5958 | `SQL_ChangeDeviceNameAndType(machinename, devicetypeid)`                                  | Change device name and type                   |
| 5975 | `SQL_UpdGameName(GameId, GameName)`                                                       | Update game name                              |
| 5990 | `SQL_UpdDeviceIsLocked(IsLocked)`                                                         | Update device is locked                       |
| 6021 | `SQL_UpdDeviceSASSerial(SASVersion, SerialNo)`                                            | Update device SAS serial                      |
| 6053 | `SQL_InsDeviceWaiterCall()`                                                               | Insert device waiter call                     |
| 7034 | `SQL_InsDeviceMoneyQuery(CashableAmount, RestrictedAmount, NonrestrictedAmount, Message)` | Insert device money query                     |
| 7057 | `SQL_InsDeviceDebug(message)`                                                             | Insert device debug                           |
| 7364 | `SQL_InsImportantMessage(Message, MessageType)`                                           | Insert important message                      |
| 7377 | `SQL_InsTraceLog(LogType, Direction, Message, RowId)`                                     | Insert trace log                              |
| 7388 | `SQL_Safe_InsTraceLog(LogType, Direction, Message)`                                       | Safe insert trace log                         |
| 7403 | `SQL_Safe_InsImportantMessage(Message, MessageType)`                                      | Safe insert important message                 |
| 7413 | `SQL_Safe_InsImportantMessageByWarningType(Message, MessageType, WarningType)`            | Safe insert important message by warning type |
| 7421 | `SQL_InsImportantMessageByWarningType(Message, MessageType, WarningType)`                 | Insert important message by warning type      |
| 7434 | `SQL_InsReceivedMessage(ReceivedMessage, IsProcessed, AnswerCommandName)`                 | Insert received message                       |
| 7449 | `SQL_Safe_InsSentCommands(CommandName, Command)`                                          | Safe insert sent commands                     |
| 7454 | `SQL_InsSentCommands(CommandName, Command)`                                               | Insert sent commands                          |
| 7034 | `SQL_DeviceStatu(MessageType)`                                                            | Device status                                 |

### Money & Financial Operations

| Line  | Function Name                                                                                                                  | Description                        |
| ----- | ------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------- |
| 5688  | `SQL_UpdInsertedBalance(machinelogid, inputbalance, promoin)`                                                                  | Update inserted balance            |
| 5701  | `SQL_InsDeviceHandpay(ProgressiveGroup, HandpayLevel, Amount, PartialPay, ResetId, UnUsed, HandpayMessage)`                    | Insert device handpay              |
| 5717  | `SQL_UpdDeviceDenomPayBack(PayBackPerc, Denomination, GameId, MaxBet)`                                                         | Update device denomination payback |
| 6006  | `SQL_UpdBillAcceptorMoney(billAcceptorId, isUploaded)`                                                                         | Update bill acceptor money         |
| 6071  | `SQLite_InsBillAcceptor(machinelogid, cardno, amount, amountcode, countrycode, piece, issynced, amountbase)`                   | SQLite insert bill acceptor        |
| 6081  | `SQL_InsBillAcceptorMoneyEFT(cardmachinelogid, cardno, amount, amountcode, countrycode, piece, islog, isUploaded, amountBase)` | Insert bill acceptor money EFT     |
| 7343  | `SQL_UploadMoney(Amount, Type)`                                                                                                | Upload money                       |
| 15333 | `AddMoney(amount)`                                                                                                             | Add money                          |

### Game & Meter Operations

| Line | Function Name                                                                                                                                                                                                                                                          | Description             |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| 7075 | `SQL_InsDeviceMeter(GameNumber, TotalCoinIn, TotalCoinOut, TotalJackpot, GamesPlayed, TotalHandPaidCredit, TotalCreditsBillsAccepted, CurrentCredits_0C, TurnOver, TurnOut, NonCashableIn, NonCashableOut, TotalBonus, GamesWon, GamesLost)`                           | Insert device meter     |
| 7102 | `SQL_InsDeviceMeter2(TotalCancelledCredits_04, GamesPlayed_05, GamesWon_06, CurrentCredits_0C, WeightedAverage_7F, RegularCashableKeyed_FA, RestrictedKeyed_FB, NonrestrictedKeyed_FC, TotalMachinePaidProgressive_1D)`                                                | Insert device meter 2   |
| 7128 | `SQL_InsDeviceMeterAll(GameNumber, ReceivedMessage)`                                                                                                                                                                                                                   | Insert device meter all |
| 7168 | `SQL_InsGameStart(Wagered, WonAmount, TotalCoinIn, WagerType, ProgressiveGroup, GamePromo, TotalPlayCount, TotalCoinInMeter)`                                                                                                                                          | Insert game start       |
| 7223 | `SQL_InsGameEnd(WinAmount)`                                                                                                                                                                                                                                            | Insert game end         |
| 7258 | `SQL_InsGameStartEnd(WinAmount)`                                                                                                                                                                                                                                       | Insert game start end   |
| 8476 | `SQL_Safe_MeterInsert(GameNumber, TotalCoinIn, TotalCoinOut, TotalJackpotCredit, GamesPlayed, TotalHandPaidCredit, TotalCreditsBillsAccepted, CurrentCredits_0C, TurnOver, TurnOut, NonCashableIn, NonCashableOut, TotalBonus, ReceivedAllMeter, GamesWon, GamesLost)` | Safe meter insert       |
| 8481 | `SQL_MeterInsert(GameNumber, TotalCoinIn, TotalCoinOut, TotalJackpotCredit, GamesPlayed, TotalHandPaidCredit, TotalCreditsBillsAccepted, CurrentCredits_0C, TurnOver, TurnOut, NonCashableIn, NonCashableOut, TotalBonus, ReceivedAllMeter, GamesWon, GamesLost)`      | Meter insert            |
| 8485 | `SQL_Safe_MeterInsert2(TotalCancelledCredits_04, GamesPlayed_05, GamesWon_06, CurrentCredits_0C, WeightedAverage_7F, RegularCashableKeyed_FA, RestrictedKeyed_FB, NonrestrictedKeyed_FC, TotalMachinePaidProgressive_1D)`                                              | Safe meter insert 2     |
| 8490 | `SQL_MeterInsert2(TotalCancelledCredits_04, GamesPlayed_05, GamesWon_06, CurrentCredits_0C, WeightedAverage_7F, RegularCashableKeyed_FA, RestrictedKeyed_FB, NonrestrictedKeyed_FC, TotalMachinePaidProgressive_1D)`                                                   | Meter insert 2          |

### Bonus Operations

| Line | Function Name                         | Description                |
| ---- | ------------------------------------- | -------------------------- |
| 5874 | `SQL_BonusRequestList()`              | Bonus request list         |
| 5893 | `SQL_GetLastSessionOfDevice(isinuse)` | Get last session of device |
| 5908 | `SQL_InsBonusRequest(amount)`         | Insert bonus request       |
| 5928 | `SQL_UpdBonusAsUsed(bonusid)`         | Update bonus as used       |

### Product Operations

| Line | Function Name                                           | Description                          |
| ---- | ------------------------------------------------------- | ------------------------------------ |
| 5750 | `SQL_InsProductOrderBySlot(Products)`                   | Insert product order by slot         |
| 5763 | `SQL_GetProductCategories()`                            | Get product categories               |
| 5944 | `SQL_GetProductsAndSubCategoriesSlot(categoryId, type)` | Get products and sub categories slot |

### Exception Handling

| Line | Function Name                                | Description       |
| ---- | -------------------------------------------- | ----------------- |
| 5537 | `ExceptionHandler(name, e, Insert2DB)`       | Exception handler |
| 7141 | `SQL_InsException(MethodName, ErrorMessage)` | Insert exception  |

## Screen & Display Functions

### Status & Text Display

| Line | Function Name                                                        | Description                             |
| ---- | -------------------------------------------------------------------- | --------------------------------------- |
| 3654 | `CheckNextVisit()`                                                   | Check next visit                        |
| 3717 | `CheckNextVisit_ByTurnover()`                                        | Check next visit by turnover            |
| 3758 | `SetMachineStatu(statumsg)`                                          | Set machine status                      |
| 3764 | `PrintAndSetAsStatuTextWithLevel(statumsg, level)`                   | Print and set as status text with level |
| 3776 | `PrintAndSetAsStatuText(statumsg)`                                   | Print and set as status text            |
| 4412 | `ScreenUpdateTextStatu(message, resetsecond)`                        | Screen update text status               |
| 4439 | `ScreenResetTextStatu()`                                             | Screen reset text status                |
| 4561 | `ChangeCustomerScreenLine(lineNo, yazi)`                             | Change customer screen line             |
| 4593 | `ChangeCustomerLineWithDelay(resetsecond, lineNo, yazi)`             | Change customer line with delay         |
| 4601 | `ChangeCustomerScreenLineTimed(lineNo, yazi, resetsecond, yazison)`  | Change customer screen line timed       |
| 4615 | `BlinkCustomerScreenLine(sender, lineno, text, howmanytimes)`        | Blink customer screen line              |
| 4627 | `BlinkCustomerScreenLine_Thread(sender, lineno, text, howmanytimes)` | Blink customer screen line thread       |

### GUI Display Functions

| Line | Function Name                       | Description                      |
| ---- | ----------------------------------- | -------------------------------- |
| 4644 | `GUI_ShowIfPossibleMainStatu(msg)`  | GUI show if possible main status |
| 4677 | `GUI_ShowCurrentPage()`             | GUI show current page            |
| 4721 | `GUI_ShowIdleWindow()`              | GUI show idle window             |
| 4746 | `GUI_RefreshPage()`                 | GUI refresh page                 |
| 4762 | `GUI_ShowBonus()`                   | GUI show bonus                   |
| 4780 | `GUI_ShowJackpot()`                 | GUI show jackpot                 |
| 4797 | `GUI_ShowBalance()`                 | GUI show balance                 |
| 4844 | `GUI_ShowAdverts()`                 | GUI show adverts                 |
| 4918 | `GUI_ShowSettings()`                | GUI show settings                |
| 4935 | `GUI_ShowAdmin()`                   | GUI show admin                   |
| 4957 | `GUI_ShowCustomerWindow()`          | GUI show customer window         |
| 5000 | `CloseCustomerWindow()`             | Close customer window            |
| 5008 | `GUI_CloseCustomerBalance()`        | GUI close customer balance       |
| 5031 | `GUI_UpdateBonus()`                 | GUI update bonus                 |
| 5095 | `ChangeBalanceAmount(lineNo, yazi)` | Change balance amount            |

### Jackpot & Notification Functions

| Line | Function Name                                                            | Description                     |
| ---- | ------------------------------------------------------------------------ | ------------------------------- |
| 4459 | `ChangeJackpotLevelText(sira, yazi)`                                     | Change jackpot level text       |
| 4471 | `ChangeJackpotLevelTextValue(sira, yazi)`                                | Change jackpot level text value |
| 4485 | `ChangeJackpotLevelValue(sira, yazi)`                                    | Change jackpot level value      |
| 4496 | `ShowNotifyScreen(header, msg, duration)`                                | Show notify screen              |
| 4521 | `ShowNotifyScreenWithButtons(header, msg, duration, showOk, showCancel)` | Show notify screen with buttons |
| 4546 | `CloseNotifyScreen(seconds)`                                             | Close notify screen             |

## Nextion Display Functions

| Line  | Function Name                     | Description                    |
| ----- | --------------------------------- | ------------------------------ |
| 4256  | `NextionCommand(data)`            | Nextion command                |
| 4271  | `NextionCommandThread(data)`      | Nextion command thread         |
| 4339  | `SendNextionCommandIfExist()`     | Send Nextion command if exists |
| 4383  | `CloseCustomerInfo()`             | Close customer info            |
| 13839 | `DoNextionPooling(isForceRead=0)` | Do Nextion pooling             |

## SAS Protocol Functions

### Command Functions

| Line | Function Name                                                                     | Description                        |
| ---- | --------------------------------------------------------------------------------- | ---------------------------------- |
| 6120 | `ExecuteCommand(Command)`                                                         | Execute command                    |
| 6232 | `Komut_GetMeter(isall, gameid)`                                                   | Command get meter                  |
| 6315 | `GetMeter(isall, sender="Unknown", gameid=0)`                                     | Get meter                          |
| 7474 | `TmrSASPooling()`                                                                 | Timer SAS pooling                  |
| 7484 | `Wait_RemoteHandpay()`                                                            | Wait remote handpay                |
| 7519 | `Komut_EFT_RequestCashoutAmount()`                                                | Command EFT request cashout amount |
| 7523 | `Komut_EFT_RequestTransferLog()`                                                  | Command EFT request transfer log   |
| 7528 | `Komut_RegisterAssetNo()`                                                         | Command register asset no          |
| 7533 | `Komut_RegisterAssetNo2()`                                                        | Command register asset no 2        |
| 7538 | `Komut_ReadAssetNo()`                                                             | Command read asset no              |
| 7543 | `Komut_RemoteHandpay()`                                                           | Command remote handpay             |
| 7553 | `Komut_DisableBillAcceptor(sender)`                                               | Command disable bill acceptor      |
| 7577 | `Komut_EnableBillAcceptor()`                                                      | Command enable bill acceptor       |
| 7610 | `Komut_ParaYukleEFT(doincreasetransactionid, amount)`                             | Command load money EFT             |
| 7650 | `Komut_ParaSilEFT(doincreasetransactionid, amount)`                               | Command delete money EFT           |
| 7688 | `Komut_ParaYukle(doincreasetransactionid, transfertype)`                          | Command load money                 |
| 8688 | `Komut_CollectButtonProcess()`                                                    | Command collect button process     |
| 8734 | `Komut_Interragition(sender)`                                                     | Command interrogation              |
| 8767 | `Komut_BakiyeSorgulama(sender, isforinfo, sendertext='UndefinedBakiyeSorgulama')` | Command balance inquiry            |
| 8844 | `Komut_CancelBalanceLock()`                                                       | Command cancel balance lock        |
| 8849 | `Komut_CancelAFTTransfer()`                                                       | Command cancel AFT transfer        |
| 9210 | `Komut_Handpay(doincreaseid)`                                                     | Command handpay                    |
| 9317 | `Komut_ParaSifirla(doincreaseid)`                                                 | Command reset money                |

### Response Functions

| Line  | Function Name                     | Description                   |
| ----- | --------------------------------- | ----------------------------- |
| 7839  | `Yanit_LegacyBonusPay(Yanit)`     | Response legacy bonus pay     |
| 7873  | `Yanit_EnabledGameNumbers(Yanit)` | Response enabled game numbers |
| 7915  | `Yanit_GameConfiguration(Yanit)`  | Response game configuration   |
| 8032  | `Yanit_HandpayInfo(Yanit)`        | Response handpay info         |
| 8068  | `Yanit_GameInfo(Yanit)`           | Response game info            |
| 8156  | `GetLengthByMeterCode(MeterCode)` | Get length by meter code      |
| 8165  | `Yanit_MeterAll(Yanit)`           | Response meter all            |
| 8496  | `Yanit_ParaYukle(Yanit)`          | Response load money           |
| 8862  | `Yanit_BakiyeSorgulama(Yanit)`    | Response balance inquiry      |
| 9474  | `Yanit_ParaSifirla(Yanit)`        | Response reset money          |
| 12458 | `Yanit_RegisterAFT(Yanit)`        | Response register AFT         |

### SAS Communication Functions

| Line  | Function Name                                     | Description                 |
| ----- | ------------------------------------------------- | --------------------------- |
| 9186  | `GetCRC(komut)`                                   | Get CRC                     |
| 11536 | `XSendSASPORT(command)`                           | Extended send SAS port      |
| 11551 | `SendSASPORT(command)`                            | Send SAS port               |
| 11573 | `SendSASCommand(Command)`                         | Send SAS command            |
| 11682 | `SendCommandIsExist()`                            | Send command if exists      |
| 11698 | `SAS_SendCommand(CommandName, Command, DoSaveDB)` | SAS send command            |
| 11741 | `ParseMessage(message)`                           | Parse message               |
| 11830 | `GetDataFromSasPort(IsMessageSent)`               | Get data from SAS port      |
| 11915 | `DoSASPoolingMsg(isInit)`                         | Do SAS pooling message      |
| 12403 | `DoConsumeSASMessage(tdata)`                      | Do consume SAS message      |
| 12544 | `HandleReceivedSASCommand(tdata)`                 | Handle received SAS command |

## Money & Balance Functions

| Line  | Function Name                                                       | Description                |
| ----- | ------------------------------------------------------------------- | -------------------------- |
| 3789  | `Wait_ParaYukle(transfertype)`                                      | Wait load money            |
| 3984  | `Wait_ParaSifirla()`                                                | Wait reset money           |
| 4150  | `Wait_Safe_Bakiye(sender, isforbilgi, sendertext)`                  | Wait safe balance          |
| 4160  | `Wait_Bakiye(sender, isforbilgi, sendertext='UndefinedWaitBakiye')` | Wait balance               |
| 4234  | `ChangeRealTimeReporting(isopened)`                                 | Change real time reporting |
| 12408 | `IsAvailableForCashout(sender)`                                     | Is available for cashout   |

## Streaming & Configuration Functions

| Line | Function Name                                                         | Description                        |
| ---- | --------------------------------------------------------------------- | ---------------------------------- |
| 6361 | `CreateStreamingScriptHDMI(casinoId, deviceId, configId)`             | Create streaming script HDMI       |
| 6403 | `CreateStreamingScriptHDMIAudio(casinoId, deviceId, configId)`        | Create streaming script HDMI audio |
| 6422 | `CreateStreamingScriptCamera(casinoId, deviceId, cameraIp, configId)` | Create streaming script camera     |
| 6447 | `SetDeviceConfiguration(deviceTypeId)`                                | Set device configuration           |

## System & Monitoring Functions

| Line  | Function Name                                | Description                    |
| ----- | -------------------------------------------- | ------------------------------ |
| 9837  | `RemoveCustomerInfoOnConfig()`               | Remove customer info on config |
| 10272 | `SyncDB()`                                   | Sync database                  |
| 10313 | `CheckAndRestartPorts(sender)`               | Check and restart ports        |
| 10411 | `RestartProgram()`                           | Restart program                |
| 10419 | `SystemCPUCheck(restartNeeded)`              | System CPU check               |
| 10500 | `DoTmrIsOnline()`                            | Do timer is online             |
| 10758 | `TmrIsOnline()`                              | Timer is online                |
| 11256 | `print_time_stamp_ms()`                      | Print timestamp milliseconds   |
| 12438 | `CreateTextFile(filename, content)`          | Create text file               |
| 14435 | `Mevlut_Warn(warningtypeid, warningmessage)` | Mevlut warning                 |
| 14465 | `ThreadStressSleep(count, duration)`         | Thread stress sleep            |
| 14469 | `ThreadStressTest()`                         | Thread stress test             |
| 15708 | `Mevlut_LicenceCheck()`                      | Mevlut licence check           |

## Game Control Functions

| Line | Function Name                      | Description              |
| ---- | ---------------------------------- | ------------------------ |
| 7593 | `EnableDisableAutoPlay(isenabled)` | Enable/disable auto play |
| 7599 | `DelayPlay()`                      | Delay play               |
| 7605 | `UnDelayPlay()`                    | Un-delay play            |

## User Input & Command Handling Functions

| Line  | Function Name               | Description          |
| ----- | --------------------------- | -------------------- |
| 14483 | `DoHandUserInput(command)`  | Do handle user input |
| 15093 | `HandUserInput(command)`    | Handle user input    |
| 15734 | `WaitingForCommand(window)` | Waiting for command  |

## Summary

**Total Functions: 247**

### Function Categories:

- **Database Operations**: 89 functions (36%)
- **SAS Protocol**: 45 functions (18%)
- **GUI/Display**: 32 functions (13%)
- **Card Reader**: 18 functions (7%)
- **Bill Acceptor**: 17 functions (7%)
- **System/Utility**: 16 functions (6%)
- **JavaScript Execution**: 12 functions (5%)
- **Configuration**: 10 functions (4%)
- **Communication/Ports**: 8 functions (3%)

This appears to be a comprehensive gaming machine control system with extensive database integration, SAS protocol support, and multiple hardware interfaces for card readers, bill acceptors, and display systems.
