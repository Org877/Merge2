# AFND (autómata finito no determinista)
- δ: Q×Σ→P(Q): un estado y símbolo pueden llevar a varios estados (o a ninguno).
- Simulación: se mantiene el CONJUNTO de estados activos; en cada símbolo se unen todos los destinos. Se acepta si algún estado activo final está en F.
- Equivale en poder a un AFD (construcción de subconjuntos), pero puede necesitar hasta 2^n estados al convertirlo.
- Error común: pensar que "adivina" el camino correcto; en realidad explora todos los caminos a la vez.
