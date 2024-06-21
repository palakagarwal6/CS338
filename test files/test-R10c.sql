USE netflix;

SELECT * FROM production
WHERE production_id = 31
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\test-R10c before.out";

INSERT INTO production (production_id, production_name) 
VALUES ('31', '20th Century Studios');

SELECT * FROM production
WHERE production_id = 31
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\test-R10c after.out";