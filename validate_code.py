#!/usr/bin/env python3
import sys
import json
from datetime import datetime, timezone
from code_checker import CodeChecker

def validate(code):
    """
    Validate a code and return result as JSON
    """
    checker = CodeChecker()
    
    # Redirect print statements to stderr for debugging
    original_stdout = sys.stdout
    sys.stdout = sys.stderr
    
    is_valid, user_id, event_type = checker.validate_code(code)
    
    if is_valid:
        # Process the valid code
        checker.update_hourly_gym_stats(event_type, datetime.now(timezone.utc))
        checker.update_current_users_in_gym(user_id, event_type)
    
    # Restore stdout for the JSON result
    sys.stdout = original_stdout
    
    # Return result as JSON
    result = {
        "is_valid": is_valid,
        "user_id": user_id,
        "event_type": event_type
    }
    
    print(json.dumps(result))
    return result

def manual_test():
    """
    Interactive function to manually test code validation
    """
    print("=== Manual Code Checker Testing ===")
    print("Enter 'exit' to quit")
    
    checker = CodeChecker()
    
    while True:
        code = input("\nEnter code to validate: ")
        if code.lower() == 'exit':
            print("Exiting test mode")
            break
            
        print(f"Validating code: {code}")
        is_valid, user_id, event_type = checker.validate_code(code)
        
        if is_valid:
            print(f"\n✅ CODE VALID")
            print(f"User ID: {user_id}")
            print(f"Event Type: {event_type}")
            
            print("\nProcessing code...")
            checker.update_hourly_gym_stats(event_type, datetime.now(timezone.utc))
            checker.update_current_users_in_gym(user_id, event_type)
            print("Code processed successfully")
        else:
            print("\n❌ CODE INVALID")

if __name__ == "__main__":
    # If no arguments provided, run in interactive mode
    if len(sys.argv) < 2:
        manual_test()
    else:
        # Otherwise process the code provided as argument
        code = sys.argv[1]
        validate(code)
