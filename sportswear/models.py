from django.db import models

class SportswearBrand(models.Model):

    brand_name = models.CharField(max_length=100, unique=True, verbose_name="Brand Name")
    description = models.TextField(verbose_name="Description")
    link = models.URLField(max_length=500, verbose_name="Link E-Commerce")
    thumbnail_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="URL Brand Logo")

    def __str__(self):
        return self.brand_name