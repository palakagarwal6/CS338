# CS338 - Group 18 

Through this project, we are aiming to work with a sample database to simulate the MovieLens dataset using MySQL on the school server. The database contains data on the movies released on or before July 2017. Users will be able to query, add, delete, and modify data through a Python-based command-line interface (CLI).

# Dependencies

In order to use this project effectively, the user must have:
1. MySQL Server 8.4 installed (THIS APPLICATION WILL NOT WORK WITH VERSIONS OTHER THAN 8.4)
2. Any version of Python 3 installed on their machine
 a. the environmental variables for python and its scripts properly configured (when installing python, there is an option to add python to PATH. This is 100% necessary) 
3. The following modules. These can be installed via a script in `main.bat`, or you can use the pip command.
 a. mysql-connector-python
 b. getpass
 c. tabulate

# Usage
Simply copy this repository and run `main.bat`

This will prompt you to:
- connect to your mysql database, assuming your server host is `localhost`
- allow you to choose create the movie schema (if not already created)
- create necessary tables
- load data from `CS338-main\tables`
- prompt you to a simple search title search function

![image](https://github.com/palakagarwal6/CS338/assets/170012515/72c1e590-35e4-4bda-8a91-f523cc2c9865)
