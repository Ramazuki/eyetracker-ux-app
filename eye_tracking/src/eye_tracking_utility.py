import asyncio
import json
import websockets
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional

from tracker import EyeTracker, GazePoint


class EyeTrackingUtility:
    def __init__(
        self,
        use_tobii: bool = True,
        backend_url: str = "ws://localhost:8000/ws/eye-tracking",
    ):
        self.tracker = EyeTracker(use_tobii=use_tobii)
        self.backend_url = backend_url
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.is_running = False
        self.output_dir = Path("heatmaps")
        self.output_dir.mkdir(exist_ok=True)

    async def connect_to_backend(self):
        """Establish WebSocket connection with the backend."""
        try:
            self.websocket = await websockets.connect(self.backend_url)
            print(f"Connected to backend at {self.backend_url}")
        except Exception as e:
            print(f"Failed to connect to backend: {e}")
            self.websocket = None

    async def send_gaze_data(self, gaze_point: GazePoint):
        """Send gaze data to the backend."""
        if self.websocket:
            data = {
                "timestamp": gaze_point.timestamp,
                "x": gaze_point.x,
                "y": gaze_point.y,
                "confidence": gaze_point.confidence,
                "source": gaze_point.source,
            }
            try:
                await self.websocket.send(json.dumps(data))
            except Exception as e:
                print(f"Failed to send data: {e}")

    async def generate_and_send_heatmap(self):
        """Generate heatmap and send it to the backend."""
        if not self.tracker.gaze_points:
            return

        try:
            heatmap = self.tracker.generate_heatmap()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.output_dir / f"heatmap_{timestamp}.png"

            if self.websocket:
                try:
                    # Send heatmap metadata
                    metadata = {
                        "type": "heatmap",
                        "timestamp": timestamp,
                        "filename": str(filename),
                        "shape": heatmap.shape,
                    }
                    await self.websocket.send(json.dumps(metadata))
                except Exception as e:
                    print(f"Failed to send heatmap metadata: {e}")
        except Exception as e:
            print(f"Failed to generate heatmap: {e}")

    async def process_gaze_data(self):
        """Process gaze data and send to backend."""
        while self.is_running:
            if self.tracker.gaze_points:
                latest_point = self.tracker.gaze_points[-1]
                await self.send_gaze_data(latest_point)

            # Generate heatmap every 30 seconds
            if len(self.tracker.gaze_points) % 300 == 0:  # Assuming 10Hz sampling rate
                await self.generate_and_send_heatmap()

            await asyncio.sleep(0.1)  # 10Hz update rate

    async def run(self):
        """Run the eye tracking utility."""
        self.is_running = True
        await self.connect_to_backend()

        try:
            # Start eye tracking
            self.tracker.start_tracking()

            # Start processing gaze data
            await self.process_gaze_data()
        except KeyboardInterrupt:
            print("\nStopping eye tracking utility...")
        except Exception as e:
            print(f"Error running eye tracking utility: {e}")
        finally:
            self.is_running = False
            self.tracker.stop_tracking()
            if self.websocket:
                await self.websocket.close()


def main():
    parser = argparse.ArgumentParser(description="Eye Tracking Utility")
    parser.add_argument(
        "--use-tobii", action="store_true", help="Use Tobii eye tracker if available"
    )
    parser.add_argument(
        "--backend-url",
        default="ws://localhost:8000/ws/eye-tracking",
        help="WebSocket URL of the backend server",
    )

    args = parser.parse_args()

    try:
        utility = EyeTrackingUtility(
            use_tobii=args.use_tobii, backend_url=args.backend_url
        )
        asyncio.run(utility.run())
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
