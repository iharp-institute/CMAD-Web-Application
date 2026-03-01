import requests
import cv2
import numpy as np
from datetime import datetime
import os


def download_and_crop_noaa_v4(date_str, save_dir=""):
    """
    Download and crop Antarctic NOAA NSIDC v4.0 image.

    date_str: YYYYMMDD (e.g., "20240201")
    """

    # -----------------------
    # 1. Parse Date
    # -----------------------
    try:
        date_obj = datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        raise ValueError("Date must be in YYYYMMDD format")

    year = date_obj.strftime("%Y")
    month_folder = date_obj.strftime("%m_%b")  # 02_Feb format

    # Correct v4.0 filename format
    filename = f"S_{date_str}_conc_v4.0.png"

    # -----------------------
    # 2. Build URL
    # -----------------------
    base_url = "https://noaadata.apps.nsidc.org/NOAA/G02135/south/daily/images/"
    image_url = f"{base_url}{year}/{month_folder}/{filename}"

    print(f"[Agent] Downloading:")
    print(image_url)

    # -----------------------
    # 3. Download
    # -----------------------
    try:
        response = requests.get(image_url, timeout=30)
    except requests.RequestException as e:
        print(f"[Agent] Network error: {e}")
        return None

    if response.status_code != 200:
        print("[Agent] Image not found.")
        return None

    # -----------------------
    # 4. Convert to OpenCV
    # -----------------------
    image_array = np.frombuffer(response.content, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image is None:
        print("[Agent] Failed to decode image.")
        return None

    # -----------------------
    # 5. Crop (Your Values)
    # -----------------------
    width = 318
    height = 334
    offset_x = 11
    offset_y = 87

    cropped = image[offset_y:offset_y + height,
                    offset_x:offset_x + width]

    cropped = cropped[1:-1, 1:-1]

    # -----------------------
    # 6. Save
    # -----------------------
    #os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"{date_str}.png")

    cv2.imwrite(save_path, cropped)

    print(f"[Agent] Saved: {save_path}")

    return save_path


