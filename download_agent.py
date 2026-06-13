import requests
import cv2
import numpy as np
from datetime import datetime
import os


def download_and_crop_noaa_v4(date_str, save_dir="", suffix=""):
    """
    Download and crop Antarctic NOAA NSIDC v4.0 image.

    date_str: YYYYMMDD (e.g., "20240201")
    suffix:   unique run_id appended to filename to avoid collisions
              between concurrent users requesting the same date.
              e.g. date_str="20150801", suffix="a3f9b2c1"
                   → saves as "20150801_a3f9b2c1.png"
    """

    try:
        date_obj = datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        raise ValueError("Date must be in YYYYMMDD format")

    year = date_obj.strftime("%Y")
    month_folder = date_obj.strftime("%m_%b")
    filename = f"S_{date_str}_conc_v4.0.png"

    base_url = "https://noaadata.apps.nsidc.org/NOAA/G02135/south/daily/images/"
    image_url = f"{base_url}{year}/{month_folder}/{filename}"

    print(f"[Agent] Downloading: {image_url}")

    try:
        response = requests.get(image_url, timeout=30)
    except requests.RequestException as e:
        print(f"[Agent] Network error: {e}")
        return None

    if response.status_code != 200:
        print("[Agent] Image not found.")
        return None

    image_array = np.frombuffer(response.content, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image is None:
        print("[Agent] Failed to decode image.")
        return None

    # Crop
    width    = 318
    height   = 334
    offset_x = 11
    offset_y = 87

    cropped = image[offset_y:offset_y + height, offset_x:offset_x + width]
    cropped = cropped[1:-1, 1:-1]

    # Unique filename per run to avoid concurrent-user collisions
    save_name = f"{date_str}_{suffix}.png" if suffix else f"{date_str}.png"
    save_path = os.path.join(save_dir, save_name)

    cv2.imwrite(save_path, cropped)
    print(f"[Agent] Saved: {save_path}")

    return save_path
