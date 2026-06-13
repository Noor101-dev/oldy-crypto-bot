import os
import json
import random
import requests

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = "-1003610983854"
OFFSET_FILE = "offset.txt"
API = f"https://api.telegram.org/bot{TOKEN}"

MEMES = [
    {"url": "https://i.imgflip.com/65939r.jpg", "caption": "Jab BTC 100k pe jaaye 😂🚀\n#HODL #OldyCrypto"},
    {"url": "https://i.imgflip.com/4t0m5.jpg",  "caption": "Mere portfolio ka haal 💀📉\n#Rekt #CryptoLife"},
    {"url": "https://i.imgflip.com/5c7lwq.jpg", "caption": "Buy high sell low 🤡\n#CryptoTrader101"},
    {"url": "https://i.imgflip.com/3oevdk.jpg", "caption": "When you check portfolio at 3am 👀\n#NoSleep"},
    {"url": "https://i.imgflip.com/2zo1ki.jpg", "caption": "Altcoin investors be like 😭\n#Hopium"},
    {"url": "https://i.imgflip.com/26am.jpg",   "caption": "Sab bole DYOR koi nahi karta 🤦\n#DYOR"},
    {"url": "https://i.imgflip.com/1bhk.jpg",   "caption": "Me explaining crypto to my parents 😅"},
    {"url": "https://i.imgflip.com/2wifvo.jpg", "caption": "Diamond hands 💎🙌 Paper hands 🧻\n#HODL"},
]

QUIZ = [
    {"q": "Bitcoin ka maximum supply kitna hai?",    "opts": ["21 Million", "100 Million", "18 Million", "Unlimited"],       "ans": 0, "exp": "Bitcoin ka max supply sirf 21 million hai! 🎯"},
    {"q": "Ethereum kis cheez ke liye famous hai?",  "opts": ["Smart Contracts", "Only Payments", "Mining Gold", "Social"],  "ans": 0, "exp": "Ethereum smart contracts ke liye! 💡"},
    {"q": "What does HODL stand for?",              "opts": ["Hold On for Dear Life", "High Order Data", "Hash Output", "None"], "ans": 0, "exp": "HODL = Hold On for Dear Life! 😂"},
    {"q": "Satoshi Nakamoto ne Bitcoin kab banaya?", "opts": ["2009", "2005", "2012", "2015"],                                "ans": 0, "exp": "Bitcoin 2009 mein launch hua! 🎂"},
    {"q": "DeFi ka full form kya hai?",             "opts": ["Decentralized Finance", "Digital Finance", "Defined", "Default"], "ans": 0, "exp": "DeFi = Decentralized Finance! 🏦"},
    {"q": "NFT ka full form kya hai?",              "opts": ["Non-Fungible Token", "New Finance Token", "Network Fee", "Node"], "ans": 0, "exp": "NFT = Non-Fungible Token! 🎨"},
    {"q": "Crypto mein whale kaun hota hai?",       "opts": ["Large holder", "A coin type", "Mining rig", "Exchange"],       "ans": 0, "exp": "Whales = log jinke paas bahut saara crypto! 🐋"},
    {"q": "Gas fees kahan pay hoti hai?",           "opts": ["Ethereum network", "Bitcoin", "Binance only", "All chains"],   "ans": 0, "exp": "Gas fees Ethereum transactions ke liye ⛽"},
]

WELCOMES = [
    lambda n: f"🎉 Welcome to OLDY CRYPTO, {n}!\n\n💎 Yahan hum sab HODLers hain\n🚀 Moon tak saath chalenge\n\n✅ No spam  ✅ Respect all  ✅ DYOR\n\nType /meme /quiz /price /profile 🔥",
    lambda n: f"👋 Aagaya {n} bhai!\n\n🔥 OLDY CRYPTO mein swagat hai!\n\n/meme 😂  /quiz 🧠  /price 📊  /profile 👤\n\nDiamond hands rakho! 💎🙌",
    lambda n: f"🌟 {n} joined OLDY CRYPTO family!\n\n₿ Sab ka swagat hai!\n\n📊 /price  🧠 /quiz  😂 /meme  🏆 /leaderboard\n\nLFG! 🚀",
]

def send_message(text, chat_id=CHAT_ID):
    requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": text})

def send_photo(url, caption, chat_id=CHAT_ID):
    r = requests.post(f"{API}/sendPhoto", json={"chat_id": chat_id, "photo": url, "caption": caption})
    if not r.json().get("ok"):
        send_message(f"{caption}\n{url}", chat_id)

def send_poll(question, options, correct_idx, explanation, chat_id=CHAT_ID):
    requests.post(f"{API}/sendPoll", json={
        "chat_id": chat_id, "question": question, "options": options,
        "type": "quiz", "correct_option_id": correct_idx,
        "explanation": explanation, "is_anonymous": False
    })

def get_updates(offset):
    r = requests.get(f"{API}/getUpdates", params={"offset": offset, "limit": 50, "timeout": 0})
    return r.json().get("result", [])

def get_prices():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin,ethereum,binancecoin,solana", "vs_currencies": "usd", "include_24hr_change": "true"}, timeout=10)
        d = r.json()
        lines = []
        for sym, coin_id in [("BTC","bitcoin"),("ETH","ethereum"),("BNB","binancecoin"),("SOL","solana")]:
            info = d.get(coin_id, {})
            price = info.get("usd", "N/A")
            change = info.get("usd_24h_change", 0)
            emoji = "🟢" if change >= 0 else "🔴"
            lines.append(f"{emoji} {sym}: ${price:,.0f} ({change:+.2f}%)")
        return "\n".join(lines)
    except:
        return "🟠 BTC: ~$95,000\n🔵 ETH: ~$3,400\n🟡 BNB: ~$580\n🟣 SOL: ~$170"

def load_lb():
    try:
        with open("leaderboard.json") as f:
            return json.load(f)
    except:
        return {}

def save_lb(lb):
    with open("leaderboard.json", "w") as f:
        json.dump(lb, f)

def track_user(lb, user_id, username, first_name):
    uid = str(user_id)
    if uid not in lb:
        lb[uid] = {"username": username, "name": first_name, "count": 0}
    lb[uid]["count"] += 1
    lb[uid]["username"] = username or lb[uid].get("username", "")
    return lb

def load_offset():
    try:
        with open(OFFSET_FILE) as f:
            return int(f.read().strip())
    except:
        return 946233168

def save_offset(offset):
    with open(OFFSET_FILE, "w") as f:
        f.write(str(offset))

def handle_start():
    send_message("🤖 Bot is ACTIVE!\n\n⚡ Commands:\n/meme 😂 — Random meme\n/quiz 🧠 — Crypto quiz\n/profile 👤 — Your info\n/price 📊 — Live prices\n/leaderboard 🏆 — Top members\n\nPowered by @Nooraspal 🔥\nLFG! 🚀")

def handle_meme():
    m = random.choice(MEMES)
    send_photo(m["url"], m["caption"])

def handle_quiz():
    q = random.choice(QUIZ)
    send_poll(q["q"], q["opts"], q["ans"], q["exp"])

def handle_profile(user_id, username, first_name, last_name):
    lb = load_lb()
    name = " ".join(filter(None, [first_name, last_name])) or "Unknown"
    msgs = lb.get(str(user_id), {}).get("count", 0)
    rank = sum(1 for u in lb.values() if u["count"] > msgs) + 1
    send_message(f"👤 User Profile\n━━━━━━━━━━━━━━\n🏷 Name: {name}\n📛 Username: @{username or 'no_username'}\n🆔 User ID: {user_id}\n💬 Messages: {msgs}\n🏆 Rank: #{rank} in OLDY CRYPTO\n━━━━━━━━━━━━━━\n💎 Keep HODLing! 🚀")

def handle_price():
    from datetime import datetime
    prices = get_prices()
    send_message(f"📊 Live Crypto Prices\n━━━━━━━━━━━━━━\n{prices}\n━━━━━━━━━━━━━━\n⏰ {datetime.now().strftime('%H:%M:%S')}\nSource: CoinGecko")

def handle_leaderboard():
    lb = load_lb()
    medals = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    sorted_lb = sorted(lb.items(), key=lambda x: x[1]["count"], reverse=True)[:10]
    lines = [f"{medals[i]} @{u.get('username') or u.get('name','Unknown')} — {u['count']} msgs" for i,(_,u) in enumerate(sorted_lb)] if sorted_lb else ["No activity yet! 💬"]
    send_message("🏆 OLDY CRYPTO Leaderboard\n━━━━━━━━━━━━━━\n" + "\n".join(lines) + "\n━━━━━━━━━━━━━━\n💎 Most active members!")

def handle_welcome(name):
    send_message(random.choice(WELCOMES)(name))

def main():
    offset = load_offset()
    lb = load_lb()
    updates = get_updates(offset)
    for upd in updates:
        offset = max(offset, upd["update_id"] + 1)
        msg = upd.get("message") or upd.get("channel_post")
        if not msg:
            continue
        if str(msg["chat"]["id"]) != CHAT_ID:
            continue
        frm = msg.get("from", {})
        user_id = frm.get("id")
        username = frm.get("username", "")
        first_name = frm.get("first_name", "")
        last_name = frm.get("last_name", "")
        text = msg.get("text", "").strip()
        if user_id:
            lb = track_user(lb, user_id, username, first_name)
        for new_member in msg.get("new_chat_members", []):
            if not new_member.get("is_bot"):
                handle_welcome(new_member.get("first_name") or new_member.get("username") or "Friend")
        cmd = text.split("@")[0].lower()
        if   cmd == "/start":       handle_start()
        elif cmd == "/meme":        handle_meme()
        elif cmd == "/quiz":        handle_quiz()
        elif cmd == "/profile":     handle_profile(user_id, username, first_name, last_name)
        elif cmd == "/price":       handle_price()
        elif cmd == "/leaderboard": handle_leaderboard()
    save_offset(offset)
    save_lb(lb)
    print(f"✅ Processed {len(updates)} updates. Next offset: {offset}")

if __name__ == "__main__":
    main()
