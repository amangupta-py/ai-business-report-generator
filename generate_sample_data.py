"""
Generates realistic sample e-commerce data for testing the report generator.
Run this once to create sales_data.csv with 30 days of fake but realistic data.
"""

import csv
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
random.seed(42)  # Same data every run, easier debugging
Faker.seed(42)

# Configuration
NUM_DAYS = 30
ORDERS_PER_DAY_RANGE = (40, 120)
PRODUCTS = [
    ("SKU001", "Wireless Earbuds", 1499),
    ("SKU002", "Phone Case", 399),
    ("SKU003", "Laptop Stand", 1899),
    ("SKU004", "USB-C Cable", 299),
    ("SKU005", "Smart Watch", 4999),
    ("SKU006", "Power Bank", 1299),
    ("SKU007", "Bluetooth Speaker", 2499),
    ("SKU008", "Screen Protector", 199),
]
CHANNELS = ["Website", "Mobile App", "Amazon", "Flipkart"]
CITIES = ["Delhi", "Mumbai", "Bangalore", "Hyderabad", "Pune", "Chennai", "Kolkata"]

# Generate data
end_date = datetime.now().date()
start_date = end_date - timedelta(days=NUM_DAYS - 1)

rows = []
order_id = 10001

for day_offset in range(NUM_DAYS):
    current_date = start_date + timedelta(days=day_offset)
    num_orders = random.randint(*ORDERS_PER_DAY_RANGE)

    # Weekend boost (realistic e-commerce pattern)
    if current_date.weekday() >= 5:
        num_orders = int(num_orders * 1.3)

    for _ in range(num_orders):
        sku, name, price = random.choice(PRODUCTS)
        quantity = random.choices([1, 2, 3, 4], weights=[0.7, 0.2, 0.07, 0.03])[0]
        revenue = price * quantity

        rows.append({
            "order_id": f"ORD{order_id}",
            "date": current_date.isoformat(),
            "sku": sku,
            "product_name": name,
            "quantity": quantity,
            "unit_price": price,
            "revenue": revenue,
            "channel": random.choice(CHANNELS),
            "city": random.choice(CITIES),
            "customer_email": fake.email(),
        })
        order_id += 1

# Write to CSV
with open("sales_data.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"✓ Generated {len(rows)} orders across {NUM_DAYS} days")
print(f"✓ File saved: sales_data.csv")
print(f"✓ Date range: {start_date} to {end_date}")