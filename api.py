import aiohttp

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