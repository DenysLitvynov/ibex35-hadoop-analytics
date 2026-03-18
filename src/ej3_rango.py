"""
Autor: Denys Litvynov Lymanets
Fecha: 2026-03-17
Descripción:
Dado el nombre de una acción y un rango de fechas, obtener su valor
mínimo y máximo de cotización, así como el porcentaje de decremento
y de incremento desde el valor inicial hasta el mínimo y máximo, respectivamente.
"""

from mrjob.job import MRJob
from datetime import datetime, timedelta

class Rango(MRJob):

    def configure_args(self):
        super(Rango, self).configure_args()
        self.add_passthru_arg('--accion', help='Nombre de la acción a analizar')
        self.add_passthru_arg('--fecha-inicio', help='Fecha de inicio del rango (formato YYYY-MM-DD)')
        self.add_passthru_arg('--fecha-fin', help='Fecha de fin del rango (formato YYYY-MM-DD)')

    def mapper_init(self):
        # Convertir las fechas de inicio y fin a objetos datetime para comparaciones posteriores
        self.options.fecha_inicio = datetime.strptime(self.options.fecha_inicio, '%Y-%m-%d')
        self.options.fecha_fin = datetime.strptime(self.options.fecha_fin, '%Y-%m-%d')

    # Filtramos por fecha y nombre de la acción, y obtenemos el valor de cada fila
    def mapper(self, _, line):
        if line.startswith('empresa'):
            return
        filas = line.split(',')
        accion = filas[0]
        fecha_fichero = datetime.strptime(filas[1], '%Y-%m-%d')
        if (accion == self.options.accion 
            and self.options.fecha_inicio <= fecha_fichero <= self.options.fecha_fin):
            yield accion, (fecha_fichero.strftime('%Y-%m-%d'), 
                           float(filas[2]), float(filas[5]), float(filas[6]))

    # Calcular el minimo, el maximo, el decremento y el incremento de la empresa en el rango de fechas
    def reducer(self, accion, valores):
        valores_ordenados = sorted(valores, key=lambda x: datetime.strptime(x[0], '%Y-%m-%d'))
        valor_inicial = valores_ordenados[0][1]
        valor_maximo = max(v[2] for v in valores_ordenados)
        valor_minimo = min(v[3] for v in valores_ordenados)
        # Dejamos solo 2 decimales en el porcentaje de incremento y decremento
        incremento = round(((valor_maximo - valor_inicial) / valor_inicial) * 100, 2)
        decremento = round(((valor_inicial - valor_minimo) / valor_inicial) * 100, 2)
        # Formatear la salida como string con etiquetas para cada valor
        resultado = f"Valor minimo: {valor_minimo}, Valor maximo: {valor_maximo}, Decremento: {decremento}%, Incremento: {incremento}%"
        yield accion, resultado
        

if __name__ == '__main__': 
    Rango.run()