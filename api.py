import aiohttp
from config import API_THEWEATHER

async def get_food_calories(product_name):
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": product_name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 3 
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    products = data.get("products", [])
                    
                    if not products:
                        return None

                    result = {}
                    for i in range(min(len(products), 3)): 
                        product = products[i]
                        nutriments = product.get("nutriments", {})
                        
                        # Собираем данные
                        calories = nutriments.get("energy-kcal_100g") or nutriments.get("energy-kcal")
                        name = product.get("product_name", "Неизвестный продукт")
                        
                        result[str(i + 1)] = {  
                            "name": name, 
                            "calories": calories
                        }
                    return result
                else:
                    print(f"Ошибка API: {response.status}")
        except Exception as e:
            print(f"Ошибка сети: {e}")
    return None


async def get_weather_async(city_name, units='metric'):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city_name,
        'appid': API_THEWEATHER,
        'units': units,
        'lang': 'ru'
    }
    
    # Настройка таймаута для aiohttp
    timeout = aiohttp.ClientTimeout(total=10)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(base_url, params=params) as response:
                
                # Проверка на HTTP ошибки (4xx, 5xx)
                response.raise_for_status()
                
                data = await response.json()
                print(data)

                # Проверка внутренней логики API
                if str(data.get('cod')) != '200':
                    print(f"Ошибка API: {data.get('message', 'Неизвестная ошибка')}") 
                    return None
                
                return data["main"]

    except aiohttp.ClientResponseError as e:
        print(f"HTTP ошибка: {e.status}, сообщение: {e.message}")
        return None
    except aiohttp.ClientError as e:
        print(f"Ошибка сети/запроса: {e}")
        return None
    except ValueError as e:
        print(f"Ошибка при обработке ответа: {e}")
        return None