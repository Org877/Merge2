# Clases de complejidad y benchmarking
- P: problemas resolubles en tiempo polinomial (ordenamiento: insertion O(n²), merge O(n log n)).
- NP: una solución propuesta (certificado) se VERIFICA en tiempo polinomial; encontrarla por fuerza bruta es exponencial (Subset-Sum O(2^n)) o factorial (TSP O(n!)). Se desconoce si P = NP.
- NSPACE / NL: REACHABILITY en grafos dirigidos. El teorema de Savitch la resuelve de forma determinista con O(log² n) de espacio, pagando más tiempo.
- El tiempo medido depende de la máquina; lo importante es CÓMO CRECE al aumentar n.
- Error común: creer que "NP" significa "no polinomial"; significa "polinomial no determinista".
