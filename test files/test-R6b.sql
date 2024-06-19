SELECT m.title #, vote_average
FROM movie m 
JOIN Classified_In c ON m.movie_id = c.movie_id
JOIN genre g ON c.genre_id = g.genre_id 
WHERE g.genre_name IN ('Action', 'Adventure')
ORDER BY vote_average
DESC LIMIT 10
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\test-R6b.out";