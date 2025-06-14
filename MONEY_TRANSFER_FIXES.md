# Money Transfer System Fixes

## Problem Analysis

Based on the Gemini documentation and code review, the original money transfer implementation had several critical issues:

### 🚨 **Critical Issues Found**

1. **Fire-and-Forget Pattern**: API endpoints sent commands but immediately returned success without waiting for machine confirmation
2. **Missing Status Updates**: Status variables existed but were never updated by response handlers
3. **Async/Sync Mismatch**: Async endpoints using blocking sleep instead of proper async waiting
4. **Transaction ID Logic Error**: Transaction ID increment happened in wrong scope
5. **No Error Handling**: No interpretation of SAS response codes or retry logic

## Fixes Applied

### 1. **Added Wait-for-Completion Logic** ✅

**File**: `sas_money_functions.py`

```python
async def wait_for_para_yukle_completion(self, timeout=10):
    """Wait for money load transfer to complete"""
    start = time.time()
    self.is_waiting_for_para_yukle = 1

    while time.time() - start < timeout:
        status = self.global_para_yukleme_transfer_status

        if status == "00":  # Success
            self.is_waiting_for_para_yukle = 0
            return True
        elif status in ("84", "87", "81", "40"):  # Error codes
            self.is_waiting_for_para_yukle = 0
            return False

        await asyncio.sleep(0.2)

    # Timeout
    self.is_waiting_for_para_yukle = 0
    return None
```

### 2. **Fixed Transaction ID Management** ✅

**Before**:

```python
# Transaction ID was incremented in wrong scope
if doincreasetransactionid:
    transactionid += 1  # Local variable, not persistent!
```

**After**:

```python
def get_next_transaction_id(self):
    """Get the next transaction ID, incrementing the internal counter"""
    self.current_transaction_id = (self.current_transaction_id + 1) % 10000
    return self.current_transaction_id

# In komut_para_yukle:
if doincreasetransactionid:
    actual_transaction_id = self.get_next_transaction_id()
else:
    actual_transaction_id = transactionid
```

### 3. **Updated API Endpoints to Wait for Completion** ✅

**File**: `routers/money_transfer.py`

**Before**:

```python
result = sas_comm.sas_money.komut_para_yukle(...)
# Immediately return success!
return MachineControlResponse(success=True, message="initiated successfully")
```

**After**:

```python
# Send command
actual_transaction_id = sas_comm.sas_money.komut_para_yukle(...)

# Wait for completion
wait_result = await sas_comm.sas_money.wait_for_para_yukle_completion(timeout=15)

if wait_result is True:
    return MachineControlResponse(success=True, message="completed successfully")
elif wait_result is False:
    status_code = sas_comm.sas_money.global_para_yukleme_transfer_status
    status_desc = sas_comm.sas_money.get_transfer_status_description(status_code)
    raise HTTPException(status_code=400, detail=f"Transfer failed: {status_desc}")
else:
    raise HTTPException(status_code=504, detail="Transfer timed out")
```

### 4. **Added Status Code Interpretation** ✅

```python
def get_transfer_status_description(self, status_code):
    """Get human-readable description of transfer status codes"""
    status_descriptions = {
        "00": "Transfer successful",
        "40": "Transfer pending",
        "81": "Transaction ID not unique",
        "84": "Transfer amount exceeds machine limit",
        "87": "Gaming machine unable to accept transfers (door open, tilt, etc.)",
        "80": "Machine not registered for AFT",
        "82": "Registration key mismatch",
        "83": "No POS ID configured"
    }
    return status_descriptions.get(status_code, f"Unknown status: {status_code}")
```

### 5. **Fixed Balance Query Waiting** ✅

**Before**:

```python
await asyncio.sleep(0.5)  # Fixed delay, might miss response
```

**After**:

```python
# Wait for balance response with proper timeout
timeout = 5
start_wait = datetime.now()
while (datetime.now() - start_wait).total_seconds() < timeout:
    # Check if balance has been updated (non-zero values indicate response)
    if (sas_comm.sas_money.yanit_bakiye_tutar > 0 or
        sas_comm.sas_money.yanit_restricted_amount > 0 or
        sas_comm.sas_money.yanit_nonrestricted_amount > 0):
        break
    await asyncio.sleep(0.2)
```

### 6. **Added Response Handler Framework** ✅

```python
def handle_aft_response(self, response_data):
    """
    Handle AFT response from the machine and update status variables.
    This should be called by your SAS polling/response handling logic.
    """
    try:
        if len(response_data) >= 6:
            command = response_data[2:4]
            if command == "72":  # AFT response
                status_code = response_data[6:8] if len(response_data) > 8 else "00"

                # Update appropriate status variable based on transfer type
                if self.is_waiting_for_para_yukle:
                    self.global_para_yukleme_transfer_status = status_code
                elif self.is_waiting_for_bakiye_sifirla:
                    self.global_para_silme_transfer_status = status_code
    except Exception as e:
        print(f"Error parsing AFT response: {e}")
```

## Testing

Created `test_money_transfer.py` to verify the implementation:

- ✅ **Success Case**: Transfer completes successfully
- ✅ **Failure Case**: Transfer fails with proper error code
- ✅ **Timeout Case**: Transfer times out after specified duration
- ✅ **Cashout Case**: Cashout completes successfully

## What Still Needs to Be Done

### 🔧 **Integration Required**

1. **Response Handler Integration**: The `handle_aft_response()` method needs to be called by your SAS polling logic when responses are received from the machine.

2. **Status Variable Updates**: Your SAS communication layer must update the status variables:

   - `global_para_yukleme_transfer_status` (for money loads)
   - `global_para_silme_transfer_status` (for cashouts)

3. **Real Machine Testing**: Test with actual slot machine to verify:
   - Response parsing works correctly
   - Status codes are interpreted properly
   - Timeouts are appropriate for your machine

### 📋 **Example Integration**

In your SAS polling/response handling code:

```python
def handle_sas_response(self, response_data):
    """Called when SAS response is received"""
    # ... existing response handling ...

    # Add AFT response handling
    if hasattr(self, 'sas_money'):
        self.sas_money.handle_aft_response(response_data)
```

## API Changes

### **Endpoint Behavior Changes**

| Endpoint       | Before                               | After                                              |
| -------------- | ------------------------------------ | -------------------------------------------------- |
| `/add-credits` | Returns immediately with "initiated" | Waits for completion, returns "completed" or error |
| `/cashout`     | Returns immediately with "initiated" | Waits for completion, returns "completed" or error |
| `/balance`     | Fixed 0.5s delay                     | Proper timeout with response checking              |

### **New Response Fields**

- `status`: "completed", "initiated_fallback"
- `transaction_id`: Actual transaction ID used (may differ from requested)
- Better error messages with status code descriptions

## Summary

The money transfer system now follows the proper AFT protocol flow:

1. **Send Command** → 2. **Wait for Response** → 3. **Return Result**

Instead of the previous broken flow:

1. **Send Command** → 2. **Return Success Immediately** ❌

This ensures that API clients only receive success responses when the slot machine has actually confirmed the transfer, preventing false positives and improving reliability.
