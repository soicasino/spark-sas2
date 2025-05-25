# SAS Message Payload Examples

This document shows examples of message payloads that include SAS message information for better debugging and audit trails.

## Mandatory Payload Elements

Every payload MUST include these three essential elements:

1. **SAS Message Information**: Current SAS protocol state and message context
2. **Procedure Parameters**: All parameters passed to the database procedure
3. **Device ID/MAC Address**: Unique identifier of the gaming machine

## Synchronous Operation Example (proc_called)

```json
{
  "procedure_name": "tsp_CheckBillacceptorIn",
  "parameters": [
    "00:11:22:33:44:55", // Device MAC
    1, // Bill acceptor type ID
    12345, // Card machine log ID
    "1234567890", // Card number
    "USD", // Bank note code
    "US", // Country code
    100, // Denomination
    "64" // Denomination hex
  ],
  "device_id": "00:11:22:33:44:55",
  "timestamp": "2024-01-15T10:30:15.123Z",
  "database_used": "postgresql",
  "execution_type": "synchronous",
  "result_count": 1,
  "error_message": null,
  "sas_message": {
    "last_billacceptor_message": "02A501C4",
    "last_billacceptor_message_handle": "02A501C4",
    "sas_version_id": 41
  },
  "result_sample": [
    {
      "Result": 1,
      "ErrorMessage": "Bill accepted successfully",
      "CreditAmount": 100.0
    }
  ]
}
```

## Asynchronous Operation Example (pending)

```json
{
  "procedure_name": "tsp_InsImportantMessage",
  "parameters": [
    "00:11:22:33:44:55", // Device MAC
    "Game started", // Message
    100, // Message type
    0, // Warning type
    12345 // Customer ID
  ],
  "device_id": "00:11:22:33:44:55",
  "timestamp": "2024-01-15T10:30:15.123Z",
  "sas_message": {
    "last_sas_command": "0120",
    "sas_version_id": 41
  }
}
```

## Failed Operation Example (proc_failed)

```json
{
  "procedure_name": "tsp_GetBalanceInfoOnGM",
  "parameters": [
    "00:11:22:33:44:55", // Device MAC
    "1234567890" // Card number
  ],
  "device_id": "00:11:22:33:44:55",
  "timestamp": "2024-01-15T10:30:15.123Z",
  "database_used": "mssql",
  "execution_type": "synchronous",
  "result_count": 0,
  "error_message": "Connection timeout",
  "sas_message": {
    "last_billacceptor_message": "01FF001CA5",
    "sas_version_id": 41
  }
}
```

## SAS Context Information

The `sas_message` field can include:

- **`last_billacceptor_message`**: Most recent bill acceptor SAS message
- **`last_billacceptor_message_handle`**: Last handled bill acceptor message
- **`last_sas_command`**: Most recent SAS command processed
- **`sas_version_id`**: Current SAS protocol version

## Benefits

1. **Debugging**: Correlate database operations with specific SAS messages
2. **Audit Trail**: Complete context of what triggered each database operation
3. **Performance Analysis**: Identify patterns between SAS messages and database calls
4. **Error Tracking**: Better understanding of failures in relation to SAS protocol state

## Querying Examples

### Find all bill acceptor related operations

```sql
SELECT * FROM device_message_queue
WHERE payload->>'procedure_name' = 'tsp_CheckBillacceptorIn'
  AND payload->'sas_message'->>'last_billacceptor_message' IS NOT NULL;
```

### Find operations during specific SAS message processing

```sql
SELECT * FROM device_message_queue
WHERE payload->'sas_message'->>'last_sas_command' = '0120';
```

### Get failed operations with SAS context

```sql
SELECT
  payload->>'procedure_name' as procedure,
  payload->>'error_message' as error,
  payload->'sas_message' as sas_context
FROM device_message_queue
WHERE status = 'proc_failed';
```
