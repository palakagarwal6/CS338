# CS338 - Group 18 

Through this project, we are aiming to work with a sample database to simulate the Netflix daily top 10 dataset using MySQL on the school server. The database in file "netflix daily top .csv" contains data on the top movies and TV shows in the United States during the COVID-19 pandemic, from April 2020 - March 2022. Users will be able to query, add, and modify data through a Python-based command-line interface (CLI).

# Dependencies

In order to use this project effectively, the user must have:
1. MySQL installed locally
2. Any version of Python 3 installed on their machine
3. MySQL connector installed with Python -> use command pip `install mysql-connector-python`
4. Pandas library installed for Python -> use command `pip install pandas`
5. and IDE that can run `main.py`. `Main.py` was personally tested with VS Code and Sublime


# Usage
Simply copy this repository and run `main.py` with your IDE of choice. As mentioned, script was personally tested with VS Code and Sublime

This will prompt you to:
- connect to your mysql database, assuming your server host is `localhost`
- create the netflix schema
- create production and rating tables
- load data from `netflix_daily_top.csv` into tables and configure data correctly
- prompt you to a simple search title search function

![image](https://github.com/palakagarwal6/CS338/assets/170012515/3cfcb244-6c30-40be-b7e9-460110345f38)
