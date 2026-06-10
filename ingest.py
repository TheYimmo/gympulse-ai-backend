import pandas as pd
from sqlalchemy import create_engine

# 1. PEGA AQUÍ TU URL EXTERNA DE RENDER
# Debe empezar con postgresql:// en lugar de postgres://
DB_URL = "postgresql://usuario:password@host.render.com/gympulse_db"

def cargar_datos():
    print("Iniciando extracción del CSV...")
    try:
        # 2. Leer tu archivo exacto
        df = pd.read_csv("clean_gym_data.csv")
        
        # 3. Conectar a PostgreSQL en la nube
        print("Conectando a la base de datos de producción...")
        engine = create_engine(DB_URL)
        
        # 4. Carga de datos (ETL)
        # Usamos if_exists='append' para no borrar la tabla creada por main.py
        # index=False asegura que no metamos la columna de índice de pandas a la BD
        df.to_sql('gym_metrics', engine, if_exists='append', index=False)
        
        print(f"Éxito: Se insertaron {len(df)} registros correctamente (100% de la carga).")
        
    except Exception as e:
        print(f"Error crítico en la ingesta: {e}")

if __name__ == "__main__":
    cargar_datos()