from django.db import models

# Create your models here.
class Products(models.Model):

    class Meta:
        verbose_name_plural = "Products"        
    id = models.IntegerField(primary_key=True)
    product_json = models.TextField() 

    def __str__(self):
        return str(self.pk)
   