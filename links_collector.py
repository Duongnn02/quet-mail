import requests
import json
import pycountry
import concurrent.futures

# Базовый URL для Facebook Ad Library API
BASE_URL = "https://graph.facebook.com/v17.0/ads_archive"

# Установите свой ключ API Facebook здесь
API_KEY = "EAAWc1nqCNvYBOxwE6khcZBdYmv6GxVSAL2uCmQFGQ0wopliGHHJKFpm86oZBnkzwRIr8A6bzhLSbEuSPmU3tQFhLS3ecfVfBrlG4NgDuXCoJbyT2n7c86w7ZBrf8CYdFxk4qMoJHPH8ZCkxe9EocZCejpxkVOZA5MydXcto4fKmvLT2MysKmQwQ7KAtLsxLnaFMY0ZCZA4zdxPb4ImuabUDhPZApErDNhG1mZChpAZD"

# Список стран в формате Alpha-2
countries_alpha_2 = ["MC", "LI", "CH", "LU", "SG", "IE", "NO", "US", "QA", "IS", "DK", "AU", "SE", "NL", "AT", "DE", "HK", "FI", "CA", "BE", "OM", "AE", "GB", "KW", "FR", "IL", "JP", "BH", "IT", "MT", "CY", "NZ", "KR", "ES", "TW", "KZ", "PR", "BR", "SA", "AR", "CL", "VE", "MX", "UY", "MY", "RU", "PL", "CN", "TR", "ZA"]

seen_pages = set()
ad_counter = 0

def fetch_country_ads(country):
    global ad_counter  # We use the global keyword to modify the global variable inside a function
    ad_links = []
    # Получаем полное название страны по ее коду Alpha-2
    country_name = pycountry.countries.get(alpha_2=country).name

    # Параметры запроса
    params = {
        "search_terms": "shop",
        "ad_reached_countries": [country],
        "access_token": API_KEY,
    }

    # Отправьте GET-запрос
    response = requests.get(BASE_URL, params=params)

    # Если запрос был успешным, выведите результат
    if response.status_code == 200:
        data = response.json()

        ad_links = [(ad.get('page_name', None), ad['ad_snapshot_url']) for ad in data['data'] if ad.get('page_name', None) not in seen_pages]

        seen_pages.update([ad[0] for ad in ad_links if ad[0]])

        # Обработка пагинации
        while 'paging' in data and 'next' in data['paging']:
            next_url = data['paging']['next']
            response = requests.get(next_url)

            if response.status_code == 200:
                data = response.json()
                new_ad_links = [(ad.get('page_name', None), ad['ad_snapshot_url']) for ad in data['data'] if ad.get('page_name', None) not in seen_pages]
                seen_pages.update([ad[0] for ad in new_ad_links if ad[0]])
                ad_links += new_ad_links
            else:
                break

        for page_name, link in ad_links:
            if page_name:
                ad_counter += 1
                print(f"Ссылка {ad_counter}: {link}")

        print(f"Сохранено {len(ad_links)} ссылок на объявления для страны {country_name}")

    else:
        print(json.dumps(response.json(), indent=1, ensure_ascii=False))
    
    return [(link, country_name, page_name) for page_name, link in ad_links if page_name]

with concurrent.futures.ThreadPoolExecutor() as executor:
    all_ad_links = executor.map(fetch_country_ads, countries_alpha_2)
    # Flatten the list of lists
    all_ad_links = [item for sublist in all_ad_links for item in sublist]

with open('ad_links.txt', 'w') as f:
    for link, country_name, page_name in all_ad_links:
        f.write("%s, %s, %s\n" % (link, country_name, page_name))
