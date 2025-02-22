-- Create Event Log Table
DROP TABLE IF EXISTS event_log;

CREATE TABLE IF NOT EXISTS event_log (
    case_id VARCHAR(100),
    activity VARCHAR(100),
    timestamp TIMESTAMP,
    username VARCHAR(100),
    old_value VARCHAR(255),
    new_value VARCHAR(255),
    changed_field VARCHAR(100)
);

CREATE TEMPORARY TABLE event_log_tmp AS

    -- POs erstellt
    SELECT
        CONCAT(po.po_id, '_', oi.item_number) as case_id,
        'Create Purchase Order Item' as activity,
        po.created_at as timestamp,
        e.name as username,
        NULL as old_value,
        NULL as new_value,
        NULL as changed_field
    FROM purchase_order po
    JOIN order_item oi ON po.po_id = oi.po_id
    JOIN employee e ON po.employee_id = e.employee_id

    UNION ALL

    -- Genehmigungsprozess Events
    SELECT
        CONCAT(po.po_id, '_', oi.item_number) as case_id,
        CONCAT('Purchase Order ', ap.decision) as activity,
        ap.created_at as timestamp,
        e.name as username,
        NULL as old_value,
        NULL as new_value,
        NULL as changed_field
    FROM approval_process ap
    JOIN purchase_order po ON ap.po_id = po.po_id
    JOIN order_item oi ON po.po_id = oi.po_id
    JOIN employee e ON ap.approver_id = e.employee_id

    UNION ALL

    -- Wareneingänge (inkl. Teillieferungen)
    SELECT
        CONCAT(po.po_id, '_', oi.item_number) as case_id,
        CASE 
            WHEN gr.quantity_received = oi.quantity THEN 'Goods Receipt Complete'
            ELSE 'Goods Receipt Partial'
        END as activity,
        gr.receipt_date as timestamp,
        e.name as username,
        NULL as old_value,
        NULL as new_value,
        NULL as changed_field
    FROM goods_receipt gr
    JOIN purchase_order po ON gr.po_id = po.po_id
    JOIN order_item oi ON gr.po_id = oi.po_id AND gr.po_item_number = oi.item_number
    JOIN employee e ON gr.receiver_id = e.employee_id

    UNION ALL

    -- Rechnungserfassung
    SELECT
        CONCAT(po.po_id, '_', oi.item_number) as case_id,
        CONCAT('Invoice ', LOWER(i.status)) as activity,
        i.created_at as timestamp,
        'SYSTEM' as username,
        NULL as old_value,
        NULL as new_value,
        NULL as changed_field
    FROM invoice i
    JOIN purchase_order po ON i.po_id = po.po_id
    JOIN order_item oi ON i.po_id = oi.po_id AND i.po_item_number = oi.item_number

    UNION ALL

    -- Zahlungen
    SELECT
        CONCAT(po.po_id, '_', oi.item_number) as case_id,
        CONCAT('Payment ', LOWER(p.status)) as activity,
        p.payment_date as timestamp,
        'SYSTEM' as username,
        NULL as old_value,
        NULL as new_value,
        NULL as changed_field
    FROM payment p
    JOIN invoice i ON p.invoice_id = i.invoice_id
    JOIN purchase_order po ON i.po_id = po.po_id
    JOIN order_item oi ON i.po_id = oi.po_id AND i.po_item_number = oi.item_number

    UNION ALL

    -- Changes to Order Items (CDPOS)
    SELECT
        CONCAT(po.po_id, '_', oi.item_number) as case_id,
        'Change Order Item' as activity,
        cdpos.timestamp as timestamp,
        e.name as username,
        cdpos.old_value as old_value,
        cdpos.new_value as new_value,
        cdpos.changed_field as changed_field
    FROM cdpos
    JOIN order_item oi ON cdpos.po_id = oi.po_id AND cdpos.po_item_number = oi.item_number
    JOIN purchase_order po ON oi.po_id = po.po_id
    JOIN employee e ON cdpos.employee_id = e.employee_id

    UNION ALL

    -- Changes to Purchase Orders (CDHDR)
    SELECT
        CONCAT(po.po_id, '_', oi.item_number) as case_id,
        'Change Order' as activity,
        cdhdr.timestamp as timestamp,
        e.name as username,
        cdhdr.old_value as old_value,
        cdhdr.new_value as new_value,
        cdhdr.changed_field as changed_field
    FROM cdhdr
    JOIN purchase_order po ON cdhdr.po_id = po.po_id
    JOIN order_item oi ON po.po_id = oi.po_id
    JOIN employee e ON cdhdr.employee_id = e.employee_id;

-- Insert sorted data into the final table
INSERT INTO event_log (case_id, activity, timestamp, username, old_value, new_value, changed_field)
SELECT case_id, activity, timestamp, username, old_value, new_value, changed_field
FROM event_log_tmp
ORDER BY case_id, timestamp;

-- Clean up temporary table
DROP TEMPORARY TABLE IF EXISTS event_log_tmp;