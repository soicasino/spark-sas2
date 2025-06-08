#!/usr/bin/env python3
"""
Example API Response Test - Shows what the meter endpoints will return
"""

# This is what you'll get when calling /api/meters/basic
example_meter_response = {
    "success": True,
    "message": "Successfully retrieved 8 meter values",
    "timestamp": "2024-01-15T10:30:45.123456",
    "execution_time_ms": 2340.5,
    "meter_type": "basic",
    "status": "success",
    "meters": {
        "total_turnover": 152450.75,      # Raw numeric values
        "total_win": 142800.25,
        "total_jackpot": 5420.00,
        "current_credits": 125.50,
        "games_played": 1542,
        "games_won": 1284,
        "bills_accepted": 234,
        "total_bonus": 1250.75
    },
    "formatted_display": {                # Human-readable formatted values
        "total_turnover": "152,450.75 TL",
        "total_win": "142,800.25 TL", 
        "total_jackpot": "5,420.00 TL",
        "current_credits": "125.50 TL",
        "games_played": "1,542",
        "games_won": "1,284",
        "bills_accepted": "234",
        "total_bonus": "1,250.75 TL"
    }
}

# This is what you'll get if no meter data is received
no_data_response = {
    "success": False,
    "message": "Meter command sent but no response received within timeout",
    "timestamp": "2024-01-15T10:30:45.123456",
    "execution_time_ms": 8000.0,
    "meter_type": "basic",
    "status": "no_data",
    "meters": {},
    "formatted_display": {},
    "note": "Check SAS communication and slot machine connection"
}

# This is what you'll get on error
error_response = {
    "success": False,
    "message": "SAS communication not available",
    "timestamp": "2024-01-15T10:30:45.123456",
    "execution_time_ms": 45.2
}

print("=== Expected API Responses ===")
print()
print("1. Successful meter response:")
print("   GET /api/meters/basic")
print("   Response:")
import json
print(json.dumps(example_meter_response, indent=2))

print()
print("2. No data response (timeout):")
print(json.dumps(no_data_response, indent=2))

print()
print("3. Error response:")
print(json.dumps(error_response, indent=2))

print()
print("=== JavaScript Usage Example ===")
print("""
// Fetch meters from your Next.js frontend
async function getSlotMachineMeters() {
  try {
    const response = await fetch('http://localhost:8000/api/meters/basic');
    const data = await response.json();
    
    if (data.success) {
      console.log('Raw meter values:', data.meters);
      console.log('Formatted for display:', data.formatted_display);
      
      // Use in your UI
      document.getElementById('total-turnover').textContent = data.formatted_display.total_turnover;
      document.getElementById('current-credits').textContent = data.formatted_display.current_credits;
      document.getElementById('games-played').textContent = data.formatted_display.games_played;
      
    } else {
      console.error('Failed to get meters:', data.message);
      // Handle error in UI
    }
    
  } catch (error) {
    console.error('Network error:', error);
  }
}

// Call every 10 seconds to update the display
setInterval(getSlotMachineMeters, 10000);
""") 