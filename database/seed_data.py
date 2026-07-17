

import csv
import random
from datetime import datetime, timedelta

from database.db import init_db, get_connection, table_has_rows
from config import CRIME_CSV_PATH

random.seed(42)

CRIME_CATEGORIES = {
    "Theft": ["Vehicle Theft", "Burglary", "Shoplifting", "Pickpocketing"],
    "Violent Crime": ["Assault", "Robbery", "Homicide", "Domestic Violence"],
    "Cybercrime": ["Phishing", "Online Fraud", "Identity Theft", "Hacking"],
    "Public Order": ["Vandalism", "Public Intoxication", "Trespassing"],
    "Narcotics": ["Drug Possession", "Drug Trafficking"],
}

ZONES = ["Zone 1", "Zone 2", "Zone 3", "Zone 4", "Zone 5", "Zone 6"]

ZONE_DOMINANT_CATEGORY = {
    "Zone 1": "Theft",
    "Zone 2": "Theft",
    "Zone 3": "Public Order",
    "Zone 4": "Violent Crime",
    "Zone 5": "Narcotics",
    "Zone 6": "Cybercrime",
}
ZONE_DOMINANT_WEIGHT = 0.55

CATEGORY_HOUR_WEIGHTS = {
    "Theft": [3]*6 + [8]*6 + [10]*6 + [4]*6,
    "Violent Crime": [2]*6 + [3]*6 + [5]*6 + [10]*6,
    "Cybercrime": [6]*24,
    "Public Order": [2]*6 + [4]*6 + [6]*6 + [9]*6,
    "Narcotics": [9]*6 + [2]*6 + [2]*6 + [7]*6,
}

# Rough lat/lng box so map markers cluster around one city (Chennai) for
# a believable-looking map without needing a real geocoded dataset.
CITY_CENTER = (13.0827, 80.2707)

LOCATION_NAMES = [
    "MG Road Junction", "Central Market", "Riverside Park", "North Bus Depot",
    "Old Town Square", "Industrial Estate", "Lakeview Colony", "Railway Station Rd",
    "Hilltop Avenue", "Greenfield Sector 7", "Harbor Front", "University Gate",
]

SEVERITIES = ["Low", "Medium", "High", "Critical"]
STATUSES = ["Solved", "Pending", "Under Investigation"]


def _random_datetime_within(days_back: int) -> datetime:
    delta_days = random.randint(0, days_back)
    delta_seconds = random.randint(0, 86399)
    return datetime.now() - timedelta(days=delta_days, seconds=delta_seconds)


def _random_coord():
    lat = CITY_CENTER[0] + random.uniform(-0.08, 0.08)
    lng = CITY_CENTER[1] + random.uniform(-0.08, 0.08)
    return round(lat, 6), round(lng, 6)


def _pick_category_for_zone(zone: str) -> str:
    all_categories = list(CRIME_CATEGORIES.keys())
    dominant = ZONE_DOMINANT_CATEGORY[zone]
    if random.random() < ZONE_DOMINANT_WEIGHT:
        return dominant
    return random.choice(all_categories)


def _pick_hour_for_category(category: str) -> int:
    weights = CATEGORY_HOUR_WEIGHTS[category]
    return random.choices(range(24), weights=weights)[0]


def generate_rows(n=1800):
    rows = []
    for _ in range(n):
        zone = random.choice(ZONES)
        category = _pick_category_for_zone(zone)
        crime_type = random.choice(CRIME_CATEGORIES[category])

        ts = _random_datetime_within(days_back=365)
        target_hour = _pick_hour_for_category(category)
        ts = ts.replace(hour=target_hour, minute=random.randint(0, 59), second=random.randint(0, 59))

        lat, lng = _random_coord()

        # Weight severity/weapon involvement by category so the data has
        # believable structure for the ML model to actually learn from.
        if category == "Violent Crime":
            severity = random.choices(SEVERITIES, weights=[10, 25, 40, 25])[0]
            weapon = random.choices([0, 1], weights=[35, 65])[0]
        elif category == "Cybercrime":
            severity = random.choices(SEVERITIES, weights=[40, 35, 20, 5])[0]
            weapon = 0
        else:
            severity = random.choices(SEVERITIES, weights=[45, 35, 15, 5])[0]
            weapon = random.choices([0, 1], weights=[85, 15])[0]

        status = random.choices(STATUSES, weights=[45, 35, 20])[0]

        rows.append({
            "crime_type": crime_type,
            "category": category,
            "date_reported": ts.strftime("%Y-%m-%d"),
            "time_reported": ts.strftime("%H:%M:%S"),
            "zone": zone,
            "location_name": random.choice(LOCATION_NAMES),
            "latitude": lat,
            "longitude": lng,
            "status": status,
            "severity": severity,
            "weapon_involved": weapon,
            "victim_age": random.randint(16, 75),
            "victim_gender": random.choice(["Male", "Female", "Other"]),
            "day_of_week": ts.strftime("%A"),
            "hour_of_day": ts.hour,
            "description": f"{crime_type} reported near {random.choice(LOCATION_NAMES)}.",
        })
    return rows


def write_csv(rows):
    fieldnames = list(rows[0].keys())
    with open(CRIME_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_into_db(rows):
    conn = get_connection()
    cur = conn.cursor()
    cur.executemany(
        """
        INSERT INTO crimes (
            crime_type, category, date_reported, time_reported, zone,
            location_name, latitude, longitude, status, severity,
            weapon_involved, victim_age, victim_gender, day_of_week,
            hour_of_day, description
        ) VALUES (
            :crime_type, :category, :date_reported, :time_reported, :zone,
            :location_name, :latitude, :longitude, :status, :severity,
            :weapon_involved, :victim_age, :victim_gender, :day_of_week,
            :hour_of_day, :description
        )
        """,
        rows,
    )
    conn.commit()
    conn.close()


def seed(force=False):
    init_db()
    if table_has_rows() and not force:
        print("Database already seeded - skipping. Pass force=True to reseed.")
        return
    rows = generate_rows()
    write_csv(rows)
    load_into_db(rows)
    print(f"Seeded {len(rows)} crime records into {CRIME_CSV_PATH.name} and SQLite.")


if __name__ == "__main__":
    seed(force=True)
