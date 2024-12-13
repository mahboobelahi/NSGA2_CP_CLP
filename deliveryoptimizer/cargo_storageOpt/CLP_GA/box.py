import copy
from .rotation import RotationType
from .helper import *


class Item:
    def __init__(self, partno, name, LWH, orderPriority,origin,destination,s_rotate,stackable=True,weight=0, value=0, rotation=0):
        ''' '''
        self.partno = partno
        self.name = name
        # self.typeof = typeof
        self.width = LWH[1]
        self.height = LWH[2]
        self.length = LWH[0]
        self.position = []
        self.rotation_type = rotation
        self.s_rotate = s_rotate
        self.weight = weight
        self.stackable = stackable 
        self.orderPriority = orderPriority
        self.origin = origin
        self.destination = destination
        self.order_receive_date = None
        self.order_delivery_date = None
        self.value = value
        self.is_projection_needed = False
        self.is_fit = False
        self.under = []
        self.top = []
        self.besideR = []
        self.besideL = []
        self.front = []
        self.back = []
        self.onBase = False
        self.pps = []
        self.sec_pps = []
        self.allVertices = {}

    def get_item_info(self):

        return{
            "partno":self.partno,"name":self.name,"stackable":self.stackable,"orderPriority":self.orderPriority,
            "effect_dim":self.get_dimension(),"rotation_type":self.rotation_type,"S_rotation":self.s_rotate
            # "length":self.length,'width':self.width,
            # "height":self.height,"effect_dim":self.get_dimension()
        }
    def get_LWH_R(self):
        return [self.length,self.width,self.height,self.rotation_type]
    
    def item_passport(self):
        return f"{self.get_id()},{self.get_LWH_R()},{self.get_dimension()},{self.get_volume()}"

    def get_dimension(self):
        rotation_map = {
            RotationType.RT_LWH: [self.length, self.width, self.height],
            RotationType.RT_WLH: [self.width, self.length, self.height],
            RotationType.RT_HWL: [self.height, self.width, self.length],
            RotationType.RT_WHL: [self.width, self.height, self.length],
            RotationType.RT_LHW: [self.length, self.height, self.width], #vertical 5
            RotationType.RT_HLW: [self.height, self.length, self.width] #vertical 3
        }

        return rotation_map.get(self.rotation_type, [self.length, self.width, self.height])

    def p_sort_key(self):
        s_key = {
                    0:2,
                    1:4,
                    2:6
                }
        return s_key.get(self.s_rotate)
    
    def get_id(self):
        return self.partno+self.name
    
    def get_plot_data(self):
        data = self.position+self.get_dimension()
        data.append(int(self.name.split("C-")[1]))
        data.append(self.partno)
        return data

    def get_under(self):
        return sorted(self.under,key=lambda bx:(bx[0].position[0],bx[0].position[1],bx[0].position[2]))#self.under

    def get_front(self):
        return sorted(self.front, key= lambda bx:(bx.position[0],bx.position[1],bx.position[2]))
    
    def get_back(self):
        return sorted(self.back,key=lambda bx:(bx.position[0],bx.position[1],bx.position[2]))

    def get_beside(self):
        return sorted(self.self.beside,key=lambda bx:(bx.position[0],bx.position[1],bx.position[2]))#self.beside

    def get_volume(self):
        return self.length*self.width*self.height

    def get_allVertices(self):
        return self.allVertices

    def get_pps(self):
        return self.pps
    
    def get_position(self):
            return self.position

    def add_under(self, item):
        self.under.append(item)

    def add_front(self, item):
        self.front.append(item)

    def add_beside(self, item):
        self.beside.append(item)

    def set_onBase(self, flag):
        self.onBase = flag

    def set_pps(self, pps):
        self.pps = pps
    
    def set_position(self,pos):
        self.position = pos
    
    def set_allvertices(self,box):
        x, y, z, l, w, h = box
        vertices = {
        "FBL": [x+l, y, z],  # Front bottom left (pp)
        "FBR": [x + l, y+w, z],  # Front bottom right
        "FTL": [x+l, y, z+h],  # Front top left
        "FTR": [x+l , y+w, z+h],  # Front top right
        "BBL": [x, y, z],  # Back bottom left
        "BBR": [x, y+w, z],  # Back bottom right (pp)
        "BTL": [x, y , z + h],  # Back top left (pp)
        "BTR": [x , y + w, z + h]  # Back top right
    }
        self.allVertices = copy.deepcopy(vertices)#copy.deepcopy(get_vertices(vertices))
