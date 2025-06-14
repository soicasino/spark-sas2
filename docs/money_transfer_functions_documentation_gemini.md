# AFT Money Transfer Functions Documentation

This document outlines the core functions responsible for handling Advanced Funds Transfer (AFT) operations between the Raspberry Pi and the slot machine via the SAS protocol. These functions manage both loading money onto the machine (cash-in) and cashing money out.

---

## Key Concepts

- **SAS (Slot Accounting System) Protocol**:  
  The industry-standard communication protocol used to communicate with gaming machines. AFT is a feature of this protocol.

- **AFT (Advanced Funds Transfer)**:  
  The specific part of the SAS protocol that allows for electronic transfer of funds to and from the gaming machine. This includes:

  - Cashable credits
  - Restricted promotional credits
  - Non-restricted promotional credits

- **Transaction ID**:  
  A unique identifier for each transfer. The script increments this ID for each new transaction to prevent duplicates.

- **BCD (Binary-Coded Decimal)**:  
  A numerical representation used extensively in the SAS protocol. Amounts are converted to BCD before being sent.

- **CRC (Cyclic Redundancy Check)**:  
  An error-detecting code used to verify the integrity of the messages sent over the serial line.

---

## Core Functions

### `Komut_ParaYukle(doincreasetransactionid, transfertype)` — Load Money Command

**Purpose:**  
To construct and send the AFT command to load funds onto the gaming machine.

**Process:**

1. Increments the global `transactionid` if `doincreasetransactionid` is 1.
2. Retrieves the customer's cashable and promotional balances from the configuration.
3. Determines the type of transfer based on the `transfertype` parameter:
   - `0`: Standard cash-in from customer balance.
   - `1`: Funds from a bill acceptor.
   - `10/11`: Jackpot or handpay award (cashable).
   - `13`: Bonus award (can be cashable or restricted promotional, depending on machine configuration).
4. Converts the monetary amounts into 5-byte BCD format.
5. Constructs the AFT "Transfer funds to GM" command (`72h`). This is a long poll message that includes:
   - Transfer Type (cashable, restricted, etc.)
   - Cashable, Restricted, and Non-Restricted Amounts in BCD
   - Asset Number (the machine's identifier)
   - A unique Transaction ID
6. Calculates the CRC for the command.
7. Sends the complete command to the gaming machine via the `SAS_SendCommand` function.

---

### `Wait_ParaYukle(transfertype)` — Wait for Load Money Completion

**Purpose:**  
To manage the state of the application while waiting for the money transfer to be acknowledged by the gaming machine.

**Process:**

1. Sets a global flag `IsWaitingForParaYukle` to `True`.
2. Calls `Komut_ParaYukle()` to send the initial transfer request.
3. Enters a while loop that continues as long as `IsWaitingForParaYukle` is `True`.
4. The loop monitors a global status variable (`Global_ParaYukleme_TransferStatus`) which is updated by the main SAS polling function when a response is received from the machine.
5. It handles various SAS AFT response codes:
   - `00h`: Full transfer successful. The loop terminates.
   - `40h`: Transfer pending. The loop continues to wait.
   - `81h`: Transaction ID not unique. This might trigger a retry.
   - `84h`: Transfer amount exceeds machine limit. The transfer fails.
   - `87h`: Gaming machine is unable to accept transfers (e.g., door open, tilt). The transfer fails after several retries.
6. If no response is received within a certain timeout, it resends the `Komut_ParaYukle` command.
7. Returns `1` for success or `0` for failure.

---

### `Komut_ParaSifirla(doincreaseid)` — Cash Out Command

**Purpose:**  
To construct and send the AFT command to cash out all funds from the gaming machine.

**Process:**

1. This function is typically called after querying the machine's balance (`Komut_BakiyeSorgulama`).
2. It increments the global `transactionid`.
3. It builds an AFT command (`72h`) with a Transfer Type of `80h` (Transfer funds from GM to host).
4. The amounts for cashable, restricted, and non-restricted are included in the command.
5. The function sends this command to the gaming machine.

---

### `Wait_ParaSifirla()` — Wait for Cash Out Completion

**Purpose:**  
To manage the state of the application while waiting for the cashout to be acknowledged.

**Process:**

1. Similar to `Wait_ParaYukle`, it sets a global flag `IsWaitingForBakiyeSifirla` to `True` and calls `Komut_ParaSifirla()`.
2. It enters a while loop, monitoring `Global_ParaSilme_TransferStatus`.
3. It handles SAS AFT response codes relevant to cashing out, resending the command if the transfer remains pending (`40h`) or if errors occur.
4. The loop terminates when the machine confirms the transfer is complete (`00h`) or has failed.

---

## Dependencies & Global State

The provided functions are heavily reliant on a large number of global variables (e.g., `Config`, `G_Machine_Balance`, `IsWaitingForParaYukle`).  
**In your new object-oriented design:**

- These should be encapsulated as properties of your AFT handling class.
- The cursor for database operations should be passed as an argument to the methods rather than being a global object.

This will improve code clarity, reduce side effects, and make your application much easier to test and maintain.
