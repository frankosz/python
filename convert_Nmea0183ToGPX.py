import re
from datetime import datetime
from pathlib import Path

def nmea_to_gpx(input_log_path, output_gpx_path):
    with open(input_log_path, 'r') as f:
        lines = f.readlines()

    gpx_head = '''<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Quark-A036-Parser" xmlns="http://topografix.com">
  <trk><name>Logged Voyage 2026</name><trkseg>'''
    gpx_foot = '''</trkseg></trk>\n</gpx>'''
    
    trackpoints = []
    current_time = ""
    is_2026 = False  # Status-Flag für das Jahr 2026

    for line in lines:
        # 1. Parse Zeit & Datum aus $GPZDA
        if "$GPZDA" in line:
            parts = line.split(',')
            if len(parts) >= 5:
                time_part = parts[1] # hhmmss.ss
                day = parts[2]
                month = parts[3]
                year = parts[4]
                
                # Filter: Nur fortfahren, wenn das Jahr exakt 2026 ist
                if year == "2026":
                    is_2026 = True
                    # ISO-Timestamp bauen (YYYY-MM-DDThh:mm:ssZ)
                    current_time = f"{year}-{month.zfill(2)}-{day.zfill(2)}T{time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}Z"
                else:
                    is_2026 = False
                    current_time = "" # Zeit zurücksetzen für falsche Jahre

        # 2. Koordinaten aus $GPGLL auslesen (nur wenn das Jahr 2026 aktiv ist)
        elif "$GPGLL" in line and is_2026:
            parts = line.split(',')
            if len(parts) >= 7 and parts[6] == 'A': # 'A' bedeutet gültige GPS-Daten
                try:
                    # NMEA Lat (DDMM.MMMM) in Dezimalgrad umrechnen
                    lat_raw = float(parts[1])
                    lat_deg = int(lat_raw / 100)
                    lat_min = lat_raw - (lat_deg * 100)
                    lat = lat_deg + (lat_min / 60.0)
                    if parts[2] == 'S': lat = -lat

                    # NMEA Lon (DDDMM.MMMM) in Dezimalgrad umrechnen
                    lon_raw = float(parts[3])
                    lon_deg = int(lon_raw / 100)
                    lon_min = lon_raw - (lon_deg * 100)
                    lon = lon_deg + (lon_min / 60.0)
                    if parts[4] == 'W': lon = -lon

                    # Trackpunkt-String bauen
                    tp = f'    <trkpt lat="{lat:.6f}" lon="{lon:.6f}">'
                    if current_time:
                        tp += f'<time>{current_time}</time>'
                    tp += '</trkpt>'
                    trackpoints.append(tp)
                except (ValueError, IndexError):
                    continue

    # GPX-Datei schreiben
    with open(output_gpx_path, 'w') as f:
        f.write(gpx_head + "\n" + "\n".join(trackpoints) + "\n" + gpx_foot)
    print(f"Erfolgreich {len(trackpoints)} Trackpunkte aus dem Jahr 2026 nach {output_gpx_path} exportiert.")

def convert_date_folders(base_path, start_date, end_date):
    base_path = Path(base_path)
    if not base_path.is_dir():
        raise FileNotFoundError(f"Folder does not exist: {base_path}")

    for folder in sorted(base_path.iterdir()):
        if not folder.is_dir() or not re.fullmatch(r"\d{8}", folder.name):
            continue

        try:
            folder_date = datetime.strptime(folder.name, "%Y%m%d").date()
        except ValueError:
            continue

        if not start_date <= folder_date <= end_date:
            continue

        input_path = folder / "combined.txt"
        if not input_path.is_file():
            print(f"Übersprungen (combined.txt fehlt): {folder}")
            continue

        output_path = folder / "vessel_track.gpx"
        nmea_to_gpx(input_path, output_path)


if __name__ == "__main__":
    convert_date_folders(
        r"E:\OneDrive - OSZ IMT\Privat\07_Sport\Segeln\_Lotta\Törndaten\2026_07+08_Schweden_Westküste",
        datetime.strptime("20260714", "%Y%m%d").date(),
        datetime.strptime("20260814", "%Y%m%d").date(),
    )
