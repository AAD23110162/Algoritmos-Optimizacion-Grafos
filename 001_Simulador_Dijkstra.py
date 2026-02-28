#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPTIMIZADOR INDUSTRIAL DE RUTAS - Version Terminal
Algoritmo: Dijkstra (Camino mas corto)
Desarrollado por: Alejandro Aguirre Diaz
"""

import os
import sys
import time
from typing import Dict, List, Tuple, Optional
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
# ALGORITMO DE DIJKSTRA
# =============================================================================

@dataclass
class ResultadoDijkstra:
    """Almacena el resultado de la ejecucion de Dijkstra"""
    distancias: Dict[str, float]
    predecesores: Dict[str, Optional[str]]
    recorrido: List[Tuple[str, str, str, int]]  # Lista de (accion, nodo_actual, nodo_vecino, peso)
    camino: Optional[List[str]]
    distancia_total: Optional[float]
    visitados: List[str]


def dijkstra(origen: str, destino: str) -> ResultadoDijkstra:
    """
    Implementacion del algoritmo de Dijkstra para encontrar la ruta mas corta
    entre dos nodos en un grafo ponderado no negativo.
    
    Args:
        origen: Nodo de inicio
        destino: Nodo de destino
    
    Returns:
        ResultadoDijkstra con toda la informacion de la ejecucion
    """
    # Inicializacion
    distancias = {nodo: float('inf') for nodo in GRAFO.keys()}
    distancias[origen] = 0
    predecesores = {nodo: None for nodo in GRAFO.keys()}
    visitados = set()
    recorrido = []  # Para registro de pasos
    
    # Cola de prioridad: (distancia, nodo)
    cola = [(0, origen)]
    
    while cola:
        # Obtener el nodo con menor distancia
        dist_actual, nodo_actual = heappop(cola)
        
        # Si ya fue visitado, ignorar
        if nodo_actual in visitados:
            recorrido.append(('ignorado', nodo_actual, nodo_actual, 0))
            continue
        
        # Marcar como visitado
        visitados.add(nodo_actual)
        recorrido.append(('visita', nodo_actual, nodo_actual, 0))
        
        # Si llegamos al destino, podemos continuar pero no es necesario detenerse
        if nodo_actual == destino:
            # Aun asi, seguimos para completar el registro
            pass
        
        # Explorar vecinos
        for vecino, peso in GRAFO[nodo_actual]:
            if vecino in visitados:
                recorrido.append(('ignorado_visitado', nodo_actual, vecino, peso))
                continue
            
            nueva_distancia = dist_actual + peso
            
            # Registrar intento de relajacion
            if nueva_distancia < distancias[vecino]:
                # Relajacion exitosa
                distancias[vecino] = nueva_distancia
                predecesores[vecino] = nodo_actual
                heappush(cola, (nueva_distancia, vecino))
                recorrido.append(('relajacion', nodo_actual, vecino, peso))
            else:
                # No mejora
                recorrido.append(('no_mejora', nodo_actual, vecino, peso))
    
    # Reconstruir el camino
    camino = []
    nodo = destino
    while nodo is not None:
        camino.insert(0, nodo)
        nodo = predecesores[nodo]
    
    # Verificar si el camino es valido (empieza en el origen)
    if camino and camino[0] == origen:
        distancia_total = distancias[destino]
    else:
        camino = None
        distancia_total = None
    
    return ResultadoDijkstra(
        distancias=distancias,
        predecesores=predecesores,
        recorrido=recorrido,
        camino=camino,
        distancia_total=distancia_total,
        visitados=list(visitados)
    )


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
    print(" OPTIMIZADOR INDUSTRIAL DE RUTAS - DIJKSTRA")
    print("=" * 70)
    print(f" Desarrollado por: Alejandro Aguirre Diaz")
    print("=" * 70)
    print()


def mostrar_nodos_disponibles():
    """Muestra la lista de nodos disponibles con sus nombres"""
    print("\n[+] ESTACIONES DISPONIBLES:")
    print("-" * 70)
    
    # Organizar en columnas para mejor visualizacion
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


def seleccionar_nodo(prompt: str) -> str:
    """
    Solicita al usuario que seleccione un nodo de la lista
    
    Args:
        prompt: Mensaje a mostrar al usuario
    
    Returns:
        ID del nodo seleccionado
    """
    while True:
        mostrar_nodos_disponibles()
        nodo = input(f"\n{prompt} (o 'q' para salir): ").strip().upper()
        
        if nodo == 'Q':
            return None
        
        if nodo in NODOS:
            return nodo
        else:
            print(f"\n[!] Error: '{nodo}' no es una estacion valida.")
            pausa()
            limpiar_pantalla()
            mostrar_titulo()


def mostrar_paso_dijkstra(paso_num: int, accion: str, nodo_actual: str, 
                          nodo_vecino: str, peso: int, distancias: Dict[str, float]):
    """
    Muestra un paso individual del algoritmo de Dijkstra de forma visual
    """
    if accion == 'visita':
        print(f"  [>] PASO {paso_num:2d}: VISITANDO {nodo_actual:12} | "
              f"distancia = {distancias[nodo_actual]:3.0f}m")
    
    elif accion == 'relajacion':
        dist_nueva = distancias[nodo_actual] + peso
        print(f"  [+] PASO {paso_num:2d}: RELAJACION {nodo_actual:12} -> {nodo_vecino:12} "
              f"(peso {peso:2d}m) | nueva dist = {dist_nueva:3.0f}m")
    
    elif accion == 'no_mejora':
        print(f"  [.] PASO {paso_num:2d}: SIN MEJORA  {nodo_actual:12} -> {nodo_vecino:12} "
              f"(peso {peso:2d}m) | mantiene {distancias[nodo_vecino]:3.0f}m")
    
    elif accion == 'ignorado':
        print(f"  [ ] PASO {paso_num:2d}: IGNORADO    {nodo_actual:12} (ya visitado)")
    
    elif accion == 'ignorado_visitado':
        print(f"  [ ] PASO {paso_num:2d}: IGNORADO    {nodo_actual:12} -> {nodo_vecino:12} "
              f"(vecino ya visitado)")


def mostrar_resultado(resultado: ResultadoDijkstra, origen: str, destino: str):
    """
    Muestra el resultado final del algoritmo
    """
    print("\n" + "=" * 70)
    print("[*] RESULTADO FINAL")
    print("=" * 70)
    
    if resultado.camino and resultado.distancia_total is not None:
        # Mostrar camino
        print(f"\n[+] RUTA ENCONTRADA: {origen} -> {destino}")
        print("-" * 70)
        
        camino_str = " -> ".join(resultado.camino)
        print(f"    {camino_str}")
        
        print(f"\n[*] Distancia total: {resultado.distancia_total:.0f} metros")
        print(f"[*] Tiempo estimado (AGV 1.2 m/s): {resultado.distancia_total/1.2:.1f} segundos")
        
        # Mostrar tabla de distancias
        print(f"\n[*] DISTANCIAS ACUMULADAS DESDE {origen}:")
        print("-" * 70)
        
        # Organizar en columnas
        nodos_ordenados = sorted(resultado.distancias.items())
        for i in range(0, len(nodos_ordenados), 3):
            linea = ""
            for j in range(3):
                if i + j < len(nodos_ordenados):
                    nodo, dist = nodos_ordenados[i + j]
                    if dist == float('inf'):
                        dist_str = "INF"
                    else:
                        dist_str = f"{dist:.0f}m"
                    linea += f"  {nodo:<10}: {dist_str:>6}  "
            print(linea)
        
        # Mostrar ruta paso a paso
        print(f"\n[*] RUTA DETALLADA:")
        print("-" * 70)
        distancia_acum = 0
        for i in range(len(resultado.camino) - 1):
            u = resultado.camino[i]
            v = resultado.camino[i + 1]
            # Buscar el peso de la arista
            peso = next((p for (a, b, p) in ARISTAS 
                        if (a == u and b == v) or (a == v and b == u)), 0)
            distancia_acum += peso
            print(f"   {i+1}. {u:12} -> {v:12} : {peso:2d}m (acumulado {distancia_acum:3d}m)")
    
    else:
        print(f"\n[!] NO EXISTE RUTA entre {origen} y {destino}")
        print("    El grafo esta desconectado o el destino es inalcanzable.")
    
    print("=" * 70)


def ejecutar_simulacion(origen: str, destino: str, velocidad: float = 0.5):
    """
    Ejecuta la simulacion completa de Dijkstra con visualizacion paso a paso
    
    Args:
        origen: Nodo de inicio
        destino: Nodo de destino
        velocidad: Tiempo de pausa entre pasos (segundos)
    """
    limpiar_pantalla()
    mostrar_titulo()
    
    print(f"\n[>>] INICIANDO DIJKSTRA: {origen} -> {destino}")
    print("=" * 70)
    
    # Ejecutar algoritmo
    resultado = dijkstra(origen, destino)
    
    # Mostrar pasos
    paso_contador = 0
    ultimo_tipo = None
    
    print("\n[*] EJECUCION PASO A PASO:")
    print("-" * 70)
    
    for accion, actual, vecino, peso in resultado.recorrido:
        paso_contador += 1
        
        # Agrupar visitas para no mostrar tantos ignorados
        if accion in ['ignorado', 'ignorado_visitado'] and ultimo_tipo == accion:
            continue
        
        mostrar_paso_dijkstra(
            paso_contador, accion, actual, vecino, peso, 
            resultado.distancias
        )
        
        ultimo_tipo = accion
        if velocidad > 0:
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
        print("   1. Ejecutar Dijkstra (ruta mas corta)")
        print("   2. Ver informacion de estaciones")
        print("   3. Cambiar velocidad de simulacion")
        print("   4. Salir")
        print()
        
        opcion = input("   Selecciona una opcion (1-4): ").strip()
        
        if opcion == '1':
            limpiar_pantalla()
            mostrar_titulo()
            
            origen = seleccionar_nodo("[>>] Nodo de ORIGEN")
            if origen is None:
                continue
            
            limpiar_pantalla()
            mostrar_titulo()
            
            destino = seleccionar_nodo("[<<] Nodo de DESTINO")
            if destino is None:
                continue
            
            if origen == destino:
                print("\n[!] Error: El origen y el destino deben ser distintos.")
                pausa()
                continue
            
            # Solicitar velocidad si se desea
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
            ejecutar_simulacion(origen, destino, velocidad)
            pausa()
        
        elif opcion == '2':
            limpiar_pantalla()
            mostrar_titulo()
            
            print("\n[*] INFORMACION DE ESTACIONES:")
            print("-" * 70)
            
            for nodo_id, nodo in NODOS.items():
                print(f"\n  [ {nodo_id} ]")
                print(f"     Nombre: {nodo.nombre}")
                
                # Mostrar conexiones
                conexiones = GRAFO[nodo_id]
                if conexiones:
                    print(f"     Conexiones:")
                    for vecino, peso in sorted(conexiones):
                        print(f"        -> {vecino:12} : {peso:2d}m")
            
            print()
            pausa()
        
        elif opcion == '3':
            print("\n[*] La velocidad se puede ajustar durante la ejecucion.")
            print("    En el menu principal, selecciona la opcion 1 y luego")
            print("    elige la velocidad deseada.")
            pausa()
        
        elif opcion == '4':
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