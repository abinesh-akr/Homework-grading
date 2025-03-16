import cv2
import numpy as np
import threading

def start_proctoring(callback=None):
    """Runs the proctoring system using OpenCV instead of Tkinter."""
    submitted_text = ""

    def show_warning(message):
        """Displays warning message on the OpenCV window."""
        print(f"Warning: {message}")  # ✅ Replace Tkinter messagebox with print

    def on_submit():
        """Handles answer submission."""
        nonlocal submitted_text
        submitted_text = "User submitted answer"  # Placeholder for actual input
        cap.release()
        if callback:
            callback(submitted_text)
        cv2.destroyAllWindows()

    def video_capture():
        """Captures webcam video for proctoring."""
        warnings = 0
        max_warnings = 3

        while warnings < max_warnings:
            ret, frame = cap.read()
            if not ret:
                warnings += 1
                show_warning(f"{warnings}/{max_warnings}: Stay visible!")

            # ✅ Display warning text on OpenCV window
            cv2.putText(frame, f"Warnings: {warnings}/{max_warnings}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            cv2.imshow("Proctoring System", frame)
            
            if warnings >= max_warnings:
                show_warning("Proctoring failed.")
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):  # Quit on 'q' key
                break

        cap.release()
        cv2.destroyAllWindows()

    # ✅ Initialize OpenCV webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Unable to access webcam.")
        return "Error: Webcam unavailable."

    # ✅ Start video capture in a thread
    threading.Thread(target=video_capture, daemon=True).start()

    return submitted_text  # ✅ Return placeholder text after OpenCV exits

# ✅ Test the function if running directly
if __name__ == "__main__":
    result = start_proctoring()
    print("Submitted Text:", result)
