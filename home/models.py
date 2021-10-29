from django.db import models

# Create your models here.
class Products(models.Model):

    class Meta:
        verbose_name_plural = "Products"
    id = models.IntegerField(primary_key=True)
    product_name = models.CharField(max_length=254)
    product_url = models.CharField(max_length=254, blank=True, null=True, default='None')
    product_image_url = models.CharField(
        max_length=254, blank=True, null=True, default='None')
    product_rating = models.DecimalField(
        max_digits=2, decimal_places=1, blank=True, null=True, default=None)
    product_json = models.TextField()

    def __str__(self):
        return str(self.product_name)

class Offers(models.Model):

    class Meta:
        verbose_name_plural = "Offers"
    products = models.ForeignKey(
            'Products', null=False, blank=False, on_delete=models.CASCADE,
            related_name='offers')
    seller_name = models.CharField(max_length=254)
    main_seller = models.BooleanField(null=True)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_json = models.TextField()

    def __str__(self):
        return str(self.products)

class HistoryJson(models.Model):

    class Meta:
        verbose_name_plural = "History_JSON"

    created_at = models.DateTimeField(auto_now_add=True)
    product_json = models.TextField()

    def __str__(self):
        return str(self.created_at)
