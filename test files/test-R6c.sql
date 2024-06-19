SELECT m.title
FROM movie m
JOIN Comprises_Of c ON m.movie_id = c.movie_id  # From N:M relationship 
JOIN credit cr ON c.person_id = cr.person_id 
WHERE cr.name = 'Leonardo DiCaprio'
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\test-R6c.out";