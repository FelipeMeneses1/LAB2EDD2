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

def Es_Bipartito(g):
    #crear el dict de color y la lista de componentes 
    #dict por que son re goated y puedes darles identificaciones
    color = {}
    componentes = []  # cada entrada: (tamaño, es_bipartito)

    for inicio in g.adyacencia:
        if inicio in color: 
            continue

        #si no esta en la lista entonces se le asigna 
        #como que [] es para listas y acceder a un dict 
        color[inicio] = 0 
        #se crea el queue para poder revisar los vecinos de ese primer dato
        #tambien se crea el tamaño para la lista de componentes 
        cola = [inicio] 
        tamaño = 0
        bipartita = True
        #casi que igual a la que hizo el profe pero con las condiciones necesarias
        while cola:
            #actual es la primera que sale del queue y a ese se le revisan sus vecinos
            actual = cola.pop(0)
            tamaño += 1
            #en un dict como tienes varios datos asignados a una sola clave entonces puedes acceder independientemente a ellos
            #se le asigna posteriormente una variable a la posicion del dato de la tupla que quieres revisar o supuestamente puedes hacer esto donde _ es ignorar el valor
            ##si el vecino no esta en la lista de coloreados entonces se le asigna un valor entre 1 y 0 y se añade a la cola para posteriormente revisar los vecinos de ese
            ##sino entonces ya esta coloreado y si ya esta coloreado entonces es ciclo impar y no es bipartito
            for vecino, _ in g.adyacencia[actual]:
                if vecino not in color:
                    color[vecino] = 1 - color[actual]
                    cola.append(vecino)
                elif color[vecino] == color[actual]:
                    bipartita = False  # ciclo impar encontrado, pero seguimos para contar
        #cuando ya termina la cola entonces ya eso es un conjunto disjunto porque no hay mas vecinos a esos nodos
        componentes.append([tamaño, bipartita])
    #revisar cual es el mas grande revisando el tamañ0
    #como componente guarda una lista entonces itera componentes y de c
    componente_grande = componentes[0]
    for i in componentes:
        if i[0] > componente_grande[0]:
            componente_grande = i
    
    print(f"Número de componentes: {len(componentes)}")
    print(f"Componente más grande: {componente_grande[0]} vértices")
    print(f"¿Es bipartita?")
    if componente_grande[1]:
        print("Sí")
    else: 
        print("No")
    
    return componente_grande[1]