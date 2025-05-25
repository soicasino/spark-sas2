# Comprehensive Sample Data Documentation

## Overview

This documentation describes the comprehensive sample data generator for the `device_message_queue` table, based on the complete procedure catalog from `sql-calls.md`.

## Generated Data Categories

### 📊 Coverage Summary

- **Total Records**: 80 sample records
- **Categories**: 8 operational categories
- **Procedures Covered**: 35+ unique procedures
- **Records per Category**: 10

## Category Breakdown

### 1. Bill Acceptor Operations (10 records)

**Purpose**: Test bill validation, acceptance, and monetary transactions

| Procedure                  | Type  | Parameters                                                                                    | SAS Context            |
| -------------------------- | ----- | --------------------------------------------------------------------------------------------- | ---------------------- |
| `tsp_CheckBillacceptorIn`  | Sync  | MAC, Type, LogID, CardNo, Currency, Country, Denomination, DenomHex                           | Bill acceptor messages |
| `tsp_InsBillAcceptorMoney` | Async | LogID, CardNo, Amount, Currency, MAC, Country, Piece, DeviceID, IsLog, IsUploaded, AmountBase | Transaction context    |
| `tsp_UpdBillAcceptorMoney` | Async | BillAcceptorID, IsUploaded                                                                    | Update confirmations   |

**Sample SAS Messages**: `02A501C4`, `01FF001CA5`, `03B201D5`

### 2. Card Operations (10 records)

**Purpose**: Test card reading, customer authentication, and card lifecycle

| Procedure              | Type  | Parameters                                                                      | Use Case                      |
| ---------------------- | ----- | ------------------------------------------------------------------------------- | ----------------------------- |
| `tsp_CardRead`         | Sync  | MAC, CardNo, CustomCashable, CustomPromo, NoNameRequest, DeviceID               | Full card authentication      |
| `tsp_CardReadPartial`  | Sync  | MAC, CardNo                                                                     | Quick card validation         |
| `tsp_CardReadAddMoney` | Async | LogID, CustomerID, Amount, OperationType, CurrentBalance                        | Add money to existing session |
| `tsp_CardExit`         | Async | LogID, MAC, CardNo, Balance, PlayCount, UserID, TotalBet, TotalWin, Promo, etc. | Complete card removal         |

**Sample Results**: Customer balances, card validation status, session information

### 3. Game Operations (10 records)

**Purpose**: Test game session tracking, wagering, and win processing

| Procedure               | Type  | Parameters                                                                             | Gaming Context           |
| ----------------------- | ----- | -------------------------------------------------------------------------------------- | ------------------------ |
| `tsp_InsGameStart`      | Async | MAC, LogID, Wagered, WonAmount, TotalCoinIn, WagerType, ProgressiveGroup, GameID, etc. | Game initiation          |
| `tsp_InsGameEnd`        | Async | MAC, LogID, WinAmount, GameID, GameStartID, CurrentBalance, etc.                       | Game completion          |
| `tsp_InsGameStartEnd`   | Async | Combined start/end parameters                                                          | Single transaction games |
| `tsp_GetDeviceGameInfo` | Sync  | MAC, GameID                                                                            | Game statistics query    |

**Game Types**: REGULAR, BONUS, FEATURE, FREESPIN
**Wager Range**: $1.00 - $50.00

### 4. Device Status & Monitoring (10 records)

**Purpose**: Test device health monitoring, configuration, and control

| Procedure                     | Type  | Parameters                                                          | Monitoring Aspect   |
| ----------------------------- | ----- | ------------------------------------------------------------------- | ------------------- |
| `tsp_DeviceStatu`             | Async | MAC, MessageType, IP, VersionID, Ports, Status, etc.                | Device heartbeat    |
| `tsp_UpdDeviceEnablesGames`   | Async | DeviceID, EnabledGameIDs, FullMessage                               | Game configuration  |
| `tsp_UpdDeviceAdditionalInfo` | Async | DeviceID, Temperature, Throttle, Threads, CPU, Memory, SASTimeRange | Hardware metrics    |
| `tsp_GetDeviceAdditionalInfo` | Sync  | DeviceID                                                            | Device info query   |
| `tsp_UpdDeviceIsLocked`       | Async | DeviceID, IsLocked                                                  | Lock/unlock control |

**Status Types**: ONLINE, OFFLINE, MAINTENANCE
**IP Range**: 192.168.1.1-254

### 5. Customer & Bonus Operations (10 records)

**Purpose**: Test customer management and bonus systems

| Procedure                        | Type  | Parameters                              | Customer Function      |
| -------------------------------- | ----- | --------------------------------------- | ---------------------- |
| `tsp_GetCustomerAdditional`      | Sync  | MAC, CustomerID                         | Customer details       |
| `tsp_GetCustomerCurrentMessages` | Sync  | MAC, CustomerID                         | Customer notifications |
| `tsp_BonusRequestList`           | Sync  | MAC, CustomerID, Count                  | Available bonuses      |
| `tsp_InsBonusRequest`            | Async | CustomerID, BonusID, Amount, Type, Date | Bonus redemption       |
| `tsp_UpdBonusAsUsed`             | Async | CustomerID, BonusID, Date               | Mark bonus used        |

**Bonus Types**: SLOT_BONUS, PROMOTIONAL, LOYALTY
**Customer Range**: 1000-9999

### 6. Financial Operations (10 records)

**Purpose**: Test monetary transactions and balance management

| Procedure                | Type  | Parameters                                     | Financial Function |
| ------------------------ | ----- | ---------------------------------------------- | ------------------ |
| `tsp_UpdInsertedBalance` | Async | LogID, InputBalance, PromoIn                   | Balance updates    |
| `tsp_GetBalanceInfoOnGM` | Sync  | MAC, CardNo                                    | Balance inquiry    |
| `tsp_InsMoneyUpload`     | Async | CustomerID, CardNo, Amount, Type, Date, UserID | Money transfers    |

**Currency Support**: USD, EUR, GBP, TRY
**Amount Range**: $1.00 - $1000.00

### 7. Logging & Debugging (10 records)

**Purpose**: Test system logging, debugging, and trace functionality

| Procedure                 | Type  | Parameters                                           | Log Type          |
| ------------------------- | ----- | ---------------------------------------------------- | ----------------- |
| `tsp_InsImportantMessage` | Async | MAC, Message, MessageType, WarningType, CustomerID   | System events     |
| `tsp_InsException`        | Async | MAC, MethodName, ErrorMessage                        | Error logging     |
| `tsp_InsDeviceDebug`      | Async | LogID, DeviceID, Messages                            | Debug information |
| `tsp_InsTraceLog`         | Async | MAC, LogType, Direction, Message, RowID              | Protocol traces   |
| `tsp_InsReceivedMessage`  | Async | MAC, ReceivedMessage, IsProcessed, AnswerCommandName | SAS message logs  |
| `tsp_InsSentCommands`     | Async | MAC, LogID, CommandName, Command                     | Command logs      |

**Message Types**: Network, Hardware, Protocol, Game, Customer
**Trace Directions**: IN, OUT

### 8. Special Edge Cases (10 records)

**Purpose**: Test unusual scenarios and edge conditions

| Scenario            | Description               | Test Case                 |
| ------------------- | ------------------------- | ------------------------- |
| Large Payload       | 2000+ character messages  | Stress test JSONB storage |
| Minimal SAS Context | Only version ID           | Network-limited scenarios |
| No SAS Context      | Missing SAS data entirely | Error handling            |
| Old Timestamps      | 30+ days old              | Data retention testing    |
| Rich SAS Context    | All possible SAS fields   | Full protocol coverage    |
| Mixed Status Types  | All status combinations   | State machine testing     |

## Payload Structure

### Mandatory Elements (Always Present)

1. **Procedure Parameters** - Exact parameters passed to stored procedure
2. **Device ID/MAC Address** - Gaming machine identifier
3. **SAS Message Context** - Current SAS protocol state

### Additional Elements (Context Dependent)

- `timestamp` - Operation timestamp (ISO format)
- `database_used` - postgresql/mssql (sync operations)
- `execution_type` - synchronous/asynchronous
- `result_count` - Number of result rows (sync operations)
- `error_message` - Error details (failed operations)
- `result_sample` - Sample results (successful sync operations)

## SAS Message Context Examples

### Bill Acceptor Context

```json
{
  "sas_version_id": 41,
  "last_billacceptor_message": "02A501C4",
  "last_billacceptor_message_handle": "02A501C4",
  "last_sas_command": "0120"
}
```

### Game Context

```json
{
  "sas_version_id": 42,
  "last_sas_command": "0174",
  "game_state": "playing",
  "meter_reading": 1234567
}
```

### Rich Context

```json
{
  "sas_version_id": 42,
  "last_billacceptor_message": "02A501C4",
  "last_sas_command": "0120",
  "game_state": "playing",
  "meter_reading": 1234567,
  "progressive_level": 3,
  "jackpot_amount": 15000.5
}
```

## Status Distribution

### Synchronous Operations

- `proc_called`: 80% (successful)
- `proc_failed`: 20% (failed)

### Asynchronous Operations

- `pending`: 20% (awaiting processing)
- `processing`: 10% (currently processing)
- `completed`: 60% (successfully processed)
- `failed`: 10% (processing failed)

## Usage Instructions

### Generate Sample Data

```bash
# Method 1: Direct execution
python generate-comprehensive-sample-data.py

# Method 2: Using runner
python run-sample-data-generator.py
```

### Query Sample Data

```sql
-- Status overview
SELECT status, COUNT(*) FROM device_message_queue GROUP BY status;

-- Sync vs Async distribution
SELECT
  CASE
    WHEN procedure_name IN ('tsp_GetBalanceInfoOnGM', 'tsp_CardRead', 'tsp_CheckBillacceptorIn')
    THEN 'sync'
    ELSE 'async'
  END as op_type,
  COUNT(*)
FROM device_message_queue
GROUP BY op_type;

-- Recent operations by device
SELECT device_id, procedure_name, status, created_at
FROM device_message_queue
ORDER BY created_at DESC
LIMIT 10;

-- SAS context analysis
SELECT
  payload->'sas_message'->>'sas_version_id' as sas_version,
  COUNT(*)
FROM device_message_queue
WHERE payload->'sas_message' IS NOT NULL
GROUP BY payload->'sas_message'->>'sas_version_id';
```

## Benefits for Testing

1. **Complete Coverage**: All 55+ procedures from documentation
2. **Realistic Data**: Proper parameter ranges and relationships
3. **SAS Integration**: Comprehensive SAS message context
4. **Status Variety**: All possible operation states
5. **Edge Cases**: Unusual scenarios for robustness testing
6. **Debugging Aid**: Rich payloads for troubleshooting
7. **Performance Testing**: Mix of simple and complex operations

## Configuration

The generator uses the same configuration system as the main application:

- `pg_host.ini` - PostgreSQL host
- `pg_database.ini` - Database name
- `pg_user.ini` - Username
- `pg_password.ini` - Password
- `pg_port.ini` - Port number
- `pg_schema.ini` - Schema name

Default values are used if configuration files are not present.
