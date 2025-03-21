import cv2
import csv
from datetime import date, datetime

def main():
    # Get current date and time
    today = date.today()
    current_date = today.strftime("%d-%b-%Y")
    
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    
    # Initialize camera
    print("Initializing camera...")
    cap = cv2.VideoCapture(0)
    
    # Check if camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    # Initialize QR code detector
    detector = cv2.QRCodeDetector()
    
    print("QR code scanner running. Press 'q' to quit.")
    
    while True:
        # Capture frame
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Can't receive frame from camera")
            break
        
        # Detect and decode QR code
        data, bbox, _ = detector.detectAndDecode(frame)
        
        # If QR code detected
        if bbox is not None:
            # Convert to integer points
            bbox = bbox.astype(int)
            
            # Draw bounding box
            for i in range(len(bbox[0])):
                p1 = tuple(bbox[0][i])
                p2 = tuple(bbox[0][(i+1) % len(bbox[0])])
                cv2.line(frame, p1, p2, (255, 0, 0), 2)
            
            # If data decoded
            if data:
                print(f"Data found: {data} | Date: {current_date} | Time: {current_time}")
                
                # Add text to image
                cv2.putText(frame, data, (bbox[0][0][0], bbox[0][0][1] - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Save to CSV file
                try:
                    with open('Database.csv', mode='a') as csvfile:
                        csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
                        csv_writer.writerow([data, current_date, current_time])
                except Exception as e:
                    print(f"Error writing to CSV: {e}")
        
        # Display result
        cv2.imshow("QR Code Scanner", frame)
        
        # Check for 'q' key to exit
        if cv2.waitKey(1) == ord('q'):
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    print("QR code scanner stopped.")

if __name__ == "__main__":
    main() 