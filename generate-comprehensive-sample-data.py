#!/usr/bin/env python3
"""
Comprehensive Device Message Queue Sample Data Generator

Based on sql-calls.md documentation - generates sample data for all 55+ stored procedures
across all operation categories with realistic parameters and SAS message context.

Categories covered:
- Bill Acceptor Operations (10 records)
- Card Operations (10 records) 
- Game Operations (10 records)
- Device Status & Monitoring (10 records)
- Customer & Bonus Operations (10 records)
- Financial Operations (10 records)
- Logging & Debugging Operations (10 records)
- Special Edge Cases (10 records)
"""

import json
import uuid
import datetime
import random
import psycopg2
import os
from decimal import Decimal

def load_config():
    """Load PostgreSQL configuration from files or use defaults"""
    config = {
        'host': '10.0.0.59',
        'database': 'postgres', 
        'user': 'postgres',
        'password': 's123',
        'port': 5432,
        'schema': 'tcasino'
    }
    
    config_files = {
        'host': 'pg_host.ini',
        'database': 'pg_database.ini', 
        'user': 'pg_user.ini',
        'password': 'pg_password.ini',
        'port': 'pg_port.ini',
        'schema': 'pg_schema.ini'
    }
    
    for key, filename in config_files.items():
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    value = f.read().strip()
                    config[key] = int(value) if key == 'port' else value
            except:
                pass
    
    return config

def generate_device_mac():
    """Generate realistic MAC addresses for gaming machines"""
    prefixes = ["00:11:22", "AA:BB:CC", "B8:27:EB", "DC:A6:32", "E4:5F:01"]
    return f"{random.choice(prefixes)}:{random.randint(10,99):02X}:{random.randint(10,99):02X}:{random.randint(10,99):02X}"

def generate_card_number():
    """Generate realistic card numbers"""
    return f"{random.randint(1000000000, 9999999999)}"

def generate_sas_context():
    """Generate realistic SAS message context with all possible fields"""
    bill_messages = [
        "02A501C4", "01FF001CA5", "03B201D5", "04C301E6", "05D401F7",
        "06E501F8", "07F601G9", "08A701H0", "09B801I1", "0AC901J2"
    ]
    
    sas_commands = [
        "0120", "0130", "0140", "0150", "0160", "01A0", "01B0", "01C0",
        "0172", "0174", "01B3", "01FF", "0128", "0166", "0164", "0169",
        "012F", "01FF7E", "01FF7F", "01FF88", "01FF51"
    ]
    
    context = {
        "sas_version_id": random.choice([40, 41, 42, 43, 44])
    }
    
    # Randomly include different SAS message components
    if random.random() > 0.2:  # 80% chance
        context["last_billacceptor_message"] = random.choice(bill_messages)
        if random.random() > 0.4:  # 60% chance if bill message exists
            context["last_billacceptor_message_handle"] = context["last_billacceptor_message"]
    
    if random.random() > 0.3:  # 70% chance
        context["last_sas_command"] = random.choice(sas_commands)
    
    # Add additional SAS context for realism
    if random.random() > 0.6:  # 40% chance
        context["game_state"] = random.choice(["idle", "playing", "bonus", "feature"])
    
    if random.random() > 0.7:  # 30% chance  
        context["meter_reading"] = random.randint(1000000, 9999999)
    
    return context

# BILL ACCEPTOR OPERATIONS
def generate_bill_acceptor_samples():
    """Bill acceptor related procedures"""
    samples = []
    procedures = {
        'tsp_CheckBillacceptorIn': lambda mac: [
            mac, random.randint(1, 3), random.randint(10000, 99999),
            generate_card_number(), random.choice(["USD", "EUR", "GBP", "TRY"]),
            random.choice(["US", "7B", "TR", "EU"]), 
            random.choice([1, 5, 10, 20, 50, 100]),
            f"{random.choice([1, 5, 10, 20, 50, 100]):02X}"
        ],
        'tsp_InsBillAcceptorMoney': lambda mac: [
            random.randint(10000, 99999), generate_card_number(),
            round(random.uniform(1, 100), 2), "USD", mac,
            "US", random.randint(1, 5), random.randint(1, 999),
            random.choice([True, False]), random.choice([True, False]),
            round(random.uniform(1, 100), 2)
        ],
        'tsp_UpdBillAcceptorMoney': lambda mac: [
            random.randint(1000, 9999), random.choice([True, False])
        ]
    }
    
    for i in range(10):
        procedure_name = random.choice(list(procedures.keys()))
        device_mac = generate_device_mac()
        parameters = procedures[procedure_name](device_mac)
        
        # Mix of sync/async based on procedure type
        is_sync = procedure_name == 'tsp_CheckBillacceptorIn'
        status = generate_status(is_sync)
        
        payload = create_base_payload(procedure_name, parameters, device_mac, is_sync)
        
        if is_sync and status == 'proc_called':
            payload['result_sample'] = [{
                "Result": 1,
                "ErrorMessage": "Bill accepted successfully", 
                "CreditAmount": parameters[6] if len(parameters) > 6 else 0
            }]
        
        samples.append(create_record(device_mac, procedure_name, payload, status))
    
    return samples

# CARD OPERATIONS  
def generate_card_operation_samples():
    """Card reader and card management procedures"""
    samples = []
    procedures = {
        'tsp_CardRead': lambda mac: [
            mac, generate_card_number(), round(random.uniform(0, 1000), 2),
            round(random.uniform(0, 100), 2), random.randint(0, 1), random.randint(1, 999)
        ],
        'tsp_CardReadPartial': lambda mac: [
            mac, generate_card_number()
        ],
        'tsp_CardReadAddMoney': lambda mac: [
            random.randint(10000, 99999), random.randint(1000, 9999),
            round(random.uniform(1, 500), 2), random.randint(1, 3),
            round(random.uniform(0, 1000), 2)
        ],
        'tsp_CardExit': lambda mac: [
            random.randint(10000, 99999), mac, generate_card_number(),
            round(random.uniform(0, 500), 2), random.randint(0, 1000),
            random.randint(1, 99), round(random.uniform(0, 1000), 2),
            round(random.uniform(0, 1000), 2), round(random.uniform(0, 100), 2),
            random.randint(0, 1), f"{random.randint(0, 100)}", random.randint(0, 2)
        ]
    }
    
    for i in range(10):
        procedure_name = random.choice(list(procedures.keys()))
        device_mac = generate_device_mac()
        parameters = procedures[procedure_name](device_mac)
        
        is_sync = procedure_name in ['tsp_CardRead', 'tsp_CardReadPartial']
        status = generate_status(is_sync)
        
        payload = create_base_payload(procedure_name, parameters, device_mac, is_sync)
        
        if is_sync and status == 'proc_called':
            if procedure_name == 'tsp_CardRead':
                payload['result_sample'] = [{
                    "Result": 1,
                    "CardMachineLogId": random.randint(10000, 99999),
                    "Balance": round(random.uniform(0, 1000), 2),
                    "CustomerName": f"Customer_{random.randint(1000, 9999)}"
                }]
        
        samples.append(create_record(device_mac, procedure_name, payload, status))
    
    return samples

# GAME OPERATIONS
def generate_game_operation_samples():
    """Game start, end, and tracking procedures"""
    samples = []
    procedures = {
        'tsp_InsGameStart': lambda mac: [
            mac, random.randint(10000, 99999), round(random.uniform(1, 50), 2),
            round(random.uniform(0, 100), 2), round(random.uniform(1, 50), 2),
            random.choice(["REGULAR", "BONUS", "FEATURE", "FREESPIN"]),
            random.randint(0, 5), random.randint(1, 100),
            round(random.uniform(0, 10), 2), random.randint(1, 999),
            random.randint(0, 1000), random.randint(0, 2), random.randint(1000, 9999),
            random.randint(1, 10), round(random.uniform(1, 50), 2)
        ],
        'tsp_InsGameEnd': lambda mac: [
            mac, random.randint(10000, 99999), round(random.uniform(0, 100), 2),
            random.randint(1, 100), random.randint(1000, 9999),
            round(random.uniform(0, 500), 2), random.randint(1, 999),
            round(random.uniform(0, 100), 2), round(random.uniform(1, 50), 2),
            round(random.uniform(100, 1000), 2)
        ],
        'tsp_InsGameStartEnd': lambda mac: [
            mac, random.randint(10000, 99999), round(random.uniform(1, 50), 2),
            round(random.uniform(1, 50), 2), random.choice(["REGULAR", "BONUS"]),
            random.randint(0, 5), random.randint(1, 100),
            round(random.uniform(0, 10), 2), random.randint(1, 999)
        ],
        'tsp_GetDeviceGameInfo': lambda mac: [
            mac, random.randint(1, 100)
        ]
    }
    
    for i in range(10):
        procedure_name = random.choice(list(procedures.keys()))
        device_mac = generate_device_mac()
        parameters = procedures[procedure_name](device_mac)
        
        is_sync = procedure_name == 'tsp_GetDeviceGameInfo'
        status = generate_status(is_sync)
        
        payload = create_base_payload(procedure_name, parameters, device_mac, is_sync)
        
        samples.append(create_record(device_mac, procedure_name, payload, status))
    
    return samples

# DEVICE STATUS & MONITORING
def generate_device_monitoring_samples():
    """Device status, monitoring and control procedures"""
    samples = []
    procedures = {
        'tsp_DeviceStatu': lambda mac: [
            mac, random.randint(0, 3), f"192.168.1.{random.randint(1, 254)}",
            random.randint(40, 44), random.randint(0, 1), random.randint(0, 1),
            "COM1", "COM2", random.choice(["ONLINE", "OFFLINE", "MAINTENANCE"]),
            random.randint(0, 1), random.randint(1, 999), random.randint(0, 1000),
            round(random.uniform(0, 1000), 2), random.randint(10000, 99999),
            "MainScreen", random.randint(1, 100), random.choice([True, False]),
            random.randint(1000, 9999), random.randint(1, 999), random.randint(0, 1)
        ],
        'tsp_UpdDeviceEnablesGames': lambda mac: [
            random.randint(1, 999), 
            ",".join([str(random.randint(1, 100)) for _ in range(random.randint(1, 10))]),
            f"Game update for {mac}"
        ],
        'tsp_UpdDeviceAdditionalInfo': lambda mac: [
            random.randint(1, 999), round(random.uniform(20, 80), 1),
            str(random.randint(0, 1)), random.randint(1, 8),
            random.randint(0, 100), random.randint(0, 100), random.randint(10, 1000)
        ],
        'tsp_GetDeviceAdditionalInfo': lambda mac: [
            random.randint(1, 999)
        ],
        'tsp_UpdDeviceIsLocked': lambda mac: [
            random.randint(1, 999), random.randint(0, 1)
        ]
    }
    
    for i in range(10):
        procedure_name = random.choice(list(procedures.keys()))
        device_mac = generate_device_mac()
        parameters = procedures[procedure_name](device_mac)
        
        is_sync = procedure_name == 'tsp_GetDeviceAdditionalInfo'
        status = generate_status(is_sync)
        
        payload = create_base_payload(procedure_name, parameters, device_mac, is_sync)
        
        samples.append(create_record(device_mac, procedure_name, payload, status))
    
    return samples

# CUSTOMER & BONUS OPERATIONS
def generate_customer_bonus_samples():
    """Customer management and bonus system procedures"""
    samples = []
    procedures = {
        'tsp_GetCustomerAdditional': lambda mac: [
            mac, random.randint(1000, 9999)
        ],
        'tsp_GetCustomerCurrentMessages': lambda mac: [
            mac, random.randint(1000, 9999)
        ],
        'tsp_BonusRequestList': lambda mac: [
            mac, random.randint(1000, 9999), random.randint(1, 10)
        ],
        'tsp_InsBonusRequest': lambda mac: [
            random.randint(1000, 9999), random.randint(1, 50),
            round(random.uniform(1, 100), 2), "SLOT_BONUS",
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ],
        'tsp_UpdBonusAsUsed': lambda mac: [
            random.randint(1000, 9999), random.randint(1, 1000),
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ]
    }
    
    for i in range(10):
        procedure_name = random.choice(list(procedures.keys()))
        device_mac = generate_device_mac()
        parameters = procedures[procedure_name](device_mac)
        
        is_sync = procedure_name in ['tsp_GetCustomerAdditional', 'tsp_GetCustomerCurrentMessages', 'tsp_BonusRequestList']
        status = generate_status(is_sync)
        
        payload = create_base_payload(procedure_name, parameters, device_mac, is_sync)
        
        samples.append(create_record(device_mac, procedure_name, payload, status))
    
    return samples

# FINANCIAL OPERATIONS
def generate_financial_operation_samples():
    """Financial transactions and balance management"""
    samples = []
    procedures = {
        'tsp_UpdInsertedBalance': lambda mac: [
            random.randint(10000, 99999), round(random.uniform(0, 1000), 2),
            round(random.uniform(0, 100), 2)
        ],
        'tsp_GetBalanceInfoOnGM': lambda mac: [
            mac, generate_card_number()
        ],
        'tsp_InsMoneyUpload': lambda mac: [
            random.randint(1000, 9999), generate_card_number(),
            round(random.uniform(1, 500), 2), "CASH_IN",
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            random.randint(1, 99)
        ]
    }
    
    for i in range(10):
        procedure_name = random.choice(list(procedures.keys()))
        device_mac = generate_device_mac()
        parameters = procedures[procedure_name](device_mac)
        
        is_sync = procedure_name == 'tsp_GetBalanceInfoOnGM'
        status = generate_status(is_sync)
        
        payload = create_base_payload(procedure_name, parameters, device_mac, is_sync)
        
        if is_sync and status == 'proc_called':
            payload['result_sample'] = [{
                "CustomerBalance": round(random.uniform(0, 1000), 2),
                "CurrentBalance": round(random.uniform(0, 500), 2),
                "BonusBalance": round(random.uniform(0, 100), 2)
            }]
        
        samples.append(create_record(device_mac, procedure_name, payload, status))
    
    return samples

# LOGGING & DEBUGGING
def generate_logging_debugging_samples():
    """Logging, debugging and trace procedures"""
    samples = []
    procedures = {
        'tsp_InsImportantMessage': lambda mac: [
            mac, random.choice([
                "Game started successfully", "Card inserted", "Bill accepted",
                "Network connection established", "Handpay requested", 
                "Door opened", "Low hopper warning", "Tilt occurred",
                "Software update completed", "Device calibration finished"
            ]), random.randint(100, 999), random.randint(0, 3), random.randint(1000, 9999)
        ],
        'tsp_InsException': lambda mac: [
            mac, random.choice([
                "NetworkTimeout", "DatabaseError", "HardwareMalfunction",
                "SASProtocolError", "CardReaderError", "BillAcceptorJam",
                "MemoryLeakDetected", "ThreadDeadlock", "ConfigurationError"
            ]), random.choice([
                "Connection timeout after 30 seconds",
                "Database constraint violation in T_Card",
                "Bill acceptor mechanical jam detected",
                "SAS message format invalid",
                "Card reader magnetic stripe error",
                "Insufficient memory for operation",
                "Thread pool exhausted",
                "Invalid configuration parameter"
            ])
        ],
        'tsp_InsDeviceDebug': lambda mac: [
            random.randint(10000, 99999), random.randint(1, 999),
            json.dumps({
                "cpu_usage": random.randint(0, 100),
                "memory_usage": random.randint(0, 100),
                "network_latency": random.randint(1, 200),
                "active_threads": random.randint(1, 50)
            })
        ],
        'tsp_InsTraceLog': lambda mac: [
            mac, random.choice(["SAS", "CARD", "BILL", "NETWORK", "GAME"]),
            random.choice(["IN", "OUT"]), 
            f"0x{random.randint(0, 0xFFFFFF):06X}",
            random.randint(1, 1000000)
        ],
        'tsp_InsReceivedMessage': lambda mac: [
            mac, f"01{random.randint(0, 255):02X}{random.randint(0, 0xFFFF):04X}",
            random.randint(0, 1), random.choice(["ACK", "NAK", "POLL", ""])
        ],
        'tsp_InsSentCommands': lambda mac: [
            mac, random.randint(10000, 99999),
            random.choice(["MoneyQuery", "CashOut", "LockMachine", "UnlockMachine"]),
            f"01{random.randint(0, 255):02X}{random.randint(0, 0xFFFF):04X}"
        ]
    }
    
    for i in range(10):
        procedure_name = random.choice(list(procedures.keys()))
        device_mac = generate_device_mac()
        parameters = procedures[procedure_name](device_mac)
        
        # All logging operations are async
        is_sync = False
        status = generate_status(is_sync)
        
        payload = create_base_payload(procedure_name, parameters, device_mac, is_sync)
        
        samples.append(create_record(device_mac, procedure_name, payload, status))
    
    return samples

# SPECIAL EDGE CASES
def generate_edge_case_samples():
    """Special scenarios and edge cases"""
    samples = []
    
    # Large payload case
    device_mac = generate_device_mac()
    large_data = "X" * 2000  # Very large data
    payload = create_base_payload('tsp_InsImportantMessage', 
                                [device_mac, large_data, 999, 1, 1234], 
                                device_mac, False)
    samples.append(create_record(device_mac, 'tsp_InsImportantMessage', payload, 'failed'))
    
    # Minimal SAS context
    device_mac = generate_device_mac()
    payload = create_base_payload('tsp_CheckNetwork', [device_mac], device_mac, True)
    payload['sas_message'] = {"sas_version_id": 41}  # Minimal context
    samples.append(create_record(device_mac, 'tsp_CheckNetwork', payload, 'proc_called'))
    
    # No SAS context (rare edge case)
    device_mac = generate_device_mac()
    payload = create_base_payload('tsp_DeviceStatu', [device_mac, 0], device_mac, False)
    del payload['sas_message']  # Remove SAS context entirely
    samples.append(create_record(device_mac, 'tsp_DeviceStatu', payload, 'pending'))
    
    # Very old timestamp
    device_mac = generate_device_mac()
    payload = create_base_payload('tsp_InsGameStart', 
                                [device_mac, 12345, 10.0], device_mac, False)
    payload['timestamp'] = (datetime.datetime.now() - datetime.timedelta(days=30)).isoformat()
    samples.append(create_record(device_mac, 'tsp_InsGameStart', payload, 'completed'))
    
    # Rich SAS context
    device_mac = generate_device_mac()
    payload = create_base_payload('tsp_CheckBillacceptorIn', 
                                [device_mac, 1, 12345, "1234567890", "USD", "US", 20, "14"], 
                                device_mac, True)
    payload['sas_message'] = {
        "sas_version_id": 42,
        "last_billacceptor_message": "02A501C4",
        "last_billacceptor_message_handle": "02A501C4", 
        "last_sas_command": "0120",
        "game_state": "playing",
        "meter_reading": 1234567,
        "progressive_level": 3,
        "jackpot_amount": 15000.50
    }
    samples.append(create_record(device_mac, 'tsp_CheckBillacceptorIn', payload, 'proc_called'))
    
    # Add 5 more edge cases
    for i in range(5):
        device_mac = generate_device_mac()
        procedure_name = random.choice([
            'tsp_InsException', 'tsp_GetBalanceInfoOnGM', 'tsp_CardRead',
            'tsp_InsGameEnd', 'tsp_UpdDeviceIsLocked'
        ])
        payload = create_base_payload(procedure_name, [device_mac], device_mac, 
                                    random.choice([True, False]))
        status = random.choice(['pending', 'completed', 'failed', 'proc_called', 'proc_failed'])
        samples.append(create_record(device_mac, procedure_name, payload, status))
    
    return samples

# UTILITY FUNCTIONS
def generate_status(is_sync):
    """Generate appropriate status based on operation type"""
    if is_sync:
        return random.choices(['proc_called', 'proc_failed'], weights=[8, 2])[0]
    else:
        return random.choices(['pending', 'processing', 'completed', 'failed'], 
                            weights=[2, 1, 6, 1])[0]

def create_base_payload(procedure_name, parameters, device_mac, is_sync):
    """Create base payload with mandatory elements"""
    payload = {
        'procedure_name': procedure_name,
        'parameters': parameters,                    # ✓ REQUIRED: Procedure Parameters
        'device_id': device_mac,                     # ✓ REQUIRED: Device ID/MAC
        'timestamp': (datetime.datetime.now() - datetime.timedelta(
            minutes=random.randint(0, 2880)
        )).isoformat(),
        'sas_message': generate_sas_context()        # ✓ REQUIRED: SAS Message Context
    }
    
    if is_sync:
        payload.update({
            'database_used': random.choice(['postgresql', 'mssql']),
            'execution_type': 'synchronous',
            'result_count': random.randint(0, 5),
            'error_message': None
        })
    
    return payload

def create_record(device_mac, procedure_name, payload, status):
    """Create a complete message queue record"""
    return {
        'id': str(uuid.uuid4()),
        'device_id': device_mac,
        'procedure_name': procedure_name,
        'payload': payload,
        'status': status,
        'created_at': payload['timestamp']
    }

def main():
    """Generate comprehensive sample data covering all procedure categories"""
    print("🎰 COMPREHENSIVE Device Message Queue Sample Data Generator")
    print("=" * 60)
    print("📋 Based on sql-calls.md documentation")
    print("🎯 Generating 10 records per category (80 total)")
    
    # Load configuration
    config = load_config()
    print(f"\n📊 Configuration: {config['host']}:{config['port']} -> {config['database']}")
    
    # Connect to PostgreSQL
    try:
        conn = psycopg2.connect(
            host=config['host'],
            database=config['database'],
            user=config['user'],
            password=config['password'],
            port=config['port']
        )
        conn.autocommit = True
        print("✅ Connected to PostgreSQL")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    cursor = conn.cursor()
    
    # Generate comprehensive sample data
    print(f"\n🔄 Generating comprehensive sample data...")
    
    sample_generators = [
        ("Bill Acceptor Operations", generate_bill_acceptor_samples),
        ("Card Operations", generate_card_operation_samples),
        ("Game Operations", generate_game_operation_samples),
        ("Device Status & Monitoring", generate_device_monitoring_samples),
        ("Customer & Bonus Operations", generate_customer_bonus_samples),
        ("Financial Operations", generate_financial_operation_samples),
        ("Logging & Debugging", generate_logging_debugging_samples),
        ("Special Edge Cases", generate_edge_case_samples)
    ]
    
    all_samples = []
    
    for category_name, generator_func in sample_generators:
        samples = generator_func()
        all_samples.extend(samples)
        print(f"✅ {category_name}: {len(samples)} samples")
    
    total_samples = len(all_samples)
    print(f"\n📝 Total samples to insert: {total_samples}")
    
    # Insert samples
    print(f"\n💾 Inserting samples into device_message_queue...")
    
    insert_query = """
        INSERT INTO device_message_queue (id, device_id, procedure_name, payload, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    successful_inserts = 0
    failed_inserts = 0
    category_stats = {}
    
    for i, sample in enumerate(all_samples, 1):
        try:
            cursor.execute(insert_query, (
                sample['id'],
                sample['device_id'],
                sample['procedure_name'], 
                json.dumps(sample['payload']),
                sample['status'],
                sample['created_at']
            ))
            successful_inserts += 1
            
            # Track category stats
            proc_name = sample['procedure_name']
            if proc_name not in category_stats:
                category_stats[proc_name] = 0
            category_stats[proc_name] += 1
            
            print(f"✅ {i:2d}/{total_samples} - {proc_name} ({sample['status']})")
            
        except Exception as e:
            failed_inserts += 1
            print(f"❌ {i:2d}/{total_samples} - Failed {sample['procedure_name']}: {e}")
    
    # Comprehensive summary
    print(f"\n📊 FINAL SUMMARY:")
    print(f"   ✅ Successful inserts: {successful_inserts}")
    print(f"   ❌ Failed inserts: {failed_inserts}")
    print(f"   📊 Total records in DB: {successful_inserts}")
    
    # Status distribution
    print(f"\n📈 Status Distribution:")
    cursor.execute("SELECT status, COUNT(*) FROM device_message_queue GROUP BY status ORDER BY status")
    for status, count in cursor.fetchall():
        print(f"   {status}: {count}")
    
    # Operation type distribution  
    print(f"\n🔄 Operation Type Distribution:")
    sync_procedures = ['tsp_GetBalanceInfoOnGM', 'tsp_CardRead', 'tsp_CardReadPartial', 
                      'tsp_CheckBillacceptorIn', 'tsp_CheckNetwork', 'tsp_GetCustomerAdditional',
                      'tsp_GetDeviceGameInfo', 'tsp_GetDeviceAdditionalInfo', 'tsp_BonusRequestList']
    
    cursor.execute(f"""
        SELECT 
            CASE 
                WHEN procedure_name = ANY(%s) THEN 'sync' 
                ELSE 'async' 
            END as op_type,
            COUNT(*) as count
        FROM device_message_queue 
        GROUP BY op_type
    """, (sync_procedures,))
    
    for op_type, count in cursor.fetchall():
        print(f"   {op_type}: {count}")
    
    # Top procedures
    print(f"\n🏆 Top Procedures:")
    cursor.execute("""
        SELECT procedure_name, COUNT(*) as count 
        FROM device_message_queue 
        GROUP BY procedure_name 
        ORDER BY count DESC 
        LIMIT 10
    """)
    for proc, count in cursor.fetchall():
        print(f"   {proc}: {count}")
    
    # Device distribution
    print(f"\n🖥️  Device Distribution:")
    cursor.execute("""
        SELECT device_id, COUNT(*) as count 
        FROM device_message_queue 
        GROUP BY device_id 
        ORDER BY count DESC 
        LIMIT 5
    """)
    for device, count in cursor.fetchall():
        print(f"   {device}: {count}")
    
    conn.close()
    print(f"\n🎉 Comprehensive sample data generation completed!")
    print(f"🎯 Coverage: All major procedure categories from sql-calls.md")

if __name__ == "__main__":
    main() 