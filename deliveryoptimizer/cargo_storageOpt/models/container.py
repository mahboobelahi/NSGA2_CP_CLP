from django.db import models


class Container(models.Model):
    class Meta:
        ordering = ['sort_id']

    OPENING_CHOICES = [
        ('T', 'Open to Top'),
        ('B', 'Open to Back'),
        ('S', 'Open to Side'),
    ]
    id = models.AutoField(primary_key=True)
    opening_type = models.CharField(max_length=1, choices=OPENING_CHOICES, default='B')
    cont_ID = models.CharField(max_length=10, default= None,blank=True)
    sort_id = models.IntegerField(default=0)
    tare_weight = models.IntegerField()
    payload = models.IntegerField()
    external_length = models.FloatField()
    external_width = models.FloatField()
    external_height = models.FloatField()
    internal_length = models.FloatField()
    internal_width = models.FloatField()
    internal_height = models.FloatField()
    
    
    
    
    def get_PK(self):
        return self.id
    def get_cont_name(self):

        return f"ISO-{self.cont_ID}"
    
    def get_info(self):
        data = {
            'name': f"ISO-{self.cont_ID}ft",
            'external_dimention': self.get_external_dimensions(),
            'internal_dimention': self.get_internal_dimensions(),
            'container_opening': self.get_opening_type_display(),
            "payload": self.payload,
            "tare_weight": self.tare_weight
        }

        return data
    
    def get_opening_type_display(self):
        for choice in self.OPENING_CHOICES:
            if choice[0] == self.opening_type:
                return choice[1]
        return "Unknown"
    
    def get_external_dimensions(self):
        dimensions = {
            "m": [self.external_length, self.external_width, self.external_height],
            "cm": [round(self.external_length * 100, 2), round(self.external_width * 100, 2),
                   round(self.external_height * 100, 2)],
            "ft": [round(self.external_length * 3.28084, 2), round(self.external_width * 3.28084, 2),
                   round(self.external_height * 3.28084, 2)]
        }
        return dimensions
    def get_internal_dimensions(self):
        dimensions = {
            "m": [self.internal_length, self.internal_width, self.internal_height],
            "cm": [round(self.internal_length * 100, 2), round(self.internal_width * 100, 2),
                   round(self.internal_height * 100, 2)],
            "ft": [round(self.internal_length * 3.28084, 2), round(self.internal_width * 3.28084, 2),
                   round(self.internal_height * 3.28084, 2)]
        }
        return dimensions

    def __str__(self):
        return f"Container {self.cont_ID}ft ,{self.opening_type} "
