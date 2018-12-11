import logging
import threading
from datetime import timezone

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from DataBase.DataBaseQuery import findProcesoCalculado, getListasCalculos, getNombreProcesosCalculados, getNameEquipo
from DataBase.SaveAnalysisProcess import saveAnalysis
from diagrams.views import resultProcess
from processes.ProcesoSeparacion import *
from processes.forms import startProcessForm, MaterialForm, ProcesoForm
from processes.tables import MaterialPrecioTable

global densities, idx_plastics, economical_parameters, compatibility, yield_table, impurity, cocktail, idx_processes


def newProcess_view(request):
    form = startProcessForm()
    if request.method == 'POST':
        form = startProcessForm(request.POST)

        if form.is_valid():
            form.cleaned_data['idprocesos']
            existe,anioInicial, anioFinal, best_combi_vector, best_profit_vector, optimal_intermediate_outputs, optimal_npv_vector, profit_global, processes_vector=processMainAnalisys(request)
            if (existe==-1):
                obj=form.save()
                threadSaveAnalysis = threading.Thread(target=saveAnalysis, args=(obj,anioInicial, anioFinal, best_combi_vector, best_profit_vector, optimal_intermediate_outputs, optimal_npv_vector, profit_global, processes_vector,))
                threadSaveAnalysis.start()
            else:
                best_profit_vector, optimal_npv_vector,optimal_intermediate_outputs=getListasCalculos(existe)
            nombreEquipo=getNameEquipo(request.POST.getlist('idequipo'))

            return resultProcess(request, best_profit_vector, optimal_npv_vector,
                                 optimal_intermediate_outputs,nombreEquipo,anioInicial['anio'],anioFinal['anio'])  # render(request, 'diagrams/diagramassankey.html')
            #saveAnalysis(obj,anioInicial, anioFinal, best_combi_vector, best_profit_vector, optimal_intermediate_outputs, optimal_npv_vector, profit_global, processes_vector)
        else:
            error = form.errors
            contexto = {
                'form': form,
                'error': error
            }
        #resultProcess(request)
#        return resultProcess(request,best_profit,optimal_npv,optimal_intermediate_outputs_vector)#render(request, 'diagrams/diagramassankey.html')
    else:
        form = startProcessForm()
        queryset = MaterialPrecio.objects.filter(anio=2018)
        table = MaterialPrecioTable(queryset)
        contexto = {
            'form': form,
            'table': table
        }
    return render(request, 'processes/startprocess.html', contexto)

def loadEquipoEntrada(request):
    idequipo = request.GET.get('idequipo')
    equipoEnt = EquipoEntrada.objects.filter(idequipo=idequipo).order_by('anio')
    return render(request, 'processes/selectOptionEquipoEntrada.html', {'equipoEnt': equipoEnt})

def loadEquipoEntradaFinal(request):
    idequipoentrada = request.GET.get('idequipoentrada')
    equipoEnt = list(EquipoEntrada.objects.filter(idequipoentrada=idequipoentrada))
    equipoFin = EquipoEntrada.objects.filter(idequipo=equipoEnt[0].idequipo,anio__gte=equipoEnt[0].anio).order_by('anio')
    return render(request, 'processes/selectOptionEquipoEntrada.html', {'equipoEnt': equipoFin})

def processMainAnalisys(request):
    global numeroMateriales
    start = time.time()
    start_total = time.time()

    listaProcesos = (request.POST.getlist('idprocesos'))
    idequipo = (request.POST.getlist('idequipo'))

    listMaterialesEqui = getListaMagterialesEquipo(idequipo)
    matrizProcesoMaterial, listaParametrosProcesos, listaMaterialesMatrizProcesses = getParametrosProcesos(listaProcesos, idequipo, listMaterialesEqui)
    numeroMateriales = listMaterialesEqui
    end = time.time()

    loading = end - start
    print('Loading time is', loading, 'seconds', '\n')
    # Calling the main function

    start = time.time()

    anioInicial = \
    EquipoEntrada.objects.values('anio').filter(idequipoentrada__exact=int(request.POST.get('idequipoentradainicio')))[
        0]
    anioFinal = \
    EquipoEntrada.objects.values('anio').filter(idequipoentrada__exact=int(request.POST.get('idequipoentradafinal')))[0]
    precios = list(MaterialPrecio.objects.filter(anio__exact=int(request.POST.get('idanioprecio'))).order_by('idmaterial'))
    numDensidades = Densidad.objects.count()
    aux = []
    for pre in precios:
        aux.append(float(pre.precioreventa))
    precios = aux[:]

    existeCalculo = findProcesoCalculado(request.POST.get('idanioprecio'), request.POST.get('idequipoentradainicio'),
                                   request.POST.get('idequipoentradafinal'), idequipo[0], request.POST.getlist('idprocesos'))

    best_combi_vector = []
    best_profit_vector = []
    optimal_intermediate_outputs = []
    optimal_npv_vector = []
    profit_global = []
    processes_vector = []
    if (existeCalculo==-1):
        best_combi_vector, best_profit_vector, optimal_intermediate_outputs, optimal_npv_vector, profit_global, processes_vector = getfunc_separation(
        idequipo, matrizProcesoMaterial, listaParametrosProcesos, precios, [0, numDensidades - 1],
        anioInicial,
        anioFinal, listMaterialesEqui,listaProcesos)
    else:
        best_combi_vector=[]
        best_profit_vector=[]
        optimal_intermediate_outputs=[]
        optimal_npv_vector=[]
        profit_global=[]
        processes_vector=[]
    end = time.time()

    execution = end - start
    print('Execution time is', execution, 'seconds', '\n')
    start = time.time()
    end = time.time()
    writing = end - start
    print('Writing time is', writing, 'seconds', '\n')

    print('Finished running', '\n')
    end_total = time.time()

    total = end_total - start_total
    print('Total time is', total, 'seconds', '\n')

    return existeCalculo, anioInicial,anioFinal,best_combi_vector, best_profit_vector, optimal_intermediate_outputs, optimal_npv_vector, profit_global, processes_vector


print('PROCESO')


def getParametrosEconomicos():
    parametrosEconomicos = Parametroseconomicos.objects.all().values()[0]
    return parametrosEconomicos

def getListaMagterialesEquipo(idequipo):
    return list(
        Equipo.objects.values('materiales').filter(pk__in=idequipo))

def getProcesoCalculadoLista_view(request):
    listaProcesoCalculado=[]
    lista=ProcesoCalculado.objects.all()
    for proceso in lista:
        aux=[]
        aux.append(proceso.idprocesocalculado)
        aux.append(proceso.idequipo)
        aux.append(proceso.idequipoentradainicio.anio)
        aux.append(proceso.idequipoentradafinal.anio)
        aux.append(proceso.idanioprecio)
        aux.append(getNombreProcesosCalculados(proceso.idprocesocalculado))
        listaProcesoCalculado.append(aux)
    args = {
        'resultado': listaProcesoCalculado
    }
    return render(request, 'processes/procesocalculado_list.html', args)

def getResultadosListView(request):
    if request.method == 'POST':
        idcalculo=int(request.POST.get('calculoID'))
        nombreEquipo = (request.POST.get('nombreEquipo'))
        aInicial = int(request.POST.get('aInicial'))
        aFinal = int(request.POST.get('aFinal'))

        best_profit_vector, optimal_npv_vector, optimal_intermediate_outputs = getListasCalculos(idcalculo)
        return resultProcess(request, best_profit_vector, optimal_npv_vector,
                             optimal_intermediate_outputs,nombreEquipo,aInicial,aFinal)


############---------------VIEW--------------####################

###   Material
class MaterialCreateView(CreateView):
    model = Material
    form_class = MaterialForm
    success_url = reverse_lazy('material_list')

class MaterialListView(ListView):
    model = Material
    context_object_name = 'materiales'

class MaterialUpdateView(UpdateView):
    model = Material
    form_class = MaterialForm
    success_url = reverse_lazy('material_list')

###   Proceso
class ProcesoCreateView(CreateView):
    model = Proceso
    form_class = ProcesoForm
    success_url = reverse_lazy('proceso_list')

##   TABLAS

def tablaMaterialPrecio(request):
    idAnioPrecio = request.GET.get('anio')
    queryset=MaterialPrecio.objects.filter(anio=idAnioPrecio)
    table=MaterialPrecioTable(queryset)
    table.paginate(page=request.GET.get('page', 1), per_page=10)
    return render(request, 'processes/table_materialprecio.html', {'table': table})