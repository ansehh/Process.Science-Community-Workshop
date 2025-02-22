INSERT INTO EventLogP2P(
    case_id,
    activity,
    activity_grouped,
    timestamp,
    sort_key,
    case_po_number,
    case_po_item
)
SELECT DISTINCT
    po_poitem.case_id AS case_id,
    'Erfasse Rechnung' AS activity,
    'Erfasse Rechnung' AS activity_grouped,
    inv.created_at AS timestamp,
    400 AS sort_key,
    po_poitem.case_po_number AS case_po_number,
    po_poitem.case_po_item AS case_po_item
FROM TMP_P2P_PO_POITEM AS po_poitem
INNER JOIN invoice AS inv ON po_poitem.case_po_number = inv.po_id;