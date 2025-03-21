import cv2
import time
import csv
from datetime import date, datetime
from picamera2 import Picamera2
from pyzbar.pyzbar import decode

def main():
    print("Initializing camera...")
    # Set up the camera with higher resolution for better detection
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (1280, 720)})  # Higher resolution
    picam2.configure(config)
    picam2.start()
    
    print("Adjusting camera settings...")
    time.sleep(2)  # Give camera time to adjust

    # For rate limiting detections
    last_detection_time = 0
    cooldown_period = 3  # seconds
    last_data = None
    scan_count = 0
    
    print("QR code scanner running. Press Ctrl+C to quit.")
    print("Waiting for QR codes...")
    
    try:
        while True:
            # Capture frame
            frame = picam2.capture_array()
            
            # Convert to grayscale for better detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding to improve contrast
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Try both the regular grayscale and the threshold image
            decoded_objects = decode(gray) or decode(thresh)
            
            scan_count += 1
            if scan_count % 50 == 0:  # Print status every 50 frames
                print(f"Still scanning... ({scan_count} frames processed)")
            
            # Current time for rate limiting
            current_time = time.time()
            
            # Process detected QR codes
            for obj in decoded_objects:
                try:
                    data = obj.data.decode('utf-8')
                    
                    if data and (data != last_data or (current_time - last_detection_time) > cooldown_period):
                        now = datetime.now()
                        timestamp = now.strftime("%H:%M:%S")
                        today = date.today()
                        datestamp = today.strftime("%d-%b-%Y")
                        
                        print(f"Data found: {data} | Date: {datestamp} | Time: {timestamp}")
                        print(f"QR Type: {obj.type}, Position: {obj.rect}")
                        
                        # Save to CSV
                        try:
                            with open('Database.csv', mode='a') as csvfile:
                                csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                                csv_writer.writerow([data, datestamp, timestamp])
                        except Exception as e:
                            print(f"Error writing to CSV: {e}")
                        
                        last_detection_time = current_time
                        last_data = data
                        scan_count = 0  # Reset counter after successful scan
                except Exception as e:
                    print(f"Error decoding QR: {e}")
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nQR code scanner stopped by user.")
    finally:
        picam2.close()
        print("Camera released.")
        print(f"Total frames processed: {scan_count}")

if __name__ == "__main__":
    main()
