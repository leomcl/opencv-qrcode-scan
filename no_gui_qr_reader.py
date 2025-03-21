import cv2
import time
import csv
from datetime import date, datetime
from picamera2 import Picamera2

def main():
    print("Initializing camera...")
    # Set up the camera
    picam2 = Picamera2()
    config = picam2.create_preview_configuration()
    picam2.configure(config)
    picam2.start()

    # QR code detector
    detector = cv2.QRCodeDetector()

    # For rate limiting detections
    last_detection_time = 0
    cooldown_period = 3  # seconds
    last_data = None

    print("QR code scanner running. Press Ctrl+C to quit.")
    try:
        while True:
            # Capture frame
            frame = picam2.capture_array()

            # Detect and decode QR code
            data, bbox, _ = detector.detectAndDecode(frame)

            # If QR code detected
            current_time = time.time()
            if data and bbox is not None:
                if data != last_data or (current_time - last_detection_time) > cooldown_period:
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