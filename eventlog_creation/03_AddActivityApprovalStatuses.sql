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
SELECT
    t.case_id,
    t.activity_grouped AS activity,
    t.activity_grouped,
    t.timestamp,
    t.sort_key,
    t.user_name,
    t.case_po_number,
    t.case_po_item
FROM (
    SELECT
        po_poitem.case_id AS case_id,
        CASE
            WHEN ap.decision = 'APPROVED' THEN 'Erteile Genehmigung'
            WHEN ap.decision = 'REJECTED' THEN 'Lehne Genehmigung ab'
        END AS activity_grouped,
        ap.created_at AS timestamp,
        CASE
            WHEN ap.decision = 'APPROVED' THEN 200
            WHEN ap.decision = 'REJECTED' THEN 210
        END AS sort_key,
        emp.name AS user_name,
        po_poitem.case_po_number AS case_po_number,
        po_poitem.case_po_item AS case_po_item,
        ROW_NUMBER() OVER (PARTITION BY po_poitem.case_id ORDER BY ap.created_at DESC) AS row_num
    FROM TMP_P2P_PO_POITEM AS po_poitem
    INNER JOIN approval_process AS ap ON po_poitem.case_po_number = ap.po_id AND ap.decision in ('APPROVED', 'REJECTED')
    LEFT JOIN employee AS emp ON ap.approver_id = emp.employee_id
) t
WHERE t.row_num = 1;