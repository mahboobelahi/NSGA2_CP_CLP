from pprint import pprint
import random
from copy import deepcopy
from operator import itemgetter
import time
from .helper import*
from . import population as gen_pop 
from .fitnesscalc import fitnessFunction as FT
from ..models.GAComputationResults import GAResult

class PlacementAlgorithm:
    def __init__(self, box_params, container, SR,custs, result, total_value,
                 ROTATIONS, population_size=100, k=2,
                 generations=100, pc=0.8, pm1=0.2, pm2=0.02):
        self.box_params = box_params
        self.container = container
        self.SR =  SR
        self.custs = custs
        self.result = result
        self.total_value = total_value
        self.rotation = ROTATIONS
        self.total_value = total_value
        self.population_size = population_size
        self.generations = generations
        self.pc = pc  
        self.numP = int(self.pc * self.population_size)
        self.k = k
        self.pm1 = pm1  
        self.pm2 = pm2  
        self.avg_fitness = []
        self.population = self.generate_population()

        

    def generate_population(self):
        """
        This function uses the dimensions of the boxes to create a diploid chromosome for every individual in the population,
        It consists of 'order', which is a permutation as the boxes order and a list of their rotation values
        """
        
        return gen_pop.generate_pop(self.box_params,self.population_size,self.rotation,self.custs)

    def evaluate(self,pop):
        population, ft= FT(pop,self.container,
                                self.box_params,self.total_value,self.SR)

        return population, ft

    def select_parents(self):
        """
        Selects parents for crossover using tournament selection based on rank and crowding distance.
        """
        parents = {}
        individuals = deepcopy(list(self.population.values()))
        for index in range(self.numP):  
            pool = random.sample(individuals, self.k)
            pool.sort(key=lambda ind: (ind['Rank']))

            # Get the highest ranked individual(s)
            top_rank = pool[0]['Rank']
            highest_ranked = [ind for ind in pool if ind['Rank'] == top_rank]
            
            if len(highest_ranked) == 1:\
                best = highest_ranked[0]
            else:
                pool.sort(key=lambda ind: (ind['crowding_distance']))
                best = pool[0]
            parents[index] = best
            individuals.remove(best)
        return parents

    def recombine(self, parents):
        """
        Performs crossover on pairs of parents to generate offspring.
        Each offspring inherits a combination of 'order' and 'rotate' traits from its parents.
        """
        offsprings = {}
        parent_keys = list(parents.keys())
        custs_index = parents[parent_keys[0]].get("custs_index")

        random.shuffle(parent_keys)
        for x in range(0, len(parents), 2):
            k1 = random.choice(parent_keys)
            o1 = deepcopy(parents[k1]['order'])
            r1 = deepcopy(parents[k1]['rotate'])
            parent_keys.remove(k1)
            
            k2 = random.choice(parent_keys)
            o2 = deepcopy(parents[k2]['order'])
            r2 = deepcopy(parents[k2]['rotate'])
            parent_keys.remove(k2)
            
            i = random.randint(1, int(len(o1) / 2) + 1)
            j = random.randint(i + 1, int(len(o1) - 1))
            
            co1, co2 = [-1] * len(o1), [-1] * len(o2)
            cr1, cr2 = [-1] * len(r1), [-1] * len(r2)
            
            co1[i:j + 1], co2[i:j + 1] = o1[i:j + 1], o2[i:j + 1]
            cr1[i:j + 1], cr2[i:j + 1] = r1[i:j + 1], r2[i:j + 1]
            
            pos = (j + 1) % len(o2)
            for k in range(len(o2)):
                if o2[k] not in co1 and co1[pos] == -1:
                    co1[pos] = o2[k]
                    pos = (pos + 1) % len(o2)
                    
            pos = (j + 1) % len(o2)
            for k in range(len(o1)):
                if o1[k] not in co2 and co2[pos] == -1:
                    co2[pos] = o1[k]
                    pos = (pos + 1) % len(o1)
                    
            pos = (j + 1) % len(o2)
            for k in range(len(r2)):
                if cr1[pos] == -1:
                    cr1[pos] = r2[k]
                    pos = (pos + 1) % len(r2)
                    
            pos = (j + 1) % len(o2)
            for k in range(len(r1)):
                if cr2[pos] == -1:
                    cr2[pos] = r1[k]
                    pos = (pos + 1) % len(r1)

            # offsprings[x], offsprings[x + 1] = {'order': deepcopy(co1), 'rotate': deepcopy(cr1)}, {'order': deepcopy(co2), 'rotate': deepcopy(cr2)}
            offsprings[x] = {'order': co1, 'rotate': cr1,"custs_index":custs_index}
            offsprings[x + 1] = {'order': co2, 'rotate': cr2,"custs_index":custs_index}    
        return offsprings

    def mutate(self, offsprings):
        """
        Performs mutation on the offspring population to introduce variability.
        """
        for child in offsprings.values():
            order = child['order']  
            rotate = child['rotate'] 
            # First level of mutation: Order Inversion Mutation
            if random.uniform(0, 1) <= self.pm1:
                i = random.randint(1, int(len(order) / 2) + 1)  
                j = random.randint(i + 1, int(len(order) - 1))  
                order[i:j + 1] = order[j:i - 1:-1]  
                rotate[i:j + 1] = rotate[j:i - 1:-1]

            # Second level of mutation: Rotation Mutation
            # for i in range(len(rotate)):
            #     if random.uniform(0, 1) <= self.pm2:
            #         rotate[i] = random.randint(0, self.rotation - 1)
        
        return offsprings

    def merge_populations(self, offsprings):
        """
        Merges the current population with the offsprings.
        """
        combined_population = deepcopy(self.population)  
        key = len(combined_population)  
        for _, value in offsprings.items():
            combined_population[key] = value  
            key += 1
        return combined_population
    
    def select_survivors(self, offsprings):
        """
        Selects survivors for the next generation based on NSGA-II sorting and crowding distance.
        """

        offsprings, _ = self.evaluate(offsprings)
        combined_population = self.merge_populations(offsprings)
        fronts = self.non_dominated_sort(combined_population)
        for front in fronts:
            self.calculate_crowding_distance(combined_population, front)

        self.population = self.select_based_on_nsga2(combined_population)

    def non_dominated_sort(self, combined_population):
        """
        Performs non-dominated sorting on the combined population to identify fronts.
        Returns:
            list: A list of fronts, where each front is a list of individual keys in that front.
        """
        fronts = [[]]
        for p_key in combined_population.keys():
            p = combined_population[p_key]
            p['dominated'] = []
            p['dom_count'] = 0
            for q_key in combined_population.keys():
                q = combined_population[q_key]
                if self.dominates(p['fitness'], q['fitness']):
                    p['dominated'].append(q_key)
                elif self.dominates(q['fitness'], p['fitness']):
                    p['dom_count'] += 1
            if p['dom_count'] == 0:
                p['Rank'] = 1
                fronts[0].append(p_key)
        
        i = 0
        while fronts[i]:
            next_front = []
            for p_key in fronts[i]:
                p = combined_population[p_key]
                for q_key in p['dominated']:
                    q = combined_population[q_key]
                    q['dom_count'] -= 1
                    if q['dom_count'] == 0:
                        q['Rank'] = i + 2
                        next_front.append(q_key)
            i += 1
            fronts.append(next_front)
        return fronts[:-1]  

    def calculate_crowding_distance(self, combined_population, front):
        """
        Calculates the crowding distance for each individual within a front.
        """
        for p_key in front:
            combined_population[p_key]['crowding_distance'] = 0
        for i in range(len(combined_population[next(iter(front))]['fitness'])):
            # Sort the front based on each objective's value
            front.sort(key=lambda x: combined_population[x]['fitness'][i])
            combined_population[front[0]]['crowding_distance'] = float('inf')
            combined_population[front[-1]]['crowding_distance'] = float('inf')
            for j in range(1, len(front) - 1):
                distance = combined_population[front[j + 1]]['fitness'][i] - combined_population[front[j - 1]]['fitness'][i]
                combined_population[front[j]]['crowding_distance'] += distance

    def select_based_on_nsga2(self, combined_population):
        """
        Selects individuals for the next generation based on their rank and crowding distance.
        """
        new_population = {}
        current_size = 0
        i=1
        while len(new_population) < self.population_size:
            group = [ind for ind in combined_population.values() if ind['Rank'] == i]
            if len(group) <= self.population_size - len(new_population):
                j = 0
                for index in range(len(new_population), len(new_population)+len(group)):
                    new_population[index] = group[j]
                    j += 1
            else:
                group = sorted(group, key=lambda x: x['crowding_distance'], reverse=True)
                j = 0
                for index in range(len(new_population), self.population_size):
                    new_population[index] = group[j]
                    j += 1
            i += 1
        return new_population
    
    def dominates(self, individual1, individual2):
        """
        Determines if one individual dominates another based on fitness values.
        Returns:
            bool: True if `individual1` dominates `individual2`, False otherwise.
        """
        better_in_all = all(m >= n for m, n in zip(individual1, individual2))
        better_in_at_least_one = any(m > n for m, n in zip(individual1, individual2))
        return better_in_all and better_in_at_least_one
     
    def calc_average_fitness(self, individuals):
        fitness_sum = [0.0, 0.0, 0.0]
        count = 0
        for key, value in individuals.items():
            if value['Rank'] == 1:
                count += 1
                fitness_sum[0] += value['fitness'][0]
                fitness_sum[1] += value['fitness'][1]
                fitness_sum[2] += value['fitness'][2]
        averaged = [sum_value / count if count > 0 else 0 for sum_value in fitness_sum]
        self.avg_fitness.append(averaged)
    
    def save_ga_results(self):
        try:
            # Create a GAComputationResult instance
            p_ind = 0
            current_datetime = datetime.now()
            file_name = f'report_{current_datetime.strftime("%Y-%m-%d_%H-%M-%S")}.json'
            for key, value in self.population.items():
                if value['Rank'] == 1 :#or value['Rank'] == 2:
                # print(p_ind,key)
                    collect_data(self.result, value, p_ind, key)
            computation_result = GAResult(file_name = file_name,result_json=self.result)

            # Save the instance to the database
            computation_result.save()

            print("GAComputationResult saved successfully!")
            computation_complete(flag=True)#flag=True
            spinFlag(flag=False)
            # queryset = Computation.objects.filter(is_fetched=False).order_by('started_at')
        

            # sorted_queryset = list(queryset)

            # # Make sure there are items in the sorted_queryset
            # if sorted_queryset:
                
            #     sorted_queryset[0].status = True
            #     sorted_queryset[0].is_fetched = True
            #     sorted_queryset[0].save()
            #     print(queryset)
            # else:
            #     print("No items in the sorted queryset")

        except Exception as e:
            print("Error:", e)

    def optimize(self):

        timing_record = {}
        timing_record[0] = {"start_time": time.time(),
                                    "end_time": None}
        self.population, _ = self.evaluate(self.population)
        fronts = self.non_dominated_sort(self.population)
        for front in fronts:
            self.calculate_crowding_distance(self.population, front)

        timing_record[0]["end_time"] = time.time()
        elapsed_time = timing_record[0]["end_time"] - \
                timing_record[0]["start_time"]
        timing_record[0]["elapsed_time"] = round(elapsed_time/60, 2)
        for gen in range(self.generations):
            print(f"Running current Generations.....{gen}")
            timing_record[gen+1] = {"start_time": time.time(),
                                      "end_time": None}
            parents = self.select_parents()
            offsprings = self.recombine(parents)
            offsprings = self.mutate(offsprings)
            self.select_survivors(offsprings)
            timing_record[gen+1]["end_time"] = time.time()
            elapsed_time = timing_record[gen]["end_time"] - \
                    timing_record[gen]["start_time"]
            timing_record[gen+1]["elapsed_time"] = round(elapsed_time/60, 2)
            pprint(timing_record)
            self.calc_average_fitness(self.population)

        self.save_ga_results()
        # self.population.clear()

    