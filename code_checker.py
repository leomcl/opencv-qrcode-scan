import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timezone

class CodeChecker:
    """
    A class for validating gym access codes and tracking gym statistics
    Can be imported and used by other applications like a scanner
    """
    
    def __init__(self, credential_path="fir-auth-458d1-firebase-adminsdk-2hr0x-ed20179b15.json"):
        """
        Initialize the CodeChecker with Firebase connection
        
        Args:
            credential_path: Path to the Firebase credentials JSON file
        """
        # Initialize the Firebase app if it's not already initialized
        try:
            self.cred = credentials.Certificate(credential_path)
            self.app = firebase_admin.initialize_app(self.cred)
        except ValueError:
            # App already exists, get the default app
            self.app = firebase_admin.get_app()
            
        # Firestore client
        self.db = firestore.client()
    
    def validate_code(self, code: str):
        """
        Validate an entry code and delete it if valid
        
        Args:
            code: The access code to validate
            
        Returns:
            tuple: (is_valid, user_id, code_type)
        """
        if not code:
            print('Please enter an entry access code.')
            return False, None, None

        try:
            # Fetch the document from Firestore with the given code
            doc_ref = self.db.collection('gymAccessCodes').document(code)
            doc = doc_ref.get()

            if not doc.exists:
                print(f'Invalid code. The code {code} does not exist.')
                return False, None, None

            # Extract data from the document and check expiry time
            data = doc.to_dict()
            expiry_time = data.get('expiryTime') 
            user_id = data.get('userId')
            code_type = data.get('type')
            print(f'code: {code_type}')

            if not expiry_time:
                print("No expiry time found in document.")
                return False, None, None

            # Make current time UTC-aware using built-in timezone
            current_time = datetime.now(timezone.utc)
            
            # Debug information
            print(f"Expiry time: {expiry_time}, Type: {type(expiry_time)}")
            print(f"Current time: {current_time}, Type: {type(current_time)}")
            
            # Check if code has expired
            if expiry_time < current_time:
                print("Code has expired. Deleting document...")
                doc_ref.delete()
                print('This code has expired and has been deleted.')
                return False, None, None
            else:
                # If the code is valid, log the entry and delete the document
                print(f"Code is valid. User ID: {user_id}. Type: {code_type}")
                # Delete the code AFTER confirming it's valid
                doc_ref.delete()
                return True, user_id, code_type

        except Exception as e:
            print(f'An error occurred: {str(e)}')
            return False, None, None

    def update_hourly_gym_stats(self, event_type: str, event_time: datetime):
        """
        Update hourly gym statistics based on entry/exit events
        
        Args:
            event_type: 'enter' or 'exit'
            event_time: The time of the event
        """
        # Generate the hour bucket in the format "yyyy-MM-dd-HH"
        hour_bucket = f'{event_time.year}-{event_time.month:02d}-{event_time.day:02d}-{event_time.hour:02d}'

        doc_ref = self.db.collection('gymHourlyStats').document(hour_bucket)

        @firestore.transactional
        def transaction_update(transaction, doc_ref, event_type):
            doc = doc_ref.get(transaction=transaction)
            
            if not doc.exists:
                # If it's a new hour, initialize the document
                initial_data = {
                    'entries': 1 if event_type == 'enter' else 0,
                    'exits': 1 if event_type == 'exit' else 0,
                    'last_updated': event_time
                }
                transaction.set(doc_ref, initial_data)
            else:
                # If the document exists, update the counts
                current_data = doc.to_dict()
                if event_type == 'enter':
                    new_entries = current_data.get('entries', 0) + 1
                    transaction.update(doc_ref, {'entries': new_entries, 'last_updated': event_time})
                elif event_type == 'exit':
                    new_exits = current_data.get('exits', 0) + 1
                    transaction.update(doc_ref, {'exits': new_exits, 'last_updated': event_time})

        # Use Firestore transaction to ensure atomic updates
        transaction = self.db.transaction()
        transaction_update(transaction, doc_ref, event_type)

    def update_current_users_in_gym(self, user_id: str, event_type: str):
        """
        Update the current users in the gym based on entry/exit events
        
        Args:
            user_id: The ID of the user
            event_type: 'enter' or 'exit'
        """
        # Reference to the specific user's document in the usersInGym collection
        user_doc_ref = self.db.collection('usersInGym').document(user_id)
        
        if event_type == 'enter':
            # Set up the entry data for the user
            entry_data = {
                'entryTime': datetime.now(timezone.utc),
                'userId': user_id,  # Store the user ID in the document as well
                'status': 'active',
                'duration': None,
                'workoutType': None,
                'workoutTags': {
                    'cardio': None,
                    'legs': None,
                    'arms': None,
                    'chest': None
                },
                'lastUpdated': datetime.now(timezone.utc)
            }
            
            # Use set() to create or overwrite the document for the user
            user_doc_ref.set(entry_data)
            print(f"User {user_id} has entered the gym. Entry data recorded.")
            
        elif event_type == 'exit':
            # For exit, delete the document for the user
            try:
                user_doc_ref.delete()
                print(f"User {user_id} has exited the gym. Document deleted.")
            except Exception as e:
                print(f"Error deleting document for user {user_id}: {str(e)}")
    
    def process_code(self, code: str):
        """
        Process a code completely - validate and update all relevant data
        
        Args:
            code: The access code to process
            
        Returns:
            bool: Whether the code was valid
        """
        is_valid, user_id, event_type = self.validate_code(code)

        if is_valid:
            print(f"Processing valid code for user {user_id} with event type: {event_type}")
            # Make sure we're passing the exact event_type from Firebase
            self.update_hourly_gym_stats(event_type, datetime.now(timezone.utc))
            self.update_current_users_in_gym(user_id, event_type)
            return True
        return False

# Main code to validate entry if script is run directly
if __name__ == "__main__":
    checker = CodeChecker()
    code = input('Enter code: ')
    if checker.process_code(code):
        print('Code accepted and processed')
    else:
        print('Invalid code')
