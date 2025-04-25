#!/usr/bin/env python3
"""
Console-based example for eye tracking without backend connection.
This example demonstrates basic eye tracking functionality using either
Tobii hardware or webcam, and displays gaze points in the console.
"""

import time
import argparse
from datetime import datetime
from pathlib import Path
from tracker import EyeTracker


def main():
    parser = argparse.ArgumentParser(description="Console Eye Tracking Example")
    parser.add_argument(
        "--use-tobii", action="store_true", help="Use Tobii eye tracker if available"
    )
    parser.add_argument(
        "--duration", type=int, default=30, help="Duration to track in seconds"
    )
    parser.add_argument(
        "--save-heatmap", action="store_true", help="Save heatmap at the end"
    )

    args = parser.parse_args()

    print("Starting console eye tracking example...")
    print(f"Using Tobii: {args.use_tobii}")
    print(f"Duration: {args.duration} seconds")
    print(f"Save heatmap: {args.save_heatmap}")
    print("Press Ctrl+C to stop early")

    # Create output directory for heatmaps if needed
    if args.save_heatmap:
        output_dir = Path("heatmaps")
        output_dir.mkdir(exist_ok=True)

    # Initialize the eye tracker
    tracker = EyeTracker(use_tobii=args.use_tobii)

    try:
        # Start tracking in a separate thread
        import threading

        tracking_thread = threading.Thread(target=tracker.start_tracking)
        tracking_thread.daemon = True  # Thread will exit when main program exits
        tracking_thread.start()

        # Monitor and display gaze points
        start_time = time.time()
        last_point_time = 0
        point_count = 0

        while time.time() - start_time < args.duration:
            # Get the latest gaze point
            if tracker.gaze_points:
                latest_point = tracker.gaze_points[-1]
                current_time = time.time()

                # Only display a new point if it's been at least 0.5 seconds since the last one
                if current_time - last_point_time >= 0.5:
                    print(
                        f"Gaze: x={latest_point.x:.3f}, y={latest_point.y:.3f}, "
                        f"confidence={latest_point.confidence:.2f}, source={latest_point.source}"
                    )
                    last_point_time = current_time
                    point_count += 1

            # Sleep briefly to avoid high CPU usage
            time.sleep(0.1)

        # Stop tracking
        tracker.stop_tracking()
        tracking_thread.join(timeout=1.0)

        # Print summary
        total_points = len(tracker.gaze_points)
        print(f"\nTracking completed. Collected {total_points} gaze points.")

        # Generate and save heatmap if requested
        if args.save_heatmap and total_points > 0:
            print("Generating heatmap...")
            tracker.generate_heatmap()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"heatmap_{timestamp}.png"
            print(f"Heatmap saved as {filename}")

    except KeyboardInterrupt:
        print("\nTracking stopped by user.")
        tracker.stop_tracking()
    except Exception as e:
        print(f"Error: {e}")
        tracker.stop_tracking()
    finally:
        # Print some statistics
        points = tracker.get_gaze_points()
        print(f"\nCollected {len(points)} gaze points")
        if points:
            print(f"First point: {points[0]}")
            print(f"Last point: {points[-1]}")


if __name__ == "__main__":
    main()
