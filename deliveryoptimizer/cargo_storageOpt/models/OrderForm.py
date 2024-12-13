from django.db import models


class FormData(models.Model):
    id = models.AutoField(primary_key=True)
    container = models.CharField(max_length=255, default='20ft-B')
    length = models.FloatField()
    height = models.FloatField()
    width = models.FloatField()
    itemWeight = models.FloatField(default=1)
    rotation = models.IntegerField()
    quantity = models.PositiveIntegerField()
    customerId = models.PositiveIntegerField()
    itemValue = models.PositiveIntegerField()
    boxTag = models.CharField(max_length=255)
    stackable = models.BooleanField(default=True)  # Default value set to False
    additional_information = models.JSONField()
    system_time = models.DateTimeField(auto_now_add=True)
    order_receive_time = models.DateTimeField(auto_now_add=True)
    order_delivery_time = models.DateTimeField(auto_now_add=True)
    order_fetched = models.BooleanField(default=False)  # Indicates whether the order is fetched or not
    

    # New fields
    orderPriority = models.IntegerField(default=1)
    origin = models.CharField(max_length=255,default="unknown")
    destination = models.CharField(max_length=255,default="unknown")
    supportRatio = models.FloatField(default=0.55)

    def __str__(self):
        return f"({self.id},{self.length},{self.width},{self.height},{self.itemWeight},{self.container})"
        
    def formatted_timestamp(self, obj):
        return obj.strftime('%Y-%m-%d_%H-%M-%S')

    def get_fields(self):
        return {
            "id": self.id,
            'containerId': self.container,
            'length': self.length,
            'height': self.height,
            'width': self.width,
            'rotation': self.rotation,
            'quantity': self.quantity,
            'customerId': self.customerId,
            'itemValue': self.itemValue,
            'boxTag': self.boxTag,
            'stackable': self.stackable,
            'additional_information': self.additional_information,
            'system_time': self.formatted_timestamp(self.system_time),
            'order_delivery_time': self.formatted_timestamp(self.order_delivery_time),
            'order_receive_time' : self.formatted_timestamp(self.order_receive_time),
            'order_fetched': self.order_fetched,
            # New fields
            'orderPriority': self.orderPriority,
            'origin': self.origin,
            'destination': self.destination,
            'supportRatio': self.supportRatio,
        }
