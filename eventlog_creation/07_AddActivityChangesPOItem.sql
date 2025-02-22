INSERT INTO EventLogP2P(
    case_id,
    activity,
    activity_grouped,
    timestamp,
    sort_key,
    user_name,
    case_po_number,
    case_po_item,
    changed_field,
    changed_from,
    changed_to
)
SELECT DISTINCT
    po_poitem.case_id AS case_id,
    CASE
        WHEN cd.changed_field = 'Price' THEN 'Ändere Bestellposition: Preis'
        WHEN cd.changed_field = 'Quantity' THEN 'Ändere Bestellposition: Menge'
        WHEN cd.changed_field = 'Material' THEN 'Ändere Bestellposition: Material'
    END AS activity,
    'Ändere Bestellposition' AS activity_grouped,
    cd.timestamp AS timestamp,
    CASE
        WHEN cd.changed_field = 'Price' THEN 150
        WHEN cd.changed_field = 'Quantity' THEN 151
        WHEN cd.changed_field = 'Material' THEN 152
    END AS sort_key,
    emp.name AS user_name,
    po_poitem.case_po_number AS case_po_number,
    po_poitem.case_po_item AS case_po_item,
    cd.changed_field AS changed_field,
    cd.old_value AS changed_from,
    cd.new_value AS changed_to
FROM TMP_P2P_PO_POITEM AS po_poitem
INNER JOIN cdpos AS cd ON po_poitem.case_po_number = cd.po_id
    AND po_poitem.case_po_item = cd.po_item_number
LEFT JOIN employee AS emp ON cd.employee_id = emp.employee_id;