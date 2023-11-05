from django.db import models


# Create your models here.
class Module(models.Model):
    title = models.CharField(max_length=30, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    module_user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='создатель модуля')

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Модуль'
        verbose_name_plural = 'Модули'
