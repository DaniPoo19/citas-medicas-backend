from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
DATABASE_URL = 'mysql+pymysql://root:uYloZwwZtRjjWHgFOaXXzuBsDfVjvJiL@autorack.proxy.rlwy.net:23579/railway'
engine = create_engine(DATABASE_URL, echo=True)  

try:
    with engine.connect() as connection:
        print("Conexión exitosa")
except OperationalError as e:
    print(f"Error de conexión: {e}")

