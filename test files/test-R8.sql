SELECT *
FROM movie
WHERE movie_id=11
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.4\\Uploads\\test-R8 before.out";

UPDATE movie 
SET title = "Star Wars: The Last Hope"
WHERE movie_id = 11;

SELECT *
FROM movie
WHERE movie_id = 11
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.4\\Uploads\\test-R8 after name change.out";

UPDATE movie 
SET vote_average = 8.2, vote_count = 6779 
WHERE movie_id = 11;

SELECT *
FROM movie
WHERE movie_id = 11
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.4\\Uploads\\test-R8 after vote change.out";

DELETE 
FROM Movie 
WHERE movie_id = 11;

SELECT *
FROM movie
WHERE movie_id = 11
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.4\\Uploads\\test-R8 after movie deliete.out";

INSERT INTO movie (movie_id, title, overview, status, release_date, adult, video, runtime, vote_average, vote_count) VALUES (36,"The Greatest Showman", "Featuring catchy musical numbers, exotic performers and daring acrobatic feats, Barnum's mesmerizing spectacle soon takes the world by storm to become the greatest show on Earth.", "Released", "2017-12-17", "False", "False","105","7.5","1500");

SELECT *
FROM movie
WHERE movie_id = 36
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.4\\Uploads\\test-R8 after insert.out";
