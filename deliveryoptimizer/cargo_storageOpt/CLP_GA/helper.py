import random,json,os
from datetime import datetime
from .configurations import*
from .box import Item
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync




# for socket
def computation_complete(flag=False):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "NSGA_flag_group",  # Group name
        {
            "type": "send_flag_message",
            "message": "Computation Completed!",
            "is_computing": flag
        }
    )

def spinFlag(flag=True):

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "Spin_flag_group",  # Group name
        {
            "type": "send_flag_message",
            "message": "Computation Completed!",
            "is_computing": flag
        }
    )

# for GA

import random

def assign_rotation(rotation_type):
    prob = random.random()
    
    if rotation_type == 2:
        # Divide [0, 1] into 2 equal parts
        return 0 if prob < 0.5 else 1
    
    elif rotation_type == 4:
        # Divide [0, 1] into 4 equal parts
        if prob < 0.25:
            return 0
        elif prob < 0.5:
            return 1
        elif prob < 0.75:
            return 2
        else:
            return 4#3
    
    elif rotation_type == 6:
        # Divide [0, 1] into 6 equal parts
        if prob < 1/6:
            return 0
        elif prob < 2/6:
            return 1
        elif prob < 3/6:
            return 2
        elif prob < 4/6:
            return 3
        elif prob < 5/6:
            return 4
        else:
            return 5
    
    else:
        # Default case for unsupported rotation_type
        return 0 if prob < 0.5 else 1

def set_box_range(custs, quantities, ord):
    # Sort orders by customer ID
    for item in sorted(ord, key=lambda x: x.get_fields().get("customerId")):
        box = item.get_fields()
        quantities.append(box.get("quantity"))

        # Construct customer and dimension keys
        customer_key = f"C-{box.get('customerId')}"
        dimensions_key = (box['length'], box['width'], box['height'])

        # Initialize or update quantity for each dimension
        if customer_key not in custs:
            custs[customer_key] = {dimensions_key: box.get("quantity")}
        else:
            if dimensions_key not in custs[customer_key]:
                    custs[customer_key][dimensions_key] = box.get("quantity")
            else:
                custs[customer_key][dimensions_key] = custs[customer_key].get(dimensions_key, 0) + box.get("quantity")

    # Compute start and stop indices for each customer
    start_index = 0
    for customer, dimensions in custs.items():
        total_quantity = sum(dimensions.values())  # Aggregate total quantity for the customer
        stop_index = start_index + total_quantity - 1
        custs[customer]['range'] = [start_index, stop_index]#{tuple(dimensions):[start_index, stop_index]}
        start_index = stop_index + 1  # Move start index for the next customer
    

def create_box_objects(ORDERS,CONT,box_params):
    tag = 1
    total_value = 0
    # print("ORDERS\n",ORDERS)
    for order in ORDERS:
        box= order.get_fields()
        # print("box\n",box)
        
        for i in range(box.get("quantity")):
            CONT.items.append(Item(
                    partno=f"{box.get('boxTag')}-{tag}", #f"{box.get("boxTag")}",#-{i+1}
                    name=f"C-{box.get('customerId')}",
                    stackable=box.get('stackable'),
                    weight=box.get('weight'),
                    orderPriority = box.get('orderPriority'),
                    origin = box.get('origin'),
                    destination = box.get('destination'),
                    LWH=[int(box.get("length")),int(box.get("width")),int(box.get("height"))],
                    rotation=config_dict["ROTATIONS"][box.get('rotation')],
                    s_rotate=config_dict["ROTATIONS"][box.get('rotation')],
                    value=int(box.get("itemValue"))
                ))
            total_value += int(box.get("itemValue"))
            tag+=1
    
    CONT.items = sorted(CONT.items,key=lambda x: ranking_key(x), reverse=False)
    # for i in CONT.items:
    #     print(i.s_rotate)
    for index in range(len(CONT.items)):
        box_params[index] = CONT.items[index]
        # pprint(CONT.items[index].get_item_info())
    return total_value


def ranking_key(box):
    id = box.name.split('-')[1]
    stackablility = box.stackable
    rotation_type = box.rotation_type
    itemPriority = box.orderPriority
    length, width, height = box.get_dimension()
    vol = length * width * height
    base_area = length * width
    max_dim = max(length, width)
    min_dim = min(length, width)
    
    # Determine primary sorting dimension based on length vs width
    primary_dimension = length if length > width else width
    secondary_dimension = width if length > width else length

    return (
        id,
        -stackablility,
        -itemPriority,
        -vol,
        -base_area,
        -length,-width#-primary_dimension,  # Primary sort dimension
        #-secondary_dimension,  # Secondary sort dimension if needed
        -height  # Sort by height last
    )
def rectIntersect(box1, box2, x, y):
    position, d1 = (box1[0:3], box1[3:6])
    position2, d2 = (box2[0:3], box2[3:6])

    cx1 = position[x] + d1[x]/2
    cy1 = position[y] + d1[y]/2
    cx2 = position2[x] + d2[x]/2
    cy2 = position2[y] + d2[y]/2

    ix = max(cx1, cx2) - min(cx1, cx2)
    iy = max(cy1, cy2) - min(cy1, cy2)

    return ix < (d1[x]+d2[x])/2 and iy < (d1[y]+d2[y])/2


def intersect(box1, box2):
    return (
        rectIntersect(box1, box2, 0, 1) and
        rectIntersect(box1, box2, 1, 2) and
        rectIntersect(box1, box2, 0, 2)
    )


def calculate_overlap_area(rect1, rect2):
    # print(rect1)
    if len(rect1)!=6 or len(rect2)!=6:
        return 0
    x1, y1, z1, l1, w1, h1 = rect1
    x2, y2, z2, l2, w2, h2 = rect2

    if z1+h1 == z2:
        # Calculate the coordinates of the intersection rectangle
        x_overlap = max(0, min(x1+l1, x2+l2) - max(x1, x2))
        y_overlap = max(0, min(y1+w1, y2+w2) - max(y1, y2))

        # Calculate the area of overlap
        overlap_area = x_overlap * y_overlap

        # Calculate the total area of the upper rectangle
        upper_area = l2 * w2

        # Calculate the support percentage
        support_percentage = overlap_area / upper_area

        return round(support_percentage, 2)
    else:
        return 0
def calculate_overlap_area_yz(rect1, rect2):
    x1, y1, z1, l1, w1, h1 = rect1
    x2, y2, z2, l2, w2, h2 = rect2

    # Calculate the coordinates of the intersection rectangle
    y_overlap = max(0, min(y1 + w1, y2 + w2) - max(y1, y2))
    z_overlap = max(0, min(z1 + h1, z2 + h2) - max(z1, z2))

    # Calculate the area of overlap
    overlap_area = y_overlap * z_overlap

    # Calculate the total area of the upper rectangle
    upper_area = w2 * h2

    # Calculate the support percentage
    support_percentage = overlap_area / upper_area

    return round(support_percentage, 2)
def get_mphX_mphY(box,CONT,PP,dict_pp,pos,removed_PPs):
    MPH_x,MPH_y = 0,0
    temp_pp = []
    L,W,H = CONT.get_dimension()
    x,y,z = box.position[0:3]
    l,w,h = box.get_dimension()
    
    # if box.stackable == False:
    #     PP.append([x+l,y,z])
    #     PP.append([x,y+w,z])
    #     return (MPH_x,MPH_y,temp_pp)


    if z==0:
        if x+l < L and [x+l,y,MPH_x] not in PP:
            PP.append([x+l,y,MPH_x])
            box.pps.append([x+l,y,MPH_x])
            if tuple([x+l,y,MPH_x]) not in dict_pp:
                dict_pp[tuple([x+l,y,MPH_x])] = box
        if y+w < W and [x,y+w,MPH_y] not in PP:
            PP.append([x,y+w,MPH_y])
            box.pps.append([x,y+w,MPH_y])
            if tuple([x,y+w,MPH_y]) not in dict_pp:
                dict_pp[tuple([x,y+w,MPH_y])] = box

    else:

        for box_j in reversed(CONT.fit_items):
            xj, yj, zj = box_j.position[0:3]
            lj, wj, hj = box_j.get_dimension()
            
            if xj < x + l and yj < y + w and\
                  xj + lj > x + l and\
                      yj + wj > y:
                if zj + hj <= z and zj + hj > MPH_x:
                    MPH_x = zj + hj
            
            if xj < x + l and yj < y + w and\
                      xj + lj > x and\
                          yj + wj > y + w:#=
                if zj + hj <= z and zj + hj > MPH_y:
                    MPH_y = zj + hj
            
            
            if MPH_x == z and MPH_y == z:
                break
               
    if x+l <= L and [x+l,y,MPH_x] not in PP:
        temp_pp.append([x+l,y,MPH_x])

    if y+w <= W and [x,y+w,MPH_y] not in PP and [x,y+w,MPH_y] not in removed_PPs:
        temp_pp.append([x,y+w,MPH_y])

    if z+h <= H and [x,y,z+h] not in PP :
        temp_pp.append([x,y,z+h])

    if len(temp_pp):PP.extend(temp_pp)
    for p in temp_pp:
        box.pps.append(p)
        if tuple(p) not in dict_pp:
            dict_pp[tuple(p)] = box

    return (MPH_x,MPH_y,temp_pp)


def is_point_inside_box(point, box, PP, dict_pp):
    # Get the vertices of the cuboid
    vertices = box.get_allVertices()

    # Find the min and max coordinates along each axis
    min_x = min(vertex[0] for vertex in vertices.values())
    max_x = max(vertex[0] for vertex in vertices.values())
    min_y = min(vertex[1] for vertex in vertices.values())
    max_y = max(vertex[1] for vertex in vertices.values())
    min_z = min(vertex[2] for vertex in vertices.values())
    max_z = max(vertex[2] for vertex in vertices.values())

    # Extract point coordinates
    x, y, z = point
    aux_bx = dict_pp.get(tuple(point))
    # Check if the point is strictly inside the box (not on the boundaries)
    if (min_x <= x <= max_x) and (min_y <= y <= max_y) and (min_z <= z <= max_z):
        if point != vertices["FBL"] and point != vertices["BBR"] and point != vertices["BTL"]:
            # Modify the point's z-coordinate
            if aux_bx:
                ver = aux_bx.get_allVertices()
                if point != ver["FBL"] and point != ver["BBR"] and point != ver["BTL"]:
                    PP.append([x, y, max_z])
                    if tuple([x, y, max_z]) not in dict_pp:
                        dict_pp[tuple([x, y, max_z])] = box
                        if [x, y, max_z] in box.sec_pps:
                            box.sec_pps.remove([x, y, max_z])
                        else:
                            box.sec_pps.append([x, y, max_z])
            if point in PP:
                PP.remove(point)
           
def clear_neighbors( box):

    if box.under:
        # * under: [[box_obj,area]]
        for b in box.under:
            if box in b.top:
                b.top.remove(box)
    if box.besideL:
        if box in box.besideL[0].besideR:
            box.besideL[0].besideR.remove(box)

    if box.besideR:
        if box in box.besideR[0].besideL:
            box.besideR[0].besideL.remove(box)
    if box.back:
        box_back = box.back[0]
        box_front =None
        if box_back.front:
           box_front = box_back.front[0]

        if box_back in box.back:
            box.back.remove(box_back)
        if box_front in box_back.front:
            box_back.front.remove(box_front)

    box.besideR.clear()
    box.besideL.clear()
    box.under.clear()
    box.top.clear()
    box.front.clear()
    box.back.clear()


def get_under_boxes(boxes):
    """
    Iteratively get all under boxes starting from the given box.
    """
    under_boxes = []
    stack = list(boxes.under)  
    visited = set()  # Set to keep track of visited boxes

    while stack:
        b = stack.pop(0)  # Get the next box to check from the stack

        if b not in visited:
            # Append the current box to the under_boxes list
            under_boxes.append(b)
            visited.add(b)

            # If the current box has an 'under' list, add to the stack
            if b.under:
                for box in b.under:
                    if box not in visited:
                        stack.append(box)

    return under_boxes


def get_top_boxes(boxes):
    """
    Iteratively get all top boxes starting from the given box.
    """
    top_boxes = []

    # Check if the given box or boxes have any 'top' boxes before proceeding
    if boxes.top:  # Assuming `boxes` is a single box
        stack = list(boxes.top)  # Initialize the stack with the boxes above the given box

        while stack:
            b = stack.pop()  # Get the next box to check from the stack

            # Append the current box to the top_boxes list
            top_boxes.append(b)

            # If the current box has a 'top' list and is not in its own 'top' list, add to the stack
            if b.top and b not in b.top:
                stack.extend(b.top)

    return top_boxes



def collect_data(result, value, p_ind, key):
    res = value['result']

    # If 'layout' key doesn't exist in result, initialize it as an empty dictionary
    if 'layouts' not in result:
        result['layouts'] = {}

    item_passport = [
        {
            "id": item.get_id(),
            "customer_belonging": item.name,
            "volume": item.get_volume(),
            "weight": item.weight,
            "material": "",
            "rotation_type": item.rotation_type,
            "dimension_before_rotation": item.get_LWH_R()[0:3],
            "dimension_after_rotation": item.get_dimension()[0:3],
            "plot_data": item.get_plot_data(),
            "on_base": item.onBase,
            "stackable": item.stackable,
            "neighboring_items": {
                "left": [neighbor.get_id() for neighbor in item.besideL if neighbor],
                "right": [neighbor.get_id() for neighbor in item.besideR if neighbor],
                "top": [neighbor.get_id() for neighbor in item.top if neighbor],#[neighbor.get_id(), neighbor][0][1]
                "under": [neighbor.get_id() for neighbor in item.under if neighbor],#[0][1]
                "back": [neighbor.get_id() for neighbor in item.back if neighbor],
                "front": [neighbor.get_id() for neighbor in item.front if neighbor],
            }
        } for item in res]

    # Check if the key already exists in result["layout"]
    layout_key = f"{p_ind}{key}"
    item_passport_sorted =item_passport
    # item_passport_sorted = sorted(item_passport,
    #             key=lambda item: (item["plot_data"][0], item["plot_data"][2], item["plot_data"][1]))
    if layout_key not in result["layouts"]:
        result["layouts"][layout_key] = {
            "solution_fitness": value["fitness"],
            "packed_items": len(res),
            "unpacked_items": {
                "quantity": len(value["un_fit_items"]),
                "stackable_item_ids": [i.get_id() for i in value["un_fit_items"] if i.stackable],
                "un_stackable_item_ids": [i.get_id() for i in value["un_fit_items"] if i.stackable ==False]
            },
            "num": len(value['result']),
            "item_passport": item_passport_sorted,
        }
    else:
        # Update existing entry with new values
        result["layouts"][layout_key].update({
            "solution_fitness": value["fitness"],
            "packed_items": len(res),
            "unpacked_items": {
                "quantity": len(value["un_fit_items"]),
                "stackable_item_ids": [i.get_id() for i in value["un_fit_items"] if i.stackable],
                "un_stackable_item_ids": [i.get_id() for i in value["un_fit_items"] if i.stackable ==False]
            },
            "num": len(value['result']),
            "item_passport":item_passport_sorted,
        })

    return result



def generate_report(result):
    # Your existing function code here
    
    # Get the current date and time
    current_datetime = datetime.now()

    # Format the current date and time as a string for the folder name
    current_folder = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

    # Define the path to the destination directory
    destination_dir = os.path.join('cargo_storageOpt', 'CLP_GA', 'Reports', current_folder)

    # Create the destination directory if it doesn't exist
    os.makedirs(destination_dir, exist_ok=True)

    # Define the file name for the report
    file_name = f"report_{current_folder}.json"

    # Construct the full path to the destination file
    destination_file = os.path.join(destination_dir, file_name)

    # Write the report data to the destination file
    with open(destination_file, 'w') as f:
        json.dump(result, f)

    return destination_file