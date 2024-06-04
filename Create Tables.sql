# After transforming data in Excel to set "-" values to "0" 
# in rank_as_of YTD_rank and Last_Week_Rank

# CREATE SCHEMA Netflix
USE netflix;

CREATE TABLE Production (
	Title VARCHAR(50) NOT NULL,
    Release_Date Varchar(50), # will change to date format later
    Netflix_Exclusive Varchar(3), # for yes/no (updated format to bit later)
    Type Varchar(20), # this will be dropped later, 
    # Purpose of Type: Assigning values to 4 attributes below, then remove
    Is_TV BIT,
    Is_Movie BIT,
    Is_Comedy BIT,
    Is_Performance BIT,
    PRIMARY KEY(Title)
);


# Last_Week_Rank and Days_in_top_10 can be derived
CREATE TABLE Rating (
	Title VARCHAR(50) NOT NULL,
    Date_As_Of Varchar(50), # will change to date format later
    Rank_As_Of INT DEFAULT 0,
    Last_Week_Rank INT DEFAULT 0,
    YTD_Rank INT DEFAULT 0,
    Days_in_top_10 INT DEFAULT 0,
    Viewership_Score INT,
    PRIMARY KEY (Title, Date_As_Of),
    FOREIGN KEY (Title) 
    REFERENCES Production (Title)
);

# Run the commands below separately

# Switch the dates from varchar to date format
# Might need to do SET SQL_SAFE_UPDATES = 0;
UPDATE Production SET Release_Date = STR_TO_DATE(Release_Date, '%m-%d-%Y');
UPDATE Rating SET Date_As_Of = STR_TO_DATE(Date_As_Of, '%m-%d-%Y');

# Update Netflix_Exclusive from Varchar to Binary (0/1)
Update Production SET Netflix_Exclusive =  
CASE 
	WHEN Netflix_Exclusive = 'Yes' THEN 1
    ELSE 0
END;


Update Production SET Is_TV =  
CASE 
	WHEN Type = 'TV Show' THEN 1
    ELSE 0
END;

Update Production SET Is_Movie =  
CASE 
	WHEN Type = 'Movie' THEN 1
    ELSE 0
END;

Update Production SET Is_Comedy =  
CASE 
	WHEN Type = 'Stand-Up Comedy' THEN 1
    ELSE 0
END;

Update Production SET Is_Performance =  
CASE 
	WHEN Type = 'Concert/Performance' THEN 1
    ELSE 0
END;

# Remove Type from the Production Table
Alter Table Production Drop Column Type;