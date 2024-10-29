import sqlite3
import pandas as pd

# Leer el archivo de Excel
excel_path = 'my_data.xlsx'
df = pd.read_excel(excel_path)

# Conectar a la base de datos SQLite
conn = sqlite3.connect("mi_base_de_datos.db")
cursor = conn.cursor()

# Verificar si las columnas del DataFrame coinciden con las columnas de la tabla
expected_columns = {'Documento', 'Nombre', 'Calidad', 'Categoria'}
if set(df.columns) != expected_columns:
    raise ValueError("Las columnas del archivo no coinciden con las esperadas: Documento, Nombre, Calidad, Categoria")

# Insertar cada fila en la tabla
for _, row in df.iterrows():
    cursor.execute("""
    INSERT OR IGNORE INTO documentos (documento, nombre, calidad, categoria)
    VALUES (?, ?, ?, ?)
    """, (row['Documento'], row['Nombre'], row['Calidad'], row['Categoria']))

conn.commit()
conn.close()
print("Datos cargados exitosamente en la tabla.")
