from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, AuthenticationForm
from django.forms import TextInput, PasswordInput
from .models import CustomUser, Medicine

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = (
        ('shopkeeper', 'Shopkeeper'),
        ('client', 'Client'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('role',)

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Username'}
        )
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Password'}
        )

class MedicineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        MEDICINE_CHOICES = [
            ('Acetaminophen', 'Acetaminophen'),
            ('Acetocillin', 'Acetocillin'),
            ('Acetomet', 'Acetomet'),
            ('Acetomycin', 'Acetomycin'),
            ('Acetonazole', 'Acetonazole'),
            ('Acetophen', 'Acetophen'),
            ('Acetoprofen', 'Acetoprofen'),
            ('Acetostatin', 'Acetostatin'),
            ('Acetovir', 'Acetovir'),
            ('Acyclovir', 'Acyclovir'),
            ('Albuterol', 'Albuterol'),
            ('Amlodipine', 'Amlodipine'),
            ('Amoxicillin', 'Amoxicillin'),
            ('Amoximet', 'Amoximet'),
            ('Amoximycin', 'Amoximycin'),
            ('Amoxinazole', 'Amoxinazole'),
            ('Amoxiphen', 'Amoxiphen'),
            ('Amoxiprofen', 'Amoxiprofen'),
            ('Amoxistatin', 'Amoxistatin'),
            ('Amoxivir', 'Amoxivir'),
            ('Antihistamines', 'Antihistamines'),
            ('Antiretroviral therapy (ART)', 'Antiretroviral therapy (ART)'),
            ('Antiviral medication', 'Antiviral medication'),
            ('Artemether', 'Artemether'),
            ('Aspirin', 'Aspirin'),
            ('Azithromycin', 'Azithromycin'),
            ('Benzoyl peroxide', 'Benzoyl peroxide'),
            ('Calamine lotion', 'Calamine lotion'),
            ('Calcipotriene', 'Calcipotriene'),
            ('Cefcillin', 'Cefcillin'),
            ('Cefmet', 'Cefmet'),
            ('Cefmycin', 'Cefmycin'),
            ('Cefnazole', 'Cefnazole'),
            ('Cefphen', 'Cefphen'),
            ('Cefprofen', 'Cefprofen'),
            ('Cefstatin', 'Cefstatin'),
            ('Cefvir', 'Cefvir'),
            ('Cephalexin', 'Cephalexin'),
            ('Cetirizine', 'Cetirizine'),
            ('Chloroquine', 'Chloroquine'),
            ('Ciprofloxacin', 'Ciprofloxacin'),
            ('Claricillin', 'Claricillin'),
            ('Clarimet', 'Clarimet'),
            ('Clarimycin', 'Clarimycin'),
            ('Clarinazole', 'Clarinazole'),
            ('Clariphen', 'Clariphen'),
            ('Clariprofen', 'Clariprofen'),
            ('Claristatin', 'Claristatin'),
            ('Clarivir', 'Clarivir'),
            ('Clopidogrel', 'Clopidogrel'),
            ('Clotrimazole', 'Clotrimazole'),
            ('Compression stockings', 'Compression stockings'),
            ('Corticosteroids', 'Corticosteroids'),
            ('Decongestants', 'Decongestants'),
            ('Dextrocillin', 'Dextrocillin'),
            ('Dextromet', 'Dextromet'),
            ('Dextromycin', 'Dextromycin'),
            ('Dextronazole', 'Dextronazole'),
            ('Dextrophen', 'Dextrophen'),
            ('Dextroprofen', 'Dextroprofen'),
            ('Dextrostatin', 'Dextrostatin'),
            ('Dextrovir', 'Dextrovir'),
            ('Dimenhydrinate', 'Dimenhydrinate'),
            ('Dolocillin', 'Dolocillin'),
            ('Dolomet', 'Dolomet'),
            ('Dolomycin', 'Dolomycin'),
            ('Dolonazole', 'Dolonazole'),
            ('Dolophen', 'Dolophen'),
            ('Doloprofen', 'Doloprofen'),
            ('Dolostatin', 'Dolostatin'),
            ('Dolovir', 'Dolovir'),
            ('Entecavir', 'Entecavir'),
            ('Glucagon', 'Glucagon'),
            ('Glucose tablets', 'Glucose tablets'),
            ('Hepatitis A vaccine', 'Hepatitis A vaccine'),
            ('Hydrocortisone cream', 'Hydrocortisone cream'),
            ('Ibuprocillin', 'Ibuprocillin'),
            ('Ibuprofen', 'Ibuprofen'),
            ('Ibupromet', 'Ibupromet'),
            ('Ibupromycin', 'Ibupromycin'),
            ('Ibupronazole', 'Ibupronazole'),
            ('Ibuprophen', 'Ibuprophen'),
            ('Ibuproprofen', 'Ibuproprofen'),
            ('Ibuprostatin', 'Ibuprostatin'),
            ('Ibuprovir', 'Ibuprovir'),
            ('Insulin', 'Insulin'),
            ('Isoniazid', 'Isoniazid'),
            ('Lansoprazole', 'Lansoprazole'),
            ('Ledipasvir', 'Ledipasvir'),
            ('Levothyroxine', 'Levothyroxine'),
            ('Lidocaine', 'Lidocaine'),
            ('Lisinopril', 'Lisinopril'),
            ('Loperamide', 'Loperamide'),
            ('Loratadine', 'Loratadine'),
            ('Meclizine', 'Meclizine'),
            ('Metformin', 'Metformin'),
            ('Methimazole', 'Methimazole'),
            ('Metocillin', 'Metocillin'),
            ('Metomet', 'Metomet'),
            ('Metomycin', 'Metomycin'),
            ('Metonazole', 'Metonazole'),
            ('Metophen', 'Metophen'),
            ('Metoprofen', 'Metoprofen'),
            ('Metostatin', 'Metostatin'),
            ('Metovir', 'Metovir'),
            ('Miconazole', 'Miconazole'),
            ('Mupirocin', 'Mupirocin'),
            ('Naproxen', 'Naproxen'),
            ('Nitrofurantoin', 'Nitrofurantoin'),
            ('Nitroglycerin', 'Nitroglycerin'),
            ('Omeprazole', 'Omeprazole'),
            ('Oral rehydration salts', 'Oral rehydration salts'),
            ('Pegylated interferon alfa-2a', 'Pegylated interferon alfa-2a'),
            ('Pentoxifylline', 'Pentoxifylline'),
            ('Propylthiouracil', 'Propylthiouracil'),
            ('Ranitidine', 'Ranitidine'),
            ('Ribavirin', 'Ribavirin'),
            ('Rifampin', 'Rifampin'),
            ('Salbutamol', 'Salbutamol'),
            ('Salicylic acid', 'Salicylic acid'),
            ('Sclerotherapy', 'Sclerotherapy'),
            ('Sofosbuvir', 'Sofosbuvir'),
            ('Sumatriptan', 'Sumatriptan'),
            ('Supportive care', 'Supportive care'),
            ('Tenofovir', 'Tenofovir'),
            ('Topical corticosteroids', 'Topical corticosteroids'),
            ('Trimethoprim', 'Trimethoprim'),
            ('Ursodeoxycholic acid', 'Ursodeoxycholic acid'),
        ]
        self.fields['name'] = forms.ChoiceField(choices=MEDICINE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:
        model = Medicine
        fields = ['name', 'price', 'quantity']
        widgets = {
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }
