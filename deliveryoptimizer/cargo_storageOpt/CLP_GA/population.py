import random
from copy import deepcopy
from pprint import pprint
from .helper import assign_rotation

def generate_pop(box_params, count, ROTATIONS, custs):
    population = {}
    if count > 5:
        x = 5
    else:
        x = count

    for i in range(0, 6):
        if i == 4:
            sorted_box = dict(
                sorted(box_params.items(),
                       key=lambda xx: xx[1].get_volume(),
                       reverse=True))
        elif i ==5:
            sorted_box = dict(
                sorted(box_params.items(),
                       key=lambda xx: xx[1].length*xx[1].width,
                       reverse=True))
        else:
            sorted_box = dict(
                sorted(box_params.items(),
                       key=lambda xx: getattr(
                           xx[1], ['length', 'width', 'height', 'value'][i]),
                       reverse=True))
        x=sorted_box
        population[i] = {"order": list(sorted_box.keys()),
                         "rotate": [assign_rotation(box_params.get(r).s_rotate) for r in sorted_box.keys()],
                         }

    keys = list(box_params.keys())
    for i in range(6, count):
        random.shuffle(keys)
        population[i] = {"order": deepcopy(keys),
                         "rotate": [assign_rotation(box_params.get(r).s_rotate) for r in keys]}

    sorted_pop = {}
    for k, v in population.items():
        order_indices = v["order"]
        rotate = v["rotate"]
        temp_box = deepcopy(box_params)
        [setattr(temp_box[idx], 'rotation_type', rotate[i]) for i, idx in enumerate(order_indices)]

        temp_sort_box = sorted(temp_box.values(), key=lambda bx: bx.name)
        
        sorted_order = [temp_sort_box.index(box) for box in temp_sort_box]
        sorted_rotate = [box.rotation_type for box in temp_sort_box]

        sorted_pop[k] = {"order": sorted_order, "rotate": sorted_rotate, 'custs_index': custs}
    
    return sorted_pop



