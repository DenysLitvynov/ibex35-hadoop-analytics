"""Autor: Denys Litvynov Lymanets
Fecha: 2026-03-18
Descripción:
Evaluar la relación entre la eficiencia operativa (ROE) y la rentabilidad anual,
calculando para cada acción el porcentaje de revalorización entre el precio inicial
y final del año junto con su ROE."""

from mrjob.job import MRJob

class ROERendimiento(MRJob):

    def mapper(self, _, line):
        if line.startswith('empresa'):
            return
        filas = line.split(',')
        if len(filas[1]) == 10 and filas[1][4] == '-':
            yield filas[0], ('cotizaciones',filas[1], float(filas[2]))
        else:
            try: 
                roe_str = filas[3]
                if roe_str != "":
                    roe = float(roe_str)
                    yield filas[0], ('fundamentales', roe)
            except (ValueError, IndexError):
                pass

    """ Ordenamos los registros de cotizaciones por fecha, 
    obtenemos el primer valor del año y el ultimo valor del año,
    calculamos el porcentaje de revalorización y emitimos con etiquetas para cada valor """
    def reducer(self, key, values):
        precios = []
        roe = None
        for value in values:
            tipo = value[0]
            if tipo == 'cotizaciones':
                precios.append((value[1], value[2]))
            elif tipo == 'fundamentales':
                roe = round(value[1] * 100, 2)
 
        # Solo emitimos si tenemos ROE válido y precios
        if roe is None or roe == 0 or len(precios) == 0:
            return
 
        precios_ordenados = sorted(precios, key=lambda x: x[0])
        precio_inicial = precios_ordenados[0][1]
        precio_final = precios_ordenados[-1][1]
 
        if precio_inicial <= 0:
            return
 
        porcentaje_revalorizacion = round(((precio_final - precio_inicial) / precio_inicial) * 100, 2)
        yield key, ('ROE: ' + str(roe) + '%', 'Revalorizacion: ' + str(porcentaje_revalorizacion) + '%')


if __name__ == '__main__':
    ROERendimiento.run()