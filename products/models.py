from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
    )

    class Meta:
        verbose_name_plural = 'Categories'
        constraints = [
            models.UniqueConstraint(fields=['name', 'parent'], name='unique_category_name_per_parent'),
        ]
        ordering = ['name']

    def __str__(self):
        if self.parent:
            return f'{self.parent} / {self.name}'
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    # DecimalField currency ke liye best hota hai taaki calculation me gadbad na ho
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
    )
    # ImageField product ki photo upload karne ke liye
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name