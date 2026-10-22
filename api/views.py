import json
import urllib.request as _urllib
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ml.climate_data import (
    TEMP_ANOMALY_1900_2025, CO2_1900_2025, SEA_LEVEL_1900_2025,
    REGIONS, COUNTRY_RANKINGS, DISASTER_HEATMAP, TIME_MACHINE_DATA
)
import ml.predictor as predictor
from ml.chat_engine import ask


def climate_metrics(request):
    current_year = 2025
    return JsonResponse({
        "global_temp": 15.1,
        "temp_anomaly": TEMP_ANOMALY_1900_2025[current_year],
        "co2_ppm": CO2_1900_2025[current_year],
        "sea_level_mm": SEA_LEVEL_1900_2025[current_year],
        "arctic_ice_extent_mkm2": 10.2,
        "global_rainfall_mm": 990,
        "ocean_temp_c": 17.3,
        "humidity_percent": 62,
        "alerts": [
            {"type": "heatwave", "region": "South Asia",    "severity": "critical"},
            {"type": "drought",  "region": "East Africa",   "severity": "high"},
            {"type": "cyclone",  "region": "Bay of Bengal", "severity": "warning"},
        ]
    })


def historical_data(request):
    years = list(range(1900, 2026))
    return JsonResponse({
        "years": years,
        "temperature_anomaly": [TEMP_ANOMALY_1900_2025[y] for y in years],
        "co2_ppm": [CO2_1900_2025[y] for y in years],
        "sea_level_mm": [SEA_LEVEL_1900_2025[y] for y in years],
    })


def region_data(request, region):
    data = REGIONS.get(region, REGIONS["Global"])
    temp_pred = predictor.predict_temperature(2050)
    REGION_ANOMALY_OFFSET = {
        "Arctic": 0.8, "Amazon": 0.3, "Sahara": 0.5, "South Asia": 0.4,
        "Pacific Islands": 0.3, "Australia": 0.4, "Sub-Saharan Africa": 0.3,
        "Europe": 0.2, "North America": 0.2, "Global": 0.0,
    }
    base_anomaly = TEMP_ANOMALY_1900_2025[2025]
    region_anomaly = round(base_anomaly + REGION_ANOMALY_OFFSET.get(region, 0.0), 2)
    disaster_pred = predictor.predict_disasters(region, region_anomaly)
    return JsonResponse({
        "region": region,
        "current": data,
        "prediction_2050": temp_pred,
        "disaster_risks": disaster_pred["risks"],
    })


def climate_by_coords(request):
    """Return coordinate-specific climate data derived from lat/lng."""
    import math
    try:
        lat = float(request.GET.get('lat', 0))
        lng = float(request.GET.get('lng', 0))
    except ValueError:
        return JsonResponse({"error": "invalid coords"}, status=400)

    # ── Temperature: varies by latitude (cold poles, hot tropics) ──────────────
    # Base temp from latitude band
    abs_lat = abs(lat)
    if abs_lat < 10:
        base_temp = 27.5
    elif abs_lat < 23.5:
        base_temp = 27.0 - (abs_lat - 10) * 0.15   # tropics stay hot longer
    elif abs_lat < 35:
        base_temp = 25.0 - (abs_lat - 23.5) * 0.4
    elif abs_lat < 50:
        base_temp = 20.4 - (abs_lat - 35) * 0.6
    elif abs_lat < 60:
        base_temp = 11.4 - (abs_lat - 50) * 0.7
    elif abs_lat < 75:
        base_temp = 4.4  - (abs_lat - 60) * 0.7
    else:
        base_temp = -6.1 - (abs_lat - 75) * 0.5

    # Continental vs oceanic modifier (land heats/cools more)
    is_ocean = _is_ocean_coords(lat, lng)
    if not is_ocean:
        if abs_lat < 35:
            base_temp += 2.0   # continental tropics/subtropics are hotter
        elif abs_lat > 50:
            base_temp -= 2.0   # continental high latitudes are colder

    # ── Regional overrides (annual mean °C, well-established values) ────────────
    # South Asia / India: annual mean ~27-28°C
    if 8 < lat < 35 and 65 < lng < 100:
        base_temp = 28.0 - (lat - 8) * 0.12

    # Southeast Asia: hot and humid ~27-29°C
    if -10 < lat < 25 and 95 < lng < 145:
        base_temp = 27.5 - abs_lat * 0.08

    # Sahara / Arabian Peninsula: very hot ~30-35°C annual mean
    if 15 < lat < 35 and -15 < lng < 60:
        base_temp = 32.0 - (lat - 15) * 0.15

    # Sub-Saharan Africa: ~25-28°C
    if -10 < lat < 15 and -20 < lng < 50:
        base_temp = 27.0

    # East Africa highlands: cooler ~18-22°C
    if -5 < lat < 15 and 30 < lng < 45:
        base_temp = 22.0

    # Mediterranean: ~17-20°C annual mean
    if 30 < lat < 45 and -10 < lng < 40:
        base_temp = 18.0 - (lat - 30) * 0.2

    # Central/Northern Europe: ~8-12°C
    if 45 < lat < 60 and -10 < lng < 30:
        base_temp = 11.0 - (lat - 45) * 0.4

    # Scandinavia / Northern Europe: ~2-6°C
    if 60 < lat < 72 and -10 < lng < 30:
        base_temp = 5.0 - (lat - 60) * 0.5

    # Amazon / tropical South America: ~26-28°C
    if -15 < lat < 5 and -75 < lng < -45:
        base_temp = 27.0

    # Australian interior: hot ~28-32°C
    if -35 < lat < -15 and 115 < lng < 145:
        base_temp = 30.0 + (lat + 15) * 0.1   # hotter in north, cooler south

    # Southern Australia / SE Australia: ~14-18°C
    if -40 < lat < -30 and 140 < lng < 155:
        base_temp = 16.0

    # East Asia (China/Japan): ~12-20°C depending on latitude
    if 20 < lat < 45 and 100 < lng < 145:
        base_temp = 22.0 - (lat - 20) * 0.4

    # North America east coast: ~10-20°C
    if 25 < lat < 50 and -90 < lng < -60:
        base_temp = 22.0 - (lat - 25) * 0.45

    # Canada / Northern North America: cold
    if 50 < lat < 70 and -140 < lng < -60:
        base_temp = 4.0 - (lat - 50) * 0.5

    # Add 2025 warming anomaly (scaled — anomaly is relative to 1951-1980 baseline)
    base_anomaly = TEMP_ANOMALY_1900_2025[2025]
    temp = round(base_temp + base_anomaly, 1)

    # ── CO2: globally ~421 ppm with slight industrial hotspot variation ─────────
    co2_base = CO2_1900_2025[2025]
    # Industrial regions slightly higher
    co2_offset = 0
    if 30 < lat < 60 and -130 < lng < -60:  co2_offset = 4   # North America industry
    if 25 < lat < 55 and 100 < lng < 135:   co2_offset = 8   # East Asia industry
    if 45 < lat < 60 and 10 < lng < 40:     co2_offset = 3   # Europe industry
    co2 = round(co2_base + co2_offset, 1)

    # ── Rainfall: latitude + geography driven ───────────────────────────────────
    if abs_lat < 10:
        rainfall = 2200  # equatorial
    elif abs_lat < 25:
        rainfall = 900
    elif abs_lat < 40:
        rainfall = 650
    elif abs_lat < 60:
        rainfall = 700
    else:
        rainfall = 300

    # Monsoon boost — South/SE Asia
    if 5 < lat < 30 and 65 < lng < 110:    rainfall = 1400
    # Amazon
    if -15 < lat < 5 and -75 < lng < -45:  rainfall = 2400
    # Sahara/Arabian desert
    if 15 < lat < 35 and -15 < lng < 60:   rainfall = 30
    # Australian desert
    if -35 < lat < -15 and 115 < lng < 140: rainfall = 280
    # Mediterranean
    if 30 < lat < 45 and -10 < lng < 40:   rainfall = 500
    # Pacific NW / NW Europe
    if 45 < lat < 65 and (-130 < lng < -110 or -10 < lng < 20): rainfall = 900

    # Ocean areas get average rainfall
    if is_ocean: rainfall = 1000

    # ── Sea level: coastal areas affected ──────────────────────────────────────
    sea_level = SEA_LEVEL_1900_2025[2025] if not is_ocean else SEA_LEVEL_1900_2025[2025]
    # Low-lying coastal boost
    if abs_lat < 30 and is_ocean: sea_level = round(sea_level * 1.1, 1)

    # ── Risk level ──────────────────────────────────────────────────────────────
    if temp > 35 or (abs_lat < 20 and rainfall < 100):
        risk = "critical"
    elif temp > 28 or abs_lat < 30:
        risk = "high"
    elif temp > 18:
        risk = "medium"
    else:
        risk = "low"

    # ── Disaster risks: continuous coordinate functions ─────────────────────────
    # Uses Gaussian "hotspot" functions so risk peaks at known centres and
    # falls off smoothly — nearby places get similar but not identical values.

    def gauss(clat, clng, sigma_lat, sigma_lng, peak):
        """Gaussian bump centred at (clat, clng)."""
        dlat = (lat - clat) / sigma_lat
        dlng = (lng - clng) / sigma_lng
        return peak * math.exp(-0.5 * (dlat**2 + dlng**2))

    # ── FLOOD ──────────────────────────────────────────────────────────────────
    # Base: tropical latitudes are wetter
    flood = 0.12 + max(0, 0.25 * math.cos(math.radians(lat * 2.5)))
    # Monsoon hotspots
    flood += gauss(23,  90,  8, 10, 0.55)   # Bangladesh / NE India
    flood += gauss(16,  80,  8, 12, 0.40)   # Andhra / Odisha coast
    flood += gauss(10, 106,  6,  8, 0.45)   # Mekong delta / Vietnam
    flood += gauss(15, 100,  8, 10, 0.40)   # Thailand / Myanmar
    flood += gauss( 5, 118,  8, 12, 0.50)   # Philippines / Borneo
    flood += gauss( 6,   3,  6,  8, 0.45)   # West Africa / Nigeria
    flood += gauss(-3,  37,  6,  8, 0.35)   # East Africa / Kenya
    flood += gauss(30, -90,  8, 10, 0.35)   # Mississippi / Gulf Coast
    flood += gauss(-15, -48, 8, 10, 0.30)   # Brazil coast
    flood += gauss(52,   5,  5,  6, 0.25)   # Netherlands / Rhine delta
    if is_ocean: flood *= 0.4

    # ── DROUGHT ────────────────────────────────────────────────────────────────
    # Base: drier at subtropical latitudes (~30°)
    drought = 0.10 + 0.20 * math.exp(-((abs_lat - 28) / 18)**2)
    # Desert hotspots
    drought += gauss(25,  15, 10, 20, 0.65)   # Sahara core
    drought += gauss(24,  45, 10, 15, 0.55)   # Arabian Peninsula
    drought += gauss(-25, 130, 10, 15, 0.50)  # Australian outback
    drought += gauss(38, -105,  8, 12, 0.40)  # US Great Plains / SW
    drought += gauss(-20, -65,  8, 10, 0.30)  # Atacama / Patagonia
    drought += gauss(15,  20,  8, 12, 0.45)   # Sahel
    drought += gauss(40,  60,  8, 12, 0.35)   # Central Asia steppe
    if is_ocean: drought *= 0.3

    # ── CYCLONE ────────────────────────────────────────────────────────────────
    # Base: peaks in 5-20° latitude band
    lat_factor = math.exp(-((abs_lat - 13) / 10)**2) if abs_lat < 40 else 0
    cyclone = 0.04 + 0.15 * lat_factor
    # Basin hotspots
    cyclone += gauss(15, 140, 10, 20, 0.65)   # W Pacific typhoon belt
    cyclone += gauss(15, -75, 10, 15, 0.55)   # Caribbean / Gulf
    cyclone += gauss(15,  88, 10, 12, 0.55)   # Bay of Bengal
    cyclone += gauss(-15,  55, 10, 15, 0.40)  # SW Indian Ocean
    cyclone += gauss(-15, 160, 10, 15, 0.45)  # SW Pacific / Coral Sea
    cyclone += gauss(20, 115, 10, 15, 0.50)   # South China Sea
    if is_ocean: cyclone *= 1.3   # stronger over open water

    # ── HEATWAVE ───────────────────────────────────────────────────────────────
    # Directly driven by temperature
    heatwave = 0.08 + max(0, (temp - 18) * 0.025)
    heatwave += gauss(25,  45, 10, 15, 0.40)   # Arabian Peninsula
    heatwave += gauss(30,  10, 10, 20, 0.35)   # Sahara / N Africa
    heatwave += gauss(-25, 130, 10, 15, 0.35)  # Australian interior
    heatwave += gauss(40, -115,  8, 12, 0.30)  # US Southwest
    heatwave += gauss(45,  60,  8, 12, 0.25)   # Central Asia
    heatwave += gauss(35,  35,  8, 10, 0.30)   # Middle East
    if is_ocean: heatwave *= 0.5

    # ── WILDFIRE ───────────────────────────────────────────────────────────────
    # Needs heat + dryness + vegetation — peaks in Mediterranean-climate zones
    wildfire = 0.04 + max(0, (temp - 22) * 0.012) * max(0, 1 - rainfall / 1500)
    wildfire += gauss(-30, 145, 10, 12, 0.60)  # SE Australia
    wildfire += gauss(-25, 120, 10, 12, 0.45)  # W Australia
    wildfire += gauss(40, -120,  8, 12, 0.55)  # California / Pacific NW
    wildfire += gauss(38,  -5,   8, 12, 0.35)  # Iberian Peninsula
    wildfire += gauss(38,  22,   8, 10, 0.30)  # Greece / Balkans
    wildfire += gauss(-20, -55,  8, 10, 0.30)  # Brazilian Cerrado
    wildfire += gauss(60, -110, 10, 15, 0.35)  # Canadian boreal
    wildfire += gauss(55,  80,  10, 15, 0.30)  # Siberian taiga
    if is_ocean: wildfire = 0.01

    def clamp(v): return round(min(0.99, max(0.01, v)) * 100, 1)

    return JsonResponse({
        "region": _region_fallback(lat, lng),
        "current": {
            "temp":      temp,
            "co2":       co2,
            "rainfall":  rainfall,
            "sea_level": round(sea_level, 1),
            "risk":      risk,
        },
        "disaster_risks": {
            "flood":    clamp(flood),
            "drought":  clamp(drought),
            "cyclone":  clamp(cyclone),
            "heatwave": clamp(heatwave),
            "wildfire": clamp(wildfire),
        },
    })


def _is_ocean_coords(lat, lng):
    """Rough ocean detection by coordinate exclusion of major land masses."""
    # Major land bounding boxes (approximate)
    LAND = [
        (60, 75, -170, -50),   # North America north
        (15, 60, -130, -60),   # North America main
        (-60, 15, -85, -30),   # South America
        (35, 72, -15, 45),     # Europe
        (-40, 38, -20, 55),    # Africa
        (10, 80, 25, 180),     # Asia
        (-50, -10, 110, 160),  # Australia
        (60, 90, -180, 180),   # Arctic land
        (-90, -60, -180, 180), # Antarctica
    ]
    for (lat_min, lat_max, lng_min, lng_max) in LAND:
        if lat_min < lat < lat_max and lng_min < lng < lng_max:
            return False
    return True


def regions_list(request):
    return JsonResponse({"regions": list(REGIONS.keys())})


def predict_temperature(request):
    year = int(request.GET.get("year", 2050))
    return JsonResponse(predictor.predict_temperature(year))


def predict_disasters(request):
    region = request.GET.get("region", "Global")
    year   = int(request.GET.get("year", 2050))
    temp   = predictor.predict_temperature(year)["temp_anomaly"]
    REGION_MULTIPLIER = {
        "Arctic": 2.8, "Amazon": 1.2, "Sahara": 1.4, "South Asia": 1.3,
        "Pacific Islands": 1.1, "Australia": 1.3, "Sub-Saharan Africa": 1.2,
        "Europe": 1.1, "North America": 1.0, "Global": 1.0,
    }
    region_temp = round(temp * REGION_MULTIPLIER.get(region, 1.0), 2)
    return JsonResponse(predictor.predict_disasters(region, region_temp))


@csrf_exempt
@require_http_methods(["POST"])
def run_simulation(request):
    body = json.loads(request.body)
    co2_change    = float(body.get("co2_change", 50))
    deforestation = float(body.get("deforestation", 10))
    renewables    = float(body.get("renewables", 20))
    return JsonResponse(predictor.run_simulation(co2_change, deforestation, renewables))


def time_machine_data(request, year):
    available = sorted(TIME_MACHINE_DATA.keys())
    closest = min(available, key=lambda y: abs(y - year))
    data = TIME_MACHINE_DATA[closest]
    return JsonResponse({"year": closest, **data})


@csrf_exempt
@require_http_methods(["POST"])
def calculate_carbon(request):
    body = json.loads(request.body)
    flights_km      = float(body.get("flights_km", 0))
    car_km          = float(body.get("car_km", 0))
    electricity_kwh = float(body.get("electricity_kwh", 0))
    meat_kg         = float(body.get("meat_kg", 0))
    total = (
        flights_km      * 0.000255 +
        car_km          * 0.000192 +
        electricity_kwh * 0.000233 +
        meat_kg         * 0.027
    )
    return JsonResponse({
        "total_tonnes_co2": round(total, 3),
        "breakdown": {
            "flights":     round(flights_km      * 0.000255, 3),
            "car":         round(car_km          * 0.000192, 3),
            "electricity": round(electricity_kwh * 0.000233, 3),
            "diet":        round(meat_kg         * 0.027,    3),
        },
        "vs_global_average": round(total / 4.0 * 100, 1),
        "trees_to_offset": round(total * 45),
    })


@csrf_exempt
@require_http_methods(["POST"])
def simulate_policy(request):
    body = json.loads(request.body)
    carbon_reduction     = float(body.get("carbon_reduction", 20))
    renewable_investment = float(body.get("renewable_investment", 100))
    reforestation        = float(body.get("reforestation", 50))
    return JsonResponse(predictor.simulate_policy(carbon_reduction, renewable_investment, reforestation))


def country_rankings(request):
    return JsonResponse({"rankings": COUNTRY_RANKINGS})


@csrf_exempt
@require_http_methods(["POST"])
def chat_ask(request):
    body = json.loads(request.body)
    question = body.get("question", "")
    return JsonResponse(ask(question))


def climate_alerts(request):
    alerts = [
        {"id": 1, "type": "heatwave", "region": "South Asia",    "severity": "critical", "message": "Extreme heat >48°C expected",               "date": "2025-03-16"},
        {"id": 2, "type": "cyclone",  "region": "Bay of Bengal", "severity": "high",     "message": "Category 4 cyclone forming",                "date": "2025-03-17"},
        {"id": 3, "type": "drought",  "region": "East Africa",   "severity": "high",     "message": "Severe drought — 3rd consecutive dry season","date": "2025-03-15"},
        {"id": 4, "type": "flood",    "region": "Bangladesh",    "severity": "warning",  "message": "Monsoon flooding risk elevated",             "date": "2025-03-18"},
        {"id": 5, "type": "wildfire", "region": "Australia",     "severity": "warning",  "message": "Fire danger rating: catastrophic",           "date": "2025-03-15"},
    ]
    return JsonResponse({"alerts": alerts})


def disaster_heatmap(request):
    return JsonResponse({"points": DISASTER_HEATMAP})


def geocode_search(request):
    """Forward a place name search to Nominatim and return lat/lng."""
    q = request.GET.get('q', '')
    if not q:
        return JsonResponse({'error': 'no query'}, status=400)
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={q}&format=json&limit=1&accept-language=en"
        req = _urllib.Request(url, headers={'User-Agent': 'AIClimateTwin/1.0'})
        with _urllib.urlopen(req, timeout=8) as resp:
            results = json.loads(resp.read())
        if not results:
            return JsonResponse({'lat': None, 'lng': None, 'display_name': ''})
        r = results[0]
        return JsonResponse({
            'lat': float(r['lat']),
            'lng': float(r['lon']),
            'display_name': r.get('display_name', ''),
        })
    except Exception:
        return JsonResponse({'lat': None, 'lng': None, 'display_name': ''})


def reverse_geocode(request):
    lat = request.GET.get('lat', '0')
    lng = request.GET.get('lng', '0')

    def _fetch(zoom):
        url = (
            f"https://nominatim.openstreetmap.org/reverse"
            f"?lat={lat}&lon={lng}&format=json&zoom={zoom}&accept-language=en"
        )
        req = _urllib.Request(url, headers={'User-Agent': 'AIClimateTwin/1.0'})
        with _urllib.urlopen(req, timeout=8) as resp:
            return json.loads(resp.read())

    def _extract(data):
        addr = data.get('address', {})

        # Ocean / sea detection
        ocean = (
            addr.get('ocean') or addr.get('sea') or addr.get('bay') or
            addr.get('strait') or addr.get('body_of_water') or ''
        )
        if ocean:
            return {
                'place_name':   ocean,
                'city':         ocean,
                'state':        '',
                'country':      'International Waters',
                'country_code': '',
                'is_ocean':     True,
            }

        place = (
            addr.get('city') or addr.get('town') or addr.get('municipality') or
            addr.get('village') or addr.get('hamlet') or addr.get('suburb') or
            addr.get('county') or addr.get('state_district') or addr.get('state') or
            addr.get('region') or ''
        )
        state   = addr.get('state') or addr.get('region') or addr.get('province') or ''
        country = addr.get('country') or ''
        code    = (addr.get('country_code') or '').upper()

        # Try display_name as last resort
        if not place and not country:
            display = data.get('display_name', '')
            if display:
                parts_dn = [p.strip() for p in display.split(',')]
                place   = parts_dn[0] if parts_dn else ''
                country = parts_dn[-1] if len(parts_dn) > 1 else ''

        if not place and country:
            place = country
            country = ''

        name_parts = [p for p in [place, country] if p]
        return {
            'place_name':   ', '.join(name_parts[:2]) if name_parts else None,
            'city':         place,
            'state':        state,
            'country':      country,
            'country_code': code,
            'is_ocean':     False,
        }

    try:
        # First try zoom=8 (city level)
        result = _extract(_fetch(8))
        # If no useful name, retry at zoom=4 (country level)
        if not result.get('place_name'):
            result = _extract(_fetch(4))
        # Final fallback to coordinate-based name
        if not result.get('place_name'):
            result['place_name'] = _region_fallback(float(lat), float(lng))
        return JsonResponse(result)

    except Exception:
        return JsonResponse({
            'place_name':   _region_fallback(float(lat), float(lng)),
            'city':         '',
            'state':        '',
            'country':      '',
            'country_code': '',
            'is_ocean':     False,
        })


def _region_fallback(lat, lng):
    """Derive a descriptive location name purely from coordinates."""
    # Polar regions first
    if lat > 70:
        return 'Arctic Ocean'
    if lat < -60:
        return 'Southern Ocean / Antarctica'

    # Pacific Ocean (large gap between Americas and Asia/Australia)
    if -60 < lat < 60 and (lng > 140 or lng < -80):
        # Exclude land masses: Americas west coast ~-80 to -70, Asia/Australia east coast ~140-160
        if not (-170 < lng < -80 and lat > 5):   # not North America
            if not (110 < lng < 160 and -50 < lat < -10):  # not Australia
                return 'North Pacific Ocean' if lat >= 0 else 'South Pacific Ocean'

    # Atlantic Ocean
    if -60 < lat < 65 and -80 < lng < -10:
        return 'North Atlantic Ocean' if lat >= 0 else 'South Atlantic Ocean'

    # Indian Ocean
    if -60 < lat < 25 and 20 < lng < 110:
        # Exclude Africa and South Asia land
        if not (-35 < lat < 38 and 20 < lng < 55):   # not Africa
            if not (5 < lat < 35 and 60 < lng < 90):  # not South Asia
                return 'Indian Ocean'

    # Land fallback by broad region
    if lat > 60:                                        return 'Northern Polar Region'
    if lat > 35  and -10 < lng < 40:                   return 'Europe'
    if lat > 15  and -170 < lng < -50:                 return 'North America'
    if -60 < lat < 15 and -85 < lng < -30:             return 'South America'
    if -40 < lat < 38 and -20 < lng < 55:              return 'Africa'
    if lat > 10  and 60  < lng < 150:                  return 'Asia'
    if -50 < lat < -10 and 110 < lng < 160:            return 'Australia / Oceania'
    if -25 < lat < 25  and (lng > 160 or lng < -130):  return 'Pacific Islands'
    return f'{abs(lat):.1f}°{"N" if lat>=0 else "S"}, {abs(lng):.1f}°{"E" if lng>=0 else "W"}'
