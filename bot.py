import os
import json
import random
import requests
from datetime import datetime, timezone

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = "-1003610983854"
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
    {"q": "Bitcoin ka maximum supply kitna hai?",    "opts": ["21 Million", "100 Million", "18 Million", "Unlimited"],          "ans": 0, "exp": "Bitcoin ka max supply sirf 21 million hai! 🎯"},
    {"q": "Ethereum kis cheez ke liye famous hai?",  "opts": ["Smart Contracts", "Only Payments", "Mining Gold", "Social"],    "ans": 0, "exp": "Ethereum smart contracts ke liye! 💡"},
    {"q": "What does HODL stand for?",              "opts": ["Hold On for Dear Life", "High Order Data", "Hash Output", "None"],"ans": 0, "exp": "HODL = Hold On for Dear Life! 😂"},
    {"q": "Satoshi Nakamoto ne Bitcoin kab banaya?", "opts": ["2009", "2005", "2012", "2015"],                                  "ans": 0, "exp": "Bitcoin 2009 mein launch hua! 🎂"},
    {"q": "DeFi ka full form kya hai?",             "opts": ["Decentralized Finance", "Digital Finance", "Defined", "Default"], "ans": 0, "exp": "DeFi = Decentralized Finance! 🏦"},
    {"q": "NFT ka full form kya hai?",              "opts": ["Non-Fungible Token", "New Finance Token", "Network Fee", "Node"], "ans": 0, "exp": "NFT = Non-Fungible Token! 🎨"},
    {"q": "Crypto mein whale kaun hota hai?",       "opts": ["Large holder", "A coin type", "Mining rig", "Exchange"],         "ans": 0, "exp": "Whales = log jinke paas bahut saara crypto! 🐋"},
    {"q": "Gas fees kahan pay hoti hai?",           "opts": ["Ethereum network", "Bitcoin", "Binance only", "All chains"],     "ans": 0, "exp": "Gas fees Ethereum transactions ke liye ⛽"},
]

WELCOMES = [
    lambda n: f"🎉 Welcome to OLDY CRYPTO, {n}!\n\n💎 Yahan hum sab HODLers hain\n🚀 Moon tak saath chalenge\n\n✅ No spam  ✅ Respect all  ✅ DYOR\n\nType /meme /quiz /price /profile 🔥",
    lambda n: f"👋 Aagaya {n} bhai!\n\n🔥 OLDY CRYPTO mein swagat hai!\n\n/meme 😂  /quiz 🧠  /price 📊  /profile 👤\n\nDiamond hands rakho! 💎🙌",
    lambda n: f"🌟 {n} joined OLDY CRYPTO family!\n\n₿ Sab ka swagat hai!\n\n📊 /price  🧠 /quiz  😂 /meme  🏆 /leaderboard\n\nLFG! 🚀",
]

def send_message(text):
    requests.post(f"{API}/sendMessage", json={"chat_id": CHAT_ID, "text": text})

def send_photo(url, caption):
    r = requests.post(f"{API}/sendPhoto", json={"chat_id": CHAT_ID, "photo": url, "caption": caption})
    if not r.json().get("ok"):
        send_message(f"{caption}\n{url}")

def send_poll(question, options, correct_idx, explanation):
    requests.post(f"{API}/sendPoll", json={
        "chat_id": CHAT_ID, "question": question, "options": options,
        "type": "quiz", "correct_option_id": correct_idx,
        "explanation": explanation, "is_anonymous": False
    })

def get_updates():
    # Get only updates from last 6 minutes (covers the 5-min cron gap + buffer)
    r = requests.get(f"{API}/getUpdates", params={"limit": 100, "timeout": 0, "allowed_updates": ["message"]})
    updates = r.json().get("result", [])
    # Filter to only last 6 minutes
    cutoff = datetime.now(timezone.utc).timestamp() - 360
    recent = [u for u in updates if (u.get("message") or {}).get("date", 0) > cutoff]
    # Acknowledge all updates so they don't repeat
    if updates:
        max_id = max(u["update_id"] for u in updates)
        requests.get(f"{API}/getUpdates", params={"offset": max_id + 1, "limit": 1, "timeout": 0})
    return recent

def get_prices():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin,ethereum,binancecoin,solana", "vs_currencies": "usd", "include_24hr_change": "true"}, timeout=10)
        d = r.json()
        lines = []
        for sym, cid in [("BTC","bitcoin"),("ETH","ethereum"),("BNB","binancecoin"),("SOL","solana")]:
            info = d.get(cid, {})
            price = info.get("usd", 0)
            change = info.get("usd_24h_change", 0)
            emoji = "🟢" if change >= 0 else "🔴"
            lines.append(f"{emoji} {sym}: ${price:,.0f} ({change:+.2f}%)")
        return "\n".join(lines)
    except:
        return "🟠 BTC: ~$95,000\n🔵 ETH: ~$3,400\n🟡 BNB: ~$580\n🟣 SOL: ~$170"

def handle_start():  send_message("🤖 Bot is ACTIVE!\n\n⚡ Commands:\n/meme 😂 — Random meme\n/quiz 🧠 — Crypto quiz\n/profile 👤 — Your info\n/price 📊 — Live prices\n/leaderboard 🏆 — Top members\n\nPowered by @Nooraspal 🔥 LFG! 🚀")
def handle_meme():   m = random.choice(MEMES); send_photo(m["url"], m["caption"])
def handle_quiz():   q = random.choice(QUIZ); send_poll(q["q"], q["opts"], q["ans"], q["exp"])
def handle_price():  send_message(f"📊 Live Crypto Prices\n━━━━━━━━━━━━━━\n{get_prices()}\n━━━━━━━━━━━━━━\n⏰ {datetime.now().strftime('%H:%M:%S')} UTC\nSource: CoinGecko")

def handle_profile(user_id, username, first_name, last_name):
    name = " ".join(filter(None, [first_name, last_name])) or "Unknown"
    send_message(f"👤 User Profile\n━━━━━━━━━━━━━━\n🏷 Name: {name}\n📛 @{username or 'no_username'}\n🆔 ID: {user_id}\n━━━━━━━━━━━━━━\n💎 Keep HODLing! 🚀")

def handle_leaderboard():
    send_message("🏆 OLDY CRYPTO Leaderboard\n━━━━━━━━━━━━━━\nUse /profile to see your rank!\n━━━━━━━━━━━━━━\n💎 Most active members!")

def handle_welcome(name):
    send_message(random.choice(WELCOMES)(name))

def main():
    updates = get_updates()
    print(f"Found {len(updates)} recent updates")
    for upd in updates:
        msg = upd.get("message")
        if not msg: continue
        if str(msg["chat"]["id"]) != CHAT_ID: continue
        frm       = msg.get("from", {})
        user_id   = frm.get("id")
        username  = frm.get("username", "")
        first_name = frm.get("first_name", "")
        last_name  = frm.get("last_name", "")
        text = msg.get("text", "").strip()
        for new_member in msg.get("new_chat_members", []):
            if not new_member.get("is_bot"):
                handle_welcome(new_member.get("first_name") or "Friend")
        cmd = text.split("@")[0].lower()
        print(f"Command: {cmd} from {username or first_name}")
        if   cmd == "/start":        handle_start()
        elif cmd == "/meme":         handle_meme()
        elif cmd == "/quiz":         handle_quiz()
        elif cmd == "/profile":      handle_profile(user_id, username, first_name, last_name)
        elif cmd == "/price":        handle_price()
        elif cmd == "/leaderboard":  handle_leaderboard()
    print("Done!")

if __name__ == "__main__":
    main()
