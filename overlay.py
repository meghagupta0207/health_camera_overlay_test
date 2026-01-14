"""
Overlay Renderer
Draws static green guides for coin and lesion alignment.
Uses frame-relative coordinates for device independence.
"""
import cv2


class OverlayRenderer:
    """Renders static clinical overlay guides on camera frames."""
    
    def __init__(self, width, height):
        """
        Initialize overlay with frame-relative coordinates.
        
        Args:
            width: Frame width in pixels
            height: Frame height in pixels
        """
        self.width = width
        self.height = height
        
        # Calculate 2mm in pixels (assuming ~96 DPI typical screen)
        # 2mm ≈ 0.0787 inches ≈ 7.5 pixels at 96 DPI
        gap_pixels = int(0.02 * 96 / 0.0254)  # 2mm to pixels (~7-8 pixels)
        
        # Lesion overlay (left side, 20% width box, centered vertically)
        lesion_width = int(0.20 * width)
        lesion_height = int(0.30 * height)
        lesion_x1 = int(0.25 * width)
        lesion_y1 = int(0.35 * height)
        
        self.lesion_box = (
            lesion_x1,
            lesion_y1,
            lesion_x1 + lesion_width,
            lesion_y1 + lesion_height
        )
        
        # Coin overlay (right side, 2mm gap from lesion box)
        self.coin_radius = int(0.08 * width)  # 8% of frame width
        coin_x = lesion_x1 + lesion_width + gap_pixels + self.coin_radius
        coin_y = int(0.5 * height)
        self.coin_center = (coin_x, coin_y)
    
    def draw_static_guides(self, frame):
        """
        Draw coin circle and lesion box overlays.
        
        Args:
            frame: Input frame to draw on
            
        Returns:
            Frame with overlays drawn
        """
        overlay = frame.copy()
        
        # Draw coin circle
        cv2.circle(
            overlay,
            self.coin_center,
            self.coin_radius,
            (0, 255, 0),  # Green
            2
        )
        
        # Draw lesion box
        x1, y1, x2, y2 = self.lesion_box
        cv2.rectangle(
            overlay,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),  # Green
            2
        )
        
        return overlay
    
    def show_feedback(self, frame, message, color=(0, 255, 0)):
        """
        Display instructional text or status feedback.
        
        Args:
            frame: Frame to draw on
            message: Text message to display
            color: BGR color tuple (default green)
            
        Returns:
            Frame with feedback text
        """
        # Main instruction at top
        cv2.putText(
            frame,
            message,
            (50, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2
        )
        
        # Coin label
        cv2.putText(
            frame,
            "Align coin inside circle",
            (self.coin_center[0] - 80, self.coin_center[1] - self.coin_radius - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1
        )
        
        # Lesion label
        x1, y1, _, _ = self.lesion_box
        cv2.putText(
            frame,
            "Place lesion here",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1
        )
        
        return frame
    
    def get_config(self):
        """
        Return overlay configuration for validation.
        
        Returns:
            Dictionary with coin and lesion overlay parameters
        """
        return {
            'coin_center': self.coin_center,
            'coin_radius': self.coin_radius,
            'lesion_box': self.lesion_box
        }
