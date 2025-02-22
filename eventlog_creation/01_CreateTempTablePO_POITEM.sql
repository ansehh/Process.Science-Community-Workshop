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