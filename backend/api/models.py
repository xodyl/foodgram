from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name='Ingredient name'
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name='Measurement unit'
    )
    
    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'


    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class Tag(models.Model):
    name = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name='Tag name'
    )  
    slug = models.SlugField(
        max_length=50, 
        unique=True,
        verbose_name='Tag name'
    ) 

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="recipes",
        verbose_name="Author"
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Title'
    )
    image = models.ImageField(
        upload_to="recipes/",
        verbose_name='Image'
    ) 
    text = models.TextField(verbose_name='Recipe text')  
    ingredients = models.ManyToManyField(
        Ingredient, 
        through='RecipeIngredient',
        verbose_name='Recipe ingredients'
    ) 
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Tags'
    ) 
    cooking_time = models.PositiveIntegerField(
        verbose_name='Cooking time'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Publication date'
    )

    class Meta:
        verbose_name = 'Reciepe'
        verbose_name_plural = 'Recipes'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title'), name='unique recipe'
            )
        ]
        ordering = ('pub_date',)
        default_related_name = 'recipes'

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.FloatField() 

    def __str__(self):
        return f"{self.amount} {self.ingredient.measurement_unit} of {self.ingredient.name} in {self.recipe.title}"

