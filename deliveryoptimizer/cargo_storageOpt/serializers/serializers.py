from rest_framework import serializers
from ..models.OrderForm import FormData
import json

class FormDataSerializer(serializers.ModelSerializer):
    itemWeight = serializers.FloatField(min_value=1)  # Add min_value constraint if weight cannot be negative
    rotation = serializers.IntegerField()  # Change to FloatField to handle string inputs
    customerId = serializers.IntegerField(allow_null=False, required=False, min_value=1)  # Handle empty string inputs
    orderPriority = serializers.IntegerField(allow_null=False, required=False, min_value=1)
    supportRatio = serializers.FloatField(allow_null=False, required=False, min_value=0.55)
    itemValue = serializers.IntegerField(default=0)  # Use default value instead of allow_null=False
    additional_information = serializers.JSONField()

    class Meta:
        model = FormData
        fields = '__all__'

    def to_internal_value(self, data):
        # Override to_internal_value to parse additional_information from a string to JSON
        if 'additionalInfo' in data:
            additional_info_str = data.pop('additionalInfo')
            try:
                additional_info_dict = json.loads(additional_info_str)
                data['additional_information'] = additional_info_dict
            except json.JSONDecodeError:
                raise serializers.ValidationError("Invalid JSON format for additional information")
        return super().to_internal_value(data)
