#!/usr/bin/env python3
"""
Heatmap Generator Utility

This script demonstrates how to generate heatmaps from saved gaze data.
It can be used to test heatmap generation without having to collect data in real-time.
"""

import json
import argparse
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from tracker import GazePoint


def load_gaze_data(file_path):
    """Load gaze data from a JSON file."""
    with open(file_path, "r") as f:
        data = json.load(f)

    # Convert JSON data to GazePoint objects
    gaze_points = []
    for point in data:
        gaze_points.append(
            GazePoint(
                timestamp=point["timestamp"],
                x=point["x"],
                y=point["y"],
                confidence=point["confidence"],
                source=point["source"],
            )
        )

    return gaze_points


def save_gaze_data(gaze_points, file_path):
    """Save gaze data to a JSON file."""
    data = [
        {
            "timestamp": p.timestamp,
            "x": p.x,
            "y": p.y,
            "confidence": p.confidence,
            "source": p.source,
        }
        for p in gaze_points
    ]

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)


def generate_heatmap(gaze_points, width=1920, height=1080, output_file=None):
    """Generate a heatmap from gaze points."""
    if not gaze_points:
        print("No gaze points to generate heatmap from.")
        return None

    # Convert gaze points to DataFrame
    df = pd.DataFrame(
        [(p.x * width, p.y * height, p.confidence) for p in gaze_points],
        columns=["x", "y", "confidence"],
    )

    # Create 2D histogram
    heatmap, xedges, yedges = np.histogram2d(
        df.x, df.y, bins=[width // 20, height // 20], weights=df.confidence
    )

    # Normalize heatmap
    heatmap = heatmap.T
    if heatmap.max() > heatmap.min():
        heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min())

    # Create figure with seaborn
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap, cmap="YlOrRd", cbar=True)
    plt.title("Eye Tracking Heatmap")

    # Save the heatmap if output file is specified
    if output_file:
        plt.savefig(output_file)
        print(f"Heatmap saved as {output_file}")
    else:
        plt.show()

    # plt.close()

    return heatmap


def create_sample_data(num_points=100, output_file=None):
    """Create sample gaze data for testing."""
    import random

    gaze_points = []
    for _ in range(num_points):
        gaze_points.append(
            GazePoint(
                timestamp=time.time() + random.uniform(0, 10),
                x=random.uniform(0, 1),
                y=random.uniform(0, 1),
                confidence=random.uniform(0.5, 1.0),
                source="sample",
            )
        )

    if output_file:
        save_gaze_data(gaze_points, output_file)
        print(f"Sample data saved as {output_file}")

    return gaze_points


def main():
    parser = argparse.ArgumentParser(description="Heatmap Generator")
    parser.add_argument("--input", help="Input JSON file with gaze data")
    parser.add_argument("--output", help="Output file for the heatmap")
    parser.add_argument("--width", type=int, default=1920, help="Width of the heatmap")
    parser.add_argument(
        "--height", type=int, default=1080, help="Height of the heatmap"
    )
    parser.add_argument(
        "--create-sample", action="store_true", help="Create sample data"
    )
    parser.add_argument(
        "--sample-points",
        type=int,
        default=100,
        help="Number of sample points to create",
    )
    parser.add_argument("--sample-output", help="Output file for sample data")

    args = parser.parse_args()

    # Create sample data if requested
    if args.create_sample:
        gaze_points = create_sample_data(args.sample_points, args.sample_output)
    # Load data from file if specified
    elif args.input:
        gaze_points = load_gaze_data(args.input)
    else:
        print("No input data specified. Use --input or --create-sample.")
        return

    # Generate heatmap
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"heatmap_{timestamp}.png"

    print(f"Generating heatmap from {len(gaze_points)} points...")

    generate_heatmap(gaze_points, args.width, args.height, output_file)


if __name__ == "__main__":
    import time  # Import here to avoid circular import

    main()
