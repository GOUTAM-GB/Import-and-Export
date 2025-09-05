from django.db import models
from django.utils import timezone

# Create your models here.
class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.BooleanField(default=True)
    def __str__(self):
        return self.name


class State(models.Model):
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="states"
    )
   
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('country', 'name')
       
    def __str__(self):
        return f"{self.name}, {self.country.name}"
      

class City(models.Model):
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="cities"
    )

    state = models.ForeignKey(
        State, on_delete=models.CASCADE, related_name="cities"
    )

    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.BooleanField(default=True)

    class Meta:
        unique_together = ('state', 'name')

    def __str__(self):
        return f"{self.name}, {self.state.name}, {self.country.name}"

