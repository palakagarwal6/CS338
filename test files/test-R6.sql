use netflix;

SELECT title
FROM movie 
WHERE title LIKE '%Star Wars%'
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.4\\Uploads\\test-R6a.out";

SELECT m.title # , m.vote_average
FROM movie m 
JOIN Classified_In c ON m.movie_id = c.movie_id
JOIN genre g ON c.genre_id = g.genre_id 
WHERE g.genre_name IN ('Action', 'Adventure')
ORDER BY vote_average
DESC LIMIT 10
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.4\\Uploads\\test-R6b.out";

SELECT m.title
FROM movie m
JOIN Comprises_Of c ON m.movie_id = c.movie_id  # From N:M relationship
JOIN credit cr ON c.person_id = cr.person_id
WHERE cr.name LIKE '%Mark Hamill%'
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.4\\Uploads\\test-R6c.out";

SELECT m.title
FROM movie m
JOIN Produced_By c ON m.movie_id = c.movie_id  # From N:M relationship 
JOIN Production p ON c.production_id = p.production_id
WHERE p.production_name = "Lucasfilm"
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.4\\Uploads\\test-R6d.out";

SELECT title, CONCAT("id: ", movie_id), vote_average, status, runtime, overview
FROM movie 
WHERE movie_id = 11
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.4\\Uploads\\test-R6e.out";
