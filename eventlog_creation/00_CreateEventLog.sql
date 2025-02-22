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