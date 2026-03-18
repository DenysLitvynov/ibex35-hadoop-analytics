"""Autor: Denys Litvynov Lymanets
Fecha: 2026-03-18
Descripción:
Analizar la relación entre la valoración de las empresas (PER) y su volatilidad anual,
calculando para cada acción el porcentaje de variación entre su precio máximo
y mínimo durante el año."""

from mrjob.job import MRJob

class ValoracionPER(MRJob):

    """Dependiendo del fichero entrante, emitimos o el max y min en un dia, 
    o el PER de una empresa """ 
    def mapper(self, _, line):
        if line.startswith('empresa'):
            return
        filas = line.split(',')
        # Comrpobamos si es cotizaciones o fundamentales
        if len(filas[1]) == 10 and filas[1][4] == '-':
            yield filas[0], ('cotizaciones', float(filas[2]))
        else:
            yield filas[0], ('fundamentales', filas[1], float(filas[2]))

    def reducer(self, key, values):
        precios = []
        sector = None
        per = None
        for value in values:
            tipo = value[0]
            if tipo == 'cotizaciones':
                precios.append(value[1])
            elif tipo == 'fundamentales':
                sector = value[1]
                per = value[2]
        if sector != None and per > 0 and per is not None and len(precios) > 0:
            precio_max = max(precios)
            precio_min = min(precios)
            volatilidad = round(((precio_max - precio_min) / precio_min) * 100, 2)
            yield key, ('Sector: ' + sector, 'PER: ' + str(per), 'Volatilidad: ' + str(volatilidad) + '%')

if __name__ == '__main__':
    ValoracionPER.run()