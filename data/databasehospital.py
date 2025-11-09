import pandas as pd
import numpy as np, json, os
from datetime import datetime
np.random.seed(7777)

n_hospitals = 50
pune_lat, pune_lon = 18.5204, 73.8567

base_names = [
    "Ruby Hill Hospital", "Sahyadri General Hospital", "Kothrud District Hospital", "Pune Central Medical Centre",
    "Deccan Health Institute", "Hadapsar Care Hospital", "Aundh Community Hospital", "Viman Nagar Health Centre",
    "Shivaji Nagar Hospital", "Lokmanya Medical Hospital", "Dhayari Clinic", "Katraj Care Centre",
    "Bhosari Health Campus", "Pune East Medical", "Pune West General", "PMC Community Hospital",
    "Bopodi Health Centre", "Baner Wellness", "Shivaji Hills Clinic", "Pune NMC Hospital",
    "Ambegaon Specialty Hospital", "Pune Metro Health", "FC Road Medical", "Karve Road Hospital",
    "Pashan General Hospital", "Yerawada Care", "Pune City Hospital", "Sinhagad Road Medical",
    "Kondhwa Community Hospital", "Wagholi Health Centre", "Narhe Hospital", "Pune North Hospital",
    "Pune South General", "Sadashiv Peth Hospital", "Pune Trauma Centre", "PMC Specialty", "Bhandarkar Memorial",
    "Sinhgad Road Clinic", "Mundhwa Medical", "Kalewadi Hospital", "Akurdi Health", "Dattanagar Hospital",
    "Koregaon Park Medical", "Kharadi Wellness", "Mahalunge Hospital", "Dapodi Health Centre", "Pune Central ER",
    "Lohegaon Hospital", "Gahunje Clinic", "Pune River Hospital", "Mhatre Hospital"
]

while len(base_names) < n_hospitals:
    base_names += [f"Pune Health Centre {len(base_names)+1}"]

sizes = np.random.choice(["small", "medium", "large"], size=n_hospitals, p=[0.45, 0.40, 0.15])
ownership_choices = ["govt", "private", "trust"]

hospitals = []
for i in range(n_hospitals):
    hid = f"PUNE_{i+1:03d}"
    name = f"{base_names[i]}, Pune"
    region = "Pune"
    ownership = np.random.choice(ownership_choices, p=[0.55, 0.4, 0.05])
    size = sizes[i]
    if size == "small":
        max_beds = int(np.clip(np.random.normal(60, 10), 25, 120))
    elif size == "medium":
        max_beds = int(np.clip(np.random.normal(180, 28), 80, 400))
    else:
        max_beds = int(np.clip(np.random.normal(420, 60), 200, 800))
    ward_capacity = int(max_beds * 0.68)
    lat = round(pune_lat + np.random.normal(0, 0.03), 6)
    lon = round(pune_lon + np.random.normal(0, 0.03), 6)
    hospitals.append({
        "hospital_id": hid,
        "hospital_name": name,
        "region": region,
        "latitude": lat,
        "longitude": lon,
        "ownership_type": ownership,
        "max_capacity_beds": max_beds,
        "ward_capacity_beds": ward_capacity,
        "size": size
    })
hospitals_df = pd.DataFrame(hospitals)

# --- Real-time snapshot data (single entry per hospital) ---
ts_rows = []
for _, row in hospitals_df.iterrows():
    hid = row["hospital_id"]
    max_beds = row["max_capacity_beds"]
    size = row["size"]
    ed_total_beds = max(6, int(max_beds * np.random.uniform(0.085, 0.14)))
    total_icu_beds = max(3, int(max_beds * np.random.uniform(0.035, 0.07)))
    base_util = {"small": 0.60, "medium": 0.74, "large": 0.86}[size]

    occ = int(np.clip(round(max_beds * np.random.normal(base_util, 0.07)), 0, max_beds))
    ed_occ = int(np.clip(round(ed_total_beds * np.random.normal(0.79, 0.13)), 0, ed_total_beds))
    icu_occ = int(np.clip(round(total_icu_beds * np.random.normal(0.73, 0.16)), 0, total_icu_beds))
    total_vent = max(1, int(np.clip(round(total_icu_beds * np.random.uniform(0.7, 1.5)), 1, 200)))
    in_use_vent = int(np.clip(round(total_vent * np.random.normal(0.69, 0.15)), 0, total_vent))
    est_daily_oxygen = max(150.0, icu_occ * np.random.uniform(380, 520) + (occ - icu_occ) * np.random.uniform(4, 12))
    available_oxygen = round(est_daily_oxygen * np.random.uniform(1.5, 6.0), 1)
    ts_rows.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hospital_id": hid,
        "occupied_beds": occ,
        "total_beds": max_beds,
        "ed_total_beds": ed_total_beds,
        "ed_occupied_beds": ed_occ,
        "ward_capacity_beds": row["ward_capacity_beds"],
        "total_icu_beds": total_icu_beds,
        "icu_occupied_beds": icu_occ,
        "total_ventilators": total_vent,
        "in_use_ventilators": in_use_vent,
        "oxygen_units_liters": round(est_daily_oxygen * 3, 1),
        "available_oxygen_liters": available_oxygen,
        "estimated_daily_consumption_oxygen_liters": est_daily_oxygen,
        "tb_med_stock_tablets": np.random.randint(2000, 4000),
        "diag_kits_available": np.random.randint(5, 50),
        "available_staff_count": np.random.randint(50, 400),
        "on_shift_doctors": np.random.randint(10, 60),
        "required_doctors": np.random.randint(15, 80),
        "on_shift_nurses": np.random.randint(20, 120),
        "ambulance_arrivals_24h": np.random.randint(0, 200),
        "critical_cases_ed": np.random.randint(0, 50),
        "avg_daily_admissions_7d": np.random.uniform(10, 200),
        "avg_ed_tat_minutes_1h": np.random.uniform(15, 45),
        "avg_ed_tat_minutes_6h": np.random.uniform(30, 60)
    })
timeseries_df = pd.DataFrame(ts_rows)

# --- Finance, Suppliers, Inventory (unchanged) ---
# (Keep your full finance, suppliers, and inventory sections exactly as they were)

# Everything else (SQL generation and file writing) stays the same


# --- Finance ---
finance_rows = []
for _, r in hospitals_df.iterrows():
    hid = r["hospital_id"]
    size = r["size"]
    total_exp = round(np.random.uniform(1e6, 9e6), 2)
    staff_cost = round(total_exp * np.random.uniform(0.5, 0.7), 2)
    supply_cost = round(total_exp * np.random.uniform(0.1, 0.2), 2)
    maintenance_cost = round(total_exp * np.random.uniform(0.02, 0.06), 2)
    transport_cost = round(total_exp * np.random.uniform(0.01, 0.03), 2)
    capex = round(total_exp * np.random.uniform(0.05, 0.1), 2)
    revenue = round(total_exp * np.random.uniform(0.6, 1.2), 2)
    finance_rows.append({
        "hospital_id": hid,
        "year": 2025,
        "month": 10,
        "period": "2025-10-01",
        "total_expenditure": total_exp,
        "operational_expenditure": total_exp - capex,
        "staff_cost": staff_cost,
        "supply_cost": supply_cost,
        "maintenance_cost": maintenance_cost,
        "transport_cost": transport_cost,
        "capital_expenditure": capex,
        "revenue": revenue,
        "budget_allocated": round(total_exp * 1.2, 2),
        "budget_remaining": round(total_exp * 0.2, 2),
        "data_confidence": "reported",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
finance_df = pd.DataFrame(finance_rows)

# --- Suppliers & Inventory ---
suppliers_df = pd.DataFrame([
    {"vendor_id": "100000001", "vendor_name": "OxySupply Pvt Ltd", "vendor_type": "distributor", "contact": '{"phone":"+91-20-55550001","email":"sales@oxysupply.in"}', "lead_time_days": 2, "payment_terms_days": 30},
    {"vendor_id": "100000002", "vendor_name": "MedEquip Traders", "vendor_type": "manufacturer", "contact": '{"phone":"+91-20-55550002","email":"contact@medequip.in"}', "lead_time_days": 6, "payment_terms_days": 45},
    {"vendor_id": "100000003", "vendor_name": "Rapid Diagnostics Co", "vendor_type": "labkits", "contact": '{"phone":"+91-20-55550004","email":"sales@rapiddiag.in"}', "lead_time_days": 3, "payment_terms_days": 30},
])

inventory_df = pd.DataFrame([
    {"item_id": "OXY_LITER", "item_name": "Oxygen (liters)", "unit": "liters", "reorder_level": 5000, "reorder_qty": 10000, "unit_cost": 0.75, "asset_flag": 0},
    {"item_id": "VENT_UNIT", "item_name": "Ventilator Unit", "unit": "unit", "reorder_level": 1, "reorder_qty": 1, "unit_cost": 250000.0, "asset_flag": 1},
])

# --- Generate SQL ---
sql_lines = []

# Hospitals
sql_lines.append("-- Pune hospitals metadata (50 hospitals)")
sql_lines.append("""
CREATE TABLE IF NOT EXISTS hospitals (
  hospital_id VARCHAR(50) PRIMARY KEY,
  hospital_name VARCHAR(100),
  region VARCHAR(50),
  latitude DECIMAL(9,6),
  longitude DECIMAL(9,6),
  ownership_type VARCHAR(20),
  max_capacity_beds INT,
  ward_capacity_beds INT
);
""")
for _, r in hospitals_df.iterrows():
    sql_lines.append(f"INSERT INTO hospitals VALUES ('{r.hospital_id}','{r.hospital_name}','{r.region}',{r.latitude},{r.longitude},'{r.ownership_type}',{r.max_capacity_beds},{r.ward_capacity_beds});")

# hospital_resource_timeseries
sql_lines.append("""
CREATE TABLE IF NOT EXISTS hospital_resource_timeseries (
  timestamp DATETIME,
  hospital_id VARCHAR(50),
  occupied_beds INT,
  total_beds INT,
  ed_total_beds INT,
  ed_occupied_beds INT,
  ward_capacity_beds INT,
  total_icu_beds INT,
  icu_occupied_beds INT,
  total_ventilators INT,
  in_use_ventilators INT,
  oxygen_units_liters FLOAT,
  available_oxygen_liters FLOAT,
  estimated_daily_consumption_oxygen_liters FLOAT,
  tb_med_stock_tablets INT,
  diag_kits_available INT,
  available_staff_count INT,
  on_shift_doctors INT,
  required_doctors INT,
  on_shift_nurses INT,
  ambulance_arrivals_24h INT,
  critical_cases_ed INT,
  avg_daily_admissions_7d FLOAT,
  avg_ed_tat_minutes_1h FLOAT,
  avg_ed_tat_minutes_6h FLOAT,
  FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id)
);
""")
for _, r in timeseries_df.iterrows():
    sql_lines.append(
        f"INSERT INTO hospital_resource_timeseries VALUES ('{r.timestamp}','{r.hospital_id}',{r.occupied_beds},{r.total_beds},{r.ed_total_beds},{r.ed_occupied_beds},{r.ward_capacity_beds},{r.total_icu_beds},{r.icu_occupied_beds},{r.total_ventilators},{r.in_use_ventilators},{r.oxygen_units_liters},{r.available_oxygen_liters},{r.estimated_daily_consumption_oxygen_liters},{r.tb_med_stock_tablets},{r.diag_kits_available},{r.available_staff_count},{r.on_shift_doctors},{r.required_doctors},{r.on_shift_nurses},{r.ambulance_arrivals_24h},{r.critical_cases_ed},{r.avg_daily_admissions_7d},{r.avg_ed_tat_minutes_1h},{r.avg_ed_tat_minutes_6h});"
    )

# Finance
sql_lines.append("""
CREATE TABLE IF NOT EXISTS hospital_finance_monthly (
  hospital_id VARCHAR(50),
  year INT,
  month INT,
  period DATE,
  total_expenditure DECIMAL(15,2),
  operational_expenditure DECIMAL(15,2),
  staff_cost DECIMAL(15,2),
  supply_cost DECIMAL(15,2),
  maintenance_cost DECIMAL(15,2),
  transport_cost DECIMAL(15,2),
  capital_expenditure DECIMAL(15,2),
  revenue DECIMAL(15,2),
  budget_allocated DECIMAL(15,2),
  budget_remaining DECIMAL(15,2),
  data_confidence VARCHAR(20),
  last_updated DATETIME,
  PRIMARY KEY (hospital_id, period)
);
""")
for _, r in finance_df.iterrows():
    sql_lines.append(
        f"INSERT INTO hospital_finance_monthly VALUES ('{r.hospital_id}',{r.year},{r.month},'{r.period}',{r.total_expenditure},{r.operational_expenditure},{r.staff_cost},{r.supply_cost},{r.maintenance_cost},{r.transport_cost},{r.capital_expenditure},{r.revenue},{r.budget_allocated},{r.budget_remaining},'{r.data_confidence}','{r.last_updated}');"
    )

# Suppliers
sql_lines.append("""
CREATE TABLE IF NOT EXISTS suppliers (
  vendor_id VARCHAR(20) PRIMARY KEY,
  vendor_name VARCHAR(100),
  vendor_type VARCHAR(50),
  contact JSON,
  lead_time_days INT,
  payment_terms_days INT
);
""")
for _, r in suppliers_df.iterrows():
    sql_lines.append(f"INSERT INTO suppliers VALUES ('{r.vendor_id}','{r.vendor_name}','{r.vendor_type}','{r.contact}',{r.lead_time_days},{r.payment_terms_days});")

# Inventory
sql_lines.append("""
CREATE TABLE IF NOT EXISTS inventory_items (
  item_id VARCHAR(50) PRIMARY KEY,
  item_name VARCHAR(100),
  unit VARCHAR(20),
  reorder_level DECIMAL(10,2),
  reorder_qty DECIMAL(10,2),
  unit_cost DECIMAL(10,2),
  asset_flag BOOLEAN
);
""")
for _, r in inventory_df.iterrows():
    sql_lines.append(f"INSERT INTO inventory_items VALUES ('{r.item_id}','{r.item_name}','{r.unit}',{r.reorder_level},{r.reorder_qty},{r.unit_cost},{int(r.asset_flag)});")

# --- Write to SQL file ---
out_path = "mock_pune_50_hospitals.sql"
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(sql_lines))

print("✅ MySQL-compatible SQL written to:", out_path)
print("Rows generated: hospitals =", len(hospitals_df), ", timeseries =", len(timeseries_df), ", finance =", len(finance_df))