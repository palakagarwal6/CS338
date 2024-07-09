use netflix;

SELECT cr.name, j.Job_Name, AVG(m.vote_average) AS "Avg. Rating"
FROM Movie m
JOIN Classified_In ci ON m.movie_id = ci.movie_id
JOIN Genre g ON ci.genre_id = g.genre_id
JOIN Performs p ON p.movie_id = m.movie_id
JOIN Crew c ON p.person_id = c.person_id
JOIN Job j ON p.Job_Name = j.Job_Name
JOIN Credit cr ON c.person_id = cr.person_id
GROUP BY cr.name
ORDER BY "Avg. Rating" DESC
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.4\\Uploads\\test-R9.out";