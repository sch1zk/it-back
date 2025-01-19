Для установки всех необходимых зависимостей необходимо выполнить команду

pip install -r requirements.txt

Fill .env file as

DATABASE_URL=postgresql://username:password@localhost/database
SECRET_KEY=your_secret_key
ALGORITHM=your_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES=time_in_minutes