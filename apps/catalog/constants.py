from django.db import models


class PublishStatus(models.TextChoices):
    DRAFT = "draft", "Borrador"
    PUBLISHED = "published", "Publicado"


class RecipeAccessType(models.TextChoices):
    LIFETIME = "lifetime", "Acceso de por vida"
    TIMED = "timed", "Acceso por tiempo limitado"
