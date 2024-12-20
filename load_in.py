import aiohttp
import asyncio
import sqlite3

API_BASE_URL = "https://swapi.py4e.com/api"


async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


async def fetch_character_data(character_id):
    character_url = f"{API_BASE_URL}/people/{character_id}/"
    character = await fetch_data(character_url)
    if "detail" in character and character["detail"] == "Not found":
        return None

    # Получаем названия связанных объектов
    async def fetch_names(urls):
        names = []
        for url in urls:
            data = await fetch_data(url)
            names.append(data.get("title") or data.get("name", "Unknown"))
        return ", ".join(names)

    films = await fetch_names(character.get("films", []))
    species = await fetch_names(character.get("species", []))
    starships = await fetch_names(character.get("starships", []))
    vehicles = await fetch_names(character.get("vehicles", []))
    homeworld = (await fetch_data(character["homeworld"])).get("name", "Unknown")

    return {
        "id": character_id,
        "name": character["name"],
        "birth_year": character["birth_year"],
        "eye_color": character["eye_color"],
        "films": films,
        "gender": character["gender"],
        "hair_color": character["hair_color"],
        "height": character["height"],
        "homeworld": homeworld,
        "mass": character["mass"],
        "skin_color": character["skin_color"],
        "species": species,
        "starships": starships,
        "vehicles": vehicles
    }


async def save_to_database(character):
    conn = sqlite3.connect("starwars.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO characters (
        id, name, birth_year, eye_color, films, gender, hair_color, height, 
        homeworld, mass, skin_color, species, starships, vehicles
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        character["id"], character["name"], character["birth_year"], character["eye_color"],
        character["films"], character["gender"], character["hair_color"], character["height"],
        character["homeworld"], character["mass"], character["skin_color"], character["species"],
        character["starships"], character["vehicles"]
    ))
    conn.commit()
    conn.close()


async def load_all_characters():
    tasks = []
    character_id = 1
    while True:
        task = asyncio.create_task(fetch_character_data(character_id))
        tasks.append(task)
        character_id += 1

        # Пакетная обработка каждых 10 персонажей
        if len(tasks) == 10:
            results = await asyncio.gather(*tasks)
            for character in results:
                if character:
                    await save_to_database(character)
                    print(f"Saved character {character['name']} (ID: {character['id']})")
            tasks = []

    # Обработка оставшихся задач
        if tasks:
            results = await asyncio.gather(*tasks)
            for character in results:
                if character:
                    await save_to_database(character)


if __name__ == "__main__":
    asyncio.run(load_all_characters())
