import asyncio
import httpx

# Данные для отправки POST-запросов
params = [
    {
        "title": "Книга 'Искусство программирования'",
        "description": "Классический учебник",
        "cost": 1500,
        "owner": "Donald Knuth"
    },
    {
        "title": "JavaScript: Подробное руководство",
        "description": "Справочник по JavaScript",
        "cost": 2000,
        "owner": "David Flanagan"
    }
]

# Данные для PATCH-запроса (частичного обновления)
update_params = [
    {
        "title": "Python Programming Guide",
        "description": "Guide to Python programming language."
    }
]

# Дополнительные тесты: поиск по разным параметрам
search_queries = [
    "http://localhost:8000/advertisement?title=Book&cost=1500",          # Поиск по названию и стоимости
    "http://localhost:8000/advertisement?minCost=1000&maxCost=2000",     # Диапазон цен
    "http://localhost:8000/advertisement?owner=Knuth",                   # Поиск по владельцу
    "http://localhost:8000/advertisement?createDate=2023-09-01"           # Поиск по дате публикации
]


async def main():
    async with httpx.AsyncClient() as client:
        # Отправляем POST-запросы параллельно
        post_tasks = [client.post("http://localhost:8000/advertisement", json=param) for param in params]
        posts_responses = await asyncio.gather(*post_tasks)
        post_results = [response.json() for response in posts_responses]
        print("\nPOST requests:")
        print(post_results)

        # Обновляем запись (PATCH-запрос)
        patch_response = await client.patch("http://localhost:8000/advertisement/2", json=update_params[0])
        patch_result = patch_response.json()
        print("\nPATCH request:")
        print(patch_result)

        # Тестирование разных видов поисковых запросов
        search_tasks = [client.get(url) for url in search_queries]
        search_responses = await asyncio.gather(*search_tasks)
        search_results = [response.json() for response in search_responses]
        print("\nSEARCH queries:")
        for i, result in enumerate(search_results):
            print(f"{i+1}. Search '{search_queries[i]}':")
            print(result)

        # Получаем одно конкретное объявление (GET-ID)
        get_id_response = await client.get("http://localhost:8000/advertisement/1")
        get_id_result = get_id_response.json()
        print("\nGET by ID:")
        print(get_id_result)

        # Удаляем объявление (DELETE-запрос)
        delete_response = await client.delete("http://localhost:8000/advertisement/1")
        delete_result = delete_response.json()
        print("\nDELETE request:")
        print(delete_result)

if __name__ == "__main__":
    asyncio.run(main())