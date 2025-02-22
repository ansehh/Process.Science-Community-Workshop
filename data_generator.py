import os
import random
from datetime import datetime, timedelta
from collections import defaultdict

# Output configuration
OUTPUT_FILE = "init/002_data.sql"

# Volume configuration
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

# Status enums and constants
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

class TimeseriesGenerator:
    def __init__(self, start_date=datetime(2022, 1, 1), end_date=datetime(2024, 12, 31)):
        self.start_date = start_date
        self.end_date = end_date
        self.current_date = start_date
        self.business_hours = [(9, 17)]  # 9 AM to 5 PM
        
    def generate_business_datetime(self):
        """Generate a datetime during business hours."""
        random_days = random.randint(0, (self.end_date - self.start_date).days)
        date = self.start_date + timedelta(days=random_days)
        
        # Ensure it's a weekday
        while date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            date += timedelta(days=1)
        
        start_hour, end_hour = self.business_hours[0]
        hour = random.randint(start_hour, end_hour - 1)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        
        return datetime(date.year, date.month, date.day, hour, minute, second)

    def generate_sequential_datetime(self, min_days=1, max_days=5):
        """Generate a datetime that's always after the previous one."""
        delta = timedelta(days=random.randint(min_days, max_days))
        self.current_date += delta
        
        # Ensure it's during business hours and a weekday
        while self.current_date.weekday() >= 5:
            self.current_date += timedelta(days=1)
            
        start_hour, end_hour = self.business_hours[0]
        hour = random.randint(start_hour, end_hour - 1)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        
        return datetime(
            self.current_date.year,
            self.current_date.month,
            self.current_date.day,
            hour,
            minute,
            second
        )

def random_price(min_val=5, max_val=1000):
    return round(random.uniform(min_val, max_val), 2)

def write_sql_file():
    os.makedirs("init", exist_ok=True)

    # Initialize time generators
    master_data_gen = TimeseriesGenerator(
        start_date=datetime(2022, 1, 1),
        end_date=datetime(2022, 12, 31)
    )
    
    po_gen = TimeseriesGenerator(
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2024, 12, 31)
    )

    suppliers_data = []
    materials_data = []
    employees_data = []
    employees_by_role = {'purchaser': [], 'approver': [], 'receiver': [], 'accountant': [], 'operations_manager': []}
    purchase_orders_data = []
    order_items_data = []
    approval_data = []
    goods_receipts_data = []
    invoice_data = []
    payment_data = []
    cdpos_data = []
    cdhdr_data = []

    # Generate suppliers
    for i in range(1, NUM_SUPPLIERS + 1):
        company = f"{random.choice(COMPANY_NAMES)} {random.choice(COMPANY_SUFFIXES)}"
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        email = f"{first_name.lower()}.{last_name.lower()}@{random.choice(DOMAINS)}"
        created_at = master_data_gen.generate_business_datetime()
        suppliers_data.append((i, company, f"{first_name} {last_name}", email, created_at))

    # Generate materials
    for i in range(1, NUM_MATERIALS + 1):
        prefix = random.choice(MATERIAL_PREFIXES)
        mat_type = random.choice(MATERIAL_TYPES)
        name = f"{prefix} {mat_type}"
        description = f"Description for {name}"
        category = random.choice(CATEGORIES)
        unit = random.choice(UNITS)
        created_at = master_data_gen.generate_business_datetime()
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
        created_at = master_data_gen.generate_business_datetime()
        employees_data.append((i, f"{first_name} {last_name}", department, role, created_at))
        employees_by_role[role].append(i)

    # Generate Purchase Orders with Order Items
    for po_id in range(1, NUM_PURCHASE_ORDERS + 1):
        supplier_id = random.randint(1, NUM_SUPPLIERS)
        employee_id = random.choice(employees_by_role.get('purchaser', list(range(1, NUM_EMPLOYEES + 1))))
        created_at = po_gen.generate_sequential_datetime(min_days=1, max_days=3)
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

    # Generate approvals with realistic timing
    for po_data in purchase_orders_data:
        po_id = po_data[0]
        po_created_at = po_data[6]
        
        approval_gen = TimeseriesGenerator(
            start_date=po_created_at,
            end_date=po_created_at + timedelta(days=5)
        )
        
        num_approvals = random.randint(1, 3)
        for level in range(1, num_approvals + 1):
            approver_id = random.choice(employees_by_role.get('approver', list(range(1, NUM_EMPLOYEES + 1))))
            decision = random.choice(APPROVAL_STATUS)
            comment = "Genehmigt" if decision == 'APPROVED' else "Abgelehnt aufgrund von Budgetüberschreitung"
            created_at = approval_gen.generate_sequential_datetime(min_days=0, max_days=1)
            approval_data.append((len(approval_data) + 1, po_id, approver_id, level, decision, comment, created_at))

    # Generate goods receipts with realistic timing
    for po_data in purchase_orders_data:
        if po_data[5] == 'APPROVED':
            po_id = po_data[0]
            po_created_at = po_data[6]
            
            gr_gen = TimeseriesGenerator(
                start_date=po_created_at + timedelta(days=2),
                end_date=po_created_at + timedelta(days=14)
            )
            
            valid_items = [(po, item) for po, item, _, _, _ in order_items_data if po == po_id]
            
            for po_id, item_number in valid_items:
                receiver_id = random.choice(employees_by_role.get('receiver', list(range(1, NUM_EMPLOYEES + 1))))
                delivery_note = f"DN-{random.randint(1000000,9999999)}"
                quantity_received = random.randint(1, 100)
                receipt_date = gr_gen.generate_sequential_datetime(min_days=0, max_days=2)
                status = random.choice(GR_STATUS)
                quality = random.choice(GR_QUALITY_STATUS)
                batch_number = f"BATCH-{random.randint(100000,999999)}"
                comment = "All good" if quality == "GOOD" else "Issue found"
                
                goods_receipts_data.append((
                    len(goods_receipts_data) + 1,
                    po_id, item_number, receiver_id, delivery_note,
                    quantity_received, receipt_date, status, quality,
                    batch_number, comment, receipt_date
                ))

    # Generate invoices with realistic timing
    for po_data in purchase_orders_data:
        if po_data[5] in ['APPROVED', 'COMPLETED']:
            po_id = po_data[0]
            po_created_at = po_data[6]
            po_currency = po_data[4]
            
            # Find the last goods receipt date for this PO
            related_receipts = [gr for gr in goods_receipts_data if gr[1] == po_id]
            if related_receipts:
                last_gr_date = max(gr[6] for gr in related_receipts)
            else:
                last_gr_date = po_created_at + timedelta(days=7)
            
            invoice_gen = TimeseriesGenerator(
                start_date=last_gr_date + timedelta(days=1),
                end_date=last_gr_date + timedelta(days=7)
            )
            
            # Calculate total amount from order items
            po_items = [(po, item, qty, price) for po, item, _, qty, price in order_items_data if po == po_id]
            total_amount = sum(qty * price for _, _, qty, price in po_items)
            
            invoice_date = invoice_gen.generate_sequential_datetime()
            due_date = invoice_date + timedelta(days=30)
            invoice_number = f"INV-{random.randint(1000000,9999999)}"
            tax_rate = 19.0
            status = random.choice(INVOICE_STATUS)
            payment_terms = "Net 30"
            
            invoice_data.append((
                len(invoice_data) + 1,
                po_id, invoice_number, invoice_date, due_date,
                total_amount, tax_rate, po_currency, status,
                payment_terms, invoice_date
            ))

    # Generate payments with realistic timing
    for invoice in invoice_data:
        invoice_id = invoice[0]
        invoice_date = invoice[3]
        due_date = invoice[4]
        
        payment_gen = TimeseriesGenerator(
            start_date=invoice_date,
            end_date=due_date
        )
        
        payment_date = payment_gen.generate_sequential_datetime()
        amount = invoice[5]  # Use invoice amount
        payment_method = random.choice(PAYMENT_METHODS)
        reference_number = f"PAY-{random.randint(100000000,999999999)}"
        status = random.choice(PAYMENT_STATUS)
        
        payment_data.append((
            len(payment_data) + 1,
            invoice_id, payment_date, amount, payment_method,
            reference_number, status, payment_date
        ))

    # Generate change documents
    for po_data in purchase_orders_data:
        po_id = po_data[0]
        
        # Generate changes for order items (30% chance)
                # Generate changes for order items (30% chance)
        related_items = [item for item in order_items_data if item[0] == po_id]
        
        for item in related_items:
            if random.random() < 0.3:
                item_number = item[1]
                material_id = item[2]
                quantity = item[3]
                price_per_unit = item[4]
                
                employee_id = random.randint(1, NUM_EMPLOYEES)
                timestamp = po_data[6] + timedelta(days=random.randint(1, 5))
                
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
                    
                cdpos_data.append((
                    len(cdpos_data) + 1,
                    po_id, item_number, changed_field, old_value, new_value, 
                    timestamp, employee_id
                ))
        
        # Generate changes for purchase order header (20% chance)
        if random.random() < 0.2:
            employee_id = random.randint(1, NUM_EMPLOYEES)
            timestamp = po_data[6] + timedelta(days=random.randint(1, 3))
            
            changed_field = random.choice(CDHDR_FIELDS)
            if changed_field == "Currency":
                old_value = po_data[4]  # currency
                new_value = "USD" if old_value == "EUR" else "EUR"
            else:  # Supplier
                old_value = str(po_data[1])  # supplier_id
                new_value = str(random.randint(1, NUM_SUPPLIERS))
                
            cdhdr_data.append((
                len(cdhdr_data) + 1,
                po_id, changed_field, old_value, new_value, timestamp, employee_id
            ))

    # Write all data to SQL file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        # Write supplier data
        f.write("-- Supplier Data\n")
        f.write("INSERT INTO supplier (supplier_id, name, contact_person, email, created_at) VALUES\n")
        f.write(",\n".join([
            f"({s[0]}, '{s[1]}', '{s[2]}', '{s[3]}', '{s[4].strftime('%Y-%m-%d %H:%M:%S')}')" 
            for s in suppliers_data
        ]) + ";\n\n")

        # Write material data
        f.write("-- Material Data\n")
        f.write("INSERT INTO material (material_id, name, description, unit, category, created_at) VALUES\n")
        f.write(",\n".join([
            f"({m[0]}, '{m[1]}', '{m[2]}', '{m[3]}', '{m[4]}', '{m[5].strftime('%Y-%m-%d %H:%M:%S')}')" 
            for m in materials_data
        ]) + ";\n\n")

        # Write employee data
        f.write("-- Employee Data\n")
        f.write("INSERT INTO employee (employee_id, name, department, role, created_at) VALUES\n")
        f.write(",\n".join([
            f"({e[0]}, '{e[1]}', '{e[2]}', '{e[3]}', '{e[4].strftime('%Y-%m-%d %H:%M:%S')}')" 
            for e in employees_data
        ]) + ";\n\n")

        # Write purchase order data
        f.write("-- Purchase Order Data\n")
        f.write("INSERT INTO purchase_order (po_id, supplier_id, employee_id, total_amount, currency, status, created_at) VALUES\n")
        f.write(",\n".join([
            f"({p[0]}, {p[1]}, {p[2]}, {p[3]}, '{p[4]}', '{p[5]}', '{p[6].strftime('%Y-%m-%d %H:%M:%S')}')" 
            for p in purchase_orders_data
        ]) + ";\n\n")

        # Write order item data
        f.write("-- Order Item Data\n")
        f.write("INSERT INTO order_item (po_id, item_number, material_id, quantity, price_per_unit) VALUES\n")
        f.write(",\n".join([
            f"({o[0]}, {o[1]}, {o[2]}, {o[3]}, {o[4]})" 
            for o in order_items_data
        ]) + ";\n\n")

        # Write approval process data
        f.write("-- Approval Process Data\n")
        f.write("INSERT INTO approval_process (approval_id, po_id, approver_id, approval_level, decision, comment, created_at) VALUES\n")
        f.write(",\n".join([
            f"({a[0]}, {a[1]}, {a[2]}, {a[3]}, '{a[4]}', '{a[5]}', '{a[6].strftime('%Y-%m-%d %H:%M:%S')}')" 
            for a in approval_data
        ]) + ";\n\n")

        # Write goods receipt data
        f.write("-- Goods Receipt Data\n")
        f.write("INSERT INTO goods_receipt (receipt_id, po_id, po_item_number, receiver_id, delivery_note_number, " +
                "quantity_received, receipt_date, status, quality_status, batch_number, comment, created_at) VALUES\n")
        f.write(",\n".join([
            f"({g[0]}, {g[1]}, {g[2]}, {g[3]}, '{g[4]}', {g[5]}, '{g[6].strftime('%Y-%m-%d %H:%M:%S')}', " +
            f"'{g[7]}', '{g[8]}', '{g[9]}', '{g[10]}', '{g[11].strftime('%Y-%m-%d %H:%M:%S')}')"
            for g in goods_receipts_data
        ]) + ";\n\n")

        # Write invoice data
        f.write("-- Invoice Data\n")
        f.write("INSERT INTO invoice (invoice_id, po_id, invoice_number, invoice_date, due_date, " +
                "total_amount, tax_rate, currency, status, payment_terms, created_at) VALUES\n")
        f.write(",\n".join([
            f"({i[0]}, {i[1]}, '{i[2]}', '{i[3].strftime('%Y-%m-%d %H:%M:%S')}', " +
            f"'{i[4].strftime('%Y-%m-%d %H:%M:%S')}', {i[5]}, {i[6]}, '{i[7]}', '{i[8]}', '{i[9]}', " +
            f"'{i[10].strftime('%Y-%m-%d %H:%M:%S')}')"
            for i in invoice_data
        ]) + ";\n\n")

        # Write payment data
        f.write("-- Payment Data\n")
        f.write("INSERT INTO payment (payment_id, invoice_id, payment_date, amount, payment_method, " +
                "reference_number, status, created_at) VALUES\n")
        f.write(",\n".join([
            f"({p[0]}, {p[1]}, '{p[2].strftime('%Y-%m-%d %H:%M:%S')}', {p[3]}, '{p[4]}', '{p[5]}', " +
            f"'{p[6]}', '{p[7].strftime('%Y-%m-%d %H:%M:%S')}')"
            for p in payment_data
        ]) + ";\n\n")

        # Write change document data
        if cdpos_data:
            f.write("-- Change Document Position Data\n")
            f.write("INSERT INTO cdpos (change_id, po_id, po_item_number, changed_field, old_value, new_value, " +
                    "timestamp, employee_id) VALUES\n")
            f.write(",\n".join([
                f"({c[0]}, {c[1]}, {c[2]}, '{c[3]}', '{c[4]}', '{c[5]}', '{c[6].strftime('%Y-%m-%d %H:%M:%S')}', {c[7]})"
                for c in cdpos_data
            ]) + ";\n\n")

        if cdhdr_data:
            f.write("-- Change Document Header Data\n")
            f.write("INSERT INTO cdhdr (change_id, po_id, changed_field, old_value, new_value, timestamp, employee_id) VALUES\n")
            f.write(",\n".join([
                f"({c[0]}, {c[1]}, '{c[2]}', '{c[3]}', '{c[4]}', '{c[5].strftime('%Y-%m-%d %H:%M:%S')}', {c[6]})"
                for c in cdhdr_data
            ]) + ";\n\n")

if __name__ == "__main__":
    write_sql_file()