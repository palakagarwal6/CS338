SELECT m.movie_id, m.title, p.production_name
FROM movie m
JOIN Produced_By c ON m.movie_id = c.movie_id
JOIN Production p ON c.production_id = p.production_id
WHERE production_name LIKE "%Twentieth%"
ORDER BY p.production_name, m.movie_id, m.release_date DESC
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.4\\Uploads\\test-R7.out";