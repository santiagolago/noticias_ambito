import pandas as pd

# Ruta al CSV exportado por Scrapy
csv_path = "ambito_test_10_paginas.csv"

# Leer el CSV como DataFrame
# - encoding='utf-8-sig' corrige tildes/ñ en Excel/Windows
# - sep=';' usar solo si exportaste con delimitador punto y coma
df = pd.read_csv(
    csv_path,
    encoding="utf-8-sig",
    sep=",",          # cambiá a ';' si usaste FEED_EXPORT_DELIMITER=";"
    quotechar='"',    # respeta comillas para textos con comas
)

# Chequeos rápidos
print(df.head())
print(df.info())
