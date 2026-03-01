from flask import Flask, render_template, request, send_from_directory
import os
from cmad_core import cmad_discord_for_two_images
from download_agent import download_and_crop_noaa_v4

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER


@app.route("/")
def index():
    return render_template("date_input.html")


from datetime import datetime

@app.route("/process", methods=["POST"])
def process_dates():

    date1 = request.form.get("date1")
    date2 = request.form.get("date2")

    error = None

    # ----------------------------
    # 1️⃣ Check Empty
    # ----------------------------
    if not date1 or not date2:
        error = "Please enter both dates."

    # ----------------------------
    # 2️⃣ Validate Format
    # ----------------------------
    if not error:
        try:
            d1 = datetime.strptime(date1, "%Y%m%d")
            d2 = datetime.strptime(date2, "%Y%m%d")
        except ValueError:
            error = "Dates must be in YYYYMMDD format."

    # ----------------------------
    # 3️⃣ Logical Check
    # ----------------------------
    if not error and d1 >= d2:
        error = "Baseline date (t-n) must be earlier than target date (t)."

    # ----------------------------
    # 4️⃣ If Error → Return to Form
    # ----------------------------
    if error:
        return render_template("date_input.html", error=error)

    # ----------------------------
    # 5️⃣ Download NOAA Images
    # ----------------------------
    img1_path = download_and_crop_noaa_v4(date1, UPLOAD_FOLDER)
    img2_path = download_and_crop_noaa_v4(date2, UPLOAD_FOLDER)

    if img1_path is None or img2_path is None:
        return render_template(
            "date_input.html",
            error="NOAA image not available for one or both dates."
        )

    # ----------------------------
    # 6️⃣ Run CMAD
    # ----------------------------
    output_filename = f"anomaly_{date2}.png"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    cmad_discord_for_two_images(
        img1_path,
        img2_path,
        lb_txt_path="lb15.txt",
        q1_txt_path="q115.txt",
        show_plot=False,
        save_path=output_path
    )

    # Cleanup
    try:
        os.remove(img1_path)
        os.remove(img2_path)
    except:
        pass

    return render_template(
        "result.html",
        image_file=output_filename,
        target_date=date2
    )


@app.route("/outputs/<filename>")
def output_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)