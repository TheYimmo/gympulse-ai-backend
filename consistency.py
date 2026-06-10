import pandas as pd

df = pd.read_csv("clean_gym_data.csv")

# Crea una matriz donde las filas son países y las columnas los años
matriz_cobertura = pd.crosstab(df['country'], df['year'])

matriz_cobertura.to_csv("matriz_consistencia_scrum11.csv")

print("Éxito: matriz_consistencia_scrum11.csv generada al 100%.")