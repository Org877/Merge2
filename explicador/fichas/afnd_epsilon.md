# AFND-ε
- Añade transiciones ε: cambios de estado sin consumir símbolo.
- ε-clausura(S): todos los estados alcanzables desde S usando solo transiciones ε (incluye a S).
- Simulación: empezar con ε-clausura({q0}); por cada símbolo: mover y volver a aplicar ε-clausura.
- Reconoce los mismos lenguajes regulares que AFD y AFND.
- Error común: olvidar aplicar la ε-clausura al estado inicial.
