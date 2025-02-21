-- ##################
-- # Stammdaten
-- ##################

-- Lieferanten
CREATE TABLE supplier (
    supplier_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    contact_person VARCHAR(100),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Materialien/Artikel
CREATE TABLE material (
    material_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    description TEXT,
    unit VARCHAR(20),
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mitarbeiter
CREATE TABLE employee (
    employee_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    department VARCHAR(50),
    role VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ##################
-- # Bestellprozess
-- ##################

-- Bestellkopf
CREATE TABLE purchase_order (
    po_id INT PRIMARY KEY AUTO_INCREMENT,
    supplier_id INT,
    employee_id INT,
    total_amount DECIMAL(10,2),
    currency VARCHAR(3),
    status ENUM('DRAFT', 'SUBMITTED', 'APPROVED', 'REJECTED', 'COMPLETED'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES supplier(supplier_id),
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
);

-- Bestellpositionen
CREATE TABLE order_item (
    order_item_id INT PRIMARY KEY AUTO_INCREMENT,
    po_id INT,
    material_id INT,
    quantity INT,
    price_per_unit DECIMAL(10,2),
    FOREIGN KEY (po_id) REFERENCES purchase_order(po_id),
    FOREIGN KEY (material_id) REFERENCES material(material_id)
);

-- ##################
-- # Aktivitätstabellen
-- ##################

-- Genehmigungsprozess
CREATE TABLE approval_process (
    approval_id INT PRIMARY KEY AUTO_INCREMENT,
    po_id INT,
    approver_id INT,
    approval_level INT,
    decision ENUM('PENDING', 'APPROVED', 'REJECTED'),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (po_id) REFERENCES purchase_order(po_id),
    FOREIGN KEY (approver_id) REFERENCES employee(employee_id)
);

-- Wareneingang (vereinfacht)
CREATE TABLE goods_receipt (
    receipt_id INT PRIMARY KEY AUTO_INCREMENT,
    po_id INT,
    order_item_id INT,
    receiver_id INT,
    delivery_note_number VARCHAR(50),
    quantity_received INT,
    receipt_date TIMESTAMP,
    status ENUM('COMPLETE', 'PARTIAL', 'DAMAGED', 'REJECTED'),
    quality_status ENUM('GOOD', 'DAMAGED', 'REJECTED'),
    batch_number VARCHAR(50),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (po_id) REFERENCES purchase_order(po_id),
    FOREIGN KEY (order_item_id) REFERENCES order_item(order_item_id),
    FOREIGN KEY (receiver_id) REFERENCES employee(employee_id)
);

-- Rechnung (vereinfacht)
CREATE TABLE invoice (
    invoice_id INT PRIMARY KEY AUTO_INCREMENT,
    po_id INT,
    order_item_id INT,
    invoice_number VARCHAR(50),
    invoice_date DATE,
    due_date DATE,
    quantity INT,
    price_per_unit DECIMAL(10,2),
    tax_rate DECIMAL(5,2),
    currency VARCHAR(3),
    status ENUM('RECEIVED', 'IN_REVIEW', 'APPROVED', 'PAID', 'DISPUTED'),
    payment_terms VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (po_id) REFERENCES purchase_order(po_id),
    FOREIGN KEY (order_item_id) REFERENCES order_item(order_item_id)
);

-- Zahlungen
CREATE TABLE payment (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    invoice_id INT,
    payment_date DATE,
    amount DECIMAL(10,2),
    payment_method ENUM('BANK_TRANSFER', 'CHECK', 'CREDIT_CARD'),
    reference_number VARCHAR(100),
    status ENUM('SCHEDULED', 'PROCESSED', 'FAILED'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (invoice_id) REFERENCES invoice(invoice_id)
);

CREATE TABLE cdpos (
    change_id INT PRIMARY KEY AUTO_INCREMENT, 
    po_item_id INT, 
    changed_field VARCHAR(100),  
    old_value VARCHAR(255),  
    new_value VARCHAR(255), 
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    employee_id INT,  
    FOREIGN KEY (po_item_id) REFERENCES order_item(order_item_id), 
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id)  
);

CREATE TABLE cdhdr (
    change_id INT PRIMARY KEY AUTO_INCREMENT,  
    po_id INT,  
    changed_field VARCHAR(100),  
    old_value VARCHAR(255),
    new_value VARCHAR(255), 
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
    employee_id INT,  
    FOREIGN KEY (po_id) REFERENCES purchase_order(po_id),
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id)  
);
