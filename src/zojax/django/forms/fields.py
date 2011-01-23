from django import forms


class CustomizableModelChoiceField(forms.ModelChoiceField):
    
    custom_label_from_instance = None
    
    def __init__(self, *kv, **kw):
        try:
            self.custom_label_from_instance = kw.pop('custom_label_from_instance')
        except KeyError:
            pass
        super(CustomizableModelChoiceField, self).__init__(*kv, **kw)
        
    def label_from_instance(self, obj):
        if self.custom_label_from_instance:
            return self.custom_label_from_instance(self, obj)
        return super(CustomizableModelChoiceField, self).custom_label_from_instance(obj)