from django import forms
from django.forms import CheckboxInput, CheckboxSelectMultiple, BooleanField

from processes.models import ProcesoCalculado, Equipo, EquipoEntrada, Material, Proceso
from django.core.exceptions import ValidationError


class startProcessForm(forms.ModelForm):
    class Meta:
        model = ProcesoCalculado

        fields = [
            'idprocesos',
            'idanioprecio',
            'idequipoentradainicio',
            'idequipoentradafinal',
            'idequipo'
        ]

    def __init__(self, *args, **kwargs):

        super(startProcessForm, self).__init__(*args, **kwargs)

        self.fields["idprocesos"].widget = CheckboxSelectMultiple()
        self.fields["idprocesos"].queryset = Proceso.objects.all()

    def clean(self):
        equipo = self.cleaned_data.get('idequipo').idequipo
        final = self.cleaned_data.get('idequipoentradafinal')
        inicial = self.cleaned_data.get('idequipoentradainicio')
        if equipo == None or final == None or inicial == None:
            raise ValidationError(" Datos requeridos no ingresados.")
        anioinicial = inicial.anio
        aniofinal = final.anio
        equipoinicial = inicial.idequipo.idequipo
        equipofinal = final.idequipo.idequipo
        if (equipofinal != equipoinicial or equipo != equipoinicial or equipo != equipoinicial):
            raise ValidationError(" El Equipo del Año Inicial y Año Final den ser igual del AEE.")
        if (anioinicial > aniofinal):
            raise ValidationError("Año Final debe ser mayor o igual al Año Inicial.")

        return self.cleaned_data


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['nombre']


class ProcesoForm(forms.ModelForm):
    materiales = BooleanField(
        widget=CheckboxSelectMultiple(
            attrs={'data-validation-error-msg': 'You have to agree to our terms and conditions'}))
    class Meta:
        model = Proceso
        fields = ['proceso',
                  'idgrupo',
                  'idtipo',
                  'materiales',
                  'costotratamiento',
                  'costoinversion',
                  'rendimientominimo',
                  'incrementorendimiento',
                  'tiempodepreciacion',
                  'iddensidad',
                  'loop',
                  'procesoid',
                  'mantenimientotonelada',
                  'manoobratonelada',
                  'energia',
                  'otros']

    def __init__(self, *args, **kwargs):
        super(ProcesoForm,self).__init__(*args, **kwargs)
        #self.fields['materiales'].widget = forms.CheckboxSelectMultiple()
        #self.fields['materiales'].widget = CheckboxInput()
        self.fields['materiales'].widget =forms.MultipleChoiceField(

            widget=forms.CheckboxSelectMultiple

        )


