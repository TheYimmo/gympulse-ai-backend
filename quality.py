import pandas as pd
import json

df = pd.read_csv("clean_gym_data.csv")

reporte = {
    "total_registros": int(len(df)),
    "valores_nulos_por_columna": df.isnull().sum().to_dict(),
    "resumen_estadistico": df.describe().to_dict()
}

with open("reporte_calidad_scrum9.json", "w") as f:
    json.dump(reporte, f, indent=4)

print("Éxito: reporte_calidad_scrum9.json generado al 100%.")