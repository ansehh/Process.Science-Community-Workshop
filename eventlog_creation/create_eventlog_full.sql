DROP TABLE IF EXISTS EventLogP2P;

CREATE TABLE EventLogP2P
(
    case_id                    VARCHAR(50),
    activity                   VARCHAR(300),
    activity_grouped           VARCHAR(300),
    timestamp                  DATETIME,
    sort_key                   INT,
    user_name                  VARCHAR(100),
    case_po_number             VARCHAR(10),
    case_po_item               VARCHAR(5),
    changed_field              VARCHAR(20),
    changed_from               VARCHAR(255),
    changed_to                 VARCHAR(255)
);

DROP TABLE IF EXISTS TMP_P2P_PO_POITEM;

CREATE TABLE TMP_P2P_PO_POITEM AS
SELECT DISTINCT CONCAT(poitem.po_id, '-', poitem.item_number)       AS case_id,
                po.created_at                                       AS created_at,
                po.po_id                                            AS case_po_number,
                poitem.item_number                                  AS case_po_item,
                po.supplier_id                                      AS supplier_id,
                po.employee_id                                      AS employee_id,
                po.total_amount                                     AS total_amount,
                po.currency                                         AS currency,
                po.status                                           AS status,
                poitem.material_id                                  AS material_id,
                poitem.price_per_unit                               AS price_per_unit,
                poitem.quantity                                     AS quantity
FROM purchase_order AS po
    INNER JOIN order_item AS poitem on po.po_id = poitem.po_id;


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
    'Gleiche Rechnung aus' AS activity,
    'Gleiche Rechnung aus' AS activity_grouped,
    inv.created_at AS timestamp,
    600 AS sort_key,
    po_poitem.case_po_number AS case_po_number,
    po_poitem.case_po_item AS case_po_item
FROM TMP_P2P_PO_POITEM AS po_poitem
INNER JOIN invoice AS inv ON po_poitem.case_po_number = inv.po_id
WHERE inv.status = 'PAID';


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