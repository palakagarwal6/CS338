USE netflix;

SELECT * FROM genre
WHERE genre_id = 10
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\test-R10b before.out";

INSERT INTO genre (genre_id, genre_name) 
VALUES (10, 'Musical');

SELECT * FROM genre
WHERE genre_id = 10
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\test-R10b after.out";