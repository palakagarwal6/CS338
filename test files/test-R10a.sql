USE netflix;

SELECT * FROM movie
WHERE movie_id = 36
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\test-R10a before.out";

INSERT INTO movie (movie_id, title, overview, status, release_date, adult, video, runtime, vote_average, vote_count) 
VALUES (36,'The Greatest Showman', 'Featuring catchy musical numbers, exotic performers and daring acrobatic feats, Barnum‘s mesmerizing spectacle soon takes the world by storm to become the greatest show on Earth.', 'Released', '2017-12-17', 'False','False','105','7.5','1500');

SELECT * FROM movie
WHERE movie_id = 36
INTO OUTFILE "C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\test-R10a after.out";