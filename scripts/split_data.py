import pandas as pd
import shutil
import os
cwd = os.getcwd()

sqlpath = 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads'

# Load the CSV file into a DataFrame
data = pd.read_csv('netflix_daily_top.csv')

# Define the columns for each table
prod_columns = ['Title', 'Release_Date', 'Netflix_Exclusive', 'Type']  # example columns for movies table
ratings_columns = ['Title', 'Date_As_Of', 'Rank_As_Of', 'Last_Week_Rank', 'YTD_Rank', 'Days_in_top_10', 'Viewership_Score']  # example columns for ratings table

# Create the DataFrames for each table
movies_df = data[prod_columns].drop_duplicates(subset=['Title'])
#movies_df = data[prod_columns]
ratings_df = data[ratings_columns].drop_duplicates(subset=['Title'])

#movies_df = data[prod_columns]
#ratings_df = data[ratings_columns]


# movies Is_x filling

movies_df['Is_TV'] = (movies_df['Type'] == "TV Show").astype(int)
movies_df['Is_Movie'] = (movies_df['Type'] == "Movie").astype(int)
movies_df['Is_Comedy'] = (movies_df['Type'] == "Stand-Up Comedy").astype(int)
movies_df['Is_Performance'] = (movies_df['Type'] == "Concert").astype(int)


# convert netflix exclusive to bit
movies_df['Netflix_Exclusive'] = (movies_df['Netflix_Exclusive'] == "Yes").astype(int)

movies_df = movies_df.drop('Type', axis=1)

# Save each DataFrame to a separate CSV file
movies_df.to_csv('prod.csv', index=False)
ratings_df.to_csv('ratings.csv', index=False)

prod_src = cwd + "\\prod.csv"
ratings_src = cwd + "\\ratings.csv"

prod_des = sqlpath + "\\prod.csv"
ratings_des = sqlpath + "\\ratings.csv"

shutil.move(prod_src, prod_des)
shutil.move(ratings_src, ratings_des)