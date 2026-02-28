#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPTIMIZADOR INDUSTRIAL DE RUTAS - Version Terminal
Algoritmo: Prim (Arbol de Expansion Minima - MST)
Desarrollado por: Alejandro Aguirre Diaz
"""

import os
import sys
import time
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from heapq import heappush, heappop


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


def construir_grafo() -> Dict[str, List[Tuple[str, int]]]:
    """Construye el grafo a partir de los nodos y aristas"""
    grafo = {nodo_id: [] for nodo_id in NODOS.keys()}
    for u, v, peso in ARISTAS:
        grafo[u].append((v, peso))
        grafo[v].append((u, peso))
    return grafo


GRAFO = construir_grafo()


# =============================================================================
# ALGORITMO DE PRIM
# =============================================================================

@dataclass
class ResultadoPrim:
    """Almacena el resultado de la ejecucion de Prim"""
    mst_aristas: List[Tuple[str, str, int]]
    costo_total: int
    recorrido: List[Tuple[str, str, str, int, str]]  # (accion, nodo_actual, nodo_vecino, peso, info)
    orden_insercion: List[str]  # Orden en que los nodos se agregaron al MST
    aristas_consideradas: int
    nodo_inicial: str


def prim(nodo_inicial: str) -> ResultadoPrim:
    """
    Implementacion del algoritmo de Prim para encontrar el
    Arbol de Expansion Minima (MST) de un grafo.
    
    Args:
        nodo_inicial: Nodo desde el cual comenzar la construccion del MST
    
    Returns:
        ResultadoPrim con toda la informacion de la ejecucion
    """
    # Inicializacion
    en_mst = set()
    distancia = {nodo: float('inf') for nodo in NODOS.keys()}
    padre = {nodo: None for nodo in NODOS.keys()}
    mst_aristas = []
    recorrido = []
    orden_insercion = []
    
    # El nodo inicial tiene distancia 0
    distancia[nodo_inicial] = 0
    
    # Cola de prioridad: (distancia, nodo)
    cola = [(0, nodo_inicial)]
    aristas_consideradas = 0
    
    # Registrar inicio
    recorrido.append(('inicio', nodo_inicial, '', 0, f"Iniciando Prim desde {nodo_inicial}"))
    
    while cola and len(en_mst) < len(NODOS):
        # Obtener el nodo con menor distancia
        dist_actual, nodo_actual = heappop(cola)
        
        # Si ya esta en el MST, ignorar
        if nodo_actual in en_mst:
            recorrido.append(('ignorado', nodo_actual, '', 0, f"{nodo_actual} ya esta en el MST"))
            continue
        
        # Agregar al MST
        en_mst.add(nodo_actual)
        orden_insercion.append(nodo_actual)
        
        # Si tiene padre, agregar la arista al MST
        if padre[nodo_actual] is not None:
            mst_aristas.append((padre[nodo_actual], nodo_actual, dist_actual))
            recorrido.append(('agregada', padre[nodo_actual], nodo_actual, dist_actual, 
                             f"Agregando arista {padre[nodo_actual]} -- {nodo_actual} ({dist_actual}m)"))
        else:
            # Es el nodo inicial
            recorrido.append(('inicial', nodo_actual, '', 0, f"Nodo inicial: {nodo_actual}"))
        
        # Explorar vecinos
        for vecino, peso in GRAFO[nodo_actual]:
            aristas_consideradas += 1
            
            if vecino not in en_mst and peso < distancia[vecino]:
                # Mejoramos la distancia
                distancia_anterior = distancia[vecino]
                distancia[vecino] = peso
                padre[vecino] = nodo_actual
                heappush(cola, (peso, vecino))
                
                if distancia_anterior == float('inf'):
                    recorrido.append(('conexion', nodo_actual, vecino, peso, 
                                     f"Nueva conexion: {nodo_actual} -> {vecino} (peso {peso}m)"))
                else:
                    recorrido.append(('mejora', nodo_actual, vecino, peso, 
                                     f"Mejorando distancia de {vecino}: {distancia_anterior:.0f}m -> {peso}m"))
            elif vecino not in en_mst:
                recorrido.append(('sin_mejora', nodo_actual, vecino, peso, 
                                 f"Sin mejora para {vecino} (peso actual {distancia[vecino]:.0f}m < {peso}m)"))
    
    # Calcular costo total
    costo_total = sum(peso for _, _, peso in mst_aristas)
    
    # Registrar fin
    recorrido.append(('fin', '', '', costo_total, f"MST completado con {len(mst_aristas)} aristas"))
    
    return ResultadoPrim(
        mst_aristas=mst_aristas,
        costo_total=costo_total,
        recorrido=recorrido,
        orden_insercion=orden_insercion,
        aristas_consideradas=aristas_consideradas,
        nodo_inicial=nodo_inicial
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
    print(" OPTIMIZADOR INDUSTRIAL DE RUTAS - PRIM (MST)")
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


def mostrar_paso_prim(paso_num: int, accion: str, nodo1: str, nodo2: str, peso: int, info: str):
    """
    Muestra un paso individual del algoritmo de Prim
    """
    if accion == 'inicio':
        print(f"\n[>>] PASO {paso_num:2d}: {info}")
    
    elif accion == 'inicial':
        print(f"\n  [*] PASO {paso_num:2d}: {info}")
        print(f"      Agregando {nodo1} al MST (nodo inicial)")
    
    elif accion == 'agregada':
        print(f"\n  [+] PASO {paso_num:2d}: {info}")
        print(f"      {nodo1:12} -- {nodo2:12} : {peso:2d}m")
    
    elif accion == 'conexion':
        print(f"\n  [+] PASO {paso_num:2d}: {info}")
        print(f"      Distancia actual de {nodo2}: {peso}m")
    
    elif accion == 'mejora':
        print(f"\n  [+] PASO {paso_num:2d}: {info}")
    
    elif accion == 'sin_mejora':
        print(f"\n  [.] PASO {paso_num:2d}: {info}")
    
    elif accion == 'ignorado':
        print(f"\n  [ ] PASO {paso_num:2d}: {info}")
    
    elif accion == 'fin':
        print(f"\n  [*] PASO {paso_num:2d}: {info}")
        print(f"      Costo total del MST: {peso}m")


def mostrar_resultado(resultado: ResultadoPrim, origen: Optional[str] = None, destino: Optional[str] = None):
    """
    Muestra el resultado final del algoritmo
    """
    print("\n" + "=" * 70)
    print("[*] RESULTADO FINAL - ARBOL DE EXPANSION MINIMA (MST)")
    print("=" * 70)
    
    print(f"\n[+] ESTADISTICAS:")
    print(f"    Nodo inicial: {resultado.nodo_inicial}")
    print(f"    Aristas consideradas: {resultado.aristas_consideradas}")
    print(f"    Aristas en el MST: {len(resultado.mst_aristas)}")
    print(f"\n[*] Costo total del MST: {resultado.costo_total} metros")
    
    # Mostrar orden de insercion
    print(f"\n[+] ORDEN DE INSERCION DE NODOS:")
    orden_str = " -> ".join(resultado.orden_insercion)
    print(f"    {orden_str}")
    
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


def ejecutar_simulacion(nodo_inicial: str, velocidad: float = 0.5, 
                        origen: Optional[str] = None, destino: Optional[str] = None):
    """
    Ejecuta la simulacion completa de Prim con visualizacion paso a paso
    
    Args:
        nodo_inicial: Nodo desde el cual comenzar
        velocidad: Tiempo de pausa entre pasos (segundos)
        origen: Nodo de origen (opcional, para mostrar camino)
        destino: Nodo de destino (opcional, para mostrar camino)
    """
    limpiar_pantalla()
    mostrar_titulo()
    
    print(f"\n[>>] INICIANDO PRIM - Buscando Arbol de Expansion Minima")
    print(f"     Nodo inicial: {nodo_inicial}")
    print("=" * 70)
    
    # Ejecutar algoritmo
    resultado = prim(nodo_inicial)
    
    # Mostrar pasos
    print("\n[*] EJECUCION PASO A PASO:")
    print("-" * 70)
    
    for paso_num, (accion, n1, n2, peso, info) in enumerate(resultado.recorrido, 1):
        mostrar_paso_prim(paso_num, accion, n1, n2, peso, info)
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
        print("   1. Ejecutar Prim (Arbol de Expansion Minima)")
        print("   2. Ejecutar Prim y mostrar camino entre nodos")
        print("   3. Ver informacion de estaciones")
        print("   4. Cambiar velocidad de simulacion")
        print("   5. Salir")
        print()
        
        opcion = input("   Selecciona una opcion (1-5): ").strip()
        
        if opcion == '1':
            limpiar_pantalla()
            mostrar_titulo()
            
            nodo_inicial = seleccionar_nodo("[>>] Nodo inicial para Prim")
            if nodo_inicial is None:
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
            
            # Ejecutar simulacion
            ejecutar_simulacion(nodo_inicial, velocidad)
            pausa()
        
        elif opcion == '2':
            limpiar_pantalla()
            mostrar_titulo()
            
            nodo_inicial = seleccionar_nodo("[>>] Nodo inicial para Prim")
            if nodo_inicial is None:
                continue
            
            limpiar_pantalla()
            mostrar_titulo()
            
            origen = seleccionar_nodo("[>>] Nodo de ORIGEN para el camino", obligatorio=False)
            if origen is None:
                continue
            
            limpiar_pantalla()
            mostrar_titulo()
            
            destino = seleccionar_nodo("[<<] Nodo de DESTINO para el camino", obligatorio=False)
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
            ejecutar_simulacion(nodo_inicial, velocidad, origen, destino)
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