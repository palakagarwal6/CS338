SELECT title, CONCAT("id: ", movie_id), vote_average, status, runtime, overview
FROM movie 
WHERE movie_id = 11
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\test-R7.out";