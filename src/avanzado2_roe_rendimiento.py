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
            yield filas[0], ('fundamentales', float(filas[3]))

    """ Ordenamos los registros de cotizaciones por fecha, 
    obtenemos el primer valor del año y el ultimo valor del año,
    calculamos el porcentaje de revalorización y emitimos con etiquetas para cada valor """
    def reducer(self, key, values):
        precios = []
        roe = None
        for value in values:
            tipo = value[0]
            if tipo == 'cotizaciones':
                precios.append(value[2])
            elif tipo == 'fundamentales':
                # Convertimos el ROE a porcentaje
                roe = round(value[1] * 100, 2)
        if roe > 0 and roe is not None and len(precios) > 0:
            precio_inicial = precios[0]
            precio_final = precios[-1]
            porcentaje_revalorizacion = round(((precio_final - precio_inicial) / precio_inicial) * 100, 2)
            yield key, ('ROE: ' + str(roe) + '%', 'Porcentaje de revalorizacion: ' + str(porcentaje_revalorizacion) + '%')
        else:
            yield key, ('ROE: ' + str(roe) + '%', 'Porcentaje de revalorizacion: 0%')


if __name__ == '__main__':
    ROERendimiento.run()