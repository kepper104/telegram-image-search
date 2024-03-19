import requests
import random
import telebot

from config import GOOGLE_API_KEY, search_engine_id, BOT_TOKEN


bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["markiplier", "search", "image"])
def send_markiplier(message):
    try:
        if message.text == "/markiplier":
            chat_id = message.chat.id
            bot.send_message(chat_id, "Markiplier coming right up!")

            image_url = get_picture("markiplier")

            bot.send_photo(chat_id, image_url)

        elif message.text == "/image":
            chat_id = message.chat.id
            bot.send_message(chat_id, f"Image of {get_query()} coming right up!")

            image_url = get_picture(get_query())

            bot.send_photo(chat_id, image_url)

        elif "/search" in message.text:
            print(message.text)

            query = " ".join(message.text.split()[1:])

            set_query(query)

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


def set_query(new_query):
    with open("query.txt", "w") as f:
        f.write(new_query)


def increase_offset(query):
    cur_offset = get_offset(query)
    with open(f"offset_{query}.txt", "w") as f:
        f.write(str(cur_offset + 10))


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


bot.infinity_polling()
