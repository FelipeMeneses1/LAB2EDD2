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


def Prim(g, componente):
    visitados = {}
    visitados[componente[0]] = True
    peso_total = 0

    while len(visitados) < len(componente):
        minimo = -1
        destino_min = None

        for vertice in visitados:
            for vecino, peso in g.adyacencia[vertice]:
                if vecino not in visitados:
                    if minimo == -1 or peso < minimo:
                        minimo = peso
                        destino_min = vecino

        visitados[destino_min] = True
        peso_total += minimo

    return peso_total

def Minimo_Componentes(g, componentes):
    for i, componente in enumerate(componentes):
        peso = Prim(g, componente)
        print(f"Componente {i + 1}: {len(componente)} vértices, peso MST = {peso:.2f} km")

def dijkstra(g, origen):
    distancias = {}
    visitados = {}
    predecesores = {}

    for vertice in g.adyacencia:
        distancias[vertice] = float('inf')
        predecesores[vertice] = None
    distancias[origen] = 0

    while True:
        minimo = float('inf')
        actual = None
        for vertice in distancias:
            if vertice not in visitados and distancias[vertice] < minimo:
                minimo = distancias[vertice]
                actual = vertice

        if actual is None:
            break

        visitados[actual] = True

        for vecino, peso in g.adyacencia[actual]:
            if vecino not in visitados:
                nueva_distancia = distancias[actual] + peso
                if nueva_distancia < distancias[vecino]:
                    distancias[vecino] = nueva_distancia
                    predecesores[vecino] = actual

    return distancias, predecesores


def camino_minimo(g, origen, destino):
    distancias, predecesores = dijkstra(g, origen)

    # Verificar si el destino es alcanzable
    if distancias[destino] == float('inf'):
        print(f"No existe camino entre {origen} y {destino}.")
        return None

    # Reconstruir el camino backwards desde destino hasta origen
    camino = []
    actual = destino
    while actual is not None:
        camino.append(actual)
        actual = predecesores[actual]

    # Invertir el camino para que vaya de origen a destino
    camino.reverse()

    # Mostrar información de cada aeropuerto en el camino
    print(f"\nCamino mínimo de {origen} a {destino} ({distancias[destino]:.2f} km):")
    for i, codigo in enumerate(camino):
        info = g.aeropuertos[codigo]
        print(f"\n{i + 1}. Código: {codigo}")
        print(f"   Nombre: {info['nombre']}")
        print(f"   Ciudad: {info['ciudad']}")
        print(f"   País: {info['pais']}")
        print(f"   Latitud: {info['lat']}")
        print(f"   Longitud: {info['lon']}")

    return camino

def top_10_lejanos(g, origen):
    info = g.aeropuertos[origen]
    print(f"Aeropuerto origen:")
    print(f"  Código: {origen}")
    print(f"  Nombre: {info['nombre']}")
    print(f"  Ciudad: {info['ciudad']}")
    print(f"  País: {info['pais']}")
    print(f"  Latitud: {info['lat']}")
    print(f"  Longitud: {info['lon']}")

    distancias, _ = dijkstra(g, origen)

    pares = []
    for codigo, distancia in distancias.items():
        if distancia != float('inf') and codigo != origen:
            pares.append([codigo, distancia])

    for i in range(min(10, len(pares))):
        max_idx = i
        for j in range(i + 1, len(pares)):
            if pares[j][1] > pares[max_idx][1]:
                max_idx = j
        pares[i], pares[max_idx] = pares[max_idx], pares[i]

    print(f"\nTop 10 aeropuertos más lejanos desde {origen}:")
    for i in range(min(10, len(pares))):
        codigo = pares[i][0]
        distancia = pares[i][1]
        info = g.aeropuertos[codigo]
        print(f"\n{i + 1}. Código: {codigo}")
        print(f"   Nombre: {info['nombre']}")
        print(f"   Ciudad: {info['ciudad']}")
        print(f"   País: {info['pais']}")
        print(f"   Latitud: {info['lat']}")
        print(f"   Longitud: {info['lon']}")
        print(f"   Distancia: {distancia:.2f} km")

def es_conexo(g, componentes):
    if len(componentes) == 1:
        print("El grafo ES conexo.")
    else:
        print(f"El grafo NO es conexo.")
        print(f"Número de componentes: {len(componentes)}")
        for i, componente in enumerate(componentes):
            print(f"  Componente {i + 1}: {len(componente)} vértices")

import tkinter as tk
from tkinter import messagebox

def interfaz():
    g = construir_grafo(data)
    componentes = encontrar_componentes(g)

    ventana = tk.Tk()
    ventana.title("Grafo de Aeropuertos")
    ventana.geometry("800x550")
    ventana.config(bg="#eef2f7")

    # ----------- FRAMES -----------
    frame_izq = tk.Frame(ventana, bg="#2c3e50", width=250)
    frame_izq.pack(side="left", fill="y")

    frame_der = tk.Frame(ventana, bg="#ecf0f1")
    frame_der.pack(side="right", expand=True, fill="both")

    # ----------- AREA RESULTADOS -----------
    resultado = tk.Text(frame_der, bg="#ffffff", fg="#2c3e50",
                        font=("Consolas", 10), bd=0)
    resultado.pack(padx=10, pady=10, fill="both", expand=True)

    # ----------- CANVAS (AHORA OSCURO) -----------
    canvas = tk.Canvas(frame_der, bg="#2c3e50", height=200, highlightthickness=0)
    canvas.pack(fill="x", padx=10, pady=5)

    def mostrar(texto):
        resultado.delete("1.0", tk.END)
        resultado.insert(tk.END, texto)

    # ----------- DIBUJAR CAMINO -----------

    def dibujar_camino(camino):
        canvas.delete("all")

        if len(camino) == 0:
            return

        x = 50
        y = 100

        for i in range(len(camino)):
            if i == 0:
                color = "#2ecc71"   # verde claro
            elif i == len(camino) - 1:
                color = "#e74c3c"   # rojo claro
            else:
                color = "#3498db"   # azul

            canvas.create_oval(x-15, y-15, x+15, y+15, fill=color, outline="")

            canvas.create_text(x, y, text=camino[i], fill="white")

            if i < len(camino) - 1:
                canvas.create_line(x+15, y, x+85, y,
                                   arrow=tk.LAST,
                                   fill="white", width=2)

            x += 100

    # ----------- FUNCIONES -----------

    def accion_conexo():
        if len(componentes) == 1:
            mostrar("El grafo ES conexo")
        else:
            texto = f"El grafo NO es conexo\nComponentes: {len(componentes)}\n"
            for i, comp in enumerate(componentes):
                texto += f"Componente {i+1}: {len(comp)} vértices\n"
            mostrar(texto)

    def accion_bipartito():
        componente_grande = componentes[0]
        for comp in componentes:
            if len(comp) > len(componente_grande):
                componente_grande = comp

        color = {}
        color[componente_grande[0]] = 0
        cola = [componente_grande[0]]
        bipartita = True

        while cola:
            actual = cola.pop(0)
            for vecino, _ in g.adyacencia[actual]:
                if vecino not in color:
                    color[vecino] = 1 - color[actual]
                    cola.append(vecino)
                elif color[vecino] == color[actual]:
                    bipartita = False

        if bipartita:
            mostrar("La componente más grande ES bipartita")
        else:
            mostrar("La componente más grande NO es bipartita")

    def accion_mst():
        texto = ""
        for i, comp in enumerate(componentes):
            peso = Prim(g, comp)
            texto += f"Componente {i+1}: {len(comp)} vértices, MST = {peso:.2f} km\n"
        mostrar(texto)

    def accion_camino():
        origen = entry_origen.get().upper()
        destino = entry_destino.get().upper()

        if origen not in g.aeropuertos or destino not in g.aeropuertos:
            messagebox.showerror("Error", "Aeropuerto inválido")
            return

        distancias, predecesores = dijkstra(g, origen)

        if distancias[destino] == float('inf'):
            mostrar("No existe camino")
            canvas.delete("all")
            return

        # reconstruir camino
        camino = []
        actual = destino
        while actual is not None:
            camino.append(actual)
            actual = predecesores[actual]
        camino.reverse()

        # -------- FORMATO BONITO --------
        texto = ""
        texto += "CAMINO MÍNIMO\n"
        texto += "─" * 65 + "\n\n"

        # Ruta tipo: BOG → PUJ → MAN → LHR
        texto += "Ruta: " + " → ".join(camino) + "\n"
        texto += f"Distancia total: {distancias[destino]:,.2f} km\n\n"

        texto += "─" * 65 + "\n\n"

        # Mostrar cada aeropuerto
        for i, codigo in enumerate(camino):
            info = g.aeropuertos[codigo]

            if i == 0:
                tipo = "[ORIGEN]"
            elif i == len(camino) - 1:
                tipo = "[DESTINO]"
            else:
                tipo = f"[ESCALA {i}]"

            texto += f"  {tipo}  {codigo}\n"
            texto += f"      Nombre:   {info['nombre']}\n"
            texto += f"      Ciudad:   {info['ciudad']}\n"
            texto += f"      País:     {info['pais']}\n"
            texto += f"      Lat/Lon:  {info['lat']}, {info['lon']}\n\n"

        texto += "─" * 65

        mostrar(texto)
        dibujar_camino(camino)

    def accion_top10():
        origen = entry_origen.get().upper()

        if origen not in g.aeropuertos:
            messagebox.showerror("Error", "Aeropuerto inválido")
            return

        info = g.aeropuertos[origen]

        # Ejecutar Dijkstra
        distancias, _ = dijkstra(g, origen)

        # Construir lista de pares
        pares = []
        for codigo, distancia in distancias.items():
            if distancia != float('inf') and codigo != origen:
                pares.append([codigo, distancia])

        # Ordenar de mayor a menor (como tú ya lo haces manual)
        for i in range(min(10, len(pares))):
            max_idx = i
            for j in range(i + 1, len(pares)):
                if pares[j][1] > pares[max_idx][1]:
                    max_idx = j
            pares[i], pares[max_idx] = pares[max_idx], pares[i]

        # -------- FORMATO BONITO --------
        texto = ""

        texto += "INFORMACIÓN DEL AEROPUERTO ORIGEN\n\n"
        texto += "─" * 65 + "\n"
        texto += f"  Nombre:   {info['nombre']}\n"
        texto += f"  Ciudad:   {info['ciudad']}\n"
        texto += f"  País:     {info['pais']}\n"
        texto += f"  Lat/Lon:  {info['lat']}, {info['lon']}\n"
        texto += "─" * 65 + "\n"


        texto += "TOP 10 AEROPUERTOS MÁS LEJANOS\n\n"
        texto += "─" * 65 + "\n\n"

        # Mostrar top 10
        for i in range(min(10, len(pares))):
            codigo = pares[i][0]
            distancia = pares[i][1]
            info_dest = g.aeropuertos[codigo]

            texto += f"  #{i+1}  {codigo}\n"
            texto += f"      Nombre:   {info_dest['nombre']}\n"
            texto += f"      Ciudad:   {info_dest['ciudad']}\n"
            texto += f"      País:     {info_dest['pais']}\n"
            texto += f"      Lat/Lon:  {info_dest['lat']}, {info_dest['lon']}\n"
            texto += f"      Distancia (camino mínimo): {distancia:,.2f} km\n\n"

        mostrar(texto)
        canvas.delete("all")

    # ----------- ESTILO BOTONES (AHORA VISIBLE) -----------

    estilo_btn = {
        "bg": "#ecf0f1",
        "fg": "#2c3e50",
        "activebackground": "#bdc3c7",
        "bd": 0,
        "font": ("Arial", 10)
    }

    # ----------- PANEL IZQUIERDO -----------

    tk.Label(frame_izq, text="Opciones", bg="#2c3e50",
             fg="white", font=("Arial", 14, "bold")).pack(pady=10)

    tk.Button(frame_izq, text="¿Es conexo?", command=accion_conexo,
              **estilo_btn).pack(pady=5, fill="x", padx=10)

    tk.Button(frame_izq, text="¿Es bipartito?", command=accion_bipartito,
              **estilo_btn).pack(pady=5, fill="x", padx=10)

    tk.Button(frame_izq, text="MST", command=accion_mst,
              **estilo_btn).pack(pady=5, fill="x", padx=10)

    tk.Label(frame_izq, text="Origen:", bg="#2c3e50", fg="white").pack(pady=5)
    entry_origen = tk.Entry(frame_izq)
    entry_origen.pack(padx=10)

    tk.Label(frame_izq, text="Destino:", bg="#2c3e50", fg="white").pack(pady=5)
    entry_destino = tk.Entry(frame_izq)
    entry_destino.pack(padx=10)

    tk.Button(frame_izq, text="Camino mínimo", command=accion_camino,
              **estilo_btn).pack(pady=5, fill="x", padx=10)

    tk.Button(frame_izq, text="Top 10 lejanos", command=accion_top10,
              **estilo_btn).pack(pady=5, fill="x", padx=10)

    ventana.mainloop()


if __name__ == "__main__":
    interfaz()
