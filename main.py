import requests
import random
import telebot

from config import GOOGLE_API_KEY, search_engine_id, BOT_TOKEN, TENOR_API_KEY


bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["markiplier", "search", "image", "searchgif", "gif"])
def send_markiplier(message):
    try:
        if message.text.strip() == "/markiplier":
            chat_id = message.chat.id
            bot.send_message(chat_id, "Markiplier coming right up!")

            image_url = get_picture("markiplier")

            bot.send_photo(chat_id, image_url)

        elif message.text.strip() == "/image":
            chat_id = message.chat.id
            bot.send_message(chat_id, f"Image of {get_query()} coming right up!")

            image_url = get_picture(get_query())

            bot.send_photo(chat_id, image_url)

        elif message.text.strip() == "/gif":
            chat_id = message.chat.id
            bot.send_message(chat_id, f"Gif of {get_query_gif()} coming right up!")

            image_url = get_gif(get_query_gif())

            bot.send_animation(chat_id, image_url)

        elif "/search " in message.text:
            print(message.text)

            query = " ".join(message.text.split()[1:])

            set_query(query)

            bot.send_message(message.chat.id, f"Query '{query}' set!")

        elif "/searchgif " in message.text:
            print(message.text)

            query = " ".join(message.text.split()[1:])

            set_query_gif(query)

            bot.send_message(message.chat.id, f"Query '{query}' set!")

    except Exception as e:
        print("CRITICAL ERROR:", e)
        try:
            bot.send_message(message.chat.id, "Error: " + str(e))

        except Exception as e:
            print("COULD NOT SEND ERROR MESSAGE!", e)

def get_offset(query):
    try:
        with open(f"offset_{query}.txt", "r") as f:
            offset = f.read().strip()
            return int(offset)

    except Exception:
        with open(f"offset_{query}.txt", "w") as f:
            f.write("0")
            return 0

def get_offset_gif(query):
    try:
        with open(f"offset_gif_{query}.txt", "r") as f:
            offset = f.read().strip()
            return int(offset)

    except Exception:
        with open(f"offset_gif_{query}.txt", "w") as f:
            f.write("0")
            return 0

def get_query():
    try:
        with open("query.txt", "r") as f:
            query = f.read().strip()
            if query == "":
                set_query("markiplier")
                return "markiplier"
            return query

    except Exception:
        with open("query.txt", "w") as f:
            f.write("markiplier")
            return "markiplier"

def get_query_gif():
    try:
        with open("query_gif.txt", "r") as f:
            query = f.read().strip()
            print("READ " + query)
            if query == "":
                set_query_gif("markiplier")
                return "markiplier"
            return query

    except Exception:
        print("Exception!")
        with open("query_gif.txt", "w") as f:
            f.write("markiplier")
            return "markiplier"

def set_query(new_query):
    with open("query.txt", "w") as f:
        f.write(new_query)

def set_query_gif(new_query):
    print("SET GIF TO " + new_query)
    with open("query_gif.txt", "w") as f:
        f.write(new_query)
        

def increase_offset(query):
    cur_offset = get_offset(query)
    with open(f"offset_{query}.txt", "w") as f:
        f.write(str(cur_offset + 10))

def increase_offset_gif(query):
    cur_offset = get_offset_gif(query)
    with open(f"offset_gif_{query}.txt", "w") as f:
        f.write(str(cur_offset + 2))


def get_picture(query):
    attempts = 5
    for i in range(attempts):
        current_offset = get_offset(query)

        res = try_to_get_picture(current_offset, query)

        if "error" in res:
            print("Error, retrying", res["error"])
            increase_offset(query)
        else:
            return res

def get_gif(query):
    attempts = 5
    for i in range(attempts):
        current_offset = get_offset_gif(query)

        res = try_to_get_gif(current_offset, query)

        if "error" in res:
            print("Error, retrying", res["error"])
            increase_offset_gif(query)
        else:
            return res


def try_to_get_picture(current_offset=0, custom_query=None):
    if custom_query is None:
        query = get_query()
    else:
        query = custom_query

    url = f"https://customsearch.googleapis.com/customsearch/v1?cx={search_engine_id}&q={query}&searchType=image&key={GOOGLE_API_KEY}&start={current_offset}"

    res = requests.get(url)

    if res.status_code != 200:
        return {"error": res}

    json = res.json()

    if "items" not in json:
        return {"error": json}

    try:
        with open(f"used_links_{query}.txt", "r") as f:
            used_links = list(map(str.strip, f.readlines()))
    except FileNotFoundError:
        with open(f"used_links_{query}.txt", "w") as f:
            used_links = []
            pass

    items = json["items"]

    item_options = [item["link"] for item in items]

    random.shuffle(item_options)

    for random_link in item_options:
        print(random_link)
        if "tiktok" in random_link:
            continue
        if random_link not in used_links:
            print("Writing to used!")
            print("Done!")
            with open(f"used_links_{query}.txt", "a") as f:
                f.write(random_link + "\n")
            return random_link
        else:
            print("Link already used...")
            continue
    return {"error": "all links used"}


def try_to_get_gif(current_offset=0, custom_query=None):
    if custom_query is None:
        query = get_query_gif()
    else:
        query = custom_query

    url = f"https://tenor.googleapis.com/v2/search?key={TENOR_API_KEY}&q={query}&pos={current_offset}&media_filter=gif&limit=10"
    print(url)
    res = requests.get(url)
    # print(res.json())

    if res.status_code != 200:
        print("CODE NOT 200")
        return {"error": res}

    json = res.json()

    if "results" not in json:
        return {"error": json}

    if len(json["results"]) == 0:
        return {"error": json}

    try:
        with open(f"used_links_gif_{query}.txt", "r") as f:
            used_links = list(map(str.strip, f.readlines()))
    except FileNotFoundError:
        with open(f"used_links_gif_{query}.txt", "w") as f:
            used_links = []

    items = json["results"]
    item_options = [item["media_formats"]["gif"]["url"] for item in items]

    print("ITEMS:")
    print(item_options)

    random.shuffle(item_options)

    for random_link in item_options:
        # print(random_link)

        if random_link not in used_links:
            print("Writing to used!")
            print("Done!")
            print(f"Sending {random_link}")
            with open(f"used_links_gif_{query}.txt", "a") as f:
                f.write(random_link + "\n")
            return random_link
        else:
            print("Link already used...")
            continue
    return {"error": "all links used"}


bot.infinity_polling()
