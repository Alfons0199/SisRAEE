from DataBase.DataBaseQuery import getTodosProcesos


def sequenceProcess(diagramaArray,anioInicial, anioFinal):


    diferenciaAnios=anioFinal-anioInicial+1
    vectorProcesos=[]
    for i in range(0,diferenciaAnios):
        secuenciaProcesos = []
        for diagrama in diagramaArray:
            if diagrama ==[]:
                break
            listaProceso = diagrama[i]
            aux = []
            anterior = ''
            num=0
            for lista in listaProceso:
                if str(lista[0])==anterior:
                    anterior = str(lista[1])
                    ban=''
                    for n in range (0,(num)):
                        listaaux=listaProceso[n]
                        if listaaux[0]==lista[0] and listaaux[1]==lista[1]:
                            ban=1
                            break
                    if ban=='':
                        if lista[1]!='':
                            aux.append(lista[1])

                num=num+1
            aux.append(i)
            secuenciaProcesos.append(aux)
        vectorProcesos.append(secuenciaProcesos)
    return vectorProcesos

def nombresListaProcesos(listaProcesosTotal,nombresProcesos,inversion,optimal_npv,anioInicial, anioFinal):

    listanombreprocesosTotal=[]
    cont = 1
    for listaProcesos in listaProcesosTotal:
        listanombreprocesos = []
        num = 1
        for listaP in listaProcesos:
            aux=[]
            aux.append(num)
            auxNombre = []
            for lista in range (len(listaP)-1):
                if listaP[lista] != '':
                    auxNombre.append(str(nombresProcesos[int(listaP[lista])]))
                else:
                    auxNombre.append(str(''))
            aux.append(auxNombre)
            aux.append(inversion[num-1][0])
            aux.append(round(float(inversion[num-1][cont]),2))#(round(float(optimal_npv[num - 1]),2))
            aux.append(listaP[len(listaP)-1])
            listanombreprocesos.append(aux)
            num=num+1
        cont=cont+1
        listanombreprocesosTotal.append(listanombreprocesos)
    return listanombreprocesosTotal

def parametrosSankey(materiales,salidaProceso,id):
    listaColorNodo = ["#f46a1a", "#4994CE", "#FABC13", "#7FC241", "#878787", "#66b431", "#3150b4", "#7a36ba", "#9e5757",
                      "#698424", "#ff4d6a", "#c662c6", "#70c6d2", "#a16363", "#4169E1", "#8B4513", "#FA8072",
                      "#f46a1a", "#4994CE", "#FABC13", "#7FC241", "#878787", "#66b431", "#3150b4", "#7a36ba", "#9e5757",
                      "#698424", "#ff4d6a", "#c662c6", "#70c6d2", "#a16363", "#4169E1", "#8B4513", "#FA8072"
                      ]
    listaColorLink = ["#f79055", "#8abbe0", "#fbc83c", "#a7d57c", "#D3D3D3", "#8bd25b", "#6b84d6", "#7a36ba", "#ba8282",
                      "#acd053", "#FFC0CB", "#DDA0DD", "#B0E0E6", "#BC8F8F", "#7f9aeb", "#eba36f", "#fcafa6",
                      "#f79055", "#8abbe0", "#fbc83c", "#a7d57c", "#D3D3D3", "#8bd25b", "#6b84d6", "#7a36ba", "#ba8282",
                      "#acd053", "#FFC0CB", "#DDA0DD", "#B0E0E6", "#BC8F8F", "#7f9aeb", "#eba36f", "#fcafa6"
                      ]
    listaColor = ["#00FFFF", "#00008B", "#008B8B", "#B8860B", "#A9A9A9", "#006400", "#A9A9A9", "#BDB76B", "#8B008B",
                  "#556B2F", "#FF8C00", "#9932CC", "#8B0000", "#E9967A", "#8FBC8F", "#483D8B", "#2F4F4F", "#2F4F4F",
                  "#00CED1", "#9400D3", "#FF1493", "#00BFFF", "#696969", "#696969", "#1E90FF", "#B22222", "#FFFAF0",
                  "#228B22", "#FF00FF", "#DCDCDC", "#F8F8FF", "#FFD700", "#DAA520", "#808080", "#008000", "#ADFF2F",
                  "#808080", "#F0FFF0", "#FF69B4", "#CD5C5C", "#4B0082", "#FFFFF0", "#F0E68C", "#E6E6FA", "#FFF0F5",
                  "#7CFC00", "#FFFACD", "#ADD8E6", "#F08080", "#E0FFFF", "#FAFAD2", "#D3D3D3", "#90EE90", "#D3D3D3",
                  "#FFB6C1", "#FFA07A", "#20B2AA", "#87CEFA", "#778899", "#778899", "#B0C4DE", "#FFFFE0", "#00FF00",
                  "#32CD32", "#FAF0E6", "#FF00FF", "#800000", "#66CDAA", "#0000CD", "#BA55D3", "#9370D8", "#3CB371",
                  "#7B68EE", "#00FA9A", "#48D1CC", "#C71585", "#191970", "#F5FFFA", "#FFE4E1", "#FFE4B5", "#FFDEAD",
                  "#000080", "#FDF5E6", "#808000", "#6B8E23", "#FFA500", "#FF4500", "#DA70D6", "#EEE8AA", "#98FB98",
                  "#AFEEEE", "#D87093", "#FFEFD5", "#FFDAB9", "#CD853F", "#FFC0CB", "#DDA0DD", "#B0E0E6", "#800080",
                  "#FF0000", "#BC8F8F", "#4169E1", "#8B4513", "#FA8072"]

    nombresProcesos = [" XRF_Brominate", " XRF_Phosphorous", " XRT_FR",
                       " LIBS", " Densities_1,03_upper",
                       " Densities_1,09_lower", " Densities_1,15_upper",
                       " Densities_1,55_lower", " Densities_1,095_upper",
                       " Densities_1,145_lower", "Proceso Densities_1,185_lower"]
    nombresProcesos = getTodosProcesos()
    idprocesos = []
    colorNodo = []
    colorLink = []
    labelNodo = []
    source = []
    target = []
    values = []
    labelLink = []
    salida = salidaProceso[id]
    listaOrden=orderProcess(salida)
    nodoactual = -1
    masaTotalEntrada=0
    for filaProceso in listaOrden:
        if filaProceso[2]=='':
            fila = salida[0]
            masas = fila[len(fila) - 1]
            masaTotalEntrada =sumarLista(masas)
            for n in range(0,len(materiales)):
                labelNodo.append(str(materiales[n]) + " " + str(round(masas[n],2)) + "Tn")
                colorNodo.append(str(listaColorNodo[n]))
            materiales.append("OTROS")
        else:
            fila = salida[filaProceso[3]]#tomo la fila que es la entrada para este proceso
            masas = fila[len(fila) - 1]#valor de las masas
            if filaProceso[2]==0:#cuando es la primera salida del proceso
                posicionpeoceso = filaProceso[1]#el id del proceso
                labelNodo.append(nombresProcesos[posicionpeoceso])
                colorNodo.append("#adad85")  #color del proceso
                nodoactual = len(labelNodo) - 1

                if filaProceso[0] == '':
                    for idmaterial in range(0,len(materiales)-1):
                        source.append(idmaterial)
                        target.append(nodoactual)
                        values.append(round(masas[idmaterial],2))
                        colorLink.append(str(listaColorLink[idmaterial]))
                        labelLink.append(str(pordentaje(masas[idmaterial], masaTotalEntrada))+" %")
                elif filaProceso[0]!='':
                    for idmaterial in range(0, len(materiales) - 1):
                        source.append(idprocesos[filaProceso[3]])
                        target.append(nodoactual)
                        values.append(round(masas[idmaterial],2))
                        colorLink.append(str(listaColorLink[idmaterial]))
                        labelLink.append("")
            if filaProceso[4]==0 and filaProceso[5]!='/' and filaProceso[5]!='':                     ##################CAMBIOOOOOOOOO  and filaProceso[5]!=''
                fila = salida[listaOrden.index(filaProceso)]
                masas = fila[len(fila) - 1]
                if filaProceso[5]!=-1:
                    labelNodo.append(str(materiales[filaProceso[5]]))
                    colorNodo.append(str(listaColorNodo[filaProceso[5]]))
                    for j in range (0,len(masas)):
                        source.append(nodoactual)
                        target.append(len(labelNodo)-1)
                        values.append(round(masas[j],2))
                        colorLink.append(str(listaColorLink[j]))
                        labelLink.append("")
                else:
                    labelNodo.append(str(materiales[len(materiales) - 1]))
                    colorNodo.append("#FB0202")
                    for j in range(0, len(masas)):

                        source.append(nodoactual)
                        target.append(len(labelNodo) - 1)
                        values.append(round(masas[j],2))
                        colorLink.append(str(listaColorLink[j]))
                        labelLink.append("")
        idprocesos.append(nodoactual)


    return colorNodo, labelNodo, source, values, target, colorLink, labelLink

def orderProcess(lista):
    listaProcesos=[]
    num=0
    for i in range (len(lista)):
        fila=lista[i]
        aux=[]
        aux.append(fila[0])#Proceso anterior
        aux.append(fila[1])#proceso actual
        aux.append(fila[2])#numero de salida
        if len(listaProcesos)==0:
            aux.append('')#salida-->entrada actual proceso

        else:
            if fila[2]==0:
                index,listaProcesos=numeroEntrada(listaProcesos,fila[0])
                aux.append(index)

            else:
                filaanterior=listaProcesos[len(listaProcesos)-1]
                aux.append(filaanterior[3])

        aux.append(0)  # bandera define salida final o entrada, 0 entrada, 1 salida final
        aux.append(fila[3])
        listaProcesos.append(aux)
        num=num+1
    print('listaProcesos: ',listaProcesos)
    return listaProcesos

def numeroEntrada(tablaProceso,procesoPrevio):
    index=-1
    for fila in tablaProceso:
        if fila[4]==0 and fila[1]==procesoPrevio:
            index=tablaProceso.index(fila)
            fila[4]=1
            tablaProceso[index]=fila
            break
    return index,tablaProceso

def sumarLista(lista):
    sum=0
    for i in range(0,len(lista)):
        sum=sum+lista[i]
    return sum

def pordentaje(subtotal,total):
    por=(subtotal/total)*100
    por=round(por,2)
    return por

def appendLabelColorNodoColorLink(labelNodo,colorNodo,colorLink,vlabelNodo,vcolorNodo,vcolorLink):
    labelNodo.append(vlabelNodo)
    if vlabelNodo=="OTROS":
        colorNodo.append("#FD0000")
        colorLink.append("#F74343")
    else:
        colorNodo.append(vcolorNodo)
        colorLink.append(vcolorNodo)

    return labelNodo,colorNodo,colorLink
