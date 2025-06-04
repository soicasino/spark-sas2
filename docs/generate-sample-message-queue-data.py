#!/usr/bin/env python3
"""
Sample Device Message Queue Data Generator

This script generates sample device_message_queue records for testing and development.
Includes all types of operations (sync/async) with various statuses and realistic parameters.
"""

import json
import uuid
import datetime
import random
import psycopg2
import configparser
import os

# Load PostgreSQL configuration
def load_config():
    config = {
        'host': '10.0.0.59',
        'database': 'postgres', 
        'user': 'postgres',
        'password': 's123',
        'port': 5432,
        'schema': 'tcasino'
    }
    
    # Try to load from config files if they exist
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
                    if key == 'port':
                        config[key] = int(value)
                    else:
                        config[key] = value
            except:
                pass
    
    return config

# Sample data generators
def generate_device_mac():
    """Generate sample MAC addresses"""
    macs = [
        "00:11:22:33:44:55",
        "AA:BB:CC:DD:EE:FF", 
        "12:34:56:78:9A:BC",
        "FF:EE:DD:CC:BB:AA",
        "01:23:45:67:89:AB"
    ]
    return random.choice(macs)

def generate_sas_context():
    """Generate realistic SAS message context"""
    bill_messages = ["02A501C4", "01FF001CA5", "03B201D5", "04C301E6", "05D401F7"]
    sas_commands = ["0120", "0130", "0140", "0150", "0160", "01A0", "01B0", "01C0"]
    
    context = {
        "sas_version_id": random.choice([40, 41, 42, 43]),
    }
    
    # Randomly include different SAS message types
    if random.random() > 0.3:
        context["last_billacceptor_message"] = random.choice(bill_messages)
        if random.random() > 0.5:
            context["last_billacceptor_message_handle"] = context["last_billacceptor_message"]
    
    if random.random() > 0.4:
        context["last_sas_command"] = random.choice(sas_commands)
    
    return context

def generate_sync_operation_samples():
    """Generate sample sync operations (immediate response)"""
    samples = []
    
    # Sync procedures and their typical parameters
    sync_procedures = {
        'tsp_GetBalanceInfoOnGM': lambda mac: [mac, f"123456789{random.randint(0,9)}"],
        'tsp_CardRead': lambda mac: [mac, f"123456789{random.randint(0,9)}", random.randint(1000, 9999)],
        'tsp_CheckBillacceptorIn': lambda mac: [
            mac, random.randint(1, 3), random.randint(10000, 99999),
            f"123456789{random.randint(0,9)}", "USD", "US", 
            random.choice([1, 5, 10, 20, 50, 100]), 
            f"{random.choice([1, 5, 10, 20, 50, 100]):02X}"
        ],
        'tsp_CheckNetwork': lambda mac: [mac],
        'tsp_GetCustomerAdditional': lambda mac: [mac, random.randint(1000, 9999)],
        'tsp_GetDeviceGameInfo': lambda mac: [mac, random.randint(1, 100)],
        'tsp_GetCustomerCurrentMessages': lambda mac: [mac, random.randint(1000, 9999)],
        'tsp_BonusRequestList': lambda mac: [mac, random.randint(1000, 9999), random.randint(1, 10)]
    }
    
    for i in range(10):
        procedure_name = random.choice(list(sync_procedures.keys()))
        device_mac = generate_device_mac()
        parameters = sync_procedures[procedure_name](device_mac)
        
        # Determine status (mostly successful for sync operations)
        status = random.choices(['proc_called', 'proc_failed'], weights=[8, 2])[0]
        
        # Generate realistic results for successful operations
        result_sample = None
        error_message = None
        
        if status == 'proc_called':
            if procedure_name == 'tsp_GetBalanceInfoOnGM':
                result_sample = [{
                    "CustomerBalance": round(random.uniform(0, 1000), 2),
                    "CurrentBalance": round(random.uniform(0, 500), 2),
                    "BonusBalance": round(random.uniform(0, 100), 2)
                }]
            elif procedure_name == 'tsp_CheckBillacceptorIn':
                result_sample = [{
                    "Result": 1,
                    "ErrorMessage": "Bill accepted successfully",
                    "CreditAmount": parameters[6]  # denomination
                }]
            elif procedure_name == 'tsp_CheckNetwork':
                result_sample = [{"NetworkStatus": 1, "ResponseTime": random.randint(10, 200)}]
            else:
                result_sample = [{"Result": 1, "Status": "Success"}]
        else:
            error_message = random.choice([
                "Connection timeout",
                "Invalid card number", 
                "Database constraint violation",
                "Bill acceptor error",
                "Network unreachable"
            ])
        
        payload = {
            'procedure_name': procedure_name,
            'parameters': parameters,                    # ✓ REQUIRED: Procedure Parameters
            'device_id': device_mac,                     # ✓ REQUIRED: Device ID/MAC
            'timestamp': (datetime.datetime.now() - datetime.timedelta(
                minutes=random.randint(0, 1440)
            )).isoformat(),
            'database_used': random.choice(['postgresql', 'mssql']),
            'execution_type': 'synchronous',
            'result_count': len(result_sample) if result_sample else 0,
            'error_message': error_message,
            'sas_message': generate_sas_context()        # ✓ REQUIRED: SAS Message Context
        }
        
        if result_sample and len(str(result_sample)) < 1000:
            payload['result_sample'] = result_sample
        
        samples.append({
            'id': str(uuid.uuid4()),
            'device_id': device_mac,
            'procedure_name': procedure_name,
            'payload': payload,
            'status': status,
            'created_at': payload['timestamp']
        })
    
    return samples

def generate_async_operation_samples():
    """Generate sample async operations (queued)"""
    samples = []
    
    # Async procedures and their typical parameters
    async_procedures = {
        'tsp_InsGameStart': lambda mac: [
            mac, random.randint(1000, 9999), random.randint(1, 100),
            round(random.uniform(1, 50), 2), "REGULAR", random.randint(0, 5)
        ],
        'tsp_InsGameEnd': lambda mac: [
            mac, random.randint(1000, 9999), random.randint(1, 100),
            round(random.uniform(0, 100), 2), round(random.uniform(0, 10), 2)
        ],
        'tsp_InsDeviceMeter': lambda mac: [
            mac, "COIN_IN", round(random.uniform(1000, 5000), 2),
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ],
        'tsp_InsImportantMessage': lambda mac: [
            mac, random.choice([
                "Game started", "Game ended", "Bill inserted", "Card inserted",
                "Network error", "Low hopper", "Door opened", "Tilt occurred"
            ]), random.randint(100, 999), random.randint(0, 3), random.randint(1000, 9999)
        ],
        'tsp_UpdDeviceAdditionalInfo': lambda mac: [
            mac, f"GAME_VERSION_{random.randint(1,10)}", 
            json.dumps({"version": f"1.{random.randint(0,9)}", "build": random.randint(1000, 9999)})
        ],
        'tsp_InsException': lambda mac: [
            mac, random.choice([
                "Network timeout", "Database error", "Hardware malfunction",
                "SAS protocol error", "Card reader error", "Bill acceptor jam"
            ]), "ERROR", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ]
    }
    
    statuses = ['pending', 'processing', 'completed', 'failed']
    status_weights = [3, 2, 4, 1]  # More completed, fewer failed
    
    for i in range(10):
        procedure_name = random.choice(list(async_procedures.keys()))
        device_mac = generate_device_mac()
        parameters = async_procedures[procedure_name](device_mac)
        status = random.choices(statuses, weights=status_weights)[0]
        
        payload = {
            'procedure_name': procedure_name,
            'parameters': parameters,                    # ✓ REQUIRED: Procedure Parameters
            'device_id': device_mac,                     # ✓ REQUIRED: Device ID/MAC
            'timestamp': (datetime.datetime.now() - datetime.timedelta(
                minutes=random.randint(0, 2880)  # Up to 2 days ago
            )).isoformat(),
            'sas_message': generate_sas_context()        # ✓ REQUIRED: SAS Message Context
        }
        
        # Add processing info for non-pending messages
        if status != 'pending':
            payload['processed_at'] = (datetime.datetime.now() - datetime.timedelta(
                minutes=random.randint(0, 1440)
            )).isoformat()
            
        if status == 'failed':
            payload['error_message'] = random.choice([
                "Database connection failed",
                "Invalid parameter format",
                "Constraint violation", 
                "Timeout during processing",
                "Unknown procedure error"
            ])
        
        samples.append({
            'id': str(uuid.uuid4()),
            'device_id': device_mac,
            'procedure_name': procedure_name,
            'payload': payload,
            'status': status,
            'created_at': payload['timestamp']
        })
    
    return samples

def generate_special_cases():
    """Generate special edge cases and scenarios"""
    samples = []
    
    # Large parameter case
    device_mac = generate_device_mac()
    large_message = "X" * 500  # Large message
    payload = {
        'procedure_name': 'tsp_InsImportantMessage',
        'parameters': [device_mac, large_message, 999, 1, 1234],
        'device_id': device_mac,
        'timestamp': datetime.datetime.now().isoformat(),
        'sas_message': generate_sas_context()
    }
    
    samples.append({
        'id': str(uuid.uuid4()),
        'device_id': device_mac,
        'procedure_name': 'tsp_InsImportantMessage',
        'payload': payload,
        'status': 'completed',
        'created_at': payload['timestamp']
    })
    
    # No SAS context case (rare but possible)
    device_mac = generate_device_mac()
    payload = {
        'procedure_name': 'tsp_CheckNetwork',
        'parameters': [device_mac],
        'device_id': device_mac,
        'timestamp': datetime.datetime.now().isoformat(),
        'database_used': 'postgresql',
        'execution_type': 'synchronous',
        'result_count': 1,
        'error_message': None
        # Note: intentionally no sas_message for this edge case
    }
    
    samples.append({
        'id': str(uuid.uuid4()),
        'device_id': device_mac,
        'procedure_name': 'tsp_CheckNetwork',
        'payload': payload,
        'status': 'proc_called',
        'created_at': payload['timestamp']
    })
    
    return samples

def main():
    """Generate and insert sample data"""
    print("🎰 Device Message Queue Sample Data Generator")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    print(f"📊 Configuration: {config['host']}:{config['port']} -> {config['database']}")
    
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
    
    # Generate sample data
    print("\n🔄 Generating sample data...")
    
    sync_samples = generate_sync_operation_samples()
    print(f"✅ Generated {len(sync_samples)} sync operation samples")
    
    async_samples = generate_async_operation_samples() 
    print(f"✅ Generated {len(async_samples)} async operation samples")
    
    special_samples = generate_special_cases()
    print(f"✅ Generated {len(special_samples)} special case samples")
    
    all_samples = sync_samples + async_samples + special_samples
    total_samples = len(all_samples)
    
    print(f"\n📝 Total samples to insert: {total_samples}")
    
    # Insert samples
    print("\n💾 Inserting samples into device_message_queue...")
    
    insert_query = """
        INSERT INTO device_message_queue (id, device_id, procedure_name, payload, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    successful_inserts = 0
    failed_inserts = 0
    
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
            print(f"✅ {i:2d}/{total_samples} - {sample['procedure_name']} ({sample['status']})")
            
        except Exception as e:
            failed_inserts += 1
            print(f"❌ {i:2d}/{total_samples} - Failed: {e}")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   ✅ Successful inserts: {successful_inserts}")
    print(f"   ❌ Failed inserts: {failed_inserts}")
    print(f"   📊 Total records: {successful_inserts}")
    
    # Query verification
    print(f"\n🔍 Verification queries:")
    
    # Count by status
    cursor.execute("SELECT status, COUNT(*) FROM device_message_queue GROUP BY status ORDER BY status")
    status_counts = cursor.fetchall()
    print(f"   Status distribution:")
    for status, count in status_counts:
        print(f"     {status}: {count}")
    
    # Count by procedure type
    cursor.execute("""
        SELECT 
            CASE 
                WHEN procedure_name IN ('tsp_GetBalanceInfoOnGM', 'tsp_CardRead', 'tsp_CheckBillacceptorIn', 'tsp_CheckNetwork', 'tsp_GetCustomerAdditional') 
                THEN 'sync' 
                ELSE 'async' 
            END as op_type,
            COUNT(*) as count
        FROM device_message_queue 
        GROUP BY op_type
    """)
    type_counts = cursor.fetchall()
    print(f"   Operation type distribution:")
    for op_type, count in type_counts:
        print(f"     {op_type}: {count}")
    
    # Recent messages
    cursor.execute("""
        SELECT procedure_name, status, created_at 
        FROM device_message_queue 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    recent = cursor.fetchall()
    print(f"   Recent messages:")
    for proc, status, created in recent:
        print(f"     {created} - {proc} ({status})")
    
    conn.close()
    print(f"\n🎉 Sample data generation completed!")

if __name__ == "__main__":
    main() 