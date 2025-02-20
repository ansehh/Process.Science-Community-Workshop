-- Erst Event Log Tabelle erstellen

DROP TABLE  IF EXISTS  event_log;

CREATE TABLE IF NOT EXISTS event_log (
    case_id VARCHAR(100),
    activity VARCHAR(100),
    timestamp TIMESTAMP,
    username VARCHAR(100)
);

CREATE TEMPORARY TABLE event_log_tmp AS

    -- POs erstellt

    SELECT
        CONCAT(po.po_id, '_', oi.order_item_id) as case_id,
        'Create Purchase Order Item' as activity,
        po.created_at as timestamp,
        e.name as username
    FROM purchase_order po
    JOIN order_item oi ON po.po_id = oi.po_id
    JOIN employee e ON po.employee_id = e.employee_id

    UNION ALL

    -- Genehmigungsprozess Events
    SELECT
        CONCAT(po.po_id, '_', oi.order_item_id) as case_id,
        CONCAT('Purchase Order ', ap.decision) as activity,
        ap.created_at as timestamp,
        e.name as username
    FROM approval_process ap
    JOIN purchase_order po ON ap.po_id = po.po_id
    JOIN order_item oi ON po.po_id = oi.po_id
    JOIN employee e ON ap.approver_id = e.employee_id

    UNION ALL

    -- Wareneingänge (inkl. Teillieferungen)
    SELECT
        CONCAT(po.po_id, '_', oi.order_item_id) as case_id,
        CASE
            WHEN gr.quantity_received = oi.quantity THEN 'Goods Receipt Complete'
            ELSE 'Goods Receipt Partial'
        END as activity,
        gr.receipt_date as timestamp,
        e.name as username
    FROM goods_receipt gr
    JOIN purchase_order po ON gr.po_id = po.po_id
    JOIN order_item oi ON gr.order_item_id = oi.order_item_id
    JOIN employee e ON gr.receiver_id = e.employee_id

    UNION ALL

    -- Rechnungserfassung
    SELECT
        CONCAT(po.po_id, '_', oi.order_item_id) as case_id,
        CONCAT('Invoice ', LOWER(i.status)) as activity,
        i.created_at as timestamp,
        'SYSTEM' as username  -- Da kein Bearbeiter in der Invoice-Tabelle hinterlegt ist
    FROM invoice i
    JOIN purchase_order po ON i.po_id = po.po_id
    JOIN order_item oi ON i.order_item_id = oi.order_item_id

    UNION ALL

    -- Zahlungen
    SELECT
        CONCAT(po.po_id, '_', oi.order_item_id) as case_id,
        CONCAT('Payment ', LOWER(p.status)) as activity,
        p.payment_date as timestamp,
        'SYSTEM' as username  -- Da kein Bearbeiter in der Payment-Tabelle hinterlegt ist
    FROM payment p
    JOIN invoice i ON p.invoice_id = i.invoice_id
    JOIN purchase_order po ON i.po_id = po.po_id
    JOIN order_item oi ON i.order_item_id = oi.order_item_id;

-- Daten sortiert in die finale Tabelle einfügen
INSERT INTO event_log (case_id, activity, timestamp, username)
SELECT case_id, activity, timestamp, username
FROM event_log_tmp
ORDER BY case_id, timestamp;

-- Temporäre Tabelle aufräumen
DROP TEMPORARY TABLE IF EXISTS event_log_tmp;