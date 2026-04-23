import os
import pandas as pd
import math
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
data = pd.read_csv(os.path.join(BASE_DIR, "flights_final.csv"))

class Grafo:
    def __init__(self):
        # - adyacencia: guarda las conexiones (aristas) entre aeropuertos
        # - aeropuertos: guarda la información de cada aeropuerto (vértice)
        self.adyacencia = {}   # { "BOG": [("MIA", 2789.5), ("JFK", 4153.2)], ... }
        self.aeropuertos = {}  # { "BOG": {"nombre": ..., "ciudad": ..., ...}, ... }

    def agregar_vertice(self, codigo, info):
        """
        Agrega un aeropuerto (vértice) al grafo si aún no existe.
        - codigo: string con el código del aeropuerto, ej: "BOG"
        - info: diccionario con nombre, ciudad, país, latitud y longitud
        """
        if codigo not in self.adyacencia:
            self.adyacencia[codigo] = []    # lista vacía de vecinos
            self.aeropuertos[codigo] = info # guarda la info del aeropuerto

    def agregar_arista(self, origen, destino, peso):
        # Revisamos si el destino ya está en la lista de vecinos de origen
        ya_existe = False
        for vecino, _ in self.adyacencia[origen]:
            if vecino == destino:
                ya_existe = True
                break

        # Si no existe, agregamos la arista en ambas direcciones
        if not ya_existe:
            self.adyacencia[origen].append((destino, peso))  # BOG → MIA
            self.adyacencia[destino].append((origen, peso))  # MIA → BOG


def calcular_distancia(lat1, lon1, lat2, lon2):
        """
        Calcula la distancia en km entre dos puntos geográficos
        usando la fórmula de Haversine.
        - lat1, lon1: coordenadas del aeropuerto origen
        - lat2, lon2: coordenadas del aeropuerto destino
        """
        radio_tierra = 6371  # km

        # Convertir grados a radianes
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)

        # Diferencias de coordenadas
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Fórmula Haversine
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.asin(math.sqrt(a))

        return radio_tierra * c
    
def construir_grafo(data):
    """
    Lee el dataset y construye el grafo de aeropuertos.
    - data: el dataframe de pandas con los datos del CSV
    """
    g = Grafo()

    for _, fila in data.iterrows():

        # Datos del aeropuerto origen
        codigo_origen = fila["Source Airport Code"]
        info_origen = {
            "nombre": fila["Source Airport Name"],
            "ciudad": fila["Source Airport City"],
            "pais":   fila["Source Airport Country"],
            "lat":    fila["Source Airport Latitude"],
            "lon":    fila["Source Airport Longitude"]
        }

        # Datos del aeropuerto destino
        codigo_destino = fila["Destination Airport Code"]
        info_destino = {
            "nombre": fila["Destination Airport Name"],
            "ciudad": fila["Destination Airport City"],
            "pais":   fila["Destination Airport Country"],
            "lat":    fila["Destination Airport Latitude"],
            "lon":    fila["Destination Airport Longitude"]
        }

        # Agregar los dos vértices
        g.agregar_vertice(codigo_origen, info_origen)
        g.agregar_vertice(codigo_destino, info_destino)

        # Calcular distancia y agregar la arista
        distancia = calcular_distancia(info_origen["lat"], info_origen["lon"], info_destino["lat"], info_destino["lon"])
        g.agregar_arista(codigo_origen, codigo_destino, distancia)

    return g

#toco separarlo por que esto se usa en el punto 3
def encontrar_componentes(g):
    visitados = {}
    componentes = []
    #como lo de queue que hizo el profe
    for inicio in g.adyacencia:
        if inicio in visitados:
            continue
        #si esta en visitados entonces se ignora y continua al while por que son no dirigidos 
        #se crea una lista de componente que es una lista de los nodos del componente, la cola y se le añade ese nodo a visitados
        componente = []
        cola = [inicio]
        visitados[inicio] = True
        while cola:
            #se revisa el primero que sale de la cola y se añade a la lista de ese componente
            actual = cola.pop(0)
            componente.append(actual)
            #para revisar tuplas tienes o que hacer el for de la posicion de la tupla y despues asignar a una variable cada elemento de la tupla 
            #o haces esto que _ supuestamente ignora el otro elemento de la tupla y ya
            ##si el vecino no esta en visitados entonces se le añade a visitados y a la cola para revisar los vecino de ese
            for vecino, _ in g.adyacencia[actual]:
                if vecino not in visitados:
                    visitados[vecino] = True
                    cola.append(vecino)
        #si termina la iteracion es por que ya se encontaron los nodos de ese componente
        #por como es la matriz de adyacencia de este codigo la si recorro la lista de vecinos de un nodo y los vecinos de esos eventualmente recorro todo el grafo
        #o recorro un conjunto disjunto de elementos si no recorro todos los nodos
        componentes.append(componente)

    return componentes

def Es_Bipartito(g, componentes):
    #mas de lo mismo que en componentes pero ahora hacendo BFS parecido al que hizo el profe
    #asumo que el primero es el mayor y reviso la longitud de la lista nada mas para ver cual es el mayor
    componente_grande = componentes[0]
    for componente in componentes:
        if len(componente) > len(componente_grande):
            componente_grande = componente
    #cuando encuentra el mayor entonces hago un dict por que son goated por lo de identificacion
    #coloreo (asigno 1 o 0) el primer nodo del componente mas grande y asumo que es bipartito
    color = {}
    color[componente_grande[0]] = 0
    cola = [componente_grande[0]]
    bipartita = True
    #igual al de componentes metiendo en una cola el actual nodo del componente y reviso sus vecinos 
    ##pero esta vez se revisa si no esta en color y se le asigna un numero distinto al del anterior nodo y se añade a la cola 
    ##si ya ese vecino esta en color es porque hay un ciclo impar en ese componente y no es bipartito
    while cola:
        actual = cola.pop(0)
        for vecino, _ in g.adyacencia[actual]:
            if vecino not in color:
                color[vecino] = 1 - color[actual]
                cola.append(vecino)
            elif color[vecino] == color[actual]:
                bipartita = False

    if bipartita:
        print("La componente más grande ES bipartita.")
    else:
        print("La componente más grande NO es bipartita.")
    return bipartita