"""
Autor: Denys Litvynov Lymanets
Fecha: 2026-03-17
Descripción:
Dado un porcentaje y un rango de fechas, mostrar las acciones
que han tenido un incremento de este porcentaje  
durante dicho período.
"""

from mrjob.job import MRJob
from mrjob.step import MRStep
from datetime import datetime, timedelta

class PorcentajeIncremento(MRJob):

    def configure_args(self):
        super().configure_args()
        self.add_passthru_arg('--fecha-inicio', help='Fecha de inicio del período (formato YYYY-MM-DD)')
        self.add_passthru_arg('--fecha-fin', help='Fecha de fin del período (formato YYYY-MM-DD)')
        self.add_passthru_arg('--porcentaje', help='Porcentaje de incremento (formato 0-100)')

    # Necesitamos definir dos steps para ordenar las empresas por el % de crecimiento
    def steps(self):
        return [
            MRStep(mapper_init = self.mapper_init,
                   mapper = self.mapper,
                   reducer = self.reducer),
            MRStep(mapper = self.mapper_ordenado, 
                   reducer = self.reducer_ordenado)
        ] 
 
    def mapper_init(self):
        self.fecha_inicio = datetime.strptime(self.options.fecha_inicio, '%Y-%m-%d')
        self.fecha_fin = datetime.strptime(self.options.fecha_fin, '%Y-%m-%d')

    # Para cada empresa devolvemos su valor en la fecha de inicio y en la fecha de fin 
    def mapper(self, _, line):
        if line.startswith('empresa'):
            return
        filas = line.split(',')
        fecha_fichero = datetime.strptime(filas[1], '%Y-%m-%d')
        if self.fecha_inicio <= fecha_fichero <= self.fecha_inicio + timedelta(days=4):
            yield filas[0], ('inicio', filas[1], float(filas[2]))
        elif self.fecha_fin - timedelta(days=4) <= fecha_fichero <= self.fecha_fin:
            yield filas[0], ('fin',filas[1], float(filas[2]))
    
    # Calculamos el porcentaje de incremento para cada empresa
    # Si el porcentaje de incremento es mayor o igual al especificado, emitimos la empresa con su porcentaje
    def reducer(self, accion, valores):
        inicio = fin = None
        inicio_fecha = fin_fecha = datetime.min

        # Asignamos los valores de inicio y fin según la etiqueta
        for etiqueta, fecha, valor in valores:
            fecha_dt = datetime.strptime(fecha, '%Y-%m-%d')
            if etiqueta == 'inicio' and fecha_dt > inicio_fecha:
                inicio = valor
                inicio_fecha = fecha_dt
            elif etiqueta == 'fin' and fecha_dt > fin_fecha:
                fin = valor
                fin_fecha = fecha_dt

        # Calculamos el porcentaje de incremento si ambos valores están disponibles 
        if inicio is not None and fin is not None:
            incremento = round(((fin - inicio) / inicio) * 100, 2)
            if incremento >= float(self.options.porcentaje):
                yield accion, incremento

    # Segundo step para ordenar. Hadoop ordena automáticamente por clave
    def mapper_ordenado(self, accion, incremento):
        yield 'resultado', (accion, incremento)

    # Ordenamos las empresas segun el % de crecimiento de menor a mayor
    def reducer_ordenado(self, _, valores):
        ordenados = sorted(valores, key=lambda x: x[1]) 
        for accion, incremento in ordenados:
            yield accion, f"{incremento}"


if __name__ == '__main__':
    PorcentajeIncremento.run()