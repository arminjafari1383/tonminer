from django.contrib import admin
from .models import MiningAccount, Deposit, MiningPosition
admin.site.register(MiningAccount)
admin.site.register(Deposit)
admin.site.register(MiningPosition)
