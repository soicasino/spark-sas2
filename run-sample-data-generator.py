#!/usr/bin/env python3
"""
Quick runner for the comprehensive sample data generator.
Executes the main generator and provides easy command line interface.
"""

import subprocess
import sys
import os

def main():
    """Run the comprehensive sample data generator"""
    print("🚀 Sample Data Generator Runner")
    print("=" * 40)
    
    # Check if the main script exists
    main_script = "generate-comprehensive-sample-data.py"
    if not os.path.exists(main_script):
        print(f"❌ Error: {main_script} not found in current directory")
        return 1
    
    # Check Python and required modules
    try:
        import psycopg2
        print("✅ psycopg2 module available")
    except ImportError:
        print("❌ Error: psycopg2 module not found")
        print("   Install with: pip install psycopg2-binary")
        return 1
    
    print(f"🔄 Executing {main_script}...")
    print("-" * 40)
    
    try:
        # Execute the main script
        result = subprocess.run([sys.executable, main_script], 
                              capture_output=False, 
                              text=True)
        
        if result.returncode == 0:
            print("\n🎉 Sample data generation completed successfully!")
            return 0
        else:
            print(f"\n❌ Script failed with return code: {result.returncode}")
            return result.returncode
            
    except Exception as e:
        print(f"❌ Error executing script: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 