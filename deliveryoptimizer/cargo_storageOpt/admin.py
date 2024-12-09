from django.contrib import admin
from .models.container import Container
from .models.OrderForm import FormData
# from .models.computation import Computation
from .models.GAComputationResults import GAResult
from django.utils.safestring import mark_safe
import json

admin.site.register(Container)



class FormDataAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'container', 'order_fetched', 'supportRatio', 'stackable', 
        'customerId', 'length', 'width', 'height', 'origin', 'destination', 
        'orderPriority', 'itemWeight', 'rotation', 'quantity', 'itemValue', 
        'boxTag', 'additional_information', 'formatted_system_time', 
        'formatted_order_receive_time', 'formatted_order_delivery_time'
    )
    readonly_fields = ('system_time', 'order_receive_time', 'order_delivery_time')

    def get_time_display(self, obj, field_name):
        """
        Generic function to get formatted time display.
        
        Args:
            obj: The instance of the model.
            field_name: The name of the field to retrieve.

        Returns:
            Formatted string representation of the time, or None if the field is missing.
        """
        value = getattr(obj, field_name, None)
        return value.strftime('%Y-%m-%d %H:%M:%S') if value else None

    # Specific methods for each field using the generic function
    def formatted_system_time(self, obj):
        return self.get_time_display(obj, 'system_time')
    
    def formatted_order_receive_time(self, obj):
        return self.get_time_display(obj, 'order_receive_time')

    def formatted_order_delivery_time(self, obj):
        return self.get_time_display(obj, 'order_delivery_time')

    # Optional: Add descriptions for admin display
    formatted_system_time.short_description = "System Time"
    formatted_order_receive_time.short_description = "Order Received Time"
    formatted_order_delivery_time.short_description = "Order Delivery Time"



class GaResultsAdmin(admin.ModelAdmin):
    pass
    readonly_fields = ('pretty_ga_results',)  # Make this field read-only in the admin

    def pretty_ga_results(self, obj):
        # Get JSON field data and format it with indentation
        try:
            formatted_json = json.dumps(obj.result_json, indent=4, sort_keys=False)
            return mark_safe(f'<pre>{formatted_json}</pre>')
        except (TypeError, json.JSONDecodeError):
            return "Invalid JSON"

    pretty_ga_results.short_description = "Formatted GA Results"

admin.site.register(FormData, FormDataAdmin)
# admin.site.register(Computation)
admin.site.register(GAResult,GaResultsAdmin)


