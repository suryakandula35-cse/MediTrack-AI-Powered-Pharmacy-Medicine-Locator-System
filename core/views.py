from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import logout
from .models import Medicine, Shop
from .forms import MedicineForm, CustomUserCreationForm, LoginForm
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import pickle
import os
from django.conf import settings
import joblib
import pandas as pd
from decimal import Decimal

class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        return render(request, 'login.html', {'form': form})

class RegisterView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
        return render(request, 'register.html', {'form': form})


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_role'] = self.request.user.role
        return context



class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')

class SearchView(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'search.html'

    def get(self, request):
        medicine_name = request.GET.get('medicine_name', '')
        location = request.GET.get('location', '')
        context = {
            'query': medicine_name,
            'location': location,
        }

        if not medicine_name or not location:
            return render(request, self.template_name, context)

        user_coords = None
        if ',' in location:
            parts = location.split(',')
            if len(parts) == 2:
                try:
                    lat = float(parts[0].strip())
                    lon = float(parts[1].strip())
                    user_coords = (lat, lon)
                except ValueError:
                    pass
        if user_coords is None:
            geolocator = Nominatim(user_agent="meditrack")
            try:
                user_location = geolocator.geocode(location)
                if not user_location:
                    context['error'] = f'Location "{location}" not found.'
                    return render(request, self.template_name, context)
                user_coords = (user_location.latitude, user_location.longitude)
            except Exception as e:
                context['error'] = 'There was an error processing your location.'
                return render(request, self.template_name, context)

        medicines = Medicine.objects.select_related('shop').filter(name__icontains=medicine_name, shop__is_open=True)
        results = []
        for medicine in medicines:
            shop = medicine.shop
            if shop.latitude and shop.longitude:
                shop_coords = (shop.latitude, shop.longitude)
                distance = geodesic(user_coords, shop_coords).kilometers
                if distance <= 25: # Search radius of 25km
                    # Mark as unavailable if price or quantity is None or 0
                    is_available = medicine.price is not None and medicine.quantity is not None and medicine.quantity > 0
                    results.append({
                        'medicine': medicine,
                        'distance': distance,
                        'available': is_available
                    })
        # Show available first, then unavailable
        sorted_results = sorted(results, key=lambda x: (not x['available'], x['distance']))
        context['results'] = sorted_results
        return render(request, self.template_name, context)

class ShopkeeperRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'shopkeeper'

class MedicineManagementView(LoginRequiredMixin, ShopkeeperRequiredMixin, View):
    login_url = '/'
    template_name = 'medicine_management.html'

    MASTER_MEDICINES = [
        'Acetaminophen', 'Acetocillin', 'Acetomet', 'Acetomycin', 'Acetonazole', 'Acetophen', 'Acetoprofen', 'Acetostatin', 'Acetovir', 'Acyclovir', 'Albuterol', 'Amlodipine', 'Amoxicillin', 'Amoximet', 'Amoximycin', 'Amoxinazole', 'Amoxiphen', 'Amoxiprofen', 'Amoxistatin', 'Amoxivir', 'Antihistamines', 'Antiretroviral therapy (ART)', 'Antiviral medication', 'Artemether', 'Aspirin', 'Azithromycin', 'Benzoyl peroxide', 'Calamine lotion', 'Calcipotriene', 'Cefcillin', 'Cefmet', 'Cefmycin', 'Cefnazole', 'Cefphen', 'Cefprofen', 'Cefstatin', 'Cefvir', 'Cephalexin', 'Cetirizine', 'Chloroquine', 'Ciprofloxacin', 'Claricillin', 'Clarimet', 'Clarimycin', 'Clarinazole', 'Clariphen', 'Clariprofen', 'Claristatin', 'Clarivir', 'Clopidogrel', 'Clotrimazole', 'Compression stockings', 'Corticosteroids', 'Decongestants', 'Dextrocillin', 'Dextromet', 'Dextromycin', 'Dextronazole', 'Dextrophen', 'Dextroprofen', 'Dextrostatin', 'Dextrovir', 'Dimenhydrinate', 'Dolocillin', 'Dolomet', 'Dolomycin', 'Dolonazole', 'Dolophen', 'Doloprofen', 'Dolostatin', 'Dolovir', 'Entecavir', 'Glucagon', 'Glucose tablets', 'Hepatitis A vaccine', 'Hydrocortisone cream', 'Ibuprocillin', 'Ibuprofen', 'Ibupromet', 'Ibupromycin', 'Ibupronazole', 'Ibuprophen', 'Ibuproprofen', 'Ibuprostatin', 'Ibuprovir', 'Insulin', 'Isoniazid', 'Lansoprazole', 'Ledipasvir', 'Levothyroxine', 'Lidocaine', 'Lisinopril', 'Loperamide', 'Loratadine', 'Meclizine', 'Metformin', 'Methimazole', 'Metocillin', 'Metomet', 'Metomycin', 'Metonazole', 'Metophen', 'Metoprofen', 'Metostatin', 'Metovir', 'Miconazole', 'Mupirocin', 'Naproxen', 'Nitrofurantoin', 'Nitroglycerin', 'Omeprazole', 'Oral rehydration salts', 'Pegylated interferon alfa-2a', 'Pentoxifylline', 'Propylthiouracil', 'Ranitidine', 'Ribavirin', 'Rifampin', 'Salbutamol', 'Salicylic acid', 'Sclerotherapy', 'Sofosbuvir', 'Sumatriptan', 'Supportive care', 'Tenofovir', 'Topical corticosteroids', 'Trimethoprim', 'Ursodeoxycholic acid'
    ]

    # Default prices for each medicine in Indian Rupees (₹)
    DEFAULT_PRICES = {
        'Acetaminophen': Decimal('25.00'),
        'Acetocillin': Decimal('45.00'),
        'Acetomet': Decimal('40.00'),
        'Acetomycin': Decimal('50.00'),
        'Acetonazole': Decimal('60.00'),
        'Acetophen': Decimal('30.00'),
        'Acetoprofen': Decimal('28.00'),
        'Acetostatin': Decimal('65.00'),
        'Acetovir': Decimal('48.00'),
        'Acyclovir': Decimal('55.00'),
        'Albuterol': Decimal('35.00'),
        'Amlodipine': Decimal('18.00'),
        'Amoxicillin': Decimal('55.00'),
        'Amoximet': Decimal('50.00'),
        'Amoximycin': Decimal('60.00'),
        'Amoxinazole': Decimal('65.00'),
        'Amoxiphen': Decimal('40.00'),
        'Amoxiprofen': Decimal('38.00'),
        'Amoxistatin': Decimal('70.00'),
        'Amoxivir': Decimal('58.00'),
        'Antihistamines': Decimal('20.00'),
        'Antiretroviral therapy (ART)': Decimal('150.00'),
        'Antiviral medication': Decimal('80.00'),
        'Artemether': Decimal('95.00'),
        'Aspirin': Decimal('15.00'),
        'Azithromycin': Decimal('75.00'),
        'Benzoyl peroxide': Decimal('120.00'),
        'Calamine lotion': Decimal('60.00'),
        'Calcipotriene': Decimal('180.00'),
        'Cefcillin': Decimal('45.00'),
        'Cefmet': Decimal('48.00'),
        'Cefmycin': Decimal('52.00'),
        'Cefnazole': Decimal('58.00'),
        'Cefphen': Decimal('50.00'),
        'Cefprofen': Decimal('55.00'),
        'Cefstatin': Decimal('70.00'),
        'Cefvir': Decimal('65.00'),
        'Cephalexin': Decimal('65.00'),
        'Cetirizine': Decimal('22.00'),
        'Chloroquine': Decimal('18.00'),
        'Ciprofloxacin': Decimal('85.00'),
        'Claricillin': Decimal('68.00'),
        'Clarimet': Decimal('65.00'),
        'Clarimycin': Decimal('70.00'),
        'Clarinazole': Decimal('75.00'),
        'Clariphen': Decimal('50.00'),
        'Clariprofen': Decimal('48.00'),
        'Claristatin': Decimal('78.00'),
        'Clarivir': Decimal('72.00'),
        'Clopidogrel': Decimal('95.00'),
        'Clotrimazole': Decimal('100.00'),
        'Compression stockings': Decimal('350.00'),
        'Corticosteroids': Decimal('110.00'),
        'Decongestants': Decimal('30.00'),
        'Dextrocillin': Decimal('48.00'),
        'Dextromet': Decimal('50.00'),
        'Dextromycin': Decimal('55.00'),
        'Dextronazole': Decimal('60.00'),
        'Dextrophen': Decimal('45.00'),
        'Dextroprofen': Decimal('42.00'),
        'Dextrostatin': Decimal('72.00'),
        'Dextrovir': Decimal('62.00'),
        'Dimenhydrinate': Decimal('35.00'),
        'Dolocillin': Decimal('50.00'),
        'Dolomet': Decimal('52.00'),
        'Dolomycin': Decimal('58.00'),
        'Dolonazole': Decimal('65.00'),
        'Dolophen': Decimal('48.00'),
        'Doloprofen': Decimal('45.00'),
        'Dolostatin': Decimal('75.00'),
        'Dolovir': Decimal('68.00'),
        'Entecavir': Decimal('200.00'),
        'Glucagon': Decimal('250.00'),
        'Glucose tablets': Decimal('40.00'),
        'Hepatitis A vaccine': Decimal('400.00'),
        'Hydrocortisone cream': Decimal('85.00'),
        'Ibuprocillin': Decimal('28.00'),
        'Ibuprofen': Decimal('20.00'),
        'Ibupromet': Decimal('22.00'),
        'Ibupromycin': Decimal('25.00'),
        'Ibupronazole': Decimal('30.00'),
        'Ibuprophen': Decimal('24.00'),
        'Ibuproprofen': Decimal('26.00'),
        'Ibuprostatin': Decimal('35.00'),
        'Ibuprovir': Decimal('32.00'),
        'Insulin': Decimal('250.00'),
        'Isoniazid': Decimal('45.00'),
        'Lansoprazole': Decimal('90.00'),
        'Ledipasvir': Decimal('300.00'),
        'Levothyroxine': Decimal('35.00'),
        'Lidocaine': Decimal('70.00'),
        'Lisinopril': Decimal('22.00'),
        'Loperamide': Decimal('45.00'),
        'Loratadine': Decimal('28.00'),
        'Meclizine': Decimal('40.00'),
        'Metformin': Decimal('25.00'),
        'Methimazole': Decimal('75.00'),
        'Metocillin': Decimal('52.00'),
        'Metomet': Decimal('55.00'),
        'Metomycin': Decimal('60.00'),
        'Metonazole': Decimal('65.00'),
        'Metophen': Decimal('50.00'),
        'Metoprofen': Decimal('48.00'),
        'Metostatin': Decimal('75.00'),
        'Metovir': Decimal('68.00'),
        'Miconazole': Decimal('95.00'),
        'Mupirocin': Decimal('110.00'),
        'Naproxen': Decimal('32.00'),
        'Nitrofurantoin': Decimal('55.00'),
        'Nitroglycerin': Decimal('65.00'),
        'Omeprazole': Decimal('75.00'),
        'Oral rehydration salts': Decimal('15.00'),
        'Pegylated interferon alfa-2a': Decimal('500.00'),
        'Pentoxifylline': Decimal('85.00'),
        'Propylthiouracil': Decimal('80.00'),
        'Ranitidine': Decimal('45.00'),
        'Ribavirin': Decimal('180.00'),
        'Rifampin': Decimal('155.00'),
        'Salbutamol': Decimal('40.00'),
        'Salicylic acid': Decimal('50.00'),
        'Sclerotherapy': Decimal('600.00'),
        'Sofosbuvir': Decimal('350.00'),
        'Sumatriptan': Decimal('120.00'),
        'Supportive care': Decimal('100.00'),
        'Tenofovir': Decimal('180.00'),
        'Topical corticosteroids': Decimal('95.00'),
        'Trimethoprim': Decimal('40.00'),
        'Ursodeoxycholic acid': Decimal('140.00'),
    }

    def _build_medicine_list(self, shop):
        """Helper method to build medicine list with default prices and discounts."""
        medicines_in_shop = {m.name: m for m in Medicine.objects.filter(shop=shop, name__in=self.MASTER_MEDICINES)}
        all_medicines = []
        for med_name in self.MASTER_MEDICINES:
            med = medicines_in_shop.get(med_name)
            default_price = self.DEFAULT_PRICES.get(med_name)
            all_medicines.append({
                'name': med_name,
                'default_price': default_price,
                'discount': med.discount if med else Decimal('0'),
                'price': med.price if med else (default_price if default_price else None),
                'quantity': med.quantity if med else None,
                'id': med.id if med else None
            })
        return all_medicines

    def get(self, request, *args, **kwargs):
        try:
            shop = Shop.objects.get(shopkeeper=request.user)
            all_medicines = self._build_medicine_list(shop)
            
            # Pagination logic
            page = int(request.GET.get('page', 1))
            per_page = 20
            total = len(all_medicines)
            start = (page - 1) * per_page
            end = start + per_page
            medicines_page = all_medicines[start:end]
            num_pages = (total + per_page - 1) // per_page
            page_range = list(range(1, num_pages + 1))
            
            return render(request, self.template_name, {
                'medicines': medicines_page,
                'shop': shop,
                'page': page,
                'num_pages': num_pages,
                'page_range': page_range
            })
        except Shop.DoesNotExist:
            return render(request, self.template_name, {'error': 'You do not have a shop assigned. Please contact an admin.'})

    def post(self, request, *args, **kwargs):
        try:
            shop = Shop.objects.get(shopkeeper=request.user)
            
            if 'delete_medicine' in request.POST:
                medicine_id = request.POST.get('medicine_id')
                Medicine.objects.filter(id=medicine_id, shop=shop).delete()
                return redirect('medicine_management')

            if 'update_medicine' in request.POST:
                medicine_id = request.POST.get('medicine_id')
                medicine_name = request.POST.get('medicine_name')
                discount_str = request.POST.get('discount', '0')
                quantity_str = request.POST.get('quantity', '')

                try:
                    discount = Decimal(discount_str) if discount_str else Decimal('0')
                    quantity = int(quantity_str) if quantity_str else None
                except (ValueError, TypeError):
                    return redirect('medicine_management')

                # Clamp discount to 0-100
                discount = max(Decimal('0'), min(Decimal('100'), discount))
                
                default_price = self.DEFAULT_PRICES.get(medicine_name)
                
                if medicine_id and medicine_id != 'None':
                    # Update existing
                    med = Medicine.objects.filter(id=medicine_id, shop=shop).first()
                    if med:
                        med.default_price = default_price
                        med.discount = discount
                        med.quantity = quantity
                        med.save()  # save() will auto-compute price
                else:
                    # Create new
                    if medicine_name and default_price:
                        Medicine.objects.create(
                            shop=shop,
                            name=medicine_name,
                            default_price=default_price,
                            discount=discount,
                            quantity=quantity
                        )
                return redirect('medicine_management')

            if 'apply_bulk_discount' in request.POST:
                bulk_discount_str = request.POST.get('bulk_discount', '0')
                try:
                    bulk_discount = Decimal(bulk_discount_str) if bulk_discount_str else Decimal('0')
                except (ValueError, TypeError):
                    return redirect('medicine_management')

                # Clamp to 0-100
                bulk_discount = max(Decimal('0'), min(Decimal('100'), bulk_discount))

                # Apply to all medicines
                for med_name in self.MASTER_MEDICINES:
                    default_price = self.DEFAULT_PRICES.get(med_name)
                    if default_price:
                        med, created = Medicine.objects.get_or_create(
                            shop=shop,
                            name=med_name,
                            defaults={'default_price': default_price, 'discount': bulk_discount}
                        )
                        if not created:
                            med.default_price = default_price
                            med.discount = bulk_discount
                            med.save()  # save() will auto-compute price
                
                return redirect('medicine_management')

        except Shop.DoesNotExist:
            return render(request, self.template_name, {'error': 'You do not have a shop assigned.'})

        return redirect('medicine_management')

class ToggleShopStatusView(LoginRequiredMixin, ShopkeeperRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            shop = Shop.objects.get(shopkeeper=request.user)
            shop.is_open = not shop.is_open
            shop.save()
        except Shop.DoesNotExist:
            pass
        return redirect('medicine_management')

class DiseasePredictionView(LoginRequiredMixin, View):
    login_url = '/'
    template_name = 'predict_disease.html'
    model = None
    vectorizer = None
    medicine_mapping = None

    @classmethod
    def load_ml_models(cls):
        if cls.model is None:
            model_path = os.path.join(settings.BASE_DIR, 'ml_model', 'disease_predictor.pkl')
            vectorizer_path = os.path.join(settings.BASE_DIR, 'ml_model', 'tfidf_vectorizer.pkl')
            medicine_mapping_path = os.path.join(settings.BASE_DIR, 'Dataset', 'disease_medicine_mapping.csv')
            try:
                cls.model = joblib.load(model_path)
                cls.vectorizer = joblib.load(vectorizer_path)
                cls.medicine_mapping = pd.read_csv(medicine_mapping_path)
            except FileNotFoundError:
                cls.model = None
                cls.vectorizer = None
                cls.medicine_mapping = None

    def dispatch(self, *args, **kwargs):
        self.load_ml_models()
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.model is None or self.vectorizer is None or self.medicine_mapping is None:
            return render(request, self.template_name, {'error': 'Machine learning model not found. Please contact an administrator.'})
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        if self.model is None or self.vectorizer is None or self.medicine_mapping is None:
            return render(request, self.template_name, {'error': 'Machine learning model not found. Please contact an administrator.'})

        symptoms = request.POST.get('symptoms')
        if not symptoms:
            return render(request, self.template_name, {'error': 'Please enter your symptoms.'})

        try:
            input_vector = self.vectorizer.transform([symptoms])
            prediction = self.model.predict(input_vector)[0]
            medicine_series = self.medicine_mapping[self.medicine_mapping['disease'] == prediction]['medicine']
            medicine = medicine_series.iloc[0] if not medicine_series.empty else 'Consult a doctor for medicine.'
            context = {'prediction': prediction, 'symptoms': symptoms, 'medicine': medicine}
        except Exception as e:
            context = {'error': f'An error occurred during prediction: {e}'}
        
        return render(request, self.template_name, context)
