"""
Autor: Denys Litvynov Lymanets
Fecha: 2026-03-18
Descripción:
Analizar qué sector del IBEX ha rendido mejor en el último año,
cruzando el sector de cada empresa con su revalorización anual.
"""

from mrjob.job import MRJob
from mrjob.step import MRStep

class RendimientoPorSector(MRJob):

    def steps(self):
        return [
            MRStep(mapper=self.mapper,
                   reducer=self.reducer),
            MRStep(mapper=self.mapper_sector,
                   reducer=self.reducer_sector)
        ]

    # Identifica si la línea es cotización o fundamental y extrae precio o sector
    def mapper(self, _, line):
        if line.startswith('empresa'):
            return
        filas = line.split(',')
        if len(filas[1]) == 10 and filas[1][4] == '-':
            yield filas[0], ('cotizaciones', filas[1], float(filas[2]))
        else:
            sector = filas[1]
            if sector and sector != 'N/A':
                yield filas[0], ('fundamentales', sector)

    # Cruza los datos de una empresa para calcular su revalorización anual y emite su sector
    def reducer(self, empresa, valores):
        precios = []
        sector = None
        for value in valores:
            if value[0] == 'cotizaciones':
                precios.append((value[1], value[2]))
            elif value[0] == 'fundamentales':
                sector = value[1]

        if sector is None or len(precios) == 0:
            return

        precios_ordenados = sorted(precios, key=lambda x: x[0])
        precio_inicial = precios_ordenados[0][1]
        precio_final = precios_ordenados[-1][1]

        if precio_inicial <= 0:
            return

        revalorizacion = round(((precio_final - precio_inicial) / precio_inicial) * 100, 2)
        yield sector, revalorizacion

    # Pasa la revalorización recibida usando el sector como nueva clave de agrupación
    def mapper_sector(self, sector, revalorizacion):
        yield sector, revalorizacion

    # Calcula la media aritmética de las revalorizaciones de todas las empresas de un mismo sector
    def reducer_sector(self, sector, revalorizaciones):
        lista = list(revalorizaciones)
        media = round(sum(lista) / len(lista), 2)
        num_empresas = len(lista)
        yield sector, {
            "Media revalorizacion": str(media) + "%",
            "Num empresas": num_empresas
        }

if __name__ == '__main__':
    RendimientoPorSector.run()