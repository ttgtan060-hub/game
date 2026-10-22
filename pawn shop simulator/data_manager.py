import os
import json
import datetime


class DataManagerMixin:

  def load_game_data(self):
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(cur_dir, "config.json")):
      self.data_dir = cur_dir
    else:
      self.data_dir = os.path.join(cur_dir, "pawn shop simulator")

    with open(os.path.join(self.data_dir, "config.json"), "r", encoding="utf-8") as f:
      self.config = json.load(f)

    with open(os.path.join(self.data_dir, "devices.json"), "r", encoding="utf-8") as f:
      dev_data = json.load(f)
      self.devices = {k: tuple(v) for k, v in dev_data["devices"].items()}
      self.DEV_GENITIVE = dev_data["genitive"]
      self.branded_categories = dev_data.get("branded_categories", [])
      self.brands = dev_data.get("brands", ["Масунг", "Опел", "Чедмі"])

    with open(os.path.join(self.data_dir, "damages.json"), "r", encoding="utf-8") as f:
      dmg_data = json.load(f)
      self.all_damages = dmg_data["damages"]
      self.damage_tool_req = dmg_data["tool_requirements"]

    with open(os.path.join(self.data_dir, "tools.json"), "r", encoding="utf-8") as f:
      tool_data = json.load(f)
      self.TOOL_INFO = {k: tuple(v) for k, v in tool_data["tools"].items()}

    with open(os.path.join(self.data_dir, "accessories.json"), "r", encoding="utf-8") as f:
      acc_data = json.load(f)
      self.ACCESSORIES = acc_data["accessories"]

    with open(os.path.join(self.data_dir, "locations.json"), "r", encoding="utf-8") as f:
      self.locations_info = json.load(f)

    with open(os.path.join(self.data_dir, "mystery_boxes.json"), "r", encoding="utf-8") as f:
      self.mystery_boxes_info = json.load(f)

    with open(os.path.join(self.data_dir, "guide.json"), "r", encoding="utf-8") as f:
      self.guide_data = json.load(f)

    with open(os.path.join(self.data_dir, "parts.json"), "r", encoding="utf-8") as f:
      self.parts_data = json.load(f)

    self.DAY_DURATION_SECONDS = self.config.get("day_duration_seconds", 900)
    self.STORAGE_DEV_LIMITS = {int(k): v for k, v in self.config["storage_dev_limits"].items()}
    self.STORAGE_PARTS_LIMITS = {int(k): v for k, v in self.config["storage_parts_limits"].items()}
    self.PC_COMPONENTS_INFO = {k: tuple(v) for k, v in self.config["imei_pc_components"].items()}
    self.pc_specs = self.config.get("pc_specs", {})
    self.pc_modding = self.config.get("pc_modding", {})
    self.skills_info = self.config.get("skills", {})

    self.init_achievements()


  def init_achievements(self):
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(os.path.dirname(cur_dir), "achievements"),
        os.path.join(cur_dir, "achievements"),
        os.path.join(getattr(self, "saves_dir", cur_dir), "achievements"),
    ]
    self.achievements_dir = candidates[0]
    for c in candidates:
      if os.path.exists(c):
        self.achievements_dir = c
        break
    os.makedirs(self.achievements_dir, exist_ok=True)
    self.achievements_file = os.path.join(self.achievements_dir, "achievements.json")

    self.achievements = {}
    if os.path.exists(self.achievements_file):
      try:
        with open(self.achievements_file, "r", encoding="utf-8") as f:
          data = json.load(f)
          self.achievements = data.get("achievements", {})
      except Exception:
        self.achievements = {}

    if not self.achievements:
      self.achievements = {
          "first_deal": {"title": "Перша угода", "desc": "Купити або продати свій перший товар у ломбарді", "icon": "🤝", "unlocked": False, "date": None},
          "first_repair": {"title": "Майстер-початківець", "desc": "Успішно відремонтувати перше замовлення клієнта", "icon": "🔧", "unlocked": False, "date": None},
          "repair_expert": {"title": "Майстер-паяльщик", "desc": "Успішно відремонтувати 5 замовлень клієнтів", "icon": "🔥", "unlocked": False, "date": None},
          "first_pc": {"title": "Шеф комп'ютерів", "desc": "Зібрати свій перший робочий системний блок ПК", "icon": "🖥️", "unlocked": False, "date": None},
          "pc_legend": {"title": "Легенда збірок", "desc": "Зібрати 5 потужних ігрових комп'ютерів", "icon": "⚡", "unlocked": False, "date": None},
          "pc_modder": {"title": "Моддер року", "desc": "Зібрати ПК з водяним охолодженням або RGB-підсвіткою", "icon": "🌈", "unlocked": False, "date": None},
          "first_bounty": {"title": "Детектив ломбарду", "desc": "Зловити злодія за 3 секунди QTE та отримати винагороду поліції", "icon": "🚨", "unlocked": False, "date": None},
          "police_hero": {"title": "Поліцейський інформатор", "desc": "Здати поліції 5 підозрілих злодіїв з краденою технікою", "icon": "👮", "unlocked": False, "date": None},
          "scanner_pro": {"title": "Справжній діагност", "desc": "Придбати безстрокову ліцензію на ручний сканер дефектів", "icon": "🔍", "unlocked": False, "date": None},
          "test_bench_user": {"title": "Інженерний контроль", "desc": "Провести стрес-тест комплектуючих на професійному Тест-стенді", "icon": "🔬", "unlocked": False, "date": None},
          "fake_buster": {"title": "Гроза реплік", "desc": "Виявити підроблену або неякісну копію гаджета", "icon": "🕵️", "unlocked": False, "date": None},
          "express_delivery": {"title": "Блискавичний ремонт", "desc": "Успішно виконати термінове 1-денне експрес-замовлення", "icon": "⚡", "unlocked": False, "date": None},
          "trade_in_master": {"title": "Король Трейд-Іну", "desc": "Укласти вигідну угоду обміну техніки з доплатою", "icon": "🔄", "unlocked": False, "date": None},
          "tool_collector": {"title": "Колекціонер інструментів", "desc": "Придбати всі професійні інструменти для майстерні", "icon": "🛠️", "unlocked": False, "date": None},
          "rich_pawn": {"title": "Акула бізнесу", "desc": "Накопичити на рахунку понад 100,000 грн", "icon": "💰", "unlocked": False, "date": None},
          "oligarch": {"title": "Олігарх електроніки", "desc": "Накопичити на рахунку понад 500,000 грн", "icon": "👑", "unlocked": False, "date": None},
          "elite_location": {"title": "Елітна локація", "desc": "Переїхати до Преміум ТЦ у центрі міста", "icon": "🏢", "unlocked": False, "date": None},
      }
      self.save_achievements()


  def save_achievements(self):
    try:
      with open(self.achievements_file, "w", encoding="utf-8") as f:
        json.dump({"achievements": self.achievements}, f, ensure_ascii=False, indent=2)
    except Exception:
      pass


  def unlock_achievement(self, ach_id):
    if ach_id in self.achievements and not self.achievements[ach_id]["unlocked"]:
      self.achievements[ach_id]["unlocked"] = True
      self.achievements[ach_id]["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
      self.save_achievements()
      if hasattr(self, "show_achievement_toast"):
        self.show_achievement_toast(self.achievements[ach_id])


  def get_part_details(self, dev, damage):
    gen = self.DEV_GENITIVE.get(dev, dev)
    info = self.parts_data.get("damage_parts", {}).get(damage, {})
    overrides = info.get("overrides", {})
    item = overrides.get(dev) or info.get("default") or self.parts_data.get("fallback", ["Запчастина для {gen}", 500])
    name, cost = item
    return name.replace("{gen}", gen), cost
