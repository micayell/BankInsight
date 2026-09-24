
import os
import django
import sys
import io

# Force UTF-8 stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'final_pjt.settings')
django.setup()

import requests
from django.conf import settings

API_KEY = settings.FIN_API_KEY
BASE_URL = 'http://finlife.fss.or.kr/finlifeapi'

url = f'{BASE_URL}/depositProductsSearch.json'
params = {'auth': API_KEY, 'topFinGrpNo': '020000', 'pageNo': 1}
res = requests.get(url, params=params).json()
print(res)

