# Casino Gaming Machine Application Architecture

## Overview

This is a comprehensive Raspberry Pi-based casino gaming machine controller that manages slot machine communication, player sessions, financial transactions, and hardware interfaces through the SAS (Slot Accounting System) protocol.

## Application Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           MAIN APPLICATION THREAD                               │
│                         (raspberryPython3.py - 15,634 lines)                    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
        ┌───────────▼──────────┐ ┌─────▼─────┐ ┌──────────▼──────────┐
        │   GUI SUBSYSTEM      │ │ DATABASE  │ │  NETWORK SERVICES   │
        │                      │ │ LAYER     │ │                     │
        │ ┌─────────────────┐  │ │           │ │ ┌─────────────────┐ │
        │ │ PyWebView       │  │ │PostgreSQL │ │ │ Flask Web API   │ │
        │ │ (HTML/JS GUI)   │  │ │   or      │ │ │ Port: 5002      │ │
        │ │ - 1280.html     │  │ │ MSSQL     │ │ │ Endpoints:      │ │
        │ │ - guiwebview.html│ │ │           │ │ │ /relays/<id>    │ │
        │ │ - Fullscreen    │  │ │           │ │ │ /sessionstart   │ │
        │ │ - Touch Events  │  │ │           │ │ │ /sessionaddmoney│ │
        │ └─────────────────┘  │ │           │ │ │ /sessionclose   │ │
        └──────────────────────┘ │           │ │ │ /screenclick    │ │
                                 │           │ │ └─────────────────┘ │
                                 └───────────┘ └─────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                        HARDWARE COMMUNICATION LAYER                             │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        │                               │                               │
┌───────▼──────────┐        ┌──────────▼──────────┐        ┌──────────▼──────────┐
│ SAS COMMUNICATION│        │  CARD READER        │        │  BILL ACCEPTOR      │
│                  │        │                     │        │                     │
│ Serial Port:     │        │ Serial Port:        │        │ Serial Port:        │
│ /dev/ttyUSB0     │        │ /dev/ttyUSB1        │        │ /dev/ttyUSB2        │
│                  │        │                     │        │                     │
│ Protocol: SAS    │        │ Protocol: Custom    │        │ Protocol: ccTalk/   │
│ Baud: 19200      │        │ Baud: 9600          │        │ MDB/Custom          │
│ Parity: Mark/    │        │ Parity: None        │        │ Baud: 9600          │
│ Space/Even       │        │                     │        │ Parity: Even        │
│                  │        │                     │        │                     │
│ Commands:        │        │ Functions:          │        │ Functions:          │
│ - 80 (Long Poll) │        │ - Card Detection    │        │ - Bill Validation   │
│ - 81 (General)   │        │ - Card Reading      │        │ - Denomination      │
│ - Meter Reads    │        │ - Card Ejection     │        │ - Enable/Disable    │
│ - Money Transfer │        │                     │        │ - Status Check      │
│ - Game Control   │        │                     │        │                     │
└──────────────────┘        └─────────────────────┘        └─────────────────────┘
        │                               │                               │
        ▼                               ▼                               ▼
┌──────────────────┐        ┌─────────────────────┐        ┌─────────────────────┐
│   SLOT MACHINE   │        │    CARD READER      │        │   BILL ACCEPTOR     │
│                  │        │                     │        │                     │
│ - Game Logic     │        │ - Magnetic Stripe   │        │ - Bill Validation   │
│ - Meters         │        │ - RFID/NFC          │        │ - Cash Handling     │
│ - Balance        │        │ - Smart Card        │        │ - Stacker           │
│ - Jackpots       │        │                     │        │                     │
└──────────────────┘        └─────────────────────┘        └─────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                           THREADING ARCHITECTURE                                │
└─────────────────────────────────────────────────────────────────────────────────┘

Main Thread
├── GUI Thread (PyQt5/PyWebView - configurable via IsGUI_Type)
├── Flask Web Server Thread (port 5002)
├── Command Input Thread (stdin.readline())
├── SAS Communication Thread (perpetualTimer 20-50ms)
│   ├── TmrSASPooling() - Main polling loop
│   ├── DoSASPoolingMsg() - Send/receive SAS messages
│   └── DoConsumeSASMessage() - Process responses (spawned per message)
├── Card Reader Thread (perpetualTimer 500ms)
│   └── TmrCardRead() - Monitor card insertion/removal
├── Bill Acceptor Thread (perpetualTimer 200ms)
│   └── DoBillAcceptorPooling() - Monitor bill insertion
├── Nextion Display Thread (perpetualTimer 1000ms)
│   └── DoNextionPooling() - Update display
├── Online Status Thread (perpetualTimer 5000ms)
│   └── TmrIsOnline() - Heartbeat to server
└── License Check Thread (perpetualTimer 600000ms)
    └── Mevlut_LicenceCheck() - Remote license validation
```

## Component Details

### 1. **Main Application Core**

- **File**: `raspberryPython3.py` (15,634 lines)
- **Purpose**: Central coordinator for all subsystems
- **Key Functions**:
  - Application initialization and configuration
  - Thread management and coordination
  - Global state management
  - Exception handling and logging
- **Configuration**: `settings.ini` file for machine-specific settings

### 2. **GUI Subsystem (Multi-Platform)**

- **Technologies**: Multiple GUI frameworks supported based on configuration
- **GUI Types** (controlled by `IsGUI_Type` variable):

  - **Type 1**: PyQt5 native GUI (QtGui.QApplication)
  - **Type 2**: Custom GUI implementation
  - **Type 3**: HTML-based GUI (WxPython)
  - **Type 4**: PyWebView with HTML/JavaScript frontend
  - **Type 5**: Advanced GUI mode

- **PyQt5 Implementation** (Type 1):

  - Native Qt5 widgets and forms
  - Fullscreen support (`IsGUIFullScreen=1`)
  - Dedicated GUI thread (`threadGUI`)
  - Uses `Ui_Widget` class for interface

- **PyWebView Implementation** (Type 4):

  - **Files**:
    - `1280.html` (1280x480 resolution)
    - `guiwebview.html` (800x480 resolution)
  - HTML/JavaScript frontend with Python backend bridge

- **Purpose**: Touch-screen interface for players and administrators
- **Features**:
  - Player balance display
  - Game selection interface
  - Administrative controls
  - Real-time status updates
  - Fullscreen kiosk mode
- **Threading**: Runs in separate GUI thread (`CreateGUI()`)
- **Connected To**: Main thread via shared global variables and function calls

### 3. **SAS Communication Layer**

- **Protocol**: SAS (Slot Accounting System) - Industry standard
- **Transport**: RS-485/RS-232 serial communication
- **Port**: `/dev/ttyUSB0` (auto-detected)
- **Timing**: 20-50ms polling interval
- **Purpose**: Real-time communication with slot machine
- **Key Commands**:
  - `80` - Long poll (check for events)
  - `81` - General poll (basic status)
  - Meter reading commands
  - Money transfer commands (AFT - Account Fund Transfer)
  - Game control commands
- **Threading**: Dedicated background thread with message processing threads
- **Connected To**: Physical slot machine hardware

### 4. **Database Layer**

- **Supported**: PostgreSQL (primary) and MSSQL (legacy)
- **Purpose**:
  - Customer account management
  - Transaction logging
  - Device status reporting
  - Audit trail maintenance
- **Key Tables**:
  - Customer accounts and balances
  - Transaction history
  - Device status logs
  - SAS message logs
- **Connection**: Configurable via `.ini` files
- **Connected To**: All subsystems for logging and data persistence

### 5. **Flask Web API**

- **Port**: 5002 (configurable)
- **Purpose**: Remote control and integration interface
- **Endpoints**:
  - `/relays/<relayid>` - GPIO relay control
  - `/sessionstart/<customerid>/<amount>` - Start gaming session
  - `/sessionaddmoney/<customerid>/<amount>` - Add money to session
  - `/sessionclose/<customerid>` - End gaming session
  - `/screenclick/<x>/<y>` - Simulate touch events
- **Connected To**: External management systems, mobile apps

### 6. **Card Reader Interface**

- **Port**: `/dev/ttyUSB1` (auto-detected)
- **Purpose**: Customer identification and authentication
- **Supported Types**:
  - Magnetic stripe cards
  - RFID/NFC cards
  - Smart cards
- **Functions**:
  - Card insertion detection
  - Card data reading
  - Card ejection control
- **Threading**: Dedicated polling thread (500ms interval)
- **Connected To**: Customer database for account lookup

### 7. **Bill Acceptor Interface**

- **Port**: `/dev/ttyUSB2` (auto-detected)
- **Purpose**: Cash input validation and handling
- **Protocols**: ccTalk, MDB, or custom protocols
- **Functions**:
  - Bill denomination recognition
  - Bill validation
  - Enable/disable control
  - Status monitoring
- **Threading**: High-frequency polling thread (200ms interval)
- **Connected To**: SAS layer for credit transfer to slot machine

### 8. **GPIO Control**

- **Purpose**: Hardware relay control for external devices
- **Pins**: 12, 16, 18, 22 (configurable)
- **Functions**:
  - Door locks
  - Lighting control
  - External device triggers
- **Connected To**: Flask API for remote control

### 9. **Nextion Display Interface** (Optional)

- **Port**: Auto-detected serial port
- **Purpose**: Secondary display for status and advertising
- **Functions**:
  - Status display
  - Advertisement rotation
  - Touch input processing
- **Threading**: 1-second polling interval
- **Connected To**: Main GUI system for synchronized updates

### 10. **Command Processing System**

- **Input Methods**:
  - Standard input (stdin) for direct commands
  - Flask API endpoints
  - GUI interactions
  - Remote license server commands
- **Command Examples**:
  - `getmeter:` - Read slot machine meters
  - `getmeter1:` - Read all meters
  - `billenable:` - Enable bill acceptor
  - `admin:` - Show admin interface
- **Threading**: Commands processed in separate threads
- **Connected To**: All subsystems for control and monitoring

## Data Flow

### Customer Session Flow

1. **Card Insertion** → Card Reader → Database Lookup → SAS Balance Query
2. **Money Insert** → Bill Acceptor → SAS Credit Transfer → Database Log
3. **Game Play** → SAS Monitoring → Real-time Updates → Database Logging
4. **Cashout** → SAS Balance Transfer → Database Update → Card Ejection

### Monitoring Flow

1. **SAS Polling** → Slot Machine Status → Database Logging
2. **Device Status** → Periodic Heartbeat → Central Server
3. **Exception Handling** → Error Logging → Alert Generation

### Remote Control Flow

1. **Flask API Request** → Command Processing → Hardware Action
2. **Database Command Queue** → Polling → Command Execution
3. **GUI Interaction** → Event Processing → System Response

## Configuration Files

- **`settings.ini`**: Machine-specific configuration
- **`pg_*.ini`**: PostgreSQL connection settings
- **`screentypeid.txt`**: Display configuration
- **`isonlineplaying.ini`**: Online gaming mode flag

## Security Features

- **License Validation**: Remote license server integration
- **Admin Cards**: Restricted access control
- **Device Locking**: Remote and local lock capabilities
- **Audit Logging**: Comprehensive transaction and event logging
- **Secure Communication**: Encrypted database connections

## Scalability

- **Multi-Device Support**: Each Raspberry Pi manages one slot machine
- **Centralized Management**: Database-driven configuration and monitoring
- **Remote Updates**: Command queue system for mass updates
- **Load Distribution**: Independent operation with central coordination

This architecture provides a robust, scalable solution for casino gaming machine management with real-time hardware control, comprehensive monitoring, and remote management capabilities.

## Web GUI Analysis (1280.html)

### **Overview**

The `1280.html` file is a comprehensive touch-screen casino gaming interface designed for 1280x480 resolution displays. It serves as the primary player interaction interface when using PyWebView (GUI Type 4).

### **Technical Stack**

- **HTML5/CSS3/JavaScript** - Core web technologies
- **jQuery 3.4.1** - DOM manipulation and event handling
- **Gauge.min.js** - Animated bonus progress gauges
- **PyWebView API Bridge** - Communication with Python backend

### **Screen Layout Architecture**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           1280x480 MAIN CONTAINER                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Header Bar (42px height)                                                       │
│ ┌─────────┬─────────────────────┬─────────────┬─────────────────────────────┐   │
│ │ Status  │ Machine Name        │ Messages    │ User Info                   │   │
│ └─────────┴─────────────────────┴─────────────┴─────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Main Content Area (414px height)                                               │
│ ┌─────────────┬─┬─────────────────────────┬─────────────────────────────────┐   │
│ │ Navigation  │ │ Content Panel           │ Advertisement Panel             │   │
│ │ Menu        │ │ (525px width)           │ (480px width)                   │   │
│ │ (210px)     │ │                         │                                 │   │
│ │             │ │ • Bonus (with gauge)    │ • Static customer_adverts.png   │   │
│ │ • BONUS     │ │ • Jackpot (4 levels)    │                                 │   │
│ │ • JACKPOT   │ │ • Balance (3 types)     │                                 │   │
│ │ • BALANCE   │ │ • Bar (ordering system) │                                 │   │
│ │ • BAR       │ │ • Settings              │                                 │   │
│ │ • SETTINGS  │ │ • Messages              │                                 │   │
│ └─────────────┴─┴─────────────────────────┴─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### **Screen Management System**

#### **1. Multi-Screen Architecture**

- **divMain** - Idle screen (background_idle1280.png)
- **divCustomer** - Active player interface
- **divAdmin** - Administrative controls
- **divKeyboard** - Numeric input interface
- **divNotify** - Modal notifications
- **divVideo** - Video playback screen

#### **2. Dynamic Content Panels**

- **divBonus** - Animated gauge bonus system
- **divJackpot** - 4-tier jackpot display (Platinum, Gold, Silver, Bronze)
- **divBalance** - 3-balance display (Cashable, Promo, Bank)
- **divBar** - Product ordering system with basket
- **divSettings** - Player settings and cash-out
- **divMessages** - Message center with notifications

### **Key Interactive Features**

#### **1. Bonus System**

- **Animated Gauge**: Canvas-based circular progress indicator
- **Dynamic Calculation**: Real-time bonus percentage based on bet amount
- **Multi-tier System**: 5 color zones with different bonus levels
- **Redemption Interface**: Button to claim earned bonus

#### **2. Bar/Ordering System**

- **Category Navigation**: Product categories with back navigation
- **Shopping Basket**: Add/remove products with visual feedback
- **Order Confirmation**: Review and confirm orders
- **Product Management**: Dynamic product list generation

#### **3. Administrative Interface**

- **Device Control**: Lock/Unlock, Restart, RAM Clear
- **SAS Testing**: Jackpot test, EFT operations, Balance checks
- **Meter Reading**: Manual meter requests
- **Configuration**: Device settings access

#### **4. Message System**

- **Real-time Notifications**: Blinking message indicator
- **Award Messages**: Special promotional messages
- **Read/Unread Status**: Visual distinction for message states

### **Python-JavaScript Communication**

#### **API Bridge Functions**

```javascript
// Main communication function
function SendData2Python(params) {
  pywebview.api.DoSomethingFromJavascript(params);
}

// Navigation events
function PythonCustomerNavIconClicked(params) {
  SendData2Python(params);
}
```

#### **Command Types Sent to Python**

- **Navigation**: `divBonus`, `divBalance`, `divJackpot`, etc.
- **Actions**: `divBonusRequest`, `divSettingsCashout`
- **Admin Commands**: `divAdminLock`, `divAdminMeter`, `divAdminRestart`
- **Bar Orders**: `divBarOrder|productlist`
- **Keyboard Input**: `divKeyboard|ok|answer`

### **Styling and UX Design**

#### **Design Principles**

- **Touch-Optimized**: Large buttons (68px+ height) for finger interaction
- **High Contrast**: White borders on colored backgrounds
- **Visual Feedback**: Hover effects and selection highlighting
- **Accessibility**: Large fonts (20px-50px) for readability

#### **Color Scheme**

- **Primary**: #fcb03c (Orange/Gold) for highlights
- **Secondary**: #dbb2a4 (Beige) for panels
- **Accent**: #7f571b (Brown) for text on gold
- **Interactive**: Green for confirm, Red for cancel/delete

#### **Responsive Elements**

- **Button States**: Hover effects with color changes
- **Selection Feedback**: Background image changes for active buttons
- **Animation**: Blinking message indicators, gauge animations

### **Asset Dependencies**

#### **Images**

- **Backgrounds**: `background1280.png`, `background_idle1280.png`
- **Icons**: `icon_user1280.png`, `icon_messages1280.png`, `icon_delete1280.png`
- **Buttons**: `btnBonus1280.png`, `btnJackpot1280.png`, etc.
- **UI Elements**: `star_full1280.png`, `star_empty1280.png`
- **Selection**: `btnBackgroundSelected1280.png`

#### **JavaScript Libraries**

- **jQuery 3.4.1**: DOM manipulation and event handling
- **Gauge.min.js**: Canvas-based circular progress gauges

### **State Management**

#### **Global Variables**

- **CurrentGUI**: Tracks active screen/panel
- **ProductBasket**: Shopping cart for bar orders
- **BarActiveScreen**: Navigation state for bar system
- **KeyboardAnswer**: Input accumulator for numeric entry
- **IsSentHelloFromPython**: Initialization handshake flag

#### **Screen Transitions**

- **ShowIdleScreen()**: Return to idle state
- **ShowCustomerPage()**: Activate player interface
- **CustomerNavIconClicked()**: Navigate between panels
- **ReturnCustomerPage()**: Return from sub-screens

### **Integration Points**

#### **With Python Backend**

- **Real-time Updates**: Balance, bonus, jackpot values
- **Command Execution**: Administrative functions
- **State Synchronization**: Screen changes, user actions
- **Data Exchange**: Customer info, transaction data

#### **With Hardware**

- **Touch Events**: Screen coordinates sent to Python
- **Display Control**: Fullscreen mode, resolution handling
- **Audio/Video**: Video playback for promotional content

This web GUI represents a sophisticated casino gaming interface with comprehensive player interaction capabilities, administrative controls, and seamless integration with the Python backend system.
