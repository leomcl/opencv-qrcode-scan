import cv2
import time
import csv
from datetime import date, datetime
from picamera2 import Picamera2
from pyzbar.pyzbar import decode

def main():
    print("Initializing camera...")
    # Set up the camera
    picam2 = Picamera2()
    config = picam2.create_preview_configuration()
    picam2.configure(config)
    picam2.start()

    # For rate limiting detections
    last_detection_time = 0
    cooldown_period = 3  # seconds
    last_data = None

    print("QR code scanner running. Press Ctrl+C to quit.")
    try:
        while True:
            # Capture frame
            frame = picam2.capture_array()
            
            # Convert to grayscale for better detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect and decode QR codes
            decoded_objects = decode(gray)
            
            # Current time for rate limiting
            current_time = time.time()
            
            # Process detected QR codes
            for obj in decoded_objects:
                data = obj.data.decode('utf-8')
                
                if data and (data != last_data or (current_time - last_detection_time) > cooldown_period):
                    now = datetime.now()
                    timestamp = now.strftime("%H:%M:%S")
                    today = date.today()
                    datestamp = today.strftime("%d-%b-%Y")
                    
                    print(f"Data found: {data} | Date: {datestamp} | Time: {timestamp}")
                    
                    # Save to CSV
                    try:
                        with open('Database.csv', mode='a') as csvfile:
                            csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                            csv_writer.writerow([data, datestamp, timestamp])
                    except Exception as e:
                        print(f"Error writing to CSV: {e}")
                    
                    last_detection_time = current_time
                    last_data = data
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nQR code scanner stopped by user.")
    finally:
        picam2.close()
        print("Camera released.")

if __name__ == "__main__":
    main() 