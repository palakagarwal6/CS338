SELECT title
FROM movie 
WHERE title LIKE '%Inception%'
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\test-R6a.out";