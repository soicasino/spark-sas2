flowchart TD
A[Start: Script Loads] --> B[Import Modules & Handle Missing Dependencies]
B --> C[Read Config Files & Set Global Variables]
C --> D{Platform/Device Detection}
D -->|Windows| E1[Set Windows-specific Ports and Flags]
D -->|Linux| E2[Set Linux-specific Ports and Flags]
D -->|Other| E3[Set Defaults]
E1 --> F[Database Setup: SQLite or PostgreSQL]
E2 --> F
E3 --> F

    F --> G[Detect and Assign Serial/USB Ports]
    G --> H[Set Up Device State: Card Reader, Bill Acceptor, SAS, Nextion, etc.]
    H --> I[Read or Recover Card and Session State]
    I --> J{GUI Type?}
    J -->|PyQt5| K1[Start PyQt5 GUI Thread]
    J -->|wxPython| K2[Start wxPython GUI Thread]
    J -->|Webview| K3[Start Webview GUI Thread]
    J -->|None| K4[No GUI]

    K1 --> L[Set Up Timers and Threads: Card Reader, SAS, Bill Acceptor, etc.]
    K2 --> L
    K3 --> L
    K4 --> L

    L --> M{Online Play Enabled?}
    M -->|Yes| N1[Start Flask Web API Thread]
    M -->|No| N2[Skip Web API]

    N1 --> O[Start Arduino Polling Thread]
    N2 --> O

    O --> P[Start Main Loop or Wait for Commands]
    P --> Q[Device Running: Handles Events via Threads, Timers, and GUI/Web API]
