from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time

options = Options()
options.add_argument("--headless")

start_url = "https://www.expansion.com/mercados/cotizaciones/indices/ibex35_I.IB.html"

with webdriver.Firefox(options=options) as driver:
    driver.get(start_url)
    time.sleep(10) # Esperamos a que la web cargue los datos

    # Buscamos las filas de la tabla de cotizaciones
    rows = driver.find_elements_by_xpath("//table//tr")

    for row in rows:
        # Buscamos todas las celdas (pueden ser td o th)
        cells = row.find_elements_by_xpath(".//*[self::td or self::th]")
        data = [c.get_attribute('textContent').strip() for c in cells]
        
        # Si la fila tiene suficientes columnas (al menos 8)
        if len(data) >= 8:
            try:
                # 1. Nombre (Primer valor)
                nombre = data[0]
                # 2. Ultima (Segundo valor)
                ultima = data[1].replace('.','').replace(',','.')
                # 3. Maximo (Sexto valor -> Indice 5)
                maximo = data[5].replace('.','').replace(',','.')
                # 4. Minimo (Septimo valor -> Indice 6)
                minimo = data[6].replace('.','').replace(',','.')
                # 5. Fecha/Hora (El ultimo valor de la fila)
                fecha_hora = data[-1]

                # Si el nombre no es vacio, lo imprimimos
                if nombre:
                    print(f"{nombre},{ultima},{maximo},{minimo},{fecha_hora}")
            except:
                continue

