"""
Clinical Overlay and Capture System - Main Orchestrator
Simple capture system with overlay guides.
"""
import cv2
import time
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


def main():
    """Main application loop."""
    global button_clicked, button_rect
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("ERROR: Cannot open camera")
        return
    
    # Read first frame to get dimensions
    ret, frame = cap.read()
    if not ret:
        print("ERROR: Cannot read from camera")
        cap.release()
        return
    
    height, width = frame.shape[:2]
    print(f"Camera initialized: {width}x{height}")
    
    # Create captures directory if it doesn't exist
    captures_dir = "captured_images"
    if not os.path.exists(captures_dir):
        os.makedirs(captures_dir)
        print(f"Created directory: {captures_dir}")
    else:
        print(f"Using existing directory: {captures_dir}")
    
    # Initialize components
    renderer = OverlayRenderer(width, height)
    
    overlay_config = renderer.get_config()
    
    print("System ready.")
    print("Controls:")
    print("  CLICK CAPTURE BUTTON or SPACEBAR - Capture image")
    print("  Q - Quit")
    print("=" * 50)
    
    # Setup mouse callback
    cv2.namedWindow("Clinical Capture System")
    cv2.setMouseCallback("Clinical Capture System", mouse_callback)
    
    captured = False
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
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
    print("\nSystem shutdown.")


if __name__ == "__main__":
    main()
