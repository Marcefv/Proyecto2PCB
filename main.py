import numpy as np
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from SmithWaterman import SmithWaterman as sw
from NeedlemanWunsch import NeedlemanWunsch as nw
from gi.repository.Gdk import RGBA
from gi.repository.Gdk import Color

class Main:
    def __init__(self):
        # cargar glade
        self.builder = Gtk.Builder()
        self.builder.add_from_file("Glade2.glade")
        self.builder.connect_signals(self)

        # objeto ventana
        self.window = self.builder.get_object("window")

        # nombrar objetos importantes de la interfaz de glade
        self.matchValue = self.builder.get_object("matchValue")
        self.mismatchValue = self.builder.get_object("mismatchValue")
        self.gapValue = self.builder.get_object("gapValue")
        self.secuencia1 = self.builder.get_object("seq1Txt")
        self.secuencia2 = self.builder.get_object("seq2Txt")
        self.scoring = self.builder.get_object("scoringLbl")
        self.scrolled = self.builder.get_object("scrolled")
        self.text_view = self.builder.get_object("text_view")

        # mostrar elementos
        self.window.show()

    # variable para determinar cual algoritmo usar
    algoritmoNW = True

    # Cerrar ventana con boton x de ventana
    def on_Window_destroy(self, window):
        Gtk.main_quit()

    # cerrar con boton del toolbar
    def on_salirBtn_clicked(self, btn):
        Gtk.main_quit()

    # volver a valores default de datos de entrada
    def on_clearBtn_clicked(self, btn):

        self.matchValue.set_value(1)
        self.mismatchValue.set_value(-1)
        self.gapValue.set_value(-2)
        self.secuencia2.set_text("")
        self.secuencia1.set_text("")
        self.borrar_text_view()
        self.scoring.set_text("")

        while self.scrolled.get_child() is not None:
            self.scrolled.remove(self.scrolled.get_child())

    # boton para elegir algoritmo nw
    def on_radiobutton2_toggled(self, widget):
        if widget.get_active():
            self.algoritmoNW = True

    # para elegir algoritmo sw
    def on_radiobutton1_toggled(self, widget):
        if widget.get_active():
            self.algoritmoNW = False

    # Metodo para generar ventana con mensaje de error
    def error(self, message):
        error_message = Gtk.MessageDialog(parent=None, flags=0, message_type=Gtk.MessageType.WARNING,
                                              buttons=Gtk.ButtonsType.OK,
                                              text=message)
        error_message.set_title("Error")
        error_message.run()
        error_message.destroy()

    # funcion para generar alineamiento
    def on_alinearBtn_clicked(self, widget):

        # valida si los datos de secuencias no van vacios
        if self.secuencia1.get_text() == "" or self.secuencia2.get_text() == "":
            self.error("Ingrese una secuencia para alinear")
            return

        # secuencias
        seq1 = self.secuencia1.get_text()
        seq2 = self.secuencia2.get_text()

        try:
            # algoritmo a utilizar
            if self.algoritmoNW:
                ned = nw()
                matrices = ned.needlman_wunsch(seq1, seq2, match=self.matchValue.get_value_as_int(),
                                                   mismatch=self.mismatchValue.get_value_as_int(),
                                                   gap=self.gapValue.get_value_as_int())
                alineadas = ned.secuencia_alineada(matrices[0], len(seq2) + 1, len(seq1) + 1, seq1, seq2, False)
            else:
                smi = sw()
                matrices = smi.smith_waterman(seq1, seq2, match=self.matchValue.get_value_as_int(),
                                                   mismatch=self.mismatchValue.get_value_as_int(),
                                                   gap=self.gapValue.get_value_as_int())
                mayor = smi.encontrar_max_score(matrices[1], len(seq2) + 1, len(seq1) + 1)
                if len(mayor) > 1:
                    islas = list()
                    for isla in range(len(mayor)):
                        alineado = smi.secuencia_alineada(matrices[0], mayor[isla][0], mayor[isla][1], seq1, seq2, False)
                        islas.append(alineado)
                else:
                    alineadas = smi.secuencia_alineada(matrices[0], mayor[0][0], mayor[0][1], seq1, seq2, False)
        except:
            self.error("Hubo un error con las secuencias, no se puede procesar")
            return

        matrizScore = matrices[1]
        matrizRuta = matrices[0]

        texto = ""
        # muestra scoring optimo en interfaz
        if self.algoritmoNW:
            self.scoring.set_text(str(matrizScore[len(seq2) + 1][len(seq1) + 1]))
            texto = texto + "Secuencia 1: " + alineadas[0] + "\n Secuencia 2: " + alineadas[1]
        elif len(mayor) > 1:
            number = 1
            for isla in islas:
                texto = texto + "Isla :"+str(number)+" : \n Secuencia 1: " + isla[0] + "\n Secuencia 2: " + isla[1] + "\n\n"
                number += 1
            self.scoring.set_text(str(mayor[0][2]))
        else:
            self.scoring.set_text(str(mayor[0][2]))
            texto = texto + "Secuencia 1: " + alineadas[0] + "\n Secuencia 2: " + alineadas[1]

        #muestra secuencias alineadas
        self.llenarTextView(texto)

        #crea matriz para mostrar en tabla
        m = self.matriz_for_show(matrizScore, matrizRuta, seq1, seq2)
        print(m)
        #crea tabla en la que se muestra la matriz
        if self.algoritmoNW:
            self.tablaFinal(m)
        else:
            mayores = smi.encontrar_max_score(m, (len(seq2) * 2) + 1, (len(seq1)*2) + 1)
            self.tablaFinal(m, mayores)


    # matriz para mostrar en tabla
    def matriz_for_show(self, matrizScore, matrizRuta, seq1, seq2):
        #crea matriz y coloca fila con secuencias y valores inciales
        fs= np.zeros(((len(seq2) * 2) + 2, (len(seq1)*2) + 2), dtype=object)
        fs[0:,0:] = ""
        # inicializar
        fs[0, 3::2] = list(seq1)
        fs[3::2, 0] = list(seq2)
        fs[1, 3::2] = matrizScore[1, 2:]
        fs[3::2, 1] = matrizScore[2:, 1]
        fs[1, 2::2] = matrizRuta[1, 2:]
        fs[2::2, 1] = matrizRuta[2:, 1]
        fs[1][1] = 0
        ien2 = 2
        jen2 = 2

        #llena con el resto de valores de las matrices
        for i in range(3, (len(seq2) * 2) + 2):
            if i % 2 != 0:
                for j in range(3,  (len(seq1) * 2) + 2):
                    if j % 2 != 0:
                        fs[i][j] = matrizScore[ien2][jen2]
                        if "↖" in matrizRuta[ien2][jen2]:
                            fs[i-1][j-1] = "↖"
                        if "↑" in matrizRuta[ien2][jen2]:
                            fs[i-1][j] = "↑"
                        if "←" in matrizRuta[ien2][jen2]:
                            fs[i][j-1] = "←"
                        jen2 = jen2+1
                ien2 = ien2+1
                jen2 = 2
        return fs

    #para crear la tabla final
    def tablaFinal(self, matrizfs, islas = None):

        # elimina grid si hay una
        while self.scrolled.get_child() is not None:
            self.scrolled.remove(self.scrolled.get_child())

        grid = Gtk.Grid()
        self.scrolled.add_with_viewport(grid)

        #establece tamanio del grid
        dim = matrizfs.shape
        filas = dim[0]
        columnas = dim[1]

        #en esta variable van a estar las celdas que se colorean
        colorear = list()

        #determinar las celdas que se colorean
        if self.algoritmoNW:
            colorear = self.colorear_celda(matrizfs, filas-1, columnas-1)
        else:
            for isla in islas:
                lista = self.colorear_celda(matrizfs, isla[0], isla[1])
                colorear.extend(lista.copy())


        celdasTabla = {}
        rgba = RGBA()
        rgba.parse("#7f7f7f")
        rgba.to_string()

        #llenar celdas
        for i in range(filas):
            for j in range(columnas):
                if isinstance(matrizfs[i][j], str):
                    celdasTabla["c9999{0},{1}".format(i, j)] = Gtk.Label()
                    celdasTabla["c9999{0},{1}".format(i, j)].set_text(matrizfs[i][j])
                    if "c9999{0},{1}".format(i, j) in colorear:
                        celdasTabla["c9999{0},{1}".format(i, j)].modify_fg(Gtk.StateFlags.NORMAL,  Color(50000, 0,0))
                else:
                    celdasTabla["c9999{0},{1}".format(i, j)] = Gtk.Entry()
                    celdasTabla["c9999{0},{1}".format(i, j)].set_property("editable", False)
                    celdasTabla["c9999{0},{1}".format(i, j)].set_text(str(matrizfs[i][j]))
                    if "c9999{0},{1}".format(i, j) in colorear:
                        celdasTabla["c9999{0},{1}".format(i, j)].override_background_color(Gtk.StateFlags.NORMAL, rgba)
                grid.attach(celdasTabla["c9999{0},{1}".format(i, j)], j, i, 1, 1)
        grid.show_all()

    #determinar las celdas que se colorean
    def colorear_celda(self, matriz, fila, columna):
        colorear = list()

        if self.algoritmoNW:
            colorear.append("c9999{0},{1}".format(1, 1))
            while (fila != 1) or (columna != 1):
                if not isinstance(matriz[fila][columna], str):
                    colorear.append("c9999{0},{1}".format(fila, columna))
                    if matriz[fila-1][columna-1] != "" and fila-1 != 0 and columna - 1 != 0:
                        fila = fila - 1
                        columna = columna - 1
                    elif matriz[fila-1][columna] != "" and fila-1 != 0:
                        fila = fila - 1
                    elif matriz[fila][columna-1] != "" and columna - 1 != 0:
                        columna = columna - 1
                else:
                    colorear.append("c9999{0},{1}".format(fila, columna))
                    if matriz[fila][columna] == "↖":
                        fila = fila - 1
                        columna = columna - 1
                    if matriz[fila][columna] == "↑":
                        fila = fila - 1
                    if matriz[fila][columna] == "←":
                        columna = columna - 1
            return colorear
        else:
            while matriz[fila][columna] != 0:
                if not isinstance(matriz[fila][columna], str):
                    colorear.append("c9999{0},{1}".format(fila, columna))
                    if matriz[fila-1][columna-1] != "" and fila-1 != 0 and columna - 1 != 0:
                        fila = fila - 1
                        columna = columna - 1
                    elif matriz[fila-1][columna] != "" and fila-1 != 0:
                        fila = fila - 1
                    elif matriz[fila][columna-1] != "" and columna - 1 != 0:
                        columna = columna - 1
                else:
                    colorear.append("c9999{0},{1}".format(fila, columna))
                    if matriz[fila][columna] == "↖":
                        fila = fila - 1
                        columna = columna - 1
                    if matriz[fila][columna] == "↑":
                        fila = fila - 1
                    if matriz[fila][columna] == "←":
                        columna = columna - 1
            return colorear

    #llenar el textview con las secuencias alineadas
    def llenarTextView(self, texto):
        self.borrar_text_view()
        buffer = self.text_view.get_buffer()
        self.text_view.get_buffer().insert(buffer.get_start_iter(), texto)

    #borrar informacion del text view
    def borrar_text_view(self):
        buffer = self.text_view.get_buffer()
        buffer.delete(
            buffer.get_start_iter(),
            buffer.get_end_iter())

main = Main()
Gtk.main()