import os
import time
import random
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
from typing import List, Dict

# Konstanten für Status
PO_STATUS = ['DRAFT', 'SUBMITTED', 'APPROVED', 'REJECTED', 'COMPLETED']
APPROVAL_STATUS = ['PENDING', 'APPROVED', 'REJECTED']
GR_STATUS = ['COMPLETE', 'PARTIAL', 'DAMAGED', 'REJECTED']
GR_QUALITY_STATUS = ['GOOD', 'DAMAGED', 'REJECTED']
INVOICE_STATUS = ['RECEIVED', 'IN_REVIEW', 'APPROVED', 'PAID', 'DISPUTED']
PAYMENT_STATUS = ['SCHEDULED', 'PROCESSED', 'FAILED']
PAYMENT_METHODS = ['BANK_TRANSFER', 'CHECK', 'CREDIT_CARD']

# Testdaten
COMPANY_NAMES = ["Technik GmbH", "Logistik AG", "Handel UG", "Industry AG", "Supply GmbH", "Parts Co.", "Tools GmbH"]
COMPANY_SUFFIXES = ["GmbH", "AG", "UG", "KG", "OHG", "Limited", "Co. KG"]
DOMAINS = ["example.com", "company.de", "business.com", "corp.de", "enterprise.com"]
FIRST_NAMES = ["Peter", "Michael", "Thomas", "Klaus", "Stefan", "Andreas", "Martin", "Julia", "Anna", "Maria", "Sandra"]
LAST_NAMES = ["Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker", "Schulz", "Hoffmann"]
DEPARTMENTS = ["Einkauf", "Logistik", "Management", "Finanzen", "Operations"]
MATERIAL_PREFIXES = ["Standard", "Premium", "Basic", "Pro", "Industrial"]
MATERIAL_TYPES = ["Schraube", "Mutter", "Blech", "Rohr", "Kabel", "Stecker", "Gehäuse", "Platine", "Motor", "Sensor"]
CATEGORIES = ["Rohstoffe", "Büromaterial", "Elektronik", "Werkzeuge", "Verbrauchsmaterial"]
UNITS = ["Stück", "Karton", "Palette", "Meter", "Kilogramm", "Liter"]

def get_database_connection():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        database=os.getenv('MYSQL_DATABASE'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD')
    )

def generate_random_date(start_year: int = 2022) -> datetime:
    """Generiert ein zufälliges Datum zwischen start_year und heute"""
    start = datetime(start_year, 1, 1)
    end = datetime.now()
    days_between = (end - start).days
    random_days = random.randint(0, days_between)
    return start + timedelta(days=random_days)

def generate_random_name() -> tuple:
    """Generiert einen zufälligen Namen"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    return first_name, last_name

def generate_random_email(first_name: str, last_name: str) -> str:
    """Generiert eine zufällige E-Mail-Adresse"""
    domain = random.choice(DOMAINS)
    return f"{first_name.lower()}.{last_name.lower()}@{domain}"

def generate_random_company() -> str:
    """Generiert einen zufälligen Firmennamen"""
    return f"{random.choice(COMPANY_NAMES)} {random.choice(COMPANY_SUFFIXES)}"

def generate_suppliers(conn, count: int) -> List[int]:
    supplier_ids = []
    cursor = conn.cursor()
    insert_query = """
    INSERT INTO supplier (name, contact_person, email, created_at)
    VALUES (%s, %s, %s, %s)
    """
    
    for _ in range(count):
        company = generate_random_company()
        first_name, last_name = generate_random_name()
        contact_person = f"{first_name} {last_name}"
        email = generate_random_email(first_name, last_name)
        created_at = generate_random_date()
        
        cursor.execute(insert_query, (company, contact_person, email, created_at))
        supplier_ids.append(cursor.lastrowid)
    
    conn.commit()
    return supplier_ids

def generate_materials(conn, count: int) -> List[int]:
    material_ids = []
    cursor = conn.cursor()
    insert_query = """
    INSERT INTO material (name, description, unit, category, created_at)
    VALUES (%s, %s, %s, %s, %s)
    """
    
    for _ in range(count):
        prefix = random.choice(MATERIAL_PREFIXES)
        type_ = random.choice(MATERIAL_TYPES)
        name = f"{prefix} {type_}"
        description = f"Standardausführung {type_}"
        unit = random.choice(UNITS)
        category = random.choice(CATEGORIES)
        created_at = generate_random_date()
        
        cursor.execute(insert_query, (name, description, unit, category, created_at))
        material_ids.append(cursor.lastrowid)
    
    conn.commit()
    return material_ids

def generate_employees(conn, count: int) -> Dict[str, List[int]]:
    employee_ids = {'purchaser': [], 'approver': [], 'receiver': []}
    
    departments = {
        'purchaser': 'Einkauf',
        'approver': 'Management',
        'receiver': 'Logistik'
    }
    
    cursor = conn.cursor()
    insert_query = """
    INSERT INTO employee (name, department, role, created_at)
    VALUES (%s, %s, %s, %s)
    """
    
    for role, dept in departments.items():
        for _ in range(count // 3):
            first_name, last_name = generate_random_name()
            name = f"{first_name} {last_name}"
            created_at = generate_random_date()
            
            cursor.execute(insert_query, (name, dept, role, created_at))
            employee_ids[role].append(cursor.lastrowid)
    
    conn.commit()
    return employee_ids

def generate_purchase_orders(conn, params: Dict) -> List[Dict]:
    orders = []
    start_date = datetime(2022, 1, 1)
    end_date = datetime.now()
    total_days = (end_date - start_date).days
    
    orders_per_day = 50000 / 365
    target_count = int((total_days * orders_per_day) + 0.5)
    
    cursor = conn.cursor()
    insert_query = """
    INSERT INTO purchase_order (supplier_id, employee_id, total_amount, currency, status, created_at)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    for _ in range(target_count):
        supplier_id = random.choice(params['supplier_ids'])
        employee_id = random.choice(params['employee_ids']['purchaser'])
        created_at = generate_random_date()
        
        order = {
            'supplier_id': supplier_id,
            'employee_id': employee_id,
            'created_at': created_at,
            'currency': 'EUR',
            'status': random.choice(['COMPLETED'] * 8 + ['REJECTED'] * 1 + ['IN_PROGRESS'] * 1),
            'items': random.randint(1, 5)
        }
        
        cursor.execute(insert_query, (
            order['supplier_id'],
            order['employee_id'],
            0,
            order['currency'],
            order['status'],
            order['created_at']
        ))
        
        order['id'] = cursor.lastrowid
        orders.append(order)
    
    conn.commit()
    return orders

def generate_order_items(conn, orders: List[Dict], material_ids: List[int]) -> Dict[int, List[Dict]]:
    items_by_order = {}
    
    cursor = conn.cursor()
    insert_query = """
    INSERT INTO order_item (po_id, material_id, quantity, price_per_unit)
    VALUES (%s, %s, %s, %s)
    """
    
    for order in orders:
        items = []
        total_amount = 0
        
        for _ in range(order['items']):
            material_id = random.choice(material_ids)
            quantity = random.randint(1, 100)
            price = round(random.uniform(10, 1000), 2)
            
            cursor.execute(insert_query, (
                order['id'],
                material_id,
                quantity,
                price
            ))
            
            item = {
                'id': cursor.lastrowid,
                'material_id': material_id,
                'quantity': quantity,
                'price': price
            }
            items.append(item)
            total_amount += quantity * price
        
        cursor.execute(
            "UPDATE purchase_order SET total_amount = %s WHERE po_id = %s",
            (total_amount, order['id'])
        )
        
        items_by_order[order['id']] = items
    
    conn.commit()
    return items_by_order

def generate_approvals(conn, orders: List[Dict], approver_ids: List[int]):
    cursor = conn.cursor()
    insert_query = """
    INSERT INTO approval_process (po_id, approver_id, approval_level, decision, comment, created_at)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    for order in orders:
        if order['status'] != 'DRAFT':
            levels = random.randint(1, 2)
            
            for level in range(1, levels + 1):
                approver_id = random.choice(approver_ids)
                decision = 'APPROVED' if order['status'] == 'COMPLETED' else 'REJECTED'
                comment = "Genehmigt" if decision == 'APPROVED' else "Abgelehnt aufgrund von Budgetüberschreitung"
                created_at = order['created_at'] + timedelta(hours=random.randint(1, 48))
                
                cursor.execute(insert_query, (
                    order['id'],
                    approver_id,
                    level,
                    decision,
                    comment,
                    created_at
                ))
    
    conn.commit()

def generate_goods_receipts(conn, orders: List[Dict], items_by_order: Dict, receiver_ids: List[int]):
    cursor = conn.cursor()
    insert_query = """
    INSERT INTO goods_receipt (po_id, order_item_id, receiver_id, delivery_note_number,
                             quantity_received, receipt_date, status, quality_status,
                             batch_number, comment, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    for order in orders:
        if order['status'] == 'COMPLETED':
            items = items_by_order[order['id']]
            receipt_date = order['created_at'] + timedelta(days=random.randint(2, 14))
            
            for item in items:
                deliveries = random.choices([1, 2], weights=[80, 20])[0]
                remaining_quantity = item['quantity']
                
                for delivery in range(deliveries):
                    if deliveries == 1:
                        quantity = remaining_quantity
                        status = 'COMPLETE'
                    else:
                        if delivery == 0:
                            quantity = int(remaining_quantity * random.uniform(0.4, 0.6))
                            status = 'PARTIAL'
                        else:
                            quantity = remaining_quantity
                            status = 'COMPLETE'
                            receipt_date += timedelta(days=random.randint(1, 7))
                    
                    remaining_quantity -= quantity
                    
                    quality_status = random.choices(
                        GR_QUALITY_STATUS,
                        weights=[92, 5, 3]
                    )[0]
                    
                    cursor.execute(insert_query, (
                        order['id'],
                        item['id'],
                        random.choice(receiver_ids),
                        f"DN-{random.randint(10000000, 99999999)}",
                        quantity,
                        receipt_date,
                        status,
                        quality_status,
                        f"BATCH-{random.randint(100000, 999999)}",
                        "Wareneingangskontrolle bestanden" if quality_status == 'GOOD' else "Qualitätsmängel festgestellt",
                        receipt_date
                    ))
    
    conn.commit()

def generate_invoices_and_payments(conn, orders: List[Dict], items_by_order: Dict):
    cursor = conn.cursor()
    invoice_query = """
    INSERT INTO invoice (po_id, order_item_id, invoice_number, invoice_date,
                        due_date, quantity, price_per_unit, tax_rate, currency,
                        status, payment_terms, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    payment_query = """
    INSERT INTO payment (invoice_id, payment_date, amount, payment_method,
                        reference_number, status, created_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    for order in orders:
        if order['status'] == 'COMPLETED':
            items = items_by_order[order['id']]
            invoice_date = order['created_at'] + timedelta(days=random.randint(5, 20))
            due_date = invoice_date + timedelta(days=30)
            
            for item in items:
                cursor.execute(invoice_query, (
                    order['id'],
                    item['id'],
                    f"INV-{random.randint(10000000, 99999999)}",
                    invoice_date,
                    due_date,
                    item['quantity'],
                    item['price'],
                    19.0,
                    'EUR',
                    'PAID',
                    'Net 30',
                    invoice_date
                ))
                
                invoice_id = cursor.lastrowid
                payment_date = due_date - timedelta(days=random.randint(0, 5))
                amount = item['quantity'] * item['price'] * 1.19
                
                cursor.execute(payment_query, (
                    invoice_id,
                    payment_date,
                    amount,
                    random.choice(PAYMENT_METHODS),
                    f"PAY-{random.randint(1000000000, 9999999999)}",
                    'PROCESSED',
                    payment_date
                ))
    
    conn.commit()

def main():
    print("Starting data generator...")
    start_time = time.time()
    
    try:
        conn = get_database_connection()
        
        print("Generating master data...")
        print("- Suppliers...")
        supplier_ids = generate_suppliers(conn, 100)  # 100 Lieferanten
        
        print("- Materials...")
        material_ids = generate_materials(conn, 500)  # 500 Materialien
        
        print("- Employees...")
        employee_ids = generate_employees(conn, 90)   # 30 je Rolle
        
        print("\nGenerating purchase orders...")
        orders = generate_purchase_orders(conn, {
            'supplier_ids': supplier_ids,
            'employee_ids': employee_ids
        })
        print(f"Generated {len(orders)} purchase orders")
        
        print("\nGenerating order items...")
        items_by_order = generate_order_items(conn, orders, material_ids)
        total_items = sum(len(items) for items in items_by_order.values())
        print(f"Generated {total_items} order items")
        
        print("\nGenerating approval processes...")
        generate_approvals(conn, orders, employee_ids['approver'])
        
        print("\nGenerating goods receipts...")
        generate_goods_receipts(conn, orders, items_by_order, employee_ids['receiver'])
        
        print("\nGenerating invoices and payments...")
        generate_invoices_and_payments(conn, orders, items_by_order)
        
        duration = time.time() - start_time
        print(f"\nData generation completed in {duration:.2f} seconds!")
        
        # Statistiken ausgeben
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM purchase_order")
        po_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM order_item")
        item_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM goods_receipt")
        gr_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM invoice")
        inv_count = cursor.fetchone()[0]
        
        print("\nGenerated Records:")
        print(f"Purchase Orders: {po_count}")
        print(f"Order Items: {item_count}")
        print(f"Goods Receipts: {gr_count}")
        print(f"Invoices: {inv_count}")
        
    except Error as e:
        print(f"Error: {e}")
    finally:
        if conn.is_connected():
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    main()