# Algoritmos Probabilistas: Monte Carlo vs. Las Vegas
- Miller-Rabin (Monte Carlo): tiempo acotado; si detecta un testigo garantiza que n es compuesto; si pasa k rondas es probablemente primo con cota de error <= 4^(-k).
- Quicksort Aleatorizado (Las Vegas): elige pivotes al azar; siempre entrega el arreglo 100% ordenado (error 0), pero su tiempo varía entre ejecuciones con promedio O(n log n).
