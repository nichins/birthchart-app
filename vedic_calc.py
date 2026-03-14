"""
Vedic Astrology Calculation Engine
Uses Swiss Ephemeris (pyswisseph) for planetary position calculations.
All names use traditional Indian/Sanskrit terminology.
"""

import swisseph as swe
import math
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# ---------------------------------------------------------------------------
# Constants: Indian names for Rashis, Grahas, Nakshatras
# ---------------------------------------------------------------------------

RASHI_NAMES = [
    "Mesha", "Vrishabha", "Mithuna", "Karka",
    "Simha", "Kanya", "Tula", "Vrishchika",
    "Dhanu", "Makara", "Kumbha", "Meena"
]

RASHI_LORDS = [
    "Mangal", "Shukra", "Budha", "Chandra",
    "Surya", "Budha", "Shukra", "Mangal",
    "Guru", "Shani", "Shani", "Guru"
]

GRAHA_NAMES = [
    "Surya", "Chandra", "Mangal", "Budha",
    "Guru", "Shukra", "Shani", "Rahu", "Ketu"
]

GRAHA_ABBR = [
    "Su", "Ch", "Ma", "Bu", "Gu", "Sk", "Sa", "Ra", "Ke"
]

# Swiss Ephemeris planet IDs
GRAHA_SE_IDS = [
    swe.SUN, swe.MOON, swe.MARS, swe.MERCURY,
    swe.JUPITER, swe.VENUS, swe.SATURN,
    swe.MEAN_NODE,  # Rahu (Mean Node)
    -1  # Ketu (calculated as Rahu + 180)
]

NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini",
    "Mrigashira", "Ardra", "Punarvasu", "Pushya",
    "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha",
    "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Nakshatra lords in order (for Vimshottari Dasha)
NAKSHATRA_LORDS = [
    "Ketu", "Shukra", "Surya", "Chandra", "Mangal",
    "Rahu", "Guru", "Shani", "Budha"
]

# Vimshottari Dasha periods in years (same order as NAKSHATRA_LORDS)
DASHA_YEARS = {
    "Ketu": 7, "Shukra": 20, "Surya": 6, "Chandra": 10,
    "Mangal": 7, "Rahu": 18, "Guru": 16, "Shani": 19, "Budha": 17
}

# Dasha sequence (fixed order)
DASHA_SEQUENCE = [
    "Ketu", "Shukra", "Surya", "Chandra", "Mangal",
    "Rahu", "Guru", "Shani", "Budha"
]

# Tithi names
TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"
]

PAKSHA_NAMES = [
    "Shukla", "Shukla", "Shukla", "Shukla", "Shukla",
    "Shukla", "Shukla", "Shukla", "Shukla", "Shukla",
    "Shukla", "Shukla", "Shukla", "Shukla", "Shukla",
    "Krishna", "Krishna", "Krishna", "Krishna", "Krishna",
    "Krishna", "Krishna", "Krishna", "Krishna", "Krishna",
    "Krishna", "Krishna", "Krishna", "Krishna", "Krishna"
]

YOGA_NAMES = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti"
]

KARANA_NAMES = [
    "Bava", "Balava", "Kaulava", "Taitila",
    "Gara", "Vanija", "Vishti",
    "Shakuni", "Chatushpada", "Naga", "Kimstughna"
]

VARA_NAMES = [
    "Ravivara", "Somavara", "Mangalavara", "Budhavara",
    "Guruvara", "Shukravara", "Shanivara"
]

# Hindu Masa (Lunar Month) names: 1=Chaitra .. 12=Phalguna
MASA_NAMES = [
    "Chaitra", "Vaishakha", "Jyeshtha", "Ashadha",
    "Shravana", "Bhadrapada", "Ashwina", "Kartika",
    "Margashirsha", "Pushya", "Magha", "Phalguna"
]

# Rutu (Season) names: index 0-5
RUTU_NAMES = [
    "Vasanta (Spring)", "Grishma (Summer)", "Varsha (Monsoon)",
    "Sharad (Autumn)", "Hemanta (Pre-winter)", "Shishira (Winter)"
]

# 60 Samvatsara (Year) names
SAMVATSARA_NAMES = [
    "Prabhava", "Vibhava", "Shukla", "Pramoduta", "Prajotpatti",
    "Angirasa", "Shrimukha", "Bhava", "Yuva", "Dhatri",
    "Ishvara", "Bahudhanya", "Pramathi", "Vikrama", "Vrisha",
    "Chitrabhanu", "Svabhanu", "Tarana", "Parthiva", "Vyaya",
    "Sarvajit", "Sarvadhari", "Virodhi", "Vikrti", "Khara",
    "Nandana", "Vijaya", "Jaya", "Manmatha", "Durmukhi",
    "Hevilambi", "Vilambi", "Vikari", "Sharvari", "Plava",
    "Shubhakrt", "Shobhakrt", "Krodhi", "Vishvavasu", "Parabhava",
    "Plavanga", "Kilaka", "Saumya", "Sadharana", "Virodhikrt",
    "Paridavi", "Pramadicha", "Ananda", "Rakshasa", "Nala",
    "Pingala", "Kalayukti", "Siddarthi", "Raudri", "Durmati",
    "Dundubhi", "Rudhirodgari", "Raktakshi", "Krodhana", "Akshaya"
]

# Extended Nakshatra data: deity, symbol, gana, nadi
NAKSHATRA_DEITIES = [
    "Ashwini Kumaras", "Yama", "Agni", "Brahma/Prajapati",
    "Soma/Chandra", "Rudra", "Aditi", "Brihaspati",
    "Sarpas/Nagas", "Pitrs (Ancestors)", "Bhaga", "Aryaman",
    "Savitri/Surya", "Vishvakarman", "Vayu", "Indra/Agni",
    "Mitra", "Indra", "Nirrti", "Apah",
    "Vishvedevas", "Vishnu", "Eight Vasus", "Varuna",
    "Ajaikapada", "Ahirbudhnya", "Pushan"
]

NAKSHATRA_SYMBOLS = [
    "Horse's head", "Yoni", "Knife/Spear", "Chariot/Cart",
    "Deer's head", "Teardrop/Diamond", "Bow and quiver", "Cow's udder/Lotus",
    "Serpent", "Royal Throne", "Hammock/Fig tree", "Bed/Hammock",
    "Hand/Fist", "Bright jewel/Pearl", "Shoot of plant/Coral", "Triumphal arch",
    "Lotus/Archway", "Circular amulet/Umbrella", "Bunch of roots", "Elephant tusk/Fan",
    "Elephant tusk/Bed", "Ear/Three Footprints", "Drum/Flute", "Empty circle/Stars",
    "Swords/Two-faced man", "Snake in water", "Fish/Drum"
]

NAKSHATRA_GANA = [
    "Deva", "Manushya", "Rakshasa", "Manushya",
    "Deva", "Manushya", "Deva", "Deva",
    "Rakshasa", "Rakshasa", "Manushya", "Manushya",
    "Deva", "Rakshasa", "Deva", "Rakshasa",
    "Deva", "Rakshasa", "Rakshasa", "Manushya",
    "Manushya", "Deva", "Rakshasa", "Rakshasa",
    "Manushya", "Manushya", "Deva"
]

NAKSHATRA_NADI = [
    "Adi (Vata)", "Madhya (Pitta)", "Antya (Kapha)", "Antya (Kapha)",
    "Madhya (Pitta)", "Adi (Vata)", "Adi (Vata)", "Madhya (Pitta)",
    "Antya (Kapha)", "Antya (Kapha)", "Madhya (Pitta)", "Adi (Vata)",
    "Adi (Vata)", "Madhya (Pitta)", "Antya (Kapha)", "Antya (Kapha)",
    "Madhya (Pitta)", "Adi (Vata)", "Adi (Vata)", "Madhya (Pitta)",
    "Antya (Kapha)", "Antya (Kapha)", "Madhya (Pitta)", "Adi (Vata)",
    "Adi (Vata)", "Madhya (Pitta)", "Antya (Kapha)"
]

# Exaltation signs (0-indexed rashi)
EXALTATION = {
    "Surya": 0, "Chandra": 1, "Mangal": 9, "Budha": 5,
    "Guru": 3, "Shukra": 11, "Shani": 6
}

# Debilitation signs (0-indexed rashi)
DEBILITATION = {
    "Surya": 6, "Chandra": 7, "Mangal": 3, "Budha": 11,
    "Guru": 9, "Shukra": 5, "Shani": 0
}

# Own signs (0-indexed rashi)
OWN_SIGNS = {
    "Surya": [4], "Chandra": [3], "Mangal": [0, 7],
    "Budha": [2, 5], "Guru": [8, 11], "Shukra": [1, 6],
    "Shani": [9, 10]
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class GrahaPosition:
    name: str
    abbr: str
    longitude: float  # sidereal longitude (0-360)
    rashi_index: int  # 0-11
    rashi_name: str
    rashi_lord: str  # lord of the rashi this graha occupies
    degree_in_rashi: float  # 0-30
    nakshatra_index: int  # 0-26
    nakshatra_name: str
    nakshatra_lord: str
    pada: int  # 1-4
    is_retrograde: bool
    dignity: str  # "Exalted", "Debilitated", "Own Sign", ""

    @property
    def degree_str(self) -> str:
        """Format degree as DD° MM' SS\" """
        d = self.degree_in_rashi
        deg = int(d)
        m = (d - deg) * 60
        mins = int(m)
        secs = int((m - mins) * 60)
        return f"{deg}° {mins:02d}' {secs:02d}\""

    @property
    def full_longitude_str(self) -> str:
        """Format full longitude as DDD° MM' SS\" """
        d = self.longitude
        deg = int(d)
        m = (d - deg) * 60
        mins = int(m)
        secs = int((m - mins) * 60)
        return f"{deg}° {mins:02d}' {secs:02d}\""


@dataclass
class PanchangData:
    vara: str
    tithi_name: str
    tithi_number: int
    paksha: str
    nakshatra_name: str
    nakshatra_lord: str
    nakshatra_pada: int
    yoga_name: str
    karana_name: str
    # Hindu calendar fields
    masa: str  # Lunar month name
    masa_is_adhika: bool  # Leap month?
    samvatsara: str  # 60-year cycle name
    ayana: str  # Uttarayana or Dakshinayana
    rutu: str  # Season name


@dataclass
class DashaPeriod:
    lord: str
    start_date: datetime
    end_date: datetime
    years: float


@dataclass
class KundliData:
    name: str
    birth_date: datetime
    birth_time_str: str
    birth_place: str
    latitude: float
    longitude: float
    timezone_name: str
    utc_offset: str
    ayanamsa: float
    ayanamsa_name: str
    lagna: GrahaPosition  # Lagna treated as a special graha
    grahas: List[GrahaPosition]
    panchang: PanchangData
    dasha_periods: List[DashaPeriod]
    # Rashi-to-graha mapping for chart rendering
    rashi_grahas: dict  # {rashi_index: [graha_abbr, ...]}


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def normalize_longitude(lon: float) -> float:
    """Normalize longitude to 0-360 range."""
    lon = lon % 360
    if lon < 0:
        lon += 360
    return lon


def longitude_to_rashi(lon: float) -> Tuple[int, float]:
    """Convert sidereal longitude to rashi index and degree within rashi."""
    lon = normalize_longitude(lon)
    rashi_index = int(lon / 30)
    degree_in_rashi = lon - (rashi_index * 30)
    return rashi_index, degree_in_rashi


def longitude_to_nakshatra(lon: float) -> Tuple[int, int]:
    """Convert sidereal longitude to nakshatra index and pada."""
    lon = normalize_longitude(lon)
    nak_span = 13.0 + (1.0 / 3.0)  # 13°20'
    nak_index = int(lon / nak_span)
    if nak_index > 26:
        nak_index = 26
    degree_in_nak = lon - (nak_index * nak_span)
    pada_span = nak_span / 4.0
    pada = int(degree_in_nak / pada_span) + 1
    if pada > 4:
        pada = 4
    return nak_index, pada


def get_nakshatra_lord(nak_index: int) -> str:
    """Get the Vimshottari Dasha lord for a given nakshatra."""
    return NAKSHATRA_LORDS[nak_index % 9]


def get_dignity(graha_name: str, rashi_index: int) -> str:
    """Determine the dignity of a graha in a given rashi."""
    if graha_name in EXALTATION and EXALTATION[graha_name] == rashi_index:
        return "Uchcha"
    if graha_name in DEBILITATION and DEBILITATION[graha_name] == rashi_index:
        return "Neecha"
    if graha_name in OWN_SIGNS and rashi_index in OWN_SIGNS[graha_name]:
        return "Swakshetra"
    return ""


def degree_to_dms_str(deg: float) -> str:
    """Convert decimal degrees to D° M' S\" string."""
    d = int(deg)
    m = (deg - d) * 60
    mins = int(m)
    secs = int((m - mins) * 60)
    return f"{d}° {mins:02d}' {secs:02d}\""


# ---------------------------------------------------------------------------
# Hindu Calendar helper functions
# ---------------------------------------------------------------------------

def _solar_longitude_ut(jd_ut):
    """Get tropical solar longitude at given Julian Day (UT)."""
    data = swe.calc_ut(jd_ut, swe.SUN)
    return data[0][0]


def _lunar_longitude_ut(jd_ut):
    """Get tropical lunar longitude at given Julian Day (UT)."""
    data = swe.calc_ut(jd_ut, swe.MOON)
    return data[0][0]


def _lunar_phase(jd_ut):
    """Moon - Sun difference (0-360). 0/360 = New Moon, 180 = Full Moon."""
    sun_lon = _solar_longitude_ut(jd_ut)
    moon_lon = _lunar_longitude_ut(jd_ut)
    return (moon_lon - sun_lon) % 360


def _inverse_lagrange(x, y, ya):
    """Given lists x and y, find xa such that f(xa) = ya using Lagrange interpolation."""
    total = 0.0
    for i in range(len(x)):
        numer = 1.0
        denom = 1.0
        for j in range(len(x)):
            if j != i:
                numer *= (ya - y[j])
                denom *= (y[i] - y[j])
        if denom != 0:
            total += numer * x[i] / denom
    return total


def _unwrap_angles(angles):
    """Ensure angles are monotonically increasing by adding 360 where needed."""
    result = list(angles)
    for i in range(1, len(result)):
        while result[i] < result[i - 1]:
            result[i] += 360
    return result


def _find_new_moon(jd_ut, tithi_val, direction=-1):
    """
    Find the Julian Day of the new moon nearest to jd_ut.
    direction = -1 for previous new moon, +1 for next new moon.
    """
    if direction == -1:
        start = jd_ut - tithi_val  # rough estimate
    else:
        start = jd_ut + (30 - tithi_val)
    # Search within a span of (start +/- 2) days using interpolation
    x = [-2 + offset / 4.0 for offset in range(17)]
    y = [_lunar_phase(start + i) for i in x]
    y = _unwrap_angles(y)
    y0 = _inverse_lagrange(x, y, 360)
    return start + y0


def _solar_raasi_at_jd(jd_ut):
    """Get the sidereal solar raasi (1-12) at given JD. 1=Mesha .. 12=Meena."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    sun_trop = _solar_longitude_ut(jd_ut)
    ayan = swe.get_ayanamsa_ut(jd_ut)
    sun_sid = (sun_trop - ayan) % 360
    return math.ceil(sun_sid / 30.0) if sun_sid > 0 else 1


def _calculate_masa(jd_ut, tithi_val):
    """
    Calculate the Hindu lunar month (Masa).
    Returns (masa_number 1-12, is_adhika_month).
    Uses Amavasyanta (new-moon-to-new-moon) system.
    """
    last_nm = _find_new_moon(jd_ut, tithi_val, -1)
    next_nm = _find_new_moon(jd_ut, tithi_val, +1)
    this_solar_month = _solar_raasi_at_jd(last_nm)
    next_solar_month = _solar_raasi_at_jd(next_nm)
    is_leap = (this_solar_month == next_solar_month)
    maasa = this_solar_month + 1
    if maasa > 12:
        maasa = maasa % 12
    if maasa == 0:
        maasa = 12
    return int(maasa), is_leap


def _calculate_samvatsara(gregorian_year, masa_num):
    """
    Calculate the Samvatsara (60-year cycle name) using the Shaka Samvatsara system.
    
    Uses the reference point: 1987-88 = Prabhava (index 0).
    The Hindu year starts at Chaitra (masa 1, ~March/April).
    Months Pushya(10), Magha(11), Phalguna(12) fall in Jan-Mar of the
    next Gregorian year, so they belong to the Hindu year that started
    the previous April.
    
    Adhika masa does NOT affect the Samvatsara. The Shaka year number
    (and therefore the Samvatsara) is the same for both Adhika Chaitra
    and Nija Chaitra. Verified against drikpanchang.com which shows
    Shaka 1951 Saumya for both Adhika Chaitra and Nija Chaitra in 2029.
    
    Adhika months for Margashirsha(9), Pushya(10), and Magha(11) never
    occur per Hindu calendar authorities (Wikipedia, hindujagruti.org),
    so the masa_num >= 10 boundary check is always safe.
    
    Verified against drikpanchang.com Shaka Samvatsara for multiple years
    including the Adhika Chaitra 2029 edge case.
    """
    # Determine the Gregorian year when the Hindu year (Ugadi) started
    if masa_num >= 10:
        # Pushya/Magha/Phalguna fall in Jan-Mar of the next Gregorian year
        hindu_year_start = gregorian_year - 1
    else:
        hindu_year_start = gregorian_year
    
    samvat_idx = (hindu_year_start - 1987) % 60
    return SAMVATSARA_NAMES[samvat_idx]


def _calculate_ayana(sun_sidereal_longitude):
    """Determine Uttarayana or Dakshinayana based on Sun's sidereal longitude."""
    # Uttarayana: Sun in Makara(270) to Mithuna(90) — i.e., lon >= 270 or lon < 90
    # Dakshinayana: Sun in Karka(90) to Dhanu(270) — i.e., 90 <= lon < 270
    lon = sun_sidereal_longitude % 360
    if lon >= 270 or lon < 90:
        return "Uttarayana"
    else:
        return "Dakshinayana"


def _calculate_rutu(masa_num):
    """Calculate Rutu (season) from Masa number (1-12)."""
    idx = (masa_num - 1) // 2
    if idx < 0:
        idx = 0
    if idx > 5:
        idx = 5
    return RUTU_NAMES[idx]


# ---------------------------------------------------------------------------
# Main calculation function
# ---------------------------------------------------------------------------

def calculate_kundli(
    name: str,
    year: int, month: int, day: int,
    hour: int, minute: int,
    place_name: str,
    latitude: float,
    longitude: float,
    tz_offset_hours: float,
    timezone_name: str = "IST"
) -> KundliData:
    """
    Calculate all Kundli data for given birth details.
    
    Parameters:
        name: Name of the person
        year, month, day: Date of birth
        hour, minute: Time of birth (local time)
        place_name: Name of birthplace
        latitude, longitude: Geographic coordinates
        tz_offset_hours: Timezone offset from UTC in hours (e.g., 5.5 for IST)
        timezone_name: Timezone name string
    
    Returns:
        KundliData object with all calculated data
    """
    swe.set_ephe_path('')  # Use built-in Moshier ephemeris

    # Convert local time to UTC
    local_decimal_hour = hour + minute / 60.0
    utc_decimal_hour = local_decimal_hour - tz_offset_hours

    # Handle date rollover
    utc_year, utc_month, utc_day = year, month, day
    if utc_decimal_hour < 0:
        utc_decimal_hour += 24
        dt = datetime(year, month, day) - timedelta(days=1)
        utc_year, utc_month, utc_day = dt.year, dt.month, dt.day
    elif utc_decimal_hour >= 24:
        utc_decimal_hour -= 24
        dt = datetime(year, month, day) + timedelta(days=1)
        utc_year, utc_month, utc_day = dt.year, dt.month, dt.day

    # Calculate Julian Day
    jd_ut = swe.julday(utc_year, utc_month, utc_day, utc_decimal_hour)

    # Set Lahiri Ayanamsa
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(jd_ut)

    # -----------------------------------------------------------------------
    # Calculate planetary positions
    # -----------------------------------------------------------------------
    grahas = []
    rahu_longitude = None

    for i, graha_name in enumerate(GRAHA_NAMES):
        se_id = GRAHA_SE_IDS[i]

        if se_id == -1:
            # Ketu = Rahu + 180
            trop_lon = rahu_longitude + 180.0
            trop_lon = normalize_longitude(trop_lon)
            is_retro = True  # Rahu/Ketu are always retrograde
            # We need the tropical longitude of Rahu to compute Ketu
            # But we stored sidereal Rahu, so recalculate
            sid_lon = normalize_longitude(trop_lon - ayanamsa)
        else:
            result = swe.calc_ut(jd_ut, se_id)
            trop_lon = result[0][0]
            speed = result[0][3]
            is_retro = speed < 0

            if se_id == swe.MEAN_NODE:
                rahu_longitude = trop_lon
                is_retro = True  # Rahu is always retrograde

            sid_lon = normalize_longitude(trop_lon - ayanamsa)

        rashi_idx, deg_in_rashi = longitude_to_rashi(sid_lon)
        nak_idx, pada = longitude_to_nakshatra(sid_lon)
        nak_lord = get_nakshatra_lord(nak_idx)
        dignity = get_dignity(graha_name, rashi_idx)

        graha = GrahaPosition(
            name=graha_name,
            abbr=GRAHA_ABBR[i],
            longitude=sid_lon,
            rashi_index=rashi_idx,
            rashi_name=RASHI_NAMES[rashi_idx],
            rashi_lord=RASHI_LORDS[rashi_idx],
            degree_in_rashi=deg_in_rashi,
            nakshatra_index=nak_idx,
            nakshatra_name=NAKSHATRA_NAMES[nak_idx],
            nakshatra_lord=nak_lord,
            pada=pada,
            is_retrograde=is_retro,
            dignity=dignity
        )
        grahas.append(graha)

    # -----------------------------------------------------------------------
    # Calculate Lagna (Ascendant)
    # -----------------------------------------------------------------------
    # Use Whole Sign houses
    houses_result = swe.houses(jd_ut, latitude, longitude, b'W')
    asc_trop = houses_result[1][0]
    asc_sid = normalize_longitude(asc_trop - ayanamsa)

    asc_rashi_idx, asc_deg = longitude_to_rashi(asc_sid)
    asc_nak_idx, asc_pada = longitude_to_nakshatra(asc_sid)
    asc_nak_lord = get_nakshatra_lord(asc_nak_idx)

    lagna = GrahaPosition(
        name="Lagna",
        abbr="Lg",
        longitude=asc_sid,
        rashi_index=asc_rashi_idx,
        rashi_name=RASHI_NAMES[asc_rashi_idx],
        rashi_lord=RASHI_LORDS[asc_rashi_idx],
        degree_in_rashi=asc_deg,
        nakshatra_index=asc_nak_idx,
        nakshatra_name=NAKSHATRA_NAMES[asc_nak_idx],
        nakshatra_lord=asc_nak_lord,
        pada=asc_pada,
        is_retrograde=False,
        dignity=""
    )

    # -----------------------------------------------------------------------
    # Build rashi-to-graha mapping for chart rendering
    # -----------------------------------------------------------------------
    rashi_grahas = {i: [] for i in range(12)}
    for g in grahas:
        rashi_grahas[g.rashi_index].append(g.abbr + ("(R)" if g.is_retrograde else ""))
    # Mark Lagna
    rashi_grahas[asc_rashi_idx].insert(0, "Lg")

    # -----------------------------------------------------------------------
    # Calculate Panchang
    # -----------------------------------------------------------------------
    sun_sid = grahas[0].longitude  # Surya
    moon_sid = grahas[1].longitude  # Chandra

    # Tithi
    moon_sun_diff = normalize_longitude(moon_sid - sun_sid)
    tithi_number = int(moon_sun_diff / 12.0)
    if tithi_number >= 30:
        tithi_number = 29
    tithi_name = TITHI_NAMES[tithi_number]
    paksha = PAKSHA_NAMES[tithi_number]

    # Nakshatra (of Moon)
    moon_nak_idx = grahas[1].nakshatra_index
    moon_nak_name = grahas[1].nakshatra_name
    moon_nak_lord = grahas[1].nakshatra_lord
    moon_pada = grahas[1].pada

    # Yoga
    sun_moon_sum = normalize_longitude(sun_sid + moon_sid)
    yoga_index = int(sun_moon_sum / (13.0 + 1.0/3.0))
    if yoga_index >= 27:
        yoga_index = 26
    yoga_name = YOGA_NAMES[yoga_index]

    # Karana
    karana_number = int(moon_sun_diff / 6.0)
    if karana_number == 0:
        karana_name = KARANA_NAMES[10]  # Kimstughna
    elif karana_number >= 57:
        fixed_idx = karana_number - 57
        karana_name = KARANA_NAMES[7 + fixed_idx] if fixed_idx < 3 else KARANA_NAMES[10]
    else:
        cycle_idx = (karana_number - 1) % 7
        karana_name = KARANA_NAMES[cycle_idx]

    # Vara (weekday)
    birth_dt = datetime(year, month, day, hour, minute)
    vara_index = birth_dt.weekday()  # Monday=0
    # Convert to Sunday=0 system
    vara_index = (vara_index + 1) % 7
    vara_name = VARA_NAMES[vara_index]

    # -----------------------------------------------------------------------
    # Hindu Calendar: Masa, Samvatsara, Ayana, Rutu
    # -----------------------------------------------------------------------
    tithi_for_masa = tithi_number + 1  # 1-based tithi
    masa_num, masa_is_adhika = _calculate_masa(jd_ut, tithi_for_masa)
    masa_name = MASA_NAMES[masa_num - 1]
    samvatsara_name = _calculate_samvatsara(year, masa_num)
    ayana_name = _calculate_ayana(sun_sid)
    rutu_name = _calculate_rutu(masa_num)

    panchang = PanchangData(
        vara=vara_name,
        tithi_name=tithi_name,
        tithi_number=tithi_number + 1,
        paksha=paksha,
        nakshatra_name=moon_nak_name,
        nakshatra_lord=moon_nak_lord,
        nakshatra_pada=moon_pada,
        yoga_name=yoga_name,
        karana_name=karana_name,
        masa=masa_name,
        masa_is_adhika=masa_is_adhika,
        samvatsara=samvatsara_name,
        ayana=ayana_name,
        rutu=rutu_name
    )

    # -----------------------------------------------------------------------
    # Calculate Vimshottari Dasha
    # -----------------------------------------------------------------------
    moon_lon = grahas[1].longitude
    nak_span = 13.0 + 1.0 / 3.0
    nak_start = moon_nak_idx * nak_span
    traversed = moon_lon - nak_start
    remaining_fraction = 1.0 - (traversed / nak_span)

    # Find the starting dasha lord
    start_lord = moon_nak_lord
    start_idx = DASHA_SEQUENCE.index(start_lord)

    # Balance of first dasha
    first_dasha_total = DASHA_YEARS[start_lord]
    first_dasha_balance = remaining_fraction * first_dasha_total

    dasha_periods = []
    current_date = birth_dt

    for i in range(9):
        lord_idx = (start_idx + i) % 9
        lord = DASHA_SEQUENCE[lord_idx]

        if i == 0:
            period_years = first_dasha_balance
        else:
            period_years = DASHA_YEARS[lord]

        period_days = period_years * 365.25
        end_date = current_date + timedelta(days=period_days)

        dasha_periods.append(DashaPeriod(
            lord=lord,
            start_date=current_date,
            end_date=end_date,
            years=period_years
        ))
        current_date = end_date

    # -----------------------------------------------------------------------
    # Format UTC offset string
    # -----------------------------------------------------------------------
    offset_h = int(tz_offset_hours)
    offset_m = int((tz_offset_hours - offset_h) * 60)
    utc_offset_str = f"+{offset_h:02d}:{offset_m:02d}" if tz_offset_hours >= 0 else f"-{abs(offset_h):02d}:{abs(offset_m):02d}"

    # -----------------------------------------------------------------------
    # Build KundliData
    # -----------------------------------------------------------------------
    kundli = KundliData(
        name=name,
        birth_date=birth_dt,
        birth_time_str=f"{hour:02d}:{minute:02d}",
        birth_place=place_name,
        latitude=latitude,
        longitude=longitude,
        timezone_name=timezone_name,
        utc_offset=utc_offset_str,
        ayanamsa=ayanamsa,
        ayanamsa_name="Lahiri (Chitrapaksha)",
        lagna=lagna,
        grahas=grahas,
        panchang=panchang,
        dasha_periods=dasha_periods,
        rashi_grahas=rashi_grahas
    )

    # -----------------------------------------------------------------------
    # Calculate Bhava (House) Cusps
    # -----------------------------------------------------------------------
    bhava_cusps = []
    for h in range(12):
        cusp_rashi = (asc_rashi_idx + h) % 12
        bhava_cusps.append({
            'house': h + 1,
            'rashi_name': RASHI_NAMES[cusp_rashi],
            'rashi_lord': RASHI_LORDS[cusp_rashi]
        })
    kundli.bhava_cusps = bhava_cusps

    # -----------------------------------------------------------------------
    # Determine Lagna Lord info
    # -----------------------------------------------------------------------
    lagna_lord_name = RASHI_LORDS[asc_rashi_idx]
    lagna_lord_graha = None
    for g in grahas:
        if g.name == lagna_lord_name:
            lagna_lord_graha = g
            break
    lagna_lord_house = None
    if lagna_lord_graha:
        lagna_lord_house = ((lagna_lord_graha.rashi_index - asc_rashi_idx) % 12) + 1
    kundli.lagna_lord_name = lagna_lord_name
    kundli.lagna_lord_rashi = lagna_lord_graha.rashi_name if lagna_lord_graha else ""
    kundli.lagna_lord_house = lagna_lord_house

    # -----------------------------------------------------------------------
    # Determine Mangal Dosha (Kuja Dosha)
    # -----------------------------------------------------------------------
    mars_graha = grahas[2]  # Mangal is index 2
    mars_house = ((mars_graha.rashi_index - asc_rashi_idx) % 12) + 1
    mangal_dosha_houses = [1, 2, 4, 7, 8, 12]
    kundli.mangal_dosha = mars_house in mangal_dosha_houses
    kundli.mangal_dosha_house = mars_house

    # -----------------------------------------------------------------------
    # Extended Nakshatra details (for Moon's nakshatra)
    # -----------------------------------------------------------------------
    moon_nak = grahas[1].nakshatra_index
    kundli.nakshatra_deity = NAKSHATRA_DEITIES[moon_nak]
    kundli.nakshatra_symbol = NAKSHATRA_SYMBOLS[moon_nak]
    kundli.nakshatra_gana = NAKSHATRA_GANA[moon_nak]
    kundli.nakshatra_nadi = NAKSHATRA_NADI[moon_nak]

    swe.close()
    return kundli


def calculate_navamsa(grahas: List[GrahaPosition], lagna: GrahaPosition) -> dict:
    """
    Calculate Navamsa (D9) chart positions.
    Returns a dict mapping rashi_index -> list of graha abbreviations.
    """
    navamsa_map = {i: [] for i in range(12)}

    all_bodies = [lagna] + grahas
    for body in all_bodies:
        lon = body.longitude
        rashi_idx = int(lon / 30)
        degree_in_rashi = lon - (rashi_idx * 30)

        # Determine navamsa division (0-8)
        navamsa_div = int(degree_in_rashi / (30.0 / 9.0))
        if navamsa_div > 8:
            navamsa_div = 8

        # Determine starting sign for navamsa counting
        rashi_type = rashi_idx % 3  # 0=Movable, 1=Fixed, 2=Dual
        # Movable signs: 0(Mesha), 3(Karka), 6(Tula), 9(Makara)
        # Fixed signs: 1(Vrishabha), 4(Simha), 7(Vrishchika), 10(Kumbha)
        # Dual signs: 2(Mithuna), 5(Kanya), 8(Dhanu), 11(Meena)

        if rashi_idx in [0, 3, 6, 9]:  # Movable
            start_sign = rashi_idx
        elif rashi_idx in [1, 4, 7, 10]:  # Fixed
            start_sign = (rashi_idx + 8) % 12  # 9th from it
        else:  # Dual
            start_sign = (rashi_idx + 4) % 12  # 5th from it

        navamsa_rashi = (start_sign + navamsa_div) % 12

        label = body.abbr
        if body.name != "Lagna" and body.is_retrograde:
            label += "(R)"
        navamsa_map[navamsa_rashi].append(label)

    return navamsa_map
