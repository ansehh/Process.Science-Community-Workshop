INSERT INTO EventLogP2P(case_id,
                        activity,
                        activity_grouped,
                        timestamp,
                        sort_key,
                        user_name,
                        case_po_number,
                        case_po_item)
SELECT DISTINCT po_poitem.case_id               AS case_id,
                'Lege Bestellposition an'       AS activity,
                'Lege Bestellposition an'       AS activity_grouped,
                po_poitem.created_at            AS timestamp,
                100                             AS sort_key,
                emp.name                        AS user_name,
                po_poitem.case_po_number        AS case_po_number,
                po_poitem.case_po_item          AS case_po_item
FROM TMP_P2P_PO_POITEM AS po_poitem
    LEFT JOIN employee AS emp ON po_poitem.employee_id = emp.employee_id