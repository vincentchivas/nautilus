#! -*- coding:utf-8 -*-
import json
from django import forms

LAYOUT_CHOICES = {
    "AndroidCN":
    ((1, '网页'),
     (2, '小说'),
     (3, '新闻'),
     (4, '购物'),
     (5, '图片'),
     ),
    "AndroidEN":
    ((101, '普通搜索'),
     (102, '垂直搜索'),
     ),
    "IosCN":
    ((201, '普通搜索'),
     ),
    "IosEN":
    ((301, '普通搜索'),
     ),
}


def get_all_choises(choices):
    choices_list = []
    for key in choices:
        choices_list.extend(list(choices[key]))
    return choices_list


class SearchCategoryAdminForm(forms.ModelForm):
    json_str = ["extend"]
    layout = forms.ChoiceField(widget=forms.Select(), choices=get_all_choises(
        LAYOUT_CHOICES), label="Category layout")
#    extend = forms.CharField(help_text="Be sure in json format")

    def clean(self):
        try:
            for content in self.json_str:
                if self.cleaned_data.get(content):
                    json.loads(self.cleaned_data.get(content))
        except Exception:
            raise forms.ValidationError(
                "%s is either None or json format string" % content)
        return self.cleaned_data
