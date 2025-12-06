import requests
import json
from datetime import datetime, date, timedelta


def scrape_silver(start_date: str = None, end_date: str = None) -> list:
    # 1) 날짜 범위 설정
    today = date.today()
    if end_date:
        try:
            end_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            end_obj = today
    else:
        end_obj = today

    if start_date:
        try:
            start_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            start_obj = end_obj - timedelta(days=365 * 3)
    else:
        start_obj = end_obj - timedelta(days=365 * 3)

    # 2) API 요청
    base_url = "https://irena111.cafe24.com/api/custom/kgs_chart.php"
    params = {
        "startDate": start_obj.strftime("%Y-%m-%d"),
        "endDate": end_obj.strftime("%Y-%m-%d"),
        "mode": "silver",
    }
    headers = {"User-Agent": "Mozilla/5.0 (compatible; SilverCrawler/1.0)"}

    try:
        resp = requests.get(base_url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"[scrape_silver] HTTP error: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"[scrape_silver] JSON decode error: {e}")
        return []

    # 3) 시세 정리 
    results = []
    if isinstance(data.get("sale"), list):
        for item in data["sale"]:
            if not isinstance(item, dict):
                continue
            x = item.get("x")  
            y = item.get("y")  
            try:
                dt = datetime.fromtimestamp(int(x) / 1000)
                date_str = dt.strftime("%Y-%m-%d")
                price_don = int(y)
                price_per_gram = round(price_don / 3.75)
                results.append({"date": date_str, "price": price_per_gram})
            except (TypeError, ValueError):
                continue
    else:
        print(
            f"[scrape_silver] Unexpected response format for 'sale': {data.get('sale')}"
        )

    # 4) 날짜순 정렬 및 중복 제거
    unique = {}
    for rec in results:
        unique[rec["date"]] = rec["price"]
    final_list = [{"date": d, "price": unique[d]} for d in sorted(unique.keys())]

    return final_list
