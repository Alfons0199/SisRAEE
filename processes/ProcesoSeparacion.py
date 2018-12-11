import numpy, itertools, time
from processes.models import *

global parametrosEconomicos, numeroMateriales  # economical_parameters,
parametrosEconomicos = Parametroseconomicos.objects.all().values()[0]


# economical_parameters=list(map(float, parametrosEconomicos.values()))


def getParametrosProcesos(listaProcesos, idequipo, listMaterialesEqui):
    global matrizProcesses, matrizProcessParametros, listaProcesosMateriales \
        , codequipo, codProcesos, yield_table, densities

    codequipo = idequipo
    codProcesos = listaProcesos
    yield_table = getRendimientoProceso(listMaterialesEqui);
    matrizProcesses = []  # matriz grupos_procesos x materiales
    matrizProcessParametros = []
    listaProcesosMateriales = []
    densities = getDensidades()

    listProcess = list(map(int, listaProcesos))  # lista de procesos de string a int
    listProcess = list(
        Proceso.objects.filter(pk__in=listProcess))  # tomo el modelo proceso en uns lista de la lista de procesos
    listaGrupos = list(Proceso.objects.values(
        'idgrupo').all().distinct())  # consulta para tomar todos los grupos de todos los procesos
    num_groups = listaGrupos.__len__()  # toma el numero de grupos de procesos exitentes ejemplo 3
    #listMaterialesEqui = getListaMagterialesEquipo(idequipo)  # numero de materiales a del equipo
    # list(
    # Equipo.objects.values('materiales').filter(pk__in=idequipo))  # numero de materiales a del equipo
    num_plastics = len(listMaterialesEqui)
    matrizProcesses = [[] for x in range(num_groups)]  # se agrega una fila para cada grupo de proceso y una mas para los id de los materiales
    # se agregan las columnas para cada material para completar la matriz
    for i in range(0, num_groups): #mas una filamas para guardar los id de los materiales
        matrizProcesses[i] = [[] for x in range(num_plastics)]

    listaMaterialesMatrizProcesses=[]
    for p in listMaterialesEqui:
        listaMaterialesMatrizProcesses.append(p['materiales'])

    for proceso in listProcess:
        idx_group = (proceso.idgrupo)  # toma el id del grupo de cada proceso
        materialesProcesos = list(Proceso.objects.values('materiales').filter(
            idproceso__exact=int(proceso.idproceso)))  # tomo los materiales del proceso
        listaProcesosMateriales = []
        # La matrizProcess grupo proceso x materiales, se agrega el id del proceso con respecto al grupo que pertenece y el material que separa
        for number in materialesProcesos:
            matrizProcesses[idx_group.idgrupo][int(number['materiales'])].append(proceso.idproceso)
            listaProcesosMateriales.append(int(number['materiales']))
            # listaProcesosMateriales[-1].append((number['materiales'])
        matrizProcessParametros.append([])
        tipoProceso = proceso.idtipo.idtipo
        matrizProcessParametros[-1].append(tipoProceso)

        matrizProcessParametros[-1].append(getListaMaterialesProceso(tipoProceso, listaProcesosMateriales, proceso))
        matrizProcessParametros[-1].append(float(proceso.costotratamiento))

        if tipoProceso == 0:
            matrizProcessParametros[-1].append(proceso.loop)
        elif tipoProceso == 2:
            matrizProcessParametros[-1].append(proceso.iddensidad.iddensidad)  # el id de la tabla densidad
        matrizProcessParametros[-1].append(proceso.idproceso)
        matrizProcessParametros[-1].append(
            [float(proceso.costoinversion), float(proceso.rendimientominimo), float(proceso.incrementorendimiento),
             float(proceso.tiempodepreciacion)])

    # range all the matrizProcesses and add their parameters in a list.
    # process_param is a list where one element is a process with its parameters

    return matrizProcesses, matrizProcessParametros,listaMaterialesMatrizProcesses


def getListaMaterialesProceso(tipoProceso, listaMateriales, proceso):
    lista = []
    if tipoProceso == 0:
        lista.append(listaMateriales.pop(0))
    elif tipoProceso == 3:
        return getEficienciaSalidaMultiple(proceso.idproceso)
    else:
        return listaMateriales
    return lista


def getEficienciaSalidaMultiple(idProceso):
    matrizRendimiento = []
    listaRendimiento = list(
        RendimientoProceso.objects.filter(idproceso=idProceso).order_by('idmaterial', 'idmaterialreferencia'))
    materialAux = -1
    lista = []
    cont = 0
    for rend in listaRendimiento:
        material = rend.idmaterial_id
        if material != materialAux:
            materialAux = material
            if cont > 0:
                matrizRendimiento.append(lista)
                lista = []
            else:
                cont = 1
        lista.append(float(rend.valor))
    matrizRendimiento.append(lista)
    return matrizRendimiento


#def getListaMagterialesEquipo(idequipo):
    #return list(
        #Equipo.objects.values('materiales').filter(pk__in=idequipo))*/


def getDensidades():  # order_by
    listaDensidades = list(Densidad.objects.values('iddensidad', 'densidad').order_by('iddensidad'))
    matrizDensidad = []
    for densi in (listaDensidades):
        listaAux = []
        listaAux.append(float(densi['densidad']))
        densidades = list(DensidadMaterial.objects.values('valor').filter(iddensidad=densi['iddensidad']))
        for valor in densidades:
            listaAux.append(float(valor['valor']))
        matrizDensidad.append(listaAux)
    return matrizDensidad


##############################################################################################################################
##############################################################################################################################
##############################################################################################################################

# Main function

def getfunc_separation(idequipo, processes, process_param, resale_price, input_densities, start_year,
                       end_year,listMaterialesEqui,listaProcesos):
    print('Optimization Model running...', '\n')
    #listMaterialesEqui = getListaMagterialesEquipo(idequipo)  # lista de materiales a del equipo
    global numeroMateriales,impuerezas,efectoCoctel
    numeroMateriales = listMaterialesEqui
    impuerezas = getImpuerezasMatriz(1)
    efectoCoctel  = getCoctelMatriz(2)
    combinacionMateriels = []  # combination_plastics = []
    combinacionProcesos = []  # combination_processes = []
    grade_vector = []
    recovery_vector = []
    profit_vector = []
    final_output_vector = []
    investment_vector = []
    ror_vector = []
    npv_global = []

    positive_profit = 0
    count = 0

    optimal_npv = float('-inf')
    optimal_intermediate_ouputs = []

    processes_vector = []

    best_profit = []
    optimal_npv_vector = []
    optimal_intermediate_ouputs = []
    best_combi = []
    best_sum_profit = []

    keep_value = 10

    for i in range(0, keep_value):
        best_profit.append(0)
        best_combi.append([])
        optimal_npv_vector.append(float('-inf'))
        optimal_intermediate_ouputs.append([])
        best_sum_profit.append(float('-inf'))
    processes_vector = []
    # Computation of the vector with all the processes combinations

    tic = time.time()
    combination_processes, combination_plastics = main_combinations(processes, listMaterialesEqui)

    toc = time.time()
    #
    anioInicial = start_year['anio']
    anioFinal = end_year['anio']
    print('The time needed to find all the combinations is', toc - tic, 'seconds', '\n')
    print('*****************************************************BASE*********************************')
    listaEquipoEntrada = list(
        EquipoEntrada.objects.values('idequipoentrada','anio').filter(idequipo__exact=int(idequipo[0]),
                                                                   anio__range=[anioInicial,anioFinal]))
    listaMasasAnios = []
    for le in listaEquipoEntrada:
        print('*****************************************************BASE*********************************')
        masasEntrada = list(
            MasaEntrada.objects.values('masa').filter(idequipoentrada = le['idequipoentrada']).order_by('idmaterial'))
        dicc={str(le['anio']):(masasEntrada)}
        listaMasasAnios.append(dicc)
    #
    #  Range all the plastics combinations
    for i in range(0, len(combination_plastics)):
        print(i)
        if i==10:
            print (i)
        # Range all the processes combinations related to one plastic combination
        for j in range(0, len(combination_processes[i])):
            #print("--->",j)
            cash_flows = [0]
            current_npv = float('-inf')
            current_intermediate_outputs = []
            plastic_combi = [z for z in combination_plastics[i] if z >= 0]  # specific plastic combination
            processes_combination = [z for z in combination_processes[i][j] if z >= 0]  # specific process combination
            # Range the different years computed for the ROR calculation
            anioInicial = start_year['anio']
            anioFinal = end_year['anio']
            for m in range(0, anioFinal - anioInicial + 1):
                anioreferencia=anioInicial + m
                masasEntrda=listaMasasAnios[m]
                masasEntrda=masasEntrda[str(anioreferencia)]
                system_input = []
                for ma in masasEntrda:
                    system_input.append(float(ma['masa']))
                global current_year
                current_year = m + 1

                revenue = []
                cost = []
                queue = []
                cost_cancel_vector = []
                incineration_output = []
                intermediate_ouputs = []

                final_output = []  # vector containing the different outputs of a sequence
                idx_cancel_combination = 0
                idx_density_combination = 0
                total_grade = 0
                total_recovery = 0
                total_mass = 0
                total_revenue = 0
                total_cost = 0
                investment_cost = 0
                post_treatment_cost = 0
                total_disassembly = 0

                mass_input = system_input[:]
                intermediate_ouputs = [['', '', '', '', '', '', '', '', '', '',
                                        system_input]]  # allocation of the vector containing the intermediate outputs

                # process of a specific sequence
                revenue, cost = func_separation_current(0, [mass_input, ''], input_densities, plastic_combi,
                                                        processes_combination, process_param, processes, revenue,
                                                        resale_price, cost, system_input, queue, final_output,
                                                        intermediate_ouputs,listaProcesos)

                initial_mass = system_input
                final_grade = [0] * len(initial_mass)
                final_recovery = [0] * len(initial_mass)
                output = [0] * len(initial_mass)
                incineration_output = [[]]

                # Allocation of an empty vector containing the output
                for k in range(0, len(output)):
                    output[k] = [0] * len(initial_mass)

                # Putting all the output targeting the same plastic together
                # Range all the outputs
                for k in range(0, len(final_output)):

                    if final_output[k][1] == -1:  # Output k has to be incinerated
                        incineration_output[-1] = [0] * len(
                            initial_mass)  # allocation of the vector to add the mass of each plastic

                        for m in range(0, len(
                                final_output[k][0])):  # add the mass of each plastic in the incineration output
                            incineration_output[-1][m] = final_output[k][0][m]

                    else:  # Plastic is resold as plastic k
                        final_idx = final_output[k][1]
                        for m in range(0, len(final_output[k][0])):
                            output[final_idx][m] = output[final_idx][m] + final_output[k][0][m]

                # Adding all the revenues together
                for k in range(len(revenue)):
                    total_revenue = total_revenue + revenue[k][0]
                    total_disassembly = total_disassembly + revenue[k][1]

                # Check if the same technique is processed two times in row for two different target plastics.
                # In this case, the costs of the second process is cancelled

                cancel_cost = []

                # deletes the "non-processes" equivalent (process with negative index)
                for k in range(len(processes_combination)):
                    if processes_combination[k] >= 0:
                        idlispro=listaProcesos.index(str(processes_combination[k]))
                        cancel_cost.append(process_param[idlispro][-2])
                    else:
                        pass
                        # Addition of the investment costs of each process

                for k in range(0, len(cost)):
                    total_cost = total_cost + cost[k][0]
                    total_disassembly = total_disassembly + cost[k][2]
                post_treatment_cost = 0
                for k in range(1, len(intermediate_ouputs)):
                    post_treatment_cost = post_treatment_cost + intermediate_ouputs[k][-3]

                # Profit for a specific year
                profit = (total_revenue - total_cost - total_disassembly - post_treatment_cost)
                grade_vector.append(total_grade)
                recovery_vector.append(total_recovery)
                profit_vector.append(profit)

                cash_flows.append(profit)  # Addition of the profit to the cash flows vector
                current_intermediate_outputs.append(intermediate_ouputs)
            sum_profit = 0

            for l in range(1, len(cash_flows)):
                sum_profit = sum_profit + cash_flows[l]

            processes_vector.append(processes_combination)
            marr = float(parametrosEconomicos['marr'])  # economical_parameters[9][0]

            total_invest_cost = 0
            salvage_value = 0
            for l in range(0, len(processes_combination)):
                process = listaProcesos.index(str(processes_combination[l]))
                investment_cost = process_param[process][-1][0]
                depreciation_years = process_param[process][-1][3]
                k = anioFinal - anioInicial + 1  # end_year - start_year + 1
                total_invest_cost = total_invest_cost - investment_cost
                while k > depreciation_years:
                    total_invest_cost = total_invest_cost - investment_cost
                    k = k - depreciation_years
                salvage_value = salvage_value + (depreciation_years - k) * investment_cost / depreciation_years

            cash_flows[0] = total_invest_cost
            cash_flows[-1] = cash_flows[-1] + salvage_value
            marr = float(marr)
            current_npv = numpy.npv(marr, cash_flows)
            npv_global.append(current_npv)
            cash_flows[-1] = cash_flows[-1] - salvage_value
            cash_flows.append(salvage_value)

            # print current_npv, cash_flows, intermediate_ouputs
            if current_npv > optimal_npv_vector[keep_value - 1] and optimal_npv_vector.count(current_npv) == 0:
                for k in range(0, keep_value - 1):
                    if current_npv < optimal_npv_vector[keep_value - k - 2]:
                        #if cash_flows[0]!=0:################################################CAMBIO DEL ESPACIO EN BLANCO
                        best_profit.insert(keep_value - k - 1, (cash_flows))
                        best_sum_profit.insert(keep_value - k - 1, int(sum_profit))
                        best_combi.insert(keep_value - k - 1, processes_combination)
                        optimal_intermediate_ouputs.insert(keep_value - k - 1, current_intermediate_outputs)
                        optimal_npv_vector.insert(keep_value - k - 1, current_npv)

                        best_profit.pop()
                        best_combi.pop()
                        optimal_npv_vector.pop()
                        optimal_intermediate_ouputs.pop()
                        best_sum_profit.pop()
                        break

                    else:
                        if k == keep_value - 2:
                            #if cash_flows[0] != 0:################################################CAMBIO DEL ESPACIO EN BLANCO
                            best_profit.insert(0, (cash_flows))
                            best_combi.insert(0, processes_combination)
                            best_sum_profit.insert(0, int(sum_profit))
                            optimal_intermediate_ouputs.insert(0, current_intermediate_outputs)
                            optimal_npv_vector.insert(0, current_npv)

                            best_profit.pop
                            best_combi.pop
                            optimal_npv_vector.pop
                            optimal_intermediate_ouputs.pop
                            best_sum_profit.pop

                            break

                        else:
                            pass


            else:
                pass

    return best_combi, best_profit, optimal_intermediate_ouputs, optimal_npv_vector, npv_global, processes_vector


def main_combinations(processes, listaMtls):
    process_vector = []
    plastic_vector = []

    # range the different group of processes
    # current_plastic is a vector containing the different combinations of plastics to target
    # current_process is a vector containing the different combinations of processes of the same group to separate the plastics

    index_list_bis = []
    combination_plastics_bis = []

    listaCombinacionMateriales = getCombinacionMateriles(listaMtls)

    for i in range(len(processes)):
        current_plastic, current_process = func_processes(listaCombinacionMateriales, processes[i])

        # This is addition of process is equivalent to a non-process.
        # This is needed to simulate a process combination that contains no process from one of the different groups (For example, it contains a process from the first and the third group but none from the second)
        current_plastic.append([-i - 1])
        current_process.append([[-i - 1]])
        print('Plasticos: ', current_plastic)
        print('Procesos: ', current_process)
        process_vector.append(current_process)
        plastic_vector.append(current_plastic)

    # Plastic vector contains three elements, one by group. Each element contains all the plastics combinations within the same group
    # Process vector contains three elements, one by group. Each element contains all the processes combinations within the same group

    current_plastic_list = []
    current_plastic_list_idx = []
    current_process_list = []
    final_process_combinations = []
    final_plastic_combinations = []
    global count_processes
    count_processes = 0

    # Function to combine the processes combinations from the different groups of processes
    combination_processes, combination_plastics = func_combination_processes(0, plastic_vector, process_vector,
                                                                             current_plastic_list, current_process_list,
                                                                             current_plastic_list_idx,
                                                                             final_plastic_combinations,
                                                                             final_process_combinations)
    print('******************************************************************')
    print('Plasticos: ', combination_plastics)
    print('Procesos: ', combination_processes)
    print('N-x = ', count_processes + len(combination_plastics), '(Number of sequences after having combined them)')
    #
    # # combination processes contains all the feasible combinations of the separation techniques to process
    # # combination_plastics contains all the feasible combinations of plastics to target
    # # Function to delete all the combinations that do not satisfy a rule specific to one process
    print('N-x-y =', len(combination_plastics), '(Number of combinations after having removed all the duplicates)')

    #final_combination_plastics=[]
    #final_combination_processes=[]
    for i in range(0, len(matrizProcessParametros)):
         if matrizProcessParametros[i][0] == 3:
             final_combination_plastics, final_combination_processes = func_individual_rule(i, combination_plastics,
                                                                                            combination_processes)
         else:
             pass
    #final_combination_plastics, final_combination_processes = func_individual_rule(3, combination_plastics,
    #                                                                               combination_processes)
    #print('N-x-y-z =', len(
        #final_combination_plastics),
          #'(Number of combinations after having removed the combinations that do not satisfy the rule specific to a process)')
    return final_combination_processes, final_combination_plastics


# funcion que devuele todas las combinaciones de los materiales
def getCombinacionMateriles(listMtls):
    combinacionMateriles = []
    listMateriales = []
    for material in listMtls:
        listMateriales.append(int(material['materiales']))

    for i in range(1, len(listMateriales)):
        # itertools.permutations computes all the possible permutations of size "i" with the elements from the list "index_list"
        els = [list(x) for x in itertools.permutations(listMateriales, i)]
        # els contains all the permutations from the same number of elements. These permutations represent the plastic permutations
        combinacionMateriles.extend(els)

    return combinacionMateriles


def func_processes(listaCombinacionMateriales, processes):
    combination_processes = []

    combination_plastics = listaCombinacionMateriales

    final_combination_plastics = []
    idx_delete_combi = 0

    # range all the plastics permutations and add an element to combination processes. This element will contain the combination processes associated to this plastic combination
    global_process_combi = []

    for i in range(0, len(combination_plastics)):
        currentlist = []
        combination_processes.append([])

        currentlist = [None] * len(combination_plastics[i])  # empty list with the size of the plastic combination

        # Computation of the processes combinations (from the same group) for a specific plastic combination
        combination_processes, idx_delete_combi = func_separation_combination(0, combination_plastics[i], processes,
                                                                              currentlist, combination_processes,
                                                                              idx_delete_combi, global_process_combi)

        # if no processes combinations is possible for this plastic combination : remove the element
        if idx_delete_combi == 1:
            combination_processes.pop()

        # if a process combination is possible : keep the plastic combination and add it to the final list
        else:
            if len(combination_processes[-1]) != 0:
                final_combination_plastics.append([])

                for j in range(len(combination_plastics[i])):
                    final_combination_plastics[-1].append(
                        combination_plastics[i][j])  # copy the plastic combination in the final list
            else:
                combination_processes.pop()
        idx_delete_combi = 0

    # return the plastics and process combinations from the same group
    return final_combination_plastics, combination_processes


def func_separation_combination(idx_recursion, combination, processes, currentlist, combination_processes,
                                idx_delete_combi, global_process_combi):
    # if the plastic is the last one of the combination : adding the processes combinations in the final list
    if idx_recursion == len(combination) - 1:

        idx = combination[idx_recursion]  # idx of the targeted plastic

        # if there are no process to target this plastic, plastic combination has to be removed
        if len(processes[idx]) == 0:
            idx_delete_combi = 1

        # otherwise add it to the final list
        else:
            for i in range(0, len(processes[idx])):  # range the different processes that can target this plastic

                currentlist[idx_recursion] = processes[idx][i]  # add the process to the process combination

                # if the same process is used twice, process combination is not taken into account
                if any(currentlist.count(x) > 1 for x in currentlist):
                    pass

                # otherwise add it to the final list of process. Final list is then copied in combination_processes

                elif global_process_combi.count(currentlist) == 1:
                    pass
                else:
                    combination_processes[-1].append([])
                    global_process_combi.append([])
                    for j in range(0, len(currentlist)):
                        combination_processes[-1][-1].append(currentlist[j])
                        global_process_combi[-1].append(currentlist[j])

        # if idx_delete_combi = 1, it means that there are no processes to target a plastic of the combination. Therefore plastic combination has to be deleted
        return combination_processes, idx_delete_combi

    # recursion to range the different plastics of the combination
    else:
        idx = combination[
            idx_recursion]  # combination is the plastic combination and idx refers to the plastic targeted
        idx_recursion = idx_recursion + 1

        # if there are no processes in the group of processes to separate the targeted plastic, plastic combination has to be removed
        if len(processes[idx]) == 0:
            idx_delete_combi = 1  # idx to indicate that the combination can't be processes and has to be deleted



        # otherwise range the different processes to target this plastic
        else:
            for i in range(0, len(processes[idx])):
                if idx_delete_combi == 0:

                    currentlist[idx_recursion - 1] = processes[idx][
                        i]  # Add the process in the processes combination. The others processes (from the same group) that can target this plastic will be added afterwards with the recursive loop.

                    # Recursive loop to check the processes for the next plastic of the combination
                    combinations_processes, idx_delete_combi = func_separation_combination(idx_recursion, combination,
                                                                                           processes, currentlist,
                                                                                           combination_processes,
                                                                                           idx_delete_combi,
                                                                                           global_process_combi)
                else:
                    break
        return combination_processes, idx_delete_combi


# Recursive function to combine the processes combinations of the different groups
def func_combination_processes(idx_recursion, plastic_combinations, process_combinations, current_plastic_list,
                               current_process_list, current_plastic_list_idx, final_plastic_combinations,
                               final_process_combinations):
    global count_processes

    # if idx_recursion is equal to the idx of that last group of processes (3 in this case)
    aux = len(process_combinations)
    if idx_recursion == len(process_combinations) - 1:

        # range all the plastics combinations of the group
        for j in range(len(plastic_combinations[idx_recursion])):

            # range all the plastics from the plastic combination and add them in a list
            for m in range(len(plastic_combinations[idx_recursion][j])):
                current_plastic_list.append(plastic_combinations[idx_recursion][j][m])

            # list to remember how many plastics of the same group have been added
            current_plastic_list_idx.append(len(plastic_combinations[idx_recursion][j]))

            # if-else condition to remove the plastics combinations that target more than once the same plastic
            if any(current_plastic_list.count(x) > 1 for x in current_plastic_list):
                pass  # if count is larger than one, it means that a plastic is targeted twice at least

            else:

                if final_plastic_combinations.count(current_plastic_list) == 0:
                    final_plastic_combinations.append([])

                    # add the plastic combinations to the final vector of combinations
                    for t in range(0, len(current_plastic_list)):
                        final_plastic_combinations[-1].append(current_plastic_list[t])

                    final_process_combinations.append([])

                    # range all the processes combinations associated to one plastic combination
                    for k in range(len(process_combinations[idx_recursion][j])):

                        final_process_combinations[-1].append(
                            [])  # add an element in the final list of processes in order to add each process combination

                        # add the process combinations associated to one plastic combination in the list of processes combinations
                        for i in range(len(process_combinations[idx_recursion][j][k])):
                            current_process_list.append(process_combinations[idx_recursion][j][k][i])

                        # add the process combination in the final list of processes combinations
                        for t in range(0, len(current_process_list)):
                            final_process_combinations[-1][-1].append(current_process_list[t])

                        # removes the number of processes belong the last group
                        for i in range(len(process_combinations[idx_recursion][j][k])):
                            current_process_list.pop()
                else:
                    count_processes = count_processes + 1
                    for k in range(len(process_combinations[idx_recursion][j])):

                        final_process_combinations[final_plastic_combinations.index(current_plastic_list)].append(
                            [])  # add an element in the final list of processes in order to add each process combination

                        # add the process combinations associated to one plastic combination in the list of processes combinations
                        for i in range(len(process_combinations[idx_recursion][j][k])):
                            current_process_list.append(process_combinations[idx_recursion][j][k][i])

                        # add the process combination in the final list of processes combinations
                        for t in range(0, len(current_process_list)):
                            final_process_combinations[final_plastic_combinations.index(current_plastic_list)][
                                -1].append(current_process_list[t])

                        # removes the number of processes belong the last group
                        for i in range(len(process_combinations[idx_recursion][j][k])):
                            current_process_list.pop()

            # removes the number of plastics that are separated through processes from the last group
            for p in range(0, current_plastic_list_idx[-1]):
                current_plastic_list.pop()
            current_plastic_list_idx.pop()

        # return the final list containing plastics combinations and processes combinations
        return final_process_combinations, final_plastic_combinations


    # if the idx is not the one corresponding to the combinations of the last group of processes
    else:

        # range all the plastics combinations of the group "idx_recursion"
        for j in range(len(plastic_combinations[idx_recursion])):
            # range the plastics of a plastic combination and add them in a list
            for m in range(len(plastic_combinations[idx_recursion][j])):
                current_plastic_list.append(plastic_combinations[idx_recursion][j][m])

            # list to remember how many plastics of the same group have been added
            current_plastic_list_idx.append(len((plastic_combinations[idx_recursion][j])))

            # range all the processes combinations associated to one plastic combination
            for k in range(len(process_combinations[idx_recursion][j])):

                # range the processes of a process combination and them in a list
                for i in range(len(process_combinations[idx_recursion][j][k])):
                    current_process_list.append(process_combinations[idx_recursion][j][k][i])

                idx_recursion = idx_recursion + 1

                # Call the function to add the processes combinations of the next group of processes
                # The processes will be added recursively.
                final_process_combinations, final_plastic_combinations = func_combination_processes(idx_recursion,
                                                                                                    plastic_combinations,
                                                                                                    process_combinations,
                                                                                                    current_plastic_list,
                                                                                                    current_process_list,
                                                                                                    current_plastic_list_idx,
                                                                                                    final_plastic_combinations,
                                                                                                    final_process_combinations)

                idx_recursion = idx_recursion - 1

                # Once they have been added, it deletes the processes from the processes list
                for i in range(len(process_combinations[idx_recursion][j][k])):
                    current_process_list.pop()

            # Once they have been added, it deletes the plastics from the plastics list
            for p in range(0, current_plastic_list_idx[-1]):
                current_plastic_list.pop()
            current_plastic_list_idx.pop()

        return final_process_combinations, final_plastic_combinations


def func_individual_rule(value, combination_plastics, combination_processes):
    final_combination_plastics = []
    final_combination_processes = [[]]
    # range all the plastics combinations
    for i in range(0, len(combination_plastics)):

        if len(final_combination_processes[-1]) == 0:
            pass
        else:
            final_combination_processes.append([])
        if i == 66:
            print(i)
        # range all the processes combinations
        for j in range(0, len(combination_processes[i])):
            # Verificar si el proceso tomado 3 LIBS esta en el grupo de procesos.
            # check if the process is in the combination of processes
            if value in combination_processes[i][
                j]:  # verifica si el tipo de proceso 3 LIBS esta en la combinacion de procesos
                aux = combination_processes[i][j]
                index_value = combination_processes[i][j].index(value)  # check the position of this process
                delete_value = 0

                for k in range(index_value + 1, len(combination_processes[i][j])):
                    if combination_processes[i][j][
                        k] >= 0:  # check if an other process if processed afterwards#se verifica si hay mas procesos a parte del tomado 3 LIBS
                        delete_value = 1  # if yes, idx_delete_combi means that the combination has to be deleted#si hay mas procesos este se elimina
                        break
                    else:
                        pass

                if delete_value == 0:  # delete_value = 0 means that the combination satisfies the rule and is added to the final list of combinations
                    final_combination_processes[-1].append(combination_processes[i][j])
                else:
                    pass

            else:  # if the process is not in the combination, combination is added to the final list of combinations
                final_combination_processes[-1].append(combination_processes[i][j])
        # si los procesos de un grupo de plasticos no se ajustan a la regla, el grupo de plasticos tampoco se agrega a la lista final
        print(len(final_combination_processes[-1]), (final_combination_processes[-1]))
        if len(final_combination_processes[-1]) == 0:
            pass  # if all the processes combination associated to one plastic combination have been deleted, plastic combination is not added to the final list of plastic combinations
        else:
            final_combination_plastics.append(combination_plastics[i])

    return final_combination_plastics, final_combination_processes


# Recursive function to process a step single step of a sequence
def func_separation_current(idx, input, input_densities, plastic_combi, process_combi, process_param, processes,
                            revenue, resale_price, cost, initial_mass, queue, final_output, intermediate_ouputs,listaProcesos):
    # idx refers to the idx of the next process from the combination process
    # input refers to the mass composition whereas input_densities refer to the first and last density of the samples in the input
    # plastic_combi is the plastic combination treated
    # process_combi is the processes combination treated

    #global indiceProcessParam
    # There are no more processes in the sequence and in the queue neither
    indiceProcessParam=0
    if idx<len(process_combi):
        indiceProcessParam = listaProcesos.index(str(process_combi[idx]))

    if idx == len(process_combi) and len(queue) == 0:
        total_mass = 0
        for j in range(0, len(input[0])):
            total_mass = total_mass + input[0][j]
        # check the optimal end-of-life for the remaining output and add it to the final output_vector
        if len(input[0]) != 0 and total_mass != 0:  # check if the output isn't empty

            biggest_mass = -1
            idx_biggest_mass = -1
            for i in range(0, len(input[0])):
                if input[0][i] > biggest_mass:
                    idx_biggest_mass = i
                    biggest_mass = input[0][i]
                else:
                    pass

            revenue, final_output, disassembly = func_revenues(input, idx_biggest_mass, initial_mass, revenue, cost,
                                                               resale_price, final_output, input_densities)
            for i in range(1, len(intermediate_ouputs)):

                if final_output[-1][0] == intermediate_ouputs[i][-1]:
                    intermediate_ouputs[i][4] = int(final_output[-1][-1])
                    intermediate_ouputs[i][3] = int(final_output[-1][1])
                    intermediate_ouputs[i][-2] = revenue[-1][-1]

                else:
                    pass

        else:
            pass

        return revenue, cost

    # End of a sequence but there are other processes in the queue
    elif idx == len(process_combi):
        total_mass = 0
        for j in range(0, len(input[0])):
            total_mass = total_mass + input[0][j]
        if len(input[0]) != 0 and total_mass != 0:  # check if the output isn't empty
            biggest_mass = -1
            idx_biggest_mass = -1
            for i in range(0, len(input[0])):
                if input[0][i] > biggest_mass:
                    idx_biggest_mass = i
                    biggest_mass = input[0][i]
                else:
                    pass

                # check the optimal end-of-life for the remaining output and add it to the final output_vector
            revenue, final_output, disassembly = func_revenues(input, idx_biggest_mass, initial_mass, revenue, cost,
                                                               resale_price, final_output, input_densities)
            for i in range(1, len(intermediate_ouputs)):
                if final_output[-1][0] == intermediate_ouputs[i][-1]:
                    intermediate_ouputs[i][4] = int(final_output[-1][-1])
                    intermediate_ouputs[i][3] = int(final_output[-1][1])
                    intermediate_ouputs[i][-2] = revenue[-1][-1]
                else:
                    pass


        else:
            pass

        # Pop the last element of the queue to process it
        last_element = queue.pop()
        input = last_element[0]
        plastic_combi = last_element[1]
        process_combi = last_element[2]
        input_densities = last_element[3]

        # process the last element of the queue
        revenue, cost = func_separation_current(0, input, input_densities, plastic_combi, process_combi, process_param,
                                                processes, revenue, resale_price, cost, initial_mass, queue,
                                                final_output, intermediate_ouputs,listaProcesos)
        return revenue, cost

    # equivalence of a non-process. Idx is just incremented to process the next one
    elif process_combi[idx] < 0:
        revenue, cost = func_separation_current(idx + 1, input, input_densities, plastic_combi, process_combi,
                                                process_param, processes, revenue, resale_price, cost, initial_mass,
                                                queue, final_output,
                                                intermediate_ouputs,listaProcesos)  # Processing the next step of the sequence
        return revenue, cost


    # Group separation
    elif process_param[indiceProcessParam][0] == 1:

        revenue, cost = func_group_separation(idx, input, input_densities, plastic_combi, process_combi, process_param,
                                              processes, initial_mass, revenue, cost, queue, final_output, resale_price,
                                              intermediate_ouputs,listaProcesos)

        return revenue, cost

    # Density separation
    elif process_param[indiceProcessParam][0] == 2:
        revenue, cost = func_density_separation(idx, input, input_densities, plastic_combi, process_combi,
                                                process_param, processes, initial_mass, revenue, cost, queue,
                                                final_output, resale_price, intermediate_ouputs,listaProcesos)

        return revenue, cost


    # Multiple output separation
    elif process_param[indiceProcessParam][0] == 3:
        revenue, cost = func_multiple_output_separation(idx, input, input_densities, plastic_combi, process_combi,
                                                        process_param, processes, revenue, resale_price, cost,
                                                        initial_mass, queue, final_output, intermediate_ouputs,listaProcesos)

        return revenue, cost

    # Individual separation
    else:
        if process_param[indiceProcessParam][3] == "0":
            revenue, cost = func_individual_separation(idx, input, input_densities, plastic_combi, process_combi,
                                                       process_param, processes, initial_mass, revenue, cost, queue,
                                                       final_output, resale_price, 0, -1, intermediate_ouputs,listaProcesos)

        elif process_param[indiceProcessParam][3] == "10":

            revenue, cost = func_individual_separation(idx, input, input_densities, plastic_combi, process_combi,
                                                       process_param, processes, initial_mass, revenue, cost, queue,
                                                       final_output, resale_price, 0, 1, intermediate_ouputs,listaProcesos)

            mass = 0
            for i in range(0, len(final_output[-1][0])):
                mass = mass + final_output[-1][0][i]
            if final_output[-1][1] == -1:
                cost[-1][0] = cost[-1][0] + mass * float(parametrosEconomicos['trituracion15'])
            else:
                cost[-1][0] = cost[-1][0] + mass * (
                        float(parametrosEconomicos['trituracion40']) + float(parametrosEconomicos['trituracion15']))

            revenue, cost = func_separation_current(idx + 1, [intermediate_ouputs[-1][7], process_combi[idx]],
                                                    input_densities, plastic_combi, process_combi, process_param,
                                                    processes, revenue, resale_price, cost, initial_mass, queue,
                                                    final_output,
                                                    intermediate_ouputs,listaProcesos)  # Processing the next step of the sequence


        elif process_param[indiceProcessParam][3] == "01":
            revenue, cost = func_individual_separation(idx, input, input_densities, plastic_combi, process_combi,
                                                       process_param, processes, initial_mass, revenue, cost, queue,
                                                       final_output, resale_price, 0, 2, intermediate_ouputs,listaProcesos)

            mass = 0
            for i in range(0, len(final_output[-1][0])):
                mass = mass + final_output[-1][0][i]
            if final_output[-1][1] == -1:
                cost[-1][0] = cost[-1][0] + mass * float(
                    parametrosEconomicos['trituracion15'])  # economical_parameters[4][0]
            else:
                cost[-1][0] = cost[-1][0] + mass * (
                        float(parametrosEconomicos['trituracion40']) + float(parametrosEconomicos['trituracion15']))

            revenue, cost = func_separation_current(idx + 1, [intermediate_ouputs[-1][7], process_combi[idx]],
                                                    input_densities, plastic_combi, process_combi, process_param,
                                                    processes, revenue, resale_price, cost, initial_mass, queue,
                                                    final_output,
                                                    intermediate_ouputs,listaProcesos)  # Processing the next step of the sequence


        elif process_param[indiceProcessParam][3] == 11:

            revenue, cost = func_individual_separation(idx, input, input_densities, plastic_combi, process_combi,
                                                       process_param, processes, initial_mass, revenue, cost, queue,
                                                       final_output, resale_price, 0, 1, intermediate_ouputs,listaProcesos)

            revenue, cost = func_individual_separation(idx, input, input_densities, plastic_combi, process_combi,
                                                       process_param, processes, initial_mass, revenue, cost, queue,
                                                       final_output, resale_price, 0, 2, intermediate_ouputs,listaProcesos)

            profit_1 = revenue[-2][0] + cost[-2][0]
            profit_2 = revenue[-1][0] + cost[-1][0]

            if profit_1 > profit_2:
                revenue.pop(-1)
                cost.pop(-1)
                final_output.pop(-1)
                intermediate_ouputs.pop(-1)
                intermediate_ouputs.pop(-1)
            else:
                revenue.pop(-2)
                cost.pop(-2)
                final_output.pop(-2)
                intermediate_ouputs.pop(-3)
                intermediate_ouputs.pop(-3)

            mass = 0
            for i in range(0, len(final_output[-1][0])):
                mass = mass + final_output[-1][0][i]
            if final_output[-1][1] == -1:
                cost[-1][0] = cost[-1][2] + mass * float(parametrosEconomicos['trituracion15'])
            else:
                cost[-1][0] = cost[-1][2] + mass * (
                        float(parametrosEconomicos['trituracion40']) + float(parametrosEconomicos['trituracion15']))

            revenue, cost = func_separation_current(idx + 1, [intermediate_ouputs[-1][10], process_combi[idx]],
                                                    input_densities, plastic_combi, process_combi, process_param,
                                                    processes, revenue, resale_price, cost, initial_mass, queue,
                                                    final_output,
                                                    intermediate_ouputs,listaProcesos)  # Processing the next step of the sequence

        return revenue, cost


# Function to process a group separation if a process targets a group of materials instead of an individual material
# The target output is the input of the next process whereas the non-target output is appended to the queue


def func_group_separation(idx, total_input, input_densities, plastic_combi, process_combi, process_param, processes,
                          initial_mass, revenue, cost, queue, final_output, resale_price, intermediate_ouputs,listaProcesos):
    output_1 = []
    output_2 = []
    total_mass = 0
    input = total_input[0]
    mass_1 = 0
    mass_2 = 0
    # yield_table=getRendimientoProceso();
    indiceProcessParam = listaProcesos.index(str(process_combi[idx]))
    for i in range(0, len(input)):
        total_mass = total_mass + input[i]  # total mass present in the input

    for i in range(len(input)):  # range the different plastics present in the input

        mass = yield_table[process_combi[idx]][i] * input[i]  # mass separated = yield * mass

        output_1.append(mass)  # target output
        output_2.append(input[i] - mass)  # non-target output
        mass_1 = mass_1 + mass
        mass_2 = mass_2 + (input[i] - mass)

    # Plastics targeted in the first output and their associated processes
    plastic_combi_1 = []
    process_combi_1 = []

    # Plastics targeted in the second output and their associated processes
    plastic_combi_2 = []
    process_combi_2 = []

    # Split of the current plastic and process vectors into two vectors for the first and second output stream
    # Output 1 contains the plastics targeted by the process and output the plastics non targeted
    # the next processes of the sequence are divided in two sequences : one for each output
    # if a process targets a plastic in the target output, he will be added in the first sequence
    # if a process targets a plastic in the non target output, he will be added in the second sequence
    # if a process targets a plastic in both output, he will be added in both sequences

    for i in range(idx + 1, len(plastic_combi)):  # range the plastics that will be targeted after this

        if process_param[indiceProcessParam][1].count(plastic_combi[i]) == 1:  # if the plastic is targeted i
            plastic_combi_1.append(plastic_combi[i])
            process_combi_1.append(process_combi[i])


        else:
            plastic_combi_2.append(plastic_combi[i])
            process_combi_2.append(process_combi[i])

    # Second output and parameters associated are added to the queue to be processed afterwards
    second_output = [[output_2, process_combi[idx]], plastic_combi_2, process_combi_2, input_densities]
    queue.append(second_output)

    cost = func_costs(idx, total_mass, process_combi, process_param, cost,indiceProcessParam)
    intermediate_ouputs.append(
        [total_input[1], process_combi[idx], 0, '/', '/', int(cost[-1][0] * mass_1 / (mass_1 + mass_2)),
         int(cost[-1][2] * mass_1 / (mass_1 + mass_2)), int(cost[-1][3] * mass_1 / (mass_1 + mass_2)), 0, '/',
         output_1])
    intermediate_ouputs.append(
        [total_input[1], process_combi[idx], 1, '/', '/', int(cost[-1][0] * mass_2 / (mass_2 + mass_2)),
         int(cost[-1][2] * mass_2 / (mass_1 + mass_2)), int(cost[-1][3] * mass_2 / (mass_1 + mass_2)), 0, '/',
         output_2])

    revenue, cost = func_separation_current(0, [output_1, process_combi[idx]], input_densities, plastic_combi_1,
                                            process_combi_1, process_param, processes, revenue, resale_price, cost,
                                            initial_mass, queue, final_output, intermediate_ouputs,listaProcesos)

    return revenue, cost


def getRendimientoProceso(materiales):
    matrizRendimientos = []
    #materiales = getListaMagterialesEquipo(codequipo)
    for pro in codProcesos:
        listaAux = []
        if (pro != '3'):
            for mtl in (materiales):
                dicc = (RendimientoProceso.objects.values('valor', 'idmaterialreferencia').filter(idproceso=pro,
                                                                                                  idmaterialreferencia=
                                                                                                  mtl[
                                                                                                      'materiales']).distinct().order_by(
                    'idmaterialreferencia'))

                # for item in range(0, len(materiales)):
                for reg in dicc:
                    val = float(reg['valor'])
                    listaAux.append(val)
            # if (len(listaAux)<len(materiales)):
        while len(listaAux) < len(materiales):
            listaAux.append(None)
        matrizRendimientos.append(listaAux)
    return matrizRendimientos


# Function to process a density separation
# The targeted densities are the input of the next process whereas the non-target densities are appended to the queue

def func_density_separation(idx, total_input, input_densities, plastic_combi, process_combi, process_param, processes,
                            initial_mass, revenue, cost, queue, final_output, resale_price, intermediate_ouputs,listaProcesos):
    global densities
    input = total_input[0]
    indiceProcessParam = listaProcesos.index(str(process_combi[idx]))
    total_mass = sum(input)

    density_separation = int(process_param[indiceProcessParam][3])  # Density to target
    first_density_input = input_densities[0]  # First density of the input
    last_density_input = input_densities[1]  # Last density of the input
    mass_1 = 0
    mass_2 = 0

    # Allocation of the two vectors containing the outputs
    output_1 = []
    output_2 = []
    current_output_1 = []
    current_output_2 = []

    for i in range(0, len(input)):
        output_1.append(0)
        output_2.append(0)
        current_output_1.append(0)
        current_output_2.append(0)

    input_densities_1 = []
    input_densities_2 = []

    for i in range(first_density_input,
                   density_separation):  # Range the densities from the first density of the input to the density of the separation
        for j in range(1, len(input) + 1):
            current_output_1[j - 1] = current_output_1[j - 1] + densities[i][j] * yield_table[process_combi[idx]][0]
            current_output_2[j - 1] = current_output_2[j - 1] + densities[i][j] * (
                    1 - yield_table[process_combi[idx]][0])  # Contains particles lighter than the density separation

    for i in range(density_separation,
                   last_density_input + 1):  # Range the densities from the the density of the separation to the last density of the input
        for j in range(1, len(input) + 1):
            current_output_1[j - 1] = current_output_1[j - 1] + densities[i][j] * (
                    1 - yield_table[process_combi[idx]][0])
            current_output_2[j - 1] = current_output_2[j - 1] + densities[i][j] * yield_table[process_combi[idx]][
                0]  # Contains particles heavier than the density separation

    # First and last density of each output
    input_densities_1.append(first_density_input)
    input_densities_1.append(density_separation - 1)

    input_densities_2.append(density_separation)
    input_densities_2.append(last_density_input)

    # Next processes of the combination are copied in an other list in order to be added in the queue
    plastic_combi_2 = []
    process_combi_2 = []

    for i in range(idx + 1, len(plastic_combi)):
        plastic_combi_2.append(plastic_combi[i])
        process_combi_2.append(process_combi[i])
    tot_mass_1 = 0
    tot_mass_2 = 0
    # multiplication of the mass percentage of particles in each ouput by the mass of the plastics
    for i in range(0, len(input)):
        if current_output_1[i] + current_output_2[i] == 0:
            pass
        else:
            output_1[i] = current_output_1[i] * input[i] / (current_output_1[i] + current_output_2[i])
            output_2[i] = current_output_2[i] * input[i] / (current_output_1[i] + current_output_2[i])

            tot_mass_1 = tot_mass_1 + current_output_1[i] * input[i] / (current_output_1[i] + current_output_2[i])
            tot_mass_2 = tot_mass_2 + current_output_2[i] * input[i] / (current_output_1[i] + current_output_2[i])

    # Computation of the costs
    cost = func_costs(idx, total_mass, process_combi, process_param, cost,indiceProcessParam)
    new_element = [[output_2, process_combi[idx]], plastic_combi_2, process_combi_2,
                   input_densities_2]  # Second output and parameters associated are added to the queue to be processed afterwards
    queue.append(new_element)

    # Add the outputs to the intermediate results
    if tot_mass_1 != 0:
        intermediate_ouputs.append(
            [total_input[1], process_combi[idx], 0, '/', '/', int(cost[-1][0] * tot_mass_1 / total_mass),
             int(cost[-1][2] * tot_mass_1 / total_mass), int(cost[-1][3] * tot_mass_1 / total_mass), 0, '/', output_1])
    else:
        intermediate_ouputs.append([total_input[1], process_combi[idx], 0, '/', '/', 0, 0, 0, 0, '/', output_1])
    if tot_mass_2 != 0:
        intermediate_ouputs.append(
            [total_input[1], process_combi[idx], 1, '/', '/', int(cost[-1][0] * tot_mass_2 / total_mass),
             int(cost[-1][2] * tot_mass_2 / total_mass), int(cost[-1][3] * tot_mass_2 / total_mass), 0, '/', output_2])
    else:
        intermediate_ouputs.append([total_input[1], process_combi[idx], 1, '/', '/', 0, 0, 0, 0, '/', output_2])
    revenue, cost = func_separation_current(idx + 1, [output_1, process_combi[idx]], input_densities_1, plastic_combi,
                                            process_combi, process_param, processes, revenue, resale_price, cost,
                                            initial_mass, queue, final_output, intermediate_ouputs,listaProcesos)
    return revenue, cost


# Function to process a multiple output separation, such as LIBS
# There is an output for each of the plastic
# Funcion para separacion multiple, LIBS
def func_multiple_output_separation(idx, total_input, input_densities, plastic_combi, process_combi, process_param,
                                    processes, revenue, resale_price, cost, initial_mass, queue, final_output,
                                    intermediate_ouputs,listaProcesos):
    output = []
    mass = 0
    input = total_input[0]
    mass = sum(input)
    indiceProcessParam = listaProcesos.index(str(process_combi[idx]))
    # Computation of the total mass proccesed in order to evaluate the costs
    for i in range(0, len(input) + 1):
        output.append([])

        for j in range(0, len(input)):
            output[i].append(
                None)  # Allocation of a matrix with the size (n_plastic*n_plastic). Each cell represents the fraction of a plastic in an output.
    # Libs efficienci table
    purity_table = process_param[indiceProcessParam][1]

    # Computation of the outputs based on the input mass and the pyrity table of the process
    for i in range(0, len(input)):
        for j in range(0, len(input) + 1):
            output[j][i] = input[i] * purity_table[i][j]  # Output = mass of the plastic * yield

    for i in range(0, len(input) + 1):
        # Computation of the revenue for each output
        if i == len(input):
            revenue, final_output, post_treatment_cost = func_revenues([output[i], process_combi[idx]], 0, initial_mass,
                                                                       revenue, cost, resale_price, final_output,
                                                                       input_densities)
        else:
            revenue, final_output, post_treatment_cost = func_revenues([output[i], process_combi[idx]], i, initial_mass,
                                                                       revenue, cost, resale_price, final_output,
                                                                       input_densities)

    # computation of the costs of the sequence
    cost = func_costs(idx, mass, process_combi, process_param, cost,indiceProcessParam)

    if final_output[-len(output) + i] == -1:
        cost[-1][3] = float(parametrosEconomicos['trituracion15']) * mass
    else:

        cost[-1][3] = (float(parametrosEconomicos['trituracion40']) + float(
            parametrosEconomicos['trituracion15'])) * mass

    # Add the outputs to the intermediate results
    for i in range(0, len(output)):
        mass_output = 0
        for j in range(0, len(output[i])):
            mass_output = mass_output + output[i][j]

        intermediate_ouputs.append([total_input[1], process_combi[idx], i, int(final_output[-len(output) + i][1]),
                                    int(revenue[-len(output) + i][0]), int(cost[-1][0] * mass_output / mass),
                                    int(cost[-1][2] * mass_output / mass), int(cost[-1][3] * mass_output / mass),
                                    int(revenue[-len(output) + i][1]), revenue[-len(output) + i][-1], output[i]])

    revenue, cost = func_separation_current(len(process_combi), [[], process_combi[idx]], input_densities,
                                            plastic_combi, process_combi, process_param, processes, revenue,
                                            resale_price, cost, initial_mass, queue, final_output, intermediate_ouputs,listaProcesos)
    return revenue, cost


# Function to process an individual separation.
# The output of the function is the grade, the recovery, the cost and the revenue of this step added to the total metrics
# The non-target output is fed in the next process

def func_individual_separation(idx, total_input, input_densities, plastic_combi, process_combi, process_param,
                               processes, initial_mass, revenue, cost, queue, final_output, resale_price, idx_caroucel,
                               output_to_caroucel, intermediate_ouputs,listaProcesos):
    # idx refers to the the idx of the step that has to be processed
    indiceProcessParam = listaProcesos.index(str(process_combi[idx]))
    input = total_input[0]  # mass composition of the input

    output_1 = []  # target_output
    output_2 = []  # non-target_output
    total_mass_1 = 0  # mass of the first output
    total_mass_2 = 0  # mass of the second output

    # range all the plastics of the input
    for i in range(len(input)):
        mass = yield_table[process_combi[idx]][i] * input[i]

        output_1.append(mass)  # adds the target mass correctly identified in the target output
        output_2.append(input[i] - mass)  # adds the remaining mass wrongly identified in the non target output

        total_mass_1 = total_mass_1 + mass  # mass of the target output
        total_mass_2 = total_mass_2 + input[i] - mass  # mass of the non-target output

    intermediate_ouput_1 = []
    intermediate_ouput_2 = []

    # Adds the different masses in intermediate outputs
    for i in range(0, len(output_1)):
        intermediate_ouput_1.append(output_1[i])
        intermediate_ouput_2.append(output_2[i])

    # No caroucel loop has been tried.
    if idx_caroucel == 0:
        # Check the revenue of the targeted output
        revenue, final_output, disassembly = func_revenues([output_1, process_combi[idx]], plastic_combi[idx],
                                                           initial_mass, revenue, cost, resale_price, final_output,
                                                           input_densities)  # Computation of grade, recovery and revenue of the target stream
        total_mass = total_mass_1 + total_mass_2
        fraction_1 = total_mass_1 / total_mass
        fraction_2 = total_mass_2 / total_mass

        # computation of the costs based on the mass processed
        cost = func_costs(idx, total_mass, process_combi, process_param, cost)

        # Adds results to the intermediate outputs : the processes where it does come from, the process just achieved and the mass composition of both outputs
        intermediate_ouputs.append(
            [total_input[1], process_combi[idx], 0, int(final_output[-1][1]), int(revenue[-1][0]),
             int(cost[-1][0] * fraction_1), int((cost[-1][2] + disassembly) * fraction_1), 0, revenue[-1][-1],
             intermediate_ouput_1])
        intermediate_ouputs.append([total_input[1], process_combi[idx], 1, '/', '/', int(cost[-1][0] * fraction_2),
                                    int((cost[-1][2] + disassembly) * fraction_2), 0, '/', intermediate_ouput_2])
        # Compute the caroucel loop with the remaining output

        if output_to_caroucel == -1:
            if final_output[-1][1] == -1:
                cost[-1][3] = cost[-1][3] + total_mass_1 * float(parametrosEconomicos['trituracion15'])
            else:
                cost[-1][3] = cost[-1][3] + total_mass_1 * (
                        float(parametrosEconomicos['trituracion40']) + float(parametrosEconomicos['trituracion15']))
            revenue, cost = func_separation_current(idx + 1, [output_2, process_combi[idx]], input_densities,
                                                    plastic_combi, process_combi, process_param, processes, revenue,
                                                    resale_price, cost, initial_mass, queue, final_output,
                                                    intermediate_ouputs)
        elif output_to_caroucel == 1:
            revenue, cost = func_individual_separation(idx, [output_1, process_combi[idx]], input_densities,
                                                       plastic_combi, process_combi, process_param, processes,
                                                       initial_mass, revenue, cost, queue, final_output, resale_price,
                                                       1, 1, intermediate_ouputs,listaProcesos)

        elif output_to_caroucel == 2:
            revenue, cost = func_individual_separation(idx, [output_2, process_combi[idx]], input_densities,
                                                       plastic_combi, process_combi, process_param, processes,
                                                       initial_mass, revenue, cost, queue, final_output, resale_price,
                                                       1, 2, intermediate_ouputs,listaProcesos)

    # caroucel loop has been processed and it is useful to check if the profit is higher with this additional step or not
    else:
        if output_to_caroucel == 1:

            for i in range(len(output_2)):
                output_2[i] = output_2[i] + intermediate_ouputs[-1][8][i]
            revenue, final_output, disassembly = func_revenues([output_1, process_combi[idx]], plastic_combi[idx],
                                                               initial_mass, revenue, cost, resale_price, final_output,
                                                               input_densities)

        else:
            for i in range(len(output_1)):
                output_1[i] = output_1[i] + intermediate_ouputs[-2][8][i]
            revenue, final_output, disassembly = func_revenues([output_1, process_combi[idx]], plastic_combi[idx],
                                                               initial_mass, revenue, cost, resale_price, final_output,
                                                               input_densities)

        # computation of the costs and revenues with the caroucel loop

        total_mass = total_mass_1 + total_mass_2

        cost = func_costs(idx, total_mass, process_combi, process_param, cost,indiceProcessParam)

        # addition of the costs of both steps in order to get the tocal cost of the caroucel loop
        caroucel_cost = cost[-1][0] + cost[-2][0]
        # check if the caroucel loop is optimal or not
        if (revenue[-1][0] - caroucel_cost) > (
                revenue[-2][0] - cost[-2][0]):  # caroucel is optimal if the profit is higher with a second loop

            disassembly_cost_1 = revenue[-2][1]
            revenue.pop(-2)
            revenue[-1][1] = disassembly_cost_1
            disassembly_cost_2 = cost[-2][2]

            cost.pop(-1)
            cost.pop(-1)

            cost.append([caroucel_cost, disassembly_cost_2, 0,
                         process_combi[idx]])  # adding the costs of both steps in the costs vector
            final_output.pop(-2)
            for i in range(0, len(output_1)):
                final_output[-1][0][i] = output_1[i]

            previous_process = intermediate_ouputs[-1][0]
            intermediate_ouputs.pop(-1)
            intermediate_ouputs.pop(-1)

            mass_1 = 0
            mass_2 = 0

            for i in range(0, len(output_1)):
                mass_1 = output_1[i] + mass_1
                mass_2 = output_2[i] + mass_2

            intermediate_ouputs.append(
                [previous_process, process_combi[idx] + 0.1 * output_to_caroucel, 0, int(final_output[-1][1]),
                 int(revenue[-1][0]), int(caroucel_cost * mass_1 / (mass_1 + mass_2)),
                 (disassembly_cost_2 + disassembly_cost_1) * mass_1 / (mass_1 + mass_2), 0, 0, revenue[-1][-1],
                 output_1])
            intermediate_ouputs.append([previous_process, process_combi[idx] + 0.1 * output_to_caroucel, 1, '/', '/',
                                        int(caroucel_cost * mass_2 / (mass_2 + mass_1)),
                                        (disassembly_cost_1 + disassembly_cost_2) * mass_2 / (mass_1 + mass_2), 0, 0,
                                        '/', output_2])



        else:  # caroucel has higher costs than revenues generated. Therefore a single step for the process is kept and caroucel loop is cancelled

            revenue.pop(-1)
            cost.pop(-1)
            final_output.pop(-1)

    return revenue, cost


##############################################################################################################################

# Function to compute the revevenus of a specific input
# There are two constraints to compute the revenue

# 1. The maximum level of impurity for each plastic. In function of the targeted plastic, each other plastic has a maximum fraction acceptable in the mix. The level of impurity depends on the compatibility matrix. If each plastic is below the maximum fraction, the first purity step is achievd. If it is not the case, the second step is tried with fractions quite higher than the first step. There is also a third step if the second is not achieved. Finally if the third is not achieved, the mix has to be incinerated

# 2. The cocktail effect. Each plastic mass is multiplied by a factor (depending on the plastic compatibility). If the addition of all these factors, is below a thrshold, the first step is achieved. There are also 3 steps before the incineration, each with different factors and threshold.

# To find the step at which the plastic is resold, we have to take the maximum between the two steps.
# E.G : if the first step is achievd for purity and the second for the cocktail effect, plastic will be resold at the second step.

# There is also a parameter related to each step to reduce the resale price of the plastic.


def func_revenues(total_input, idx_target, initial_mass, revenue, cost, resale_price, final_output, densities):
    global compatibility, economical_parameters
    input = total_input[0]
    incineration_cost = float(parametrosEconomicos['incineracion'])
    # economical_parameters[0][0]  # Incineration cost
    number_steps = int(parametrosEconomicos['pasospureza'])
    num_plastics = len(input)
    purity_index = 0
    cocktail_index = 0
    resale_price_parameter = 0
    impurity = impuerezas#getImpuerezasMatriz(1)
    cocktail = efectoCoctel#getCoctelMatriz(2)
    # Check if the target material is known and is the single target. This is the case for individual separation and multiple output separation.
    if idx_target > -1:

        mass = sum(input)

        target_mass = input[idx_target]  # mass of the target plastic

        if mass == 0:
            resale = 0
            post_treatment_cost = 0
            current_resale = 0
            current_idx_target = -1

        else:
            current_resale = -incineration_cost * mass  # if the lowest purity isn't achieved or if the compatibility matrix doesn't allow recycling
            current_idx_target = -1

            # check the impurity constraint
            for i in range(0, number_steps):
                switch_index = 0

                for j in range(len(input)):  # range all the plastics
                    if 100 * input[j] / mass <= impurity[(num_plastics + 1) * i + idx_target][
                        j]:  # check if each plastic is below the maximum acceptable fraction
                        pass
                    else:  # if not, the second step is tried
                        purity_index = i + 1
                        switch_index = 1
                        break
                if switch_index == 0:  # it means that the last step is achieved, and it is not needed to try the next step
                    break
                else:
                    pass
            # check the cocktail effect
            for i in range(purity_index, number_steps):  # start from the step achieved with the purity constraint
                cocktail_mass = 0

                for j in range(len(input)):  # range all the plastics
                    cocktail_mass = cocktail_mass + input[j] * cocktail[(num_plastics + 1) * i + idx_target + 1][
                        j]  # multiply the mass of each plastic by the coressponding factor
                if cocktail_mass <= cocktail[(num_plastics + 1) * i][
                    0]:  # check if the sum of all these factors is below a certain threshold
                    cocktail_index = i  # step achieved by the cocktail constraint
                    break
                else:  # if not the next step is tried
                    pass

            resale_price_parameter = max(cocktail_index,
                                         purity_index)  # takes the maximum between purity and cocktail constraint
            parametroVenta = ''
            if resale_price_parameter == 2:
                parametroVenta = 'patametroreventa3'
            if resale_price_parameter == 1:
                parametroVenta = 'patametroreventa2'
            if resale_price_parameter == 0:
                parametroVenta = 'patametroreventa1'
            if resale_price_parameter == number_steps:
                post_treatment_cost = 0  # one or both contraints haven't been achieved and plastic is incinerated
            else:
                current_idx_target = idx_target  # idx of the plastic that is resold
                current_resale = mass * resale_price[idx_target] * float(
                    parametrosEconomicos[parametroVenta])  # economical_parameters[6 + resale_price_parameter][0]
                post_treatment_cost = float(parametrosEconomicos[
                                                'posttratamiento']) * mass  # economical_parameters[2][0] * mass  # resale price = mass of the mix * resale price of the plastic *  parameter related to the step achieve
        final_output.append([input, current_idx_target, densities, total_input[1], post_treatment_cost, current_resale])
        revenue.append([current_resale, post_treatment_cost,
                        resale_price_parameter])  # check which is the best end-of-life for the plastic, depending on the revenue/cost
        return revenue, final_output, post_treatment_cost

    # if the material targeted by the process is a group of material (density separation or group separation), it needs to check the potential revenue for each plastic
    # The same procedure as before is done except that this time, it checks the potential revenue for all the plastics and keeps the revenue with the highest profit. This one is the real target plastic.
    # Example : If XRF targets Brominated plastics, there is not a single plastic targeted. Therefore the algorithm is going to compute the revenues/costs for each plastic and keeps the highest. If there is only ABS BrFR and no HIPS BrFR, the mix will be resold as ABS BrFR.
    else:
        pass


def getImpuerezasMatriz(tipoImpuereza):
    numEtapas = list(Impureza.objects.values('idimpureza').filter(idtipoimpureza=tipoImpuereza).order_by('idimpureza'))
    listaImpurezas = []
    print("IMPUEREZAS*******************")
    for ne in (numEtapas):
        for mat in (numeroMateriales):
            listaaux = []
            valorImpuerezas = list(ImpuezaMaterial.objects.values('valor').filter(idimpuereza=int(ne['idimpureza']),
                                                                                  idimaterial=int(
                                                                                      mat['materiales'])).order_by(
                'idimaterialreferencia'))
            for valor in valorImpuerezas:
                listaaux.append(float(valor['valor']))
            listaImpurezas.append(listaaux)
        listaaux = len(numeroMateriales) * [None]
        listaImpurezas.append(listaaux)
    listaImpurezas.pop()
    return listaImpurezas


def getCoctelMatriz(tipoImpuereza):
    numEtapas = list(
        Impureza.objects.values('idimpureza', 'parametro').filter(idtipoimpureza=tipoImpuereza).order_by('idimpureza'))
    listaImpurezas = []

    for ne in (numEtapas):
        listapara = len(numeroMateriales) * [None]
        listapara.insert(0, float(ne['parametro']))
        listaImpurezas.append(listapara)
        for mat in (numeroMateriales):
            listaaux = []
            valorImpuerezas = list(ImpuezaMaterial.objects.values('valor').filter(idimpuereza=int(ne['idimpureza']),
                                                                                  idimaterial=int(
                                                                                      mat['materiales'])).order_by(
                'idimaterialreferencia'))
            for valor in valorImpuerezas:
                listaaux.append(float(valor['valor']))
            listaImpurezas.append(listaaux)

    return listaImpurezas


# Funcion para costos delproceso separacion
# Multiplica la masa por el costo del parametro del proceso

def func_costs(idx, total_mass, process_combi, process_param, cost,indiceProcessParam):
    param_cost = process_param[indiceProcessParam][2]
    global economical_parameters

    treatment_cost = total_mass * param_cost  # Treatment costs for the process (labour, energy, maintenance)

    # if-else condition to check is manual disassembly or shredding costs need to be taken into account
    if (idx == 0 and process_param[indiceProcessParam][0] == 0) or (idx == 0 and process_param[indiceProcessParam][
        0] == 3):  # It is the first process and it belongs to the first group of process. Manual disassembly is needed
        manual_disassembly = float(
            parametrosEconomicos['desmontajemanual']) * total_mass  # economical_parameters[1][0] * total_mass
        rough_shredding = 0
        fine_shredding = 0

    else:

        if process_param[indiceProcessParam][0] == process_param[indiceProcessParam-1][
            0] and idx != 0:  # check if the previous process belongs to the same group of process. If yes, no size reduction process is needed
            manual_disassembly = 0
            rough_shredding = 0
            fine_shredding = 0
        elif process_param[indiceProcessParam][
            0] == 1:  # If it is the first process of the second group, a rough shredding process is required
            manual_disassembly = 0
            rough_shredding = float(
                parametrosEconomicos['trituracion40']) * total_mass  # economical_parameters[3][0] * total_mass
            fine_shredding = 0
        else:  # If it is the first process of the first group, a fine shredding is required (and maybe also a rough shredding)
            list = []
            for i in range(0, idx):
                list.append(process_param[indiceProcessParam][0])
            if list.count(
                    1) > 0:  # if list.count(1)>0 means that there were processes from the second group and the rough shredding is not needed
                manual_disassembly = 0
                rough_shredding = float(
                    parametrosEconomicos['trituracion40']) * total_mass  # economical_parameters[3][0] * total_mass
                fine_shredding = 0
            else:  # in this case, there were none processes from the second group and therefore a rough shredding as well as a fine shredding are needed
                manual_disassembly = 0

                rough_shredding = float(
                    parametrosEconomicos['trituracion40']) * total_mass  # economical_parameters[3][0] * total_mass
                fine_shredding = float(
                    parametrosEconomicos['trituracion15']) * total_mass  # economical_parameters[4][0] * total_mass

    treatment_cost = treatment_cost  # + manual_disassembly + rough_shredding + fine_shredding #total treatment cost of the process
    size_reduction = manual_disassembly + rough_shredding + fine_shredding

    throughput = process_param[indiceProcessParam][-1][
        1]  # Throughput and investment for the first level of the machine
    investment = process_param[indiceProcessParam][-1][0]
    hours_year = 3120

    increment = 0

    while total_mass > throughput * hours_year:  # check if the mass to process is lower the throughput. If it is not the case, a machine with a higher throughput is needed and then also a higher investment cost
        increment = increment + process_param[indiceProcessParam][-1][2]
        investment = investment + increment * investment  # incrementation of the investment
        throughput = throughput + increment * throughput  # incrementation of the throughput

    depreciation_years = process_param[indiceProcessParam][-1][
        3]  # number of years taken into account for the depreciation of the machine

    cost.append([treatment_cost, '/', manual_disassembly, rough_shredding + fine_shredding, process_combi[idx]])
    return cost
