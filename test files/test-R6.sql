Use netflix;
SELECT *
FROM production 
ORDER BY RAND()
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\test-R6.out"