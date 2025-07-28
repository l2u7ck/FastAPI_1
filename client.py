import asyncio
import httpx

params = [
    {"title": "Кулинария", "description": "Рецепты", "cost": 1000, "owner": "Stiv"},
    {"title": "Машины", "description": "Супер тачки", "cost": 2000, "owner": "Bob"}
]

update_params = [
    {"title": "Роботы", "description": "механизмы"}
]


async def main():
    async with httpx.AsyncClient() as client:
        # Параллельное выполнение POST-запросов
        res_post = [client.post("http://localhost:8000/announcement", json=param) for param in params]
        responses = await asyncio.gather(*res_post)
        post_results = [resp.json() for resp in responses]

        # Выполняем PATCH-запрос
        patch_result = await client.patch("http://localhost:8000/announcement/2", json=update_params[0])
        patch_result = patch_result.json()

        # Выполняем GET_ID-запрос
        get_id_result = await client.get("http://localhost:8000/announcement/1")
        get_id_result = get_id_result.json()

        # Выполняем GET_PARAMS-запрос
        get_params_result = await client.get("http://localhost:8000/announcement?cost=1000")
        get_params_result = get_params_result.json()

        # Выполняем DELETE-запрос
        delete_result = await client.delete("http://localhost:8000/announcement/1")
        delete_result = delete_result.json()

        # Распечатаем результаты
        print("POST:", post_results)
        print("PATCH:", patch_result)
        print("GET_ID:", get_id_result)
        print("GET_PARAMS:", get_params_result)
        print("DELETE:", delete_result)


if __name__ == "__main__":
    asyncio.run(main())
