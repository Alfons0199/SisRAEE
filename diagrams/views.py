from django.shortcuts import render

from DataBase.DataBaseQuery import getNombresMaterialesEquipoNombre, getTodosProcesos
from diagrams.analyzeDiagram import *

listaTotal=[]

global materiales
nombresProcesos=["XRF_Brominate","XRF_Phosphorous","XRT_FR","LIBS","Densities_1,03_upper","Densities_1,09_lower","Densities_1,15_upper","Densities_1,55_lower","Densities_1,095_upper","Densities_1,145_lower","Densities_1,185_lower"]

def resultProcess(request,best_profit,optimal_npv,optimal_intermediate_outputs,nombreEquipo,anioInicial, anioFinal):
    global nombresProcesos,materiales
    request.session['matrizprocesos'] = optimal_intermediate_outputs
    #nombresProcesos = getTodosProcesos()
    materiales= getNombresMaterialesEquipoNombre(nombreEquipo)
    inversion = vectorInvestment(best_profit)
    resultado=sequenceProcess(optimal_intermediate_outputs,anioInicial, anioFinal)
    resultadoNombre=nombresListaProcesos(resultado,nombresProcesos,inversion,optimal_npv,anioInicial, anioFinal)


    args = {
        'resultadoTotal': resultadoNombre,'equipo':nombreEquipo,'anio':anioInicial
    }
    return render(request, 'diagrams/diagramassankey.html',args)

def generateSankey(request):

    colorNodo = []
    anioCalculo=0
    procesos=''
    labelNodo = []
    source = []
    values = []
    target = []
    colorLink = []
    labelLink = []
    listaTotal=request.session['matrizprocesos']

    materiales = ["ABS", "HIPS", "PC/ABS PFr", "HIPPS/PPE PFr", "ABS/PMMA", "HIPS BFr", "ABS BFr"]

    idProcess=0
    if request.method == 'POST':
        if str(request.POST.get('diagramsID')) != 'None':
            idProcess = int(request.POST.get('diagramsID'))
            referencia = int(request.POST.get('referencia'))
            procesos = (request.POST.get('procesos'))
            aux=procesos.split("'")
            procesos=''
            for proc in aux:
                if proc!=']' and proc!='[' and proc!=', ':
                    if procesos!='':
                        procesos=procesos+' -> '+proc
                    else:
                        procesos = proc
            anio = int(request.POST.get('anio'))
            anioCalculo=anio+referencia
            lista = listaTotal[idProcess-1]
            listaPara=[]
            listaPara.append(lista[referencia])
            colorNodo, labelNodo, source, values, target, colorLink, labelLink = parametrosSankey(materiales, listaPara, 0)

    args = {
        'colorNodo': colorNodo, 'labelNodo': labelNodo, 'source': source, 'values': values, 'target': target,
        'colorLink': colorLink, 'labelLink': labelLink, 'anio': anioCalculo,'idProcesos':idProcess,'procesos':procesos
    }
    print(colorNodo)
    print(labelNodo)
    print(source)
    print(values)
    print(target)
    print(colorLink)
    print(labelLink)


    return render(request,'diagrams/sankey.html',args)

def vectorInvestment(vector):

    #vector=[[-90000.0, 12927.755724547314, 67500.0], [0, -98529.6, 0], [-145000.0, -102921.73633843375, 124285.71428571429], [-145000.0, -110454.06765852516, 124285.71428571429], [-145000.0, -110718.69836082301, 124285.71428571429], [-580000.0, -9502.951137066935, 497142.85714285716], [-580000.0, -10079.90618964308, 497142.85714285716], [-580000.0, -10198.585337120574, 497142.85714285716], [-580000.0, -10548.4287093514, 497142.85714285716], [-580000.0, -10951.403081891476, 497142.85714285716], [-580000.0, -12133.703141704958, 497142.85714285716]]
    #vector =[[-90000.0, 15779.71286716318, 67500.0], [0, -16529.702994445062, 0],
     #[-145000.0, -13224.079110827646, 124285.71428571429], [-145000.0, -13354.336909442776, 124285.71428571429],
     ##[-145000.0, -20100.11884124519, 124285.71428571429], [-225000.0, -31670.910937356733, 192857.14285714287],
     #[-290000.0, -16662.878288889013, 248571.42857142858], [-290000.0, -16790.53093153183, 248571.42857142858],
     #[-290000.0, -16794.494957627787, 248571.42857142858], [-290000.0, -16924.752756242902, 248571.42857142858],
     #[-290000.0, -16932.015752236126, 248571.42857142858]]
    vectorInversion=[]
    for list in vector:
        if list !=0:
            vectorInversion.append(list[0]*(-1))

    return vectorInversion