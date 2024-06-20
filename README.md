# CS338 - Group 18 

Through this project, we are aiming to work with a sample database to simulate the Netflix daily top 10 dataset using MySQL on the school server. The database in file "netflix daily top .csv" contains data on the top movies and TV shows in the United States during the COVID-19 pandemic, from April 2020 - March 2022. Users will be able to query, add, and modify data through a Python-based command-line interface (CLI).

# Dependencies

In order to use this project effectively, the user must have:
1. MySQL installed locally
2. Any version of Python 3 installed on their machine
3. The following modules. These can be installed via a script in `main.bat`
 a. mysql-connector-python
 b. getpass
 c. tabulate

# Usage
Simply copy this repository and run `main.bat`

This will prompt you to:
- connect to your mysql database, assuming your server host is `localhost`
- allow you to choose create the netflix schema (if not already created)
- create necessary tables
- load data from `CS338-main\tables`
- prompt you to a simple search title search function

![image](https://github.com/palakagarwal6/CS338/assets/170012515/72c1e590-35e4-4bda-8a91-f523cc2c9865)
