"""
Janam Kundali Generator - Streamlit App
Generates Vedic birth charts in South Indian format with downloadable PDF.
"""

import streamlit as st
from datetime import datetime, date, time
from timezonefinder import TimezoneFinder
import pytz
import re
from vedic_calc import (
    calculate_kundli, calculate_navamsa,
    RASHI_NAMES, GRAHA_NAMES, NAKSHATRA_NAMES
)
from pdf_generator import generate_kundli_pdf

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Janam Kundali Generator",
    page_icon="🙏",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------------------------
# Custom CSS for clean, traditional look (works in light and dark mode)
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        max-width: 800px;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #8B1A1A 0%, #5D1212 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .main-header h1 {
        color: #D4A017 !important;
        font-size: 2rem;
        margin: 0;
    }
    .main-header p {
        color: #F5E6CC;
        font-size: 0.9rem;
        margin: 0.3rem 0 0 0;
    }
    
    /* Section headers */
    .section-header {
        color: #8B1A1A;
        border-bottom: 2px solid #D4A017;
        padding-bottom: 0.3rem;
        margin-top: 1.5rem;
    }
    
    /* Info box - works in both light and dark mode */
    .info-box {
        background: rgba(212, 160, 23, 0.1);
        border-left: 4px solid #D4A017;
        padding: 0.8rem 1rem;
        border-radius: 0 5px 5px 0;
        margin: 0.5rem 0;
        font-size: 0.85rem;
    }
    
    /* Result card */
    .result-card {
        background: rgba(212, 160, 23, 0.05);
        border: 1px solid #D4A017;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Button styling */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #8B1A1A 0%, #5D1212 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        font-size: 1rem !important;
        border-radius: 8px !important;
    }
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #A52020 0%, #8B1A1A 100%) !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>Janam Kundali</h1>
    <p>Vedic Birth Chart Generator — South Indian Style</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Comprehensive Indian City Database (100+ cities)
# Sorted alphabetically. All coordinates verified.
# Format: "City, State": (latitude, longitude)
# ---------------------------------------------------------------------------
INDIAN_CITIES = {
    "Agra, Uttar Pradesh": (27.1767, 78.0081),
    "Ahmedabad, Gujarat": (23.0225, 72.5714),
    "Ajmer, Rajasthan": (26.4499, 74.6399),
    "Aligarh, Uttar Pradesh": (27.8974, 78.0880),
    "Allahabad (Prayagraj), Uttar Pradesh": (25.4358, 81.8463),
    "Amritsar, Punjab": (31.6340, 74.8723),
    "Aurangabad, Maharashtra": (19.8762, 75.3433),
    "Bareilly, Uttar Pradesh": (28.3670, 79.4304),
    "Belagavi (Belgaum), Karnataka": (15.8497, 74.4977),
    "Bengaluru, Karnataka": (12.9716, 77.5946),
    "Bhopal, Madhya Pradesh": (23.2599, 77.4126),
    "Bhubaneswar, Odisha": (20.2961, 85.8245),
    "Bikaner, Rajasthan": (28.0229, 73.3119),
    "Chandigarh": (30.7333, 76.7794),
    "Chennai, Tamil Nadu": (13.0827, 80.2707),
    "Chikkamagaluru, Karnataka": (13.3153, 75.7754),
    "Coimbatore, Tamil Nadu": (11.0168, 76.9558),
    "Cuttack, Odisha": (20.4625, 85.8830),
    "Davangere, Karnataka": (14.4644, 75.9218),
    "Dehradun, Uttarakhand": (30.3165, 78.0322),
    "Delhi, NCR": (28.6139, 77.2090),
    "Dharwad, Karnataka": (15.4589, 75.0078),
    "Dhanbad, Jharkhand": (23.7957, 86.4304),
    "Ernakulam (Kochi), Kerala": (9.9312, 76.2673),
    "Faridabad, Haryana": (28.4089, 77.3178),
    "Ghaziabad, Uttar Pradesh": (28.6692, 77.4538),
    "Gorakhpur, Uttar Pradesh": (26.7606, 83.3732),
    "Gulbarga (Kalaburagi), Karnataka": (17.3297, 76.8343),
    "Guntur, Andhra Pradesh": (16.3067, 80.4365),
    "Gurgaon (Gurugram), Haryana": (28.4595, 77.0266),
    "Guwahati, Assam": (26.1445, 91.7362),
    "Gwalior, Madhya Pradesh": (26.2183, 78.1828),
    "Hassan, Karnataka": (13.0073, 76.0962),
    "Hubli-Dharwad, Karnataka": (15.3647, 75.1240),
    "Hyderabad, Telangana": (17.3850, 78.4867),
    "Imphal, Manipur": (24.8170, 93.9368),
    "Indore, Madhya Pradesh": (22.7196, 75.8577),
    "Jabalpur, Madhya Pradesh": (23.1815, 79.9864),
    "Jaipur, Rajasthan": (26.9124, 75.7873),
    "Jalandhar, Punjab": (31.3260, 75.5762),
    "Jammu, Jammu & Kashmir": (32.7266, 74.8570),
    "Jamshedpur, Jharkhand": (22.8046, 86.2029),
    "Jodhpur, Rajasthan": (26.2389, 73.0243),
    "Kanpur, Uttar Pradesh": (26.4499, 80.3319),
    "Kochi, Kerala": (9.9312, 76.2673),
    "Kolhapur, Maharashtra": (16.7050, 74.2433),
    "Kolkata, West Bengal": (22.5726, 88.3639),
    "Kota, Rajasthan": (25.2138, 75.8648),
    "Kozhikode (Calicut), Kerala": (11.2588, 75.7804),
    "Lucknow, Uttar Pradesh": (26.8467, 80.9462),
    "Ludhiana, Punjab": (30.9010, 75.8573),
    "Madurai, Tamil Nadu": (9.9252, 78.1198),
    "Mangaluru, Karnataka": (12.9141, 74.8560),
    "Meerut, Uttar Pradesh": (28.9845, 77.7064),
    "Moradabad, Uttar Pradesh": (28.8386, 78.7733),
    "Mumbai, Maharashtra": (19.0760, 72.8777),
    "Muzaffarpur, Bihar": (26.1209, 85.3647),
    "Mysuru (Mysore), Karnataka": (12.2958, 76.6394),
    "Nagpur, Maharashtra": (21.1458, 79.0882),
    "Nanded, Maharashtra": (19.1383, 77.3210),
    "Nashik, Maharashtra": (19.9975, 73.7898),
    "Navi Mumbai, Maharashtra": (19.0330, 73.0297),
    "Noida, Uttar Pradesh": (28.5355, 77.3910),
    "Palakkad, Kerala": (10.7867, 76.6548),
    "Panaji, Goa": (15.4909, 73.8278),
    "Patna, Bihar": (25.6093, 85.1376),
    "Pondicherry (Puducherry)": (11.9416, 79.8083),
    "Pune, Maharashtra": (18.5204, 73.8567),
    "Raipur, Chhattisgarh": (21.2514, 81.6296),
    "Rajkot, Gujarat": (22.3039, 70.8022),
    "Ranchi, Jharkhand": (23.3441, 85.3096),
    "Raichur, Karnataka": (16.2076, 77.3463),
    "Salem, Tamil Nadu": (11.6643, 78.1460),
    "Shimla, Himachal Pradesh": (31.1048, 77.1734),
    "Shimoga (Shivamogga), Karnataka": (13.9299, 75.5681),
    "Siliguri, West Bengal": (26.7271, 88.3953),
    "Solapur, Maharashtra": (17.6599, 75.9064),
    "Srinagar, Jammu & Kashmir": (34.0837, 74.7973),
    "Surat, Gujarat": (21.1702, 72.8311),
    "Thane, Maharashtra": (19.2183, 72.9781),
    "Thiruvananthapuram, Kerala": (8.5241, 76.9366),
    "Thrissur, Kerala": (10.5276, 76.2144),
    "Tiruchirappalli (Trichy), Tamil Nadu": (10.7905, 78.7047),
    "Tirunelveli, Tamil Nadu": (8.7139, 77.7567),
    "Tirupati, Andhra Pradesh": (13.6288, 79.4192),
    "Tiruppur, Tamil Nadu": (11.1085, 77.3411),
    "Tumkur, Karnataka": (13.3379, 77.1173),
    "Udaipur, Rajasthan": (24.5854, 73.7125),
    "Udupi, Karnataka": (13.3409, 74.7421),
    "Ujjain, Madhya Pradesh": (23.1765, 75.7885),
    "Vadodara, Gujarat": (22.3072, 73.1812),
    "Varanasi, Uttar Pradesh": (25.3176, 82.9739),
    "Vijayawada, Andhra Pradesh": (16.5062, 80.6480),
    "Visakhapatnam, Andhra Pradesh": (17.6868, 83.2185),
    "Warangal, Telangana": (17.9784, 79.5941),
}

# ---------------------------------------------------------------------------
# Abbreviation map for display
# ---------------------------------------------------------------------------
GRAHA_ABBREV = {
    "Lagna": "Lg",
    "Surya": "Su",
    "Chandra": "Ch",
    "Mangal": "Ma",
    "Budha": "Bu",
    "Guru": "Gu",
    "Shukra": "Sk",
    "Shani": "Sa",
    "Rahu": "Ra",
    "Ketu": "Ke",
}

# ---------------------------------------------------------------------------
# Input Form
# ---------------------------------------------------------------------------
st.markdown('<h3 class="section-header">Birth Details</h3>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    person_name = st.text_input("Full Name", placeholder="Enter full name")
    birth_date = st.date_input(
        "Date of Birth",
        value=date(1990, 1, 15),
        min_value=date(1900, 1, 1),
        max_value=date.today()
    )

with col2:
    # Minute-granular time input with AM/PM
    birth_time_str = st.text_input(
        "Time of Birth (HH:MM AM/PM)",
        value="08:30 AM",
        placeholder="e.g. 04:35 PM",
        help="Enter exact birth time with AM or PM. Examples: 06:15 AM, 10:45 PM, 12:00 PM (noon), 12:00 AM (midnight). Accuracy to the minute matters for Lagna calculation."
    )

# Parent names (optional)
parent_col1, parent_col2 = st.columns(2)
with parent_col1:
    father_name = st.text_input("Father's Name", placeholder="Optional")
with parent_col2:
    mother_name = st.text_input("Mother's Name", placeholder="Optional")

st.markdown('<h3 class="section-header">Birth Place</h3>', unsafe_allow_html=True)

# City selection — searchable dropdown with 100+ cities + manual option
city_options = ["-- Select a city (type to search) --"] + sorted(INDIAN_CITIES.keys()) + ["Other (enter coordinates manually)"]

selected_city = st.selectbox(
    "City",
    options=city_options,
    index=0,
    help="Start typing to search. If your city is not listed, select 'Other' at the bottom to enter latitude and longitude manually."
)

use_manual = selected_city == "Other (enter coordinates manually)"
no_selection = selected_city == "-- Select a city (type to search) --"

if use_manual:
    st.markdown('<div class="info-box">Enter the birth place name and its latitude/longitude coordinates. You can find coordinates by searching your city on <a href="https://www.google.com/maps" target="_blank">Google Maps</a> — right-click on the location and copy the coordinates.</div>', unsafe_allow_html=True)
    manual_place = st.text_input("Place Name", placeholder="e.g., Hassan, Karnataka")
    coord_col1, coord_col2 = st.columns(2)
    with coord_col1:
        manual_lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=12.97, format="%.4f", help="e.g., 12.9716 for Bengaluru")
    with coord_col2:
        manual_lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=77.59, format="%.4f", help="e.g., 77.5946 for Bengaluru")

# ---------------------------------------------------------------------------
# Generate Button
# ---------------------------------------------------------------------------
st.markdown("---")

if st.button("Generate Kundali", type="primary", width='stretch'):
    
    # Validate name
    if not person_name.strip():
        st.error("Please enter a name.")
        st.stop()
    
    # Validate city selection
    if no_selection:
        st.error("Please select a city from the dropdown, or choose 'Other' to enter coordinates manually.")
        st.stop()
    
    # Validate and parse time input (AM/PM format)
    time_match = re.match(r'^(\d{1,2}):(\d{2})\s*(AM|PM|am|pm|Am|Pm)$', birth_time_str.strip())
    if not time_match:
        st.error("Invalid time format. Please enter time as HH:MM AM/PM (e.g., 08:30 AM or 04:35 PM).")
        st.stop()
    
    hour = int(time_match.group(1))
    minute = int(time_match.group(2))
    ampm = time_match.group(3).upper()
    
    if hour < 1 or hour > 12 or minute < 0 or minute > 59:
        st.error("Invalid time. Hours must be 1-12, minutes must be 0-59.")
        st.stop()
    
    # Convert to 24-hour format
    if ampm == 'AM':
        if hour == 12:
            hour = 0  # 12:xx AM = 00:xx
    else:  # PM
        if hour != 12:
            hour += 12  # 1-11 PM = 13-23
    
    # Determine coordinates
    lat, lon = None, None
    place_name = ""
    
    if use_manual:
        if not manual_place or not manual_place.strip():
            st.error("Please enter a place name.")
            st.stop()
        lat = manual_lat
        lon = manual_lon
        place_name = manual_place.strip()
    else:
        coords = INDIAN_CITIES[selected_city]
        lat, lon = coords
        place_name = selected_city
    
    # Find timezone and calculate
    with st.spinner("Calculating Kundali..."):
        try:
            tf = TimezoneFinder()
            tz_name = tf.timezone_at(lat=lat, lng=lon)
            if tz_name:
                tz = pytz.timezone(tz_name)
                birth_dt = datetime(
                    birth_date.year, birth_date.month, birth_date.day,
                    hour, minute
                )
                localized_dt = tz.localize(birth_dt)
                utc_offset = localized_dt.utcoffset()
                tz_offset_hours = utc_offset.total_seconds() / 3600
            else:
                tz_name = "Asia/Kolkata"
                tz_offset_hours = 5.5
            
            # Calculate Kundli
            kundli = calculate_kundli(
                name=person_name.strip(),
                year=birth_date.year,
                month=birth_date.month,
                day=birth_date.day,
                hour=hour,
                minute=minute,
                place_name=place_name,
                latitude=lat,
                longitude=lon,
                tz_offset_hours=tz_offset_hours,
                timezone_name=tz_name
            )
            
            # Attach parent names to kundli object
            kundli.father_name = father_name.strip() if father_name else ""
            kundli.mother_name = mother_name.strip() if mother_name else ""
            
            # Store in session state
            st.session_state['kundli'] = kundli
            st.session_state['generated'] = True
            
        except Exception as e:
            st.error(f"Calculation error: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            st.stop()

# ---------------------------------------------------------------------------
# Display Results
# ---------------------------------------------------------------------------
if st.session_state.get('generated', False):
    kundli = st.session_state['kundli']
    
    st.markdown("---")
    st.markdown('<h3 class="section-header">Results</h3>', unsafe_allow_html=True)
    
    # Birth Info section
    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.markdown(f"**Date of Birth:** {kundli.birth_date.strftime('%d %B %Y')}")
        st.markdown(f"**Time of Birth:** {kundli.birth_time_str}")
        st.markdown(f"**Latitude:** {kundli.latitude:.4f}")
        st.markdown(f"**Longitude:** {kundli.longitude:.4f}")
    with info_col2:
        st.markdown(f"**Day:** {kundli.panchang.vara}")
        st.markdown(f"**Timezone:** {kundli.timezone_name} ({kundli.utc_offset})")
        st.markdown(f"**Place:** {kundli.birth_place}")
        st.markdown(f"**Ayanamsha:** {kundli.ayanamsa_name}: {kundli.ayanamsa:.4f}°")
    
    # Quick summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Lagna", kundli.lagna.rashi_name)
    with col2:
        st.metric("Chandra Rashi", kundli.grahas[1].rashi_name)
    with col3:
        st.metric("Surya Rashi", kundli.grahas[0].rashi_name)
    
    # Panchang
    st.markdown('<h4 class="section-header">Panchang Details</h4>', unsafe_allow_html=True)
    panchang_col1, panchang_col2 = st.columns(2)
    with panchang_col1:
        st.markdown(f"**Vara:** {kundli.panchang.vara}")
        st.markdown(f"**Tithi:** {kundli.panchang.paksha} {kundli.panchang.tithi_name}")
        st.markdown(f"**Nakshatra:** {kundli.panchang.nakshatra_name} (Pada {kundli.panchang.nakshatra_pada})")
        st.markdown(f"**Yoga:** {kundli.panchang.yoga_name}")
        st.markdown(f"**Karana:** {kundli.panchang.karana_name}")
    with panchang_col2:
        st.markdown(f"**Samvatsara:** {kundli.panchang.samvatsara}")
        masa_str = f"Adhika {kundli.panchang.masa}" if kundli.panchang.masa_is_adhika else kundli.panchang.masa
        st.markdown(f"**Masa:** {masa_str}")
        st.markdown(f"**Paksha:** {kundli.panchang.paksha}")
        st.markdown(f"**Ayana:** {kundli.panchang.ayana}")
        st.markdown(f"**Rutu:** {kundli.panchang.rutu}")
    
    # Planetary Positions Table
    st.markdown('<h4 class="section-header">Graha Sthiti (Planetary Positions)</h4>', unsafe_allow_html=True)
    
    import pandas as pd
    planet_data = []
    for g in [kundli.lagna] + kundli.grahas:
        retro = " (Vakri)" if g.is_retrograde else ""
        abbrev = GRAHA_ABBREV.get(g.name, "?")
        planet_data.append({
            "Graha": g.name + retro,
            "Abbr.": abbrev,
            "Rashi": g.rashi_name,
            "Rashi Lord": g.rashi_lord,
            "Degree": g.degree_str,
            "Nakshatra": g.nakshatra_name,
            "Nak. Lord": g.nakshatra_lord,
            "Pada": g.pada,
            "Dignity": g.dignity if g.dignity else "-"
        })
    
    df = pd.DataFrame(planet_data)
    st.dataframe(df, width='stretch', hide_index=True)
    
    st.markdown('<div class="info-box">The <b>Abbr.</b> column shows the abbreviation used in the chart diagrams below (e.g., Su=Surya, Ch=Chandra). (R) after an abbreviation in the chart means Vakri (retrograde).</div>', unsafe_allow_html=True)
    
    # Current Dasha
    st.markdown('<h4 class="section-header">Vimshottari Maha Dasha</h4>', unsafe_allow_html=True)
    
    now = datetime.now()
    dasha_data = []
    for dp in kundli.dasha_periods:
        is_current = dp.start_date <= now <= dp.end_date
        years = int(dp.years)
        months = int((dp.years - years) * 12)
        duration = f"{years} years" if months == 0 else f"{years} years {months} months"
        dasha_data.append({
            "Dasha Lord": dp.lord + (" (Current)" if is_current else ""),
            "Start": dp.start_date.strftime("%d %b %Y"),
            "End": dp.end_date.strftime("%d %b %Y"),
            "Duration": duration
        })
    
    dasha_df = pd.DataFrame(dasha_data)
    st.dataframe(dasha_df, width='stretch', hide_index=True)
    
    # Generate PDF
    st.markdown("---")
    st.markdown('<h4 class="section-header">Download PDF Report</h4>', unsafe_allow_html=True)
    
    with st.spinner("Generating PDF..."):
        pdf_bytes = generate_kundli_pdf(kundli)
    
    filename = f"Kundali_{kundli.name.replace(' ', '_')}_{kundli.birth_date.strftime('%Y%m%d')}.pdf"
    
    st.download_button(
        label="Download Kundali PDF",
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf",
        width='stretch'
    )
    
    st.markdown('<div class="info-box">The PDF includes Rashi Kundali (D1), Navamsha Kundali (D9), planetary positions with chart abbreviations, Panchang details, and Vimshottari Dasha timeline.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Reference PDF
# ---------------------------------------------------------------------------
st.markdown("---")
with st.expander("Rashi & Nakshatra Quick Reference (PDF)"):
    st.markdown("Download a handy 3-page reference covering the 12 Rashis, "
                "27 Nakshatras with Padas, degree ranges, and lords.")
    from reference_pdf import generate_reference_pdf_bytes
    ref_pdf = generate_reference_pdf_bytes()
    st.download_button(
        label="Download Reference PDF",
        data=ref_pdf,
        file_name="Rashi_Nakshatra_Reference.pdf",
        mime="application/pdf",
        width='stretch'
    )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#888; font-size:0.8rem;">'
    'Vedic Kundali Generator | Lahiri Ayanamsa | Swiss Ephemeris<br>'
    'This tool is for reference only. Please consult a qualified Jyotishi for detailed interpretation.'
    '</p>',
    unsafe_allow_html=True
)
