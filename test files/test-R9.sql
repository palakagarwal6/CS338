USE netflix;

SELECT * FROM movie
WHERE movie_id = 11
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\test-R9 before.out";

DELETE
FROM Movie
WHERE movie_id = 11;

SELECT *
FROM movie
WHERE movie_id = 11
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\test-R9 after.out";