ALTER TABLE himalaya.expedition DROP COLUMN  harmonized_agency_name;
ALTER TABLE himalaya.expedition ADD COLUMN harmonized_agency_name VARCHAR(255);

SET SQL_SAFE_UPDATES = 0;
-- Mettre à jour les valeurs de la nouvelle colonne
UPDATE himalaya.expedition
SET harmonized_agency_name = TRIM(
    REGEXP_REPLACE(
        REGEXP_REPLACE(
            trekking_agency,
            '\\([^)]*\\)',  -- Supprimer tout ce qui est entre parenthèses
            ''
        ),
        '[/?].*$',  -- Supprimer tout ce qui suit un / ou un ?
        ''
    )
);
SET SQL_SAFE_UPDATES = 1;
SELECT distinct trekking_agency, harmonized_agency_name FROM himalaya.expedition ;