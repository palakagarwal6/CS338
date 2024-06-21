USE netflix;

SELECT m.title
FROM movie m
JOIN Produced_By c ON m.movie_id = c.movie_id  # From N:M relationship 
JOIN Production p ON c.production_id = p.production_id
WHERE p.production_name = "Lucasfilm"
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\test-R6d.out";