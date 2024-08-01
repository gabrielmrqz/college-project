from django.db import models
from django.utils import timezone
import uuid

# Create your models here.
class Setores(models.Model):
    setor=models.CharField(max_length=150,null=False,blank=False)
    emails= models.TextField(blank=False,null=False)

class Historico(models.Model):
    nome = models.CharField(max_length=150,null=False,blank=False)
    emails = models.TextField()
    setor = models.CharField(max_length=150)
    data_hora = models.DateTimeField()
    emails_enviados = models.IntegerField()
    falharam = models.IntegerField()
    passaram = models.IntegerField()
    abriram = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)


class Agendados(models.Model):
    nome = models.CharField(max_length=150,null=False,blank=False)
    emails = models.TextField()
    setor = models.CharField(max_length=150)    
    template = models.TextField()
    data_hora = models.DateTimeField()

class Templates(models.Model):
    nome = models.CharField(max_length=150,null=False,blank=False)
    body = models.TextField()

class HistoricoIndiv(models.Model):
    nome = models.CharField(max_length=50,null=False,blank=False)
    email = models.TextField()
    setor = models.CharField(max_length=40)
    enviados = models.IntegerField(default=0)
    falhou = models.IntegerField(default=0)
    passou = models.IntegerField(default=0)
    abriu = models.IntegerField(default=0)

class RastreioPixel(models.Model):
    id_pixel = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    nome_campanha = models.TextField()
    email = models.TextField()
    aberto = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

class RastreioLink(models.Model):
    id_link = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    nome_campanha = models.TextField()
    email = models.TextField()
    aberto = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)