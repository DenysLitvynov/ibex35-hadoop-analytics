"""
Autor: Denys Litvynov Lymanets
Fecha: 2026-03-17
Descripción:
Generar un listado semanal (de la semana actual) donde se indique,
para cada acción, su valor inicial, final, mínimo y máximo.
"""

from mrjob.job import MRJob
from datetime import datetime, timedelta

class MRListadoSemanal(MRJob):

    def configure_args(self):
        super(MRListadoSemanal, self).configure_args()
        self.add_passthru_arg('--fecha-referencia', help='Fecha de referencia para la semana (formato YYYY-MM-DD)')

    def mapper_init(self):
        fecha_referencia = datetime.strptime(self.options.fecha_referencia, '%Y-%m-%d')
        dia_semana = fecha_referencia.weekday()
        self.lunes = fecha_referencia - timedelta(days=dia_semana)
        self.domingo = self.lunes + timedelta(days=6)

    """ Mapear por empresa, filtrando por la semana actual y obteniendo 
    el valor de cada fila. """     
    def mapper(self, _, line):
        # Ignorar lineas vacias y encabezados
        if not line.strip() or line.startswith('empresa'):
            return
        filas = line.split(',')

        # Verificar que la fecha del fichero esta dentro de la semana
        fecha_fichero = datetime.strptime(filas[1], '%Y-%m-%d')
        if self.lunes <= fecha_fichero <= self.domingo: 
            yield filas[0], (fecha_fichero.strftime('%Y-%m-%d'), float(filas[2]), float(filas[5]), float(filas[6]))
    
    """ Reducir por empresa, ordenando los valores por fecha y 
    obteniendo el valor inicial, final, mínimo y máximo. """
    def reducer(self, empresa, valores):
        # Ordenar los valores por fecha
        valores_ordenados = sorted(valores, key=lambda x: datetime.strptime(x[0], '%Y-%m-%d'))
        valor_inicial = valores_ordenados[0][1]
        valor_final = valores_ordenados[-1][1]
        # Obtener el max y el min de los ordenados
        valor_maximo = max(v[2] for v in valores_ordenados)
        valor_minimo = min(v[3] for v in valores_ordenados)
        # Añadimos etiquetas a cada valor en un string
        resultado = f"Valor inicial: {valor_inicial}, Valor final: {valor_final}, Valor maximo: {valor_maximo}, Valor minimo: {valor_minimo}"
        yield empresa, resultado

    
if __name__ == '__main__':
    MRListadoSemanal.run()
