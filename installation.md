### Clone the repository
   ```terminal
   git clone https://github.com/Jobdaiyoung/ku-polls.git
   ```
   
### Change directory to the project directory
   ```terminal
   cd ku-polls
   ```

### Create virtual environment
   ```terminal
   python -m venv venv
   ```

### Activate virtual environment

* MacOS/Linux:
   ```terminal
   . venv/bin/activate
   ```
* Windows:
   ```terminal
   .venv\Scripts\activate.bat
   ```

### Install the required packages
   ```terminal
   pip install -r requirements.txt
   ```

### Create a file named `.env` using sample.env
   ```terminal
   cp sample.env .env
   ```

### Run migration
   ```terminal
   python manage.py migrate
   ```

### Load initial data
   ```terminal
   python manage.py loaddata data/polls-v2.json 
   python manage.py loaddata data/users.json
   ```

### Run server
   ```terminal
   python manage.py runserver
   ```