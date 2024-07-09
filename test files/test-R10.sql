use netflix;

SELECT p.production_name, AVG(m.vote_average) AS vote_score 
FROM Movie m 
JOIN Classified_In ci ON m.movie_id = ci.movie_id 
JOIN Genre g ON ci.genre_id = g.genre_id 
JOIN Produced_By pb ON m.movie_id = pb.movie_id 
JOIN Production p ON pb.production_id = p.production_id 
WHERE g.genre_name = 'Action' 
GROUP BY p.production_name ORDER BY vote_score DESC
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.4\\Uploads\\test-R10.out";
