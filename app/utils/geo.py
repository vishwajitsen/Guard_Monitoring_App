import os
import requests
import geocoder
from openlocationcode import openlocationcode as olc

USER_AGENT = "GuardMonitoringApp/1.0 (contact: example@example.com)"  # edit if you like

def get_current_location():
    """
    Try IP-based geolocation. Returns (lat, lon, source).
    If it fails, returns ("", "", "manual") so UI can ask the user.
    """
    try:
        g = geocoder.ip("me")
        if g and g.latlng:
            return float(g.latlng[0]), float(g.latlng[1]), "ip"
    except Exception:
        pass
    return "", "", "manual"

def reverse_geocode_google(lat, lon, api_key):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"latlng": f"{lat},{lon}", "key": api_key}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    js = r.json()
    if js.get("status") != "OK":
        return None, None
    result = js["results"][0]
    addr = result.get("formatted_address", "")
    pincode = None
    for comp in result.get("address_components", []):
        if "postal_code" in comp.get("types", []):
            pincode = comp.get("long_name")
            break
    return addr, pincode

def reverse_geocode_osm(lat, lon):
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "addressdetails": 1
    }
    r = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=10)
    r.raise_for_status()
    js = r.json()
    addr = js.get("display_name", "")
    pincode = (js.get("address", {}) or {}).get("postcode")
    return addr, pincode

def reverse_geocode(lat, lon):
    """
    Returns (address, pincode). Tries Google first if key present, else OSM.
    """
    if lat == "" or lon == "" or lat is None or lon is None:
        return "", ""
    key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if key:
        try:
            addr, pin = reverse_geocode_google(lat, lon, key)
            if addr:
                return addr, pin or ""
        except Exception:
            pass
    # fallback to OSM
    try:
        addr, pin = reverse_geocode_osm(lat, lon)
        return addr or "", pin or ""
    except Exception:
        return "", ""

def to_plus_code(lat, lon, code_length=11):
    try:
        return olc.encode(float(lat), float(lon), codeLength=code_length)
    except Exception:
        return ""
