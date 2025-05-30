# IGT SAS Protocol Version 6.02 Reference Documentation

_Document ID: gsa-p0013.004.00_  
_Standard Adopted: November 15, 2005_  
_©1991-2005 International Game Technology, Reno, Nevada_

## Purpose

The purpose of the GSA SAS protocol version 6.02 is to facilitate communications between gaming machines and gaming systems.

## Benefits

SAS 6.02 is intended to benefit electronic gaming device manufacturers, system manufacturers, operators, and regulators by defining the system/game communication protocol. The goal of this specification is to improve interoperability between equipment provided by various gaming equipment manufacturers.

## Table of Contents

1. [Gaming Machine Interface](#1-gaming-machine-interface)
2. [Communications](#2-communications)
3. [Host Acknowledgment](#3-host-acknowledgment)
4. [Error Conditions](#4-error-conditions)
5. [Cyclical Redundancy Check](#5-cyclical-redundancy-check)
6. [ROM Signature](#6-rom-signature)
7. [Long Poll Response Specifications](#7-long-poll-response-specifications)
8. [Advanced Funds Transfer](#8-advanced-funds-transfer)
9. [Reserved](#9-reserved)
10. [Progressives](#10-progressives)
11. [Tournament](#11-tournament)
12. [Real Time Event Reporting](#12-real-time-event-reporting)
13. [Bonusing](#13-bonusing)
14. [Jackpot Handpay Reset Methods](#14-jackpot-handpay-reset-methods)
15. [Validation and Ticket Redemption](#15-validation-and-ticket-redemption)
16. [Multi-Denom Extensions](#16-multi-denom-extensions)
17. [Component Authentication Protocol](#17-component-authentication-protocol)

Appendices:

- [A: General Poll Exception Codes](#appendix-a-general-poll-exception-codes)
- [B: Long Poll Commands](#appendix-b-long-poll-commands)
- [C: Game Data Tables](#appendix-c-game-data-tables)
- [D: Figures](#appendix-d-figures)
- [Glossary](#glossary)

## Overview

This document specifies the logical and physical interface of a gaming machine to a slot accounting system host. The communication between the gaming machine and host occurs at 19.2Kbaud, using a wakeup format. Gaming machines can be interfaced to a host either by daisy chaining multiple gaming machines to a single data collection unit, or by connecting single machines to smart interface boards.

To distinguish one gaming machine from another when using a daisy chained configuration, gaming machines must support an attendant configurable system address with a range of 0-127. When a gaming machine is configured with an address of zero, it ignores all communications from the host.

The host requests data by sending general polls and long polls to the gaming machine. General polls are sent to obtain event information. Gaming machines respond with a single byte exception code indicating that an event has occurred (e.g., door open, bill accepted, or handpay pending). When the host desires accounting information, such as the gaming machine's coin in meter, it issues a long poll requesting the specific data. The gaming machine's response includes its address, host command, requested data, and a two-byte CRC.

To verify a gaming machine's Read Only Memory (ROM), the host issues a ROM signature request. Gaming machines are required to continue communications with the host while generating the signature.

The protocol supports various functionalities including:

- Progressive information
- Tournament operation
- Real-time event reporting
- Bonus awards and multiplied jackpots
- Jackpot handpay reset
- Enhanced validation for cash out tickets and handpays
- Support for multiple denominations
- Authentication of gaming machine components

## 1 Gaming Machine Interface

### 1.1 Physical Interface

Gaming machines can be interfaced to the host by two methods:

#### 1.1.1 Daisy Chain

Connects multiple gaming machines to a single host via fiber tap boards. The gaming machine provides:

- A four-wire communication cable terminated with a Molex 70066 Series connector
- A two-wire AC power cable

**Communication Cable Pin Assignments:**

1. Vdd (10 volts typical)
2. Rxd (Serial data input to gaming machine)
3. Txd (Serial data output from gaming machine)
4. Gnd (Ground)

**Power Cable Pin Assignments:**

1. Hot (120V/220V AC)
2. Gnd (Ground)
3. Com (Common)

#### 1.1.2 Smart Interface Boards

Involves installing a SMIB (Smart Interface Board) in each gaming machine to continuously obtain and update information for a single gaming machine and relay this to the host as needed.

### 1.2 Logical Interface

Communication occurs through a serial data link operating at 19.2 KBaud in a "wakeup" mode. The 11-bit data packet consists of:

- One start bit
- Eight data bits
- A ninth 'wakeup' bit
- One stop bit

#### 1.2.1 Wakeup Mode

In wakeup mode, the host sets the 9th (wakeup) bit each time it sends the first byte of a message to the gaming machine. For all additional bytes in the message, this bit is cleared. Gaming machines use the wakeup bit to determine whether the received byte is the first byte of a new message or an additional byte of the current message.

Gaming machines clear the wakeup bit for all bytes when responding to the host, except when reporting a loop break condition.

_Note: For UARTs/DUARTs that do not directly support wakeup mode, the parity bit can be used in place of the wakeup bit._

## 2 Communications

### 2.1 Gaming Machine Addressing

Gaming machines must support an attendant-configurable address with a range of 0 to 127. When configured with an address of 0, the gaming machine ignores all communications from the host. When a gaming machine suffers a critical memory error, it defaults its address to 0, thereby disabling communication until properly configured.

### 2.2 Host Polling

The two primary forms of polls that the host can use to interrogate the gaming machine are general and long polls.

#### 2.2.1 General Polls

To request an event exception from a gaming machine, the host transmits a single-byte message consisting of the gaming machine's address ORed with 80 hex with the wakeup bit set. The addressed gaming machine replies with a single byte exception or a ROM signature verification long poll response. If no exceptions are pending, the gaming machine responds with exception 00, no activity.

Gaming machines must maintain a first in/first out (FIFO) exception queue of at least 20 elements in non-volatile memory. In the event of exception queue overrun, the oldest exception is lost. If one or more exceptions have been lost from the queue, exception 70, buffer overflow, should be reported at the next opportunity.

Most exceptions indicate events, such as a door opened or a tilt. However, some exceptions are part of an interactive process with the host. Interactive exceptions are generally identified as priority exceptions and are not inserted in the exception queue. If the gaming machine has a priority exception pending and also an exception in the queue, the priority exception is always sent before the exception in the queue.

#### 2.2.2 Long Polls

Several types of long polls are available:

##### 2.2.2.1 Type R

This consists of the gaming machine address with the wakeup bit set, followed by a single-byte command code. The gaming machine's response includes its address, command code, an optional length byte, requested data, and a two-byte message CRC.

##### 2.2.2.2 Type S

This consists of the gaming machine address with the wakeup bit set, a single-byte command code, an optional length byte, optional data, and a two-byte message CRC. The gaming machine validates the message CRC and data. If valid, it acknowledges (ACKs) the host by transmitting its address, or by transmitting its address, command code, requested data, and a two-byte message CRC if the poll requests data.

##### 2.2.2.3 Type M

A specialized form of Type S used for multi-game machines. It includes the gaming machine address, command code, optional length byte, a two-byte BCD game number, optional data, and a two-byte message CRC.

Game numbers must be assigned from 0001 through the value returned by long poll 51, without gaps. The numbers should not change dynamically.

##### 2.2.2.4 Type G

Used to transmit data to all gaming machines simultaneously (global broadcast). It consists of a gaming machine address of 00 with the wakeup bit set, a command code, optional length byte, data, and a two-byte message CRC. Gaming machines do not ACK or NACK type G long polls.

#### 2.2.3 Transmitted Data Formats

Data can be in any combination of:

- Packed binary coded decimal (BCD)
- ASCII
- Binary formats

BCD and ASCII data are sent most significant byte (MSB) first. Binary data is sent least significant byte (LSB) first.

For variable length commands/responses, the length is a single binary byte indicating the number of bytes following the length byte (excluding address, command, length or CRC bytes).

### 2.3 Timing Requirements

#### 2.3.1 Gaming Machine Response Time

After a gaming machine has received an entire host message, it has 20 milliseconds (ms) to start transmitting its response. If the host hasn't begun receiving a response after 20 ms, it may time out the gaming machine and continue its polling cycle.

#### 2.3.2 Inter-Byte Delay Time

Inter-byte delay (time between received bytes) cannot exceed 5 ms for both host and gaming machine. If either encounters a delay greater than 5 ms, the message may be considered invalid.

#### 2.3.3 Polling Rate

The host may not issue polls to any single gaming machine faster than once per 200 ms. The slowest allowable polling rate is 5000 ms (five seconds).

Some SAS features (RTE, ticketing) require the gaming machine to support a 40 ms polling rate. Gaming machines capable of this should indicate it in the long poll A0 response.

## 3 Host Acknowledgment

### 3.1 Implied Acknowledgment

An implied acknowledgment (ACK) concept is used to acknowledge data sent from the gaming machine to the host. After the host performs a poll and the gaming machine responds, the host can perform an implied ACK by:

- Issuing a long poll to the same gaming machine (for a general poll)
- Issuing a general poll or a long poll with a different command byte to the same gaming machine (for a long poll)
- Issuing a poll to a different gaming machine
- Issuing a global broadcast

Once a gaming machine has received an implied ACK, it deletes the information from its transmit queue.

### 3.2 Implied Negative Acknowledgment

If the host doesn't receive the response correctly, it repeats the poll. This second poll is an implied negative acknowledgment (NACK), telling the gaming machine to re-send the information. If needed, a third and final poll is issued. The gaming machine must not dispose of the volatile information after this third poll.

### 3.3 Synchronization

After startup or loop break detection, the gaming machine must synchronize to the host polling cycle by ignoring polls for itself and waiting for another gaming machine to be polled or a poll to address zero. Then it resets its state counter and can respond the next time it's polled.

## 4 Error Conditions

### 4.1 Gaming Machine Busy Response

If a gaming machine receives a long poll when processing a time-sensitive task (e.g., spinning reels, accepting a bill), it can respond with a busy response consisting of its address followed by a 00 command code. The host then aborts the long poll attempt and will retry later.

### 4.2 Loop Break Indication

When a gaming machine doesn't receive any address byte for five seconds, it "chirps" by transmitting its own address byte with the wakeup bit set every 200 ms. This indicates a failure in the receive line or a break in the communication loop.

### 4.3 Link Down Detection

A gaming machine must consider the communications link down if:

- It has not received any address byte for five seconds, or
- It has not received any implied acknowledgement from the host for 30 seconds

### 4.4 Unsupported Long Polls

If a gaming machine receives a long poll it doesn't support, it must ignore it and not NACK it. The host must determine which long polls are supported.

### 4.5 Collisions

The gaming machine may only transmit data in response to a poll or when chirping. If it receives an address byte while transmitting or about to transmit, it must abort immediately.

## 5 Cyclical Redundancy Check

### 5.1 Convention

The CRC follows the CCITT convention by starting with the most significant byte, least significant bit and applying the polynomial x^16+x^12+x^5+1.

### 5.2 Host and Gaming Machine CRC Generation

The host calculates a CRC for all type S, M and G long polls over the entire packet, with an initial seed value of zero. The gaming machine calculates the CRC in the same manner for all multi-byte long poll responses, except game busy.

## 6 ROM Signature

### 6.1 Verification

Gaming machines may be required to verify the contents of game ROM(s) upon request. All program memory that influences game outcomes must be included. The verification uses the 16-bit CRC algorithm with a variable seed.

While performing this computation, the gaming machine must continue responding to all communications. The ROM signature is returned to the host in response to the first general poll received after completing the calculation.

### 6.2 Message Format

The ROM signature verification request long poll provides a two-byte ROM verification seed. Once the gaming machine has calculated the signature, it sends a response including the two-byte signature.

## 7 Long Poll Response Specifications

### 7.1 Single Meter Accounting Long Polls

Many defined long polls request a single four-byte BCD meter from the gaming machine. Some are defined as multi-denom aware so meters may be retrieved for all games at a specific denomination.

If a gaming machine doesn't support a meter but knows the value must be zero, it should report zero. However, a meter that cannot be tracked should result in the poll being ignored.

### 7.2 Multiple Meter Accounting Long Polls

Several long polls allow the host to obtain multiple meters with a single long poll (0F, 19, 1C, 1E). These return sets of related meters like:

- Total cancelled credits, coin in, coin out, drop, jackpot, and games played
- Bill meters ($1, $5, $10, $20, $50, $100)

### 7.3 Send Selected Meters for Game N Long Poll

Long poll 2F allows the host to obtain up to ten selectable meters with a single long poll. Meters are reported using the number of BCD bytes listed in Table C-7.

This poll is multi-denom-aware, so meters may be retrieved for all games at a specific denomination. However, the game number must be 0000 (for the entire terminal) when using with the multi-denom preamble.

### 7.4 Enable/Disable Long Polls

Various aspects of the gaming machine can be enabled or disabled by the host:

- Game play
- Sound
- Bill acceptor
- Maintenance mode

#### 7.4.1 Shutdown (Lock Out Play) Command

This disables all user inputs except "cash out" and "change/attendant". If a game is in progress, it must complete the current game cycle before disabling.

#### 7.4.2 Maintenance Mode

Used in some jurisdictions to inform the gaming machine that an operator is properly logged into the system, preventing door alarm sounds.

# IGT SAS Protocol Version 6.02 Reference Documentation (Continued)

## 7.5 Configure Bill Denominations Long Poll

A special form of the enable/disable long poll, the configure bill denomination long poll allows the host to enable/disable bill denominations independently of one another. This type S long poll from the host includes:

- Gaming machine address
- Command (08)
- Bill Denominations (4 bytes binary, LSB first)
  - Each bit controls a specific denomination
  - Bit 0 = $1, Bit 1 = $2, Bit 2 = $5, etc.
- Bill Acceptor Action Flag
  - Bit 0: 0 = Disable bill acceptor after each accepted bill, 1 = Keep bill acceptor enabled

The gaming machine may be configured to ignore bills regardless of this message.

## 7.6 Multi-Game Long Polls

### 7.6.1 Enable/Disable Game N

This type M long poll specifies command code 09, the game number of the desired game, and a 1-byte binary flag indicating whether to enable or disable game n. Long poll 09 is defined as a multi-denom-aware poll, so games may be enabled or disabled for a specific denomination.

### 7.6.2 Send Total Hand Paid Cancelled Credits

By issuing a type M long poll with a 2D command code, the host can request the total amount of hand paid cancelled credits for a specific game. These include all credits paid from the credit meter by an attendant handpay. They do not include any credits added to the jackpot meter.

### 7.6.3 Send Number of Games Implemented

The host issues the type R long poll with a 51 command code to obtain the number of implemented games from a gaming machine. This returns a 2-byte BCD value indicating the total number of games implemented.

In response to long poll 51, gaming machines must send the total number of implemented games, not the number of games currently available to the player. Games must be numbered from 0001 through the number in the response.

If a gaming machine does not support multi-game extensions, it must respond with the number of games implemented equal to zero and ignore all multi-game polls that specify a game number other than zero.

### 7.6.4 Send Game N Meters

By issuing a type M long poll with a 52 command code and specifying the desired game number, the host can request meters for a specific game in a multi-game gaming machine.

The response includes:

- Game number
- Total coin in meter
- Total coin out meter
- Total jackpot meter
- Games played meter

### 7.6.5 Send Game N Configuration

To obtain a specific game's information from a multi-game gaming machine, the host issues a type M long poll with a 53 command code and specifies the game number.

The response includes:

- Game number
- Game ID (2-byte ASCII)
- Additional ID (3-byte ASCII)
- Denomination (1-byte binary)
- Max bet (1-byte binary)
- Progressive group (1-byte binary)
- Game options (2-byte binary)
- Paytable ID (6-byte ASCII)
- Base % (4-byte ASCII)

If the host issues this poll with a game number of 0000, the information in the response must match the information returned in long poll 1F.

### 7.6.6 Send Selected Game Number

The host may issue the type R long poll with a 55 command code to obtain the game number of the currently selected game on a multi-game gaming machine. If the gaming machine is in a game selection menu with no game currently selected, it responds with game number zero (0000).

### 7.6.7 Send Enabled Game Numbers

The host can issue a type R long poll with a 56 command code to obtain the game numbers of the games that are actually available to the player. For a multi-denom gaming machine, these will be the games enabled at the currently selected denomination. Long poll 56 is multi-denom-aware, allowing the host to obtain the list of games enabled for any specific denomination.

## 7.7 Send Games Played Since Last Power Up and Slot Door Closure Long Poll

This variation of the multiple meter accounting long poll requires the gaming machine to respond with a pair of two-byte BCD meters:

- Games played since last power up
- Games played since last slot door closure

## 7.8 Send Handpay Information Long Poll

When the host receives exception 51 (handpay pending), it requests the handpay information by sending a type R long poll with a 1B command code.

The response includes:

- Progressive group
- Level
- Amount (5 BCD)
- Partial pay (2 BCD)
- Reset ID (1 binary)

If the handpay amount does not include any progressive wins, the "amount" field indicates only the handpay amount and does not include any partial pay amount. If it includes progressive wins, the "amount" field indicates the entire win amount, including the amount in the "partial pay" field.

### 7.8.1 Handpay Queue

To prevent loss of handpay information during SAS link down situations, gaming machines must maintain an n-entry FIFO handpay queue (minimum of 5). Exceptions 51 and 52 are treated as priority exceptions. When a handpay occurs, the gaming machine stores all pertinent data required for the 1B long poll and sends exception 51.

If long poll 1B is not received within fifteen seconds after exception 51 has been acknowledged, the gaming machine reissues exception 51 every fifteen seconds as long as the entry remains in the queue.

Exception 52 is sent after the handpay has been reported via long poll 1B and reset. If multiple handpays are queued, after exception 52 is acknowledged, the machine sends another exception 51 for the next handpay.

### 7.8.2 Legacy Handpay Reporting

The original handpay behavior inserts exception 51 in the exception queue when the gaming machine locks up in a handpay, and inserts exception 52 when the handpay is reset. Long poll 1B returns current handpay information while in lockup, or all zeros when not in a handpay lockup.

Some systems may not know to poll for 1B data in response to exception 51. For compatibility with such systems, gaming machines must provide an operator configuration to enable legacy handpay reporting or disable the re-issuing of exception 51 every 15 seconds.

## 7.9 Remote Handpay Reset

As an alternative to an attendant resetting a handpay condition, the host can remotely reset a handpay using type S long poll with a 94 command code.

The response includes a reset code:

- 00: Handpay was reset
- 01: Unable to reset the handpay
- 02: Not currently in a handpay condition

If the W2-G Reset To Credit Meter function has been enabled using long poll A8, long poll 94 will reset the handpay to the credit meter.

## 7.10 Send Gaming Machine ID and Information Long Poll

The host can issue a type R long poll with command code 1F to request gaming machine ID and information.

The response includes:

- Game ID (2-byte ASCII)
- Additional ID (3-byte ASCII)
- Denomination (1-byte binary)
- Max bet (1-byte binary)
- Progressive group (1-byte binary)
- Game options (2-byte binary)
- Paytable ID (6-byte ASCII)
- Base % (4-byte ASCII)

For multi-game machines where only a subset of games are available, the max bet field contains the largest configured max bet for available games, and the base % field contains an average percentage for available games.

## 7.11 Send Last Accepted Bill Information Long Poll

When a gaming machine accepts a bill, it reports a corresponding bill accepted exception code (47-4E, 50), or the general bill accepted exception 4F. The host can then poll for the bill information using long poll 48.

The response includes:

- Country code (1 BCD)
- Denomination code (1 BCD)
- Bill meter (4 BCD) - Number of accepted bills of this type

## 7.12 Send Card Information

The host can request a gaming machine's card information using type R long poll with an 8E command code.

The response includes:

- Hand type (0 = Dealt hand, 1 = Final hand)
- Hand (5 binary) - Card data with the left most card sent first

On gaming machines with multiple hands or more than five card positions, only the base hand or first five card positions can be reported.

## 7.13 Send Physical Reel Stop Information

The host can obtain a gaming machine's physical reel stop information using type R long poll with an 8F command code. The response includes 9 bytes of binary reel stop information with the left most reel sent first. Unused bytes are padded with FF.

## 7.14 Send Enabled Features

By issuing a type M long poll with an A0 command code, the host can interrogate numerous features of a gaming machine.

The response includes Feature Codes for:

- Jackpot multiplier
- AFT bonus awards
- Legacy bonus awards
- Tournament support
- Validation extensions
- Validation style
- Ticket redemption
- Meter model flag
- Support for extended meters
- Component Authentication
- Advanced Funds Transfer
- Multi-denom extensions
- Maximum polling rate
- Multiple SAS progressive win reporting

## 7.15 Send SAS Version ID and Gaming Machine Serial Number

To obtain a gaming machine's serial number and SAS version support, the host can issue a type R long poll with a 54 command code. The response includes the SAS version number (3 ASCII) and the gaming machine serial number (0 to 40 bytes ASCII).

## 7.16 Send Cash Out Limit

The cash out limit is the largest amount (in SAS accounting denom units) that the gaming machine can pay from the hopper without locking up in a handpay. The host can obtain this by issuing a type M long poll with an A4 command code.

## 7.17 Receive Date and Time

The host can synchronize all gaming machines to the same real time clock using type G global broadcast long poll 7F. This sends a date (MMDDYYYY) and time (HHMMSS) to set the gaming machine's clock.

## 7.18 Send Current Date and Time

The host can read a gaming machine's current date and time using type R long poll with a 7E command code.

## 7.19 Send Current Hopper Status

The host can obtain the current hopper status and level by issuing a type R long poll with a 4F command code. The response includes:

- Status (1 binary)
- % Full (1 binary)
- Level (4 BCD) - Number of coins in hopper, if available

## 7.20 Enable/Disable Game Auto Rebet

To configure a game to auto rebet (play continuously without customer interaction), the host issues the type S long poll with command code AA.

## 7.21 Send Extended Meters for Game N

This provides a method to communicate cumulative meters up to 18 decimal digits in length. Two different long poll codes (6F and AF) can access the same meter data, allowing consecutive meter polls.

Using these polls, the host can obtain up to 12 meters per poll from the list in Table C-7. The response includes the meter code, size (in bytes), and value for each requested meter.

## 7.22 Send Token Denomination

The host may use the type R long poll B3 to determine the current coin mechanism and/or hopper denomination.

## 7.23 Send Extended Game N Information

The type M long poll B5 allows a host to retrieve additional data for the gaming machine or a specific game. This includes the max bet (2 BCD bytes, allowing larger values than long polls 1F and 53), progressive group, progressive levels, game name, paytable name, and number of wager categories supported.

## 7.24 Weighted Average Theoretical Payback Percentage

If any single paytable has a significant difference between minimum and maximum theoretical payback percentage, the gaming machine may need to provide a calculated weighted average.

### 7.24.1 Calculated By Gaming Machine

Meter 007F provides the weighted average theoretical payback percentage as calculated by the gaming machine. This is calculated by dividing the amount wagered at each different theoretical base payback percentage by the total amount wagered, multiplying by the individual payback percentage, then summing the results.

### 7.24.2 Send Wager Category Information

Long poll B4 allows the host to obtain the individual Coin In meters for each different payback percentage or credits wagered. The response includes the payback percentage and Coin In meter for each wager category.

## 8 Advanced Funds Transfer

The SAS Advanced Funds Transfer Protocol (AFT) provides a robust, secure, highly auditable method for transferring funds between a host and a gaming machine. This replaces the EFT/ECT protocol from SAS 3.x.

All transfers require:

- A non-zero "asset number" to identify the gaming machine
- A unique transaction ID (printable ASCII characters 20-7E hex)

Key terminology:

- "Promotional" refers to amounts given as incentive or reward
- "Restricted" refers to promotional amounts that must be wagered and cannot be redeemed for cash
- "Nonrestricted" refers to promotional amounts that may be redeemed for cash but have special accounting
- "Cashable" refers to amounts redeemable for cash with no special accounting
- "Regular cashable" refers specifically to amounts that aren't debit or nonrestricted promotional
- "Total cashable" refers to the combined total of debit, cashable and nonrestricted promotional amounts

When multiple types of credits are present, restricted amounts must be played first, then nonrestricted, and finally cashable amounts.

Transfers are categorized as:

- In-house
- Bonus (win amounts awarded by an external bonusing system)
- Debit (transactions from a player's external bank account)

For transfers, the gaming machine maintains:

- A one-element buffer for the current/recent transfer request
- A circular history buffer (max 127 elements) for completed transfers

### 8.1 AFT Register Gaming Machine Long Poll

Before instructing a gaming machine to perform debit transfers, the host must register the gaming machine using long poll 73. Registration for debit transfers requires:

- A non-zero AFT registration key
- A non-zero Point of Sale terminal ID (POS ID)

The registration process involves:

1. Host initializes registration with registration code 00
2. Gaming machine transitions to registration status 00
3. Host completes registration with registration code 01, machine's asset number, registration key and POS ID
4. Gaming machine sets status to 01

For operator present registrations:

1. Gaming machine issues exception 6C (request to register)
2. Host may request operator acknowledgement (code 40)
3. Gaming machine waits for operator acknowledgement
4. After acknowledgement, machine issues exception 6D and reverts to status 00
5. Host completes registration with code 01

### 8.2 AFT Game Lock and Status Request Long Poll

The host may interrogate the current AFT availability status and request gaming machine locking using type S long poll 74.

The lock process allows the host to hold the gaming machine in a state where it can perform a transfer. The gaming machine may be in one of three lock states:

- FF = Not locked
- 40 = Lock pending
- 00 = Locked

When locked, the gaming machine should display "Please Wait" and start a timer for the lock timeout duration. If the timer expires, the machine exits the locked state.

After entering the locked state, the gaming machine issues exception 6F (game locked) and reissues it every five seconds while locked.

### 8.3 AFT Transfer Funds Long Poll

The host may use long poll 72 to transfer funds to or from the gaming machine, instruct the machine to print a ticket, or award a bonus win amount. The host may also request transaction receipts for these transfers.

When initiating a transfer, the transaction index must be zero. Transfer requests may specify "full transfer only" (code 00) or "partial transfer allowed" (code 01). For partial transfers, the gaming machine can perform a transfer for any amount equal to or less than the specified amount.

The host may also use long poll 72 to interrogate the status of current or recent transfer requests and retrieve the history of completed transfers.

Transfer status codes in the response are categorized by their most significant bits:

- Binary codes 000xxxxx indicate transfer successful
- Binary codes 010xxxxx indicate transfer pending
- Binary codes 100xxxxx indicate transfer failed
- Binary codes 110xxxxx indicate incompatible poll
- Binary codes 111xxxxx indicate no transfer information available

Transaction receipts are only printed for successful transfers of non-zero amounts. If a receipt was requested, the gaming machine indicates receipt status in the response.

### 8.4 Accepting Transfers

The gaming machine must reject transfers or ignore transfer polls if it is not enabled for AFT. It must not accept transfers when in an unplayable state (door open, operator menu, tilt, disabled, waiting for handpay, etc.), except if cash out is allowed in a tilt or disable state.

If the host requests that a transfer only be accepted if the gaming machine is "locked," the machine must reject the transfer if not currently locked using long poll 74.

### 8.5 Bonus Awards

Bonus award transfers differ from other transfers in that they are considered game win and contribute to total gaming machine hold and yield calculations. Because they can be paid to the credit meter, hopper, ticket, handpay, etc., they are not limited by the credit limit or maximum transfer limit.

Bonus awards are metered in either the Total Machine Paid External Bonus Win meter or Total Attendant Paid External Bonus Win meter, depending on the payment method. They are also added to the Total Coin Out or Total Jackpot meter as appropriate.

### 8.6 Transaction History

The gaming machine maintains a circular buffer of successfully completed transfers for non-zero amounts and all bonus transfers, up to a maximum of 127 entries. The host can retrieve transactions from this history using the interrogation form of long poll 72.

### 8.7 Host Cashout Enable

When initiating a transfer, the host can specify a requested Host Cashout Enable state. When enabled, the gaming machine should treat the host as an available cashout device.

When the player requests a cashout and host cashouts are enabled, the gaming machine issues exception 6A (AFT request for host cashout). The host should then send long poll 72 to initiate a transfer to the host.

For wins ready to be cashed out to the host, the gaming machine issues exception 6B (AFT request for host to cash out win).

### 8.8 Cash Out Button Pressed

If AFT transfers to host are enabled, the gaming machine reports exception 66 whenever the player presses the cash out button, regardless of credit amount or type.

### 8.9 Lock After Transfer

The host can request a lock after transfer completion in the long poll 72 transfer request. When requested, the gaming machine attempts to establish a new lock when the transfer is complete, before allowing game play. This allows multiple transfers in one game idle state.

### 8.10 AFT Meters

Gaming machines supporting AFT must track the cumulative value and total number of transfers for each supported transfer type. These meters can be obtained using long polls 2F, 6F, or AF.

### 8.11 Transaction Receipts

To print transaction receipts and registration reports, a gaming machine must have a printer capable of at least 24 lines of 22 ASCII characters per line. Three basic receipt types are defined:

- In-house transfers to the gaming machine
- Debit transfers to the gaming machine
- In-house transfers to the host

#### 8.11.1 Set AFT Receipt Data

Long poll 75 allows the host to configure various data fields printed on transaction receipts.

#### 8.11.2 Transaction Receipt Layout

A standard receipt layout includes:

- Location and address information
- Transfer description and details
- Date and time
- Asset number
- Transaction ID
- Amount information
- Custom text lines

#### 8.11.3 Sample Transaction Receipts

Examples are provided for AFT transfers to/from the gaming machine and debit card withdrawals.

### 8.12 Set Custom AFT Ticket Data

Long poll 76 provides support for custom text and graphics on tickets generated using the AFT transfer to ticket functionality. This allows customization while leaving standard text in place for normal cashout activity.

## 9 Reserved

This section is intentionally left blank.

## 10 Progressives

SAS progressive support allows the host to provide progressive amounts to the gaming machine. The gaming machine must be configured with a non-zero Group ID to enable progressive control by the SAS host.

### 10.1 Broadcasts

The host can send progressive information to gaming machines using global broadcasts (long polls 80 and 86):

- Single Level Progressive Broadcast (80): sends one progressive level to one group
- Multiple Level Progressive Broadcast (86): sends up to 32 progressive levels to one group

#### 10.1.1 Group

The group ID identifies the group to which the level and amount belong. Group ID 00 is reserved for non-SAS progressives.

#### 10.1.2 Level

The level field allows multiple progressive amounts to be configured under a single group. Level 01 is the top award, level 02 is the next highest, etc.

#### 10.1.3 Amount

This is the progressive amount in units of cents.

### 10.2 Timing

Progressive broadcasts are issued as needed to update gaming machines. A gaming machine configured for SAS progressives must receive updates for its configured levels within five seconds of the last broadcast for that level.

If a gaming machine doesn't receive a progressive broadcast within the required time frame, it reports exception 53 (no progressive information received for five seconds).

### 10.3 Contributions

The host can obtain progressive coin in contribution amounts through:

- Credits wagered amount from the game start message (in RTE mode)
- Polling the coin in meter and calculating a delta amount
- Using the coin/credit wagered exception for machines with max bet of 10 or less

### 10.4 Reporting Progressive Wins

When a progressive win occurs, the gaming machine reports exception 54 (cashout device/credit paid win) or 51 (handpay pending). For SAS-controlled progressives, it also reports exception 56 (SAS progressive level hit).

#### 10.4.1 SAS Progressive Level Hit Exception

Gaming machines must maintain a queue of SAS progressive win data. When a SAS progressive level is hit, the level and amount are placed in this queue and exception 56 is reported.

#### 10.4.2 Send SAS Progressive Win Amount

Upon receiving exception 56, the host can request the progressive win amount using long poll 85.

#### 10.4.3 Send Multiple SAS Progressive Win Amounts

Alternatively, the host can request all progressive win amounts in the queue using long poll 87.

### 10.5 Resetting Progressive Levels

After receiving progressive win information, the host should immediately broadcast the reset amount for the hit progressive.

### 10.6 Cumulative Progressive Wins Meter

Gaming machines track the cumulative sum of all progressive wins in the Cumulative Progressive Wins meter, accessible via long poll 83.

## 11 Tournament

### 11.1 Configuration

Tournament mode configuration allows the host to remotely configure gaming machines for tournament play using long poll 8C. This includes setting:

- Time in minutes and seconds
- Starting credits
- Tournament pulses enablement

### 11.2 Entering Tournament Mode

When a gaming machine receives the enter/exit tournament long poll, it completes any game, funds transfer, or bill transaction before entering tournament mode. If in a tilt or handpay condition, it waits until the condition is reset.

### 11.3 Accounting

Gaming machines must account for tournament games played, games won, credits wagered, and credits awarded per tournament session.

## 12 Real Time Event Reporting

Real-time event reporting (RTE) allows gaming machines to report events in response to long polls as well as general polls. This enables timely reporting of reel stops, coins in, game end, etc.

### 12.1 Enabling/Disabling Real Time Event Reporting

The host configures a gaming machine for RTE using long poll 0E.

### 12.2 Polling Method

The standard polling format is used, but the polling rate can be increased to 40 ms to better approximate real-time reporting.

### 12.3 Priority

Event reporting takes priority over long poll responses. If a gaming machine has outstanding events when it receives a long poll, it reports the event.

### 12.4 Host/Gaming Machine Acknowledgment

When the host receives an event response to a long poll, it considers the long poll NACKed and reinserts it into the transmit queue.

### 12.5 Event Response Format

In RTE mode, gaming machines report exceptions using an event message format that includes:

- Gaming machine address
- Event identifier (FF)
- Exception code
- Additional data (if applicable)
- CRC

Specific event messages include:

#### 12.5.1 Bill Accepted

Includes country code, denomination code, and number of accepted bills of this type.

#### 12.5.2 Legacy Bonus Pay Was Awarded

Reports multiplier, multiplied win amount, tax status, and bonus amount.

#### 12.5.3 Game Start

Includes credits wagered, coin in meter, wager type, and progressive group.

#### 12.5.4 Game End

Reports the game win amount (excluding bonus awards).

#### 12.5.5 Reel N Has Stopped

Includes the reel number and physical stop position.

#### 12.5.6 Game Recall Entry Displayed

Reports the game number and recall entry index being viewed.

#### 12.5.7 Card Held/Not Held

Indicates the card number and whether it was held or not held.

#### 12.5.8 Game Selected

Reports the selected game number on a multi-game machine.

### 12.6 No Activity Exceptions

In RTE mode, gaming machines don't report exception codes 00 (no activity) and 1F (no activity and waiting for player input). No activity is implied when no real-time event is sent.

### 12.7 ROM Signature Response

Gaming machines may respond with a ROM signature response to a long poll. Unlike RTE responses, this doesn't include the event identifier byte FF.

## 13 Bonusing

SAS supports two forms of bonusing:

1. "Legacy" bonusing - direct bonus awards and multiplied jackpots
2. AFT bonusing - through the Advanced Funds Transfer protocol

### 13.1 Enabling/Disabling Bonusing

Gaming machines must have a secure method for enabling/disabling bonusing at the machine level. AFT bonusing and legacy bonusing should be configurable separately.

### 13.2 Reporting Active Players

A SAS host can award 'active' players with additional bonuses by monitoring game start exceptions. If a second game start exception is received before a timer expires, that player is deemed active.

Exception 1F is reported when the gaming machine is waiting for player input (idle state, waiting for player to insert coins, play credits, etc.).

### 13.3 Legacy Bonus Awards

The host can award bonuses to players using long poll 8A, specifying:

- Credit amount
- Tax status (deductible, non-deductible, wager match)

The gaming machine's behavior depends on its current state:

#### 13.3.1 During Game Play

Bonuses received during game play are held in escrow until the game ends.

#### 13.3.2 During Idle

Bonuses received during idle state are paid immediately.

#### 13.3.3 During a Handpay

Bonuses received during a handpay are escrowed until the handpay is reset.

#### 13.3.4 During Player Screens

Bonuses received during player screens can be awarded immediately or escrowed until the screen is exited.

#### 13.3.5 During a Malfunction, Door Open, or Maintenance

Bonuses received during tilt conditions, door open, maintenance mode, or game recall mode should not be escrowed. The gaming machine indicates its inability to fulfill the bonus by issuing a game busy response.

### 13.4 Multiplied Jackpots

_Note: This feature is not recommended for implementation due to game design dependency issues._

Allows the host to instruct the gaming machine to multiply wins within a specified range.

#### 13.4.1 Multiplied Jackpots and Multi-Line Gaming Machines

For multi-line games, if max bet is required for multiplier eligibility, the total max bet must be wagered. If a game cycle results in wins on multiple lines, the individual wins are summed before applying the multiplier.

#### 13.4.2 Multiplied Jackpots and Bonus Awards

External bonus awards are not included in the multiplication of multiplied jackpots.

#### 13.4.3 Multiplied Jackpots and Progressive Wins

Progressive wins are eligible for multiplied jackpots, except for Wide Area Progressive wins.

### 13.5 Reporting Multiplied Jackpots and Legacy Bonus Awards

When a gaming machine awards a legacy bonus, it reports exception 7C. The host can request details using long poll 90.

### 13.6 Bonus Accounting

Gaming machines must account for deductible, non-deductible, and wager match legacy bonus awards and multiplied jackpots. The host can request these meters using long poll 9A.

### 13.7 Game Delay

To accommodate fast game cycles where the host may not have time to issue a bonus pay, the game delay command (long poll 2E) allows the gaming machine to delay after a game end event.

## 14 Jackpot Handpay Reset Methods

For high denomination gaming machines, an alternative handpay reset method allows wins to be reset to the credit meter instead of being paid by an attendant.

### 14.1 Attendant Authorization

When a jackpot handpay occurs, the gaming machine checks the win against the upper jackpot limit and the machine's credit limit to determine if it's eligible for reset to the credit meter. This eligibility is reported to the host in the Reset ID field of long poll 1B response.

### 14.2 Enabling Jackpot Handpay Reset Methods

The host enables the reset-to-credit-meter method using long poll A8.

## 15 Validation and Ticket Redemption

SAS supports three validation types:

1. Standard validation - gaming machine generated 8-digit validation number
2. Secure enhanced validation - gaming machine generated 16-digit number with security features
3. System validation - host-provided 16-digit number plus 2-digit system ID

Secure enhanced validation requires the gaming machine to maintain:

- A gaming machine validation ID
- A validation sequence number
- A circular buffer of validation records

System validation has the gaming machine request a validation number from the host when a cashout is pending, using exception 57.

For both secure enhanced and system validation, the gaming machine reports exception 3D (cash out ticket printed) or 3E (handpay validated).

### 15.1 Improved Ticket Expiration Support

Extended validation provides improved functionality for setting and reporting ticket expiration values through long poll 7B.

### 15.2 Extended Validation Status Long Poll

Long poll 7B controls parameters for validation and ticket printing, including:

- Using printer as cashout device
- Using printer as handpay receipt device
- Validating handpays
- Printing restricted tickets
- Allowing tickets for "foreign" restricted amounts
- Enabling ticket redemption

### 15.3 Set Extended Ticket Data

Long poll 7C configures data printed on tickets and receipts, including:

- Location name
- Address lines
- Restricted ticket title
- Debit ticket title

### 15.4 Set Ticket Data Long Poll

Long poll 7D sends common ticket data to multiple machines, including:

- Host ID
- Expiration period
- Location name
- Address lines

## 15.5 Send Cash Out Ticket Information Long Poll

When a gaming machine reports exception 3D (cash out ticket printed) or 3E (handpay validated), the host may issue a type R long poll with a 3D command code to request the cash out ticket information. The gaming machine response includes an eight-digit (4 BCD) ticket validation number and the amount of the cash out in cents.

If a gaming machine is configured for secure enhanced or system validation, it should not respond to long poll 3D to the validation controller. When responding to a non-validation controller host, the gaming machine must return all zeros in the Validation Number field.

## 15.6 Set Secure Enhanced Validation ID

For a gaming machine to perform secure enhanced ticket/receipt/handpay validation, the host must use type S long poll 4C to set the gaming machine's validation ID number and initial validation sequence number.

The gaming machine response includes the current ID and sequence number. If the host sends the same ID and sequence number that were previously sent, but the gaming machine has incremented the sequence number, it will continue to use the current incremented value.

Note: To prevent non-unique validation numbers in the field, systems providers should contact IGT for allocation of gaming machine validation ID numbers.

## 15.7 Send Pending Cashout Information

When a gaming machine configured for system validation is ready to print a cashout ticket, it issues exception 57 (system validation request). When the host receives this, it uses type R long poll 57 to request the pending cashout information.

The response includes:

- Cashout type (00 = Cashable ticket, 01 = Restricted promotional ticket, 80 = Not waiting for system validation)
- Amount (in cents)

## 15.8 Receive Validation Number

After polling for the cashout information, the host provides the validation number using type S long poll 58. This includes:

- Validation System ID (1 BCD) - non-zero for valid validation, 00 to deny validation
- Validation number (8 BCD) - 16-digit number to use for the cashout

If validation is denied, the gaming machine must use another means to perform the cashout or abort it. If the host doesn't respond within ten seconds, the gaming machine proceeds as though system validation had been denied.

## 15.9 System Validation Examples

Two examples demonstrate the system validation process:

1. Host validates a cashout ticket
2. Host refuses to validate a cashout ticket

## 15.10 Send Enhanced Validation Information

For secure enhanced or system validation, the host uses type S long poll 4D to read validation records from the gaming machine's buffer. This long poll has function codes:

- 00 = Read current unread validation info (marks record as read)
- 01-1F = Read validation info from buffer index n
- FF = Look ahead at current validation info (without marking as read)

The response includes:

- Validation Type
- Buffer Index number
- Date and Time
- Validation number (16 digits)
- Amount (in cents)
- Ticket number
- Validation System ID
- Expiration date
- Pool ID (for restricted tickets)

## 15.11 Send Ticket Validation Data Long Poll

When a ticket is inserted into a validator, the gaming machine issues exception 67 (ticket has been inserted). The host responds with type R long poll 70 to request the ticket's validation data.

The response includes:

- Ticket status (00 = ticket in escrow, FF = no ticket in escrow)
- Ticket amount (in cents)
- Parsing code (identifies format of validation data)
- Validation data (up to 32 bytes)

## 15.12 Redeem Ticket Long Poll

After receiving the validation data, the host can authorize or reject the ticket using long poll 71. This includes:

- Transfer code (table of values indicating validity and type of ticket)
- Transfer amount (in cents)
- Parsing code
- Validation data
- Restricted expiration (for restricted tickets)
- Pool ID (for restricted tickets)

The gaming machine response includes:

- Machine status code (indicates success, pending, failure, etc.)
- Transfer amount
- Parsing code
- Validation data

A ticket redemption cycle proceeds as follows:

1. Gaming machine receives long poll 70
2. Gaming machine responds with ticket data
3. Host sends long poll 71 with authorization/rejection
4. Gaming machine responds with status 40 (redemption pending)
5. Gaming machine validates and processes the ticket
6. Gaming machine issues exception 68 (ticket transfer complete)
7. Host polls for completion status with long poll 71 (transfer code FF)
8. Gaming machine responds with final status

## 15.13 Send Validation Meters

Gaming machines supporting validation/redemption track cumulative values and counts for each type of validation and redemption. The host obtains these meters using type S long poll 50.

Types of validation include:

- Cashable tickets
- Restricted promotional tickets
- Handpay receipts (canceled credits and jackpots)
- Validated handpays (no receipt)
- Redeemed tickets (cashable, restricted, nonrestricted)

## 15.14 Standard Validation Algorithm

A method for calculating the 8-digit validation number is provided, using:

- Credit amount (3 bytes BCD)
- Time of cashout (3 bytes BCD)
- BCD addition with carry
- Base 16 to base 10 conversion

## 15.15 Secure Enhanced Validation Algorithm

For secure enhanced validation, cash out ticket and handpay validation numbers are generated using the gaming machine validation ID and the current validation sequence number. The algorithm involves:

1. Placing the ID and sequence number in a 6-byte array
2. Transforming this array using XOR operations
3. Applying CRC calculations
4. Converting to BCD
5. Final transformations to produce a 16-digit number

## 16 Multi-Denom Extensions

Gaming machines allowing player-selectable denominations require special handling in SAS. A base "accounting" credit value must be established that can represent any credit transaction on the machine. All available player denominations must be evenly divisible by this accounting denomination.

Terminology:

- Accounting denomination: Base denomination used for gaming machine accounting
- Player denominations (or game denominations): Denominations available to the player
- Token denomination: Denomination of the coin mechanism and/or hopper

### 16.1 Multi-Denom Preamble

The host uses the multi-denom preamble (long poll B0) with certain long polls to obtain player denomination-specific information. The preamble takes the form of a variable length type S long poll that includes:

- Gaming machine address
- Command (B0)
- Length
- Denomination (specific value or 00 for default)
- Base command (from the list of multi-denom-aware long polls)
- Data appropriate for the base long poll

The response mirrors this structure, with data appropriate to the base command's response. If there's an error, the base command response byte will be 00, followed by an error code.

### 16.2 Multi-Denom Preamble Examples

Examples demonstrate using the preamble to:

1. Obtain a list of games enabled for a specific denomination
2. Get the Total Coin In meter for a specific denomination

### 16.3 Send Current Player Denomination

Type R long poll B1 provides the denomination currently selected by the player for game play.

### 16.4 Send Enabled Player Denominations

Type R long poll B2 provides a list of all denominations currently available to the player.

## 17 Component Authentication Protocol

The SAS Component Authentication Protocol allows the host to verify that all executable programs and fixed data in a gaming machine match the data approved for operation in the local jurisdiction. The host can:

- Interrogate which software components exist
- Request authentication of specific components
- Select from supported authentication methods
- Provide seeds and offsets as needed

Components may include:

- Executable code
- Paytables
- Graphics
- Sound data
- Peripheral device firmware

Each component must have a unique ASCII name up to 127 characters long.

### 17.1 Send Authentication Info

Type S long poll 6E allows the host to monitor and control the Component Authentication Protocol. Actions include:

- Interrogate number of installed components
- Read status of components
- Authenticate components
- Interrogate authentication status

Authentication methods supported include:

- CRC 16
- CRC 32
- MD5
- Kobetron I
- Kobetron II
- SHA1

When the list of installed components changes, the gaming machine issues exception 8E. When authentication completes, it issues exception 8F.

Note that authentication of some components may not be possible during game play without impacting operation. Gaming machines must provide authentication of program memory that influences game outcomes at any time, but other memory and peripherals may only be available for authentication when the credit meter is zero and the machine is disabled.

## Appendix A: General Poll Exception Codes

A comprehensive list of exception codes includes categories such as:

- Activity (00, 1F)
- Door events (11-16, 19-1E, 98-9B)
- Power events (17, 18)
- Tilt conditions (20-2E)
- Memory errors (31-39)
- Configuration changes (3C)
- Ticket/validation events (3D, 3E, 3F, 57, 67, 68)
- Reel events (40-46, 88)
- Bill acceptor events (28-2C, 47-50)
- Game events (51-56, 7C, 7E, 7F, 89, 8A, 8B, 8C)
- Printer events (60, 61, 74-78)
- AFT events (6A-6F)
- System events (70, 8E, 8F)

## Appendix B: Long Poll Commands

A full listing of long poll commands organized by poll type (R, S, M, G) including:

- Enable/disable commands (01-0B)
- Meter reading commands (0F-47, 49-4A, 83)
- Configuration commands (08, 09, 2E)
- Validation commands (3D, 4C-4D, 50, 57-58, 70-71, 7B-7D)
- Information requests (51-56, 7E, 8E-90, 95-99)
- Progressive commands (80, 84-87)
- Tournament commands (8C)
- Bonusing commands (8A-8B)
- AFT commands (72-76)
- Authentication commands (6E)

## Appendix C: Game Data Tables

### Game Identification Codes

An extensive list of two-letter codes identifying game manufacturers and platforms (e.g., AC = American Coin, AT = Aristocrat, SS = IGT S-Plus slot).

### Denomination Table

A mapping of binary codes to denominations in cents (e.g., 01 = $0.01, 06 = $1.00, 0A = $100.00).

### Bill Acceptor Country Code Values

A mapping of BCD codes to countries (e.g., 01 = Argentina, 37 = United States).

### Bill Denomination Code Values

A mapping of BCD codes to bill denominations (e.g., 00 = $1, 06 = $50, 0A = $500).

### Meter Code Values

An extensive list of meter codes with values from 0000-FFFF, including:

- Basic meters (coin in, coin out, jackpot, etc.)
- Bill meters
- Ticket meters
- AFT-specific meters
- Validation-specific meters

## Appendix D: Figures

### Figure 1: Schematic for IGT fiber optic interface board

### Figure 2: Sample schematic for PT95A-to-machine interface board

## Glossary

Definitions of key terms used throughout the protocol, including:

- Credit meter terminology (restricted promotional credits, nonrestricted promotional credits, cashable credits, etc.)
- Game meter terminology (Total Coin In, Total Coin Out, Total Jackpot, etc.)
- Denomination terminology (accounting denomination, game credits, player/game denomination, token denomination)
- Technical terms (ACK, NACK, BCD, CRC, etc.)

---

this is a sample code in python that implements sas protocol. use this code as extra reference.

#!/usr/bin/python

# -_- coding: utf8 -_-

import bcd
import serial
import time
import binascii
#import string
from PyCRC.CRC16Kermit import CRC16Kermit
from array import array
#ser = serial.Serial('/dev/ttyS3','19200', timeout=1) # open first serial port
data_to_sent=[0x01, 0x21, 0x00, 0x00]
#adress=1
#print "OK"
meters = dict.fromkeys(('total_cancelled_credits_meter',
'total_in_meter',
'total_out_meter',
'total_in_meter',
'total_jackpot_meter',
'games_played_meter',
'games_won_meter',
'games_lost_meter',
'games_last_power_up',
'games_last_slot_door_close',
'slot_door_opened_meter',
'power_reset_meter',
's1_bills_accepted_meter',
's5_bills_accepted_meter',
's10_bills_accepted_meter',
's20_bills_accepted_meter',
's50_bills_accepted_meter',
's100_bills_accepted_meter',
's500_bills_accepted_meter',
's1000_bills_accepted_meter',
's200_bills_accepted_meter',
's25_bills_accepted_meter',
's2000_bills_accepted_meter',
's2500_bills_accepted_meter',
's5000_bills_accepted_meter',
's10000_bills_accepted_meter',
's20000_bills_accepted_meter',
's25000_bills_accepted_meter',
's50000_bills_accepted_meter',
's100000_bills_accepted_meter',
's250_bills_accepted_meter',
'cashout_ticket_number',
'cashout_amount_in_cents',
'ASCII_game_ID',
'ASCII_additional_ID',
'bin_denomination',
'bin_max_bet',
'bin_progressive_mode',
'bin_game_options',
'ASCII_paytable_ID',
'ASCII_base_percentage',
'bill_meter_in_dollars',
'ROM_signature',
'current_credits',
'bin_level',
'amount',
'partial_pay_amount',
'bin_reset_ID',
'bill_meter_in_dollars',
'true_coin_in',
'true_coin_out',
'current_hopper_level',
'credit_amount_of_all_bills_accepted',
'coin_amount_accepted_from_external_coin_acceptor',
'country_code',
'bill_denomination',
'meter_for_accepted_bills',
'number_bills_in_stacker',
'credits_SAS_in_stacker',
'machine_ID',
'sequence_number',
'validation_type',
'index_number',
'date_validation_operation',
'time_validation_operation',
'validation_number',
'ticket_amount',
'ticket_number',
'validation_system_ID',
'expiration_date_printed_on_ticket',
'pool_id',
'current_hopper_lenght',
'current_hopper_ststus',
'current_hopper_percent_full',
'current_hopper_level',
'bin_validation_type',
'total_validations',
'cumulative_amount',
'total_number_of_games_impemented',
'game_n_number',
'game_n_coin_in_meter',
'game_n_coin_out_meter',
'game_n_jackpot_meter',
'geme_n_games_played_meter',
'game_n_number_config',
'game_n_ASCII_game_ID',
'game_n_ASCII_additional_id',
'game_n_bin_denomination',
'game_n_bin_max_bet',
'game_n_bin_progressive_group',
'game_n_bin_game_options',
'game_n_ASCII_paytable_ID',
'game_n_ASCII_base_percentage',
'ASCII_SAS_version',
'ASCII_serial_number',
'selected_game_number',
'number_of_enabled_games',
'enabled_games_numbers',
'cashout_type',
'cashout_amount',
'ticket_status',
'ticket_amount',
'parsing_code',
'validation_data',
'registration_status',
'asset_number',
'registration_key',
'POS_ID',
'game_lock_status',
'avilable_transfers',
'host_cashout_status',
'AFT_ststus',
'max_buffer_index',
'current_cashable_amount',
'current_restricted_amount',
'current_non_restricted_amount',
'restricted_expiration',
'restricted_pool_ID',
'game_number',
'features_1',
'features_2',
'features_3'

                ),[])

aft_statement=dict.fromkeys((
'registration_status',
'asset_number',
'registration_key',
'POS_ID',
'transaction_buffer_position',
'transfer_status',
'receipt_status',
'transfer_type',
'cashable_amount',
'restricted_amount',
'nonrestricted_amount',
'transfer_flags',
'asset_number',
'transaction_ID_lenght',
'transaction_ID',
'transaction_date',
'transaction_time',
'expiration',
'pool_ID',
'cumulative_casable_amount_meter_size',
'cumulative_casable_amount_meter',
'cumulative_restricted_amount_meter_size',
'cumulative_restricted_amount_meter',  
 'cumulative_nonrestricted_amount_meter_size',
'cumulative_nonrestricted_amount_meter',
'asset_number',
'game_lock_status',
'avilable_transfers',
'host_cashout_status',
'AFT_status',
'max_buffer_index',
'current_cashable_amount',
'current_restricted_amount',
'current_non_restricted_amount',
'restricted_expiration',
'restricted_pool_ID',

        ),[])

tito_statement=dict.fromkeys((
'asset_number',
'status_bits',
'cashable_ticket_reciept_exp',
'restricted_ticket_exp',
'cashout_ticket_number',
'cashout_amount_in_cents',
'machine_ID',
'sequence_number'
'cashout_type',
'cashout_amount',
'validation_type',
'index_number',
'date_validation_operation',
'time_validation_operation',
'validation_number',
'ticket_amount',
'ticket_number',
'validation_system_ID',
'expiration_date_printed_on_ticket'
'pool_id'
),[])

eft_statement=dict.fromkeys((
'eft_status',
'promo_amount',
'cashable_amount',
'eft_transfer_counter'

        ),[])

game_features=dict.fromkeys((
'game_number',
'jackpot_multiplier',
'AFT_bonus_avards',
'legacy_bonus_awards',
'tournament',
'validation_extensions',
'validation_style',
'ticket_redemption'
),[])
class sas(object):
adress=1

        def __init__(self, port):
                try:
                        #print 1
                        self.connection=serial.Serial(port=port,baudrate=19200, timeout=2)
                except:
                        print "port error"
                return
        def start(self):
                print 'Connecting SAS...'
                while True:
                        response =self.connection.read(1)
                        if (response<>''):
                                self.adress=int(binascii.hexlify(response))
                                if self.adress>=1:
                                        print 'adress recognised '+str(self.adress)
                                        break

                        #print str(binascii.hexlifyself.adress))
                        time.sleep(.5)

                self.gaming_machine_ID()
                print meters.get('ASCII_game_ID')
                print meters.get('ASCII_additional_ID')
                print meters.get('bin_denomination')
                print meters.get('bin_max_bet')
                print meters.get('bin_progressive_mode')
                print meters.get('bin_game_options')
                print meters.get('ASCII_paytable_ID')
                print meters.get('ASCII_base_percentage')
                self.SAS_version_gaming_machine_serial_ID()
                print meters.get('ASCII_SAS_version')
                print meters.get('ASCII_serial_number')
                self.enabled_features() #todo

                # 7e date_time_add
                self.AFT_register_gaming_machine(reg_code=0xff)
                print aft_statement.get('registration_status')
                print aft_statement.get('asset_number')
                print aft_statement.get('registration_key')
                print aft_statement.get('POS_ID')




                return True

        def __send_command( self, command, no_response=False, timeout=3, crc_need=True):
                busy = True
                response=b''
                try:
                        buf_header=[self.adress]
                        buf_header.extend(command)
                        buf_count=len(command)
                        #buf_header[2]=buf_count+2
                        if (crc_need==True):
                                crc=CRC16Kermit().calculate(str(bytearray(buf_header)))
                                buf_header.extend([((crc>>8)&0xFF),(crc&0xFF)])
                        #print buf_header
                        print buf_header
                        #print self.connection.portstr
                        #self.connection.write([0x31, 0x32,0x33,0x34,0x35])
                        self.connection.write((buf_header))

                except Exception as e:
                        print e

                try:
                        buffer = []
                        self.connection.flushInput()
                        t=time.time()
                        while time.time()-t<timeout:
                                response +=self.connection.read()
                                #print binascii.hexlify(response)
                                if (self.checkResponse(response)<>False):
                                        break

                        if time.time()-t>=timeout:
                                print "timeout waiting response"
                                #buffer.append(response)
                                #print binascii.hexlify(bytearray(response))
                                return None

                        busy = False
                        return self.checkResponse(response)
                        #return None
                except Exception as e:
                        print e

                busy = False
                return None

        def checkResponse(self, rsp):
                if (rsp==''):
                        print 'not response'
                        return False

                resp = bytearray(rsp)
                #print resp
                if (resp[0]<>self.adress):
                        print "wrong ardess or NACK"
                        return False

                CRC = binascii.hexlify(resp[-2:])


                command = resp[0:-2]

                crc1=crc=CRC16Kermit().calculate(str(bytearray(command)))

                data = resp[1:-2]

                crc1 = hex(crc1).split('x')[-1]

                while len(crc1)<4:
                        crc1 = "0"+crc1

                #print crc1
                #print CRC
                if(CRC != crc1):

                            #print "Wrong response command hash " + str(CRC)
                            #print        "////" + str(hex(crc1).split('x')[-1])
                            #print        "////" + str(binascii.hexlify(command))
                            return False
                print binascii.hexlify(data)
                return data

## def check_crc(self):

## cmd=[0x01, 0x50, 0x81]

## cmd=bytearray(cmd)

## #print self.sas_CRC([0x01, 0x50, 0x81])

## #print ('\\'+'\\'.join(hex(e)[1:] for e in cmd))

##

## print (CRC16Kermit().calculate(str(cmd)))

## return

        def events_poll(self, timeout=1):
                event=''
                cmd=[0x80+self.adress]
                try:
                        self.connection.write(cmd)
                        t=time.time()
                        while time.time()-t<timeout:
                            #print "time"+ str(time.time()-t)
                                event =self.connection.read()
                                if event!='':
                                        break


                except Exception as e:
                        print e
                        return None
                return event


        def shutdown(self):
                #01
                #print "1"
                if (self.__send_command([0x01],True, crc_need=True)[0]==0x80+self.adress):
                        return "True"
                else:
                        return "False"
                return
        def startup(self, timeout=0.2):
                #02
                cmd=[self.adress, 0x02]
                try:
                        self.connection.write(cmd)
                        t=time.time()
                        while time.time()-t<timeout:
                            #print "time"+ str(time.time()-t)
                                event =self.connection.read()
                                if event!='':
                                        break


                except Exception as e:
                        print e
                        return None
                return event

        def sound_off(self):
                #03
                if (self.__send_command([0x03],True, crc_need=True)[0]==0x80+self.adress):
                        return "True"
                else:
                        return "False"
                return
        def sound_on(self):
                #04
                if (self.__send_command([0x04],True, crc_need=True)[0]==0x80+self.adress):
                        return "True"
                else:
                        return "False"
                return
        def reel_spin_game_sounds_disabled(self):
                #05
                if (self.__send_command([0x05],True, crc_need=True)[0]==0x80+self.adress):
                        return "True"
                else:
                        return "False"
                return
        def enable_bill_acceptor(self):
                #06
                if (self.__send_command([0x06],True, crc_need=True)[0]==0x80+self.adress):
                        return "True"
                else:
                        return "False"
                return
        def disable_bill_acceptor(self):
                #07
                if (self.__send_command([0x07],True, crc_need=True)[0]==0x80+self.adress):
                        return "True"
                else:
                        return "False"
                return
        def configure_bill_denom(self, bill_denom=[0xFF,0xFF,0xFF], action_flag=[0xff]):
                #08
                cmd=[0x08,0x00]
                ##print str(hex(bill_denom))
                s='00ffffff'
                #print bytes.fromhex(((s)))
                cmd.extend(bill_denom)
                cmd.extend(action_flag)
                print cmd
                if (self.__send_command(cmd,True, crc_need=True)[0]==0x80+self.adress):
                        return "True"
                else:
                        return "False"
                return
        def en_dis_game(self,  game_number=[1], en_dis=[1]):
                #09
                cmd=[0x09]
                cmd.extend(bytearray(game_number))
                cmd.extend(bytearray(en_dis))
                print cmd
                if (self.__send_command(cmd,True, crc_need=True)[0]==0x80+self.adress):
                        return "True"
                else:
                        return "False"

                return
        def enter_maintenance_mode(self):
                #0A
                return
        def exit_maintanance_mode(self):
                #0B
                return
        def en_dis_rt_event_reporting(self):
                #0E
                return
        def send_meters_10_15(self):
                #0F
                cmd=[0x0f]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):
                        meters['total_cancelled_credits_meter']=int((binascii.hexlify(bytearray(data[1:5]))))
                        meters['total_in_meter']=int(binascii.hexlify(bytearray(data[5:9])))
                        meters['total_out_meter']=int(binascii.hexlify(bytearray(data[9:13])))
                        meters['total_droup_meter']=int(binascii.hexlify(bytearray(data[13:17])))
                        meters['total_jackpot_meter']=int(binascii.hexlify(bytearray(data[17:21])))
                        meters['games_played_meter']=int(binascii.hexlify(bytearray(data[21:25])))
                        return data
                return ''
        def total_cancelled_credits(self):
                #10
                cmd=[0x10]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):
                        meters['total_cancelled_credits_meter']=int(binascii.hexlify(bytearray(data[1:5])))
                        return data
                return ''
        def total_bet_meter(self):
                #11
                cmd=[0x11]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['total_bet_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def total_win_meter(self):
                #12
                cmd=[0x12]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['total_win_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def total_in_meter(self):
                #13
                cmd=[0x13]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['total_in_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def total_jackpot_meter(self):
                #14
                cmd=[0x14]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['total_jackpot_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def games_played_meter(self):
                #15
                cmd=[0x15]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['games_played_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def games_won_meter(self):
                #16
                cmd=[0x16]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['games_won_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def games_lost_meter(self):
                #17
                cmd=[0x17]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['games_lost_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def games_powerup_door_opened(self):
                #18
                cmd=[0x18]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['games_last_power_up']=int(binascii.hexlify(bytearray(data[1:3])))
                        meters['games_last_slot_door_close']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def meters_11_15(self):
                #19
                cmd=[0x19]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):
                        meters['total_bet_meter']=int(binascii.hexlify(bytearray(data[1:5])))
                        meters['total_win_meter']=int(binascii.hexlify(bytearray(data[5:9])))
                        meters['total_in_meter']=int(binascii.hexlify(bytearray(data[9:13])))
                        meters['total_jackpot_meter']=int(binascii.hexlify(bytearray(data[13:17])))
                        meters['games_played_meter']=int(binascii.hexlify(bytearray(data[17:21])))
                        return data
                return ''
        def current_credits(self):
                #1A
                cmd=[0x1A]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):
                        meters['current_credits']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def handpay_info(self):
                #1B
                cmd=[0x1B]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['bin_progressive_group']=int(binascii.hexlify(bytearray(data[1:2])))
                        meters['bin_level']=int(binascii.hexlify(bytearray(data[2:3])))
                        meters['amount']=int(binascii.hexlify(bytearray(data[3:8])))
                        meters['bin_reset_ID']=int(binascii.hexlify(bytearray(data[8:])))
                        return data
                return ''
        def meters(self):
                #1C
                cmd=[0x1C]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):
                        meters['total_bet_meter']=int(binascii.hexlify(bytearray(data[1:5])))
                        meters['total_win_meter']=int(binascii.hexlify(bytearray(data[5:9])))
                        meters['total_in_meter']=int(binascii.hexlify(bytearray(data[9:13])))
                        meters['total_jackpot_meter']=int(binascii.hexlify(bytearray(data[13:17])))
                        meters['games_played_meter']=int(binascii.hexlify(bytearray(data[17:21])))
                        meters['games_won_meter']=int(binascii.hexlify(bytearray(data[21:25])))
                        meters['slot_door_opened_meter']=int(binascii.hexlify(bytearray(data[25:29])))
                        meters['power_reset_meter']=int(binascii.hexlify(bytearray(data[29:33])))

                        return data
                return ''
        def total_bill_meters(self):
                #1E
                cmd=[0x1E]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):
                        meters['s1_bills_accepted_meter']=int(binascii.hexlify(bytearray(data[1:5])))
                        meters['s5_bills_accepted_meter']=int(binascii.hexlify(bytearray(data[5:9])))
                        meters['s10_bills_accepted_meter']=int(binascii.hexlify(bytearray(data[9:13])))
                        meters['s20_bills_accepted_meter']=int(binascii.hexlify(bytearray(data[13:17])))
                        meters['s50_bills_accepted_meter']=int(binascii.hexlify(bytearray(data[17:21])))
                        meters['s100_bills_accepted_meter']=int(binascii.hexlify(bytearray(data[21:25])))

                        return data
                return ''
        def gaming_machine_ID(self):
                #1F
                cmd=[0x1F]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['ASCII_game_ID']=(((data[1:3])))
                        meters['ASCII_additional_ID']=(((data[3:6])))
                        meters['bin_denomination']=int(binascii.hexlify(bytearray(data[6])))
                        meters['bin_max_bet']=(binascii.hexlify(bytearray(data[7:8])))
                        meters['bin_progressive_mode']=int(binascii.hexlify(bytearray(data[8:9])))
                        meters['bin_game_options']=(binascii.hexlify(bytearray(data[9:11])))
                        meters['ASCII_paytable_ID']=(((data[11:17])))
                        meters['ASCII_base_percentage']=(((data[17:21])))

                        return data
                return ''
        def total_dollar_value_of_bills_meter(self):
                #20

                cmd=[0x20]
                data=self.__send_command(cmd,True, crc_need=False)

                if(data<>''):

                        meters['bill_meter_in_dollars']=int(binascii.hexlify(bytearray(data[1:])))

                        return data
                return ''
        def ROM_signature_verification(self):
                #21

                cmd=[0x21, 0x00, 0x00]
                data=self.__send_command(cmd,True, crc_need=True)
                print data
                if(data<>None):

                        meters['ROM_signature']= int(binascii.hexlify(bytearray(data[1:3])))
                        print (str(meters.get('ROM_signature')))
                        return data
                return False

        def eft_button_pressed(self, state=0):
                #24

                cmd=[0x24, 0x03]
                cmd.append(state)

                data=self.__send_command(cmd,True, crc_need=True)
                print data
                if(data<>None):

                        return data
                return ''

        def true_coin_in(self):
                #2A
                cmd=[0x2A]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['true_coin_in']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def true_coin_out(self):
                #2B
                cmd=[0x2B]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['true_coin_out']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def curr_hopper_level(self):
                #2C
                cmd=[0x2C]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['current_hopper_level']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def total_hand_paid_cancelled_credit(self):
                #2D
                return
        def delay_game(self, delay=0x01):
                #2E
                cmd=[0x2E]

## if (delay[0]<=0xff):

## cmd.extend([0x00])

                cmd.append(delay)


                #print cmd
                if (self.__send_command(cmd,True, crc_need=True)[0]==self.adress):
                        return "True"
                else:
                        return "False"

                return
        def selected_meters_for_game(self):
                #2F
                return
        def send_1_bills_in_meters(self):
                #31
                cmd=[0x31]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['s1_bills_in_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def send_2_bills_in_meters(self):
                #32
                cmd=[0x32]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['s2_bills_in_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def send_5_bills_in_meters(self):
                #33
                cmd=[0x33]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['s5_bills_in_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def send_10_bills_in_meters(self):
                #34
                cmd=[0x34]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['s10_bills_in_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def send_20_bills_in_meters(self):
                #35
                cmd=[0x35]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['s20_bills_in_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def send_50_bills_in_meters(self):
                #36
                cmd=[0x36]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['s50_bills_in_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def send_100_bills_in_meters(self):
                #37
                cmd=[0x37]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['s100_bills_in_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def send_500_bills_in_meters(self):
                #38
                cmd=[0x38]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['s500_bills_in_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def send_1000_bills_in_meters(self):
                #39
                cmd=[0x39]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['s1000_bills_in_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def send_200_bills_in_meters(self):
                #3A
                cmd=[0x3a]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['s200_bills_in_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def send_25_bills_in_meters(self):
                #3B
                cmd=[0x3B]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['s25_bills_in_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def send_2000_bills_in_meters(self):
                #3C
                cmd=[0x3C]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['s2000_bills_in_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def cash_out_ticket_info(self):
                #3D
                cmd=[0x3D]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        tito_statement['cashout_ticket_number']=int(binascii.hexlify(bytearray(data[1:3])))
                        tito_statement['cashout_amount_in_cents']=int(binascii.hexlify(bytearray(data[3:])))

                        return data
                return ''
        def send_2500_bills_in_meters(self):
                #3E
                cmd=[0x3E]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['s2500_bills_in_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def send_5000_bills_in_meters(self):
                #3F
                cmd=[0x3F]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['s5000_bills_in_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def send_10000_bills_in_meters(self):
                #40
                cmd=[0x40]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['s10000_bills_in_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def send_20000_bills_in_meters(self):
                #41
                cmd=[0x41]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['s20000_bills_in_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def send_25000_bills_in_meters(self):
                #42
                cmd=[0x42]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['s25000_bills_in_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def send_50000_bills_in_meters(self):
                #43
                cmd=[0x43]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['s50000_bills_in_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def send_100000_bills_in_meters(self):
                #44
                cmd=[0x44]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['s100000_bills_in_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def send_250_bills_in_meters(self):
                #45
                cmd=[0x45]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['s250_bills_in_meter']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def credit_amount_of_all_bills_accepted(self):
                #46

                cmd=[0x46]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>''):

                        meters['credit_amount_of_all_bills_accepted']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def coin_amount_accepted_from_external_coin_acceptor(self):
                #47
                cmd=[0x47]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>None):

                        meters['coin_amount_accepted_from_external_coin_acceptor']=int(binascii.hexlify(bytearray(data[1:5])))

                        return data
                return ''
        def last_accepted_bill_info(self):
                #48
                cmd=[0x48]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>None):
                        meters['country_code']=int(binascii.hexlify(bytearray(data[1:2])))
                        meters['bill_denomination']=int(binascii.hexlify(bytearray(data[2:3])))
                        meters['meter_for_accepted_bills']=int(binascii.hexlify(bytearray(data[3:6])))
                        return data
                return ''
        def number_of_bills_currently_in_stacker(self):
                #49
                cmd=[0x49]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>None):
                        meters['number_bills_in_stacker']=int(binascii.hexlify(bytearray(data[1:5])))
                        return data
                return ''
        def total_credit_amount_of_all_bills_in_stacker(self):
                #4A
                cmd=[0x49]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>None):
                        meters['credits_SAS_in_stacker']=int(binascii.hexlify(bytearray(data[1:5])))
                        return data
                return ''
        def set_secure_enhanced_validation_ID(self, MachineID=[0x01,0x01,0x01], seq_num=[0x00,0x00,0x01]):
                #4C
                cmd=[0x4C]

                cmd.extend(MachineID)
                cmd.extend(seq_num)
                cmd=bytearray(cmd)
                #print str(binascii.hexlify((cmd)))
                data=self.__send_command(cmd,True, crc_need=True)
                if(data<>None):
                        tito_statement['machine_ID']=int(binascii.hexlify(bytearray(data[1:4])))
                        tito_statement['sequence_number']=int(binascii.hexlify(bytearray(data[4:8])))

                        return data
                return ''
        def enhanced_validation_information(self, curr_validation_info=0):
                #4D

                cmd=[0x4D]

                #cmd.append(transfer_code)
                #cmd=cmd.extend(0)
                #rint str(binascii.hexlify(bytearray(cmd)))
                cmd.append((curr_validation_info))
                data=self.__send_command(cmd,True, crc_need=True)
                if(data<>None):
                        tito_statement['validation_type']=int(binascii.hexlify(bytearray(data[1:2])))
                        tito_statement['index_number']=int(binascii.hexlify(bytearray(data[2:3])))
                        tito_statement['date_validation_operation']=str(binascii.hexlify(bytearray(data[3:7])))
                        tito_statement['time_validation_operation']=str(binascii.hexlify(bytearray(data[7:10])))
                        tito_statement['validation_number']=str(binascii.hexlify(bytearray(data[10:18])))
                        tito_statement['ticket_amount']=int(binascii.hexlify(bytearray(data[18:23])))
                        tito_statement['ticket_number']=int(binascii.hexlify(bytearray(data[23:25])))
                        tito_statement['validation_system_ID']=int(binascii.hexlify(bytearray(data[25:26])))
                        tito_statement['expiration_date_printed_on_ticket']=str(binascii.hexlify(bytearray(data[26:30])))
                        tito_statement['pool_id']=int(binascii.hexlify(bytearray(data[30:32])))


                        return data
                return ''
        def current_hopper_status(self):
                #4F

                cmd=[0x4F]

                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>None):
                        meters['current_hopper_lenght']=int(binascii.hexlify(bytearray(data[1:2])))
                        meters['current_hopper_ststus']=int(binascii.hexlify(bytearray(data[2:3])))
                        meters['current_hopper_percent_full']=int(binascii.hexlify(bytearray(data[3:4])))
                        meters['current_hopper_level']=int(binascii.hexlify(bytearray(data[4:])))
                        return data
                return ''
        def validation_meters(self, type_of_validation=0x00):
                #50

                cmd=[0x50]
                cmd.append(type_of_validation)
                data=self.__send_command(cmd,True, crc_need=True)
                if(data<>None):
                        meters['bin_validation_type']=int(binascii.hexlify(bytearray(data[1])))
                        meters['total_validations']=int(binascii.hexlify(bytearray(data[2:6])))
                        meters['cumulative_amount']=str(binascii.hexlify(bytearray(data[6:])))

                        return data
                return ''
        def total_number_of_games_impimented(self):
                #51
                cmd=[0x51]
                cmd.extend(type_of_validation)
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>None):
                        meters['total_number_of_games_impemented']=str(binascii.hexlify(bytearray(data[1:])))


                        return data
                return ''
        def game_meters(self, n=1):
                #52

                cmd=[0x52]
                cmd.extend([(n&0xFF), ((n>>8)&0xFF)])

                data=self.__send_command(cmd,True, crc_need=True)
                if(data<>None):
                        meters['game_n_number']=str(binascii.hexlify(bytearray(data[1:3])))
                        meters['game_n_coin_in_meter']=str(binascii.hexlify(bytearray(data[3:7])))
                        meters['game_n_coin_out_meter']=str(binascii.hexlify(bytearray(data[7:11])))
                        meters['game_n_jackpot_meter']=str(binascii.hexlify(bytearray(data[11:15])))
                        meters['geme_n_games_played_meter']=str(binascii.hexlify(bytearray(data[15:])))


                        return data
                return ''
        def game_configuration(self, n=1):
                #53

                cmd=[0x53]
                cmd.extend([(n&0xFF), ((n>>8)&0xFF)])

                data=self.__send_command(cmd,True, crc_need=True)
                if(data<>None):
                        meters['game_n_number_config']=int(binascii.hexlify(bytearray(data[1:3])))
                        meters['game_n_ASCII_game_ID']=str(binascii.hexlify(bytearray(data[3:5])))
                        meters['game_n_ASCII_additional_id']=str(binascii.hexlify(bytearray(data[5:7])))
                        meters['game_n_bin_denomination']=str(binascii.hexlify(bytearray(data[7])))
                        meters['game_n_bin_progressive_group']=str(binascii.hexlify(bytearray(data[8])))
                        meters['game_n_bin_game_options']=str(binascii.hexlify(bytearray(data[9:11])))
                        meters['game_n_ASCII_paytable_ID']=str(binascii.hexlify(bytearray(data[11:17])))
                        meters['game_n_ASCII_base_percentage']=str(binascii.hexlify(bytearray(data[17:])))


                        return data
                return ''
        def SAS_version_gaming_machine_serial_ID(self):
                #54
                cmd=[0x54]

                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>None):
                        meters['ASCII_SAS_version']=data[2:5]
                        meters['ASCII_serial_number']=data[5:]
                        return data
                return ''
        def selected_game_number(self):
                #55
                cmd=[0x55]

                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>None):
                        meters['selected_game_number']=int(binascii.hexlify(bytearray(data[1:])))
                        return data
                return ''
        def enabled_game_numbers(self):
                #56

                cmd=[0x56]

                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>None):
                        meters['number_of_enabled_games']=int(binascii.hexlify(bytearray(data[2])))
                        meters['enabled_games_numbers']=int(binascii.hexlify(bytearray(data[3:])))

                        return data
                return ''
        def pending_cashout_info(self):
                #57

                cmd=[0x57]

                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>None):
                        tito_statement['cashout_type']=int(binascii.hexlify(bytearray(data[1:2])))
                        tito_statement['cashout_amount']=str(binascii.hexlify(bytearray(data[2:])))

                        return data
                return ''
        def validation_number(self, validationID=1, valid_number=0):
                #58

                cmd=[0x58]
                cmd.append(validationID)
                cmd.extend(self.bcd_coder_array( valid_number,8))
                print cmd
                data=self.__send_command(cmd,True, crc_need=True)
                if(data<>None):

                    return data[1]
                return ''
        def eft_send_promo_to_machine(self, amount=0, count=1, status=0):
                #63
                cmd=[0x63, count, ]
                #status 0-init 1-end
                cmd.append(status)
                cmd.extend(self.bcd_coder_array(amount, 4))
                data=self.__send_command(cmd,True, crc_need=True)

                if(data<>None):
                        eft_statement['eft_status']=str(binascii.hexlify(bytearray(data[1:])))
                        eft_statement['promo_amount']=str(binascii.hexlify(bytearray(data[4:])))
                       # eft_statement['eft_transfer_counter']=int(binascii.hexlify(bytearray(data[3:4])))


                        return data[3]
                return ''
        def eft_load_cashable_credits(self, amount=0, count=1, status=0):
                #69
                cmd=[0x69, count, ]
                cmd.append(status)
                cmd.extend(self.bcd_coder_array(amount, 4))
                data=self.__send_command(cmd,True, crc_need=True)

                if(data<>None):
                        meters['eft_status']=str(binascii.hexlify(bytearray(data[1:2])))
                        meters['cashable_amount']=str(binascii.hexlify(bytearray(data[2:5])))


                        return data[3]
                return ''

        def eft_avilable_transfers(self):
                #6A
                cmd=[0x6A]
                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>None):
                        #meters['number_bills_in_stacker']=int(binascii.hexlify(bytearray(data[1:5])))
                        return data
                return ''


        def autentification_info(self, action=0, adressing_mode=0, component_name='', auth_method=b'\x00\x00\x00\x00', seed_lenght=0, seed='', offset_lenght=0, offset=''):
                #6E
                cmd=[0x6E, 0x00]
                cmd.append(action)
                if action==0:
                        #cmd.append(action)
                        cmd[1]=1
                else:
                        if (action==1 or action==3):
                                cmd.append(adressing_mode)
                                cmd.append(len(bytearray(component_name)))
                                cmd.append (bytearray(component_name))
                                cmd[1]=len(bytearray(component_name))+3
                        else:
                                if action==2:
                                        cmd.append(adressing_mode)
                                        cmd.append(len(bytearray(component_name)))
                                        cmd.append (bytearray(component_name))
                                        cmd.append(auth_metod)
                                        cmd.append(seed_lenght)
                                        cmd.append(bytearray(seed))
                                        cmd.append(offset_lenght)
                                        cmd.append(bytearray(offset))

                                        cmd[1]=len(bytearray(offset))+len(bytearray(seed))+len(bytearray(component_name))+6


                data=self.__send_command(cmd,True, crc_need=True)
                if(data<>None):

                    return data[1]
                return ''
        def extended_meters_for_game(self, n=1):
                #6F
                return
        def ticket_validation_data(self):
                #70

                cmd=[0x70]

                data=self.__send_command(cmd,True, crc_need=False)
                if(data<>None):
                        meters['ticket_status']=int(binascii.hexlify(bytearray(data[2:3])))
                        meters['ticket_amount']=str(binascii.hexlify(bytearray(data[3:8])))
                        meters['parsing_code']=int(binascii.hexlify(bytearray(data[8:9])))
                        meters['validation_data']=str(binascii.hexlify(bytearray(data[9:])))


                        return data[1]
                return ''
        def redeem_ticket(self, transfer_code=0, transfer_amount=0, parsing_code=0, validation_data=0, rescticted_expiration=0, pool_ID=0):
                #71

                cmd=[0x71, 0x00]
                cmd.append(transfer_code)
                cmd.extend(self.bcd_coder_array(transfer_amount, 5))
                cmd.append(parsing_code)

                cmd.extend(self.bcd_coder_array(validation_data, 8))
                cmd.extend(self.bcd_coder_array(rescticted_expiration, 4))
                cmd.extend(self.bcd_coder_array(pool_ID,2))
                cmd[1]=8+13

                data=self.__send_command(cmd,True, crc_need=True)
                if(data<>None):
                        meters['ticket_status']=int(binascii.hexlify(bytearray(data[2:3])))
                        meters['ticket_amount']=int(binascii.hexlify(bytearray(data[3:8])))
                        meters['parsing_code']=int(binascii.hexlify(bytearray(data[8:9])))
                        meters['validation_data']=str(binascii.hexlify(bytearray(data[9:])))


                        return data[1]
                return ''
        def AFT_transfer_funds(self, transfer_code=0x00, transaction_index=0x00, transfer_type=0x00, cashable_amount=0, restricted_amount=0, non_restricted_amount=0, transfer_flags=0x00, asset_number=b'\x00\x00\x00\x00\x00', registration_key=0, transaction_ID_lenght=0x00, transaction_ID='', expiration=0, pool_ID=0, reciept_data='', lock_timeout=0):
                #72

#sas.AFT_transfer_funds(0, 1, 0x60, 10000, 0, 0, 0b00000000,)
cmd=[0x72, 0x00]
cmd.append(transfer_code)
cmd.append(transaction_index)
cmd.append(transfer_type)
cmd.extend(self.bcd_coder_array(cashable_amount, 5))
cmd.extend(self.bcd_coder_array(restricted_amount, 5))
cmd.extend(self.bcd_coder_array(non_restricted_amount, 5))
cmd.append(transfer_flags)
cmd.extend((asset_number))
cmd.extend(self.bcd_coder_array(registration_key, 20))
cmd.append(len(transaction_ID))
cmd.extend(transaction_ID)
cmd.extend(self.bcd_coder_array(expiration, 4))
cmd.extend(self.bcd_coder_array(pool_ID, 2))

                cmd.append(len(reciept_data))
                cmd.extend(reciept_data)
                cmd.extend(self.bcd_coder_array(lock_timeout,2))

                cmd[1]=len(transaction_ID)+len(transaction_ID)+53

                data=self.__send_command(cmd,True, crc_need=True)
                if(data<>None):
                        aft_statement['transaction_buffer_position']=int(binascii.hexlify(bytearray(data[2:3])))
                        aft_statement['transfer_status']=int(binascii.hexlify(bytearray(data[3:4])))
                        aft_statement['receipt_status']=int(binascii.hexlify(bytearray(data[4:5])))
                        aft_statement['transfer_type']=int(binascii.hexlify(bytearray(data[5:6])))
                        aft_statement['cashable_amount']=int(binascii.hexlify(bytearray(data[6:11])))
                        aft_statement['restricted_amount']=int(binascii.hexlify(bytearray(data[11:16])))
                        aft_statement['nonrestricted_amount']=int(binascii.hexlify(bytearray(data[16:21])))
                        aft_statement['transfer_flags']=int(binascii.hexlify(bytearray(data[21:22])))
                        aft_statement['asset_number']=(binascii.hexlify(bytearray(data[22:26])))
                        aft_statement['transaction_ID_lenght']=int(binascii.hexlify(bytearray(data[26:27])))
                        a=int(binascii.hexlify(bytearray(data[26:27])))
                        aft_statement['transaction_ID']=str(binascii.hexlify(bytearray(data[27:(27+a+1)])))
                        a=27+a+1
                        aft_statement['transaction_date']=str(binascii.hexlify(bytearray(data[a:a+5])))
                        a=a+5
                        aft_statement['transaction_time']=str(binascii.hexlify(bytearray(data[a:a+4])))
                        aft_statement['expiration']=str(binascii.hexlify(bytearray(data[a+4:a+9])))
                        aft_statement['pool_ID']=str(binascii.hexlify(bytearray(data[a+9:a+11])))
                        aft_statement['cumulative_casable_amount_meter_size']=(binascii.hexlify(bytearray(data[a+11:a+12])))
                        b=a+int(binascii.hexlify(bytearray(data[a+11:a+12])))
                        aft_statement['cumulative_casable_amount_meter']=(binascii.hexlify(bytearray(data[a+12:b+1])))
                        aft_statement['cumulative_restricted_amount_meter_size']=(binascii.hexlify(bytearray(data[b+1:b+2])))
                        c=b+2+int(binascii.hexlify(bytearray(data[b+1:b+2])))
                        aft_statement['cumulative_restricted_amount_meter']=(binascii.hexlify(bytearray(data[b+2:c])))
                        aft_statement['cumulative_nonrestricted_amount_meter_size']=(binascii.hexlify(bytearray(data[c:c+1])))
                        b=int(binascii.hexlify(bytearray(data[c:c+1])))+c
                        aft_statement['cumulative_nonrestricted_amount_meter']=(binascii.hexlify(bytearray(data[c+1:])))


                        return data[1]
                return ''
        def AFT_register_gaming_machine(self, reg_code=0xff, asset_number=0, reg_key=0, POS_ID=b'\x00\x00\x00\x00'):
                #73
                cmd=[0x73, 0x00]
                if reg_code==0xFF:
                        cmd.append(reg_code)
                        cmd[1]=1

                else:
                        cmd.append(reg_code)
                        cmd.extend(self.bcd_coder_array(asset_number, 4))
                        cmd.extend(self.bcd_coder_array(reg_key, 20))
                        cmd.extend(self.bcd_coder_array(POS_ID, 4))
                        cmd[1]=0x1D
                data=self.__send_command(cmd,True, crc_need=True)
                if(data<>None):
                        print len(data)
                        aft_statement['registration_status']=(binascii.hexlify((data[2:3])))
                        aft_statement['asset_number']=bytearray(data[3:7])
                        aft_statement['registration_key']=bytearray(data[7:27])
                        aft_statement['POS_ID']=str(binascii.hexlify((data[27:])))
                        return data[1]
                return ''
        def AFT_game_lock_and_status_request(self, lock_code=0x00, transfer_condition=0b00000000, lock_timeout=0):
                #74
                cmd=[0x74]

                cmd.append(lock_code)
                cmd.append(transfer_condition)
                cmd.extend(self.bcd_coder_array(lock_timeout, 2))
                #cmd.addend(0x23)

                data=self.__send_command(cmd,True, crc_need=True)
                if(data<>None):
                        aft_statement['asset_number']=str(binascii.hexlify(bytearray(data[2:6])))
                        aft_statement['game_lock_status']=str(binascii.hexlify(bytearray(data[6:7])))
                        aft_statement['avilable_transfers']=str(binascii.hexlify(bytearray(data[7:8])))
                        aft_statement['host_cashout_status']=str(binascii.hexlify(bytearray(data[8:9])))
                        aft_statement['AFT_status']=str(binascii.hexlify(bytearray(data[9:10])))
                        aft_statement['max_buffer_index']=str(binascii.hexlify(bytearray(data[10:11])))
                        aft_statement['current_cashable_amount']=str(binascii.hexlify(bytearray(data[11:16])))
                        aft_statement['current_restricted_amount']=str(binascii.hexlify(bytearray(data[16:21])))
                        aft_statement['current_non_restricted_amount']=str(binascii.hexlify(bytearray(data[21:26])))
                        aft_statement['restricted_expiration']=str(binascii.hexlify(bytearray(data[26:29])))
                        aft_statement['restricted_pool_ID']=str(binascii.hexlify(bytearray(data[29:31])))

                        return data[1]
                return ''
        def set_AFT_reciept_data(self):
                #75
                return
        def set_custom_AFT_ticket_data(self):
                #76
                return
        def exnended_validation_status(self, control_mask=[0,0], status_bits=[0,0], cashable_ticket_reciept_exp=0, restricted_ticket_exp=0):
                #7B
                cmd=[0x7B, 0x08]

                cmd.extend(control_mask)
                cmd.extend(status_bits)
                cmd.extend(self.bcd_coder_array(cashable_ticket_reciept_exp, 2))
                cmd.extend(self.bcd_coder_array(restricted_ticket_exp, 2))

                #cmd.addend(0x23)


                data=self.__send_command(cmd,True, crc_need=True)
                if(data<>None):
                        aft_statement['asset_number']=str(binascii.hexlify(bytearray(data[2:6])))
                        aft_statement['status_bits']=str(binascii.hexlify(bytearray(data[6:8])))
                        aft_statement['cashable_ticket_reciept_exp']=str(binascii.hexlify(bytearray(data[8:10])))
                        aft_statement['restricted_ticket_exp']=str(binascii.hexlify(bytearray(data[10:])))

                        return data[1]
                return ''
        def set_extended_ticket_data(self):
                #7C
                return
        def set_ticket_data(self):
                #7D
                return
        def current_date_time(self):
                #7E
                return
        def recieve_date_time(self):
                #7F
                return
        def recieve_progressive_amount(self):
                #80
                return
        def cumulative_progressive_wins(self):
                #83
                return
        def progressive_win_amount(self):
                #84
                return
        def SAS_progressive_win_amount(self):
                #85
                return
        def recieve_multiple_progressive_levels(self):
                #86
                return
        def multiple_SAS_progresive_win_amounts(self):
                #87
                return
        def initiate_legacy_bonus_pay(self):
                #8A
                return
        def initiate_multiplied_jackpot_mode(self):
                #8B
                return
        def enter_exit_tournament_mode(self):
                #8C
                return
        def card_info(self):
                #8E
                return
        def physical_reel_stop_info(self):
                #8F
                return
        def legacy_bonus_win_info(self):
                #90
                return
        def remote_handpay_reset(self):
                #94
                return
        def tournament_games_played(self):
                #95
                return
        def tournament_games_won(self):
                #96
                return
        def tournament_credits_wagered(self):
                #97
                return
        def tournament_credits_won(self):
                #98
                return
        def meters_95_98(self):
                #99
                return
        def legacy_bonus_meters(self):
                #9A
                return
        def enabled_features(self, game_nimber=0):
                #A0
                cmd=[0xA0]

                cmd.extend(self.bcd_coder_array(game_nimber, 2))

                data=self.__send_command(cmd,True, crc_need=True)
                if(data<>None):
                        aft_statement['game_number']=str(binascii.hexlify(bytearray(data[1:3])))
                        aft_statement['features_1']=data[3]
                        aft_statement['features_2']=data[4]
                        aft_statement['features_3']=data[5]

                        game_features['game_number']=aft_statement.get('game_number')
                        if (data[3]&0b00000001):
                                game_features['jackpot_multiplier']=1
                        else:
                                game_features['jackpot_multiplier']=0

                        if (data[3]&0b00000010):
                                game_features['AFT_bonus_avards']=1
                        else:
                                game_features['AFT_bonus_avards']=0
                        if (data[3]&0b00000100):
                                game_features['legacy_bonus_awards']=1
                        else:
                                game_features['legacy_bonus_awards']=0
                        if (data[3]&0b00001000):
                                game_features['tournament']=1
                        else:
                                game_features['tournament']=0
                        if (data[3]&0b00010000):
                                game_features['validation_extensions']=1
                        else:
                                game_features['validation_extensions']=0

                        game_features['validation_style']=data[3]&0b01100000>>5

                        if (data[3]&0b10000000):
                                game_features['ticket_redemption']=1
                        else:
                                game_features['ticket_redemption']=0




                        return data[1]
                return ''
        def cashout_limit(self):
                #A4
                return
        def enable_jackpot_handpay_reset_method(self):
                #A8
                return
        def en_dis_game_auto_rebet(self):
                #AA
                return
        def extended_meters_game_alt(self,n=1):
                #AF
                return
        def multi_denom_preamble(self):
                #B0
                return
        def current_player_denomination(self):
                #B1
                return
        def enabled_player_denominations(self):
                #B2
                return
        def token_denomination(self):
                #B3
                return
        def wager_category_info(self):
                #B4
                return
        def extended_game_info(self,n=1):
                #B5
                return
        def event_response_to_long_poll(self):
                #FF
                return
        def bcd_coder_array(self, value=0, lenght=4):
                return self.int_to_bcd(value, lenght)


        def int_to_bcd(self, number=0, lenght=5):
                n=0
                m=0
                bval=0
                p=lenght-1
                result=[]
                for i in range(0, lenght):
                        result.extend([0x00])
                while (p>=0):
                        if (number!=0):
                                digit=number%10
                                number=number/10
                                m=m+1
                        else:
                                digit=0
                        if (n&1):
                                bval |= digit<<4
                                result[p]=bval
                                p=p-1
                                bval=0
                        else:
                                bval=digit
                        n=n+1
                return result



if **name** =="**main**":
print "OK"
sas=sas('/dev/ttyS3')
#print ( bcd.bcd_to_int(100))
#print int(bcd.int_to_bcd(0x1467))
#a=sas.bcd_coder_array(value=100, lenght=10)
#print ((a))
print sas.int_to_bcd(1234567890365421,8)
#sas.start()
#sas.ROM_signature_verification()
#sas.total_cancelled_credits()
#sas.send_meters_10_15()
#sas.total_bet_meter()
#sas.total_win_meter()
#sas.total_in_meter()
#sas.total_jackpot_meter()

        #sas.SAS_version_gaming_machine_serial_ID()

## sas.start( )

##

##

##

##

# print sas.events_poll( timeout=1)

##

##

##

## sas.shutdown( )

##

## sas.startup( )

##

## sas.sound_off( )

##

## sas.sound_on( )

##

## sas.reel_spin_game_sounds_disabled( )

##

## sas.enable_bill_acceptor( )

##

## sas.disable_bill_acceptor( )

##

## sas.configure_bill_denom( , bill_denom=[0xFF,0xFF,0xFF], action_flag=[0xff])

##

## sas.en_dis_game( , game_number=[1], en_dis=[1])

##

## sas.enter_maintenance_mode( )

##

## sas.exit_maintanance_mode( )

##

## sas.en_dis_rt_event_reporting( )

##

## sas.send_meters_10_15( )

##

## sas.total_cancelled_credits( )

##

## sas.total_bet_meter( )

##

## sas.total_win_meter( )

##

## sas.total_in_meter( )

##

## sas.total_jackpot_meter( )

##

# sas.games_played_meter( )

##

# sas.games_won_meter( )

##

# sas.games_lost_meter( )

##

# sas.games_powerup_door_opened( )

##

# sas.meters_11_15( )

##

# sas.current_credits( )

##

# sas.handpay_info( )

##

# sas.meters( )

##

# sas.total_bill_meters( )

##

# sas.gaming_machine_ID( )

##

# sas.total_dollar_value_of_bills_meter( )

##

# sas.ROM_signature_verification( ) # test usage?

##

# sas.true_coin_in( )

##

# sas.true_coin_out( )

##

# sas.curr_hopper_level( )

##

# sas.total_hand_paid_cancelled_credit( ) #need for maid

##

# sas.delay_game( delay=1) # need to test

##

# sas.selected_meters_for_game( ) #need to maid

##

# sas.send_1_bills_in_meters( )

##

# sas.send_2_bills_in_meters( )

##

# sas.send_5_bills_in_meters( )

##

# sas.send_10_bills_in_meters( )

##

# sas.send_20_bills_in_meters( )

##

# sas.send_50_bills_in_meters( )

##

# sas.send_100_bills_in_meters( )

##

# sas.send_500_bills_in_meters( )

##

# sas.send_1000_bills_in_meters( )

##

# sas.send_200_bills_in_meters( )

##

# sas.send_25_bills_in_meters( )

##

# sas.send_2000_bills_in_meters( )

##

# sas.cash_out_ticket_info( )

##

# sas.send_2500_bills_in_meters( )

##

# sas.send_5000_bills_in_meters( )

##

# sas.send_10000_bills_in_meters( )

##

# sas.send_20000_bills_in_meters( )

##

# sas.send_25000_bills_in_meters( )

##

# sas.send_50000_bills_in_meters( )

##

# sas.send_100000_bills_in_meters( )

##

# sas.send_250_bills_in_meters( )

##

# sas.credit_amount_of_all_bills_accepted( )

##

# sas.coin_amount_accepted_from_external_coin_acceptor( )

##

# sas.last_accepted_bill_info( )

##

# sas.number_of_bills_currently_in_stacker( )

##

# sas.total_credit_amount_of_all_bills_in_stacker( )

##

# sas.set_secure_enhanced_validation_ID( MachineID=b'\x01\x00\x01', seq_num=b'\x00\x01\x00') # read manual

##

# sas.enhanced_validation_information( curr_validation_info=0x00) # asc Lena (append)

##

# sas.current_hopper_status( )

##

# sas.validation_meters( type_of_validation=0x01)

##

## sas.total_number_of_games_impimented( )

##

## sas.game_meters( , n=1)

##

## sas.game_configuration( , n=1)

##

## sas.SAS_version_gaming_machine_serial_ID( )

##

## sas.selected_game_number( )

##

## sas.enabled_game_numbers( )

##

## sas.pending_cashout_info( )

##

# sas.validation_number( 11, 123456)

##

## sas.autentification_info( )

##

## sas.extended_meters_for_game( , n=1)

## #6F

##

## sas.ticket_validation_data( )

## #70

##

# sas.redeem_ticket( )

## #71

##

# sas.AFT_transfer_funds(0x00, 0,0x00, 10000, 0, 0, 0, b'\xea\x03\x00\x00', b'\x67\x68\x6a\x68\x62\x76\x79\x64\x6a\x6c\x66\x79\x76\x6d\x6b\x64\x79\x79\x64\x72', transaction_ID_lenght=0x01, transaction_ID='1', expiration=b'\x03\x25\x20\x18', pool_ID=0x1010, reciept_data='fgh', lock_timeout=1)

#transfer_code=0x00, transaction_index=0x00, transfer_type=0x00, cashable_amount=0, restricted_amount=0, non_restricted_amount=0, transfer_flags=0x00, asset_number=b'\x00\x00\x00\x00\x00', registration_key=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', transaction_ID_lenght=0x00, transaction_ID='', expiration=b'\x00\x00\x00\x00', pool_ID=0, reciept_data='', lock_timeout=0):

## #72

##

## sas.AFT_register_gaming_machine( )

## #73

##

## sas.AFT_game_lock_and_status_request( )

## #74

# sas.AFT_register_gaming_machine(reg_code=0x01, asset_number=b'\xea\x03\x00\x00', reg_key='ghjhbvydjlfyvmkdyydr', POS_ID=b'\x03\x04\x05\x06')

##

## sas.set_AFT_reciept_data( )

## #75

##

## sas.set_custom_AFT_ticket_data( )

## #76

##

# sas.exnended_validation_status(control_mask=[0b00000011,0b00000000], status_bits=[0b00000011,0b00000000], cashable_ticket_reciept_exp=0, restricted_ticket_exp=0)

## #7B

##

## sas.set_extended_ticket_data( )

## #7C

##

## sas.set_ticket_data( )

## #7D

##

## sas.current_date_time( )

## #7E

##

## sas.recieve_date_time( )

## #7F

##

## sas.recieve_progressive_amount( )

## #80

##

## sas.cumulative_progressive_wins( )

## #83

##

## sas.progressive_win_amount( )

## #84

##

## sas.SAS_progressive_win_amount( )

## #85

##

## sas.recieve_multiple_progressive_levels( )

## #86

##

## sas.multiple_SAS_progresive_win_amounts( )

## #87

##

## sas.initiate_legacy_bonus_pay( )

## #8A

##

## sas.initiate_multiplied_jackpot_mode( )

## #8B

##

## sas.enter_exit_tournament_mode( )

## #8C

##

## sas.card_info( )

## #8E

##

## sas.physical_reel_stop_info( )

## #8F

##

## sas.legacy_bonus_win_info( )

## #90

##

## sas.remote_handpay_reset( )

## #94

##

## sas.tournament_games_played( )

## #95

##

## sas.tournament_games_won( )

## #96

##

## sas.tournament_credits_wagered( )

## #97

##

## sas.tournament_credits_won( )

## #98

##

## sas.meters_95_98( )

## #99

##

## sas.legacy_bonus_meters( )

## #9A

##

## sas.enabled_features( )

## #A0

##

## sas.cashout_limit( )

## #A4

##

## sas.enable_jackpot_handpay_reset_method( )

## #A8

##

## sas.en_dis_game_auto_rebet( )

## #AA

##

## sas.extended_meters_game_alt( ,n=1)

## #AF

##

## sas.multi_denom_preamble( )

## #B0

##

## sas.current_player_denomination( )

## #B1

##

## sas.enabled_player_denominations( )

## #B2

##

## sas.token_denomination( )

## #B3

##

## sas.wager_category_info( )

## #B4

##

## sas.extended_game_info( ,n=1)

## #B5

##

## sas.event_response_to_long_poll( )

## #FF

##

## for keys, values in aft_statement.items():

## print(keys)

## print(values)

        #sas.enhanced_validation_information(0)

        #sas.set_secure_enhanced_validation_ID( MachineID=[0x01,0x01,0x01], seq_num=[0x00,0x00,0x01])

##

        while True:
                state= binascii.hexlify(bytearray(sas.events_poll()))
                print state
                if (state=='57'):
                        sas.pending_cashout_info()
                        sas.validation_number( validationID=1, valid_number=1234567890365421)

                        #sas.cash_out_ticket_info()

                if (state=='67'): #cashin
                        sas.ticket_validation_data()
                        sas.redeem_ticket( transfer_code=0, transfer_amount=10000, parsing_code=0, validation_data=1234567891234567, rescticted_expiration=3, pool_ID=0)
                        time.sleep(.3)
                        sas.redeem_ticket( transfer_code=0xff, transfer_amount=10000, parsing_code=0, validation_data=1234567891234567, rescticted_expiration=3, pool_ID=0)

                #71

                time.sleep(1)

        for keys, values in tito_statement.items():
                print(keys)
                print(values)

