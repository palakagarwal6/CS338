USE netflix;

CREATE TABLE Movie (
	movie_id INT NOT NULL,
    title Varchar(100) NOT NULL DEFAULT 'No Title',
    overview Varchar(8000) DEFAULT 'No Overview', # for large paragraphs
    `status` Varchar(20) NOT NULL,
    release_date Varchar(50), # will change to date format later
    adult Varchar(5) DEFAULT 'False', # will be booleans
    video Varchar(5) DEFAULT 'False', # will be booleans
    runtime DECIMAL(5,1) DEFAULT 0,
    vote_average DECIMAL(2,1) DEFAULT 0.0,
    vote_count INT DEFAULT 0,
    PRIMARY KEY(movie_id)
);

ALTER TABLE Movie ADD CONSTRAINT movie_id CHECK (movie_id >= 0);
ALTER TABLE Movie ADD CONSTRAINT status CHECK (status IN ('Released','Rumored','Post Production','In Production','Planned'));
UPDATE Movie SET release_date = STR_TO_DATE(release_date, '%Y-%m-%d');
ALTER TABLE Movie ADD CONSTRAINT adult CHECK (adult IN ('True','False'));
ALTER TABLE Movie ADD CONSTRAINT runtime CHECK (runtime >= 0);
ALTER TABLE Movie ADD CONSTRAINT vote_average CHECK (vote_average >= 0);
ALTER TABLE Movie ADD CONSTRAINT vote_count CHECK (vote_count >= 0);

CREATE TABLE Credit (
    person_id INT NOT NULL,
	name Varchar(100),
	PRIMARY KEY(person_id)
);

ALTER TABLE Credit ADD CONSTRAINT person_id CHECK (person_id >= 0);

-- Subclass of Credit
CREATE TABLE Cast (
	cast_id INT NOT NULL,
    movie_id INT NOT NULL,
    person_id INT NOT NULL,
    `Character` Varchar(100),
    UNIQUE (movie_id, cast_id),
    FOREIGN KEY (person_id) REFERENCES Credit (person_id)
		ON DELETE CASCADE
        ON UPDATE CASCADE,
	FOREIGN KEY (movie_id) REFERENCES movie (movie_id)
		ON DELETE CASCADE
        ON UPDATE CASCADE,
	PRIMARY KEY(cast_id, person_id)
);

-- Subclass of Credit
CREATE TABLE Crew (
	person_id INT NOT NULL,
    FOREIGN KEY (person_id) REFERENCES Credit (person_id)
		ON DELETE CASCADE
        ON UPDATE CASCADE,
	PRIMARY KEY(person_id)
);

-- New Entity
CREATE TABLE Department(
	Dept_Name Varchar(50) UNIQUE,
    PRIMARY KEY(Dept_Name)
);

-- New Entity
CREATE TABLE Job(
	Job_Name Varchar(50) UNIQUE,
    PRIMARY KEY(Job_Name)
);

-- M:N for Crew and Job
CREATE TABLE Performs (
	Job_Name Varchar(50),
	person_id INT NOT NULL,
    movie_id INT NOT NULL,
    FOREIGN KEY (Job_Name) REFERENCES Job (Job_Name)
		ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (person_id) REFERENCES Crew (person_id)
		ON DELETE CASCADE
        ON UPDATE CASCADE,
	FOREIGN KEY (movie_id) REFERENCES movie (movie_id)
		ON DELETE CASCADE
        ON UPDATE CASCADE,
	PRIMARY KEY(Job_Name, person_id, movie_id)
);

-- M:N for Crew and Department
CREATE TABLE Assigned_To (
	Dept_Name Varchar(50),
	person_id INT NOT NULL,
    movie_id INT NOT NULL,
    FOREIGN KEY (Dept_Name) REFERENCES Department (Dept_Name)
		ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (person_id) REFERENCES Crew (person_id)
		ON DELETE CASCADE
        ON UPDATE CASCADE,
	FOREIGN KEY (movie_id) REFERENCES movie (movie_id)
		ON DELETE CASCADE
        ON UPDATE CASCADE,
	PRIMARY KEY(Dept_Name, person_id, movie_id)
);

CREATE TABLE Production (
	production_id INT NOT NULL,
	production_name Varchar(100),
	PRIMARY KEY(production_id)
);

CREATE TABLE Genre (
	genre_id INT NOT NULL,
	genre_name Varchar(50),
	PRIMARY KEY(genre_id)
);

-- M:N for Movie and Production
CREATE TABLE Produced_By (
	movie_id INT NOT NULL,
    production_id INT NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES Movie (movie_id)
		ON DELETE CASCADE
        ON UPDATE CASCADE,
	FOREIGN KEY (production_id) REFERENCES Production (production_id)
		ON DELETE CASCADE
        ON UPDATE CASCADE,
	PRIMARY KEY(movie_id, production_id)
);

-- M:N for Movie and Genre
CREATE TABLE Classified_In (
	movie_id INT NOT NULL,
	genre_id INT NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES Movie (movie_id)
		ON DELETE CASCADE
        ON UPDATE CASCADE,
	FOREIGN KEY (genre_id) REFERENCES Genre (genre_id)
		ON DELETE CASCADE
        ON UPDATE CASCADE,
	PRIMARY KEY(movie_id, genre_id)
);

-- M:N for Movie and Credit
CREATE TABLE Comprises_Of (
	movie_id INT NOT NULL,
	person_id INT NOT NULL,
    FOREIGN KEY (movie_id) REFERENCES Movie (movie_id)
		ON DELETE CASCADE
        ON UPDATE CASCADE,
	FOREIGN KEY (person_id) REFERENCES Credit (person_id)
		ON DELETE CASCADE
        ON UPDATE CASCADE,
	PRIMARY KEY(movie_id, person_id)
);
