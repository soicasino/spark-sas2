Executed SQL Operations

1. Stored Procedure Calls (55 different procedures):
   - Bill Acceptor Operations:
   - tsp_CheckBillacceptorIn - Validates bill acceptance
   - tsp_InsBillAcceptorMoney - Records bill acceptor transactions
   - tsp_UpdBillAcceptorMoney - Updates bill acceptor status
   - Card Operations:
   - tsp_CardRead - Full card reading
   - tsp_CardReadPartial - Partial card reading
   - tsp_CardReadAddMoney - Add money to card
   - tsp_CardExit - Handle card removal
   - Game Operations:
   - tsp_InsGameStart - Record game start
   - tsp_InsGameEnd - Record game end
   - tsp_InsGameStartEnd - Combined game start/end
   - tsp_GetDeviceGameInfo - Get game information
   - Device Status & Monitoring:
   - tsp_DeviceStatu - Device status updates
   - tsp_UpdDeviceEnablesGames - Update enabled games
   - tsp_UpdDeviceAdditionalInfo - Update device info
   - tsp_GetDeviceAdditionalInfo - Get device info
   - tsp_UpdDeviceIsLocked - Lock/unlock device
   - Customer & Bonus Operations:
   - tsp_GetCustomerAdditional - Get customer details
   - tsp_GetCustomerCurrentMessages - Get customer messages
   - tsp_BonusRequestList - Get bonus list
   - tsp_InsBonusRequest - Create bonus request
   - tsp_UpdBonusAsUsed - Mark bonus as used
   - Financial Operations:
   - tsp_UpdInsertedBalance - Update inserted balance
   - tsp_GetBalanceInfoOnGM - Get balance info
   - tsp_InsMoneyUpload - Record money uploads
   - Logging & Debugging:
   - tsp_InsImportantMessage - Log important messages
   - tsp_InsException - Log exceptions
   - tsp_InsDeviceDebug - Debug logging
   - tsp_InsTraceLog - Trace logging
   - tsp_InsReceivedMessage - Log received messages
   - tsp_InsSentCommands - Log sent commands
2. Direct SQL Statements:
   - SQLite Operations (local database):
   - Apply to raspberryPyt...
   - CREATE TABLE IF NOT EXISTS billacceptor (...)
   - INSERT INTO billacceptor(machinelogid,cardno,amount,amountcode,countrycode,piece,issynced,amountbase) VALUES (...)
   - SELECT \* FROM billacceptor
   - DELETE FROM billacceptor WHERE billacceptorid=...
3. Connection Patterns:

   - Standard Connection:
   - Apply to raspberryPyt...
   - conn = pymssql.connect(host=G_DB_Host, user=G_DB_User, password=G_DB_Password, database=G_DB_Database,tds_version='7.2')
   - conn.autocommit(True)
   - cursor = conn.cursor(as_dict=True)
   - Connection with Timeout:
   - Apply to raspberryPyt...
   - conn = pymssql.connect(host=G_DB_Host, user=G_DB_User, password=G_DB_Password, database=G_DB_Database, login_timeout=10, timeout=0.01, tds_version='7.2')

4. Main Function Categories:

   - Gaming Machine Operations - Card reading, game tracking, balance management
   - Bill Acceptor Integration - Currency validation and processing
   - Customer Management - Bonus systems, messaging, loyalty programs
   - Device Monitoring - Status reporting, error logging, performance metrics
   - Financial Transactions - Money transfers, balance updates, audit trails
   - The system appears to be a comprehensive casino gaming machine management system with extensive database logging and real-time transaction processing capabilities.
