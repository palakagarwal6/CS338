USE netflix;


-- movie(movie_id, title, overview, status, release date, adult, video, runtime, vote_average, vote_count)
CREATE TABLE Movie (
	movie_id INT NOT NULL,
    title Varchar(100) NOT NULL DEFAULT 'No Title',
    overview Varchar(8000) DEFAULT 'No Overview', # for large paragraphs
    status Varchar(100) NOT NULL,
    release_date Varchar(50), # will change to date format later
    adult Varchar(5) DEFAULT 'False', # will be booleans
    video Varchar(5) DEFAULT 'False', # will be booleans
    runtime DECIMAL(5,1) DEFAULT 0,
    vote_average DECIMAL(2,1) DEFAULT 0.0,
    vote_count INT DEFAULT 0,
    PRIMARY KEY(movie_id)
);

ALTER TABLE Movie ADD CONSTRAINT movie_id CHECK (movie_id >= 0); -- check if movie_id is non-negative
ALTER TABLE Movie ADD CONSTRAINT status CHECK (status IN ('Rumored','Planned','In Production','Post Production','Released','Canceled')); -- constrain status to certain conditions
UPDATE Movie SET release_date = STR_TO_DATE(release_date, '%Y-%m-%d'); -- constrain release date to date format
ALTER TABLE Movie ADD CONSTRAINT adult CHECK (adult IN ('True','False')); -- adult to be bool
ALTER TABLE Movie ADD CONSTRAINT video CHECK (adult IN ('True','False')); -- video to be bool
ALTER TABLE Movie ADD CONSTRAINT runtime CHECK (runtime >= 0); -- check if runtime is non-negative
ALTER TABLE Movie ADD CONSTRAINT vote_average CHECK (vote_average >= 0); -- check if non-negative
ALTER TABLE Movie ADD CONSTRAINT vote_count CHECK (vote_count >= 0); -- check if non-negative

-- credit(person_id, name)
CREATE TABLE Credit (
    person_id INT NOT NULL,
	name Varchar(100),
	PRIMARY KEY(person_id)
);

ALTER TABLE Credit ADD CONSTRAINT person_id CHECK (person_id >= 0); -- check if person_id is non-negative

-- Cast(cast_id, person_id, movie_id, character)
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

-- crew(person_id)
CREATE TABLE Crew (
	person_id INT NOT NULL,
    FOREIGN KEY (person_id) REFERENCES Credit (person_id)
		ON DELETE CASCADE
        ON UPDATE CASCADE,
	PRIMARY KEY(person_id)
);

-- department(dept_name)
CREATE TABLE Department(
	Dept_Name Varchar(50) UNIQUE,
    PRIMARY KEY(Dept_Name)
);

-- job(job_name)
CREATE TABLE Job(
	Job_Name Varchar(50) UNIQUE,
    PRIMARY KEY(Job_Name)
);

-- performs(job_name, person_id, movie_id) (relation: crew <---> job)
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

-- assigned_to(dept_name, person_id, movie_id) (relation: crew <---> department)
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

-- production(production_id, production_name)
CREATE TABLE Production (
	production_id INT NOT NULL,
	production_name Varchar(100),
	PRIMARY KEY(production_id)
);

-- genre(genre_id, genre_name)
CREATE TABLE Genre (
	genre_id INT NOT NULL,
	genre_name Varchar(50),
	PRIMARY KEY(genre_id)
);

-- produce_by(movie_id, production_id) (relation: movie <---> production)
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

-- classified_in(movie_id, genre_id) (relation: movie <---> genre)
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

-- comprises_of(movie_id, person_id) (relation: movie <---> crew)
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