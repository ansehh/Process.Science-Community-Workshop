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
        WHEN cd.changed_field = 'Currency' THEN 'Ändere Bestellung: Währung'
        WHEN cd.changed_field = 'Supplier' THEN 'Ändere Bestellung: Lieferant'
    END AS activity,
    'Ändere Bestellung' AS activity_grouped,
    cd.timestamp AS timestamp,
    CASE
        WHEN cd.changed_field = 'Currency' THEN 110
        WHEN cd.changed_field = 'Supplier' THEN 111
    END AS sort_key,
    emp.name AS user_name,
    po_poitem.case_po_number AS case_po_number,
    po_poitem.case_po_item AS case_po_item,
    cd.changed_field AS changed_field,
    cd.old_value AS changed_from,
    cd.new_value AS changed_to
FROM TMP_P2P_PO_POITEM AS po_poitem
INNER JOIN cdhdr AS cd ON po_poitem.case_po_number = cd.po_id
LEFT JOIN employee AS emp ON cd.employee_id = emp.employee_id;