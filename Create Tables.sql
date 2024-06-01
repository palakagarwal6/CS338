# CREATE SCHEMA Netflix
USE netflix;

CREATE TABLE Production (
	Title VARCHAR(50) NOT NULL,
    Date_As_Of Varchar(50), # will change to date format later
    Release_Date Varchar(50), # will change to date format later
    Netflix_Exclusive Varchar(3), # for yes/no (updated format to bit later)
    Viewership_Score INT,
    PRIMARY KEY(Title, Date_As_Of)
);


# Last_Week_Rank and Days_in_top_10 can be derived
CREATE TABLE Rating (
	Title VARCHAR(50) NOT NULL,
    Date_As_Of Varchar(50), # will change to date format later
    Rank_As_Of INT DEFAULT 0,
    Last_Week_Rank INT DEFAULT 0,
    YTD_Rank INT DEFAULT 0,
    Days_in_top_10 INT DEFAULT 0,
    FOREIGN KEY (Title, Date_As_Of) 
    REFERENCES Production (Title, Date_As_Of)
);

CREATE TABLE TV_show (
	Title VARCHAR(50) NOT NULL,
    Date_As_Of VARCHAR(50), # will change to date format later
    FOREIGN KEY (Title, Date_As_Of) 
    REFERENCES Production (Title, Date_As_Of)
);

CREATE TABLE Movie (
	Title VARCHAR(50) NOT NULL,
    Date_As_Of VARCHAR(50), # will change to date format later
    FOREIGN KEY (Title, Date_As_Of) 
    REFERENCES Production (Title, Date_As_Of)
);

CREATE TABLE Comedy (
	Title VARCHAR(50) NOT NULL,
    Date_As_Of VARCHAR(50), # will change to date format later
    FOREIGN KEY (Title, Date_As_Of) 
    REFERENCES Production (Title, Date_As_Of)
);

CREATE TABLE Concert_Performance (
	Title VARCHAR(50) NOT NULL,
    Date_As_Of VARCHAR(50), # will change to date format later
    FOREIGN KEY (Title, Date_As_Of) 
    REFERENCES Production (Title, Date_As_Of)
);

# Switch the dates from varchar to date format
UPDATE Production SET Release_Date = STR_TO_DATE(Release_Date, '%m-%d-%Y');
UPDATE Production SET Date_As_Of = STR_TO_DATE(Date_As_Of, '%m-%d-%Y');
UPDATE Rating SET Date_As_Of = STR_TO_DATE(Date_As_Of, '%m-%d-%Y');
UPDATE TV_show SET Date_As_Of = STR_TO_DATE(Date_As_Of, '%m-%d-%Y');
UPDATE Movie SET Date_As_Of = STR_TO_DATE(Date_As_Of, '%m-%d-%Y');
UPDATE Comedy SET Date_As_Of = STR_TO_DATE(Date_As_Of, '%m-%d-%Y');
UPDATE Concert_Performance SET Date_As_Of = STR_TO_DATE(Date_As_Of, '%m-%d-%Y');

# Update from varchar to binary (0/1)
Update Production SET Netflix_Exclusive =  
CASE 
	WHEN Netflix_Exclusive = 'Yes' THEN 1
    ELSE 0
END;

# After transforming data in Excel to set "-" values to "0" 
# in rank_as_of YTD_rank and Last_Week_Rank