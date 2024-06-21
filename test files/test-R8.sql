USE netflix;

SELECT *
FROM movie
WHERE movie_id = 11
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\test-R8 before.out";

UPDATE movie 
SET title = 'Star Wars: The Last Hope'
WHERE movie_id = 11;

UPDATE movie 
SET vote_average = 8.2, vote_count = 6779 
WHERE movie_id = 11;

SELECT *
FROM movie
WHERE movie_id = 11
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\test-R8 after.out";