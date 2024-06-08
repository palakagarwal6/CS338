SELECT *
FROM Production
WHERE Title LIKE '%sh%'
AND Is_movie = 1
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\test-R8.out"