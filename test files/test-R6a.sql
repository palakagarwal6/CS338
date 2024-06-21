USE netflix;

SELECT title
FROM movie 
WHERE title LIKE '%Star Wars%'
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\test-R6a.out";