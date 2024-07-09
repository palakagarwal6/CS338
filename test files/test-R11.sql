use netflix;

SELECT g.genre_name, COUNT(*) AS "Movie Count" FROM genre g
JOIN Classified_In c ON g.genre_id = c.genre_id 
GROUP BY g.genre_name 
ORDER BY "Movie Count" DESC
LIMIT 10
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.4\\Uploads\\test-R11a.out";

SELECT g.genre_name, ROUND(AVG(m.vote_average), 2) AS "Avg. Rating"
FROM genre g JOIN Classified_In c ON g.genre_id = c.genre_id
JOIN movie m ON c.movie_id = m.movie_id
GROUP BY g.genre_name
ORDER BY "Avg. Rating" DESC
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.4\\Uploads\\test-R11b.out";