import asyncio
import argparse
from eye_tracking_utility import EyeTrackingUtility


async def main():
    parser = argparse.ArgumentParser(description="Eye Tracking Example")
    parser.add_argument(
        "--use-tobii", action="store_true", help="Use Tobii eye tracker if available"
    )
    parser.add_argument(
        "--backend-url",
        default="ws://localhost:8000/ws/eye-tracking",
        help="WebSocket URL of the backend server",
    )

    args = parser.parse_args()

    print("Starting eye tracking utility...")
    print(f"Using Tobii: {args.use_tobii}")
    print(f"Backend URL: {args.backend_url}")

    utility = EyeTrackingUtility(use_tobii=args.use_tobii, backend_url=args.backend_url)
    await utility.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExample stopped by user.")
    except Exception as e:
        print(f"Error: {e}")
