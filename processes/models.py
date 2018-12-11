from django.db import models

from DataBase.DataBaseQuery import getPreciosAnio


class AnioPrecio(models.Model):
    anio=models.IntegerField(db_column='ANIOPRECIO',primary_key=True)
    class Meta:
        managed = True
        db_table = 'ANIOPRECIO'
    def __str__(self):
        return str(self.anio)#+" "+str(getPreciosAnio(self.anio))#str(self.anio)


class Material(models.Model):
    idmaterial = models.AutoField(db_column='IDMATERIAL', primary_key=True)
    nombre = models.CharField(db_column='NOMBRE', max_length=45)

    class Meta:
        managed = True
        db_table = 'MATERIAL'

    def __str__(self):
        return self.nombre

class Equipo(models.Model):
    idequipo = models.AutoField(db_column='IDEQUIPO', primary_key=True)  
    nombre = models.CharField(db_column='NOMBRE', max_length=45)
    materiales = models.ManyToManyField(Material)

    class Meta:
        managed = True
        db_table = 'EQUIPO'
        unique_together = (('nombre'),)

    def __str__(self):
        return self.nombre

class EquipoEntrada(models.Model):
    idequipoentrada = models.AutoField(db_column='IDEQUIPOENTRADA', primary_key=True)  
    idequipo = models.ForeignKey('Equipo', models.DO_NOTHING, db_column='IDEQUIPO')  
    anio = models.IntegerField(db_column='ANIO')  

    class Meta:
        managed = True
        db_table = 'EQUIPOENTRADA'
        unique_together = (('idequipo', 'anio'),)

    def __str__(self):
        return str(self.anio)+" "+str(self.idequipo)

class MasaEntrada(models.Model):
    idmasaentrada = models.AutoField(db_column='IDMASAENTRADA', primary_key=True)
    idequipoentrada = models.ForeignKey('EquipoEntrada', models.DO_NOTHING, db_column='IDEQUIPOENTRADA')  
    idmaterial = models.ForeignKey('Material', models.DO_NOTHING, db_column='IDMATERIAL')  
    masa = models.DecimalField(db_column='MASA', max_digits=50, decimal_places=20)  


    class Meta:
        managed = True
        db_table = 'MASAENTRADA'
        unique_together = (('idequipoentrada', 'idmaterial'),)

class MaterialPrecio(models.Model):
    idmaterialprecio = models.AutoField(db_column='IDMATERIALPRECIO', primary_key=True,verbose_name='Cod')
    anio = models.ForeignKey('AnioPrecio', models.DO_NOTHING, db_column='ANIOPRECIO',verbose_name='Año')
    idmaterial = models.ForeignKey('Material', models.DO_NOTHING, db_column='IDMATERIAL',verbose_name='Material')
    precioreventa = models.DecimalField(db_column='PRECIOREVENTA', max_digits=50, decimal_places=2,verbose_name='Precio Venta $')

    class Meta:
        managed = True
        db_table = 'MATERIALPRECIO'
        unique_together = (('anio', 'idmaterial'),)

    def __str__(self):
        return str(self.idmaterial) + " €" + str(float(self.precioreventa))

class Grupo(models.Model):
    idgrupo = models.AutoField(db_column='IDGRUPO', primary_key=True)  
    nombre = models.CharField(db_column='NOMBRE', max_length=45)  

    class Meta:
        managed = True
        db_table = 'GRUPO'

    def __str__(self):
        return self.nombre

class Tipo(models.Model):
    idtipo = models.AutoField(db_column='IDTIPO', primary_key=True)  
    nombre = models.CharField(db_column='NOMBRE', max_length=45)  

    class Meta:
        managed = True
        db_table = 'TIPO'

    def __str__(self):
        return self.nombre

class Densidad(models.Model):
    iddensidad = models.AutoField(db_column='IDDENSIDAD', primary_key=True)  
    densidad = models.DecimalField(db_column='DENSIDAD', max_digits=50, decimal_places=20)  

    class Meta:
        managed = True
        db_table = 'DENSIDAD'
        unique_together = (('iddensidad', 'densidad'),)

    def __str__(self):
        return str(self.iddensidad)

class DensidadMaterial(models.Model):
    iddensidad = models.ForeignKey('Densidad', models.DO_NOTHING,db_column='IDDENSIDAD')  
    idmaterial = models.ForeignKey('Material', models.DO_NOTHING, db_column='MATERIAL_IDMATERIAL')  
    valor = models.DecimalField(db_column='VALOR', max_digits=50, decimal_places=20)  

    class Meta:

        db_table = 'DENSIDADMATERIAL'
        unique_together = (('iddensidad', 'idmaterial'),)

class Proceso(models.Model):
    idproceso = models.AutoField(db_column='IDPROCESO', primary_key=True)  
    proceso = models.CharField(db_column='PROCESO', max_length=45,verbose_name='Nombre Proceso')
    idgrupo = models.ForeignKey('Grupo', models.DO_NOTHING, db_column='GRUPO',verbose_name='Grupo')
    idtipo = models.ForeignKey('Tipo', models.DO_NOTHING, db_column='TIPO',verbose_name='Tipo')
    materiales = models.ManyToManyField(Material)#db_table='Material_has_Proceso'  through='Material_has_Proceso'
    costotratamiento = models.DecimalField(db_column='COSTOTRATAMIENTO', max_digits=50,decimal_places=20,verbose_name='Costotra Tamiento')
    costoinversion = models.DecimalField(db_column='COSTOINVERSION', max_digits=50, decimal_places=20,verbose_name='Costo Inversion')
    rendimientominimo = models.DecimalField(db_column='RENDIMIENTOMINIMO', max_digits=50, decimal_places=20, blank=True, null=True,verbose_name='Rendimiento Minimo')
    incrementorendimiento=models.DecimalField(db_column='INCREMENTORENDIMIENTO', max_digits=50, decimal_places=20, blank=True, null=True,verbose_name='Incremento Rendimiento')
    tiempodepreciacion=models.DecimalField(db_column='TIEMPODEPRECIACION', max_digits=50, decimal_places=20, blank=True, null=True,verbose_name='Tiempo Depreciacion')
    iddensidad=models.ForeignKey('Densidad', models.DO_NOTHING, db_column='IDDENSIDAD', blank=True, null=True,verbose_name='Densidad')
    loop=models.CharField(db_column='LOOP', max_length=45,verbose_name='Loop')
    procesoid=models.IntegerField(db_column='PROCESOID', null=True,verbose_name='Proceso Id')
    mantenimientotonelada=models.DecimalField(db_column='MANTENIMIENTOTONELADA', max_digits=50, decimal_places=20, blank=True, null=True,verbose_name='Mantenimiento Tonelada $')
    manoobratonelada=models.DecimalField(db_column='MANOOBRATONELADA', max_digits=50, decimal_places=20, blank=True, null=True,verbose_name='Mano Obra Tonelada $')
    energia=models.DecimalField(db_column='ENERGIA', max_digits=50, decimal_places=20, blank=True, null=True,verbose_name='Energia')
    otros = models.DecimalField(db_column='OTROS', max_digits=50, decimal_places=20, blank=True, null=True,verbose_name='Otros')

    class Meta:
        managed = True
        db_table = 'PROCESO'
        unique_together = (('idproceso','idgrupo','idtipo'),)

    def __str__(self):
        return self.proceso

class RendimientoProceso(models.Model):
    idmaterial = models.ForeignKey(Material, models.DO_NOTHING,related_name='materialidmaterial', db_column='IDMATERIAL')  
    idmaterialreferencia = models.ForeignKey(Material, models.DO_NOTHING, related_name='idmaterialRefe', db_column='IDMATERIALREFERENCIA')
    #idmaterialreferencia = models.IntegerField(db_column='IDMATERIALREFERENCIA')
    idproceso = models.ForeignKey(Proceso, models.DO_NOTHING, db_column='IDPROCESO')  
    valor = models.DecimalField(db_column='VALOR', max_digits=50, decimal_places=20)  

    class Meta:
        managed = True
        db_table = 'RENDIMIENTOPROCESO'
        unique_together = (('idmaterial', 'idmaterialreferencia', 'idproceso'),)

class ProcesoCalculado(models.Model):
    idprocesocalculado = models.AutoField(db_column='IDPROCESOSCALCULADO', primary_key=True)
    idprocesos=models.ManyToManyField(Proceso)
    idanioprecio=models.ForeignKey(AnioPrecio,models.DO_NOTHING,db_column='ANIOPRECIO')
    idequipoentradainicio=models.ForeignKey(EquipoEntrada,models.DO_NOTHING,db_column='IDENTRADAINICIO',related_name='ANIOINICIO')
    idequipoentradafinal=models.ForeignKey(EquipoEntrada,models.DO_NOTHING,db_column='IDENTRADAFINAL',related_name='ANIOFINAL')
    idequipo=models.ForeignKey(Equipo,models.DO_NOTHING,db_column='IDEQUIPO')
    class Meta:
        managed = True
        db_table = 'PROCESOCALCULADO'

    def __str__(self):
        return str(self.idequipo)+" "+str(self.idequipoentradainicio)+" "+str(self.idequipoentradafinal)


class ProcesoSeparacionId(models.Model):
    idprocesosseparacionid = models.AutoField(db_column='IDPROCESOSSEPARACIONID', primary_key=True)  
    anio = models.IntegerField(db_column='ANIO')  
    idprocesocalculado=models.ForeignKey(ProcesoCalculado,models.DO_NOTHING,db_column='IDPROCESOCALCULADO')
    #idequipo=models.ForeignKey(Equipo, models.DO_NOTHING, db_column='IDEQUIPO')
    class Meta:
        managed = True
        db_table = 'PROCESOSEPARACIONID'
        unique_together = (('idprocesosseparacionid', 'anio'),)

class ProcesoSeparacion(models.Model):
    idprocesosseparacion = models.AutoField(db_column='IDPROCESOSSEPARACION',primary_key=True)  
    idprocesosseparacionid = models.ForeignKey(ProcesoSeparacionId, models.DO_NOTHING, db_column='IDPROCESOSSEPARACIONID')  
    secuenciaprocesoseparacion = models.IntegerField(db_column='SECUENCIAPROCESOSEPARACION')  
    inversion=models.DecimalField(db_column='INVERSION', max_digits=50, decimal_places=20)  
    valorneto=models.DecimalField(db_column='VALORNETO', max_digits=50, decimal_places=20)  

    class Meta:
        managed = True
        db_table = 'PROCESOSEPARACION'
        unique_together = (('idprocesosseparacionid', 'secuenciaprocesoseparacion'),)

class ProcesoCombinacion(models.Model):
    idprocesocombinacion = models.AutoField(db_column='IDPROCESOCOMBINACION',primary_key=True)
    idprocesosseparacion = models.ForeignKey('ProcesoSeparacion', models.DO_NOTHING, related_name='PSidprocesosseparacion', db_column='IDPROCESOSSEPARACION')
    secuencia = models.IntegerField(db_column='SECUENCIA')
    idprocesosalida = models.ForeignKey('Proceso', models.DO_NOTHING, db_column='IDPROCESOSALIDA', null=True)
    idprocesoprevio = models.ForeignKey('Proceso', models.DO_NOTHING, db_column='IDPROCESOPREVIO',related_name='idprocesoPre', null=True)
        #models.IntegerField(db_column='IDPROCESOPREVIO', blank=True, null=True)
    idmaterial = models.IntegerField(db_column='IDMATERIAL', blank=True, null=True)
    salida = models.IntegerField(db_column='SALIDA', null=True)

    class Meta:
        managed = True
        db_table = 'PROCESOCOMBINACION'
        unique_together = (('idprocesosseparacion','secuencia'),)

class TipoImpureza(models.Model):
    idtipoimpureza = models.AutoField(db_column='IDTIPOIMPUREZA', primary_key=True)
    descripcion = models.CharField(db_column='DESCRIPCION', max_length=45)

    class Meta:
        managed = True
        db_table = 'TIPOIMPUREZA'

    def __str__(self):
        return self.descripcion

class Impureza(models.Model):
    idimpureza = models.AutoField(db_column='IDIMPUREZA', primary_key=True)
    idtipoimpureza= models.ForeignKey(TipoImpureza, models.DO_NOTHING, db_column='IDTIPOIMPUREZA')
    etapa = models.IntegerField(db_column='ETAPA')
    parametro = models.DecimalField(db_column='PARAMETRO', max_digits=50, decimal_places=20)

    class Meta:
        managed = True
        db_table = 'IMPUREZA'
        unique_together = (('idtipoimpureza', 'etapa'),)

    def __str__(self):
        return str(self.idtipoimpureza)+" Etapa " +str(self.etapa)

class ImpuezaMaterial(models.Model):
    idimpuereza=models.ForeignKey(Impureza,models.DO_NOTHING,db_column='IDIMPUEREZA')
    idimaterial=models.ForeignKey(Material,models.DO_NOTHING,db_column='IDMATERIAL',related_name='IdmaterialPri')
    idimaterialreferencia = models.ForeignKey(Material, models.DO_NOTHING, db_column='IDMATERIALREFERENCIA',related_name='IdmaterialRef')
    valor=models.DecimalField(db_column='VALOR', max_digits=50, decimal_places=20)

    class Meta:
        managed = True
        db_table = 'IMPUREZAMATERIAL'


class Parametroseconomicos(models.Model):
    idparametroseconomicos = models.AutoField(db_column='IDPARAMETROSECONOMICOS', primary_key=True)
    idproceso = models.ForeignKey('Proceso', models.DO_NOTHING, db_column='IDPROCESO')
    incineracion = models.DecimalField(db_column='INCINERACION', max_digits=50, decimal_places=20)
    desmontajemanual = models.DecimalField(db_column='DESMONTAJEMANUAL', max_digits=50, decimal_places=20)
    posttratamiento = models.DecimalField(db_column='POSTTRATAMIENTO', max_digits=50, decimal_places=20)
    trituracion40 = models.DecimalField(db_column='TRITURACION40', max_digits=50, decimal_places=20)
    trituracion15 = models.DecimalField(db_column='TRITURACION15', max_digits=50, decimal_places=20)
    pasospureza = models.IntegerField(db_column='PASOSPUREZA')
    patametroreventa1 = models.DecimalField(db_column='PATAMETROREVENTA1', max_digits=50, decimal_places=20)
    patametroreventa2 = models.DecimalField(db_column='PATAMETROREVENTA2', max_digits=50, decimal_places=20)
    patametroreventa3 = models.DecimalField(db_column='PATAMETROREVENTA3', max_digits=50, decimal_places=20)
    marr = models.DecimalField(db_column='MARR', max_digits=50, decimal_places=20)

    class Meta:
        managed = True
        db_table = 'PARAMETROSECONOMICOS'

class CostoEconomico(models.Model):
     idprocesoeconomico = models.AutoField(db_column='IDPROCESOECONOMICO',primary_key=True)
     idparametroseconomicos=models.ForeignKey(Parametroseconomicos, models.DO_NOTHING, db_column='IDPARAMETROSECONOMICOS',null=True)
     idprocesocombinacion = models.ForeignKey(ProcesoCombinacion, models.DO_NOTHING, db_column='IDPROCESOSCOMBINACION')
     idimpureza = models.ForeignKey(Impureza, models.DO_NOTHING, db_column='IDIMPUREZA' )
     ingresos = models.DecimalField(db_column='INGRESOS', max_digits=50, decimal_places=20)
     costotratamiento = models.DecimalField(db_column='COSTOTRATAMIENTO', max_digits=50, decimal_places=20)
     costodesmontajemanual = models.DecimalField(db_column='COSTODESMONTAJEMANUAL', max_digits=50, decimal_places=20)
     costotrituracion = models.DecimalField(db_column='COSTOTRITURACION', max_digits=50, decimal_places=20)
     costoposttratamiento = models.DecimalField(db_column='COSTOPOSTTRATAMIENTO', max_digits=50, decimal_places=20)


     class Meta:
         managed = True
         db_table = 'COSTOECONOMICO'
         unique_together = (('idprocesocombinacion', 'idimpureza'),)

#################
class Masasalida(models.Model):
    idprocesocombinacion = models.ForeignKey(ProcesoCombinacion, models.DO_NOTHING, db_column='IDPROCESOSCOMBINACION')
    idmaterial = models.ForeignKey('Material', models.DO_NOTHING, related_name='IDMATERIAL', db_column='IDMATERIAL')
    valormasa = models.DecimalField(db_column='VALORMASA', max_digits=50, decimal_places=20)

    class Meta:
        managed = True
        db_table = 'MASASALIDA'
        unique_together = (('idprocesocombinacion', 'idmaterial'),)