#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPTIMIZADOR INDUSTRIAL DE RUTAS - Version Terminal
Algoritmo: Kruskal (Arbol de Expansion Minima - MST)
Desarrollado por: Alejandro Aguirre Diaz
"""

import os
import sys
import time
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass


# =============================================================================
# DEFINICION DEL GRAFO - PLANTA INDUSTRIAL DELTA-7
# =============================================================================

@dataclass
class Nodo:
    """Representa una estacion en la planta"""
    id: str
    nombre: str

# Nodos de la planta
NODOS = {
    'ALMACEN': Nodo('ALMACEN', 'Almacen Central'),
    'CNC-1': Nodo('CNC-1', 'CNC Maq.1'),
    'CNC-2': Nodo('CNC-2', 'CNC Maq.2'),
    'ENSAMBLE-A': Nodo('ENSAMBLE-A', 'Ensamble Area A'),
    'ENSAMBLE-B': Nodo('ENSAMBLE-B', 'Ensamble Area B'),
    'ENSAMBLE-C': Nodo('ENSAMBLE-C', 'Ensamble Area C'),
    'SOLDADURA': Nodo('SOLDADURA', 'Soldadura Robotica'),
    'PINTURA': Nodo('PINTURA', 'Cabina Pintura'),
    'QA': Nodo('QA', 'Control Calidad'),
    'EMPAQUE': Nodo('EMPAQUE', 'Empaque Final'),
    'DESPACHO': Nodo('DESPACHO', 'Despacho Logistica'),
    'CARGA': Nodo('CARGA', 'Estacion Carga'),
}

# Aristas con sus pesos (distancias en metros)
ARISTAS = [
    ('ALMACEN', 'CNC-1', 18),
    ('ALMACEN', 'CNC-2', 18),
    ('ALMACEN', 'ENSAMBLE-B', 32),
    ('CNC-1', 'ENSAMBLE-A', 22),
    ('CNC-1', 'ENSAMBLE-B', 25),
    ('CNC-2', 'ENSAMBLE-B', 25),
    ('CNC-2', 'ENSAMBLE-C', 22),
    ('ENSAMBLE-A', 'SOLDADURA', 20),
    ('ENSAMBLE-A', 'ENSAMBLE-B', 18),
    ('ENSAMBLE-B', 'SOLDADURA', 24),
    ('ENSAMBLE-B', 'PINTURA', 24),
    ('ENSAMBLE-B', 'ENSAMBLE-C', 18),
    ('ENSAMBLE-C', 'PINTURA', 20),
    ('SOLDADURA', 'QA', 28),
    ('SOLDADURA', 'EMPAQUE', 30),
    ('PINTURA', 'EMPAQUE', 28),
    ('PINTURA', 'QA', 35),
    ('QA', 'EMPAQUE', 18),
    ('QA', 'DESPACHO', 22),
    ('EMPAQUE', 'DESPACHO', 20),
    ('EMPAQUE', 'CARGA', 22),
    ('DESPACHO', 'CARGA', 25),
]


# =============================================================================
# ESTRUCTURAS PARA UNION-FIND (CONJUNTOS DISJUNTOS)
# =============================================================================

class UnionFind:
    """Implementacion de Union-Find para deteccion de ciclos"""
    
    def __init__(self, nodos: List[str]):
        self.parent = {nodo: nodo for nodo in nodos}
        self.rank = {nodo: 0 for nodo in nodos}
    
    def find(self, x: str) -> str:
        """Encuentra el representante del conjunto de x (con compresion de ruta)"""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x: str, y: str) -> bool:
        """Une los conjuntos de x e y. Retorna True si se unieron, False si ya estaban unidos"""
        raiz_x = self.find(x)
        raiz_y = self.find(y)
        
        if raiz_x == raiz_y:
            return False
        
        # Union por rango
        if self.rank[raiz_x] < self.rank[raiz_y]:
            self.parent[raiz_x] = raiz_y
        elif self.rank[raiz_x] > self.rank[raiz_y]:
            self.parent[raiz_y] = raiz_x
        else:
            self.parent[raiz_y] = raiz_x
            self.rank[raiz_x] += 1
        
        return True
    
    def mismo_conjunto(self, x: str, y: str) -> bool:
        """Verifica si x e y estan en el mismo conjunto"""
        return self.find(x) == self.find(y)


# =============================================================================
# ALGORITMO DE KRUSKAL
# =============================================================================

@dataclass
class ResultadoKruskal:
    """Almacena el resultado de la ejecucion de Kruskal"""
    mst_aristas: List[Tuple[str, str, int]]
    costo_total: int
    recorrido: List[Tuple[str, str, str, int, bool]]  # (accion, u, v, peso, aceptada)
    aristas_consideradas: int
    aristas_agregadas: int
    aristas_rechazadas: int


def kruskal() -> ResultadoKruskal:
    """
    Implementacion del algoritmo de Kruskal para encontrar el
    Arbol de Expansion Minima (MST) de un grafo.
    
    Returns:
        ResultadoKruskal con toda la informacion de la ejecucion
    """
    # Ordenar aristas por peso ascendente
    aristas_ordenadas = sorted(ARISTAS, key=lambda x: x[2])
    
    # Inicializar Union-Find
    uf = UnionFind(list(NODOS.keys()))
    
    # Inicializar resultados
    mst_aristas = []
    recorrido = []
    costo_total = 0
    aristas_consideradas = 0
    aristas_agregadas = 0
    aristas_rechazadas = 0
    
    # Registrar inicio
    recorrido.append(('inicio', '', '', 0, True))
    
    # Procesar cada arista en orden
    for u, v, peso in aristas_ordenadas:
        aristas_consideradas += 1
        
        # Verificar si agregar esta arista forma un ciclo
        if not uf.mismo_conjunto(u, v):
            # No forma ciclo, agregar al MST
            uf.union(u, v)
            mst_aristas.append((u, v, peso))
            costo_total += peso
            aristas_agregadas += 1
            recorrido.append(('agregada', u, v, peso, True))
            
            # Si ya tenemos V-1 aristas, el MST esta completo
            if len(mst_aristas) == len(NODOS) - 1:
                recorrido.append(('completo', '', '', 0, True))
                break
        else:
            # Forma ciclo, rechazar
            aristas_rechazadas += 1
            recorrido.append(('rechazada', u, v, peso, False))
    
    # Registrar fin
    recorrido.append(('fin', '', '', costo_total, True))
    
    return ResultadoKruskal(
        mst_aristas=mst_aristas,
        costo_total=costo_total,
        recorrido=recorrido,
        aristas_consideradas=aristas_consideradas,
        aristas_agregadas=aristas_agregadas,
        aristas_rechazadas=aristas_rechazadas
    )


def encontrar_camino_en_mst(mst_aristas: List[Tuple[str, str, int]], origen: str, destino: str) -> Optional[List[str]]:
    """
    Encuentra el camino entre dos nodos dentro del MST usando BFS
    
    Args:
        mst_aristas: Lista de aristas del MST
        origen: Nodo de inicio
        destino: Nodo de destino
    
    Returns:
        Lista de nodos en el camino, o None si no hay camino
    """
    if not mst_aristas:
        return None
    
    # Construir grafo del MST
    grafo_mst = {nodo: [] for nodo in NODOS.keys()}
    for u, v, peso in mst_aristas:
        grafo_mst[u].append((v, peso))
        grafo_mst[v].append((u, peso))
    
    # BFS para encontrar camino
    visitados = set()
    cola = [(origen, [origen])]
    visitados.add(origen)
    
    while cola:
        nodo, camino = cola.pop(0)
        
        if nodo == destino:
            return camino
        
        for vecino, _ in grafo_mst[nodo]:
            if vecino not in visitados:
                visitados.add(vecino)
                cola.append((vecino, camino + [vecino]))
    
    return None  # No hay camino


# =============================================================================
# FUNCIONES DE VISUALIZACION EN TERMINAL
# =============================================================================

def limpiar_pantalla():
    """Limpia la pantalla de la terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')


def pausa():
    """Pausa la ejecucion hasta que el usuario presione Enter"""
    input("\n[+] Presiona Enter para continuar...")


def mostrar_titulo():
    """Muestra el titulo de la aplicacion"""
    print("=" * 70)
    print(" OPTIMIZADOR INDUSTRIAL DE RUTAS - KRUSKAL (MST)")
    print("=" * 70)
    print(f" Desarrollado por: Alejandro Aguirre Diaz")
    print("=" * 70)
    print()


def mostrar_nodos_disponibles():
    """Muestra la lista de nodos disponibles con sus nombres"""
    print("\n[+] ESTACIONES DISPONIBLES:")
    print("-" * 70)
    
    # Organizar en columnas
    nodos_lista = list(NODOS.items())
    for i in range(0, len(nodos_lista), 3):
        linea = ""
        for j in range(3):
            if i + j < len(nodos_lista):
                nodo_id, nodo = nodos_lista[i + j]
                linea += f"  {nodo_id:<12} "
        print(linea)
    
    # Mostrar nombres completos
    print("\n Nombres completos:")
    for nodo_id, nodo in NODOS.items():
        print(f"   {nodo_id:<12} - {nodo.nombre}")
    print("-" * 70)


def seleccionar_nodo(prompt: str, obligatorio: bool = True) -> Optional[str]:
    """
    Solicita al usuario que seleccione un nodo de la lista
    
    Args:
        prompt: Mensaje a mostrar al usuario
        obligatorio: Si es True, el nodo es obligatorio
    
    Returns:
        ID del nodo seleccionado o None
    """
    while True:
        mostrar_nodos_disponibles()
        
        if obligatorio:
            mensaje = f"\n{prompt} (o 'q' para salir): "
        else:
            mensaje = f"\n{prompt} (o 'q' para salir, Enter para omitir): "
        
        nodo = input(mensaje).strip().upper()
        
        if nodo == 'Q':
            return None
        
        if not obligatorio and nodo == '':
            return None
        
        if nodo in NODOS:
            return nodo
        else:
            print(f"\n[!] Error: '{nodo}' no es una estacion valida.")
            pausa()
            limpiar_pantalla()
            mostrar_titulo()


def mostrar_paso_kruskal(paso_num: int, accion: str, u: str, v: str, peso: int, aceptada: bool):
    """
    Muestra un paso individual del algoritmo de Kruskal
    """
    if accion == 'inicio':
        print(f"\n[>>] PASO {paso_num:2d}: INICIANDO KRUSKAL")
        print(f"     Ordenando {len(ARISTAS)} aristas por peso ascendente...")
    
    elif accion == 'agregada':
        print(f"\n  [+] PASO {paso_num:2d}: ARISTA AGREGADA al MST")
        print(f"      {u:12} -- {v:12} : {peso:2d}m")
        print(f"      [No forma ciclo]")
    
    elif accion == 'rechazada':
        print(f"\n  [ ] PASO {paso_num:2d}: ARISTA RECHAZADA")
        print(f"      {u:12} -- {v:12} : {peso:2d}m")
        print(f"      [Forma ciclo]")
    
    elif accion == 'completo':
        print(f"\n  [*] PASO {paso_num:2d}: MST COMPLETADO")
        print(f"      Se alcanzaron las {len(NODOS)-1} aristas necesarias")
    
    elif accion == 'fin':
        print(f"\n  [*] PASO {paso_num:2d}: ALGORITMO FINALIZADO")
        print(f"      Costo total del MST: {peso}m")


def mostrar_resultado(resultado: ResultadoKruskal, origen: Optional[str] = None, destino: Optional[str] = None):
    """
    Muestra el resultado final del algoritmo
    """
    print("\n" + "=" * 70)
    print("[*] RESULTADO FINAL - ARBOL DE EXPANSION MINIMA (MST)")
    print("=" * 70)
    
    print(f"\n[+] ESTADISTICAS:")
    print(f"    Aristas consideradas: {resultado.aristas_consideradas}")
    print(f"    Aristas agregadas al MST: {resultado.aristas_agregadas}")
    print(f"    Aristas rechazadas (ciclos): {resultado.aristas_rechazadas}")
    print(f"\n[*] Costo total del MST: {resultado.costo_total} metros")
    
    # Mostrar aristas del MST
    print(f"\n[+] ARISTAS DEL MST:")
    print("-" * 70)
    for i, (u, v, peso) in enumerate(resultado.mst_aristas, 1):
        print(f"   {i:2d}. {u:12} -- {v:12} : {peso:2d}m")
    
    # Si se proporcionaron origen y destino, mostrar camino en el MST
    if origen and destino and origen in NODOS and destino in NODOS:
        camino = encontrar_camino_en_mst(resultado.mst_aristas, origen, destino)
        
        print(f"\n[+] CAMINO EN EL MST: {origen} -> {destino}")
        print("-" * 70)
        
        if camino:
            camino_str = " -> ".join(camino)
            print(f"    {camino_str}")
            
            # Calcular distancia del camino
            distancia = 0
            for i in range(len(camino) - 1):
                u = camino[i]
                v = camino[i + 1]
                for a, b, p in resultado.mst_aristas:
                    if (a == u and b == v) or (a == v and b == u):
                        distancia += p
                        break
            
            print(f"\n    Distancia en el MST: {distancia} metros")
            print(f"    Tiempo estimado (AGV 1.2 m/s): {distancia/1.2:.1f} segundos")
        else:
            print(f"    [No hay camino entre {origen} y {destino} en el MST]")
    
    print("=" * 70)


def ejecutar_simulacion(velocidad: float = 0.5, origen: Optional[str] = None, destino: Optional[str] = None):
    """
    Ejecuta la simulacion completa de Kruskal con visualizacion paso a paso
    
    Args:
        velocidad: Tiempo de pausa entre pasos (segundos)
        origen: Nodo de origen (opcional, para mostrar camino)
        destino: Nodo de destino (opcional, para mostrar camino)
    """
    limpiar_pantalla()
    mostrar_titulo()
    
    print(f"\n[>>] INICIANDO KRUSKAL - Buscando Arbol de Expansion Minima")
    print("=" * 70)
    
    # Ejecutar algoritmo
    resultado = kruskal()
    
    # Mostrar pasos
    print("\n[*] EJECUCION PASO A PASO:")
    print("-" * 70)
    
    for paso_num, (accion, u, v, peso, aceptada) in enumerate(resultado.recorrido, 1):
        mostrar_paso_kruskal(paso_num, accion, u, v, peso, aceptada)
        if velocidad > 0 and accion not in ['inicio', 'fin']:
            time.sleep(velocidad)
    
    # Mostrar resultado final
    mostrar_resultado(resultado, origen, destino)
    
    return resultado


def menu_principal():
    """Muestra el menu principal y maneja la interaccion con el usuario"""
    
    while True:
        limpiar_pantalla()
        mostrar_titulo()
        
        print("\n[+] MENU PRINCIPAL:")
        print("   1. Ejecutar Kruskal (Arbol de Expansion Minima)")
        print("   2. Ejecutar Kruskal y mostrar camino entre nodos")
        print("   3. Ver informacion de estaciones")
        print("   4. Cambiar velocidad de simulacion")
        print("   5. Salir")
        print()
        
        opcion = input("   Selecciona una opcion (1-5): ").strip()
        
        if opcion == '1':
            # Solicitar velocidad
            print("\n[*] Velocidad de simulacion:")
            print("   1. Lenta (1s por paso)")
            print("   2. Normal (0.5s por paso)")
            print("   3. Rapida (0.2s por paso)")
            print("   4. Instantanea")
            
            vel_opcion = input("\n   Selecciona velocidad (1-4) [2]: ").strip() or '2'
            
            if vel_opcion == '1':
                velocidad = 1.0
            elif vel_opcion == '2':
                velocidad = 0.5
            elif vel_opcion == '3':
                velocidad = 0.2
            else:
                velocidad = 0.0
            
            # Ejecutar simulacion
            ejecutar_simulacion(velocidad)
            pausa()
        
        elif opcion == '2':
            limpiar_pantalla()
            mostrar_titulo()
            
            origen = seleccionar_nodo("[>>] Nodo de ORIGEN (opcional)", obligatorio=False)
            if origen is None:
                continue
            
            limpiar_pantalla()
            mostrar_titulo()
            
            destino = seleccionar_nodo("[<<] Nodo de DESTINO (opcional)", obligatorio=False)
            if destino is None:
                continue
            
            # Solicitar velocidad
            print("\n[*] Velocidad de simulacion:")
            print("   1. Lenta (1s por paso)")
            print("   2. Normal (0.5s por paso)")
            print("   3. Rapida (0.2s por paso)")
            print("   4. Instantanea")
            
            vel_opcion = input("\n   Selecciona velocidad (1-4) [2]: ").strip() or '2'
            
            if vel_opcion == '1':
                velocidad = 1.0
            elif vel_opcion == '2':
                velocidad = 0.5
            elif vel_opcion == '3':
                velocidad = 0.2
            else:
                velocidad = 0.0
            
            # Ejecutar simulacion con origen y destino
            ejecutar_simulacion(velocidad, origen, destino)
            pausa()
        
        elif opcion == '3':
            limpiar_pantalla()
            mostrar_titulo()
            
            print("\n[*] INFORMACION DE ESTACIONES:")
            print("-" * 70)
            
            # Mostrar todas las aristas
            print("\n[+] ARISTAS DEL GRAFO:")
            aristas_ordenadas = sorted(ARISTAS, key=lambda x: x[2])
            for u, v, peso in aristas_ordenadas:
                print(f"   {u:12} -- {v:12} : {peso:2d}m")
            
            print("\n[+] TOTAL:")
            print(f"   Nodos: {len(NODOS)}")
            print(f"   Aristas: {len(ARISTAS)}")
            
            print()
            pausa()
        
        elif opcion == '4':
            print("\n[*] La velocidad se puede ajustar durante la ejecucion.")
            print("    En el menu principal, selecciona la opcion 1 o 2 y luego")
            print("    elige la velocidad deseada.")
            pausa()
        
        elif opcion == '5':
            print("\n[*] ¡Hasta luego! Gracias por usar el Optimizador Industrial de Rutas.")
            sys.exit(0)
        
        else:
            print("\n[!] Opcion no valida. Intenta de nuevo.")
            pausa()


# =============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# =============================================================================

def main():
    """Funcion principal del programa"""
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n[*] Simulacion interrumpida por el usuario. ¡Hasta luego!")
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()