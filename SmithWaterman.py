import numpy as np


class SmithWaterman:

    def smith_waterman(self, seq1, seq2, match, mismatch, gap):
        # matriz con scores
        S = np.zeros((len(seq2) + 2, len(seq1) + 2), dtype=object)

        # matriz traceback con direcciones
        T = np.zeros((len(seq2) + 2, len(seq1) + 2), dtype=object)

        # inicializar
        T[0, 2:] = list(seq1)
        T[2:, 0] = list(seq2)
        S[0, 2:] = list(seq1)
        S[2:, 0] = list(seq2)
        for i in range(2, len(seq2) + 2):
            T[i][1] = "*"
        for j in range(2, len(seq1) + 2):
            T[1][j] = "*"
        T[1][1] = "*"

        # calcular score de cada espacio de la matriz
        for i in range(2, len(seq2) + 2):
            # primero calcula los valores de top, left y diagonal
            for j in range(2, len(seq1) + 2):
                top = S[i - 1][j] + gap
                left = S[i][j - 1] + gap
                if S[i][0] == S[0][j]:
                    diag = S[i - 1][j - 1] + match
                else:
                    diag = S[i - 1][j - 1] + mismatch

                # luego compara los valores para ver el maximo y lo asigna a la casilla de la tabla de scores, si es negativo le asigna un 0
                if max(top, left, diag) < 0:
                    S[i][j] = 0
                else:
                    S[i][j] = max(top, left, diag)

                # para asignar la casilla de la tabla de traceback se determina cual, si top, left o diag fue el asignado o si es 0 pone *
                if S[i][j] == 0:
                    T[i][j] = "*"
                elif S[i][j] == top:
                    T[i][j] = "↑"
                elif S[i][j] == left:
                    T[i][j] = "←"
                elif S[i][j] == diag:
                    T[i][j] = "↖"

        return T, S

    # encontar la casilla con el score mayor para iniciar el alineamiento local
    def encontrar_max_score(self, matriz, filas, columnas):
        mayor = -1
        listaMayores = list()
        for i in range(2, filas+1):
            isla = list()
            for j in range(2, columnas+1):
                if not isinstance(matriz[i][j], str):
                    if matriz[i][j] >= mayor and matriz[i][j] != 0:
                        mayor = matriz[i][j]
                        fila = i
                        columna = j
                        isla.append(fila)
                        isla.append(columna)
                        isla.append(mayor)
                        listaMayores.append(isla.copy())
                        isla.clear()
            for item in listaMayores:
                if item[2] != mayor:
                    listaMayores.remove(item)
        return listaMayores

        # para resultado final de alineamiento con traceback

    def secuencia_alineada(self, matrizRuta, fila, columna, seq1, seq2, listo):
        secuencia1 = ""
        secuencia2 = ""

        while not listo:
            # evalua si se debe avanzar en diagonal, arriba o abajo

            # determina la fila y la columna con el mayor scoring
            # si avanza en diagonal el valor esta alineado y lo asigna al string
            if matrizRuta[fila][columna] == "↖":
                secuencia1 += seq1[columna - 2]
                secuencia2 += seq2[fila - 2]
                fila = fila - 1
                columna = columna - 1

            # si avanza hacia arriba, introduce un gap en la secuencia de arriba, solo cambia el valor de la fila
            elif matrizRuta[fila][columna] == "↑":
                secuencia1 += "-"
                secuencia2 += seq2[fila - 2]
                fila = fila - 1
            # si avanza hacia izquierda, introduce un gap en la secuencia de la izquierda, solo cambia el valor de la columna
            elif matrizRuta[fila][columna] == "←":
                secuencia1 += seq1[columna - 2]
                secuencia2 += "-"
                columna = columna - 1
            else:
                listo = True
        # retorna las secuencias
        return secuencia1[::-1], secuencia2[::-1]  # para darle vuelta porque el alineamiento es al reves
