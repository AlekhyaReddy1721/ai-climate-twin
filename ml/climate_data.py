"""
Mock climate dataset — replace with real APIs (NASA, NOAA, Copernicus) in production.
"""
import math

# Historical global temperature anomaly (°C relative to 1951-1980 baseline)
# Values based on NASA GISS Surface Temperature Analysis trends
TEMP_ANOMALY_1900_2025 = {
    year: round(-0.30 + (year - 1900) * 0.0095 + (max(0, year - 1980) ** 1.6 * 0.00018), 2)
    for year in range(1900, 2026)
}

# CO2 concentration (ppm) — follows Keeling Curve shape
CO2_1900_2025 = {
    year: round(296 + (year - 1900) * 0.95 + max(0, (year - 1960) * 0.6), 1)
    for year in range(1900, 2026)
}

# Sea level rise (mm relative to 1900) — accelerating post-1993 (satellite era)
SEA_LEVEL_1900_2025 = {
    year: round((year - 1900) * 1.8 + max(0, (year - 1993) * 1.2), 1)
    for year in range(1900, 2026)
}

REGIONS = {
    "Global":        {"temp": 15.1, "co2": 421, "rainfall": 990,  "sea_level": 0,    "risk": "medium"},
    "Arctic":        {"temp": -10.2,"co2": 421, "rainfall": 250,  "sea_level": 0,    "risk": "critical"},
    "Amazon":        {"temp": 26.5, "co2": 415, "rainfall": 2300, "sea_level": 0,    "risk": "high"},
    "Sahara":        {"temp": 30.1, "co2": 418, "rainfall": 25,   "sea_level": 0,    "risk": "high"},
    "South Asia":    {"temp": 27.3, "co2": 430, "rainfall": 1200, "sea_level": 12,   "risk": "critical"},
    "Europe":        {"temp": 10.5, "co2": 410, "rainfall": 650,  "sea_level": 5,    "risk": "medium"},
    "North America": {"temp": 8.9,  "co2": 415, "rainfall": 715,  "sea_level": 8,    "risk": "medium"},
    "Pacific Islands":{"temp":28.1, "co2": 420, "rainfall": 1800, "sea_level": 25,   "risk": "critical"},
    "Australia":     {"temp": 21.8, "co2": 412, "rainfall": 465,  "sea_level": 7,    "risk": "high"},
    "Sub-Saharan Africa":{"temp":25.4,"co2":416,"rainfall": 800,  "sea_level": 3,    "risk": "high"},
}

COUNTRY_RANKINGS = [
    {"rank":1,  "country":"Iceland",       "score":94, "co2_per_capita":3.5,  "renewables":85, "pollution":2},
    {"rank":2,  "country":"Norway",        "score":91, "co2_per_capita":6.2,  "renewables":98, "pollution":3},
    {"rank":3,  "country":"Sweden",        "score":89, "co2_per_capita":4.1,  "renewables":75, "pollution":4},
    {"rank":4,  "country":"Denmark",       "score":87, "co2_per_capita":5.0,  "renewables":80, "pollution":5},
    {"rank":5,  "country":"Switzerland",   "score":85, "co2_per_capita":4.4,  "renewables":60, "pollution":4},
    {"rank":6,  "country":"Costa Rica",    "score":82, "co2_per_capita":1.6,  "renewables":99, "pollution":6},
    {"rank":7,  "country":"New Zealand",   "score":79, "co2_per_capita":6.8,  "renewables":84, "pollution":5},
    {"rank":8,  "country":"Finland",       "score":77, "co2_per_capita":6.5,  "renewables":45, "pollution":6},
    {"rank":9,  "country":"Germany",       "score":72, "co2_per_capita":8.1,  "renewables":46, "pollution":8},
    {"rank":10, "country":"France",        "score":70, "co2_per_capita":4.6,  "renewables":23, "pollution":7},
    {"rank":50, "country":"Brazil",        "score":55, "co2_per_capita":2.3,  "renewables":45, "pollution":15},
    {"rank":80, "country":"India",         "score":42, "co2_per_capita":1.9,  "renewables":22, "pollution":35},
    {"rank":100,"country":"China",         "score":38, "co2_per_capita":7.4,  "renewables":29, "pollution":42},
    {"rank":120,"country":"USA",           "score":35, "co2_per_capita":14.2, "renewables":21, "pollution":28},
    {"rank":150,"country":"Saudi Arabia",  "score":22, "co2_per_capita":18.1, "renewables":1,  "pollution":55},
]

DISASTER_HEATMAP = [
    {"lat": 23.5, "lng": 90.3,  "type": "flood",    "risk": 0.92, "region": "Bangladesh"},
    {"lat": 14.1, "lng": 121.0, "type": "cyclone",  "risk": 0.88, "region": "Philippines"},
    {"lat": -8.5, "lng": 115.2, "type": "flood",    "risk": 0.75, "region": "Indonesia"},
    {"lat": 30.0, "lng": 31.2,  "type": "heatwave", "risk": 0.85, "region": "Egypt"},
    {"lat": 19.4, "lng": -99.1, "type": "drought",  "risk": 0.70, "region": "Mexico"},
    {"lat": -23.5,"lng": -46.6, "type": "flood",    "risk": 0.65, "region": "Brazil"},
    {"lat": 35.7, "lng": 139.7, "type": "cyclone",  "risk": 0.72, "region": "Japan"},
    {"lat": 28.6, "lng": 77.2,  "type": "heatwave", "risk": 0.90, "region": "India"},
    {"lat": -33.9,"lng": 151.2, "type": "wildfire", "risk": 0.80, "region": "Australia"},
    {"lat": 37.8, "lng": -122.4,"type": "wildfire", "risk": 0.78, "region": "California"},
    {"lat": 51.5, "lng": 0.1,   "type": "flood",    "risk": 0.55, "region": "UK"},
    {"lat": 6.4,  "lng": 2.4,   "type": "flood",    "risk": 0.82, "region": "West Africa"},
    {"lat": -1.3, "lng": 36.8,  "type": "drought",  "risk": 0.88, "region": "East Africa"},
    {"lat": 15.5, "lng": 32.5,  "type": "drought",  "risk": 0.91, "region": "Sudan"},
    {"lat": 25.2, "lng": 55.3,  "type": "heatwave", "risk": 0.95, "region": "UAE"},
]

TIME_MACHINE_DATA = {
    1900: {"temp_anomaly": -0.30, "co2": 296, "sea_level": 0,   "arctic_ice": 14.5, "events": ["Pre-industrial baseline", "Coal era begins"]},
    1950: {"temp_anomaly": -0.01, "co2": 311, "sea_level": 72,  "arctic_ice": 13.8, "events": ["Post-WWII industrial boom", "Smog events in London"]},
    2000: {"temp_anomaly":  0.42, "co2": 369, "sea_level": 180, "arctic_ice": 12.1, "events": ["Kyoto Protocol", "Record El Niño 1998"]},
    2025: {"temp_anomaly":  1.45, "co2": 421, "sea_level": 220, "arctic_ice": 10.2, "events": ["Paris Agreement targets missed", "Record heatwaves globally"]},
    2050: {"temp_anomaly":  2.10, "co2": 480, "sea_level": 310, "arctic_ice": 7.5,  "events": ["Projected: Major coastal flooding", "Projected: Arctic summers ice-free"]},
    2100: {"temp_anomaly":  3.80, "co2": 600, "sea_level": 650, "arctic_ice": 3.2,  "events": ["Projected: Catastrophic sea rise", "Projected: Mass ecosystem collapse"]},
}
