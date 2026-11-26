# Auditoría Estática de Complejidad (AST)
- El módulo ast analiza el árbol sintáctico del código Python sin ejecutarlo.
- Cada nivel de bucles anidados (for/while) multiplica el orden polinomial: k niveles sugieren O(n^k).
- Múltiples llamadas recursivas dentro de una misma función sugieren crecimiento exponencial O(2^n).
