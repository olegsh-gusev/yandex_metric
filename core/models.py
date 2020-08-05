from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def __str__(self):
        return self.username


class WorkPlace(models.Model):
    name = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=30, blank=True)

    # TODO add is_active?

    def __str__(self):
        return self.name


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workplace = models.ForeignKey(WorkPlace, on_delete=models.CASCADE)
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()

    def save(self, *args, **kwargs):
        if self.date_from > self.date_to:
            raise ValueError('date_from>date_to')
        # check reservation time?
        super(Reservation, self).save(*args, **kwargs)
