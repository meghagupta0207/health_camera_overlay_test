"""
Clinical Overlay and Capture System - Phone Camera Support
Simple capture system with overlay guides.
Supports both webcam and phone camera via IP.
"""
import cv2
import time
import sys
import os
from overlay import OverlayRenderer


# Global variables for mouse interaction
button_clicked = False
button_rect = None


def mouse_callback(event, x, y, flags, param):
    """Handle mouse clicks on the capture button."""
    global button_clicked, button_rect
    
    if event == cv2.EVENT_LBUTTONDOWN and button_rect:
        bx, by, bw, bh = button_rect
        if bx <= x <= bx + bw and by <= y <= by + bh:
            button_clicked = True


def get_camera_source():
    """
    Prompt user to select camera source.
    
    Returns:
        Camera source (int or string)
    """
    print("\n" + "="*50)
    print("SELECT CAMERA SOURCE")
    print("="*50)
    print("1. Webcam (default)")
    print("2. Phone Camera (IP Webcam)")
    print("="*50)
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "2":
        print("\nEnter your phone's IP address from IP Webcam app")
        print("Example: 192.168.1.100:8080")
        ip = input("IP Address: ").strip()
        
        # Support multiple formats
        if not ip.startswith("http"):
            ip = f"http://{ip}"
        if not ip.endswith("/video"):
            ip = f"{ip}/video"
        
        print(f"Connecting to: {ip}")
        return ip
    else:
        return 0


def main():
    """Main application loop."""
    global button_clicked, button_rect
    
    # Get camera source
    camera_source = get_camera_source()
    
    # Initialize camera
    cap = cv2.VideoCapture(camera_source)
    
    if not cap.isOpened():
        print("ERROR: Cannot open camera")
        print("\nTroubleshooting:")
        print("- Check that IP Webcam is running on your phone")
        print("- Verify both devices are on the same WiFi network")
        print("- Ensure IP address is correct")
        return
    
    # Read first frame to get dimensions
    ret, frame = cap.read()
    if not ret:
        print("ERROR: Cannot read from camera")
        cap.release()
        return
    
    height, width = frame.shape[:2]
    print(f"\n✓ Camera initialized: {width}x{height}")
    
    # Create captures directory if it doesn't exist
    captures_dir = "captured_images"
    if not os.path.exists(captures_dir):
        os.makedirs(captures_dir)
        print(f"✓ Created directory: {captures_dir}")
    else:
        print(f"✓ Using existing directory: {captures_dir}")
    
    # Initialize components
    renderer = OverlayRenderer(width, height)
    
    overlay_config = renderer.get_config()
    
    print("\n" + "="*50)
    print("SYSTEM READY")
    print("="*50)
    print("Instructions:")
    print("1. Align ₹1 coin inside the green circle")
    print("2. Position lesion inside the green rectangle")
    print("3. CLICK CAPTURE BUTTON or press SPACEBAR")
    print("4. Press 'Q' to quit")
    print("="*50 + "\n")
    
    # Setup mouse callback
    cv2.namedWindow("Clinical Capture System")
    cv2.setMouseCallback("Clinical Capture System", mouse_callback)
    
    captured = False
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("WARNING: Frame dropped")
            continue
        
        # If already captured, show frozen frame
        if captured:
            # Draw overlay
            frame = renderer.draw_static_guides(frame)
            frame = renderer.show_feedback(
                frame, 
                "CAPTURED SUCCESSFULLY - Press Q to exit",
                (0, 255, 255)  # Cyan
            )
            cv2.imshow("Clinical Capture System", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue
        
        # Draw static overlay guides
        frame = renderer.draw_static_guides(frame)
        
        # Show feedback
        message = "Align coin and lesion in guides"
        color = (0, 255, 0)  # Green
        frame = renderer.show_feedback(frame, message, color)
        
        # Show CAPTURE BUTTON (always visible)
        # Button dimensions
        button_width = 200
        button_height = 60
        button_x = (width - button_width) // 2
        button_y = height - 100
        
        button_rect = (button_x, button_y, button_width, button_height)
        
        # Draw button background
        cv2.rectangle(
            frame,
            (button_x, button_y),
            (button_x + button_width, button_y + button_height),
            (0, 255, 0),  # Green
            -1  # Filled
        )
        
        # Draw button border
        cv2.rectangle(
            frame,
            (button_x, button_y),
            (button_x + button_width, button_y + button_height),
            (255, 255, 255),  # White border
            3
        )
        
        # Draw button text
        button_text = "CAPTURE"
        text_size = cv2.getTextSize(button_text, cv2.FONT_HERSHEY_DUPLEX, 1.2, 3)[0]
        text_x = button_x + (button_width - text_size[0]) // 2
        text_y = button_y + (button_height + text_size[1]) // 2
        
        cv2.putText(
            frame,
            button_text,
            (text_x, text_y),
            cv2.FONT_HERSHEY_DUPLEX,
            1.2,
            (0, 0, 0),  # Black text
            3
        )
        
        # Display frame
        cv2.imshow("Clinical Capture System", frame)
        
        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF
        
        # Check for capture trigger (button click or spacebar)
        if button_clicked or key == ord(' ') or key == 32:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"capture_{timestamp}.png"
            filepath = os.path.join(captures_dir, filename)
            cv2.imwrite(filepath, frame)
            print(f"\n✓ IMAGE CAPTURED: {filepath}")
            captured = True
            button_clicked = False  # Reset flag
        
        # Exit on 'q'
        if key == ord('q'):
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("\n✓ System shutdown.")


if __name__ == "__main__":
    main()
