# TSP DeviceStatu Function Documentation

## Overview

The `tcasino.tsp_devicestatu` function is a comprehensive PostgreSQL stored procedure that handles device status management and communication for a casino gaming system. It processes device heartbeats, manages device registration, handles commands, and returns configuration or dynamic data based on the message type.

## Function Signature

```sql
CREATE OR REPLACE FUNCTION tcasino.tsp_devicestatu(
    p_mac_address text,
    p_message_type integer,
    p_ip_address text,
    p_version_id bigint DEFAULT 0,
    p_is_sas_port bigint DEFAULT 0,
    p_is_card_reader bigint DEFAULT 0,
    p_sas_port text DEFAULT '',
    p_card_reader_port text DEFAULT '',
    p_statu_text text DEFAULT '',
    p_is_locked integer DEFAULT 0,
    p_device_id bigint DEFAULT 0,
    p_play_count bigint DEFAULT 0,
    p_total_bet numeric DEFAULT 0,
    p_machine_log_id bigint DEFAULT 0,
    p_active_screen text DEFAULT '',
    p_online_count bigint DEFAULT 0,
    p_is_sas_link boolean DEFAULT false,
    p_customer_id bigint DEFAULT 0,
    p_asset_no bigint DEFAULT 0,
    p_is_bill_acceptor bigint DEFAULT 0,
    p_wagered numeric DEFAULT 0,
    p_current_balance numeric DEFAULT 0,
    p_current_promo numeric DEFAULT 0,
    p_win_amount numeric DEFAULT 0,
    p_bet_amount numeric DEFAULT 0,
    p_total_win numeric DEFAULT 0
)
```

## Parameters

### Required Parameters

- **p_mac_address** (text): Device MAC address for identification
- **p_message_type** (integer): Type of message being processed
- **p_ip_address** (text): Device IP address

### Message Types

- **0**: Device startup/initialization - Returns full device configuration
- **1**: Device login - Updates login statistics and device info
- **2**: Device operation - Updates operation counters
- **3**: Device heartbeat/online status - Updates online status and gaming data

### Optional Parameters

- **p_version_id**: Software version identifier
- **p_is_sas_port**: SAS (Slot Accounting System) port availability flag
- **p_is_card_reader**: Card reader availability flag
- **p_asset_no**: Physical asset number for device identification
- **p_is_locked**: Device lock status
- **p_play_count**: Number of games played
- **p_total_bet**: Total amount bet
- **p_machine_log_id**: Reference to machine log entry
- **p_active_screen**: Current active screen on device
- **p_online_count**: Online message counter
- **p_is_sas_link**: SAS link status
- **p_is_bill_acceptor**: Bill acceptor availability
- Gaming amounts: p_wagered, p_current_balance, p_current_promo, p_win_amount, p_bet_amount, p_total_win

## Return Structure

Returns a table with 50 columns containing device configuration and dynamic data:

### Core Device Information

- **IsNewRecord**: Flag indicating if this is a newly created device
- **DeviceId**: Unique device identifier
- **MachineName**: Display name for the device
- **AssetNo**: Physical asset number

### Device Configuration

- **DeviceTypeId**, **DeviceTypeGroupId**: Device type classifications
- **ScreenTypeId**: Screen configuration type
- **BillAcceptorTypeId**: Bill acceptor hardware type
- **TicketPrinterTypeId**: Ticket printer hardware type
- **MachineType**: Machine category

### Gaming Configuration

- **IsBonusGives**: Bonus eligibility flag
- **CashInLimit**: Maximum cash input limit
- **IsPartialTransfer**: Partial transfer capability
- **IsRecordAllSAS**: SAS recording configuration
- **JackpotFactor**: Jackpot calculation multiplier
- **PayBackPerc**: Payout percentage
- **DefBetFactor**: Default bet multiplier

### Casino Settings

- **CasinoName**: Casino name
- **CasinoId**: Casino identifier
- **CurrencyCode**: Currency code (e.g., USD)
- **CurrencyId**, **MachineCurrencyId**: Currency identifiers
- **CurrencyRate**: Exchange rate

### Operational Flags

- **IsCanPlayWithoutCard**: Card-less play permission
- **IsCashless**: Cashless operation mode
- **IsBonusCashable**: Bonus cashout permission
- **IsPromoAccepts**: Promotional acceptance
- **IsAutoNextVisit**: Auto-advance to next visit

### Technical Configuration

- **ProtocolType**: Communication protocol type
- **SASVersion**: SAS protocol version
- **ScreenRotate**: Screen rotation setting
- **CalcBetByTotalCoinIn**: Bet calculation method
- **GameStartEndNotifications**: Game event notification setting

### Timeout Settings

- **NoActivityTimeOutForBillAcceptor**: Bill acceptor timeout
- **NoActivityTimeForCashoutMoney**: Cashout timeout
- **NoActivityTimeForCashoutSeconds**: Cashout seconds timeout
- **MinsToRebootNoNetwork**: Network reboot timeout

### Dynamic Data Fields

- **RowType**: Type of dynamic data row ('jackpotinfo', 'cmd', 'oldgamingdate', 'prize')
- **RowNo**: Row sequence number
- **Command**: Device command to execute
- **TextInfo**: Additional text information
- **TextValue**: Numeric value associated with the row

## Main Logic Flow

### 1. IP Address Tracking

```sql
-- Updates T_DeviceIP table with current IP and timestamp
IF NOT EXISTS (SELECT 1 FROM tcasino.T_DeviceIP WHERE AssetNo = p_asset_no AND IPAddress = p_ip_address)
```

### 2. Device Identification

The function uses a hierarchical approach to identify devices:

1. **By Asset Number**: Primary lookup using asset number
2. **By MAC + Asset**: Secondary lookup combining MAC address and asset number
3. **By MAC Only**: Fallback lookup using MAC address only

### 3. Device Registration

For new devices (when device_id = 0):

- Creates new device record in T_Device table
- Assigns new DeviceId
- Sets initial configuration values

### 4. Device Updates by Message Type

- **Type 0 (Startup)**: Resets online count, updates last login
- **Type 1 (Login)**: Increments login count, updates device capabilities
- **Type 2 (Operation)**: Increments operation count
- **Type 3 (Heartbeat)**: Updates online status, gaming statistics

### 5. Return Data Logic

- **Message Type 0**: Returns complete device configuration
- **Message Type > 0**: Returns dynamic data including:
  - Jackpot information (when active_screen = 'GUI_ShowJackpot')
  - Pending device commands
  - Gaming date notifications
  - Prize notifications

## Key Database Tables

### Primary Tables

- **T_Device**: Main device registry
- **T_DeviceIP**: IP address tracking
- **T_DeviceStarts**: Device startup log
- **T_DeviceCommands**: Pending commands for devices
- **T_CardMachineLogs**: Gaming session logs

### Reference Tables

- **T_CasinoSettings**: Global casino configuration
- **T_Currency**: Currency definitions
- **T_WagerGroups**: Betting group configurations
- **T_Card**: Card definitions (for admin cards)
- **T_JackpotLevels**: Jackpot level definitions
- **T_PrizeWon**: Prize notifications

## Error Handling

The function includes comprehensive error handling:

- Exception blocks around critical operations
- RAISE NOTICE statements for debugging
- Graceful fallbacks for missing data
- COALESCE functions to provide default values

## Performance Considerations

- Uses indexed lookups on DeviceId, AssetNo, and MAC address
- Limits command processing to recent entries (5-minute window)
- Batch updates for efficiency
- Conditional processing based on message type

## Security Features

- Input validation through parameter typing
- Controlled access through schema permissions
- Audit trail through timestamp tracking
- Command expiration to prevent replay attacks

## Usage Examples

### Device Startup (Message Type 0)

```sql
SELECT * FROM tcasino.tsp_devicestatu(
    'AA:BB:CC:DD:EE:FF',  -- MAC address
    0,                     -- Message type (startup)
    '192.168.1.100',      -- IP address
    12345,                 -- Version ID
    1,                     -- Has SAS port
    1,                     -- Has card reader
    'COM1',               -- SAS port
    'COM2',               -- Card reader port
    'Online',             -- Status text
    0,                     -- Not locked
    0,                     -- Device ID (0 for auto-detect)
    0,                     -- Play count
    0,                     -- Total bet
    0,                     -- Machine log ID
    '',                   -- Active screen
    0,                     -- Online count
    true,                 -- SAS link active
    0,                     -- Customer ID
    1001,                 -- Asset number
    1                     -- Has bill acceptor
);
```

### Device Heartbeat (Message Type 3)

```sql
SELECT * FROM tcasino.tsp_devicestatu(
    'AA:BB:CC:DD:EE:FF',  -- MAC address
    3,                     -- Message type (heartbeat)
    '192.168.1.100',      -- IP address
    12345,                 -- Version ID
    1,                     -- Has SAS port
    1,                     -- Has card reader
    'COM1',               -- SAS port
    'COM2',               -- Card reader port
    'Playing',            -- Status text
    0,                     -- Not locked
    123,                   -- Device ID
    50,                    -- Play count
    1250.00,              -- Total bet
    789,                   -- Machine log ID
    'GUI_Game',           -- Active screen
    1500,                 -- Online count
    true,                 -- SAS link active
    456,                   -- Customer ID
    1001,                 -- Asset number
    1,                     -- Has bill acceptor
    25.00,                -- Wagered
    75.50,                -- Current balance
    10.00,                -- Current promo
    15.00,                -- Win amount
    5.00,                 -- Bet amount
    200.00                -- Total win
);
```

## Maintenance Notes

- Monitor T_DeviceIP table growth for cleanup opportunities
- Review command timeout settings based on network conditions
- Regularly analyze device startup patterns for optimization
- Consider archiving old T_DeviceStarts records
- Monitor function performance with high device counts
