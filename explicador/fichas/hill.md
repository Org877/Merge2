# Hill-Climbing (escalada de colina)
- Desde el nodo actual avanza al vecino con mejor heurística; se detiene cuando ningún vecino mejora.
- No retrocede ni guarda alternativas: puede atascarse en un MÍNIMO LOCAL (o meseta) sin llegar al destino.
- Remedio habitual: reinicios aleatorios. Muy poco espacio: O(1) adicional.
- No garantiza solución ni optimalidad.
