import discord
from discord.ext import commands
from discord.ext.commands import cooldown, BucketType
import random
import json
import os
import re
import io
from datetime import datetime, timezone, timedelta
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

load_dotenv()
TOKEN = os.getenv("TOKEN")
PREFIX = ","
DATA_FILE = "server_bot_data.json"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

ALLOWED_MENTIONS_NONE = discord.AllowedMentions.none()

# -------------------------
# COLOURS
# -------------------------

COLOUR_NORMAL = discord.Colour.blurple()
COLOUR_RARE = discord.Colour.gold()
COLOUR_STATS = discord.Colour.green()
COLOUR_HUNT = discord.Colour.orange()
COLOUR_SHOP = discord.Colour.purple()
COLOUR_ERROR = discord.Colour.red()
COLOUR_MONEY = discord.Colour.teal()
COLOUR_UTILITY = discord.Colour(0x2B2D31)

# -------------------------
# FLAVOURS / VAPE
# -------------------------

COMMON_FLAVOURS = [
    "Blue Raspberry Ice",
    "Strawberry Kiwi",
    "Watermelon Chill",
    "Mango Peach",
    "Grape Ice",
    "Banana Ice",
    "Lemon Lime",
    "Mint Freeze",
    "Bubblegum",
    "Cherry Fizz",
    "Cola Burst",
    "Pineapple Chill",
    "Apple Ice",
    "Peach Lemonade",
    "Cotton Candy",
    "Vanilla Mist",
    "Orange Soda",
    "Blackcurrant Ice",
    "Kiwi Passionfruit",
    "Coconut Splash",
    "Pink Lemonade",
    "Cherry Cola",
    "Icy Melon",
    "Tropical Punch",
    "Sour Apple",
]

RARE_FLAVOURS = [
    "Dragonfruit Nova",
    "Nebula Mint",
    "Cosmic Cola",
    "Golden Peach Frost",
    "Voidberry Ice",
    "Starlight Lychee",
    "Solar Mango",
    "Phantom Grape",
    "Aurora Apple Ice",
    "Celestial Bubblegum",
]

VAPE_LINES = [
    "takes a fat rip",
    "blows a dramatic cloud",
    "hits the vape like rent is due",
    "takes a suspiciously long puff",
    "fills the room with fog",
    "inhales with dangerous confidence",
    "lets out a huge cloud",
    "takes a smooth drag",
    "absolutely demolishes the vape",
    "puffs like a true cloud chaser",
]

# -------------------------
# PETS / ANIMALS
# -------------------------

VAPE_ANIMALS = [
    {"name": "Nicotine Fox", "coins": (8, 18), "emoji": "🦊"},
    {"name": "Cloud Beaver", "coins": (10, 20), "emoji": "🦫"},
    {"name": "Mint Wolf", "coins": (12, 24), "emoji": "🐺"},
    {"name": "Berry Raccoon", "coins": (9, 17), "emoji": "🦝"},
    {"name": "Fog Rat", "coins": (5, 12), "emoji": "🐀"},
    {"name": "Vapor Hawk", "coins": (14, 28), "emoji": "🦅"},
    {"name": "Smoke Otter", "coins": (11, 21), "emoji": "🦦"},
    {"name": "Cherry Cobra", "coins": (13, 25), "emoji": "🐍"},
    {"name": "Frost Bunny", "coins": (7, 16), "emoji": "🐇"},
    {"name": "Peach Panther", "coins": (15, 27), "emoji": "🐆"},
    {"name": "Lime Gecko", "coins": (8, 15), "emoji": "🦎"},
    {"name": "Bubblegum Bat", "coins": (10, 19), "emoji": "🦇"},
    {"name": "Grape Bear", "coins": (16, 30), "emoji": "🐻"},
    {"name": "Mango Monkey", "coins": (9, 18), "emoji": "🐒"},
    {"name": "Cola Croc", "coins": (14, 26), "emoji": "🐊"},
    {"name": "Mist Boar", "coins": (12, 22), "emoji": "🐗"},
    {"name": "Lemon Lynx", "coins": (13, 23), "emoji": "🐱"},
    {"name": "Cloud Crow", "coins": (9, 17), "emoji": "🐦"},
    {"name": "Kiwi Koala", "coins": (11, 20), "emoji": "🐨"},
    {"name": "Fizzy Ferret", "coins": (10, 18), "emoji": "🦦"},
]

RARE_VAPE_ANIMALS = [
    {"name": "Golden Puff Deer", "coins": (30, 50), "emoji": "🦌"},
    {"name": "Mythic Cloud Panther", "coins": (40, 65), "emoji": "🐆"},
    {"name": "Astral Nic Serpent", "coins": (50, 80), "emoji": "🐉"},
    {"name": "Royal Vapor Lion", "coins": (45, 75), "emoji": "🦁"},
    {"name": "Phantom Mint Owl", "coins": (38, 68), "emoji": "🦉"},
    {"name": "Celestial Puff Whale", "coins": (55, 90), "emoji": "🐋"},
]

PET_TRAITS = {
    "Sneaky": "Boosts rob success a bit.",
    "Lucky": "Boosts daily and crime payouts a bit.",
    "Hunter": "Boosts hunt coins a bit.",
    "Cloudborn": "Boosts rare flavour chance a bit.",
    "Guardian": "Reduces coins stolen from you.",
}

# -------------------------
# SHOP
# -------------------------

SHOP_ITEMS = {
    "rare_coil": {
        "name": "Rare Coil",
        "cost": 180,
        "description": "Slightly improves rare flavour chance.",
    },
    "cloud_tank": {
        "name": "Cloud Tank",
        "cost": 220,
        "description": "Gives extra coins on vape.",
    },
    "hunter_net": {
        "name": "Hunter Net",
        "cost": 160,
        "description": "Gives extra coins on hunt.",
    },
    "tracker_goggles": {
        "name": "Tracker Goggles",
        "cost": 300,
        "description": "Improves rare animal chance.",
    },
    "lucky_charm": {
        "name": "Lucky Charm",
        "cost": 260,
        "description": "Improves daily and crime rewards.",
    },
    "lockpick_set": {
        "name": "Lockpick Set",
        "cost": 280,
        "description": "Improves rob success.",
    },
    "smoke_bomb": {
        "name": "Smoke Bomb",
        "cost": 330,
        "description": "Reduces harsh crime failures.",
    },
    "crime_mask": {
        "name": "Crime Mask",
        "cost": 360,
        "description": "Improves rob and crime rewards.",
    },
    "bodyguard": {
        "name": "Bodyguard",
        "cost": 420,
        "description": "Reduces coins stolen from you.",
    },
    "vault": {
        "name": "Pocket Vault",
        "cost": 700,
        "description": "Strong protection from rob attempts.",
    },
    "pet_tag": {
        "name": "Pet Tag",
        "cost": 140,
        "description": "Lets you rename pets.",
    },
    "feed_bowl": {
        "name": "Feed Bowl",
        "cost": 150,
        "description": "Lets you feed pets with flavours.",
    },
}

# -------------------------
# QUESTS
# -------------------------

QUEST_TEMPLATES = [
    {"id": "vape5", "name": "Cloud Warmup", "type": "vape", "goal": 5, "reward": 100},
    {"id": "hunt3", "name": "Animal Tracker", "type": "hunt", "goal": 3, "reward": 120},
    {"id": "crime2", "name": "Petty Criminal", "type": "crime", "goal": 2, "reward": 130},
    {"id": "daily1", "name": "Clock In", "type": "daily", "goal": 1, "reward": 90},
    {"id": "feed2", "name": "Caretaker", "type": "feed", "goal": 2, "reward": 110},
    {"id": "rare1", "name": "Lucky Pull", "type": "rare", "goal": 1, "reward": 140},
    {"id": "rob1", "name": "Sticky Fingers", "type": "rob_success", "goal": 1, "reward": 180},
]

# -------------------------
# RANKS
# -------------------------

RANKS = [
    (0, "😮‍💨 Fresh Lungs"),
    (25, "💨 Casual Puffer"),
    (75, "🌫️ Cloud Chaser"),
    (150, "🌁 Fog Bringer"),
    (300, "⚔️ Nicotine Knight"),
    (500, "👹 Vape Goblin"),
    (800, "🛡️ Mist Warlord"),
    (1200, "👑 Lord of the Clouds"),
]

# -------------------------
# RUNTIME CACHE
# -------------------------

deleted_messages = {}

# -------------------------
# DATA HELPERS
# -------------------------

def utc_now():
    return datetime.now(timezone.utc)

def today_str():
    return utc_now().date().isoformat()

def now_iso():
    return utc_now().isoformat()

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def default_user():
    return {
        "coins": 0,
        "total_hits": 0,
        "rare_hits": 0,
        "last_flavour": None,
        "flavour_counts": {},
        "flavour_inventory": {},
        "streak": 0,
        "best_streak": 0,
        "last_vape_date": None,
        "last_daily_claim": None,
        "daily_streak": 0,
        "hunt_count": 0,
        "pets": [],
        "next_pet_id": 1,
        "inventory": {},
        "quotes_saved": 0,
        "quests": {
            "date": "",
            "active": []
        }
    }

def default_guild():
    return {
        "quotes": []
    }

def ensure_root(data):
    if "_guilds" not in data:
        data["_guilds"] = {}
    return data

def get_guild_record(data, guild_id: int):
    ensure_root(data)
    gid = str(guild_id)
    if gid not in data["_guilds"]:
        data["_guilds"][gid] = default_guild()
    return data["_guilds"][gid]

def get_user_record(data, user_id: int):
    uid = str(user_id)
    if uid not in data:
        data[uid] = default_user()
    return data[uid]

def add_item(user_record, item_key, amount=1):
    user_record["inventory"][item_key] = user_record["inventory"].get(item_key, 0) + amount

def has_item(user_record, item_key):
    return user_record["inventory"].get(item_key, 0) > 0

def get_rank(total_hits: int):
    current = RANKS[0][1]
    for hits, name in RANKS:
        if total_hits >= hits:
            current = name
        else:
            break
    return current

def get_next_rank(total_hits: int):
    for hits, name in RANKS:
        if total_hits < hits:
            return hits, name
    return None, None

def update_vape_streak(user_record):
    today = utc_now().date()
    last_date_iso = user_record.get("last_vape_date")

    if last_date_iso is None:
        user_record["streak"] = 1
    else:
        try:
            last_date = datetime.fromisoformat(last_date_iso).date()
            diff = (today - last_date).days
            if diff == 0:
                pass
            elif diff == 1:
                user_record["streak"] += 1
            else:
                user_record["streak"] = 1
        except ValueError:
            user_record["streak"] = 1

    user_record["last_vape_date"] = now_iso()
    user_record["best_streak"] = max(user_record["best_streak"], user_record["streak"])

# -------------------------
# QUEST HELPERS
# -------------------------

def refresh_quests_if_needed(user_record):
    if user_record["quests"]["date"] == today_str():
        return

    chosen = random.sample(QUEST_TEMPLATES, k=3)
    active = []
    for q in chosen:
        active.append({
            "id": q["id"],
            "name": q["name"],
            "type": q["type"],
            "goal": q["goal"],
            "reward": q["reward"],
            "progress": 0,
            "claimed": False,
        })

    user_record["quests"] = {
        "date": today_str(),
        "active": active,
    }

def update_quest_progress(user_record, quest_type, amount=1):
    refresh_quests_if_needed(user_record)
    for quest in user_record["quests"]["active"]:
        if quest["type"] == quest_type and not quest["claimed"]:
            quest["progress"] = min(quest["goal"], quest["progress"] + amount)

def claimable_quests(user_record):
    refresh_quests_if_needed(user_record)
    return [q for q in user_record["quests"]["active"] if q["progress"] >= q["goal"] and not q["claimed"]]

# -------------------------
# GAME HELPERS
# -------------------------

def get_equipped_pet(user_record):
    for pet in user_record["pets"]:
        if pet.get("equipped"):
            return pet
    return None

def roll_flavour(user_record):
    rare_chance = 0.10
    if has_item(user_record, "rare_coil"):
        rare_chance += 0.03

    equipped = get_equipped_pet(user_record)
    if equipped and equipped["trait"] == "Cloudborn":
        rare_chance += 0.02

    is_rare = random.random() < rare_chance
    return (random.choice(RARE_FLAVOURS), True) if is_rare else (random.choice(COMMON_FLAVOURS), False)

def vape_coin_reward(user_record, is_rare):
    coins = random.randint(3, 7)
    if has_item(user_record, "cloud_tank"):
        coins += 4
    if is_rare:
        coins += random.randint(4, 8)
    return coins

def hunt_roll(user_record):
    rare_chance = 0.12
    if has_item(user_record, "tracker_goggles"):
        rare_chance += 0.05

    equipped = get_equipped_pet(user_record)
    if equipped and equipped["trait"] == "Hunter":
        rare_chance += 0.02

    rare = random.random() < rare_chance
    animal = random.choice(RARE_VAPE_ANIMALS if rare else VAPE_ANIMALS)
    coins = random.randint(animal["coins"][0], animal["coins"][1])

    if has_item(user_record, "hunter_net"):
        coins += 5

    if equipped and equipped["trait"] == "Hunter":
        coins += 3

    return animal, coins, rare

def generate_pet(user_record, animal):
    pet_id = user_record["next_pet_id"]
    user_record["next_pet_id"] += 1

    favourite_flavour = random.choice(COMMON_FLAVOURS + RARE_FLAVOURS)
    trait = random.choice(list(PET_TRAITS.keys()))
    nickname = animal["name"]

    pet = {
        "id": pet_id,
        "species": animal["name"],
        "emoji": animal["emoji"],
        "nickname": nickname,
        "favourite_flavour": favourite_flavour,
        "trait": trait,
        "hunger": 60,
        "happiness": 50,
        "level": 1,
        "xp": 0,
        "equipped": False,
        "wins": 0,
        "losses": 0,
    }
    user_record["pets"].append(pet)
    return pet

def get_pet(user_record, pet_id):
    for pet in user_record["pets"]:
        if pet["id"] == pet_id:
            return pet
    return None

def pet_gain_xp(pet, amount):
    pet["xp"] += amount
    while pet["xp"] >= pet["level"] * 20:
        pet["xp"] -= pet["level"] * 20
        pet["level"] += 1
        pet["happiness"] = min(100, pet["happiness"] + 5)

def defense_multiplier(target_user):
    mult = 1.0
    if has_item(target_user, "bodyguard"):
        mult -= 0.20
    if has_item(target_user, "vault"):
        mult -= 0.35

    equipped = get_equipped_pet(target_user)
    if equipped and equipped["trait"] == "Guardian":
        mult -= 0.15

    return max(0.25, mult)

def rob_success_chance(attacker_user):
    chance = 0.35
    if has_item(attacker_user, "lockpick_set"):
        chance += 0.12

    equipped = get_equipped_pet(attacker_user)
    if equipped and equipped["trait"] == "Sneaky":
        chance += 0.08

    return min(0.75, chance)

def daily_reward(user_record):
    base = random.randint(90, 140)
    if has_item(user_record, "lucky_charm"):
        base += 20

    equipped = get_equipped_pet(user_record)
    if equipped and equipped["trait"] == "Lucky":
        base += 10

    streak_bonus = min(user_record["daily_streak"] * 5, 50)
    return base + streak_bonus

def crime_roll(user_record):
    crimes = [
        ("sold fake disposables behind the petrol station", 0.60, (60, 140), (20, 60)),
        ("raided a shady vape shipment", 0.48, (90, 200), (30, 80)),
        ("forged discount vouchers", 0.55, (70, 160), (25, 70)),
        ("lifted a crate from the back of a van", 0.50, (85, 180), (30, 75)),
        ("ran a sketchy black-market stall", 0.58, (65, 150), (25, 65)),
    ]
    scenario, success_chance, success_range, fail_range = random.choice(crimes)

    if has_item(user_record, "lucky_charm"):
        success_range = (success_range[0] + 10, success_range[1] + 15)
    if has_item(user_record, "crime_mask"):
        success_range = (success_range[0] + 20, success_range[1] + 25)

    equipped = get_equipped_pet(user_record)
    if equipped and equipped["trait"] == "Lucky":
        success_range = (success_range[0] + 8, success_range[1] + 12)

    if has_item(user_record, "smoke_bomb"):
        fail_range = (max(5, fail_range[0] - 10), max(10, fail_range[1] - 15))

    return scenario, success_chance, success_range, fail_range

# -------------------------
# QUOTE IMAGE HELPERS
# -------------------------

def get_font(size=28):
    candidates = ["arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"]
    for font_name in candidates:
        try:
            return ImageFont.truetype(font_name, size=size)
        except OSError:
            continue
    return ImageFont.load_default()

def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = f"{current} {word}".strip()
        width = draw.textbbox((0, 0), test, font=font)[2]
        if width <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines[:8]

async def build_quote_image(member: discord.Member, quote_text: str):
    avatar_bytes = await member.display_avatar.replace(size=256).read()
    avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA").resize((180, 180))

    mask = Image.new("L", (180, 180), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, 180, 180), fill=255)

    avatar_circle = Image.new("RGBA", (180, 180))
    avatar_circle.paste(avatar, (0, 0), mask)

    width, height = 1100, 600
    image = Image.new("RGBA", (width, height), (22, 24, 32, 255))
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, width, height), fill=(22, 24, 32))
    draw.rounded_rectangle((40, 40, width - 40, height - 40), radius=28, fill=(32, 36, 48))
    draw.rounded_rectangle((55, 55, width - 55, height - 55), radius=24, outline=(110, 125, 210), width=2)

    image.paste(avatar_circle, (80, 80), avatar_circle)

    title_font = get_font(52)
    text_font = get_font(34)
    small_font = get_font(24)

    draw.text((290, 85), "“", font=title_font, fill=(255, 255, 255))
    lines = wrap_text(draw, quote_text.strip(), text_font, 710)

    y = 150
    for line in lines:
        draw.text((290, y), line, font=text_font, fill=(245, 245, 245))
        y += 48

    draw.text((290, 500), f"— {member.display_name}", font=small_font, fill=(180, 190, 255))
    draw.text((80, 500), "saved quote", font=small_font, fill=(160, 160, 160))

    output = io.BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return output

# -------------------------
# EMBED HELPERS
# -------------------------

def make_embed(title, description=None, colour=COLOUR_NORMAL):
    return discord.Embed(title=title, description=description, colour=colour)

def set_user_thumb(embed, member):
    if member.display_avatar:
        embed.set_thumbnail(url=member.display_avatar.url)

# -------------------------
# INDEX BUTTON VIEW
# -------------------------

class IndexView(discord.ui.View):
    def __init__(self, author_id: int, guild_icon_url: str | None = None):
        super().__init__(timeout=180)
        self.author_id = author_id
        self.guild_icon_url = guild_icon_url

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "This menu isn't yours. Use `,index` to open your own.",
                ephemeral=True
            )
            return False
        return True

    def _finish_embed(self, embed: discord.Embed) -> discord.Embed:
        embed.set_footer(text="Shortcuts: ,q • ,s • ,ht")
        if self.guild_icon_url:
            embed.set_thumbnail(url=self.guild_icon_url)
        return embed

    def make_home_embed(self):
        embed = discord.Embed(
            title="📚 Bot Index",
            description="Use the buttons below to browse commands.",
            colour=COLOUR_UTILITY
        )
        embed.add_field(
            name="Categories",
            value=(
                "💰 Economy\n"
                "💨 Vape\n"
                "🦁 Pets\n"
                "🛒 Shop\n"
                "🖼️ Utility\n"
                "🏆 Leaderboards"
            ),
            inline=False
        )
        return self._finish_embed(embed)

    def make_economy_embed(self):
        embed = discord.Embed(
            title="💰 Economy Commands",
            description="Money, risk, and daily progress.",
            colour=COLOUR_MONEY
        )
        embed.add_field(
            name="Commands",
            value=(
                "` ,bal ` — view balance\n"
                "` ,daily ` — claim daily coins\n"
                "` ,crime ` — risky money command\n"
                "` ,rob @user ` — steal coins\n"
                "` ,quests ` — view and claim daily quests\n"
                "` ,coinflip <heads/tails> <amount> ` — gamble\n"
                "` ,ht <heads/tails> <amount> ` — shortcut"
            ),
            inline=False
        )
        return self._finish_embed(embed)

    def make_vape_embed(self):
        embed = discord.Embed(
            title="💨 Vape Commands",
            description="Hits, flavours, and profile progress.",
            colour=COLOUR_NORMAL
        )
        embed.add_field(
            name="Commands",
            value=(
                "` ,vape ` — take a vape hit\n"
                "` ,stats ` — view full profile"
            ),
            inline=False
        )
        return self._finish_embed(embed)

    def make_pets_embed(self):
        embed = discord.Embed(
            title="🦁 Pet Commands",
            description="Catch, manage, feed, and battle pets.",
            colour=COLOUR_HUNT
        )
        embed.add_field(
            name="Commands",
            value=(
                "` ,hunt ` — catch a vape animal\n"
                "` ,animals ` — view your pets\n"
                "` ,pet <id> ` — inspect a pet\n"
                "` ,equipet <id> ` — equip a pet\n"
                "` ,renamepet <id> <name> ` — rename a pet\n"
                "` ,feedpet <id> <flavour> ` — feed a pet\n"
                "` ,petbattle <your_pet_id> @user <their_pet_id> ` — battle pets"
            ),
            inline=False
        )
        return self._finish_embed(embed)

    def make_shop_embed(self):
        embed = discord.Embed(
            title="🛒 Shop Commands",
            description="Buy upgrades and check your stock.",
            colour=COLOUR_SHOP
        )
        embed.add_field(
            name="Commands",
            value=(
                "` ,shop ` — open the shop\n"
                "` ,buy <item> ` — buy an item\n"
                "` ,inventory ` — view your inventory"
            ),
            inline=False
        )
        return self._finish_embed(embed)

    def make_utility_embed(self):
        embed = discord.Embed(
            title="🖼️ Utility Commands",
            description="Quotes and deleted-message tools.",
            colour=COLOUR_UTILITY
        )
        embed.add_field(
            name="Commands",
            value=(
                "` ,quote save ` — save a replied message as a quote image\n"
                "` ,quote random ` — random saved quote\n"
                "` ,quote user @member ` — quote from a specific user\n"
                "` ,q ... ` — shortcut for quote\n"
                "` ,snipe ` — show last deleted message\n"
                "` ,s ` — shortcut for snipe"
            ),
            inline=False
        )
        return self._finish_embed(embed)

    def make_leaderboards_embed(self):
        embed = discord.Embed(
            title="🏆 Leaderboards",
            description="Compare stats across the server.",
            colour=COLOUR_STATS
        )
        embed.add_field(
            name="Commands",
            value=(
                "` ,top ` — default leaderboard\n"
                "` ,top coins ` — richest users\n"
                "` ,top hits ` — most vape hits\n"
                "` ,top pets ` — most pets owned"
            ),
            inline=False
        )
        return self._finish_embed(embed)

    @discord.ui.button(label="Home", style=discord.ButtonStyle.secondary, row=0)
    async def home_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.make_home_embed(), view=self)

    @discord.ui.button(label="Economy", style=discord.ButtonStyle.success, row=0)
    async def economy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.make_economy_embed(), view=self)

    @discord.ui.button(label="Vape", style=discord.ButtonStyle.primary, row=0)
    async def vape_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.make_vape_embed(), view=self)

    @discord.ui.button(label="Pets", style=discord.ButtonStyle.primary, row=1)
    async def pets_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.make_pets_embed(), view=self)

    @discord.ui.button(label="Shop", style=discord.ButtonStyle.secondary, row=1)
    async def shop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.make_shop_embed(), view=self)

    @discord.ui.button(label="Utility", style=discord.ButtonStyle.secondary, row=1)
    async def utility_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.make_utility_embed(), view=self)

    @discord.ui.button(label="Leaderboards", style=discord.ButtonStyle.success, row=2)
    async def leaderboards_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=self.make_leaderboards_embed(), view=self)

# -------------------------
# EVENTS
# -------------------------

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}", flush=True)

@bot.event
async def on_message_delete(message):
    if message.author.bot or not message.guild:
        return
    if not message.content and not message.attachments:
        return

    deleted_messages[message.channel.id] = {
        "author_id": message.author.id,
        "author_name": message.author.display_name,
        "content": message.content or "*attachment only*",
        "created_at": now_iso(),
        "attachment": message.attachments[0].url if message.attachments else None,
    }

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = make_embed(
            "⏳ Slow down",
            f"Wait **{round(error.retry_after)} seconds** before using that again.",
            COLOUR_ERROR,
        )
        await ctx.send(embed=embed)

    elif isinstance(error, commands.MissingRequiredArgument):
        embed = make_embed(
            "❌ Missing Argument",
            "Usage: `,steale <custom emoji>`",
            COLOUR_ERROR
        )
        await ctx.send(embed=embed)

    elif isinstance(error, commands.BadArgument):
        embed = make_embed(
            "❌ Invalid Input",
            "That emoji couldn't be read.",
            COLOUR_ERROR
        )
        await ctx.send(embed=embed)

    elif isinstance(error, commands.CommandNotFound):
        return

    else:
        print(error)  

# -------------------------
# COMMANDS: CORE
# -------------------------

@bot.command()
async def vape(ctx):
    data = load_data()
    user = get_user_record(data, ctx.author.id)
    refresh_quests_if_needed(user)

    flavour, is_rare = roll_flavour(user)
    line = random.choice(VAPE_LINES)

    user["total_hits"] += 1
    user["last_flavour"] = flavour
    user["flavour_counts"][flavour] = user["flavour_counts"].get(flavour, 0) + 1
    user["flavour_inventory"][flavour] = user["flavour_inventory"].get(flavour, 0) + 1

    if is_rare:
        user["rare_hits"] += 1
        update_quest_progress(user, "rare", 1)

    update_vape_streak(user)
    user["coins"] += vape_coin_reward(user, is_rare)
    update_quest_progress(user, "vape", 1)

    save_data(data)

    embed = make_embed(
        "💨 Vape Hit",
        f"**{ctx.author.display_name}** {line}",
        COLOUR_RARE if is_rare else COLOUR_NORMAL,
    )
    embed.add_field(name="🍓 Flavour", value=flavour, inline=False)
    embed.add_field(name="📈 Total Hits", value=str(user["total_hits"]), inline=True)
    embed.add_field(name="📦 Flavour Stock", value=str(user["flavour_inventory"].get(flavour, 0)), inline=True)
    if is_rare:
        embed.add_field(name="🌟 Rare Hit", value="You pulled a rare flavour.", inline=False)

    set_user_thumb(embed, ctx.author)
    embed.set_footer(text="use ,stats or ,quests for the bigger picture")
    await ctx.send(embed=embed)

@bot.command()
async def stats(ctx, member: discord.Member = None):
    data = load_data()
    target = member or ctx.author
    user = get_user_record(data, target.id)
    refresh_quests_if_needed(user)

    total_hits = user["total_hits"]
    rank = get_rank(total_hits)
    next_hits, next_rank = get_next_rank(total_hits)
    progress_text = "Max rank reached" if next_rank is None else f"{next_hits - total_hits} hits until {next_rank}"

    if user["flavour_counts"]:
        top_flavour = max(user["flavour_counts"], key=user["flavour_counts"].get)
        top_flavour_count = user["flavour_counts"][top_flavour]
    else:
        top_flavour = "None"
        top_flavour_count = 0

    embed = make_embed(
        f"📊 {target.display_name}'s Stats",
        "Full profile card",
        COLOUR_STATS,
    )
    embed.add_field(name="🪙 Coins", value=str(user["coins"]), inline=True)
    embed.add_field(name="💨 Hits", value=str(user["total_hits"]), inline=True)
    embed.add_field(name="🌟 Rare Hits", value=str(user["rare_hits"]), inline=True)
    embed.add_field(name="🏅 Rank", value=rank, inline=False)
    embed.add_field(name="🔥 Vape Streak", value=str(user["streak"]), inline=True)
    embed.add_field(name="🎁 Daily Streak", value=str(user["daily_streak"]), inline=True)
    embed.add_field(name="🎯 Hunts", value=str(user["hunt_count"]), inline=True)
    embed.add_field(name="🍓 Favourite Flavour", value=f"{top_flavour} ({top_flavour_count})", inline=False)
    embed.add_field(name="🕓 Last Flavour", value=user["last_flavour"] or "None", inline=True)
    embed.add_field(name="➡️ Progress", value=progress_text, inline=False)
    set_user_thumb(embed, target)

    await ctx.send(embed=embed)

@bot.command()
async def bal(ctx, member: discord.Member = None):
    data = load_data()
    target = member or ctx.author
    user = get_user_record(data, target.id)

    embed = make_embed(
        f"💰 {target.display_name}'s Balance",
        colour=COLOUR_MONEY,
    )
    embed.add_field(name="Coins", value=str(user["coins"]), inline=True)
    set_user_thumb(embed, target)

    await ctx.send(embed=embed)

@bot.command()
async def daily(ctx):
    data = load_data()
    user = get_user_record(data, ctx.author.id)
    refresh_quests_if_needed(user)

    if user["last_daily_claim"] == today_str():
        embed = make_embed("📅 Daily", "You already claimed your daily today.", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    yesterday = (utc_now().date() - timedelta(days=1)).isoformat()
    if user["last_daily_claim"] == yesterday:
        user["daily_streak"] += 1
    else:
        user["daily_streak"] = 1

    reward = daily_reward(user)
    user["coins"] += reward
    user["last_daily_claim"] = today_str()
    update_quest_progress(user, "daily", 1)

    save_data(data)

    embed = make_embed("📅 Daily Claimed", colour=COLOUR_MONEY)
    embed.add_field(name="Reward", value=f"{reward} coins", inline=True)
    embed.add_field(name="Daily Streak", value=str(user["daily_streak"]), inline=True)

    equipped = get_equipped_pet(user)
    bonus_text = "Lucky Charm / Lucky pet may have boosted this." if has_item(user, "lucky_charm") or (equipped and equipped["trait"] == "Lucky") else "No bonus modifiers used."
    embed.add_field(name="Notes", value=bonus_text, inline=False)

    await ctx.send(embed=embed)

import re

@bot.command()
async def steale(ctx, *, emoji_input: str = None):
    if not ctx.guild:
        await ctx.send("This command only works in a server.")
        return

    if not emoji_input:
        await ctx.send("Usage: `,steale <custom emoji>`")
        return

    match = re.search(r"<a?:\w+:\d+>", emoji_input)

    if not match:
        await ctx.send("❌ I couldn't find a custom emoji in your message.")
        return

    emoji = discord.PartialEmoji.from_str(match.group(0))

    if emoji.id is None:
        await ctx.send("❌ That is not a valid custom emoji.")
        return

    me = ctx.guild.me
    if me is None:
        await ctx.send("❌ I couldn't check my permissions here.")
        return

    if not me.guild_permissions.create_guild_expressions:
        await ctx.send("❌ I need the **Create Guild Expressions** permission.")
        return

    try:
        image_bytes = await emoji.read()

        new_emoji = await ctx.guild.create_custom_emoji(
            name=emoji.name or "stolen_emoji",
            image=image_bytes,
            reason=f"Emoji uploaded by request of {ctx.author}"
        )

        await ctx.send(f"✅ Success. Added {new_emoji} to this server.")

    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to upload emojis here.")

    except discord.HTTPException as e:
        await ctx.send(f"❌ Discord rejected the upload: `{e}`")

    except Exception as e:
        await ctx.send(f"❌ Unexpected error: `{e}`")

# -------------------------
# COMMANDS: HUNT / PETS
# -------------------------

@bot.command()
@cooldown(1, 60, BucketType.user)
async def hunt(ctx):
    data = load_data()
    user = get_user_record(data, ctx.author.id)
    refresh_quests_if_needed(user)

    animal, coins, is_rare = hunt_roll(user)
    pet = generate_pet(user, animal)

    user["coins"] += coins
    user["hunt_count"] += 1
    update_quest_progress(user, "hunt", 1)

    save_data(data)

    embed = make_embed(
        "🎯 Hunt Result",
        f"You found **{animal['name']}** {animal['emoji']} and caught it as a pet.",
        COLOUR_RARE if is_rare else COLOUR_HUNT,
    )
    embed.add_field(name="Coins Found", value=str(coins), inline=True)
    embed.add_field(name="Pet ID", value=str(pet["id"]), inline=True)
    embed.add_field(name="Trait", value=pet["trait"], inline=True)
    embed.add_field(name="Favourite Flavour", value=pet["favourite_flavour"], inline=False)
    if is_rare:
        embed.add_field(name="🌟 Rare Animal", value="Big catch.", inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def animals(ctx, member: discord.Member = None):
    data = load_data()
    target = member or ctx.author
    user = get_user_record(data, target.id)

    if not user["pets"]:
        embed = make_embed("🦴 Pet Collection", f"**{target.display_name}** has no pets yet.", COLOUR_HUNT)
        await ctx.send(embed=embed)
        return

    lines = []
    for pet in user["pets"][:20]:
        star = "⭐ " if pet.get("equipped") else ""
        lines.append(
            f"{star}`{pet['id']}` {pet['emoji']} **{pet['nickname']}** "
            f"({pet['species']}) • Lv {pet['level']} • {pet['trait']}"
        )

    embed = make_embed(f"🦁 {target.display_name}'s Pets", "\n".join(lines), COLOUR_HUNT)
    set_user_thumb(embed, target)

    await ctx.send(embed=embed)

@bot.command()
async def pet(ctx, pet_id: int):
    data = load_data()
    user = get_user_record(data, ctx.author.id)
    pet = get_pet(user, pet_id)

    if not pet:
        embed = make_embed("❌ Pet Not Found", "That pet ID is not yours.", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    embed = make_embed(f"{pet['emoji']} {pet['nickname']}", colour=COLOUR_HUNT)
    embed.add_field(name="Species", value=pet["species"], inline=True)
    embed.add_field(name="Level", value=str(pet["level"]), inline=True)
    embed.add_field(name="XP", value=str(pet["xp"]), inline=True)
    embed.add_field(name="Trait", value=pet["trait"], inline=False)
    embed.add_field(name="Trait Effect", value=PET_TRAITS[pet["trait"]], inline=False)
    embed.add_field(name="Hunger", value=str(pet["hunger"]), inline=True)
    embed.add_field(name="Happiness", value=str(pet["happiness"]), inline=True)
    embed.add_field(name="Favourite Flavour", value=pet["favourite_flavour"], inline=False)
    embed.add_field(name="Equipped", value="Yes" if pet.get("equipped") else "No", inline=True)
    embed.add_field(name="Wins", value=str(pet.get("wins", 0)), inline=True)
    embed.add_field(name="Losses", value=str(pet.get("losses", 0)), inline=True)

    await ctx.send(embed=embed)

@bot.command()
async def equipet(ctx, pet_id: int):
    data = load_data()
    user = get_user_record(data, ctx.author.id)
    pet = get_pet(user, pet_id)

    if not pet:
        embed = make_embed("❌ Pet Not Found", "That pet ID is not yours.", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    for p in user["pets"]:
        p["equipped"] = False
    pet["equipped"] = True

    save_data(data)

    embed = make_embed("⭐ Pet Equipped", f"**{pet['nickname']}** is now your active pet.", COLOUR_HUNT)
    await ctx.send(embed=embed)

@bot.command()
async def renamepet(ctx, pet_id: int, *, new_name: str):
    data = load_data()
    user = get_user_record(data, ctx.author.id)
    pet = get_pet(user, pet_id)

    if not pet:
        embed = make_embed("❌ Pet Not Found", "That pet ID is not yours.", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    if not has_item(user, "pet_tag"):
        embed = make_embed("🏷️ Pet Tag Needed", "Buy a `pet_tag` from the shop first.", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    pet["nickname"] = new_name[:32]
    save_data(data)

    embed = make_embed("✏️ Pet Renamed", f"Pet `{pet_id}` is now **{pet['nickname']}**.", COLOUR_HUNT)
    await ctx.send(embed=embed, allowed_mentions=ALLOWED_MENTIONS_NONE)

@bot.command()
async def feedpet(ctx, pet_id: int, *, flavour_name: str):
    data = load_data()
    user = get_user_record(data, ctx.author.id)
    pet = get_pet(user, pet_id)

    if not pet:
        embed = make_embed("❌ Pet Not Found", "That pet ID is not yours.", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    if not has_item(user, "feed_bowl"):
        embed = make_embed("🥣 Feed Bowl Needed", "Buy a `feed_bowl` from the shop first.", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    matched = None
    for flavour in list(user["flavour_inventory"].keys()):
        if flavour.lower() == flavour_name.lower():
            matched = flavour
            break

    if matched is None or user["flavour_inventory"].get(matched, 0) <= 0:
        embed = make_embed("🍓 Flavour Missing", "You do not have that flavour in stock.", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    user["flavour_inventory"][matched] -= 1
    if user["flavour_inventory"][matched] <= 0:
        del user["flavour_inventory"][matched]

    if matched == pet["favourite_flavour"]:
        pet["hunger"] = min(100, pet["hunger"] + 30)
        pet["happiness"] = min(100, pet["happiness"] + 20)
        pet_gain_xp(pet, 12)
        result = "Favourite flavour. Big boost."
    elif matched in RARE_FLAVOURS:
        pet["hunger"] = min(100, pet["hunger"] + 20)
        pet["happiness"] = min(100, pet["happiness"] + 12)
        pet_gain_xp(pet, 10)
        result = "Rare flavour. Nice boost."
    else:
        pet["hunger"] = min(100, pet["hunger"] + 15)
        pet["happiness"] = min(100, pet["happiness"] + 8)
        pet_gain_xp(pet, 6)
        result = "Fed successfully."

    update_quest_progress(user, "feed", 1)
    save_data(data)

    embed = make_embed("🥣 Pet Fed", f"**{pet['nickname']}** ate **{matched}**.", COLOUR_HUNT)
    embed.add_field(name="Result", value=result, inline=False)
    embed.add_field(name="Hunger", value=str(pet["hunger"]), inline=True)
    embed.add_field(name="Happiness", value=str(pet["happiness"]), inline=True)
    embed.add_field(name="Level", value=str(pet["level"]), inline=True)

    await ctx.send(embed=embed)

@bot.command()
@cooldown(1, 20, BucketType.user)
async def petbattle(ctx, your_pet_id: int = None, opponent: discord.Member = None, opponent_pet_id: int = None):
    if your_pet_id is None or opponent is None or opponent_pet_id is None:
        embed = make_embed(
            "⚔️ Pet Battle",
            "Use `,petbattle <your_pet_id> @user <their_pet_id>`",
            COLOUR_ERROR,
        )
        await ctx.send(embed=embed)
        return

    if opponent.bot or opponent.id == ctx.author.id:
        embed = make_embed("❌ Invalid Opponent", "Pick another real user.", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    data = load_data()
    your_user = get_user_record(data, ctx.author.id)
    their_user = get_user_record(data, opponent.id)

    your_pet = get_pet(your_user, your_pet_id)
    enemy_pet = get_pet(their_user, opponent_pet_id)

    if not your_pet:
        embed = make_embed("❌ Missing Pet", "Your pet ID was not found.", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    if not enemy_pet:
        embed = make_embed("❌ Missing Opponent Pet", "Their pet ID was not found.", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    your_power = (
        your_pet["level"] * 10
        + your_pet["happiness"]
        + your_pet["hunger"]
        + random.randint(1, 25)
    )

    enemy_power = (
        enemy_pet["level"] * 10
        + enemy_pet["happiness"]
        + enemy_pet["hunger"]
        + random.randint(1, 25)
    )

    if your_pet["trait"] == "Sneaky":
        your_power += 8
    elif your_pet["trait"] == "Hunter":
        your_power += 6
    elif your_pet["trait"] == "Lucky":
        your_power += random.randint(1, 10)
    elif your_pet["trait"] == "Guardian":
        your_power += 7
    elif your_pet["trait"] == "Cloudborn":
        your_power += 5

    if enemy_pet["trait"] == "Sneaky":
        enemy_power += 8
    elif enemy_pet["trait"] == "Hunter":
        enemy_power += 6
    elif enemy_pet["trait"] == "Lucky":
        enemy_power += random.randint(1, 10)
    elif enemy_pet["trait"] == "Guardian":
        enemy_power += 7
    elif enemy_pet["trait"] == "Cloudborn":
        enemy_power += 5

    if your_power >= enemy_power:
        winner = your_pet
        loser = enemy_pet
        winner_owner = your_user
        loser_owner = their_user
        winner_name = ctx.author.display_name
        loser_name = opponent.display_name
        reward = random.randint(25, 60)

        your_pet["wins"] = your_pet.get("wins", 0) + 1
        enemy_pet["losses"] = enemy_pet.get("losses", 0) + 1

        pet_gain_xp(your_pet, 12)
        pet_gain_xp(enemy_pet, 5)

        winner_owner["coins"] += reward
        loser_owner["coins"] = max(0, loser_owner["coins"] - min(20, loser_owner["coins"]))
    else:
        winner = enemy_pet
        loser = your_pet
        winner_owner = their_user
        loser_owner = your_user
        winner_name = opponent.display_name
        loser_name = ctx.author.display_name
        reward = random.randint(25, 60)

        enemy_pet["wins"] = enemy_pet.get("wins", 0) + 1
        your_pet["losses"] = your_pet.get("losses", 0) + 1

        pet_gain_xp(enemy_pet, 12)
        pet_gain_xp(your_pet, 5)

        winner_owner["coins"] += reward
        loser_owner["coins"] = max(0, loser_owner["coins"] - min(20, loser_owner["coins"]))

    save_data(data)

    embed = make_embed(
        "⚔️ Pet Battle Result",
        f"**{winner_name}'s {winner['nickname']}** defeated **{loser_name}'s {loser['nickname']}**.",
        COLOUR_HUNT,
    )
    embed.add_field(name=f"{your_pet['emoji']} {your_pet['nickname']}", value=f"Power: {your_power}", inline=True)
    embed.add_field(name=f"{enemy_pet['emoji']} {enemy_pet['nickname']}", value=f"Power: {enemy_power}", inline=True)
    embed.add_field(name="Reward", value=f"{reward} coins to the winner", inline=False)

    await ctx.send(embed=embed)

# -------------------------
# COMMANDS: ECONOMY
# -------------------------

@bot.command()
async def crime(ctx):
    data = load_data()
    user = get_user_record(data, ctx.author.id)
    refresh_quests_if_needed(user)

    scenario, success_chance, success_range, fail_range = crime_roll(user)
    success = random.random() < success_chance

    embed = make_embed("🕶️ Crime", colour=COLOUR_MONEY)

    if success:
        amount = random.randint(*success_range)
        user["coins"] += amount
        update_quest_progress(user, "crime", 1)
        embed.description = f"You **{scenario}** and got away with it."
        embed.add_field(name="Payout", value=f"+{amount} coins", inline=True)
    else:
        loss = min(user["coins"], random.randint(*fail_range))
        user["coins"] -= loss
        embed.description = f"You **{scenario}** and it went badly."
        embed.add_field(name="Loss", value=f"-{loss} coins", inline=True)

    save_data(data)
    embed.add_field(name="Balance", value=str(user["coins"]), inline=True)
    await ctx.send(embed=embed)

@bot.command()
@cooldown(1, 180, BucketType.user)
async def rob(ctx, target: discord.Member = None):
    if target is None:
        embed = make_embed("🧤 Rob", "Use `,rob @user`", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    if target.bot or target.id == ctx.author.id:
        embed = make_embed("❌ Invalid Target", "Pick a real user that is not yourself.", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    data = load_data()
    attacker = get_user_record(data, ctx.author.id)
    victim = get_user_record(data, target.id)
    refresh_quests_if_needed(attacker)

    if victim["coins"] < 75:
        embed = make_embed("🪙 Target Too Broke", "They need at least 75 coins to be worth robbing.", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    success_chance = rob_success_chance(attacker)
    success = random.random() < success_chance

    embed = make_embed("🧤 Rob Attempt", colour=COLOUR_MONEY)

    if success:
        max_base = min(200, max(40, int(victim["coins"] * 0.25)))
        stolen = random.randint(30, max_base)
        if has_item(attacker, "crime_mask"):
            stolen += 20

        equipped = get_equipped_pet(attacker)
        if equipped and equipped["trait"] == "Sneaky":
            stolen += 12

        stolen = int(stolen * defense_multiplier(victim))
        stolen = max(10, min(stolen, victim["coins"]))

        victim["coins"] -= stolen
        attacker["coins"] += stolen
        update_quest_progress(attacker, "rob_success", 1)

        embed.description = f"You robbed **{target.display_name}**."
        embed.add_field(name="Stolen", value=f"{stolen} coins", inline=True)
    else:
        penalty = min(attacker["coins"], random.randint(20, 70))
        attacker["coins"] -= penalty
        embed.description = f"You tried to rob **{target.display_name}** and failed."
        embed.add_field(name="Penalty", value=f"-{penalty} coins", inline=True)

    save_data(data)
    embed.add_field(name="Your Balance", value=str(attacker["coins"]), inline=True)

    await ctx.send(embed=embed)

@bot.command(aliases=["ht"])
@cooldown(1, 10, BucketType.user)
async def coinflip(ctx, side: str = None, amount: int = None):
    if side is None or amount is None:
        embed = make_embed(
            "🪙 Coinflip",
            "Use `,coinflip <heads/tails> <amount>`",
            COLOUR_ERROR,
        )
        await ctx.send(embed=embed)
        return

    side = side.lower()
    if side not in ["heads", "tails"]:
        embed = make_embed("❌ Invalid Side", "Pick `heads` or `tails`.", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    if amount <= 0:
        embed = make_embed("❌ Invalid Amount", "Bet must be above 0.", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    data = load_data()
    user = get_user_record(data, ctx.author.id)

    if user["coins"] < amount:
        embed = make_embed("💸 Not Enough Coins", "You do not have that many coins.", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    result = random.choice(["heads", "tails"])

    if result == side:
        winnings = amount
        user["coins"] += winnings
        text = f"The coin landed on **{result}**.\nYou won **{winnings}** coins."
        colour = COLOUR_MONEY
    else:
        user["coins"] -= amount
        text = f"The coin landed on **{result}**.\nYou lost **{amount}** coins."
        colour = COLOUR_ERROR

    save_data(data)

    embed = make_embed("🪙 Coinflip", text, colour)
    embed.add_field(name="Balance", value=str(user["coins"]), inline=True)
    await ctx.send(embed=embed)

# -------------------------
# COMMANDS: QUESTS / SHOP / INV
# -------------------------

@bot.command()
async def quests(ctx):
    data = load_data()
    user = get_user_record(data, ctx.author.id)
    refresh_quests_if_needed(user)

    claim_now = claimable_quests(user)
    gained = 0
    claimed_count = 0

    for quest in claim_now:
        user["coins"] += quest["reward"]
        quest["claimed"] = True
        gained += quest["reward"]
        claimed_count += 1

    save_data(data)

    lines = []
    for quest in user["quests"]["active"]:
        check = "✅" if quest["claimed"] else "🟨" if quest["progress"] >= quest["goal"] else "⬜"
        lines.append(
            f"{check} **{quest['name']}** — {quest['progress']}/{quest['goal']} • reward: {quest['reward']}"
        )

    embed = make_embed("📜 Daily Quests", "\n".join(lines), COLOUR_MONEY)
    if claimed_count:
        embed.add_field(name="Claimed Now", value=f"{claimed_count} quest(s)", inline=True)
        embed.add_field(name="Coins Gained", value=str(gained), inline=True)
    embed.set_footer(text="quests refresh daily and auto-claim when you run ,quests")

    await ctx.send(embed=embed)

@bot.command()
async def shop(ctx):
    embed = make_embed("🛒 Shop", "Use `,buy <item_key>`", COLOUR_SHOP)

    for key, item in SHOP_ITEMS.items():
        embed.add_field(
            name=f"{item['name']} — {item['cost']} coins",
            value=f"`{key}`\n{item['description']}",
            inline=False,
        )

    await ctx.send(embed=embed)

@bot.command()
async def buy(ctx, item_key: str = None):
    if item_key is None:
        embed = make_embed("🛒 Buy", "Use `,buy <item_key>`", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    item_key = item_key.lower()
    if item_key not in SHOP_ITEMS:
        embed = make_embed("❌ Unknown Item", "That item is not in the shop.", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    data = load_data()
    user = get_user_record(data, ctx.author.id)
    item = SHOP_ITEMS[item_key]

    if user["coins"] < item["cost"]:
        embed = make_embed(
            "💸 Not Enough Coins",
            f"You need {item['cost']} coins but only have {user['coins']}.",
            COLOUR_ERROR,
        )
        await ctx.send(embed=embed)
        return

    user["coins"] -= item["cost"]
    add_item(user, item_key, 1)
    save_data(data)

    embed = make_embed("✅ Purchase Complete", f"You bought **{item['name']}**.", COLOUR_SHOP)
    embed.add_field(name="Coins Left", value=str(user["coins"]), inline=True)

    await ctx.send(embed=embed)

@bot.command()
async def inventory(ctx):
    data = load_data()
    user = get_user_record(data, ctx.author.id)

    item_lines = []
    for key, amount in user["inventory"].items():
        if amount > 0 and key in SHOP_ITEMS:
            item_lines.append(f"• **{SHOP_ITEMS[key]['name']}** x{amount}")

    flavour_lines = []
    for flavour, amount in sorted(user["flavour_inventory"].items(), key=lambda x: x[0])[:20]:
        flavour_lines.append(f"• {flavour} x{amount}")

    embed = make_embed("🎒 Inventory", colour=COLOUR_SHOP)
    embed.add_field(name="Items", value="\n".join(item_lines) if item_lines else "Empty", inline=False)
    embed.add_field(name="Flavours", value="\n".join(flavour_lines) if flavour_lines else "No stored flavours", inline=False)

    await ctx.send(embed=embed)

# -------------------------
# COMMANDS: QUOTES / SNIPE
# -------------------------

@bot.group(invoke_without_command=True, aliases=["q"])
async def quote(ctx):
    embed = make_embed(
        "🖼️ Quote Commands",
        "` ,quote save ` while replying to a message\n` ,quote random `\n` ,quote user @member `",
        COLOUR_UTILITY,
    )
    await ctx.send(embed=embed)

@quote.command(name="save")
async def quote_save(ctx):
    if ctx.message.reference is None or ctx.message.reference.message_id is None:
        embed = make_embed("❌ Reply Required", "Reply to a message, then run `,quote save`.", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    try:
        referenced = await ctx.channel.fetch_message(ctx.message.reference.message_id)
    except discord.NotFound:
        embed = make_embed("❌ Message Missing", "Could not fetch that message.", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    if not referenced.content.strip():
        embed = make_embed("❌ Empty Message", "That message has no text to quote.", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    data = load_data()
    saver = get_user_record(data, ctx.author.id)
    guild_data = get_guild_record(data, ctx.guild.id)

    saver["quotes_saved"] += 1

    quote_entry = {
        "author_id": referenced.author.id,
        "author_name": referenced.author.display_name,
        "content": referenced.content[:400],
        "saved_by": ctx.author.id,
        "saved_at": now_iso(),
        "channel_id": ctx.channel.id,
    }
    guild_data["quotes"].append(quote_entry)
    save_data(data)

    image_bytes = await build_quote_image(referenced.author, referenced.content[:400])
    file = discord.File(image_bytes, filename="quote.png")

    embed = make_embed("🖼️ Quote Saved", f"Saved a quote from **{referenced.author.display_name}**.", COLOUR_UTILITY)
    embed.set_image(url="attachment://quote.png")

    await ctx.send(embed=embed, file=file, allowed_mentions=ALLOWED_MENTIONS_NONE)

@quote.command(name="random")
async def quote_random(ctx):
    data = load_data()
    guild_data = get_guild_record(data, ctx.guild.id)
    guild_quotes = guild_data.get("quotes", [])

    if not guild_quotes:
        embed = make_embed("🖼️ No Quotes", "No saved quotes in this server yet.", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    entry = random.choice(guild_quotes)
    member = ctx.guild.get_member(entry["author_id"])
    if member is None:
        embed = make_embed("❌ User Missing", "That quoted user is no longer in the server.", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    image_bytes = await build_quote_image(member, entry["content"])
    file = discord.File(image_bytes, filename="quote.png")

    embed = make_embed("🖼️ Random Quote", f"From **{entry['author_name']}**", COLOUR_UTILITY)
    embed.set_image(url="attachment://quote.png")

    await ctx.send(embed=embed, file=file, allowed_mentions=ALLOWED_MENTIONS_NONE)

@quote.command(name="user")
async def quote_user(ctx, member: discord.Member):
    data = load_data()
    guild_data = get_guild_record(data, ctx.guild.id)
    guild_quotes = guild_data.get("quotes", [])
    matches = [q for q in guild_quotes if q["author_id"] == member.id]

    if not matches:
        embed = make_embed("🖼️ No Quotes", f"No saved quotes for **{member.display_name}**.", COLOUR_ERROR)
        await ctx.send(embed=embed)
        return

    entry = random.choice(matches)
    image_bytes = await build_quote_image(member, entry["content"])
    file = discord.File(image_bytes, filename="quote.png")

    embed = make_embed("🖼️ User Quote", f"From **{member.display_name}**", COLOUR_UTILITY)
    embed.set_image(url="attachment://quote.png")

    await ctx.send(embed=embed, file=file, allowed_mentions=ALLOWED_MENTIONS_NONE)

@bot.command(aliases=["s"])
async def snipe(ctx):
    data = deleted_messages.get(ctx.channel.id)
    if not data:
        embed = make_embed("🎯 Snipe", "Nothing recently deleted in this channel.", COLOUR_UTILITY)
        await ctx.send(embed=embed)
        return

    author = ctx.guild.get_member(data["author_id"])
    embed = make_embed("🎯 Sniped Message", colour=COLOUR_UTILITY)
    embed.add_field(name="Author", value=data["author_name"], inline=True)
    embed.add_field(name="Message", value=data["content"][:1024], inline=False)

    if data["attachment"]:
        embed.add_field(name="Attachment", value=data["attachment"], inline=False)

    if author:
        set_user_thumb(embed, author)

    await ctx.send(embed=embed, allowed_mentions=ALLOWED_MENTIONS_NONE)

# -------------------------
# COMMANDS: LEADERBOARD / INDEX
# -------------------------

@bot.command()
async def top(ctx, category: str = "coins"):
    data = load_data()
    category = category.lower()

    user_records = {k: v for k, v in data.items() if k != "_guilds"}

    if not user_records:
        embed = make_embed("🏆 Leaderboard", "No data yet.", COLOUR_STATS)
        await ctx.send(embed=embed)
        return

    if category not in ["coins", "hits", "pets"]:
        category = "coins"

    if category == "coins":
        ranking = sorted(
            user_records.items(),
            key=lambda item: item[1].get("coins", 0),
            reverse=True
        )[:10]
        title = "🏆 Coin Leaderboard"
        lines = []
        for i, (user_id, record) in enumerate(ranking, start=1):
            member = ctx.guild.get_member(int(user_id))
            name = member.display_name if member else f"User {user_id}"
            lines.append(f"{i}. **{name}** — {record.get('coins', 0)} coins")

    elif category == "hits":
        ranking = sorted(
            user_records.items(),
            key=lambda item: item[1].get("total_hits", 0),
            reverse=True
        )[:10]
        title = "💨 Hit Leaderboard"
        lines = []
        for i, (user_id, record) in enumerate(ranking, start=1):
            member = ctx.guild.get_member(int(user_id))
            name = member.display_name if member else f"User {user_id}"
            lines.append(f"{i}. **{name}** — {record.get('total_hits', 0)} hits")

    else:
        ranking = sorted(
            user_records.items(),
            key=lambda item: len(item[1].get("pets", [])),
            reverse=True
        )[:10]
        title = "🦁 Pet Leaderboard"
        lines = []
        for i, (user_id, record) in enumerate(ranking, start=1):
            member = ctx.guild.get_member(int(user_id))
            name = member.display_name if member else f"User {user_id}"
            lines.append(f"{i}. **{name}** — {len(record.get('pets', []))} pets")

    embed = make_embed(title, "\n".join(lines) if lines else "No leaderboard data.", COLOUR_STATS)
    await ctx.send(embed=embed)

@bot.command()
async def index(ctx):
    guild_icon_url = ctx.guild.icon.url if ctx.guild and ctx.guild.icon else None
    view = IndexView(ctx.author.id, guild_icon_url)
    await ctx.send(embed=view.make_home_embed(), view=view)

# -------------------------
# COMMANDS: HELP
# -------------------------

@bot.command()
async def helpme(ctx):
    embed = make_embed(
        "📖 Help",
        "Use `,index` to open the button menu.",
        COLOUR_NORMAL,
    )
    await ctx.send(embed=embed)
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

if __name__ == "__main__":
    keep_alive()

    print("TOKEN loaded:", bool(TOKEN), flush=True)
    print("Starting bot login...", flush=True)

    bot.run(TOKEN)