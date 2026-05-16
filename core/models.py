from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from geopy.geocoders import Nominatim

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('shopkeeper', 'Shopkeeper'),
        ('client', 'Client'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')

class Shop(models.Model):
    shopkeeper = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'shopkeeper'})
    name = models.CharField(max_length=255)
    address = models.TextField()
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(null=True, blank=True)
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.address and (not self.latitude or not self.longitude):
            geolocator = Nominatim(user_agent="meditrack_app")
            try:
                location = geolocator.geocode(self.address)
                if location:
                    self.latitude = location.latitude
                    self.longitude = location.longitude
            except Exception as e:
                # Handle potential geocoding errors, e.g., network issues
                print(f"Geocoding error: {e}")
        super().save(*args, **kwargs)

class Medicine(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='medicines')
    name = models.CharField(max_length=255)
    default_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Immutable default price loaded from master data.'
    )
    discount = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text='Discount percentage (0-100).'
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Effective (discounted) price shown to clients.'
    )
    quantity = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def discounted_price(self):
        """Calculate discounted price from default_price and discount percentage."""
        if self.default_price is not None and self.discount is not None:
            from decimal import Decimal
            return round(self.default_price * (Decimal('1') - self.discount / Decimal('100')), 2)
        return self.default_price

    def save(self, *args, **kwargs):
        """Auto-compute effective price from default_price and discount before saving."""
        from core.constants import DEFAULT_PRICES
        
        # Load default price from master data if medicine name matches
        master_default = DEFAULT_PRICES.get(self.name)
        if master_default is not None:
            from decimal import Decimal
            self.default_price = Decimal(str(master_default))
        
        # Compute effective price from default_price and discount
        if self.default_price is not None and self.discount is not None:
            from decimal import Decimal
            self.price = round(
                self.default_price * (Decimal('1') - self.discount / Decimal('100')), 2
            )
        
        super().save(*args, **kwargs)



# Create your models here.
