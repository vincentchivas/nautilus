from django import forms
from dolphinopadmin.configure.models import Package


def get_packages():
    return tuple([(i.uid, i.name) for i in Package.objects.all()])


class ButtonAdminForm(forms.ModelForm):
    package = forms.ChoiceField(widget=forms.Select(), choices=get_packages())
