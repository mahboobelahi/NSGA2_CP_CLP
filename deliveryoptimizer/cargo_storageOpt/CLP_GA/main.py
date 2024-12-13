from pprint import pprint
import time
from . import population as geni
from . import fitnesscalc as ft
from . import recombination as re
from . import mutation as mt
from .import nsga2 as ns
from .import survivor_selection as ss
from tabulate import tabulate
from copy import deepcopy
from .helper import *
from .configurations import* 
from .container import Container as cont
from ..models.container import Container
from ..models.GAComputationResults import GAResult
from .placementAlgorithm import PlacementAlgorithm as PA
from .configurations import config_dict

def main(ORDERS):
    
    computation_complete(flag=False)
    spinFlag()
    NUM_OF_INDIVIDUALS = config_dict["NUM_OF_INDIVIDUALS"]
    NUM_OF_GENERATIONS = config_dict["NUM_OF_GENERATIONS"]#00#50
    PC = config_dict["PC"]
    PM1 = config_dict["PM1"]
    PM2 = config_dict["PM2"]
    K = config_dict["K"]
    ROTATIONS = config_dict["ROTATIONS"]
    quantities = []
    custs = {}
    box_params = {}
    timing_record = {}
    print(tabulate([['Generations', NUM_OF_GENERATIONS], ['Individuals', NUM_OF_INDIVIDUALS],
                        ['Rotations', ROTATIONS], [
                            'Crossover Prob.', PC], ['Mutation Prob1', PM1],
                        ['Mutation Prob2', PM2], ['Tournament Size', K]], headers=['Parameter', 'Value'],
                       tablefmt="github"))

    
    id=ORDERS[0].get_fields().get("containerId")
    supportRatio=ORDERS[0].get_fields().get("supportRatio")
    obj = Container.objects.get(cont_ID=id)
    L,W,H = obj.get_internal_dimensions().get("cm")
    CONT = cont(
        name=f"ISO-{obj.cont_ID} feet Dry Container",
        LWH=[L,W,H],#L,W,H
        max_weight=obj.payload
    ) 

    result = {"cargo_metadata": {
                "id": id,#ORDERS[0].get("container"),
                    "container_dimension": CONT.get_dimension(),
                    "container_weight": 28080,
                    "container_volume": CONT.get_volume(),
                    
                    "consignment_origin": [ord.origin for ord in ORDERS],
                    "consignment_destinations": [ord.destination for ord in ORDERS]
                }}
    
    set_box_range(custs,quantities,ORDERS)
    total_value = create_box_objects(ORDERS,CONT,box_params)
    pa = PA(box_params=box_params, container = deepcopy(CONT), SR=supportRatio,total_value=total_value,
            custs=deepcopy(custs),result=deepcopy(result),
            population_size=NUM_OF_INDIVIDUALS, generations=NUM_OF_GENERATIONS,
            k=K, pc=PC, pm1=PM1, pm2=PM2, ROTATIONS=ROTATIONS
            )
    pa.optimize()
    # #! Storing the average values over every single iteration
    # average_vol = []
    # average_num = []
    # average_value = []
    # for i in range(1):
    #     # Generate the initial population
    #     population = geni.generate_pop(box_params, NUM_OF_INDIVIDUALS, ROTATIONS,custs)
    #     gen = 0
    #     timing_record = {}
    #     average_fitness = []
    #     population, fitness = ft.evaluate(population, CONT, box_params, total_value,support_ratio=supportRatio)
    #     population = ns.rank(population, fitness)
    #     while gen < NUM_OF_GENERATIONS:
    #         print(f"Running current Generations.....{gen}")
            # timing_record[gen] = {"start_time": time.time(),
            #                           "end_time": None}
    #         # population, fitness = ft.evaluate(population, CONT, box_params, total_value,support_ratio=supportRatio)
    #         # population = ns.rank(population, fitness)
    #         offsprings = re.crossover(deepcopy(population), PC, k=K)
    #         offsprings = mt.mutate(offsprings, PM1, PM2, ROTATIONS)
    #         population = ss.select(population, offsprings, CONT, box_params, total_value,
    #                                 NUM_OF_INDIVIDUALS)
    #         average_fitness.append(calc_average_fitness(population))
    #         #print(f"Running current Generations.....{gen}")
            # timing_record[gen]["end_time"] = time.time()
            # elapsed_time = timing_record[gen]["end_time"] - \
            #         timing_record[gen]["start_time"]
            # timing_record[gen]["elapsed_time"] = round(elapsed_time/60, 2)
    #         # pprint(timing_record)
    #         gen += 1
    #         pprint(timing_record)

    #     result["elapsed_times"] = extract_elapsed_times(timing_record)
    #     result["cargo_metadata"]["total_items"] = len(CONT.items)
    #     # Storing the final Rank 1 solutions
    #     p_ind="0"
        # for key, value in population.items():
        #     if value['Rank'] == 1 :#or value['Rank'] == 2:
        #         # print(p_ind,key)
        #         collect_data(result, value, p_ind, key)
    #     # draw_pareto(population)
    #     average_vol.append(average_fitness[-1][0])
    #     average_num.append(average_fitness[-1][1])
    #     average_value.append(average_fitness[-1][2])
    #     population.clear()
    #     del CONT
    # print(tabulate(
    #     [['Problem Set', 'Test1'], ['Runs', 1], ['Avg. Volume%', sum(average_vol) / len(average_vol)],
    #         ['Avg. Number%', sum(average_num) / len(average_num)],
    #         ['Avg. Value%', sum(average_value) / len(average_value)]],
    #     headers=['Parameter', 'Value'], tablefmt="github"))
    # # requests.get('http://localhost:8000/storage/set-computing')
    # # ORDERS.clear()
    
    # try:
    #     # Create a GAComputationResult instance
    #     current_datetime = datetime.now()
    #     file_name = f'report_{current_datetime.strftime("%Y-%m-%d_%H-%M-%S")}.json'
    #     computation_result = GAResult(file_name = file_name,result_json=result)

    #     # Save the instance to the database
    #     computation_result.save()

    #     print("GAComputationResult saved successfully!")
    #     computation_complete(flag=True)#flag=True
    #     spinFlag(flag=False)
    #     # queryset = Computation.objects.filter(is_fetched=False).order_by('started_at')
    

    #     # sorted_queryset = list(queryset)

    #     # # Make sure there are items in the sorted_queryset
    #     # if sorted_queryset:
            
    #     #     sorted_queryset[0].status = True
    #     #     sorted_queryset[0].is_fetched = True
    #     #     sorted_queryset[0].save()
    #     #     print(queryset)
    #     # else:
    #     #     print("No items in the sorted queryset")

    # except Exception as e:
    #     # Handle any exceptions that occur during creation or saving
    #     print("Error:", e)
    
    
    
