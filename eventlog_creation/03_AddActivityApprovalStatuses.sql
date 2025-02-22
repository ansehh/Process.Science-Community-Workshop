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
        WHEN ap.decision = 'PENDING' THEN CONCAT('Fordere Genehmigung Level ', ap.approval_level, ' an')
        WHEN ap.decision = 'APPROVED' THEN CONCAT('Erteile Genehmigung Level ', ap.approval_level)
        WHEN ap.decision = 'REJECTED' THEN CONCAT('Lehne Genehmigung Level ', ap.approval_level, ' ab')
    END AS activity,
    CASE
        WHEN ap.decision = 'PENDING' THEN 'Fordere Genehmigung an'
        WHEN ap.decision = 'APPROVED' THEN 'Erteile Genehmigung'
        WHEN ap.decision = 'REJECTED' THEN 'Lehne Genehmigung ab'
    END AS activity_grouped,
    ap.created_at AS timestamp,
    CASE
        WHEN ap.decision = 'PENDING' THEN 200
        WHEN ap.decision = 'APPROVED' THEN 210
        WHEN ap.decision = 'REJECTED' THEN 220
    END AS sort_key,
    emp.name AS user_name,
    po_poitem.case_po_number AS case_po_number,
    po_poitem.case_po_item AS case_po_item
FROM TMP_P2P_PO_POITEM AS po_poitem
INNER JOIN approval_process AS ap ON po_poitem.case_po_number = ap.po_id
LEFT JOIN employee AS emp ON ap.approver_id = emp.employee_id;