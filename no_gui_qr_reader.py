import cv2
import csv
import time
from datetime import date, datetime
from picamera2 import Picamera2

def main():
    # Get current date and time
    today = date.today()
    current_date = today.strftime("%d-%b-%Y")
    
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    
    # Initialize camera
    print("Initializing camera...")
    picam2 = Picamera2()
    config = picam2.create_preview_configuration()
    picam2.configure(config)
    picam2.start()
    
    # Initialize QR code detector
    detector = cv2.QRCodeDetector()
    
    print("QR code scanner running. Press Ctrl+C to quit.")
    
    # For rate limiting detections
    last_detection_time = 0
    cooldown_period = 3  # seconds between registering the same code
    last_data = None
    
    try:
        while True:
            # Capture frame
            frame = picam2.capture_array()
            
            # Detect and decode QR code
            data, bbox, _ = detector.detectAndDecode(frame)
            
            # If QR code detected with data
            current_time = time.time()
            if data and bbox is not None:
                # Only register if it's a new code or enough time has passed
                if data != last_data or (current_time - last_detection_time) > cooldown_period:
                    now = datetime.now()
                    timestamp = now.strftime("%H:%M:%S")
                    today = date.today()
                    datestamp = today.strftime("%d-%b-%Y")
                    
                    print(f"Data found: {data} | Date: {datestamp} | Time: {timestamp}")
                    
                    # Save to CSV file
                    try:
                        with open('Database.csv', mode='a') as csvfile:
                            csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                            csv_writer.writerow([data, datestamp, timestamp])
                    except Exception as e:
                        print(f"Error writing to CSV: {e}")
                    
                    # Update tracking variables
                    last_detection_time = current_time
                    last_data = data
            
            # Short delay to prevent maxing out CPU
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nQR code scanner stopped by user.")
    finally:
        # Release resources
        picam2.close()
        print("Camera released.")

if __name__ == "__main__":
    main() 