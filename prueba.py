from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
DATABASE_URL = 'mysql+pymysql://root:uYloZwwZtRjjWHgFOaXXzuBsDfVjvJiL@mysql-copy.railway.internal:3306/railway'
engine = create_engine(DATABASE_URL, echo=True)  

try:
    with engine.connect() as connection:
        print("Conexión exitosa")
except OperationalError as e:
    print(f"Error de conexión: {e}")
    
    
