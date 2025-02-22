INSERT INTO EventLogP2P(
    case_id,
    activity,
    activity_grouped,
    timestamp,
    sort_key,
    user_name,
    case_po_number,
    case_po_item
)
SELECT DISTINCT
    po_poitem.case_id AS case_id,
    CASE
        WHEN gr.quality_status = 'GOOD'
            THEN 'Erfasse Wareneingang'
        WHEN gr.quality_status = 'DAMAGED' OR gr.quality_status = 'REJECTED'
            THEN 'Lehne Wareneingang ab'
    END AS activity,
    'Wareneingang erfasst' AS activity_grouped,
    gr.created_at AS timestamp,
    300 AS sort_key,
    emp.name AS user_name,
    po_poitem.case_po_number AS case_po_number,
    po_poitem.case_po_item AS case_po_item
FROM TMP_P2P_PO_POITEM AS po_poitem
INNER JOIN goods_receipt AS gr ON po_poitem.case_po_number = gr.po_id AND po_poitem.case_po_item = gr.po_item_number
LEFT JOIN employee AS emp ON gr.receiver_id = emp.employee_id;