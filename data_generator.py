import os
import random
from datetime import datetime, timedelta
from collections import defaultdict

OUTPUT_FILE = "init/002_data.sql"

NUM_SUPPLIERS = 100
NUM_MATERIALS = 200
NUM_EMPLOYEES = 90
NUM_PURCHASE_ORDERS = 1000
ITEMS_PER_PO_MIN = 1
ITEMS_PER_PO_MAX = 5
NUM_APPROVALS = 500
NUM_GOODS_RECEIPTS = 500
NUM_INVOICES = 500
NUM_PAYMENTS = 500

# Constants
PO_STATUS = ['DRAFT', 'SUBMITTED', 'APPROVED', 'REJECTED', 'COMPLETED']
APPROVAL_STATUS = ['PENDING', 'APPROVED', 'REJECTED']
GR_STATUS = ['COMPLETE', 'PARTIAL', 'DAMAGED', 'REJECTED']
GR_QUALITY_STATUS = ['GOOD', 'DAMAGED', 'REJECTED']
INVOICE_STATUS = ['RECEIVED', 'IN_REVIEW', 'APPROVED', 'PAID', 'DISPUTED']
PAYMENT_STATUS = ['SCHEDULED', 'PROCESSED', 'FAILED']
PAYMENT_METHODS = ['BANK_TRANSFER', 'CHECK', 'CREDIT_CARD']

# Test data arrays
COMPANY_NAMES = ["Technik GmbH", "Logistik AG", "Handel UG", "Industry AG", "Supply GmbH", "Parts Co.", "Tools GmbH"]
COMPANY_SUFFIXES = ["GmbH", "AG", "UG", "KG", "OHG", "Limited", "Co. KG"]
DOMAINS = ["example.com", "company.de", "business.com", "corp.de", "enterprise.com"]
FIRST_NAMES = ["Peter", "Michael", "Thomas", "Klaus", "Stefan", "Andreas", "Martin", "Julia", "Anna", "Maria", "Sandra"]
LAST_NAMES = ["Mueller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker", "Schulz", "Hoffmann"]
DEPARTMENTS = ["Einkauf", "Logistik", "Management", "Finanzen", "Operations"]
MATERIAL_PREFIXES = ["Standard", "Premium", "Basic", "Pro", "Industrial"]
MATERIAL_TYPES = ["Schraube", "Mutter", "Blech", "Rohr", "Kabel", "Stecker", "Gehaeuse", "Platine", "Motor", "Sensor"]
CATEGORIES = ["Rohstoffe", "Bueromaterial", "Elektronik", "Werkzeuge", "Verbrauchsmaterial"]
UNITS = ["Stueck", "Karton", "Palette", "Meter", "Kilogramm", "Liter"]
CURRENCIES = ["EUR", "USD"]
CDPOS_FIELDS = ['Material', 'Quantity', 'Price']
CDHDR_FIELDS = ['Currency', 'Supplier']

def generate_random_date(start_year=2022):
    start = datetime(start_year, 1, 1)
    end = datetime.now()
    random_date = start + timedelta(days=random.randint(0, (end - start).days))
    random_time = timedelta(
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )
    return (random_date + random_time).strftime("%Y-%m-%d %H:%M:%S")

def random_price(min_val=5, max_val=1000):
    return round(random.uniform(min_val, max_val), 2)

def write_sql_file():
    os.makedirs("init", exist_ok=True)

    suppliers_data= []
    materials_data = []
    employees_data = []
    employees_by_role = {'purchaser': [], 'approver': [], 'receiver': [], 'accountant': [], 'operations_manager': []}
    purchase_orders_data = []
    order_items_data = []
    approval_data = []
    goods_receipts_data = []
    invoice_data = []
    payment_data = []

    # Generate suppliers
    for i in range(1, NUM_SUPPLIERS + 1):
        company = f"{COMPANY_NAMES[i % len(COMPANY_NAMES)]} {COMPANY_SUFFIXES[i % len(COMPANY_SUFFIXES)]}"
        first_name = FIRST_NAMES[i % len(FIRST_NAMES)]
        last_name = LAST_NAMES[i % len(LAST_NAMES)]
        email = f"{first_name.lower()}.{last_name.lower()}@{DOMAINS[i % len(DOMAINS)]}"
        created_at = generate_random_date()
        suppliers_data.append((i, company, f"{first_name} {last_name}", email, created_at))

    # Generate materials
    for i in range(1, NUM_MATERIALS + 1):
        prefix = random.choice(MATERIAL_PREFIXES)
        mat_type = random.choice(MATERIAL_TYPES)
        name = f"{prefix} {mat_type}"
        description = f"Description for {name}"
        category = random.choice(CATEGORIES)
        unit = random.choice(UNITS)
        created_at = generate_random_date()
        materials_data.append((i, name, description, unit, category, created_at))

    # Generate employees
    for i in range(1, NUM_EMPLOYEES + 1):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        department = random.choice(DEPARTMENTS)
        if department == "Einkauf":
            role = "purchaser"
        elif department == "Management":
            role = "approver"
        elif department == "Logistik":
            role = "receiver"
        elif department == "Finanzen":
            role = "accountant"
        else:
            role = "operations_manager"
        created_at = generate_random_date()
        employees_data.append((i, f"{first_name} {last_name}", department, role, created_at))
        employees_by_role[role].append(i)

    # Generate Purchase Orders with Order Items using composite key
    for po_id in range(1, NUM_PURCHASE_ORDERS + 1):
        supplier_id = random.randint(1, NUM_SUPPLIERS)
        employee_id = random.choice(employees_by_role.get('purchaser', list(range(1, NUM_EMPLOYEES + 1))))
        created_at = generate_random_date()
        status = random.choice(PO_STATUS)
        currency = random.choice(CURRENCIES)

        # Generate items for this PO
        num_items = random.randint(ITEMS_PER_PO_MIN, ITEMS_PER_PO_MAX)
        total_amount = 0

        for item_number in range(1, num_items + 1):
            material_id = random.randint(1, NUM_MATERIALS)
            quantity = random.randint(1, 100)
            price_per_unit = random_price(10, 1000)
            total_amount += quantity * price_per_unit
            order_items_data.append((po_id, item_number, material_id, quantity, price_per_unit))

        purchase_orders_data.append((po_id, supplier_id, employee_id, total_amount, currency, status, created_at))

    # Generate approvals
    for i in range(1, NUM_APPROVALS + 1):
        po_id = random.randint(1, NUM_PURCHASE_ORDERS)
        approver_id = random.choice(employees_by_role.get('approver', list(range(1, NUM_EMPLOYEES + 1))))
        approval_level = random.randint(1, 3)
        decision = random.choice(APPROVAL_STATUS)
        comment = "Genehmigt" if decision == 'APPROVED' else "Abgelehnt aufgrund von Budgetüberschreitung"
        created_at = generate_random_date()
        approval_data.append((i, po_id, approver_id, approval_level, decision, comment, created_at))

    # Generate goods receipts with composite key reference
    for i in range(1, NUM_GOODS_RECEIPTS + 1):
        po_id = random.randint(1, NUM_PURCHASE_ORDERS)
        # Find valid item numbers for this PO
        valid_items = [(po, item) for po, item, _, _, _ in order_items_data if po == po_id]
        if valid_items:
            po_id, item_number = random.choice(valid_items)
            receiver_id = random.choice(employees_by_role.get('receiver', list(range(1, NUM_EMPLOYEES + 1))))
            delivery_note = f"DN-{random.randint(1000000,9999999)}"
            quantity_received = random.randint(1, 100)
            receipt_date = generate_random_date()
            status = random.choice(GR_STATUS)
            quality = random.choice(GR_QUALITY_STATUS)
            batch_number = f"BATCH-{random.randint(100000,999999)}"
            comment = "All good" if quality == "GOOD" else "Issue found"
            created_at = receipt_date
            goods_receipts_data.append((i, po_id, item_number, receiver_id, delivery_note,
                                      quantity_received, receipt_date, status, quality,
                                      batch_number, comment, created_at))

    # Generate invoices with composite key reference
    for i in range(1, NUM_INVOICES + 1):
        po_id = random.randint(1, NUM_PURCHASE_ORDERS)
        valid_items = [(po, item) for po, item, _, _, _ in order_items_data if po == po_id]
        if valid_items:
            po_id, item_number = random.choice(valid_items)
            invoice_number = f"INV-{random.randint(1000000,9999999)}"
            invoice_date = generate_random_date()
            due_date = generate_random_date(start_year=2023)
            quantity = random.randint(1, 50)
            price_per_unit = random_price(10, 800)
            tax_rate = 19.0
            currency = random.choice(CURRENCIES)
            status = random.choice(INVOICE_STATUS)
            payment_terms = "Net 30"
            created_at = invoice_date
            invoice_data.append((i, po_id, item_number, invoice_number, invoice_date, due_date,
                               quantity, price_per_unit, tax_rate, currency, status,
                               payment_terms, created_at))

    # Generate payments
    for i in range(1, NUM_PAYMENTS + 1):
        invoice_id = random.randint(1, NUM_INVOICES)
        payment_date = generate_random_date(start_year=2023)
        amount = random_price(50, 5000)
        payment_method = random.choice(PAYMENT_METHODS)
        reference_number = f"PAY-{random.randint(100000000,999999999)}"
        status = random.choice(PAYMENT_STATUS)
        created_at = payment_date
        payment_data.append((i, invoice_id, payment_date, amount, payment_method,
                           reference_number, status, created_at))

    # Generate change data
    cdpos_data = []
    cdhdr_data = []
    
    # Generate changes for order items using composite key
    for po_id, item_number, material_id, quantity, price_per_unit in order_items_data:
        if random.random() < 0.3:  # 30% chance of having changes
            employee_id = random.randint(1, NUM_EMPLOYEES)
            timestamp = generate_random_date()
            
            changed_field = random.choice(CDPOS_FIELDS)
            if changed_field == "Material":
                old_value = str(material_id)
                new_value = str(random.randint(1, NUM_MATERIALS))
            elif changed_field == "Quantity":
                old_value = str(quantity)
                new_value = str(max(1, int(quantity * random.uniform(0.8, 1.2))))
            else:  # Price
                old_value = str(price_per_unit)
                new_value = str(random_price(10, 1000))
                
            cdpos_data.append((po_id, item_number, changed_field, old_value, new_value, timestamp, employee_id))

    # Generate changes for purchase orders
    for po_data in purchase_orders_data:
        po_id, supplier_id, _, _, currency, _, _ = po_data
        if random.random() < 0.2:  # 20% chance of having changes
            employee_id = random.randint(1, NUM_EMPLOYEES)
            timestamp = generate_random_date()
            
            changed_field = random.choice(CDHDR_FIELDS)
            if changed_field == "Currency":
                old_value = currency
                new_value = "USD" if currency == "EUR" else "EUR"
            else:
                old_value = str(supplier_id)
                new_value = str(random.randint(1, NUM_SUPPLIERS))
                
            cdhdr_data.append((po_id, changed_field, old_value, new_value, timestamp, employee_id))

    # Write SQL file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        # Write supplier data
        f.write("INSERT INTO supplier (supplier_id, name, contact_person, email, created_at) VALUES\n")
        f.write(",\n".join([
            f"({s[0]}, '{s[1]}', '{s[2]}', '{s[3]}', '{s[4]}')" for s in suppliers_data
        ]) + ";\n\n")

        # Write material data
        f.write("INSERT INTO material (material_id, name, description, unit, category, created_at) VALUES\n")
        f.write(",\n".join([
            f"({m[0]}, '{m[1]}', '{m[2]}', '{m[3]}', '{m[4]}', '{m[5]}')" for m in materials_data
        ]) + ";\n\n")

        # Write employee data
        f.write("INSERT INTO employee (employee_id, name, department, role, created_at) VALUES\n")
        f.write(",\n".join([
            f"({e[0]}, '{e[1]}', '{e[2]}', '{e[3]}', '{e[4]}')" for e in employees_data
        ]) + ";\n\n")

        # Write purchase order data
        f.write("INSERT INTO purchase_order (po_id, supplier_id, employee_id, total_amount, currency, status, created_at) VALUES\n")
        f.write(",\n".join([
            f"({p[0]}, {p[1]}, {p[2]}, {p[3]}, '{p[4]}', '{p[5]}', '{p[6]}')" for p in purchase_orders_data
        ]) + ";\n\n")

# [Previous code remains the same until the SQL writing part]

        # Write order item data with composite key
        f.write("INSERT INTO order_item (po_id, item_number, material_id, quantity, price_per_unit) VALUES\n")
        f.write(",\n".join([
            f"({o[0]}, {o[1]}, {o[2]}, {o[3]}, {o[4]})" for o in order_items_data
        ]) + ";\n\n")

        # Write approval process data
        f.write("INSERT INTO approval_process (approval_id, po_id, approver_id, approval_level, decision, comment, created_at) VALUES\n")
        f.write(",\n".join([
            f"({a[0]}, {a[1]}, {a[2]}, {a[3]}, '{a[4]}', '{a[5]}', '{a[6]}')" for a in approval_data
        ]) + ";\n\n")

        # Write goods receipt data
        f.write("INSERT INTO goods_receipt (receipt_id, po_id, po_item_number, receiver_id, delivery_note_number, "
                "quantity_received, receipt_date, status, quality_status, batch_number, comment, created_at) VALUES\n")
        f.write(",\n".join([
            f"({g[0]}, {g[1]}, {g[2]}, {g[3]}, '{g[4]}', {g[5]}, '{g[6]}', '{g[7]}', '{g[8]}', '{g[9]}', '{g[10]}', '{g[11]}')" 
            for g in goods_receipts_data
        ]) + ";\n\n")

        # Write invoice data
        f.write("INSERT INTO invoice (invoice_id, po_id, po_item_number, invoice_number, invoice_date, due_date, "
                "quantity, price_per_unit, tax_rate, currency, status, payment_terms, created_at) VALUES\n")
        f.write(",\n".join([
            f"({i[0]}, {i[1]}, {i[2]}, '{i[3]}', '{i[4]}', '{i[5]}', {i[6]}, {i[7]}, {i[8]}, '{i[9]}', '{i[10]}', '{i[11]}', '{i[12]}')" 
            for i in invoice_data
        ]) + ";\n\n")

        # Write payment data
        f.write("INSERT INTO payment (payment_id, invoice_id, payment_date, amount, payment_method, reference_number, "
                "status, created_at) VALUES\n")
        f.write(",\n".join([
            f"({p[0]}, {p[1]}, '{p[2]}', {p[3]}, '{p[4]}', '{p[5]}', '{p[6]}', '{p[7]}')" 
            for p in payment_data
        ]) + ";\n\n")

        # Write CDPOS data with composite key reference
        if cdpos_data:
            f.write("INSERT INTO cdpos (po_id, po_item_number, changed_field, old_value, new_value, timestamp, employee_id) VALUES\n")
            f.write(",\n".join([    
                f"({c[0]}, {c[1]}, '{c[2]}', '{c[3]}', '{c[4]}', '{c[5]}', {c[6]})" for c in cdpos_data
            ]) + ";\n\n")

        # Write CDHDR data
        if cdhdr_data:
            f.write("INSERT INTO cdhdr (po_id, changed_field, old_value, new_value, timestamp, employee_id) VALUES\n")
            f.write(",\n".join([
                f"({c[0]}, '{c[1]}', '{c[2]}', '{c[3]}', '{c[4]}', {c[5]})" for c in cdhdr_data
            ]) + ";\n\n")

if __name__ == "__main__":
    write_sql_file()