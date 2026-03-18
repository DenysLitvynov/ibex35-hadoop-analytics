"""
Autor: Denys Litvynov Lymanets
Fecha: 2026-03-17
Descripción:
Mostrar las 5 acciones que más han subido en la última semana
y en el último mes.
"""

from mrjob.job import MRJob
from mrjob.step import MRStep
from datetime import datetime, timedelta

class Top5Subida(MRJob):
    
    def configure_args(self):
        super().configure_args()
        self.add_passthru_arg('--fecha', help='Fecha de referencia para el análisis (formato YYYY-MM-DD)')
    
    def steps(self):
        return [
            MRStep(mapper_init=self.mapper_init,
                   mapper=self.mapper,
                   reducer=self.reducer),
            MRStep(mapper=self.mapper_final,
                   reducer=self.reducer_top5)
        ]
    
    def mapper_init(self):
        self.fecha = datetime.strptime(self.options.fecha, '%Y-%m-%d') 

    # Emitimos la ultima acción general, la primera de la semana y la primera del mes
    # para cada empresa, con etiquetas para cada periodo
    def mapper(self, _, line):
        if line.startswith('empresa'):
            return
        filas = line.split(',')
        accion = filas[0]
        fecha_fichero = datetime.strptime(filas[1], '%Y-%m-%d')
        # Comprobamos si la fecha es la de referencia
        if self.fecha - timedelta(days=4) <= fecha_fichero <= self.fecha:
            yield accion, ('ultima',filas[1], float(filas[2]))
        # Comprobamos si la fecha es la primera de la semana
        if self.fecha - timedelta(days=9) <= fecha_fichero <= self.fecha - timedelta(days=5):
            yield accion, ('semana',filas[1], float(filas[2]))
        # Comprobamos si la fecha es la primera del mes        
        if self.fecha - timedelta(days=32) <= fecha_fichero <= self.fecha - timedelta(days=28):
            yield accion, ('mes',filas[1], float(filas[2]))
    
    # Calculamos el porcentaje de subida para cada periodo (semana y mes) y emitimos con etiqueta
    def reducer(self, accion, valores):

        ultimo = semana = mes = None
        ultimo_fecha = ultimo_semana = ultimo_mes = datetime.min

        # Recorremos los valores por etiqueta para asignar el valor
        #  correspondiente a cada periodo
        for etiqueta,fecha, valor in valores:
            fecha = datetime.strptime(fecha, '%Y-%m-%d')
            if etiqueta == 'ultima' and fecha > ultimo_fecha:
                ultimo = valor
                ultimo_fecha = fecha
            elif etiqueta == 'semana' and fecha > ultimo_semana:
                semana = valor
                ultimo_semana = fecha
            elif etiqueta == 'mes' and fecha > ultimo_mes:
                mes = valor
                ultimo_mes = fecha

        pct_sem = round(((ultimo - semana) / semana) * 100, 2) if semana is not None else None
        pct_mes = round(((ultimo - mes) / mes) * 100, 2) if mes is not None else None
        yield accion, (pct_sem, pct_mes)

    # Dividimos en semana y mes
    def mapper_final(self, accion, pct_sem_mes):
        pct_sem, pct_mes = pct_sem_mes
        if pct_sem is not None and pct_sem > 0:
            yield 'semana', (accion, pct_sem)
        if pct_mes is not None and pct_mes > 0:
            yield 'mes', (accion, pct_mes)

    # Ordenamos y emitimos el top 5 de cada periodo
    def reducer_top5(self, periodo, valores):
        # Formateamos la salida como string con etiquetas para cada valor
        top5 = sorted(valores, key=lambda x: x[1], reverse=True)[:5]
        top5_formateado = [f"{v[0]}: {v[1]}%" for v in top5]
        yield periodo, top5_formateado

if __name__ == '__main__':
    Top5Subida.run()
        