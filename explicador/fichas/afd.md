# AFD (autómata finito determinista)
- Definición: (Q, Σ, δ, q0, F). δ: Q×Σ→Q es una función: exactamente un destino por estado y símbolo.
- Idea clave: se lee la palabra símbolo a símbolo siguiendo δ desde q0. Se acepta si el estado final está en F.
- Reconoce exactamente los lenguajes regulares. Tiempo de simulación: O(|w|).
- Error común: aceptar solo por "llegar a un estado de aceptación" a mitad de la palabra; debe terminar de leerla completa. Si falta una transición, la palabra se rechaza.
