USE netflix;

SELECT g.genre_name, AVG(m.vote_average) AS average_rating 
FROM genre g JOIN Classified_In c ON g.genre_id = c.genre_id 
JOIN movie m ON c.movie_id = m.movie_id
GROUP BY g.genre_name
ORDER BY average_rating DESC
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\test-R11b.out";