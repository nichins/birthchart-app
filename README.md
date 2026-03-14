# ಜನ್ಮ ಪತ್ರಿಕಾ — Janam Patrika (Vedic Birth Chart Generator)

A cross-platform Streamlit app that generates professional Vedic birth charts (Kundli) in **South Indian format** with a downloadable 2-page PDF report.

## Features

- **South Indian chart format** with Rashi (D1) and Navamsha (D9) diagrams
- **Indian/Sanskrit names** throughout (Mesha, Vrishabha, Surya, Chandra, etc.)
- **Kannada shloka and title** on the PDF cover page
- **Ganesha emblem** on the first page
- **Panchang details**: Vara, Tithi, Nakshatra, Yoga, Karana
- **Hindu calendar fields**: Samvatsara (60-year cycle), Masa, Paksha, Ayana, Rutu
- **Nakshatra details**: Nakshatra Lord, Deity, Gana, Nadi
- **Parent names**: Father's and Mother's names displayed on the report
- **Bhava (House) chart** with Rashi and Lord for all 12 houses
- **Planetary positions table** with abbreviations matching the chart diagrams
- **Vimshottari Maha Dasha** timeline with current period highlighted
- **Planetary dignity**: Uchcha, Neecha, Swakshetra
- **Retrograde (Vakri)** indicators
- **Lagna ear-mark**: Small triangle in top-left corner of Lagna box with yellow highlight
- **Traditional Indian styling**: maroon/gold color scheme with decorative border
- **100% offline calculations** using Swiss Ephemeris (Lahiri Ayanamsa)
- **93 pre-loaded Indian cities** for quick selection (with manual lat/lon fallback)
- **AM/PM time input** for ease of use
- **Generation timestamp** on every PDF

## Quick Start

### 1. Install Python

Make sure you have Python 3.9 or later installed. Download from [python.org](https://www.python.org/downloads/).

### 2. Install Dependencies

Open a terminal/command prompt in the project folder and run:

```bash
pip install -r requirements.txt
```

### 3. Run the App

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`.

## File Structure

```
kundli_app/
├── app.py                      # Streamlit UI (input form, results, PDF download)
├── vedic_calc.py               # Core calculation engine (Swiss Ephemeris, Dasha, Panchang)
├── pdf_generator.py            # PDF report generator (South Indian charts, styling)
├── ganesha_emblem.png          # Ganesha image for PDF header
├── NotoSansKannada-Bold.ttf    # Bundled Kannada font (cross-platform)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

**Note:** `shloka_kannada.png` and `title_kannada.png` are auto-generated on first run.

## How to Use

1. Enter the person's **full name**
2. Optionally enter **Father's Name** and **Mother's Name**
3. Select the **date of birth** using the date picker
4. Enter the **time of birth** in HH:MM AM/PM format (e.g., `07:17 AM` or `04:35 PM`)
5. Select a **city** from the dropdown (type to search), or choose "Other" to enter coordinates manually
6. Click **"Generate Kundali"**
7. View the results on screen and click **"Download Kundali PDF"** to save the report

## Deploying for Remote Access (iPad, etc.)

### Option A: Local Network

```bash
streamlit run app.py --server.address 0.0.0.0
```

Then open `http://<your-laptop-ip>:8501` on the iPad's browser.

### Option B: Streamlit Cloud (Free)

1. Push the project to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo and deploy
4. Share the generated URL — works on any device with a browser

## Technical Details

- **Ephemeris**: Swiss Ephemeris via `pyswisseph` (Moshier method, compiled into the package)
- **Ayanamsa**: Lahiri (Chitrapaksha), the Indian government standard
- **House System**: Whole Sign Houses
- **Chart Style**: South Indian (fixed signs, houses counted clockwise from Lagna)
- **Rahu**: Mean Node; Ketu = Rahu + 180 degrees
- **Samvatsara**: Shaka Samvatsara system (South Indian tradition), verified against drikpanchang.com
- **Internet Required?**: No — all calculations are 100% offline. The bundled Kannada font ensures cross-platform rendering.

## Requirements

- Python 3.9+
- See `requirements.txt` for all package dependencies
