CREATE TABLE Movie (
	movie_id INT NOT NULL,
    title Varchar(50) NOT NULL DEFAULT 'No Title',
    overview Varchar(1000) DEFAULT 'No Overview', # for large paragraphs
    `status` Varchar(20) NOT NULL,
    release_date Varchar(50), # will change to date format later
    adult Varchar(5) DEFAULT 'False', # will be booleans
    video Varchar(5) DEFAULT 'False', # will be booleans
    runtime DECIMAL(5,1) DEFAULT 0,
    vote_average DECIMAL(2,1) DEFAULT 0.0,
    vote_count INT DEFAULT 0,
    PRIMARY KEY(movie_id)
);

ALTER TABLE MovieInfo ADD CONSTRAINT movie_id CHECK (movie_id >= 0);
ALTER TABLE MovieInfo ADD CONSTRAINT status CHECK (status IN ('Released','Rumored','Post Production','In Production','Planned'));
UPDATE Movie SET release_date = STR_TO_DATE(release_date, '%Y-%m-%d');
ALTER TABLE MovieInfo ADD CONSTRAINT adult CHECK (adult IN ('True','False'));
ALTER TABLE MovieInfo ADD CONSTRAINT runtime CHECK (runtime >= 0);
ALTER TABLE MovieInfo ADD CONSTRAINT popularity CHECK (popularity >= 0);
ALTER TABLE MovieInfo ADD CONSTRAINT vote_average CHECK (vote_average >= 0);
ALTER TABLE MovieInfo ADD CONSTRAINT vote_count CHECK (vote_count >= 0);

CREATE TABLE Credit (
    person_id INT NOT NULL,
	name Varchar(50),
	gender INT NOT NULL,
	PRIMARY KEY(person_id)
);

ALTER TABLE Credit ADD CONSTRAINT person_id CHECK (person_id >= 0);
ALTER TABLE Credit ADD CONSTRAINT gender CHECK (gender >= 0 AND gender <= 2);

CREATE TABLE Cast (
	cast_id INT NOT NULL UNIQUE,
    person_id INT NOT NULL UNIQUE,
    FOREIGN KEY (person_id) REFERENCES Credit (person_id),
	PRIMARY KEY(cast_id, person_id)
);

CREATE TABLE Crew (
	person_id INT NOT NULL,
	Department Varchar(20),
    FOREIGN KEY (person_id) REFERENCES Credit (person_id),
	PRIMARY KEY(person_id)
);

CREATE TABLE Crew_Job (
	person_id INT NOT NULL,
    Job Varchar(20),
    FOREIGN KEY (person_id) REFERENCES Credit (person_id),
	PRIMARY KEY(person_id, Job)
);

CREATE TABLE Cast2 (
	cast_id INT NOT NULL,
	`Character` Varchar(50),
    `Order` Varchar(50),
	PRIMARY KEY(cast_id)
);

CREATE TABLE Production (
	production_id INT NOT NULL,
	production_name Varchar(50),
	PRIMARY KEY(production_id)
);

CREATE TABLE Genre (
	genre_id INT NOT NULL,
	genre_name Varchar(50),
	PRIMARY KEY(genre_id)
);

CREATE TABLE Produced_By (
	production_id INT NOT NULL,
	movie_id INT NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES Movie (movie_id),
	FOREIGN KEY (production_id) REFERENCES Production (production_id),
	PRIMARY KEY(production_id, movie_id)
);

CREATE TABLE Classified_In (
	movie_id INT NOT NULL,
	genre_id Varchar(50),
    FOREIGN KEY (movie_id) REFERENCES Movie (movie_id),
	FOREIGN KEY (genre_id) REFERENCES Genre (genre_id),
	PRIMARY KEY(movie_id, genre_id)
);

CREATE TABLE Comprises_Of (
	movie_id INT NOT NULL,
	person_id INT NOT NULL UNIQUE,
    FOREIGN KEY (movie_id) REFERENCES Movie (movie_id),
	FOREIGN KEY (person_id) REFERENCES Credit (person_id),
	PRIMARY KEY(movie_id, person_id)
);





