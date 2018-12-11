
from processes.models import ProcesoSeparacionId, ProcesoSeparacion, ProcesoCombinacion, Masasalida, Material, Proceso


def saveAnalysis(procesoCalculado,start_year, end_year, best_combi_vector, best_profit_vector, optimal_intermediate_outputs, optimal_npv_vector, profit_global, processes_vector):
    print('Start thread Save Analysis')
    anioInicial = start_year['anio']
    anioFinal = end_year['anio']
    for m in range(0, anioFinal - anioInicial + 1):
        print(anioInicial+m)
        dateYear = anioInicial+m
        psid = ProcesoSeparacionId(anio=dateYear, idprocesocalculado=procesoCalculado)
        psid.save()

        secuencia=1
        for indice,mejorBeneficio in enumerate(best_profit_vector):

            salida=optimal_intermediate_outputs[indice]
            restaAnios = anioFinal - anioInicial
            listaSalida=[]
            if (restaAnios > 0):
                listaSalida.append(salida[m])  # tomo la salida del anio correspondiente
            else:
                listaSalida=salida
            for salidaProceso in listaSalida:

                secuenciaTupla = 1
                ps = ProcesoSeparacion(idprocesosseparacionid=psid, secuenciaprocesoseparacion=secuencia,
                                       inversion=mejorBeneficio[0], valorneto=optimal_npv_vector[indice])
                ps.save()

                secuencia = secuencia + 1
                for tuplaSalida in salidaProceso:
                    idprocesosalida=Proceso.objects.get(pk=tuplaSalida[1]) if tuplaSalida[1] !=  '' else None     #Proceso.objects.get(pk=tuplaSalida[1] if tuplaSalida[1] !=  '' else -1)#tuplaSalida[1] if tuplaSalida[1] !=  '' else None
                    idprocesoprevio=Proceso.objects.get(pk=tuplaSalida[0]) if tuplaSalida[0] !=  '' else None#tuplaSalida[0] if tuplaSalida[0] !=  '' else None
                    idmaterial=tuplaSalida[3] if tuplaSalida[3] !=  '' else None
                    salidaCombinacion= tuplaSalida[2] if tuplaSalida[2] !=  '' else None

                    pc = ProcesoCombinacion(idprocesosseparacion=ps,secuencia=secuenciaTupla,idprocesosalida=idprocesosalida,
                                                idprocesoprevio=idprocesoprevio,idmaterial=idmaterial if idmaterial!='/' else None,salida=salidaCombinacion)
                    secuenciaTupla=secuenciaTupla+1
                    pc.save()


                    for i,masasSalida in enumerate(tuplaSalida[10]):
                        material=Material.objects.get(pk=i)
                        ms=Masasalida(idprocesocombinacion=pc,idmaterial=material,valormasa=masasSalida)
                        ms.save()

    print('Save ProcesoSeparacionId')
    print('Save ProcesoSeparacion')
    print('Save ProcesoCombinacion')
    print('Save Masasalida')
