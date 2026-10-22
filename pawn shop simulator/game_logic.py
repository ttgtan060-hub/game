import datetime
import random
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk


class GameLogicMixin:

  def start_new_game(self):
    self.day = 1
    self.balance = 30000
    self.inventory = []
    self.parts_inventory = {}
    self.parts_costs = {}
    self.client_orders = []
    self.pending_deliveries = []
    self.storage_dev_lvl = 1
    self.storage_parts_lvl = 1
    self.free_market_refresh_active = False
    self.ads_active = False
    self.lawyer_lvl = 0
    self.pc_parts = {
        "case": False, "mobo": False, "cpu_ram": False,
        "psu": False, "database": False
    }
    self.sound_enabled = True
    self.tools = {
        "screwdriver_set": False,
        "soldering_station": False,
        "screen_separator": False,
        "battery_tester": False,
        "programmer": False,
        "ultrasonic_bath": False,
    }
    self.tools_wear = {k: 20 for k in self.TOOL_INFO.keys()}
    self.skills = {
        "soldering_master": False,
        "bargaining_art": False,
        "neon_sign": False,
        "wholesale_partner": False,
        "scanner_permanent": False,
    }
    self.scanner_license_permanent = False
    self.location_lvl = 1
    self.reputation_stars = 1
    self.active_loan = None
    self.mystery_boxes_bought_today = {"small": False, "medium": False, "vip": False}
    self.stats = {
        "total_revenue": 0,
        "total_expenses": 0,
        "items_sold": 0,
        "orders_completed": 0,
        "pcs_assembled": 0,
        "police_confiscated": 0,
        "bounties_claimed": 0,
        "fakes_detected": 0,
        "trade_ins_completed": 0,
        "express_completed": 0,
    }
    self.transactions_history = []
    self.day_time_left = self.DAY_DURATION_SECONDS
    self.refresh_market_stock()
    self.gen_item()
    self.show_screen("game")
    self.start_day_timer()


  def buy_tool(self, tool_key, cost, name):
    if self.balance < cost:
      self.play_sound("error")
      messagebox.showerror("Недостатньо коштів", f"У вас недостатньо коштів на балансі для купівлі '{name}'!")
      return False
    self.balance -= cost
    self.tools[tool_key] = True
    self.tools_wear[tool_key] = 20
    self.play_sound("deal")
    messagebox.showinfo("Інструмент придбано", f"Ви успішно придбали '{name}' за {cost} грн!\nТепер це постійне обладнання вашої майстерні.")
    if all(self.tools.values()):
      self.unlock_achievement("tool_collector")
    self.update_ui_state()
    if getattr(self, "current_screen_name", None) == "night":
      self.render_night_screen()
    return True


  def service_tool(self, tool_key):
    cost = 150
    if self.balance < cost:
      messagebox.showerror("Недостатньо коштів", f"Обслуговування інструменту коштує {cost} грн!")
      return
    self.balance -= cost
    self.tools_wear[tool_key] = 20
    self.play_sound("repair")
    t_name = self.TOOL_INFO[tool_key][0]
    messagebox.showinfo("Інструмент обслуговано", f"Інструмент '{t_name}' заточено та обслуговано! Міцність відновлено до 100%.")
    self.update_ui_state()


  def dismantle_to_parts(self, idx):
    item = self.inventory[idx]
    dev = item["dev"]

    if dev == "Системний блок (ПК)":
      self.dismantle_pc(idx)
      return

    confirm = messagebox.askyesno(
        "Розібрати на запчастини",
        f"Розібрати '{dev}' на донорські комплектуючі?\n\n"
        f"⚠️ Пристрій буде знищено, але справні деталі надійдуть на ваш склад запчастин!",
    )
    if not confirm:
      return

    allowed_dmgs = [
        d for d, data in self.all_damages.items()
        if dev in data["allowed"] and d not in item.get("damages", [])
    ]

    salvaged = []
    if allowed_dmgs:
      count = min(len(allowed_dmgs), random.choice([1, 2]))
      chosen_dmgs = random.sample(allowed_dmgs, k=count)
      for cd in chosen_dmgs:
        p_name, p_cost = self.get_part_details(dev, cd)
        salvaged.append((p_name, p_cost))
    else:
      p_name, p_cost = self.get_part_details(dev, "Мікроцарапини на корпусі")
      salvaged.append((p_name, p_cost))

    max_parts = self.STORAGE_PARTS_LIMITS[self.storage_parts_lvl]
    curr_parts = sum(self.parts_inventory.values())
    if curr_parts + len(salvaged) > max_parts:
      self.play_sound("error")
      messagebox.showwarning(
          "Склад запчастин переповнений",
          f"Недостатньо місця на складі запчастин ({curr_parts}/{max_parts}) для збереження деталей!",
      )
      return

    self.inventory.pop(idx)

    salvaged_names = []
    for p_name, p_cost in salvaged:
      self.parts_inventory[p_name] = self.parts_inventory.get(p_name, 0) + 1
      if p_name not in self.parts_costs:
        self.parts_costs[p_name] = []
      self.parts_costs[p_name].append(p_cost)
      salvaged_names.append(f"• {p_name} (~{p_cost} грн)")

    self.play_sound("repair")
    salvaged_str = "\n".join(salvaged_names)
    messagebox.showinfo(
        "Пристрій розібрано",
        f"Пристрій успішно демонтовано! Отримані запчастини:\n\n"
        f"{salvaged_str}\n\n"
        f"Вони додані на ваш склад деталей.",
    )
    self.update_ui_state()


  def dismantle_pc(self, idx):
    item = self.inventory[idx]
    max_devs = self.STORAGE_DEV_LIMITS[self.storage_dev_lvl]
    occupied = len(self.inventory) + len(self.client_orders)
    if occupied - 1 + 5 > max_devs:
      self.play_sound("error")
      messagebox.showwarning(
          "Склад переповнено",
          f"Для розбирання ПК на 5 окремих компонентів потрібно 5 вільних місць!\n"
          f"Наразі зайнято {occupied}/{max_devs} місць на складі пристроїв.",
      )
      return

    confirm = messagebox.askyesno(
        "Розбирання комп'ютера",
        f"Розібрати {item['dev']} на окремі комплектуючі?\n\n"
        f"• Процесор\n• Відеокарта\n• Материнська плата Gaming\n• Блок живлення\n• Корпус ATX Glass\n\n"
        f"Кожен компонент стане окремим товаром на складі!",
    )
    if not confirm:
      return

    base = item["base_price"]
    buy_share = item["buy_price"] // 5
    stolen = item.get("is_stolen", False)
    checked = item.get("is_checked", False)
    dmg_list = list(item.get("damages", []))

    cpu_name = item.get("cpu_name", "Процесор Core-X5")
    gpu_name = item.get("gpu_name", "Відеокарта ATX 4060")
    psu_name = item.get("psu_name", "Блок живлення 750W")

    parts_specs = [
        (cpu_name, int(base * 0.22), ["Перегрів процесора / кулер", "Погнуті ніжки сокета CPU"]),
        (gpu_name, int(base * 0.40), ["Збій відеокарти", "Артефакти VRAM відеокарти"]),
        ("Материнська плата Gaming", int(base * 0.18), ["Не стартує системна плата", "Не вмикається взагалі", "Здуті конденсатори живлення"]),
        (psu_name, int(base * 0.10), ["Згорів блок живлення", "Здуті конденсатори живлення"]),
        ("Корпус ATX Glass", int(base * 0.10), ["Тріщина скла корпусу ПК", "Мікроцарапини на корпусі", "Глибокі сколи корпусу"]),
    ]

    self.inventory.pop(idx)

    for p_dev, p_base, possible_dmgs in parts_specs:
      inherited_dmgs = [d for d in dmg_list if d in possible_dmgs]
      is_rep = len(inherited_dmgs) == 0
      p_fair = p_base if is_rep else int(p_base * 0.7)
      new_comp = {
          "dev": p_dev,
          "buy_price": buy_share,
          "base_price": p_base,
          "fair_price": p_fair,
          "status": "ідеальний" if is_rep else "потребує ремонту",
          "damages": inherited_dmgs,
          "actual_repair_cost": 0,
          "spent_on_repair": 0,
          "is_repaired": is_rep,
          "is_stolen": stolen,
          "is_checked": checked,
          "on_sale": False,
          "target_sell_price": int(p_base * 1.15 if is_rep else p_fair * 1.15),
          "accessories": [],
      }
      self.inventory.append(new_comp)

    self.play_sound("repair")
    messagebox.showinfo(
        "ПК розібрано",
        f"Системний блок успішно розібрано на комплектуючі!\n"
        f"Усі вони розміщені на вашому складі товарів.",
    )
    self.update_ui_state()


  def dismantle_client_order_pc(self, idx):
    if idx >= len(self.client_orders):
      return
    order = self.client_orders[idx]
    if order.get("dev") != "Системний блок (ПК)":
      messagebox.showwarning(
          "Помилка",
          "Розбирати дозволено лише комп'ютери (ПК)! Іншу техніку клієнтів розбирати заборонено.",
      )
      return

    max_devs = self.STORAGE_DEV_LIMITS[self.storage_dev_lvl]
    occupied = len(self.inventory) + len(self.client_orders)
    if occupied - 1 + 5 > max_devs:
      self.play_sound("error")
      messagebox.showwarning(
          "Склад переповнено",
          f"Для розбирання ПК на 5 окремих компонентів потрібно 5 вільних місць!\n"
          f"Наразі зайнято {occupied}/{max_devs} місць на складі пристроїв.",
      )
      return

    confirm = messagebox.askyesno(
        "Розібрати клієнтський ПК",
        f"⚠️ УВАГА: Це клієнтське замовлення на ремонт!\n\n"
        f"Розібрати системний блок на 5 деталей і конфіскувати на свій склад?\n"
        f"Замовлення клієнта буде анульовано. Продовжити?",
    )
    if not confirm:
      return

    base = order.get("base_price", 18000)
    dmg_list = list(order.get("damages", []))

    parts_specs = [
        ("Процесор Core-X5", int(base * 0.22), ["Перегрів процесора / кулер"]),
        ("Відеокарта ATX 4060", int(base * 0.40), ["Збій відеокарти"]),
        ("Материнська плата Gaming", int(base * 0.18), ["Не стартує системна плата", "Не вмикається взагалі"]),
        ("Блок живлення 750W", int(base * 0.10), ["Згорів блок живлення"]),
        ("Корпус ATX Glass", int(base * 0.10), ["Тріщина скла корпусу ПК", "Мікроцарапини на корпусі", "Глибокі сколи корпусу"]),
    ]

    self.client_orders.pop(idx)

    for p_dev, p_base, possible_dmgs in parts_specs:
      inherited_dmgs = [d for d in dmg_list if d in possible_dmgs]
      is_rep = len(inherited_dmgs) == 0
      p_fair = p_base if is_rep else int(p_base * 0.7)
      new_comp = {
          "dev": p_dev,
          "buy_price": 0,
          "base_price": p_base,
          "fair_price": p_fair,
          "status": "ідеальний" if is_rep else "потребує ремонту",
          "damages": inherited_dmgs,
          "actual_repair_cost": 0,
          "spent_on_repair": 0,
          "is_repaired": is_rep,
          "is_stolen": False,
          "is_checked": True,
          "on_sale": False,
          "target_sell_price": int(p_base * 1.15 if is_rep else p_fair * 1.15),
          "accessories": [],
      }
      self.inventory.append(new_comp)

    self.play_sound("repair")
    messagebox.showinfo(
        "ПК клієнта розібрано",
        f"Системний блок успішно розібрано на 5 компонентів!\n"
        f"Усі вони розміщені на вашому складі товарів.",
    )
    self.update_ui_state()


  def assemble_pc(self):
    self.open_pc_assembly_dialog()


  def open_pc_assembly_dialog(self):
    cpus = [it for it in self.inventory if it["dev"].startswith("Процесор")]
    gpus = [it for it in self.inventory if it["dev"].startswith("Відеокарта")]
    rams = [it for it in self.inventory if it["dev"].startswith("Оперативна")]
    mobos = [it for it in self.inventory if it["dev"].startswith("Материнська")]
    psus = [it for it in self.inventory if it["dev"].startswith("Блок живлення")]
    cases = [it for it in self.inventory if it["dev"].startswith("Корпус")]

    missing = []
    if not cpus: missing.append("Процесор (Core-X3..X9)")
    if not gpus: missing.append("Відеокарта (ATX 3050..5080)")
    if not mobos: missing.append("Материнська плата")
    if not psus: missing.append("Блок живлення (200W..1000W)")
    if not cases: missing.append("Корпус ПК")

    if missing:
      self.play_sound("error")
      miss_str = "\n".join(f"  ❌ {m}" for m in missing)
      messagebox.showwarning(
          "Не вистачає деталей для ПК",
          f"Для збірки ПК потрібні компоненти на складі товарів:\n\n"
          f"{miss_str}\n\n"
          f"Придбайте їх у клієнтів або розберіть інший ПК!",
      )
      return

    if not self.tools.get("screwdriver_set", False):
      t_name, t_cost, _ = self.TOOL_INFO["screwdriver_set"]
      confirm_buy = messagebox.askyesno(
          "Потрібен інструмент",
          f"Для збірки комп'ютера потрібен інструмент:\n\n"
          f"🛠️ {t_name} ({t_cost} грн)\n\n"
          f"Придбати його зараз для майстерні?",
      )
      if confirm_buy:
        if not self.buy_tool("screwdriver_set", t_cost, t_name):
          return
      else:
        return

    dlg = ctk.CTkToplevel(self)
    dlg.title("🖥️ Професійний конфігуратор збірки ПК")
    dlg.geometry("640x720")
    dlg.grab_set()
    dlg.resizable(False, False)

    lbl_t = ctk.CTkLabel(dlg, text="⚙️ Конфігуратор системного блока", font=ctk.CTkFont(size=20, weight="bold"))
    lbl_t.pack(pady=(15, 5))

    lbl_sub = ctk.CTkLabel(dlg, text="Оберіть комплектуючі зі складу. Блок живлення зобов'язаний витримати споживання!", font=ctk.CTkFont(size=13), text_color="#bdc3c7")
    lbl_sub.pack(pady=(0, 10))

    frame_selectors = ctk.CTkFrame(dlg, corner_radius=12)
    frame_selectors.pack(fill="x", padx=25, pady=5)

    def format_item_label(it):
      return f"{it['dev']} (база {it['base_price']} грн)"

    row_cpu = ctk.CTkFrame(frame_selectors, fg_color="transparent")
    row_cpu.pack(fill="x", padx=15, pady=6)
    ctk.CTkLabel(row_cpu, text="🧠 Процесор:", width=130, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left")
    cpu_var = tk.StringVar(value=format_item_label(cpus[0]))
    cb_cpu = ctk.CTkComboBox(row_cpu, values=[format_item_label(c) for c in cpus], variable=cpu_var, width=380)
    cb_cpu.pack(side="right")

    row_gpu = ctk.CTkFrame(frame_selectors, fg_color="transparent")
    row_gpu.pack(fill="x", padx=15, pady=6)
    ctk.CTkLabel(row_gpu, text="🎮 Відеокарта:", width=130, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left")
    gpu_var = tk.StringVar(value=format_item_label(gpus[0]))
    cb_gpu = ctk.CTkComboBox(row_gpu, values=[format_item_label(g) for g in gpus], variable=gpu_var, width=380)
    cb_gpu.pack(side="right")

    row_ram = ctk.CTkFrame(frame_selectors, fg_color="transparent")
    row_ram.pack(fill="x", padx=15, pady=6)
    ctk.CTkLabel(row_ram, text="⚡ ОЗП (RAM):", width=130, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left")
    ram_options = [format_item_label(r) for r in rams] if rams else ["Стандартна 16GB (в платі)"]
    ram_var = tk.StringVar(value=ram_options[0])
    cb_ram = ctk.CTkComboBox(row_ram, values=ram_options, variable=ram_var, width=380)
    cb_ram.pack(side="right")

    row_mobo = ctk.CTkFrame(frame_selectors, fg_color="transparent")
    row_mobo.pack(fill="x", padx=15, pady=6)
    ctk.CTkLabel(row_mobo, text="🖲️ Системна плата:", width=130, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left")
    mobo_var = tk.StringVar(value=format_item_label(mobos[0]))
    cb_mobo = ctk.CTkComboBox(row_mobo, values=[format_item_label(m) for m in mobos], variable=mobo_var, width=380)
    cb_mobo.pack(side="right")

    row_case = ctk.CTkFrame(frame_selectors, fg_color="transparent")
    row_case.pack(fill="x", padx=15, pady=6)
    ctk.CTkLabel(row_case, text="📦 Корпус:", width=130, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left")
    case_var = tk.StringVar(value=format_item_label(cases[0]))
    cb_case = ctk.CTkComboBox(row_case, values=[format_item_label(ca) for ca in cases], variable=case_var, width=380)
    cb_case.pack(side="right")

    row_psu = ctk.CTkFrame(frame_selectors, fg_color="transparent")
    row_psu.pack(fill="x", padx=15, pady=6)
    ctk.CTkLabel(row_psu, text="🔌 Блок живлення:", width=130, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left")
    psu_var = tk.StringVar(value=format_item_label(psus[0]))
    cb_psu = ctk.CTkComboBox(row_psu, values=[format_item_label(p) for p in psus], variable=psu_var, width=380)
    cb_psu.pack(side="right")

    frame_mod = ctk.CTkFrame(dlg, corner_radius=12)
    frame_mod.pack(fill="x", padx=25, pady=10)

    ctk.CTkLabel(frame_mod, text="✨ Преміум моддинг (підвищує ціну при продажу):", font=ctk.CTkFont(size=14, weight="bold"), anchor="w").pack(padx=15, pady=(10, 5), anchor="w")

    var_rgb = tk.BooleanVar(value=False)
    chk_rgb = ctk.CTkCheckBox(frame_mod, text="🌈 RGB-підсвітка корпусу та кулерів (+450 грн / +15% вартості)", variable=var_rgb)
    chk_rgb.pack(padx=15, pady=4, anchor="w")

    var_cables = tk.BooleanVar(value=False)
    chk_cables = ctk.CTkCheckBox(frame_mod, text="🧵 Кастомні кабелі в обплетенні (+350 грн / +10% вартості)", variable=var_cables)
    chk_cables.pack(padx=15, pady=4, anchor="w")

    var_water = tk.BooleanVar(value=False)
    chk_water = ctk.CTkCheckBox(frame_mod, text="💧 Кастомне водяне охолодження СВО (+1600 грн / +25% вартості)", variable=var_water)
    chk_water.pack(padx=15, pady=(4, 10), anchor="w")

    lbl_power_status = ctk.CTkLabel(dlg, text="", font=ctk.CTkFont(size=15, weight="bold"))
    lbl_power_status.pack(pady=8)

    def calculate_current_balance():
      cpu_sel = cpus[cb_cpu.cget("values").index(cpu_var.get())]
      gpu_sel = gpus[cb_gpu.cget("values").index(gpu_var.get())]
      ram_sel = rams[cb_ram.cget("values").index(ram_var.get())] if rams else None
      psu_sel = psus[cb_psu.cget("values").index(psu_var.get())]

      cpu_w = self.pc_specs.get("cpus", {}).get(cpu_sel["dev"], 95)
      gpu_w = self.pc_specs.get("gpus", {}).get(gpu_sel["dev"], 150)
      ram_w = self.pc_specs.get("rams", {}).get(ram_sel["dev"], 20) if ram_sel else 20
      mobo_w = self.pc_specs.get("motherboard_watts", 50)

      total_needed = cpu_w + gpu_w + ram_w + mobo_w
      psu_cap = self.pc_specs.get("psus", {}).get(psu_sel["dev"], 500)

      is_ok = psu_cap >= total_needed
      if is_ok:
        lbl_power_status.configure(
            text=f"⚡ Споживання: {total_needed}W | БЖ: {psu_cap}W ✅ Баланс витримано (Запас {psu_cap - total_needed}W)",
            text_color="#2ecc71"
        )
      else:
        lbl_power_status.configure(
            text=f"🚨 ПЕРЕВАНТАЖЕННЯ: Потрібно {total_needed}W, а БЖ видає лише {psu_cap}W! ❌ НЕ ЗАПУСТИТЬСЯ",
            text_color="#e74c3c"
        )
      return is_ok, total_needed, psu_cap, cpu_sel, gpu_sel, ram_sel, mobos[0], cases[0], psu_sel

    cb_cpu.configure(command=lambda _: calculate_current_balance())
    cb_gpu.configure(command=lambda _: calculate_current_balance())
    cb_ram.configure(command=lambda _: calculate_current_balance())
    cb_psu.configure(command=lambda _: calculate_current_balance())
    calculate_current_balance()

    def do_build():
      is_ok, total_needed, psu_cap, c_item, g_item, r_item, m_item, ca_item, p_item = calculate_current_balance()
      if not is_ok:
        self.play_sound("error")
        messagebox.showerror(
            "Помилка потужності БЖ",
            f"Неможливо зібрати ПК!\n\n"
            f"Загальне споживання системи: {total_needed}W.\n"
            f"Обраний {p_item['dev']} має потужність лише {psu_cap}W.\n\n"
            f"Встановіть потужніший блок живлення (наприклад 600W, 750W або 1000W)!",
        )
        return

      mod_cost = 0
      mod_bonus = 0.0
      mods_applied = []
      if var_rgb.get():
        mod_cost += 450
        mod_bonus += 0.15
        mods_applied.append("RGB-підсвітка")
      if var_cables.get():
        mod_cost += 350
        mod_bonus += 0.10
        mods_applied.append("Кастомні кабелі")
      if var_water.get():
        mod_cost += 1600
        mod_bonus += 0.25
        mods_applied.append("Водяне охолодження")

      if self.balance < mod_cost:
        messagebox.showerror("Недостатньо коштів", f"Для встановлення обраного моддингу потрібно {mod_cost} грн на балансі!")
        return

      if mod_cost > 0:
        self.balance -= mod_cost
        self.stats["total_expenses"] += mod_cost
        self.add_transaction("витрата", f"Моддинг ПК ({', '.join(mods_applied)})", mod_cost)

      consumed = [c_item, g_item, m_item, ca_item, p_item]
      if r_item: consumed.append(r_item)

      for item in consumed:
        if item in self.inventory:
          self.inventory.remove(item)

      total_base = sum(c["base_price"] for c in consumed)
      total_buy = sum(c["buy_price"] for c in consumed) + mod_cost
      total_spent = sum(c.get("spent_on_repair", 0) for c in consumed) + mod_cost

      combined_damages = []
      for c in consumed:
        combined_damages.extend(c.get("damages", []))

      is_rep = len(combined_damages) == 0
      base_markup = 1.25 + mod_bonus
      pc_base = int(total_base * base_markup)
      pc_fair = pc_base if is_rep else int(pc_base * 0.75)
      pc_stolen = any(c.get("is_stolen", False) for c in consumed)

      pc_name = f"Системний блок ({c_item['dev'].replace('Процесор ', '')} / {g_item['dev'].replace('Відеокарта ', '')})"
      new_pc = {
          "dev": "Системний блок (ПК)",
          "title": pc_name,
          "cpu_name": c_item["dev"],
          "gpu_name": g_item["dev"],
          "psu_name": p_item["dev"],
          "mods": mods_applied,
          "buy_price": total_buy,
          "base_price": pc_base,
          "fair_price": pc_fair,
          "status": "ідеальний" if is_rep else "потребує ремонту",
          "damages": combined_damages,
          "actual_repair_cost": 0,
          "spent_on_repair": total_spent,
          "is_repaired": is_rep,
          "is_stolen": pc_stolen,
          "is_checked": True,
          "on_sale": False,
          "target_sell_price": int(pc_base * 1.20 if is_rep else pc_fair * 1.20),
          "accessories": [],
      }
      self.inventory.append(new_pc)
      self.stats["pcs_assembled"] = self.stats.get("pcs_assembled", 0) + 1

      self.unlock_achievement("first_pc")
      if self.stats["pcs_assembled"] >= 5:
        self.unlock_achievement("pc_legend")
      if mods_applied:
        self.unlock_achievement("pc_modder")

      self.play_sound("deal")
      dlg.destroy()
      messagebox.showinfo(
          "Збірка завершена",
          f"🎉 {pc_name} успішно зібрано!\n\n"
          f"⚡ Споживання: {total_needed}W (БЖ {psu_cap}W).\n"
          f"✨ Моддинг: {', '.join(mods_applied) if mods_applied else 'Базовий'}.\n"
          f"💰 Базова ринкова вартість: {pc_base} грн (+{int(base_markup*100 - 100)}% до комплектуючих)!\n"
          f"Стан: {'✨ Ідеальний' if is_rep else '⚠️ Потребує ремонту'}.\n"
          f"ПК розміщено на вашому складі та готовий до продажу!",
      )
      self.update_ui_state()

    btn_do_assemble = ctk.CTkButton(
        dlg,
        text="🛠️ Зібрати комп'ютер зараз",
        font=ctk.CTkFont(size=16, weight="bold"),
        height=48,
        fg_color="#27ae60",
        hover_color="#219150",
        command=do_build,
    )
    btn_do_assemble.pack(fill="x", padx=25, pady=(10, 20))


  def add_accessory(self, item_idx, acc_key):
    item = self.inventory[item_idx]
    acc_info = self.ACCESSORIES.get(acc_key)
    if not acc_info:
      return

    acc_name = acc_info["name"]
    cost = acc_info["cost"]

    if self.skills.get("wholesale_partner", False):
      cost = int(cost * 0.85)

    if acc_name in item.get("accessories", []):
      messagebox.showwarning("Увага", f"Аксесуар '{acc_name}' вже встановлено на цей пристрій!")
      return

    if self.balance < cost:
      messagebox.showerror("Недостатньо коштів", f"Не вистачає коштів для закупівлі '{acc_name}' ({cost} грн)!")
      return

    self.balance -= cost
    self.stats["total_expenses"] += cost
    self.add_transaction("витрата", f"Монтаж аксесуара: {acc_name} для {item['dev']}", cost)

    if "accessories" not in item:
      item["accessories"] = []
    item["accessories"].append(acc_name)
    item["base_price"] += acc_info["price_bonus"]
    item["fair_price"] += acc_info["price_bonus"]
    item["target_sell_price"] += acc_info["price_bonus"]
    item["spent_on_repair"] = item.get("spent_on_repair", 0) + cost

    self.play_sound("repair")
    messagebox.showinfo(
        "Аксесуар встановлено",
        f"Успішно встановлено '{acc_name}'!\n"
        f"Вартість пристрою зросла на +{acc_info['price_bonus']} грн,\n"
        f"а шанс швидкого продажу підвищено на +{int(acc_info['chance_bonus']*100)}%!",
    )
    self.update_ui_state()
    self.refresh_sell_tab()


  def start_day_timer(self):
    self.day_timer_running = True
    self.tick_day_timer()


  def stop_day_timer(self):
    self.day_timer_running = False
    if self.day_timer_after_id:
      try:
        self.after_cancel(self.day_timer_after_id)
      except Exception:
        pass
      self.day_timer_after_id = None


  def tick_day_timer(self):
    if not self.day_timer_running:
      return

    mins = self.day_time_left // 60
    secs = self.day_time_left % 60
    self.lbl_timer.configure(text=f"⏱️ {mins:02d}:{secs:02d}")

    if self.day_time_left <= 0:
      self.stop_day_timer()
      self.end_day()
      return

    self.day_time_left -= 1
    self.day_timer_after_id = self.after(1000, self.tick_day_timer)


  def add_transaction(self, t_type, desc, amount):
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    self.transactions_history.insert(0, {
        "day": self.day,
        "time": now_str,
        "type": t_type,
        "desc": desc,
        "amount": amount,
    })
    if len(self.transactions_history) > 100:
      self.transactions_history.pop()


  def take_loan(self, amount, days):
    if self.active_loan:
      messagebox.showwarning("Кредит вже активний", "Ви не можете взяти новий кредит, доки не погасите поточний!")
      return
    interest = int(amount * 0.20)
    total_repay = amount + interest
    self.active_loan = {
        "principal": amount,
        "total_to_repay": total_repay,
        "days_left": days,
        "days_total": days,
    }
    self.balance += amount
    self.stats["total_revenue"] += amount
    self.add_transaction("дохід", f"Кредит банку: +{amount} грн на {days} дн.", amount)
    self.play_sound("deal")
    messagebox.showinfo("Кредит отримано", f"Ви отримали {amount} грн!\nТермін повернення: {days} дн.\nСума до повернення: {total_repay} грн.")
    self.update_ui_state()
    self.render_night_screen()


  def repay_loan(self):
    if not self.active_loan:
      return
    cost = self.active_loan["total_to_repay"]
    if self.balance < cost:
      messagebox.showerror("Недостатньо коштів", f"Для погашення кредиту потрібно {cost} грн!")
      return
    self.balance -= cost
    self.stats["total_expenses"] += cost
    self.add_transaction("витрата", f"Погашення кредиту ({cost} грн)", cost)
    self.active_loan = None
    self.play_sound("deal")
    messagebox.showinfo("Кредит закрито", "Кредит банку успішно погашено в повному обсязі!")
    self.update_ui_state()
    self.render_night_screen()


  def move_to_next_location(self, new_lvl):
    loc_data = self.locations_info.get(str(new_lvl))
    if not loc_data:
      return
    cost = loc_data["cost"]
    if self.balance < cost:
      messagebox.showerror("Недостатньо коштів", f"Переїзд до '{loc_data['name']}' коштує {cost} грн!")
      return
    self.balance -= cost
    self.location_lvl = new_lvl
    self.reputation_stars = min(5, self.location_lvl + 1)
    self.add_transaction("витрата", f"Переїзд до локації: {loc_data['name']}", cost)
    self.play_sound("deal")
    messagebox.showinfo("Нова локація!", f"Вітаємо! Ваш ломбард переїхав до:\n🏢 '{loc_data['name']}'!\nПотік клієнтів та ціни значно зросли!")
    if new_lvl >= 3:
      self.unlock_achievement("elite_location")
    self.update_ui_state()
    self.render_night_screen()


  def buy_mystery_box(self, box_type):
    b_info = self.mystery_boxes_info.get(box_type)
    if not b_info:
      return
    if self.mystery_boxes_bought_today.get(box_type, False):
      messagebox.showwarning("Ліміт", "Ви вже купували цю таємничу коробку сьогодні! Завітайте завтра.")
      return
    cost = b_info["cost"]
    if self.balance < cost:
      messagebox.showerror("Недостатньо коштів", f"Для купівлі '{b_info['name']}' потрібно {cost} грн!")
      return
    self.balance -= cost
    self.mystery_boxes_bought_today[box_type] = True
    self.stats["total_expenses"] += cost
    self.add_transaction("витрата", f"Купівля боксу: {b_info['name']}", cost)

    min_val, max_val = b_info["value_range"]
    actual_value = random.randint(min_val, max_val)

    pool = [d for d, (p_min, p_max) in self.devices.items() if p_min <= actual_value * 1.5 and not d.startswith("Процесор") and not d.startswith("Відеокарта") and not d.startswith("Блок")]
    if not pool: pool = list(self.devices.keys())
    reward_dev = random.choice(pool)

    item_data = {
        "dev": reward_dev,
        "buy_price": cost,
        "base_price": actual_value,
        "fair_price": actual_value,
        "status": "ідеальний",
        "damages": [],
        "actual_repair_cost": 0,
        "spent_on_repair": 0,
        "is_repaired": True,
        "is_stolen": False,
        "is_checked": True,
        "on_sale": False,
        "target_sell_price": int(actual_value * 1.15),
        "accessories": [],
    }
    self.inventory.append(item_data)
    self.play_sound("deal")
    messagebox.showinfo(
        "Скриню відкрито!",
        f"🎁 Ви відкрили {b_info['name']}!\n\n"
        f"Всередині виявився:\n📱 {reward_dev}\n"
        f"Ринкова оцінка: {actual_value} грн!\n\n"
        f"Товар додано на ваш склад.",
    )
    self.update_ui_state()
    self.render_night_screen()


  def buy_skill(self, skill_key):
    s_info = self.skills_info.get(skill_key)
    if not s_info:
      return
    if self.skills.get(skill_key, False):
      messagebox.showinfo("Навичка активна", "Цю навичку вже розблоковано!")
      return
    cost = s_info["cost"]
    if self.balance < cost:
      messagebox.showerror("Недостатньо коштів", f"Для розблокування '{s_info['name']}' потрібно {cost} грн!")
      return
    self.balance -= cost
    self.skills[skill_key] = True
    if skill_key == "scanner_permanent":
      self.scanner_license_permanent = True
      self.unlock_achievement("scanner_pro")
    self.play_sound("deal")
    messagebox.showinfo("Навичку здобуто!", f"🎉 Вітаємо! Ви розблокували перманентну навичку:\n{s_info['name']}!\nЕфект діє назавжди.")
    self.update_ui_state()
    self.render_night_screen()


  def end_day(self):
    self.stop_day_timer()
    loc_data = self.locations_info.get(str(self.location_lvl), {})
    rent = loc_data.get("rent", 800)
    utilities = loc_data.get("utilities", 200)
    mandatory_expenses = rent + utilities

    sold_items = []
    remained_inventory = []
    police_incidents = []

    for item in self.inventory:
      if item.get("on_sale", False):
        price = item.get("target_sell_price", item["fair_price"])
        fair = item["fair_price"]
        ratio = price / fair if fair > 0 else 1.0

        if ratio <= 0.9: chance = 0.85
        elif ratio <= 1.05: chance = 0.65
        elif ratio <= 1.25: chance = 0.40
        elif ratio <= 1.50: chance = 0.20
        else: chance = 0.05

        if self.ads_active:
          chance = min(0.95, chance * 2.2)

        if self.skills.get("neon_sign", False):
          chance = min(0.98, chance * 1.25)

        for acc_k, acc_data in self.ACCESSORIES.items():
          if acc_data["name"] in item.get("accessories", []):
            chance = min(0.98, chance + acc_data["chance_bonus"])

        if random.random() < chance:
          if item.get("is_stolen", False) and random.random() < 0.45:
            lawyer_chance = {0: 0.0, 1: 0.25, 2: 0.50, 3: 0.75}.get(self.lawyer_lvl, 0.0)
            if random.random() < lawyer_chance:
              police_incidents.append(
                  f"⚖️ Поліція намагалася конфіскувати {item['dev']}, але ваш Юрист успішно відстояв інтереси! Продано за {price} грн."
              )
              sold_items.append((item, price))
            else:
              police_incidents.append(
                  f"🚔 РЕЙД ПОЛІЦІЇ! {item['dev']} виявився краденим і був КОНФІСКОВАНИЙ!"
              )
              self.stats["police_confiscated"] += 1
          else:
            sold_items.append((item, price))
        else:
          remained_inventory.append(item)
      else:
        remained_inventory.append(item)

    self.inventory = remained_inventory
    sales_revenue = sum(p for _, p in sold_items)
    self.balance += sales_revenue
    self.balance -= mandatory_expenses

    if sales_revenue > 0:
      self.stats["total_revenue"] += sales_revenue
      self.stats["items_sold"] += len(sold_items)
      self.add_transaction("дохід", f"Продажі з вітрини ({len(sold_items)} шт.)", sales_revenue)
      self.unlock_achievement("first_deal")

    self.stats["total_expenses"] += mandatory_expenses
    self.add_transaction("витрата", f"Оренда ({rent} грн) та комунальні ({utilities} грн)", mandatory_expenses)

    if self.active_loan:
      self.active_loan["days_left"] -= 1
      if self.active_loan["days_left"] <= 0:
        penalty = self.active_loan["principal"] * 2
        self.balance -= penalty
        self.stats["total_expenses"] += penalty
        self.add_transaction("витрата", f"ШТРАФ БАНКУ 2X ({penalty} грн)", penalty)
        self.play_sound("error")
        messagebox.showerror("🚨 ДЕФОЛТ ЗА КРЕДИТОМ!", f"Термін кредиту сплив! Банк списав штраф: -{penalty} грн!")
        self.active_loan = None

    self.free_market_refresh_active = False
    self.ads_active = False
    self.lawyer_lvl = 0

    completed_orders = []
    abandoned_devices = []
    failed_orders = []
    active_orders = []

    for ord_item in self.client_orders:
      ord_item["days_left"] -= 1
      if ord_item["days_left"] <= 0:
        if ord_item["is_repaired"]:
          if random.random() < 0.85:
            reward = ord_item["reward"]
            self.balance += reward
            self.stats["total_revenue"] += reward
            self.stats["orders_completed"] += 1
            self.add_transaction("дохід", f"Оплата за ремонт: {ord_item['dev']}", reward)
            completed_orders.append((ord_item, reward))
            self.unlock_achievement("first_repair")
            if self.stats["orders_completed"] >= 5:
              self.unlock_achievement("repair_expert")
            if ord_item.get("is_express", False):
              self.unlock_achievement("express_delivery")
          else:
            dev_data = {
                "dev": ord_item["dev"],
                "buy_price": 0,
                "base_price": ord_item["base_price"],
                "fair_price": ord_item["base_price"],
                "status": "ідеальний",
                "damages": [],
                "actual_repair_cost": 0,
                "spent_on_repair": 0,
                "is_repaired": True,
                "is_stolen": False,
                "is_checked": True,
                "on_sale": False,
                "target_sell_price": int(ord_item["base_price"] * 1.15),
                "accessories": [],
            }
            max_devs = self.STORAGE_DEV_LIMITS[self.storage_dev_lvl]
            if len(self.inventory) < max_devs:
              self.inventory.append(dev_data)
              abandoned_devices.append((ord_item, True))
            else:
              abandoned_devices.append((ord_item, False))
        else:
          failed_orders.append(ord_item)
      else:
        active_orders.append(ord_item)

    self.client_orders = active_orders

    self.daily_report = {
        "rent": rent,
        "utilities": utilities,
        "sold_items": sold_items,
        "completed_orders": completed_orders,
        "abandoned_devices": abandoned_devices,
        "failed_orders": failed_orders,
        "police_incidents": police_incidents,
        "sales_revenue": sales_revenue,
        "repair_revenue": sum(r for _, r in completed_orders),
        "mandatory_expenses": mandatory_expenses,
    }

    self.check_achievement_progress()

    if self.balance < 0 and len(self.inventory) == 0 and len(self.parts_inventory) == 0:
      messagebox.showerror(
          "БАНКРУТСТВО!",
          f"Ваш баланс упав до {self.balance} грн, і у вас не залишилося активів.\nЛомбард закрито за борги!",
      )
      self.show_screen("menu")
      return

    self.show_screen("night")


  def start_next_day(self):
    self.day += 1
    self.mystery_boxes_bought_today = {"small": False, "medium": False, "vip": False}
    self.day_time_left = self.DAY_DURATION_SECONDS

    delivered = []
    still_pending = []
    for p in getattr(self, "pending_deliveries", []):
      p["days_left"] -= 1
      if p["days_left"] <= 0:
        delivered.append(p)
      else:
        still_pending.append(p)
    self.pending_deliveries = still_pending

    if delivered:
      for p in delivered:
        p_name = p["name"]
        p_cost = p["cost"]
        self.parts_inventory[p_name] = self.parts_inventory.get(p_name, 0) + 1
        self.parts_costs.setdefault(p_name, []).append(p_cost)
      self.play_sound("deal")
      messagebox.showinfo(
          "📦 Ранкова пошта!",
          f"Прибула доставка оригінальних деталей від офіційного постачальника ({len(delivered)} шт.)!\n"
          f"Усі деталі додані до вашого складу запчастин.",
      )

    self.refresh_market_stock()
    self.gen_item()
    self.show_screen("game")
    self.start_day_timer()


  def is_pc_ready(self):
    return all(self.pc_parts.values())


  def upgrade_dev_storage(self, cost, new_lvl):
    if self.balance < cost:
      messagebox.showerror("Недостатньо коштів", "У вас недостатньо коштів на балансі!")
      return
    self.balance -= cost
    self.storage_dev_lvl = new_lvl
    messagebox.showinfo("Успіх", f"Склад пристроїв розширено до {self.STORAGE_DEV_LIMITS[new_lvl]} місць!")
    self.render_night_screen()


  def upgrade_parts_storage(self, cost, new_lvl):
    if self.balance < cost:
      messagebox.showerror("Недостатньо коштів", "У вас недостатньо коштів на балансі!")
      return
    self.balance -= cost
    self.storage_parts_lvl = new_lvl
    messagebox.showinfo("Успіх", f"Склад деталей розширено до {self.STORAGE_PARTS_LIMITS[new_lvl]} деталей!")
    self.render_night_screen()


  def buy_free_market_refresh(self):
    cost = 500
    if self.balance < cost:
      messagebox.showerror("Недостатньо коштів", "У вас недостатньо коштів на балансі!")
      return
    self.balance -= cost
    self.free_market_refresh_active = True
    messagebox.showinfo("Абонемент придбано", "Завтра всі оновлення Ринку деталей будуть БЕЗКОШТОВНИМИ (0 грн)!")
    self.render_night_screen()


  def buy_ads(self):
    cost = 600
    if self.balance < cost:
      messagebox.showerror("Недостатньо коштів", "У вас недостатньо коштів на балансі!")
      return
    self.balance -= cost
    self.ads_active = True
    messagebox.showinfo("Реклама активована", "Рекламна кампанія запущена! Завтра товари з вітрини розкуповуватимуть у 2.2 рази швидше!")
    self.render_night_screen()


  def hire_lawyer(self, lvl, cost):
    if self.balance < cost:
      messagebox.showerror("Недостатньо коштів", "У вас недостатньо коштів на балансі!")
      return
    self.balance -= cost
    self.lawyer_lvl = lvl
    pct = {1: 25, 2: 50, 3: 75}[lvl]
    messagebox.showinfo("Юрист найнятий", f"Ви найняли юриста {lvl}-го рівня ({pct}% захисту від рейдів поліції) на 1 день!")
    self.render_night_screen()


  def buy_pc_component(self, part_key, cost, part_name):
    if self.balance < cost:
      messagebox.showerror("Недостатньо коштів", "У вас недостатньо коштів на балансі!")
      return
    self.balance -= cost
    self.pc_parts[part_key] = True

    if self.is_pc_ready():
      messagebox.showinfo(
          "ПК ЗІБРАНО!",
          f"Ви встановили '{part_name}'!\n\n"
          f"🎉 Комп'ютер повністю зібрано та підключено до бази IMEI!\n"
          f"Відтепер перевірка техніки на розшук БЕЗКОШТОВНА!",
      )
    else:
      messagebox.showinfo("Деталь встановлена", f"Ви успішно придбали та встановили '{part_name}'!")
    self.render_night_screen()


  def gen_item(self):
    if getattr(self, "qte_police_active", False):
      self.cancel_police_qte()

    self.cur_is_repair_order = (random.random() < 0.30)
    self.cur_is_express = (random.random() < 0.25 and self.cur_is_repair_order)
    self.cur_client_patience_type = random.randint(1, 5)
    self.cur_client_patience = 100

    can_trade_in = (not self.cur_is_repair_order and any(i.get("is_repaired", False) for i in self.inventory))
    self.cur_is_trade_in = (random.random() < 0.18 and can_trade_in)

    self.cur_dev = random.choice(list(self.devices.keys()))
    if self.cur_dev in self.branded_categories:
      self.cur_brand = random.choice(self.brands)
    else:
      self.cur_brand = ""

    min_p, max_p = self.devices[self.cur_dev]
    loc_mult = self.locations_info.get(str(self.location_lvl), {}).get("client_multiplier", 1.0)
    raw_base = random.randint(min_p // 100, max_p // 100) * 100
    self.cur_base_price = int(raw_base * loc_mult // 10 * 10)

    valid_damages = [
        dmg_name for dmg_name, data in self.all_damages.items()
        if self.cur_dev in data["allowed"]
    ]

    self.cur_is_fake = (random.random() < 0.15 and not self.cur_is_repair_order and self.cur_dev in ["Смартфон", "Планшет", "Смарт-годинник", "Бездротові навушники"])

    if self.cur_is_repair_order:
      dmg_count = random.choice([1, 2, 3])
      self.cur_dmg_list = random.sample(valid_damages, k=min(dmg_count, len(valid_damages)))
    else:
      dmg_count = random.choices([0, 1, 2, 3], weights=[25, 40, 25, 10])[0]
      self.cur_dmg_list = random.sample(valid_damages, k=min(dmg_count, len(valid_damages)))
      if self.cur_is_fake and "Дешева копія (підробка)" in valid_damages and "Дешева копія (підробка)" not in self.cur_dmg_list:
        if random.random() < 0.4:
          self.cur_dmg_list.append("Дешева копія (підробка)")

    multiplier = 1.0
    est_min = 0
    est_max = 0

    for dmg in self.cur_dmg_list:
      data = self.all_damages[dmg]
      multiplier *= data["mult"]
      p_min, p_max = data["cost_pct"]
      est_min += self.cur_base_price * p_min
      est_max += self.cur_base_price * p_max

    if self.cur_is_fake and "Дешева копія (підробка)" not in self.cur_dmg_list:
      multiplier *= 0.5

    self.cur_est_repair_min = int(est_min * 0.9)
    self.cur_est_repair_max = int(est_max * 1.1)
    self.cur_fair_price = max(100, int(self.cur_base_price * multiplier))
    self.cur_real_status = "ідеальний" if len(self.cur_dmg_list) == 0 else "потребує ремонту"

    self.cur_is_stolen = (random.random() < 0.20) if not self.cur_is_repair_order else False
    self.cur_is_checked = False

    if self.cur_is_repair_order:
      parts_cost_approx = sum(self.get_part_details(self.cur_dev, d)[1] for d in self.cur_dmg_list)
      base_repair = int((parts_cost_approx * 1.5 + self.cur_base_price * 0.15 + 200) // 10 * 10)
      if self.cur_is_express:
        base_repair = int(base_repair * 2.0)
      self.cur_fair_repair_cost = base_repair
      markup = random.uniform(1.25, 1.55)
      max_by_market = int(self.cur_fair_repair_cost * markup)
      max_by_device_value = int(self.cur_base_price * 0.85)
      self.cur_client_max_repair_budget = max(self.cur_fair_repair_cost, min(max_by_market, max_by_device_value))
    else:
      if self.cur_is_stolen:
        client_markup = random.uniform(0.50, 0.70)
      else:
        client_markup = random.uniform(0.85, 1.20)
      self.cur_client_price = int(self.cur_fair_price * client_markup)

    if self.is_pc_ready():
      self.btn_check_stolen.configure(state="normal", text="💻 Перевірити IMEI через власний ПК (0 грн)")
    else:
      self.btn_check_stolen.configure(state="normal", text="🔍 Перевірити за базою IMEI (150 грн)")

    if hasattr(self, "btn_qte_police"):
      self.btn_qte_police.pack_forget()

    self.update_buy_text()


  def update_buy_text(self):
    self.txt_item_info.configure(state="normal")
    self.txt_item_info.delete("1.0", tk.END)

    brand_str = f" '{self.cur_brand}'" if getattr(self, "cur_brand", "") else ""
    full_title = f"{self.cur_dev}{brand_str}"

    p_names = {
        1: "🏃 Гіперактивний (Нетерплячий)",
        2: "⚡ Нервовий",
        3: "💼 Звичайний",
        4: "☕ Спокійний",
        5: "🧘 Дзен (Дуже терплячий)",
    }
    ptype_str = p_names.get(self.cur_client_patience_type, "Звичайний")

    dmg_text = (
        "\n".join([f"  • {d}" for d in self.cur_dmg_list])
        if self.cur_dmg_list
        else "  • Ідеальний стан, без дефектів."
    )

    if self.cur_dmg_list:
      req_parts = [self.get_part_details(self.cur_dev, d)[0] for d in self.cur_dmg_list]
      parts_list_str = "\n".join([f"  • {p}" for p in req_parts])
      repair_est_text = (
          f"~{self.cur_est_repair_min} - {self.cur_est_repair_max} грн\n"
          f"🔩 Необхідні деталі:\n{parts_list_str}"
      )
    else:
      repair_est_text = "Ремонт не потрібен"

    check_status = "❓ Не перевірявся"
    if self.cur_is_checked:
      check_status = (
          "🚨 УВАГА! Пристрій є в базі РОЗШУКУ!"
          if self.cur_is_stolen
          else "✅ Пристрій ЦІЛКОМ ЧИСТИЙ"
      )

    p_pct = max(0, min(100, self.cur_client_patience))
    if hasattr(self, "bar_client_patience"):
      self.bar_client_patience.set(p_pct / 100.0)
      mood_color = "#2ecc71" if p_pct >= 65 else ("#f39c12" if p_pct >= 35 else "#e74c3c")
      self.lbl_patience_val.configure(
          text=f"😊 Настрій: {p_pct}% | Тип клієнта: {ptype_str}",
          text_color=mood_color
      )

    if self.cur_is_repair_order:
      exp_tag = "⚡ ТЕРМІНОВЕ ЕКСПРЕС-ЗАМОВЛЕННЯ (1 день, 2x оплата!)" if self.cur_is_express else "Дедлайн: 3 робочі дні"
      self.lbl_card_title.configure(text=f"📋 Клієнтське замовлення: {exp_tag}")
      self.lbl_form_title.configure(text="📋 Ваша оцінка ремонту")
      self.btn_check_stolen.configure(state="disabled", text="🛡️ Пристрій клієнта (чистий)")
      self.lbl_price_input.configure(text="Ваша вартість ремонту (грн):")
      self.lbl_price_input.pack(anchor="w", padx=20, pady=(5, 2))
      self.entry_price.pack(fill="x", padx=20, pady=(0, 15))
      self.btn_submit_deal.configure(text="Запропонувати ціну та прийняти")

      info_str = (
          f"👤 ТИП: ЗАМОВЛЕННЯ НА РЕМОНТ ({exp_tag})\n"
          f"📱 Пристрій: {full_title}\n"
          f"💵 Ринкова вартість техніки: ~{self.cur_base_price} грн\n"
          f"📊 Орієнтовна ринкова вартість ремонту: ~{self.cur_fair_repair_cost} грн\n"
          f"🛠️ Необхідні деталі:\n{repair_est_text}\n\n"
          f"🔍 Виявлені несправності:\n{dmg_text}\n\n"
          f"💡 ПІДКАЗКА: Ви самі призначаєте ціну ремонту. Якщо завищити понад міру — клієнт піде геть!"
      )
      self.entry_price.delete(0, tk.END)
      self.entry_price.insert(0, str(self.cur_fair_repair_cost))
    elif self.cur_is_trade_in:
      repaired_items = [i for i in self.inventory if i.get("is_repaired", False)]
      trade_target = repaired_items[0] if repaired_items else None
      target_title = trade_target.get("title", trade_target["dev"]) if trade_target else "Ваш товар"
      target_val = trade_target.get("target_sell_price", trade_target["fair_price"]) if trade_target else 5000
      cash_surcharge = max(500, int(target_val - self.cur_fair_price))

      self.lbl_card_title.configure(text="🔄 Пропозиція TRADE-IN (Обмін з доплатою)")
      self.lbl_form_title.configure(text="🔄 Рішення щодо обміну")
      self.lbl_price_input.configure(text="Доплата від клієнта (грн):")
      self.btn_submit_deal.configure(text=f"Прийняти обмін на '{target_title}' (+{cash_surcharge} грн)")

      info_str = (
          f"🔄 УГОДА ТРЕЙД-ІН (TRADE-IN):\n"
          f"Клієнт віддає свій: {full_title} (Оцінка: ~{self.cur_fair_price} грн)\n"
          f"Натомість просить ваш товар з вітрини: 🛒 {target_title} (Ціна: {target_val} грн)\n"
          f"💵 Клієнт пропонує доплатити зверху: +{cash_surcharge} грн готівкою!\n\n"
          f"🛡️ База розшуку: {check_status}\n"
          f"🔍 Стан пристрою клієнта:\n{dmg_text}"
      )
      self.entry_price.delete(0, tk.END)
      self.entry_price.insert(0, str(cash_surcharge))
      self.cur_trade_in_target = trade_target
      self.cur_trade_in_cash = cash_surcharge
    else:
      self.lbl_card_title.configure(text="📥 Огляд пристрою від клієнта (Скупка)")
      self.lbl_form_title.configure(text="🤝 Купівля та Торг")
      self.lbl_price_input.configure(text="Запропонувати свою ціну (грн):")
      self.lbl_price_input.pack(anchor="w", padx=20, pady=(5, 2))
      self.entry_price.pack(fill="x", padx=20, pady=(0, 15))
      self.btn_submit_deal.configure(text="Купити пристрій")

      info_str = (
          f"📱 Пристрій: {full_title}\n"
          f"💵 Ринкова ціна (ідеальний): ~{self.cur_base_price} грн\n"
          f"🗣️ Бажана ціна клієнта: {self.cur_client_price} грн\n"
          f"🛠️ Вартість ремонту: {repair_est_text}\n"
          f"🛡️ Перевірка за базою: {check_status}\n\n"
          f"🔍 Виявлені пошкодження:\n{dmg_text}"
      )
      self.entry_price.delete(0, tk.END)
      self.entry_price.insert(0, str(self.cur_client_price))

    self.txt_item_info.insert("1.0", info_str)
    self.txt_item_info.configure(state="disabled")


  def check_stolen_status(self):
    cost = 0 if self.is_pc_ready() else 150
    if self.balance < cost:
      messagebox.showwarning("Помилка", f"У вас недостатньо коштів для перевірки ({cost} грн)!")
      return

    self.balance -= cost
    self.cur_is_checked = True
    self.btn_check_stolen.configure(state="disabled", text="🔍 Вже перевірено")
    self.update_ui_state()
    self.update_buy_text()

    if self.cur_is_stolen:
      self.start_police_qte()
    else:
      messagebox.showinfo("ПОЛІЦЕЙСЬКА БАЗА", "✅ Пристрій повністю чистий. Проблем немає.")


  def start_police_qte(self):
    self.qte_police_active = True
    self.qte_police_seconds = 3
    if hasattr(self, "btn_qte_police"):
      self.btn_qte_police.configure(
          text=f"🚨 ЗАХОПИТИ ЗЛОДІЯ / ПОЛІЦІЯ ({self.qte_police_seconds}с)!",
          state="normal"
      )
      self.btn_qte_police.pack(fill="x", padx=20, pady=(10, 5), before=self.btn_submit_deal)
    self.play_sound("error")
    self.qte_police_timer_id = self.after(1000, self.tick_police_qte)


  def tick_police_qte(self):
    if not getattr(self, "qte_police_active", False):
      return
    self.qte_police_seconds -= 1
    if self.qte_police_seconds <= 0:
      self.police_qte_expired()
    else:
      if hasattr(self, "btn_qte_police"):
        self.btn_qte_police.configure(text=f"🚨 ЗАХОПИТИ ЗЛОДІЯ / ПОЛІЦІЯ ({self.qte_police_seconds}с)!")
      self.qte_police_timer_id = self.after(1000, self.tick_police_qte)


  def cancel_police_qte(self):
    self.qte_police_active = False
    if getattr(self, "qte_police_timer_id", None):
      try:
        self.after_cancel(self.qte_police_timer_id)
      except Exception:
        pass
      self.qte_police_timer_id = None
    if hasattr(self, "btn_qte_police"):
      self.btn_qte_police.pack_forget()


  def claim_police_bounty(self):
    self.cancel_police_qte()
    bounty = 1500
    self.balance += bounty
    self.stats["total_revenue"] += bounty
    self.stats["bounties_claimed"] = self.stats.get("bounties_claimed", 0) + 1
    self.add_transaction("дохід", "Винагорода поліції за затримання крадія", bounty)

    self.unlock_achievement("first_bounty")
    if self.stats["bounties_claimed"] >= 5:
      self.unlock_achievement("police_hero")

    self.play_sound("deal")
    messagebox.showinfo(
        "🚨 ЗЛОДІЯ ЗАТРИМАНО!",
        f"Оперативна група поліції прибула на місце за 3 секунди!\n\n"
        f"Злодія взято на гарячому, крадений пристрій вилучено як речовий доказ.\n"
        f"Начальник відділу виплатив вам офіційну грошову премію: +{bounty} грн!",
    )
    self.update_ui_state()
    self.gen_item()


  def police_qte_expired(self):
    self.cancel_police_qte()
    self.play_sound("error")
    messagebox.showwarning(
        "💨 ЗЛОДІЙ ВТІК!",
        "Злодій помітив, що ви занадто довго дивитеся в базу розшуку!\n\n"
        f"Він вихопив {self.cur_dev} з ваших рук і блискавично втік із ломбарду!",
    )
    self.lbl_buy_result.configure(text="💨 Підозрілий тип вихопив телефон і накивав п'ятами!")
    self.gen_item()


  def open_scanner_minigame(self):
    if self.cur_dev == "Системний блок (ПК)":
      self.play_sound("error")
      messagebox.showwarning(
          "ПК занадто великий",
          "⚠️ Системний блок занадто громіздкий та складний для ручного сканера!\n\n"
          "Для комплексної діагностики ПК та його компонентів використовуйте вкладку 'Тест-стенд'.",
      )
      return

    if not self.scanner_license_permanent:
      ans = messagebox.askyesnocancel(
          "Ліцензія діагностичного сканера",
          "🔍 Ручний лазерний сканер дозволяє виявити 100% прихованих дефектів та реплік.\n\n"
          "Оберіть спосіб активації:\n"
          "• [Так] — Оплатити разове сканування (100 грн)\n"
          "• [Ні] — Придбати постійну ліцензію НАЗАВЖДИ (500 грн)\n"
          "• [Скасувати] — Відмовитися від сканування",
      )
      if ans is None:
        return
      elif ans is False:
        if self.balance < 500:
          messagebox.showerror("Недостатньо коштів", "Для безстрокової ліцензії потрібно 500 грн!")
          return
        self.balance -= 500
        self.scanner_license_permanent = True
        self.skills["scanner_permanent"] = True
        self.unlock_achievement("scanner_pro")
        self.add_transaction("витрата", "Постійна ліцензія сканера", 500)
        self.play_sound("deal")
        messagebox.showinfo("Ліцензія отримана", "Ви придбали безстрокову ліцензію на сканер! Усі майбутні сканування безкоштовні.")
      else:
        if self.balance < 100:
          messagebox.showerror("Недостатньо коштів", "Разове сканування коштує 100 грн!")
          return
        self.balance -= 100
        self.add_transaction("витрата", "Діагностичне сканування гаджета", 100)

    self.update_ui_state()

    dlg = ctk.CTkToplevel(self)
    dlg.title(f"🔍 Сканування дефектів: {self.cur_dev}")
    dlg.geometry("520x600")
    dlg.grab_set()
    dlg.resizable(False, False)

    lbl_t = ctk.CTkLabel(dlg, text="🔬 Діагностичний лазерний аналізатор", font=ctk.CTkFont(size=18, weight="bold"))
    lbl_t.pack(pady=(15, 5))

    lbl_inst = ctk.CTkLabel(dlg, text="Проскануйте всі 5 зон пристрою, щоб знайти приховані дефекти та підробки:", font=ctk.CTkFont(size=13), text_color="#bdc3c7")
    lbl_inst.pack(pady=(0, 10))

    zones = [
        ("📱 Сенсорний екран / Матриця", ["Тріщина на екрані", "Плями / вигорання матриці"]),
        ("🔋 Батарея та контролер живлення", ["Зношена батарея (<70%)", "Не заряджається (роз'єм)"]),
        ("⚙️ Системна плата та чіпсет", ["Не вмикається взагалі", "Утоплений / сліди корозії", "Заблокований (пароль / акаунт)"]),
        ("🔌 Порти, шлейфи та акустика", ["Рипить / тихий динамік", "Зламаний кабель / шнур", "Дрифт стіків / зламані кнопки"]),
        ("🛡️ Корпус та захисне покриття", ["Мікроцарапини на корпусі", "Глибокі сколи корпусу", "Зігнутий навпіл корпус", "Прокол / знос шини"]),
    ]

    scanned_zones = [False] * len(zones)
    progress_bar = ctk.CTkProgressBar(dlg, width=420)
    progress_bar.set(0.0)
    progress_bar.pack(pady=10)

    txt_results = ctk.CTkTextbox(dlg, width=460, height=220, font=ctk.CTkFont(size=13))
    txt_results.pack(padx=20, pady=10)
    txt_results.insert("1.0", "Натискайте кнопки зон нижче для детального апаратного аналізу...\n")
    txt_results.configure(state="disabled")

    def scan_zone(z_idx, btn):
      scanned_zones[z_idx] = True
      btn.configure(state="disabled", fg_color="#27ae60", text=f"✅ {zones[z_idx][0]} — Проскановано")
      count_done = sum(scanned_zones)
      progress_bar.set(count_done / float(len(zones)))

      matched = [d for d in self.cur_dmg_list if d in zones[z_idx][1]]
      txt_results.configure(state="normal")
      txt_results.insert(tk.END, f"\n[{zones[z_idx][0]}]:\n")
      if matched:
        for m in matched:
          txt_results.insert(tk.END, f"  🚨 ВИЯВЛЕНО ДЕФЕКТ: {m}\n")
      else:
        txt_results.insert(tk.END, "  ✨ Стан бездоганний, дефектів не зафіксовано.\n")

      if count_done == len(zones):
        if self.cur_is_fake:
          txt_results.insert(tk.END, "\n🕵️ АПАРАТНИЙ АНАЛІЗ: ЦЕ ПІДРОБКА / РЕПЛІКА НИЗЬКОЇ ЯКОСТІ!\n")
          self.unlock_achievement("fake_buster")
        txt_results.insert(tk.END, "\n🏁 Повне сканування завершено! Всі дефекти розкрито.\n")
        self.play_sound("deal")
      txt_results.configure(state="disabled")

    for i, (z_name, _) in enumerate(zones):
      b = ctk.CTkButton(dlg, text=f"🔍 Сканувати: {z_name}", width=420, height=36)
      b.configure(command=lambda idx=i, btn_w=b: scan_zone(idx, btn_w))
      b.pack(pady=4)

    def scan_all():
      for i in range(len(zones)):
        scanned_zones[i] = True
      progress_bar.set(1.0)
      txt_results.configure(state="normal")
      txt_results.delete("1.0", tk.END)
      txt_results.insert("1.0", "🏁 ПОВНЕ ЛАЗЕРНЕ СКАНУВАННЯ ЗАВЕРШЕНО:\n\n")
      if self.cur_dmg_list:
        txt_results.insert(tk.END, "⚠️ Виявлені несправності:\n")
        for d in self.cur_dmg_list:
          txt_results.insert(tk.END, f"  • {d}\n")
      else:
        txt_results.insert(tk.END, "✨ Пристрій у бездоганному технічному стані!\n")

      if self.cur_is_fake:
        txt_results.insert(tk.END, "\n🕵️ УВАГА: Пристрій є кустарною копією (підробка)!\n")
        self.unlock_achievement("fake_buster")

      txt_results.configure(state="disabled")
      self.play_sound("deal")

    btn_all = ctk.CTkButton(dlg, text="⚡ Сканувати все миттєво", fg_color="#3498db", width=420, height=38, command=scan_all)
    btn_all.pack(pady=(8, 12))


  def run_test_bench_diagnostic(self, item_idx):
    if item_idx >= len(self.inventory):
      return
    item = self.inventory[item_idx]

    cost = 100
    if self.balance < cost:
      messagebox.showerror("Недостатньо коштів", f"Діагностика на тест-стенді коштує {cost} грн!")
      return

    self.balance -= cost
    self.stats["total_expenses"] += cost
    self.add_transaction("витрата", f"Стрес-тест на Тест-стенді: {item['dev']}", cost)
    self.unlock_achievement("test_bench_user")
    self.play_sound("repair")

    dev_name = item["dev"]
    dmgs = item.get("damages", [])
    report_lines = []
    report_lines.append(f"🔬 ПРОТОКОЛ ТЕСТУВАННЯ: {item.get('title', dev_name)}")
    report_lines.append("--------------------------------------------------")

    if dev_name.startswith("Відеокарта"):
      report_lines.append("• Стрес-тест FurMark 4K: Температура 68°C, FPS стабільний.")
      if "Збій відеокарти" in dmgs or "Артефакти VRAM відеокарти" in dmgs:
        report_lines.append("❌ ПОМИЛКА: Зафіксовано збій відеопам'яті GDDR або артефакти рендерингу!")
      else:
        report_lines.append("✅ Відеочіп та чіпи пам'яті працюють на 100%.")

    elif dev_name.startswith("Процесор"):
      report_lines.append("• Стрес-тест Prime95: Навантаження 100% на всі ядра.")
      if "Перегрів процесора / кулер" in dmgs or "Погнуті ніжки сокета CPU" in dmgs:
        report_lines.append("❌ ПОМИЛКА: Троттлінг або пошкодження контактних ніжок сокета!")
      else:
        report_lines.append("✅ Обчислювальні блоки та кеш-пам'ять ідеальні.")

    elif dev_name.startswith("Блок живлення"):
      report_lines.append("• Навантажувальний стенд: Тестування ліній 12V, 5V, 3.3V.")
      if "Згорів блок живлення" in dmgs or "Здуті конденсатори живлення" in dmgs:
        report_lines.append("❌ ПОМИЛКА: Просідання напруги по лінії 12V або пульсації через здуті конденсатори!")
      else:
        report_lines.append("✅ Пульсації в межах норми ATX Gold, ККД 90%.")

    elif dev_name == "Системний блок (ПК)":
      report_lines.append("• Комплексний стрес-тест системи AIDA64 + 3DMark TimeSpy.")
      if dmgs:
        report_lines.append(f"❌ ВИЯВЛЕНО НЕПОЛАДКИ СИСТЕМИ: {', '.join(dmgs)}")
      else:
        report_lines.append("✅ Усі модулі ПК пройшли 30-хвилинний стрес-тест без жодного збою!")
    else:
      report_lines.append("• Апаратна перевірка контролерів та сенсорів.")
      if dmgs:
        report_lines.append(f"❌ ЗАФІКСОВАНО ДЕФЕКТИ: {', '.join(dmgs)}")
      else:
        report_lines.append("✅ Електронні компоненти справні.")

    report_lines.append("--------------------------------------------------")
    report_lines.append("Результат: Пристрій повністю продіагностовано.")
    res_str = "\n".join(report_lines)

    item["is_checked"] = True
    self.update_ui_state()
    self.render_test_bench_tab()

    messagebox.showinfo("Результати тест-стенду", res_str)


  def handle_deal_submit(self):
    if self.cur_is_repair_order:
      self.accept_repair_order()
    elif self.cur_is_trade_in:
      self.accept_trade_in_deal()
    else:
      self.buy_item()


  def accept_trade_in_deal(self):
    if not getattr(self, "cur_trade_in_target", None):
      self.buy_item()
      return

    target_item = self.cur_trade_in_target
    if target_item not in self.inventory:
      messagebox.showwarning("Помилка", "Обраний товар з вітрини вже відсутній!")
      self.gen_item()
      return

    try:
      client_surcharge = int(self.entry_price.get())
    except ValueError:
      messagebox.showwarning("Помилка", "Введіть коректну суму доплати!")
      return

    req_cash = getattr(self, "cur_trade_in_cash", 1000)
    if client_surcharge < req_cash * 0.8:
      self.play_sound("error")
      messagebox.showwarning("Відмова клієнта", "Клієнт не згоден доплачувати більше, ніж пропонував! Угоду Трейд-Ін зірвано.")
      self.gen_item()
      return

    self.inventory.remove(target_item)
    self.balance += client_surcharge
    self.stats["total_revenue"] += client_surcharge
    self.stats["trade_ins_completed"] = self.stats.get("trade_ins_completed", 0) + 1
    self.add_transaction("дохід", f"Доплата Трейд-Ін за обмін на {target_item['dev']}", client_surcharge)

    new_device = {
        "dev": self.cur_dev,
        "title": f"{self.cur_dev} '{self.cur_brand}'" if self.cur_brand else self.cur_dev,
        "buy_price": target_item.get("buy_price", 0),
        "base_price": self.cur_base_price,
        "fair_price": self.cur_fair_price,
        "status": self.cur_real_status,
        "damages": list(self.cur_dmg_list),
        "actual_repair_cost": 0,
        "spent_on_repair": 0,
        "is_repaired": len(self.cur_dmg_list) == 0,
        "is_stolen": self.cur_is_stolen,
        "is_checked": self.cur_is_checked,
        "on_sale": False,
        "target_sell_price": int(self.cur_fair_price * 1.15),
        "accessories": [],
    }
    self.inventory.append(new_device)
    self.unlock_achievement("trade_in_master")
    self.play_sound("deal")

    messagebox.showinfo(
        "Угода Trade-In завершена!",
        f"🎉 Успішний обмін техніки!\n\n"
        f"Ви передали клієнту: {target_item['dev']}.\n"
        f"Отримали пристрій: {self.cur_dev} та +{client_surcharge} грн доплати готівкою!",
    )
    self.update_ui_state()
    self.gen_item()


  def accept_repair_order(self):
    max_devs = self.STORAGE_DEV_LIMITS[self.storage_dev_lvl]
    occupied = len(self.inventory) + len(self.client_orders)
    if occupied >= max_devs:
      messagebox.showwarning(
          "Склад заповнено",
          f"Ваш склад заповнений ({occupied}/{max_devs})!\n"
          f"Звільніть місце перед тим, як приймати нові замовлення на ремонт.",
      )
      return

    try:
      offer = int(self.entry_price.get())
    except ValueError:
      messagebox.showwarning("Помилка", "Будь ласка, введіть коректну числову ціну за ремонт!")
      return

    if offer <= 0:
      messagebox.showwarning("Помилка", "Ціна ремонту повинна бути більшою за 0 грн!")
      return

    if offer > self.cur_client_max_repair_budget:
      p_drop = 50 if self.cur_client_patience_type != 1 else 100
      self.cur_client_patience -= p_drop
      if self.cur_client_patience <= 0:
        if self.cur_client_patience_type == 1:
          self.lbl_buy_result.configure(
              text="🏃 Клієнт розлютився: 'У мене літак через 20 хвилин на острови збирати банани, я не маю часу торгуватися!' і вибіг геть!"
          )
        else:
          self.lbl_buy_result.configure(
              text=f"😠 Клієнт обурився: '{offer} грн — це занадто дорого за такий ремонт!' і пішов до іншої майстерні."
          )
        self.gen_item()
        return
      else:
        messagebox.showwarning("Клієнт незадоволений", f"Клієнт каже: '{offer} грн — це забагато! Спробуйте назвати адекватнішу ціну.'")
        self.update_buy_text()
        return

    days_duration = 1 if self.cur_is_express else 3
    order_data = {
        "dev": self.cur_dev,
        "base_price": self.cur_base_price,
        "damages": list(self.cur_dmg_list),
        "reward": offer,
        "days_left": days_duration,
        "is_repaired": False,
        "is_stolen": False,
        "is_express": self.cur_is_express,
    }
    self.client_orders.append(order_data)
    self.play_sound("deal")
    self.lbl_buy_result.configure(
        text=f"🤝 Клієнт погодився на вашу ціну ({offer} грн)! Замовлення на {self.cur_dev} прийнято на {days_duration} дн."
    )
    self.update_ui_state()
    self.gen_item()


  def buy_item(self):
    max_devs = self.STORAGE_DEV_LIMITS[self.storage_dev_lvl]
    occupied = len(self.inventory) + len(self.client_orders)
    if occupied >= max_devs:
      messagebox.showwarning(
          "Склад заповнено",
          f"Ваш склад заповнений ({occupied}/{max_devs})!\n"
          f"Продайте товари або розширте склад у меню нічної прокачки.",
      )
      return

    try:
      offer = int(self.entry_price.get())
    except ValueError:
      messagebox.showwarning("Помилка", "Будь ласка, введіть коректну числову ціну!")
      return

    if offer > self.balance:
      messagebox.showerror("Помилка", "У вас недостатньо коштів на балансі!")
      return

    lowball_threshold = 0.60
    if self.skills.get("bargaining_art", False):
      lowball_threshold = 0.50

    if offer < self.cur_fair_price * lowball_threshold:
      drop_val = 70 if self.cur_client_patience_type == 1 else (45 if self.cur_client_patience_type == 2 else 30)
      self.cur_client_patience -= drop_val
      if self.cur_client_patience <= 0:
        if self.cur_client_patience_type == 1:
          self.lbl_buy_result.configure(text="🏃 Клієнт обурився мізерною пропозицією і втік, бо спізнюється на літак збирати банани!")
        else:
          self.lbl_buy_result.configure(text="😠 Клієнт обурився занадто низькою ціною і пішов геть!")
        self.gen_item()
        return
      else:
        messagebox.showwarning("Клієнт торгується", f"Клієнт незадоволений ціною {offer} грн! Підвищіть ставку або він піде.")
        self.update_buy_text()
        return

    self.balance -= offer

    actual_repair_cost = 0
    for dmg in self.cur_dmg_list:
      data = self.all_damages[dmg]
      p_min, p_max = data["cost_pct"]
      actual_repair_cost += int(self.cur_base_price * random.uniform(p_min, p_max))

    default_sell = (
        int(self.cur_base_price * 1.15)
        if len(self.cur_dmg_list) == 0
        else int(self.cur_fair_price * 1.15)
    )
    default_sell = max(default_sell, int(offer * 1.15 // 10 * 10))

    item_data = {
        "dev": self.cur_dev,
        "title": f"{self.cur_dev} '{self.cur_brand}'" if self.cur_brand else self.cur_dev,
        "buy_price": offer,
        "base_price": self.cur_base_price,
        "fair_price": self.cur_fair_price,
        "status": getattr(self, "cur_real_status", "ідеальний" if len(self.cur_dmg_list) == 0 else "потребує ремонту"),
        "damages": list(self.cur_dmg_list),
        "actual_repair_cost": actual_repair_cost,
        "spent_on_repair": 0,
        "is_repaired": len(self.cur_dmg_list) == 0,
        "is_stolen": self.cur_is_stolen,
        "is_checked": self.cur_is_checked,
        "is_fake": getattr(self, "cur_is_fake", False),
        "on_sale": False,
        "target_sell_price": default_sell,
        "accessories": [],
    }

    self.inventory.append(item_data)
    self.stats["total_expenses"] += offer
    self.add_transaction("витрата", f"Скупка товару: {item_data['title']}", offer)
    self.unlock_achievement("first_deal")
    self.play_sound("deal")
    self.lbl_buy_result.configure(text=f"✅ Успішно куплено за {offer} грн і відправлено на склад!")
    self.update_ui_state()
    self.gen_item()


  def skip_item(self):
    if getattr(self, "cur_is_repair_order", False):
      self.lbl_buy_result.configure(text="🗑️ Ви відмовилися брати замовлення в ремонт.")
    else:
      self.lbl_buy_result.configure(text="🗑️ Ви відмовилися від угоди.")
    self.gen_item()


  def toggle_showcase(self, idx, entry_widget):
    item = self.inventory[idx]
    if item.get("on_sale", False):
      item["on_sale"] = False
      messagebox.showinfo("Вітрина", f"'{item.get('title', item['dev'])}' знято з вітрини.")
    else:
      try:
        new_price = int(entry_widget.get())
        if new_price <= 0:
          raise ValueError()
        item["target_sell_price"] = new_price
        item["on_sale"] = True
        messagebox.showinfo("Вітрина", f"'{item.get('title', item['dev'])}' виставлено на вітрину за {new_price} грн!")
      except ValueError:
        messagebox.showerror("Помилка", "Введіть коректну ціну продажу!")
        return
    self.update_ui_state()
    self.refresh_sell_tab()


  def sell_part(self, part_name, entry_widget):
    curr_qty = self.parts_inventory.get(part_name, 0)
    if curr_qty <= 0:
      return

    try:
      count = int(entry_widget.get())
      if count <= 0:
        raise ValueError()
    except ValueError:
      messagebox.showerror("Помилка", "Введіть додатну кількість деталей для продажу!")
      return

    actual_count = min(count, curr_qty)
    unit_price = int(self.catalog.get(part_name, {}).get("base_cost", 300) * 0.7)
    total_revenue = unit_price * actual_count

    self.parts_inventory[part_name] -= actual_count
    self.balance += total_revenue
    self.stats["total_revenue"] += total_revenue
    self.add_transaction("дохід", f"Продаж запчастини: {part_name} ({actual_count} шт.)", total_revenue)

    if part_name in self.parts_costs:
      for _ in range(actual_count):
        if self.parts_costs[part_name]:
          self.parts_costs[part_name].pop()

    if self.parts_inventory[part_name] <= 0:
      del self.parts_inventory[part_name]

    messagebox.showinfo(
        "Продаж успішний",
        f"Ви успішно продали {actual_count} шт. '{part_name}' за {total_revenue} грн!",
    )
    self.update_ui_state()
    self.refresh_parts_tab()


  def repair_item(self, idx):
    item = self.inventory[idx]

    for dmg in item["damages"]:
      req_tool_key = self.damage_tool_req.get(dmg)
      if req_tool_key and not self.tools.get(req_tool_key, False):
        t_name, t_cost, _ = self.TOOL_INFO[req_tool_key]
        confirm_buy = messagebox.askyesno(
            "Потрібен інструмент",
            f"Для усунення несправності '{dmg}' потрібен інструмент:\n\n"
            f"🛠️ {t_name}\n"
            f"💰 Вартість: {t_cost} грн\n\n"
            f"Придбати його зараз для майстерні?",
        )
        if confirm_buy:
          if not self.buy_tool(req_tool_key, t_cost, t_name):
            return
        else:
          return

    needed_parts = {}
    for dmg in item["damages"]:
      p_name, _ = self.get_part_details(item["dev"], dmg)
      needed_parts[p_name] = needed_parts.get(p_name, 0) + 1

    missing_parts = []
    for p_name, needed_qty in needed_parts.items():
      have = self.parts_inventory.get(p_name, 0)
      if have < needed_qty:
        missing_parts.append(f"• {p_name} (потрібно {needed_qty}, є {have})")

    if missing_parts:
      self.play_sound("error")
      miss_str = "\n".join(missing_parts)
      messagebox.showwarning(
          "Не вистачає запчастин",
          f"Для ремонту цього пристрою не вистачає деталей на складі:\n\n"
          f"{miss_str}\n\n"
          f"Придбайте їх на Ринку деталей!",
      )
      return

    total_parts_cost = 0
    for p_name, needed_qty in needed_parts.items():
      for _ in range(needed_qty):
        self.parts_inventory[p_name] -= 1
        if self.parts_costs.get(p_name):
          cost = self.parts_costs[p_name].pop()
        else:
          cost = self.catalog.get(p_name, {}).get("base_cost", 300)
        total_parts_cost += cost

      if self.parts_inventory[p_name] <= 0:
        del self.parts_inventory[p_name]

    item["spent_on_repair"] += total_parts_cost

    fail_chance = 0.20 if self.skills.get("soldering_master", False) else 0.35
    if random.random() < fail_chance:
      self.play_sound("error")
      messagebox.showerror(
          "⚠️ НЕВДАЛИЙ РЕМОНТ",
          f"Під час монтажу виникло замикання або бракована деталь зіпсувалася!\n\n"
          f"Деталі на суму {total_parts_cost} грн зіпсовані.\n"
          f"Пристрій залишився несправним. Спробуйте ще раз із новими деталями!",
      )
      self.update_ui_state()
      self.refresh_repair_tab()
      return

    item["is_repaired"] = True
    item["damages"] = []
    item["status"] = "ідеальний"

    self.unlock_achievement("first_repair")
    self.play_sound("repair")
    messagebox.showinfo(
        "Ремонт завершено",
        f"Пристрій {item['dev']} успішно відремонтовано!\n\n"
        f"Використано запчастин на суму: {total_parts_cost} грн.\n"
        f"Його стан тепер ІДЕАЛЬНИЙ.",
    )
    self.update_ui_state()
    self.refresh_repair_tab()


  def repair_client_order(self, idx):
    order = self.client_orders[idx]

    for dmg in order["damages"]:
      req_tool_key = self.damage_tool_req.get(dmg)
      if req_tool_key and not self.tools.get(req_tool_key, False):
        t_name, t_cost, _ = self.TOOL_INFO[req_tool_key]
        confirm_buy = messagebox.askyesno(
            "Потрібен інструмент",
            f"Для ремонту замовлення клієнта ('{dmg}') потрібен інструмент:\n\n"
            f"🛠️ {t_name}\n"
            f"💰 Вартість: {t_cost} грн\n\n"
            f"Придбати його зараз для майстерні?",
        )
        if confirm_buy:
          if not self.buy_tool(req_tool_key, t_cost, t_name):
            return
        else:
          return

    needed_parts = {}
    for dmg in order["damages"]:
      p_name, _ = self.get_part_details(order["dev"], dmg)
      needed_parts[p_name] = needed_parts.get(p_name, 0) + 1

    missing_parts = []
    for p_name, needed_qty in needed_parts.items():
      have = self.parts_inventory.get(p_name, 0)
      if have < needed_qty:
        missing_parts.append(f"• {p_name} (потрібно {needed_qty}, є {have})")

    if missing_parts:
      self.play_sound("error")
      miss_str = "\n".join(missing_parts)
      messagebox.showwarning(
          "Не вистачає запчастин",
          f"Для ремонту клієнтського замовлення не вистачає деталей на складі:\n\n"
          f"{miss_str}\n\n"
          f"Придбайте їх на Ринку деталей!",
      )
      return

    total_parts_cost = 0
    for p_name, needed_qty in needed_parts.items():
      for _ in range(needed_qty):
        self.parts_inventory[p_name] -= 1
        if self.parts_costs.get(p_name):
          cost = self.parts_costs[p_name].pop()
        else:
          cost = self.catalog.get(p_name, {}).get("base_cost", 300)
        total_parts_cost += cost

      if self.parts_inventory[p_name] <= 0:
        del self.parts_inventory[p_name]

    fail_chance = 0.20 if self.skills.get("soldering_master", False) else 0.35
    if random.random() < fail_chance:
      self.play_sound("error")
      messagebox.showerror(
          "⚠️ НЕВДАЛИЙ РЕМОНТ",
          f"Під час пайки клієнтського пристрою деталь вийшла з ладу!\n\n"
          f"Запчастини на {total_parts_cost} грн зіпсовані.\n"
          f"Пристрій не відремонтовано. Спробуйте повторити до завершення терміну замовлення!",
      )
      self.update_ui_state()
      self.refresh_repair_tab()
      return

    order["is_repaired"] = True
    order["damages"] = []

    self.play_sound("repair")
    messagebox.showinfo(
        "Замовлення відремонтовано!",
        f"Замовлення на {order['dev']} успішно відремонтовано!\n\n"
        f"Витрати на деталі: {total_parts_cost} грн.\n"
        f"Оплата ({order['reward']} грн) надійде при поверненні клієнту.",
    )
    self.update_ui_state()
    self.refresh_repair_tab()


  def go_to_market(self):
    self.tabview.set("🏪 Ринок деталей")


  def init_catalog(self):
    self.catalog = {}
    for dmg, d_info in self.parts_data.get("damage_parts", {}).items():
      if "default" in d_info:
        name, cost = d_info["default"]
        self.catalog[name] = {
            "name": name,
            "dev": "Різні пристрої",
            "damage": dmg,
            "base_cost": cost,
        }
      if "overrides" in d_info:
        for dev, (name, cost) in d_info["overrides"].items():
          self.catalog[name] = {
              "name": name,
              "dev": dev,
              "damage": dmg,
              "base_cost": cost,
          }


  def refresh_market_stock(self, manual=False):
    if manual and not self.free_market_refresh_active:
      if self.balance < 100:
        messagebox.showerror(
            "Недостатньо коштів",
            f"Оновлення асортименту ринку коштує 100 грн!\n\n"
            f"Ваш баланс: {self.balance} грн.",
        )
        return
      self.balance -= 100
      self.update_ui_state()

    items = []
    chosen_names = set()
    catalog_list = list(self.catalog.values())
    random.shuffle(catalog_list)

    for cat_item in catalog_list:
      if len(items) >= 20:
        break
      if cat_item["name"] not in chosen_names:
        chosen_names.add(cat_item["name"])
        fluctuation = random.uniform(0.85, 1.25)
        raw_price = int(cat_item["base_cost"] * fluctuation // 10 * 10)
        price = max(100, raw_price)

        items.append({
            "name": cat_item["name"],
            "dev": cat_item["dev"],
            "damage": cat_item["damage"],
            "price": price,
            "bought": False,
        })

    self.market_items = items
    if hasattr(self, "render_market_tab"):
      self.render_market_tab()


  def buy_market_part_analog(self, idx):
    item = self.market_items[idx]
    if item["bought"]:
      return

    max_parts = self.STORAGE_PARTS_LIMITS[self.storage_parts_lvl]
    if sum(self.parts_inventory.values()) >= max_parts:
      messagebox.showwarning(
          "Склад деталей заповнено",
          f"Склад запчастин переповнений ({max_parts}/{max_parts})!",
      )
      return

    price = int(item["price"] * 0.65)
    if self.skills.get("wholesale_partner", False):
      price = int(price * 0.85)

    if self.balance < price:
      messagebox.showerror("Недостатньо коштів", f"Не вистачає коштів! Ціна аналога: {price} грн.")
      return

    self.balance -= price
    self.stats["total_expenses"] += price
    self.add_transaction("витрата", f"Аналог запчастини: {item['name']}", price)
    part_name = item["name"]
    self.parts_inventory[part_name] = self.parts_inventory.get(part_name, 0) + 1
    self.parts_costs.setdefault(part_name, []).append(price)
    item["bought"] = True

    messagebox.showinfo(
        "Аналог придбано",
        f"Ви придбали аналог деталі: {part_name} за {price} грн (-35% знижка)!\n"
        f"Деталь миттєво доставлена на склад запчастин.",
    )
    self.update_ui_state()
    self.render_market_tab()


  def buy_market_part_original(self, idx):
    item = self.market_items[idx]
    if item["bought"]:
      return

    price = item["price"]
    if self.skills.get("wholesale_partner", False):
      price = int(price * 0.85)

    if self.balance < price:
      messagebox.showerror("Недостатньо коштів", f"Не вистачає коштів! Ціна оригіналу: {price} грн.")
      return

    self.balance -= price
    self.stats["total_expenses"] += price
    self.add_transaction("витрата", f"Оригінал запчастини (замовлення): {item['name']}", price)
    item["bought"] = True

    self.pending_deliveries.append({
        "name": item["name"],
        "cost": price,
        "days_left": 1,
    })

    messagebox.showinfo(
        "Замовлення оригіналу оформлено",
        f"Ви замовили оригінальну сертифіковану деталь: {item['name']} за {price} грн!\n\n"
        f"📦 Доставка кур'єром прибуде завтра вранці.",
    )
    self.update_ui_state()
    self.render_market_tab()


  def buy_market_part(self, idx):
    self.buy_market_part_analog(idx)


  def buy_market_accessory(self, acc_key):
    acc_info = self.ACCESSORIES.get(acc_key)
    if not acc_info:
      return

    cost = acc_info["cost"]
    if self.skills.get("wholesale_partner", False):
      cost = int(cost * 0.85)

    if self.balance < cost:
      messagebox.showerror("Недостатньо коштів", f"Для закупівлі оптом потрібно {cost} грн!")
      return

    self.balance -= cost
    self.stats["total_expenses"] += cost
    acc_name = acc_info["name"]
    self.add_transaction("витрата", f"Оптова партія аксесуарів: {acc_name}", cost)

    max_parts = self.STORAGE_PARTS_LIMITS[self.storage_parts_lvl]
    if sum(self.parts_inventory.values()) >= max_parts:
      messagebox.showwarning("Склад деталей заповнено", f"Склад запчастин переповнений ({max_parts}/{max_parts})!")
      return

    part_name = f"Аксесуар: {acc_name}"
    self.parts_inventory[part_name] = self.parts_inventory.get(part_name, 0) + 1
    self.parts_costs.setdefault(part_name, []).append(cost)

    self.play_sound("deal")
    messagebox.showinfo("Аксесуар додано", f"Ви придбали '{acc_name}' за {cost} грн! Збережено на складі деталей.")
    self.update_ui_state()
    if hasattr(self, "render_accessories_tab"):
      self.render_accessories_tab()


  def check_achievement_progress(self):
    if self.balance >= 100000:
      self.unlock_achievement("rich_pawn")
    if self.balance >= 500000:
      self.unlock_achievement("oligarch")


  def show_achievements_modal(self):
    dlg = ctk.CTkToplevel(self)
    dlg.title("🏆 Ваші досягнення та трофеї TechPawn")
    dlg.geometry("640x700")
    dlg.grab_set()
    dlg.resizable(False, False)

    lbl_t = ctk.CTkLabel(dlg, text="🏆 Зал слави та досягнень", font=ctk.CTkFont(size=22, weight="bold"))
    lbl_t.pack(pady=(15, 5))

    unlocked_count = sum(1 for a in self.achievements.values() if a.get("unlocked", False))
    total_count = len(self.achievements)

    lbl_stat = ctk.CTkLabel(
        dlg,
        text=f"Розблоковано: {unlocked_count} з {total_count} трофеїв ({int(unlocked_count/total_count*100)}%)",
        font=ctk.CTkFont(size=14, weight="bold"),
        text_color="#f39c12",
    )
    lbl_stat.pack(pady=(0, 10))

    scroll = ctk.CTkScrollableFrame(dlg, label_text="Список почесних досягнень майстерні")
    scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    for ach_id, data in self.achievements.items():
      is_unl = data.get("unlocked", False)
      card = ctk.CTkFrame(scroll, corner_radius=10, fg_color="#2c3e50" if is_unl else "#1e272e")
      card.pack(fill="x", padx=10, pady=5)

      row = ctk.CTkFrame(card, fg_color="transparent")
      row.pack(fill="x", padx=12, pady=8)

      icon_lbl = ctk.CTkLabel(row, text=data.get("icon", "🏆"), font=ctk.CTkFont(size=26))
      icon_lbl.pack(side="left", padx=(5, 12))

      info_box = ctk.CTkFrame(row, fg_color="transparent")
      info_box.pack(side="left", fill="both", expand=True)

      title_color = "#f1c40f" if is_unl else "#7f8c8d"
      t_lbl = ctk.CTkLabel(info_box, text=data.get("title", ""), font=ctk.CTkFont(size=15, weight="bold"), text_color=title_color, anchor="w")
      t_lbl.pack(anchor="w")

      d_lbl = ctk.CTkLabel(info_box, text=data.get("desc", ""), font=ctk.CTkFont(size=12), text_color="#bdc3c7", anchor="w")
      d_lbl.pack(anchor="w")

      st_box = ctk.CTkFrame(row, fg_color="transparent")
      st_box.pack(side="right", padx=10)

      if is_unl:
        date_str = data.get("date", "") or "Отримано"
        s_lbl = ctk.CTkLabel(st_box, text=f"✅ {date_str}", font=ctk.CTkFont(size=12, weight="bold"), text_color="#2ecc71")
        s_lbl.pack()
      else:
        s_lbl = ctk.CTkLabel(st_box, text="🔒 Заблоковано", font=ctk.CTkFont(size=12), text_color="#95a5a6")
        s_lbl.pack()
