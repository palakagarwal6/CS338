USE netflix;

SELECT g.genre_name, COUNT(*) AS movie_count FROM genre g
JOIN Classified_In c ON g.genre_id = c.genre_id 
GROUP BY g.genre_name 
ORDER BY movie_count DESC
LIMIT 10
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\test-R11a.out";