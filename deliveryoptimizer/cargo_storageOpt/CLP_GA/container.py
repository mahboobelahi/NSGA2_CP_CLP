class Container:
    def __init__(self, name, LWH, max_weight):
        ''' '''
        self.name = name
        self.length = LWH[0]
        self.width = LWH[1]
        self.height = LWH[2]
        self.max_weight = max_weight
        self.items = []
        self.fit_items = []
        self.unfitted_items = []
        self.PP = [[0, 0, 0]]

    def string(self):

        return f"{self.name}, ({self.length,self.width, self.height}, max_weight({self.max_weight}),Vol({self.get_volume()})"

    def get_volume(self):
        ''' '''
        return round((self.width * self.height * self.length), 2)

    def get_total_weight(self):
        
        total_weight = 0
        for item in self.fit_items:
            total_weight += item.weight
        return round(total_weight, 2)
    
    def get_total_occupide_volume(self):
        
        total_volume = 0
        for item in self.fit_items:
            total_volume += item.get_volume()
        return round(total_volume, 2)
    
    def get_total_fitted_item_value(self):
        
        total_value = 0
        for item in self.fit_items:
            total_value += item.value
        return round(total_value, 2)
    
    def get_dimension(self):
        return [self.length, self.width, self.height]
