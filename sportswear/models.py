from django.db import models
from django.contrib.auth import get_user_model

class SportswearBrand(models.Model):

    brand_name = models.CharField(max_length=100, unique=True, verbose_name="Brand Name")
    description = models.TextField(verbose_name="Description")
    link = models.URLField(max_length=500, verbose_name="Link E-Commerce")
    thumbnail_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="URL Brand Logo")

    category_tag = models.CharField(max_length=50, default='Yoga', verbose_name="Category Tag (Yoga, Pilates, etc.)")
    average_rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0, verbose_name="Average Rating")

    def __str__(self):
        return self.brand_name
    
class BrandReview(models.Model):
    brand = models.ForeignKey(
        SportswearBrand, 
        on_delete=models.CASCADE, 
        related_name='reviews' 
    )

    rating_value = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)
    review_text = models.TextField(verbose_name="Review Text")
    reviewer = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sportswear_reviews'
    )

    location = models.CharField(max_length=50, default='Jakarta')

    def __str__(self):
        return f"Review ({self.rating_value}/5) for {self.brand.brand_name} by {self.reviewer.username if self.reviewer else 'Anonymous'}"