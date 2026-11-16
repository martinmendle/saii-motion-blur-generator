#!/usr/bin/env python3
"""
Blur generation pipeline.

Usage:
    python blur_pipeline.py 51
    python blur_pipeline.py 51 --trajectories diagonal sine
    python blur_pipeline.py 101 -t horizontal vertical --input-dir ./corrected_Y_ini_Y_final

For each requested trajectory:
    1. Takes the N central images of the trajectory (the excess is discarded
       equally from both ends; with 101 available and N=51, 25 are dropped per side).
    2. Averages the images (blur).
    3. Crops the result.
    4. Saves ONLY the cropped image as <trajectory>_<N>.png
       (the pre-crop image is never written to disk).

It also crops the ground truth image (by default X450_Y1000.jpg) with the
same margins and the same rendering as the blur, and saves it in ./gt.
"""

import argparse
import glob
import io
import os
import re
import sys

import cv2 as cv
import matplotlib

matplotlib.use("Agg")  # no window, render to memory only
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from tqdm import tqdm

# ----------------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------------
INPUT_DIR_DEFAULT = "./corrected_Y_ini_Y_final"
OUTPUT_DIR_DEFAULT = "./blur_results"

# Ground truth image and output folder
GT_IMAGE_DEFAULT = "./corrected_Y_ini_Y_final/X450_Y1000.jpg"
GT_DIR_DEFAULT = "./gt"

# Camera grid
X_START = 400
Y_START = 900
STEP_X = 1
STEP_Y = 2

# Total number of available positions in the diagonal/sine trajectories
NUM_COLUMNS = 101
NUM_ROWS = 101

# Fixed column for vertical motion and fixed row for horizontal motion
X_VERTICAL = 450
Y_HORIZONTAL = 1000

# Sine parameters
CYCLES = 1

# Crop margins in pixels, applied to the image already rendered by matplotlib
# (dpi=300, bbox tight), same as in the notebook.
MARGINS = {
    "left": 455,
    "top": 160,
    "right": 495,
    "bottom": 160,
}

TRAJECTORIES = ["diagonal", "horizontal", "vertical", "sine"]


# ----------------------------------------------------------------------------
# UTILITIES
# ----------------------------------------------------------------------------
def central_range(total, n):
    """Returns (start, end) of the n central positions out of a total."""
    if n > total:
        raise ValueError(
            f"{n} images were requested but the trajectory only has {total} available."
        )
    start = (total - n) // 2
    return start, start + n


def extract_x(path):
    return int(os.path.basename(path).split("_")[0][1:])


def extract_y(path):
    m = re.search(r"_Y(-?\d+(?:\.\d+)?)\.jpg$", os.path.basename(path))
    if m is None:
        raise ValueError(f"Unexpected file name: {os.path.basename(path)}")
    return float(m.group(1))


# ----------------------------------------------------------------------------
# TRAJECTORIES: return the list of paths (already trimmed to the N central ones)
# ----------------------------------------------------------------------------
def paths_diagonal(input_dir, n):
    t_start, t_end = central_range(NUM_COLUMNS, n)
    paths = []
    for t in range(t_start, t_end):
        cam_x = X_START + t * STEP_X
        cam_y = Y_START + t * STEP_Y
        paths.append(os.path.join(input_dir, f"X{cam_x}_Y{cam_y}.jpg"))
    return paths


def paths_horizontal(input_dir, n):
    files = glob.glob(os.path.join(input_dir, f"X*_Y{Y_HORIZONTAL}.jpg"))
    files.sort(key=extract_x)
    start, end = central_range(len(files), n)
    return files[start:end]


def paths_vertical(input_dir, n):
    files = glob.glob(os.path.join(input_dir, f"X{X_VERTICAL}_Y*.jpg"))
    files.sort(key=extract_y)
    start, end = central_range(len(files), n)
    return files[start:end]


def paths_sine(input_dir, n):
    x_end = X_START + (NUM_COLUMNS - 1) * STEP_X
    y_end = Y_START + (NUM_ROWS - 1) * STEP_Y

    y_mid = Y_START + (y_end - Y_START) // 2
    amplitude = (y_end - Y_START) // 8

    N = NUM_COLUMNS
    t = np.arange(N)
    cam_x = X_START + t * STEP_X
    y_float = y_mid + amplitude * np.sin(2 * np.pi * CYCLES * t / (N - 1))

    # Snap to the available Y grid and clip to the valid range
    cam_y = Y_START + np.round((y_float - Y_START) / STEP_Y) * STEP_Y
    cam_y = np.clip(cam_y, Y_START, y_end).astype(int)

    start, end = central_range(N, n)
    return [
        os.path.join(input_dir, f"X{x}_Y{y}.jpg")
        for x, y in zip(cam_x[start:end], cam_y[start:end])
    ]


GENERATORS = {
    "diagonal": paths_diagonal,
    "horizontal": paths_horizontal,
    "vertical": paths_vertical,
    "sine": paths_sine,
}


# ----------------------------------------------------------------------------
# BLUR + CROP
# ----------------------------------------------------------------------------
def average_images(paths, desc):
    """Averages the images in `paths` without loading them all into memory."""
    accumulated = None
    loaded = 0
    missing = 0

    for p in tqdm(paths, desc=desc):
        if not os.path.exists(p):
            missing += 1
            continue
        with Image.open(p) as img:
            arr = np.array(img.convert("RGB")).astype(np.float64)
        accumulated = arr if accumulated is None else accumulated + arr
        loaded += 1

    if loaded == 0:
        raise FileNotFoundError(f"No images found for: {desc}")
    if missing:
        print(f"  [warning] {desc}: {missing} missing images (skipped)")

    return (accumulated / loaded).astype(np.uint8), loaded


def render_in_memory(mean):
    """
    Reproduces the notebook's rendering (imshow + savefig dpi=300, bbox tight)
    but into an in-memory buffer, so the crop margins remain valid and the
    pre-crop image is never written to disk.
    Returns the image in BGR (like cv.imread).
    """
    fig = plt.figure()
    plt.axis("off")
    plt.imshow(mean)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight", pad_inches=0)
    plt.close(fig)

    data = np.frombuffer(buf.getvalue(), dtype=np.uint8)
    return cv.imdecode(data, cv.IMREAD_COLOR)


def crop(img, margins):
    height, width, _ = img.shape
    y0 = margins["top"]
    y1 = height - margins["bottom"]
    x0 = margins["left"]
    x1 = width - margins["right"]

    if y1 <= y0 or x1 <= x0:
        raise ValueError(
            f"The crop margins do not fit in the image ({width}x{height} px)."
        )
    return img[y0:y1, x0:x1]


def generate(trajectory, n, input_dir, output_dir, margins):
    paths = GENERATORS[trajectory](input_dir, n)
    mean, loaded = average_images(paths, f"{trajectory}_{n}")
    print(f"  {trajectory}: {loaded} images averaged")

    rendered_img = render_in_memory(mean)
    cropped_img = crop(rendered_img, margins)

    out_path = os.path.join(output_dir, f"{trajectory}_{n}.png")
    cv.imwrite(out_path, cropped_img)
    print(f"  -> {out_path}  ({cropped_img.shape[1]}x{cropped_img.shape[0]} px)")


def generate_gt(gt_path, gt_dir, margins):
    """
    Crops the ground truth image with the same margins as the blur.
    It goes through the same rendering (imshow + dpi=300, bbox tight) so the
    crop matches the trajectories' crop geometrically.
    """
    if not os.path.exists(gt_path):
        raise FileNotFoundError(f"GT image does not exist: {gt_path}")

    with Image.open(gt_path) as img:
        arr = np.array(img.convert("RGB"))

    cropped_img = crop(render_in_memory(arr), margins)

    os.makedirs(gt_dir, exist_ok=True)
    name = os.path.splitext(os.path.basename(gt_path))[0] + ".png"
    out_path = os.path.join(gt_dir, name)
    cv.imwrite(out_path, cropped_img)
    print(f"  -> {out_path}  ({cropped_img.shape[1]}x{cropped_img.shape[0]} px)")


# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Generates cropped blur per trajectory.")
    ap.add_argument("count", type=int, help="Number of images per blur (e.g. 51)")
    ap.add_argument(
        "-t",
        "--trajectories",
        nargs="+",
        choices=TRAJECTORIES,
        default=TRAJECTORIES,
        help="Trajectories to generate (default: all)",
    )
    ap.add_argument("--input-dir", default=INPUT_DIR_DEFAULT)
    ap.add_argument("--output-dir", default=OUTPUT_DIR_DEFAULT)
    ap.add_argument("--gt-image", default=GT_IMAGE_DEFAULT, help="Ground truth image to crop")
    ap.add_argument("--gt-dir", default=GT_DIR_DEFAULT, help="GT output folder")
    ap.add_argument("--no-gt", action="store_true", help="Do not generate the cropped GT")
    ap.add_argument("--margin-left", type=int, default=MARGINS["left"])
    ap.add_argument("--margin-top", type=int, default=MARGINS["top"])
    ap.add_argument("--margin-right", type=int, default=MARGINS["right"])
    ap.add_argument("--margin-bottom", type=int, default=MARGINS["bottom"])
    args = ap.parse_args()

    if args.count < 1:
        ap.error("The number of images must be >= 1")

    margins = {
        "left": args.margin_left,
        "top": args.margin_top,
        "right": args.margin_right,
        "bottom": args.margin_bottom,
    }

    os.makedirs(args.output_dir, exist_ok=True)

    errors = 0
    for traj in args.trajectories:
        print(f"[{traj}]")
        try:
            generate(traj, args.count, args.input_dir, args.output_dir, margins)
        except (ValueError, FileNotFoundError) as e:
            errors += 1
            print(f"  [error] {e}")

    if not args.no_gt:
        print("[gt]")
        try:
            generate_gt(args.gt_image, args.gt_dir, margins)
        except (ValueError, FileNotFoundError) as e:
            errors += 1
            print(f"  [error] {e}")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
