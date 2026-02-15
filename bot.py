import requests
import time
import json
from datetime import datetime

TOKEN = "8573101517:AAEcr0TdueHQTXB8Kg7_yKdfIQuyUdpX8Vo"
CHAT_ID = 306895822

URL = "https://www.cian.ru/cat.php?acontext=Новомосковский%7Cмой+адрес+на+клинской%7Cрумянцево-парк&currency=2&deal_type=sale&demolished_in_moscow_programm=0&district%5B0%5D=1&district%5B1%5D=5&district%5B2%5D=7&district%5B3%5D=9&district%5B4%5D=10&district%5B5%5D=11&electronic_trading=2&engine_version=2&flat_share=2&house_material%5B0%5D=1&house_material%5B1%5D=2&house_material%5B2%5D=4&house_material%5B3%5D=8&maxprice=26000000&maxtarea=80&min_house_year=2020&minprice=22000000&mintarea=72&object_type%5B0%5D=1&offer_type=flat&only_flat=1&repair%5B0%5D=1&room3=1"

CHECK_INTERVAL = 43200  # 12 часов (в секундах)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

SENT_FILE = "sent_flats.json"


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
    }
    requests.post(url, data=data)


def load_sent():
    try:
        with open(SENT_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()


def save_sent(sent):
    with open(SENT_FILE, "w", encoding="utf-8") as f:
        json.dump(list(sent), f, ensure_ascii=False, indent=2)


def get_flats():
    response = requests.get(URL, headers=HEADERS)
    html = response.text

    items = []

    blocks = html.split('data-name="LinkArea"')

    for block in blocks[1:]:
        try:
            link_part = block.split('href="')[1].split('"')[0]
            link = "https://www.cian.ru" + link_part

            items.append(link)
        except:
            pass

    return items


def main():
    sent = load_sent()
    send_telegram("🏠 Бот запущен. Начинаю мониторинг новых квартир на ЦИАН.")

    while True:
        try:
            flats = get_flats()

            for link in flats:
                if link in sent:
                    continue

                message = (
                    f"🏠 Новое объявление на ЦИАН\n"
                    f"🔗 {link}\n"
                    f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}"
                )
                send_telegram(message)
                sent.add(link)
                save_sent(sent)

        except Exception as e:
            send_telegram(f"⚠️ Ошибка бота: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
