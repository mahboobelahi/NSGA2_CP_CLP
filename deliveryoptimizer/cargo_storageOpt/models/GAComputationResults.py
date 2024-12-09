from django.db import models
import json

class GAResult(models.Model):
    # Fields to store GA computation results
    id = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=255)
    result_json = models.JSONField()

    def __str__(self):
        return f"{self.file_name}-{self.id}"
    
    def get_metadata(self):
        return self.result_json.get("cargo_metadata")
    
    def get_layouts(self):
        return self.result_json.get("layouts")
    
    def get_result_json(self):
        return self.result_json