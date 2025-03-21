from code_checker import CodeChecker
from datetime import datetime, timezone
import json

def test_validation():
    checker = CodeChecker()
    code = input("Enter a code to validate: ")
    
    print("\n--- VALIDATING CODE ---")
    is_valid, user_id, event_type = checker.validate_code(code)
    
    print("\n--- VALIDATION RESULTS ---")
    print(f"Is valid: {is_valid}")
    print(f"User ID: {user_id}")
    print(f"Event type: {event_type}")
    
    if is_valid:
        print("\n--- PROCESSING CODE ---")
        try:
            checker.update_hourly_gym_stats(event_type, datetime.now(timezone.utc))
            print("✅ Updated hourly stats")
            
            checker.update_current_users_in_gym(user_id, event_type)
            print("✅ Updated user status")
            
            print("\n✅ Processing complete.")
        except Exception as e:
            print(f"❌ Error processing code: {e}")
    else:
        print("\n❌ Code is invalid, not processing.")

if __name__ == "__main__":
    test_validation() 