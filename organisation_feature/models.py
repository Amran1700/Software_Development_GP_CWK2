from django.db import models
# Register your models here.

class TeamType(models.Model):
    #Represents a category that team belongs to

    type_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.type_name
    
    class Meta: 
        ordering = ['type_name']


class Department (models.Model):
    #reprents department in sky organisation 

    department_name = models.CharField(max_length=150)
    specialisation = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.department_name
    
    class Meta:
        ordering = ['department_name']

