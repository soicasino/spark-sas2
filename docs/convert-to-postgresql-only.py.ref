#!/usr/bin/env python3
"""
Convert raspberryPython3.py from MSSQL to PostgreSQL-only operation

This script will:
1. Remove all pymssql imports and connections
2. Convert all stored procedure calls to PostgreSQL format
3. Ensure only PostgreSQL connections are used
4. Maintain the async message queue functionality
"""

import re
import os
import shutil
from datetime import datetime

def backup_original_file():
    """Create a backup of the original file"""
    original_file = "raspberryPython3.py"
    backup_file = f"raspberryPython3_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    if os.path.exists(original_file):
        shutil.copy2(original_file, backup_file)
        print(f"✓ Backup created: {backup_file}")
        return backup_file
    else:
        print("✗ Original file not found!")
        return None

def read_file_content(filename):
    """Read the content of the file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"✗ Error reading file: {e}")
        return None

def write_file_content(filename, content):
    """Write content to file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ File updated: {filename}")
        return True
    except Exception as e:
        print(f"✗ Error writing file: {e}")
        return False

def convert_mssql_to_postgresql(content):
    """Convert MSSQL code to PostgreSQL-only"""
    
    print("🔄 Converting MSSQL to PostgreSQL...")
    
    # 1. Remove pymssql imports
    content = re.sub(r'import pymssql.*?\n', '', content)
    content = re.sub(r'#import _mssql.*?\n', '', content)
    
    # 2. Force PostgreSQL to be enabled
    content = re.sub(
        r'G_USE_POSTGRESQL=.*',
        'G_USE_POSTGRESQL=True  # Force PostgreSQL only',
        content
    )
    
    # 3. Replace all pymssql.connect calls with PostgreSQL connections
    mssql_connection_pattern = r'conn = pymssql\.connect\([^)]+\)'
    postgresql_connection = '''conn = psycopg2.connect(
        host=G_PG_Host,
        database=G_PG_Database,
        user=G_PG_User,
        password=G_PG_Password,
        port=G_PG_Port
    )
    conn.autocommit = True'''
    
    content = re.sub(mssql_connection_pattern, postgresql_connection, content, flags=re.MULTILINE | re.DOTALL)
    
    # 4. Replace cursor creation for PostgreSQL
    content = re.sub(
        r'cursor = conn\.cursor\(as_dict=True\)',
        'cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)',
        content
    )
    
    content = re.sub(
        r'cursor = conn\.cursor\(\)',
        'cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)',
        content
    )
    
    # 5. Convert stored procedure calls to PostgreSQL format
    procedure_mappings = {
        'tsp_CheckBillacceptorIn': 'tcasino.tsp_checkbillacceptorin',
        'tsp_InsBillAcceptorMoney': 'tcasino.tsp_insbillacceptormoney',
        'tsp_UpdBillAcceptorMoney': 'tcasino.tsp_updbillacceptormoney',
        'tsp_CardRead': 'tcasino.tsp_cardread',
        'tsp_CardReadPartial': 'tcasino.tsp_cardreadpartial',
        'tsp_CardReadAddMoney': 'tcasino.tsp_cardreadaddmoney',
        'tsp_CardExit': 'tcasino.tsp_cardexit',
        'tsp_InsGameStart': 'tcasino.tsp_insgamestart',
        'tsp_InsGameEnd': 'tcasino.tsp_insgameend',
        'tsp_InsGameStartEnd': 'tcasino.tsp_insgamestartend',
        'tsp_DeviceStatu': 'tcasino.tsp_devicestatu',
        'tsp_UpdDeviceEnablesGames': 'tcasino.tsp_upddeviceenablesgames',
        'tsp_UpdDeviceAdditionalInfo': 'tcasino.tsp_upddeviceadditionalinfo',
        'tsp_GetDeviceAdditionalInfo': 'tcasino.tsp_getdeviceadditionalinfo',
        'tsp_UpdDeviceIsLocked': 'tcasino.tsp_upddeviceislocked',
        'tsp_UpdInsertedBalance': 'tcasino.tsp_updinsertedbalance',
        'tsp_GetBalanceInfoOnGM': 'tcasino.tsp_getbalanceinfoongm',
        'tsp_InsImportantMessage': 'tcasino.tsp_insimportantmessage',
        'tsp_InsException': 'tcasino.tsp_insexception',
        'tsp_InsDeviceDebug': 'tcasino.tsp_insdevicedebug',
        'tsp_InsTraceLog': 'tcasino.tsp_instracelog',
        'tsp_InsReceivedMessage': 'tcasino.tsp_insreceivedmessage',
        'tsp_InsSentCommands': 'tcasino.tsp_inssentcommands'
    }
    
    # Convert procedure calls
    for old_proc, new_proc in procedure_mappings.items():
        # Pattern for EXEC procedure calls
        pattern = rf'cursor\.execute\(\s*["\']EXEC\s+{old_proc}\s*([^"\']*)["\']'
        replacement = rf'cursor.execute("SELECT * FROM {new_proc}(\1)"'
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        # Pattern for direct procedure calls
        pattern = rf'cursor\.execute\(\s*["\']CALL\s+{old_proc}\s*([^"\']*)["\']'
        replacement = rf'cursor.execute("SELECT * FROM {new_proc}(\1)"'
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    # 6. Add PostgreSQL import if not present
    if 'import psycopg2' not in content:
        psycopg2_import = '''try:
    import psycopg2
    import psycopg2.extras
    import uuid
    POSTGRESQL_AVAILABLE = True
except ImportError:
    print("PostgreSQL dependencies not available")
    POSTGRESQL_AVAILABLE = False'''
        
        # Find the first import statement and add after it
        import_match = re.search(r'^import\s+\w+', content, re.MULTILINE)
        if import_match:
            insert_pos = import_match.end()
            content = content[:insert_pos] + '\n' + psycopg2_import + '\n' + content[insert_pos:]
    
    # 7. Update database helper class to use PostgreSQL only
    database_helper_replacement = '''
class DatabaseHelper:
    def __init__(self):
        self.pg_conn = None
        self.last_pg_connect_attempt = None
        
        # Define operations that require immediate response (synchronous)
        self.SYNC_OPERATIONS = {
            'tsp_GetBalanceInfoOnGM',
            'tsp_CardRead',
            'tsp_CardReadPartial', 
            'tsp_CheckBillacceptorIn',
            'tsp_CheckNetwork',
            'tsp_GetCustomerAdditional',
            'tsp_GetDeviceGameInfo',
            'tsp_GetCustomerCurrentMessages',
            'tsp_GetCustomerMessage',
            'tsp_BonusRequestList'
        }
    
    def get_postgresql_connection(self):
        """Get PostgreSQL connection with retry logic"""
        if not POSTGRESQL_AVAILABLE:
            return None
            
        # Don't retry too frequently
        if (self.last_pg_connect_attempt and 
            datetime.datetime.now() - self.last_pg_connect_attempt < datetime.timedelta(seconds=30)):
            return None
            
        try:
            if self.pg_conn is None or self.pg_conn.closed:
                self.pg_conn = psycopg2.connect(
                    host=G_PG_Host,
                    database=G_PG_Database,
                    user=G_PG_User,
                    password=G_PG_Password,
                    port=G_PG_Port,
                    connect_timeout=10
                )
                self.pg_conn.autocommit = True
                print("PostgreSQL connected successfully")
            return self.pg_conn
        except Exception as e:
            self.last_pg_connect_attempt = datetime.datetime.now()
            print(f"PostgreSQL connection failed: {e}")
            return None
    
    def execute_procedure(self, procedure_name, parameters, sas_message=None):
        """Execute PostgreSQL procedure"""
        result = None
        execution_success = False
        error_message = None
        
        # Get PostgreSQL connection
        pg_conn = self.get_postgresql_connection()
        if not pg_conn:
            print("No PostgreSQL connection available")
            return None
            
        try:
            cursor = pg_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Set search path to include tcasino schema
            cursor.execute(f"SET search_path TO tcasino, public;")
            
            # Call the procedure in tcasino schema
            placeholders = ','.join(['%s'] * len(parameters))
            full_procedure_name = f"tcasino.{procedure_name.lower()}"
            cursor.execute(f"SELECT * FROM {full_procedure_name}({placeholders})", parameters)
            result = cursor.fetchall()
            execution_success = True
            
            # Log the procedure call to message queue for async operations
            if procedure_name not in self.SYNC_OPERATIONS:
                self.log_procedure_call(procedure_name, parameters, result, "postgresql", None, sas_message)
            
            return result
        except Exception as e:
            error_message = str(e)
            print(f"PostgreSQL procedure execution failed: {e}")
            return None
    
    def log_procedure_call(self, procedure_name, parameters, result, database_type, error_message, sas_message):
        """Log procedure call to message queue"""
        try:
            pg_conn = self.get_postgresql_connection()
            if not pg_conn:
                return
                
            cursor = pg_conn.cursor()
            
            payload = {
                'procedure_name': procedure_name,
                'parameters': parameters,
                'device_id': getattr(self, 'current_device_id', 'unknown'),
                'sas_message': sas_message,
                'database_type': database_type,
                'execution_result': result,
                'error_message': error_message,
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            cursor.execute("""
                INSERT INTO device_message_queue (device_id, procedure_name, payload, status, created_at)
                VALUES (%s, %s, %s, 'completed', NOW())
            """, (payload['device_id'], procedure_name, json.dumps(payload)))
            
        except Exception as e:
            print(f"Failed to log procedure call: {e}")
'''
    
    # Replace the existing DatabaseHelper class
    content = re.sub(
        r'class DatabaseHelper:.*?(?=\n\n|\nclass|\n#|$)',
        database_helper_replacement,
        content,
        flags=re.DOTALL
    )
    
    # 8. Remove MSSQL fallback logic
    content = re.sub(
        r'# Fallback to MSSQL.*?(?=\n\n|\n    # |\n    def|\nclass)',
        '',
        content,
        flags=re.DOTALL
    )
    
    # 9. Update connection creation functions
    connection_function_replacement = '''
def create_database_connection():
    """Create PostgreSQL database connection"""
    try:
        conn = psycopg2.connect(
            host=G_PG_Host,
            database=G_PG_Database,
            user=G_PG_User,
            password=G_PG_Password,
            port=G_PG_Port,
            connect_timeout=10
        )
        conn.autocommit = True
        return conn
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}")
        return None

def execute_stored_procedure(procedure_name, parameters):
    """Execute stored procedure in PostgreSQL"""
    conn = create_database_connection()
    if not conn:
        return None
        
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(f"SET search_path TO tcasino, public;")
        
        placeholders = ','.join(['%s'] * len(parameters))
        full_procedure_name = f"tcasino.{procedure_name.lower()}"
        cursor.execute(f"SELECT * FROM {full_procedure_name}({placeholders})", parameters)
        
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        print(f"Procedure execution failed: {e}")
        if conn:
            conn.close()
        return None
'''
    
    # Add the connection functions if they don't exist
    if 'def create_database_connection():' not in content:
        # Find a good place to insert (after imports, before main code)
        insert_pos = content.find('G_Static_VersionId=41')
        if insert_pos > 0:
            content = content[:insert_pos] + connection_function_replacement + '\n\n' + content[insert_pos:]
    
    print("✓ MSSQL to PostgreSQL conversion completed")
    return content

def update_configuration_check(content):
    """Update configuration to ensure PostgreSQL is used"""
    
    print("🔄 Updating configuration checks...")
    
    # Force PostgreSQL usage
    config_update = '''
# Force PostgreSQL usage - no MSSQL fallback
G_USE_POSTGRESQL = True
print("PostgreSQL-only mode enabled")

# Ensure PostgreSQL configuration is loaded
if not POSTGRESQL_AVAILABLE:
    print("ERROR: PostgreSQL dependencies not available!")
    print("Please install: pip install psycopg2-binary")
    sys.exit(1)

# Validate PostgreSQL configuration
required_pg_configs = ['G_PG_Host', 'G_PG_Database', 'G_PG_User', 'G_PG_Password', 'G_PG_Port']
for config in required_pg_configs:
    if config not in globals() or not globals()[config]:
        print(f"ERROR: {config} not configured!")
        sys.exit(1)

print(f"PostgreSQL Configuration:")
print(f"  Host: {G_PG_Host}")
print(f"  Database: {G_PG_Database}")
print(f"  User: {G_PG_User}")
print(f"  Port: {G_PG_Port}")
'''
    
    # Find where to insert this (after PostgreSQL config loading)
    insert_pos = content.find('print("Use PostgreSQL:", G_USE_POSTGRESQL)')
    if insert_pos > 0:
        # Find the end of that line
        line_end = content.find('\n', insert_pos)
        content = content[:line_end] + '\n' + config_update + content[line_end:]
    
    print("✓ Configuration checks updated")
    return content

def main():
    """Main conversion function"""
    print("=" * 60)
    print("Converting raspberryPython3.py to PostgreSQL-only operation")
    print("=" * 60)
    
    # Step 1: Backup original file
    backup_file = backup_original_file()
    if not backup_file:
        return False
    
    # Step 2: Read original content
    content = read_file_content("raspberryPython3.py")
    if not content:
        return False
    
    # Step 3: Convert MSSQL to PostgreSQL
    content = convert_mssql_to_postgresql(content)
    
    # Step 4: Update configuration
    content = update_configuration_check(content)
    
    # Step 5: Write updated content
    success = write_file_content("raspberryPython3.py", content)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Conversion completed successfully!")
        print("=" * 60)
        print(f"📁 Original file backed up as: {backup_file}")
        print("🔄 Application now uses PostgreSQL exclusively")
        print("📋 Next steps:")
        print("   1. Test the application: python3 raspberryPython3.py")
        print("   2. Check logs for PostgreSQL connection messages")
        print("   3. Verify all procedures work correctly")
        print("=" * 60)
        return True
    else:
        print("\n❌ Conversion failed!")
        return False

if __name__ == "__main__":
    main() 