import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_name = os.getenv('DB_NAME')


engine = create_engine(
    f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}/{db_name}",
    echo = False
)

session = sessionmaker(engine, expire_on_commit=False)
