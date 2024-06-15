CREATE TABLE Movie (
	movie_id INT NOT NULL,
    title Varchar(50) NOT NULL DEFAULT 'No Title',
    overview Varchar(1000) DEFAULT 'No Overview', # for large paragraphs
    `status` Varchar(20) NOT NULL,
    release_date Varchar(50), # will change to date format later
    adult Varchar(5) DEFAULT 'False', # will be booleans
    video Varchar(5) DEFAULT 'False', # will be booleans
    runtime DECIMAL(5,1) DEFAULT 0,
    popularity DECIMAL(10,6) DEFAULT 0,
    vote_average DECIMAL(2,1) DEFAULT 0.0,
    vote_count INT DEFAULT 0,
    PRIMARY KEY(movie_id)
);

ALTER TABLE MovieInfo ADD CONSTRAINT movie_id CHECK (movie_id >= 0);
ALTER TABLE MovieInfo ADD CONSTRAINT status CHECK (status IN ('Released','Rumored','Post Production','In Production','Planned'));
UPDATE Movie SET release_date = STR_TO_DATE(release_date, '%Y-%m-%d');
ALTER TABLE MovieInfo ADD CONSTRAINT adult CHECK (adult IN ('True','False'));
ALTER TABLE MovieInfo ADD CONSTRAINT video CHECK (video IN ('True','False'));
ALTER TABLE MovieInfo ADD CONSTRAINT runtime CHECK (runtime >= 0);
ALTER TABLE MovieInfo ADD CONSTRAINT popularity CHECK (popularity >= 0);
ALTER TABLE MovieInfo ADD CONSTRAINT vote_average CHECK (vote_average >= 0);
ALTER TABLE MovieInfo ADD CONSTRAINT vote_count CHECK (vote_count >= 0);

CREATE TABLE Credit (
	credit_id INT NOT NULL,
    person_id INT NOT NULL,
	PRIMARY KEY(credit_id)
);

ALTER TABLE Credit ADD CONSTRAINT credit_id CHECK (credit_id >= 0);

CREATE TABLE Cast (
	cast_id INT NOT NULL UNIQUE,
    credit_id INT NOT NULL,
    FOREIGN KEY (credit_id) REFERENCES Credit (credit_id),
	PRIMARY KEY(credit_id)
);

CREATE TABLE Crew (
	Department Varchar(20),
    Job Varchar(20),
    FOREIGN KEY (credit_id) REFERENCES Credit (credit_id),
	PRIMARY KEY(credit_id)
);

CREATE TABLE Credit2 (
	person_id INT NOT NULL,
	name Varchar(50),
	PRIMARY KEY(person_id)
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

CREATE TABLE ProductionCountries (
	production_id INT NOT NULL,
	country Varchar(50),
	PRIMARY KEY(production_id, country)
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
	production_id INT NOT NULL,
	country Varchar(50),
    FOREIGN KEY (movie_id) REFERENCES Movie (movie_id),
	FOREIGN KEY (credit_id) REFERENCES Credit (credit_id),
	PRIMARY KEY(movie_id, credit_id)
);





