
def getPreciosAnio(anio):

    from processes.models import MaterialPrecio
    listaPrecios=list(MaterialPrecio.objects.filter(anio=anio))
    lista="|| "
    for lstPre in listaPrecios:
        lista=lista+str(lstPre)+" || "
    return lista

def findProcesoCalculado(idanioprecio, idequipoentradainicio, idequipoentradafinal, idequipo,idprocesos):
    from processes.models import ProcesoCalculado
    procesoCalculado=(ProcesoCalculado.objects.filter(idanioprecio=idanioprecio,
    idequipoentradainicio=idequipoentradainicio, idequipoentradafinal=idequipoentradafinal, idequipo=idequipo))
    for procesoCal in procesoCalculado:
        listaProcesos=procesoCal.idprocesos.all()
        lenProcesosBuscdo=len(listaProcesos)
        lenProcesosParametro = len(idprocesos)
        cont=0
        if (lenProcesosBuscdo == lenProcesosParametro):
            for procesos in (listaProcesos):
                if (str(procesos.idproceso) in idprocesos):
                    cont=cont+1
            if (cont==lenProcesosBuscdo):
                return procesoCal.idprocesocalculado
    return -1

def getListasCalculos(idprocesocalculado):
    from processes.models import ProcesoCombinacion,ProcesoSeparacionId, ProcesoSeparacion, Masasalida
    procesoSeparacionId=list(ProcesoSeparacionId.objects.values('idprocesosseparacionid').filter(idprocesocalculado=idprocesocalculado))
    print(procesoSeparacionId[0]['idprocesosseparacionid'])
    listaProcesoSeparacion=ProcesoSeparacion.objects.filter(idprocesosseparacionid=procesoSeparacionId[0]['idprocesosseparacionid']).order_by('secuenciaprocesoseparacion')
    best_profit_vector=[]
    optimal_npv_vector=[]
    optimal_intermediate_outputs=[]
    for best_profit in listaProcesoSeparacion:
        aux=[]
        aux.append(float(best_profit.inversion))
        best_profit_vector.append(aux)
        aux = []
        aux.append(float(best_profit.valorneto))
        optimal_npv_vector.append(float(best_profit.valorneto))
        condicion_in=[]
        for procesoSeparacionid in procesoSeparacionId:
            condicion_in.append(procesoSeparacionid['idprocesosseparacionid'])
        lista=ProcesoSeparacion.objects.values('idprocesosseparacion').filter(idprocesosseparacionid__in = condicion_in,secuenciaprocesoseparacion=best_profit.secuenciaprocesoseparacion).order_by('idprocesosseparacionid')
        condicion_in=[]
        for n in lista:
            condicion_in.append(n['idprocesosseparacion'])
        optimal_padre=[]
        for cond in condicion_in:
            optimal_hija = []
            procesoCombinacion=list(ProcesoCombinacion.objects.filter(idprocesosseparacion = cond).order_by('secuencia'))
            for proceCom in procesoCombinacion:
                optimal_aux=[]
                procesoAux=proceCom.idprocesoprevio
                optimal_aux.append(procesoAux.idproceso if procesoAux!=None else '')
                procesoAux = proceCom.idprocesosalida
                optimal_aux.append(procesoAux.idproceso if procesoAux!=None else '')
                optimal_aux.append(proceCom.salida if proceCom.salida!=None else '')
                optimal_aux.append(proceCom.idmaterial if proceCom.idmaterial!=None else '')
                for i in range(0,6):
                    optimal_aux.append('')
                masasAux=[]
                listaMasaSalida=Masasalida.objects.values('valormasa').filter(idprocesocombinacion=proceCom.idprocesocombinacion).order_by("idmaterial")
                for masas in listaMasaSalida:
                    masasAux.append(float(masas['valormasa']))
                optimal_aux.append(masasAux)
                optimal_hija.append(optimal_aux)
            optimal_padre.append(optimal_hija)
        optimal_intermediate_outputs.append(optimal_padre)
    return best_profit_vector,optimal_npv_vector,optimal_intermediate_outputs

def getNombreProcesosCalculados(idprocesocalculado):
    from processes.models import Proceso,ProcesoCalculado

    procesosDict=ProcesoCalculado.objects.values('idprocesos').filter(idprocesocalculado=idprocesocalculado)

    vectorProcesos = []
    for dic in procesosDict:
        vectorProcesos.append(dic['idprocesos'])
    listaProcesos=Proceso.objects.values('proceso').filter(idproceso__in=vectorProcesos).order_by('idproceso')
    nombresProcesos=''
    for proceso in listaProcesos:
        nombresProcesos=nombresProcesos+proceso['proceso']+' || '#.append(proceso['proceso'])
    return nombresProcesos

def getNameEquipo(idequipo):
    from processes.models import Equipo
    nombre=Equipo.objects.filter(idequipo=int(idequipo[0]))
    for nom in nombre:
        return nom.nombre
    return ''

def getNombresMaterialesEquipoNombre(nombreEquipo):
    from processes.models import Equipo
    listaMat=Equipo.objects.values('materiales').filter(nombre=nombreEquipo)
    listaNombreMateriales=[]
    for mat in listaMat:
        listaNombreMateriales.append(getNombreMaterial(mat['materiales']))
    print(listaMat)
    return listaNombreMateriales

def getNombreMaterial(idmaterial):
    from processes.models import Material
    nombre=list(Material.objects.values("nombre").filter(idmaterial=idmaterial))
    return nombre[0]['nombre']

def getTodosProcesos():
    from processes.models import Proceso
    procesoslis=list(Proceso.objects.values('proceso').all())
    listaNombreProceso=[]
    for pro in procesoslis:
        listaNombreProceso.append(pro['proceso'])

    return listaNombreProceso
