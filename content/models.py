from django.db import models

# Create your models here.


class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=300)
    nickname = models.CharField(max_length=200, null=True)
    age = models.IntegerField(null=True)
    desc = models.TextField(null=True)

    def __str__(self):
        result = "username = " + self.username
        result += ", password = " + self.password
        if self.nickname:
            result += ", nickname = " + self.nickname
        if self.age:
            result += ", age = " + str(self.age)
        if self.desc:
            result += ", desc = " + self.desc
        return result


