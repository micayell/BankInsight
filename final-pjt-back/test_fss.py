
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'final_pjt.settings')
django.setup()

from financial_products.services import save_deposit_products
res = save_deposit_products()
print(f'save_deposit_products result: {res}')

from financial_products.models import DepositProduct
print(f'Total deposits in DB: {DepositProduct.objects.count()}')

