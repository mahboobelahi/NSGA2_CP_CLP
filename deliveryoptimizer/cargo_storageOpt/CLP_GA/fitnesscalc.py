import copy
from operator import itemgetter
from copy import deepcopy
from pprint import pprint
from .helper import *
import sys

sys.setrecursionlimit(10**6)

def fitnessFunction(population, CONT, boxes_objs, total_value, support_ratio=0.55):
    """
    This function uses the S-DBLF algorithm to pack the boxes in the container and calculates the utilization space, the
    number of boxes packed and the total value of the boxes packed onto the container as the fitness values
    :param population: A dictionary of individuals, with order, rotate and values for each box
    :param truck_dimension: The [l, w, h] of the container
    :param boxes: A dictionary of the box number as the key and a list of [l, w, h, vol, value] of the boxes as values
    :return: The population dictionary adn list of fitness values for every individual
    """
    
    L, W, H = CONT.get_dimension()
    ft = {}

    
    for key, individual in population.items():
        boxes = []
        removed_PP = []
        removed_PPs = []
        dict_pp={}
        items =[]
        items_not_stackable = []
        PP = [[0,0,0]]
        tallest_box_height = 0
        custs_index = deepcopy(individual['custs_index'])
        # custs_index["rotatiob_varients"] = {}

        print(f"processing key.....{key}---:{len(PP)}")
        
        items = [(copy.deepcopy(boxes_objs)[box_number], r)
                 for box_number, r in zip(individual['order'], individual['rotate'])]

        for i in range(len(items)):
            bx, r = items[i]
            if bx.stackable:
                bx.rotation_type = r
                boxes.append(bx)
            else:
                prob = random.random()
                
                if prob <= 1:
                    bx.rotation_type = 0
                else: 
                    bx.rotation_type = 1
                boxes.append(bx)
                items_not_stackable.append(bx)

        if items_not_stackable:
            items_not_stackable.sort(key=lambda x: ranking_key(x))
            tallest_box = max(items_not_stackable, key=lambda box: box.height)
            tallest_box_height = tallest_box.height

        boxes.sort(key=lambda x: ranking_key(x))

        for id in custs_index.keys():
            # Filter boxes based on id and count dimensions directly
            filtered_boxes = [tuple(bx.get_dimension()) for bx in boxes if bx.name == id]

            # Initialize 'rotation_varients' as an empty dictionary if not already present
            rotation_varients = custs_index[id].setdefault("rotation_varients", {})

            # Count each dimension tuple and update rotation_varients dictionary
            for box_dim in filtered_boxes:
                rotation_varients[box_dim] = rotation_varients.get(box_dim, 0) + 1

        # boxes.extend(items_not_stackable)
        # for bx in boxes:
        #     print(bx.get_item_info())
        cID = boxes[0].name

        for box in boxes[:]:#, r
            l, w, h = box.get_dimension()
            if cID != box.name:
                cID = box.name
            for pos in PP:  
                is_overlap = []
                temp_pp = []
                area = 0
                stackable = False
                if box.stackable == False:
                    tallest_box_height = 0
                elif len(items_not_stackable) == 0:
                    tallest_box_height = 0
                if (L < pos[0]+l or W < pos[1]+w or H-tallest_box_height < pos[2]+h):
                    continue

                if pos[2] == 0 and box.stackable:
                    stackable = True
                    area = 1
                    box.set_onBase(True)
                    box.set_position(pos[:])
                    box.set_allvertices(pos+box.get_dimension())
    #    elif fit_box.sec_pps:
    #                         sec_pp = next([p for p in fit_box.sec_pps], None)
    #                         if(sec_pp == new_box_vertices["BBL"]) and\
    #                         check_overlap == False:
                    for fit_item in CONT.fit_items:
                        fit_box = fit_item.get_position()+fit_item.get_dimension()
                        new_box = pos+box.get_dimension()
                        fit_item.set_allvertices(fit_item.get_position()+fit_item.get_dimension())
                        box.set_allvertices(pos+box.get_dimension())
                        fit_box_vertices = fit_item.get_allVertices()
                        new_box_vertices = box.get_allVertices()
                        check_overlap = intersect(fit_box, new_box)
                        is_overlap.append(check_overlap)
                        
                        if (fit_box_vertices["BBR"] == new_box_vertices["BBL"]) and\
                            check_overlap == False:
                            if box not in fit_item.besideR:
                                    fit_item.besideR.append(box)
                            if fit_item not in box.besideL:
                                box.besideL.append(fit_item)

                        if (fit_box_vertices["FBL"] == new_box_vertices["BBL"]) and\
                            check_overlap == False:
                            if box not in fit_item.front:
                                fit_item.front.append(box)
                            if fit_item not in box.back:
                                box.back.append(fit_item)
                        if check_overlap:
                            break
                else:
                    # if pos[2] >= tallest_box_height:
                    #     box = items_not_stackable.pop(0)
                    area =0
                    stackable = False
                    for fit_item in CONT.fit_items:
        
                        fit_box = fit_item.get_position()+fit_item.get_dimension()
                        new_box = pos+box.get_dimension()
                        fit_item.set_allvertices(fit_item.get_position()+fit_item.get_dimension())
                        box.set_allvertices(pos+box.get_dimension())
                        fit_box_vertices = fit_item.get_allVertices()
                        new_box_vertices = box.get_allVertices()
                        check_overlap = intersect(fit_box, new_box)
                        is_overlap.append(check_overlap)
                        
                        if calculate_overlap_area(fit_box, new_box) !=0 and\
                            check_overlap == False:
                            area += calculate_overlap_area(fit_box, new_box)
                            if fit_item not in box.under:
                                box.under.append(fit_item)
                            
                            if fit_item.stackable == True:
                                stackable = True
                            elif fit_item.stackable == False and box.stackable == False:
                                stackable = True
                                
                            if box not in fit_item.top:
                                fit_item.top.append(box)                            
                        if box.name == 'C-2' and box.stackable ==False:
                            if fit_item.stackable == False:
                                if (fit_box_vertices["BTL"] == new_box_vertices["BBL"]):
                                    pass#print()
                        if (fit_box_vertices["BTL"] == new_box_vertices["BBL"]) and\
                                check_overlap == False:
                            if fit_item not in box.under:
                                box.under.append(fit_item)
                            
                            if fit_item.stackable == True:
                                    stackable = True
                            elif fit_item.stackable == False and box.stackable == False:
                                    stackable = True
                                
                            if box not in fit_item.top:
                                fit_item.top.append(box)
##################################################################################
                        elif fit_item.sec_pps and area >= support_ratio:
                            sec_pp = next((p for p in fit_item.sec_pps if p == new_box_vertices["BBL"]), None)
                            if(sec_pp == new_box_vertices["BBL"]) and check_overlap == False:
                                if fit_item not in box.under:
                                    box.under.append(fit_item)
                                    print(f"[xxx] {area}--Sec-Placed--{sec_pp}--{new_box_vertices['BBL']}")
                                if fit_item.stackable == True:
                                        stackable = True
                                elif fit_item.stackable == False and box.stackable == False:
                                        stackable = True
                                    
                                if box not in fit_item.top:
                                    fit_item.top.append(box)

        #######################################################################                            
                        if (fit_box_vertices["BBR"] == new_box_vertices["BBL"]) and\
                            check_overlap == False:
                            if box not in fit_item.besideR:
                                    fit_item.besideR.append(box)
                            if fit_item not in box.besideL:
                                box.besideL.append(fit_item)

                        if (fit_box_vertices["FBL"] == new_box_vertices["BBL"]) and\
                            check_overlap == False:
                            if box not in fit_item.front:
                                fit_item.front.append(box)
                            if fit_item not in box.back:
                                box.back.append(fit_item)
                        if check_overlap:
                            
                            clear_neighbors( box)
                            removed_PP.clear()
                            stackable = False
                            break
                        

                if True in is_overlap:
                    stackable = False
                    continue

                if area >= support_ratio and stackable:
                    fit = True
                else:
                    clear_neighbors(box)
                    stackable = False
                    removed_PP.clear()
                    continue
                if CONT.get_total_occupide_volume() + box.get_volume() > CONT.get_volume():
                    CONT.unfitted_items.append(box)
                    fit = False
                
                if fit:
                    if box in items_not_stackable:
                        items_not_stackable.remove(box)
                    if pos[2] == 0:
                        box.set_onBase(True)
                    box.set_position(pos)       
                    box.is_fit = True
                    under_boxes = get_under_boxes(box)
                    if under_boxes:
                        for ubx in under_boxes:
                            if box.get_allVertices()["BBR"][1] > ubx.get_allVertices()["BTR"][1]:
                                if ubx.get_allVertices()["BBR"] in PP:
                                    if ubx.get_allVertices()["BBR"][2]!=0: PP.remove(ubx.get_allVertices()["BBR"])
                                    if tuple(ubx.get_allVertices()["BBR"]) in dict_pp:
                                        dict_pp.pop(tuple(ubx.get_allVertices()["BBR"]))
                                
                    if pos in PP: 
                        PP.remove(pos)
                        removed_PPs.append(pos)
                        if tuple(pos) in dict_pp:
                                dict_pp.pop(tuple(pos))
                    
                    CONT.fit_items.append(box)
                    
                    MPH_x,MPH_y,pps = get_mphX_mphY(box,CONT,PP,dict_pp,pos,removed_PPs)
                    [is_point_inside_box(pp, box,PP,dict_pp) for pp in reversed(PP)]
                    
                    
                    removed_PP.clear()
                    
                    PP = sorted(PP, key=lambda point: (point[0], point[2], point[1]), reverse=False)
                    # boxes.remove(box)
                break

            if box.is_fit == False:
                
                if box not in CONT.unfitted_items:
                    CONT.unfitted_items.append(box)
                    box.position.clear()
                    # boxes.remove(box)
                # if len(boxes) == 0 and len(items_not_stackable) !=0:
                #     boxes=items_not_stackable
                    

        fitness = [round((CONT.get_total_occupide_volume() / CONT.get_volume() * 100), 2),
                    round((len(CONT.fit_items) / len(CONT.items) * 100), 2),
                    round((CONT.get_total_fitted_item_value() / total_value * 100), 2)]
        ft[key] = fitness
        population[key]['fitness'] = deepcopy(fitness)
        population[key]['result'] = copy.deepcopy(CONT.fit_items)
        population[key]['un_fit_items'] = copy.deepcopy(CONT.unfitted_items)
        CONT.fit_items.clear()
        CONT.unfitted_items.clear()
        removed_PPs.clear()
        custs_index.clear()
        print(f"End processing key.....{key}---:{len(PP)}")
    return population, ft