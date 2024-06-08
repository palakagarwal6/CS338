Use netflix;
SELECT * 
FROM production
JOIN rating ON production.Title = rating.Title
Where production.Title = "Shrek 2"
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\R9.out"