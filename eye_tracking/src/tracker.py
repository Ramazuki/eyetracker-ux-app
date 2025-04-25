import time
from typing import Optional, List
import numpy as np
import pandas as pd
import seaborn as sns
import cv2
import mediapipe as mp
import tobii_research as tr
import matplotlib.pyplot as plt
from dataclasses import dataclass
from datetime import datetime


@dataclass
class GazePoint:
    timestamp: float
    x: float
    y: float
    confidence: float
    source: str  # 'tobii' or 'webcam'


class EyeTracker:
    def __init__(self, use_tobii: bool = True):
        self.use_tobii = use_tobii
        self.tobii_tracker = None
        self.webcam = None
        self.mp_face_mesh = None
        self.gaze_points: List[GazePoint] = []

        if use_tobii:
            self._initialize_tobii()
        else:
            self._initialize_webcam()

    def _initialize_tobii(self):
        """Initialize Tobii eye tracker if available."""
        try:
            # In Tobii Research SDK 2.1.0, the API has changed
            # Check if the method exists in the current version
            if hasattr(tr, "find_all_eyetrackers"):
                eyetrackers = tr.find_all_eyetrackers()
            else:
                # Try alternative method names that might be used in newer versions
                if hasattr(tr, "find_eyetrackers"):
                    eyetrackers = tr.find_eyetrackers()
                else:
                    print("Tobii SDK API not recognized. Falling back to webcam.")
                    self.use_tobii = False
                    self._initialize_webcam()
                    return

            if eyetrackers:
                self.tobii_tracker = eyetrackers[0]
                # Check if serial_number attribute exists
                if hasattr(self.tobii_tracker, "serial_number"):
                    print(
                        f"Connected to Tobii tracker: {self.tobii_tracker.serial_number}"
                    )
                else:
                    print("Connected to Tobii tracker")
            else:
                print("No Tobii eye trackers found. Falling back to webcam.")
                self.use_tobii = False
                self._initialize_webcam()
        except Exception as e:
            print(f"Error initializing Tobii tracker: {e}")
            print("Falling back to webcam.")
            self.use_tobii = False
            self._initialize_webcam()

    def _initialize_webcam(self):
        """Initialize webcam and MediaPipe for webcam-based eye tracking."""
        try:
            # Try different camera indices if the default one fails
            for i in range(5):  # Try first 5 camera indices
                self.webcam = cv2.VideoCapture(i)
                if self.webcam.isOpened():
                    print(f"Connected to webcam at index {i}")
                    break

            if not self.webcam or not self.webcam.isOpened():
                print("Failed to open any webcam. Eye tracking will not work.")
                return

            # Initialize MediaPipe Face Mesh
            try:
                self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5,
                )
            except AttributeError:
                # Try alternative initialization if the API has changed
                try:
                    self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
                        max_num_faces=1,
                        min_detection_confidence=0.5,
                        min_tracking_confidence=0.5,
                    )
                except Exception as e:
                    print(f"Failed to initialize MediaPipe: {e}")
                    self.mp_face_mesh = None
        except Exception as e:
            print(f"Error initializing webcam: {e}")

    def _process_tobii_data(self, gaze_data):
        """Process data from Tobii eye tracker."""
        try:
            # Check if the gaze data has the expected structure
            if hasattr(gaze_data, "left_eye") and hasattr(gaze_data, "right_eye"):
                left_eye = gaze_data.left_eye
                right_eye = gaze_data.right_eye

                # Check if the eyes have pupil data
                if (
                    hasattr(left_eye, "pupil")
                    and hasattr(right_eye, "pupil")
                    and hasattr(left_eye.pupil, "validity")
                    and hasattr(right_eye.pupil, "validity")
                    and hasattr(left_eye.pupil, "position_in_trackbox")
                    and hasattr(right_eye.pupil, "position_in_trackbox")
                ):
                    if left_eye.pupil.validity and right_eye.pupil.validity:
                        # Calculate average position of both eyes
                        x = (
                            left_eye.pupil.position_in_trackbox[0]
                            + right_eye.pupil.position_in_trackbox[0]
                        ) / 2
                        y = (
                            left_eye.pupil.position_in_trackbox[1]
                            + right_eye.pupil.position_in_trackbox[1]
                        ) / 2

                        # Calculate confidence as average of both eyes
                        confidence = (
                            left_eye.pupil.validity + right_eye.pupil.validity
                        ) / 2

                        return GazePoint(
                            timestamp=time.time(),
                            x=x,
                            y=y,
                            confidence=confidence,
                            source="tobii",
                        )
            return None
        except Exception as e:
            print(f"Error processing Tobii data: {e}")
            return None

    def _process_webcam_data(self, frame) -> Optional[GazePoint]:
        """Process data from webcam using MediaPipe."""
        if self.mp_face_mesh is None:
            return None

        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.mp_face_mesh.process(frame_rgb)

            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]

                # Get eye landmarks (simplified version)
                left_eye = face_landmarks.landmark[33]  # Left eye center
                right_eye = face_landmarks.landmark[263]  # Right eye center

                # Calculate average position
                x = (left_eye.x + right_eye.x) / 2
                y = (left_eye.y + right_eye.y) / 2

                return GazePoint(
                    timestamp=time.time(),
                    x=x,
                    y=y,
                    confidence=1.0,  # MediaPipe doesn't provide confidence
                    source="webcam",
                )
            return None
        except Exception as e:
            print(f"Error processing webcam data: {e}")
            return None

    def start_tracking(self):
        """Start eye tracking and collect data."""
        if self.use_tobii and self.tobii_tracker:
            try:

                def gaze_data_callback(gaze_data):
                    point = self._process_tobii_data(gaze_data)
                    if point:
                        self.gaze_points.append(point)

                # Check if the method exists
                if hasattr(self.tobii_tracker, "subscribe_to"):
                    self.tobii_tracker.subscribe_to(
                        gaze_data_callback, as_dictionary=False
                    )
                else:
                    print(
                        "Tobii tracker does not support subscription. Falling back to webcam."
                    )
                    self.use_tobii = False
                    self._initialize_webcam()
                    self.start_tracking()
            except Exception as e:
                print(f"Error starting Tobii tracking: {e}")
                print("Falling back to webcam.")
                self.use_tobii = False
                self._initialize_webcam()
                self.start_tracking()
        else:
            if self.webcam is None or not self.webcam.isOpened():
                print("Webcam not available. Cannot start tracking.")
                return

            while True:
                ret, frame = self.webcam.read()
                if not ret:
                    break

                point = self._process_webcam_data(frame)
                if point:
                    self.gaze_points.append(point)

                # Display frame (for debugging)
                cv2.imshow("Eye Tracking", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    def stop_tracking(self):
        """Stop eye tracking and cleanup."""
        if self.use_tobii and self.tobii_tracker:
            try:
                if hasattr(self.tobii_tracker, "unsubscribe_from_all"):
                    self.tobii_tracker.unsubscribe_from_all()
            except Exception as e:
                print(f"Error stopping Tobii tracking: {e}")
        else:
            if self.webcam is not None and self.webcam.isOpened():
                self.webcam.release()
            cv2.destroyAllWindows()

    def generate_heatmap(self, width: int = 1920, height: int = 1080) -> np.ndarray:
        """Generate a heatmap from collected gaze points using seaborn."""
        if not self.gaze_points:
            return np.zeros((height, width))

        # Convert gaze points to DataFrame
        df = pd.DataFrame(
            [(p.x * width, p.y * height, p.confidence) for p in self.gaze_points],
            columns=["x", "y", "confidence"],
        )

        # Create 2D histogram
        heatmap, xedges, yedges = np.histogram2d(
            df.x, df.y, bins=[width // 20, height // 20], weights=df.confidence
        )

        # Normalize heatmap
        heatmap = heatmap.T
        heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min())

        # Create figure with seaborn
        plt.figure(figsize=(12, 8))
        sns.heatmap(heatmap, cmap="YlOrRd", cbar=True)
        plt.title("Eye Tracking Heatmap")

        # Save the heatmap
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"heatmap_{timestamp}.png"
        plt.savefig(filename)
        plt.close()

        return heatmap

    def get_gaze_points(self) -> List[GazePoint]:
        """Return collected gaze points."""
        return self.gaze_points

    def clear_gaze_points(self):
        """Clear collected gaze points."""
        self.gaze_points = []
