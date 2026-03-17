"""
Autor: Denys Litvynov Lymanets
Fecha: 2026-03-17
Descripción:
Dado el nombre de una acción, recuperar su valor mínimo y máximo
de cotización de la última hora, semana y mes.
"""

from mrjob.job import MRJob
from datetime import datetime, timedelta

class MinMaxPeriodos(MRJob):

    def configure_args(self):
        super().configure_args()
        self.add_passthru_arg('--accion', help='Nombre de la acción a analizar')
        self.add_passthru_arg('--fecha', help='Fecha de referencia para el análisis (formato YYYY-MM-DD)') 
    
    def mapper_init(self):
        # Convertir la fecha de referencia a un objeto datetime para comparaciones posteriores
        self.options.fecha = datetime.strptime(self.options.fecha, '%Y-%m-%d')
    
    # Comprobamos por la fecha de la fila si pertenece a la última hora, semana o mes, y emitimos con distintas etiquetas 
    def mapper(self, _, line):
        if line.startswith('empresa'):
            return
        filas = line.split(',')
        accion = filas[0]
        fecha_fichero = datetime.strptime(filas[1], '%Y-%m-%d')
        if accion == self.options.accion:
            if fecha_fichero >= self.options.fecha - timedelta(hours=1):
                yield filas[0], ('dia', filas[5], filas[6])
            if fecha_fichero >= self.options.fecha - timedelta(days=7):
                yield filas[0], ('semana', filas[5], filas[6])
            if fecha_fichero >= self.options.fecha - timedelta(days=30):
                yield filas[0], ('mes', filas[5], filas[6])

    # Función auxiliar fuera del reducer para calcular el mínimo y máximo 
    # de una lista de valores
    @staticmethod
    def min_max(lst):
        """Devuelve el mínimo y máximo de una lista de tuplas (periodo, max_val, min_val) de forma segura."""
        if lst:
            min_val = min(float(v[2]) for v in lst)
            max_val = max(float(v[1]) for v in lst)
            return min_val, max_val
        else:
            return None, None  

    # Calculamos el mínimo y máximo para cada periodo (día, semana, mes)
    def reducer(self, accion, valores):
        valores = list(valores)

        # Filtramos los valores por periodo
        dia = [v for v in valores if v[0] == 'dia']
        semana = [v for v in valores if v[0] == 'semana']
        mes = [v for v in valores if v[0] == 'mes']

        # Calculamos el mínimo y máximo para cada periodo utilizando la función auxiliar
        min_dia, max_dia = self.min_max(dia)
        min_semana, max_semana = self.min_max(semana)
        min_mes, max_mes = self.min_max(mes)

        yield accion, {
            'ultima_hora': {'min': min_dia, 'max': max_dia},
            'ultima_semana': {'min': min_semana, 'max': max_semana},
            'ultimo_mes': {'min': min_mes, 'max': max_mes}
        }

if __name__ == '__main__':
    MinMaxPeriodos.run()
