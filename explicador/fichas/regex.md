# Conversión Regex -> AFN-ε -> AFD
- Algoritmo de Thompson: convierte la expresión regular en un AFN-ε con transiciones vacías (ε).
- Construcción de subconjuntos: elimina el no determinismo agrupando estados alcanzables por clausura-ε en estados del AFD.
- Ventaja: el AFD evalúa cualquier cadena de longitud m en tiempo lineal O(m) con un solo estado activo por paso.
