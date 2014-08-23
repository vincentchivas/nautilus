#! -*- coding:utf-8 -*-
import json
from django import forms

PUSHTYPE_CHOICES = (
    (1, '增加一个桌面icon'),
    (2, '增加一条书签'),
    (3, '修改一个桌面icon'),
    (4, '修改一条书签'),
    (5, '增加一个icon文件夹'),
    (6, '删除一个桌面icon'),
    (7, 'push消息到海豚公告'),
)


class PushAdminForm(forms.ModelForm):
    json_str = ["content1", "content2", "content3", "content4"]
    push_type = forms.ChoiceField(
        widget=forms.Select(), choices=PUSHTYPE_CHOICES, label="Category layout")
#    content1 = forms.CharField(help_text="Be sure in json format")

    def clean(self):
        try:
            for content in self.json_str:
                if self.cleaned_data.get(content):
                    json.loads(self.cleaned_data.get(content))
        except Exception:
            raise forms.ValidationError(
                "%s is either None or json format string" % content)
        return self.cleaned_data
