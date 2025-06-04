#!/usr/bin/env python3
"""
Fixed Device Message Queue Sample Data Generator

Uses existing slot machine IDs from the database to avoid foreign key constraint violations.
"""

import json
import uuid
import datetime
import random
import psycopg2
import os

def load_config():
    """Load PostgreSQL configuration from files or use defaults"""
    config = {
        'host': '10.0.0.59',
        'database': 'postgres', 
        'user': 'postgres',
        'password': 's123',
        'port': 5432,
        'schema': 'public'
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

def get_available_slot_machines(cursor):
    """Get available slot machine IDs from the database"""
    cursor.execute("SELECT id, mac_address FROM slot_machines LIMIT 20")
    return cursor.fetchall()

def generate_card_number():
    """Generate realistic card numbers"""
    return f"{random.randint(1000000000, 9999999999)}"

def generate_sas_context():
    """Generate realistic SAS message context"""
    bill_messages = [
        "02A501C4", "01FF001CA5", "03B201D5", "04C301E6", "05D401F7"
    ]
    
    sas_commands = [
        "0120", "0130", "0140", "0150", "0160", "01A0", "01B0", "01C0"
    ]
    
    context = {
        "sas_version_id": random.choice([40, 41, 42, 43, 44])
    }
    
    if random.random() > 0.2:
        context["last_billacceptor_message"] = random.choice(bill_messages)
    
    if random.random() > 0.3:
        context["last_sas_command"] = random.choice(sas_commands)
    
    return context

def generate_samples(available_machines):
    """Generate sample data using existing slot machine IDs"""
    samples = []
    
    # Sample procedures with their parameter generators
    procedures = [
        ('tsp_CheckBillacceptorIn', lambda mac: [mac, 1, 12345, generate_card_number(), "USD", "US", 20, "14"]),
        ('tsp_CardRead', lambda mac: [mac, generate_card_number(), 100.0, 10.0, 1, 123]),
        ('tsp_InsGameStart', lambda mac: [mac, 12345, 10.0, 5.0, 10.0, "REGULAR", 0, 50, 2.5, 123]),
        ('tsp_InsGameEnd', lambda mac: [mac, 12345, 15.0, 50, 1234, 25.0, 123, 5.0, 10.0, 150.0]),
        ('tsp_DeviceStatu', lambda mac: [mac, 1, "192.168.1.100", 42, 1, 1, "COM1", "COM2", "ONLINE"]),
        ('tsp_InsImportantMessage', lambda mac: [mac, "Game started successfully", 100, 1, 1234]),
        ('tsp_InsException', lambda mac: [mac, "NetworkTimeout", "Connection timeout after 30 seconds"]),
        ('tsp_GetBalanceInfoOnGM', lambda mac: [mac, generate_card_number()]),
        ('tsp_UpdDeviceIsLocked', lambda mac: [123, 0]),
        ('tsp_InsMoneyUpload', lambda mac: [1234, generate_card_number(), 50.0, "CASH_IN", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 1])
    ]
    
    # Generate 8 samples per procedure (80 total)
    for procedure_name, param_generator in procedures:
        for i in range(8):
            # Pick a random slot machine
            machine_id, machine_mac = random.choice(available_machines)
            
            # Generate parameters
            parameters = param_generator(machine_mac)
            
            # Determine if sync or async
            is_sync = procedure_name in ['tsp_CheckBillacceptorIn', 'tsp_CardRead', 'tsp_GetBalanceInfoOnGM']
            
            # Generate status
            if is_sync:
                status = random.choices(['proc_called', 'proc_failed'], weights=[8, 2])[0]
            else:
                status = random.choices(['pending', 'processing', 'completed', 'failed'], weights=[2, 1, 6, 1])[0]
            
            # Create payload
            payload = {
                'procedure_name': procedure_name,
                'parameters': parameters,
                'device_id': machine_mac,
                'timestamp': (datetime.datetime.now() - datetime.timedelta(
                    minutes=random.randint(0, 2880)
                )).isoformat(),
                'sas_message': generate_sas_context()
            }
            
            if is_sync:
                payload.update({
                    'database_used': random.choice(['postgresql', 'mssql']),
                    'execution_type': 'synchronous',
                    'result_count': random.randint(0, 5),
                    'error_message': None
                })
            
            # Create record
            record = {
                'id': str(uuid.uuid4()),
                'slot_machine_id': machine_id,  # Use the actual slot machine ID
                'procedure_name': procedure_name,
                'payload': payload,
                'status': status,
                'created_at': payload['timestamp']
            }
            
            samples.append(record)
    
    return samples

def main():
    """Generate sample data with existing slot machine IDs"""
    print("🎰 FIXED Device Message Queue Sample Data Generator")
    print("=" * 60)
    print("🔧 Using existing slot machine IDs to avoid foreign key violations")
    
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
    
    # Get available slot machines
    print(f"\n🔍 Getting available slot machines...")
    available_machines = get_available_slot_machines(cursor)
    if not available_machines:
        print("❌ No slot machines found in database. Please add some slot machines first.")
        return
    
    print(f"✅ Found {len(available_machines)} slot machines")
    for machine_id, mac in available_machines[:5]:  # Show first 5
        print(f"   - {machine_id[:8]}... (MAC: {mac})")
    
    # Generate sample data
    print(f"\n🔄 Generating sample data...")
    samples = generate_samples(available_machines)
    print(f"📝 Generated {len(samples)} samples")
    
    # Insert samples
    print(f"\n💾 Inserting samples into device_messages_queue...")
    
    insert_query = """
        INSERT INTO device_messages_queue (id, slot_machine_id, procedure_name, payload, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    successful_inserts = 0
    failed_inserts = 0
    
    for i, sample in enumerate(samples, 1):
        try:
            cursor.execute(insert_query, (
                sample['id'],
                sample['slot_machine_id'],
                sample['procedure_name'], 
                json.dumps(sample['payload']),
                sample['status'],
                sample['created_at']
            ))
            successful_inserts += 1
            print(f"✅ {i:2d}/{len(samples)} - {sample['procedure_name']} ({sample['status']})")
            
        except Exception as e:
            failed_inserts += 1
            print(f"❌ {i:2d}/{len(samples)} - Failed {sample['procedure_name']}: {e}")
    
    # Summary
    print(f"\n📊 FINAL SUMMARY:")
    print(f"   ✅ Successful inserts: {successful_inserts}")
    print(f"   ❌ Failed inserts: {failed_inserts}")
    
    if successful_inserts > 0:
        # Status distribution
        print(f"\n📈 Status Distribution:")
        cursor.execute("SELECT status, COUNT(*) FROM device_messages_queue GROUP BY status ORDER BY status")
        for status, count in cursor.fetchall():
            print(f"   {status}: {count}")
        
        # Top procedures
        print(f"\n🏆 Top Procedures:")
        cursor.execute("""
            SELECT procedure_name, COUNT(*) as count 
            FROM device_messages_queue 
            GROUP BY procedure_name 
            ORDER BY count DESC 
            LIMIT 5
        """)
        for proc, count in cursor.fetchall():
            print(f"   {proc}: {count}")
    
    conn.close()
    print(f"\n🎉 Sample data generation completed!")

if __name__ == "__main__":
    main() 