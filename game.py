import random
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class PawnshopGame(ctk.CTk):

  def __init__(self):
    super().__init__()

    self.title("📱 TechPawn: Скупка, Ремонт та Продаж")
    self.geometry("950x750")
    self.resizable(False, False)

    self.balance = 30000
    self.inventory = []

    self.cur_dev = ""
    self.cur_base_price = 0
    self.cur_fair_price = 0
    self.cur_real_status = "нормальний"
    self.cur_dmg_list = []
    self.cur_est_repair_min = 0
    self.cur_est_repair_max = 0

    self.devices = {
        "Смартфон": (4000, 25000),
        "Ноутбук": (10000, 45000),
        "Планшет": (5000, 20000),
        "Смарт-годинник": (2000, 10000),
        "Монітор": (3000, 15000),
        "Ігрова консоль": (8000, 22000),
        "Геймпад": (1000, 4500),
        "Бездротові навушники": (1000, 6000),
    }

    self.all_damages = {
        "Мікроцарапини на корпусі": {
            "mult": 0.95,
            "cost_pct": (0.05, 0.10),
            "allowed": [
                "Смартфон",
                "Ноутбук",
                "Планшет",
                "Смарт-годинник",
                "Монітор",
                "Ігрова консоль",
                "Геймпад",
                "Бездротові навушники",
            ],
        },
        "Тріщина на екрані": {
            "mult": 0.70,
            "cost_pct": (0.20, 0.35),
            "allowed": [
                "Смартфон",
                "Ноутбук",
                "Планшет",
                "Смарт-годинник",
                "Монітор",
            ],
        },
        "Глибокі сколи корпусу": {
            "mult": 0.85,
            "cost_pct": (0.10, 0.20),
            "allowed": [
                "Смартфон",
                "Ноутбук",
                "Планшет",
                "Смарт-годинник",
                "Монітор",
                "Ігрова консоль",
                "Геймпад",
            ],
        },
        "Зігнутий навпіл корпус": {
            "mult": 0.30,
            "cost_pct": (0.40, 0.60),
            "allowed": ["Смартфон", "Планшет"],
        },
        "Зношена батарея (<70%)": {
            "mult": 0.80,
            "cost_pct": (0.10, 0.20),
            "allowed": [
                "Смартфон",
                "Ноутбук",
                "Планшет",
                "Смарт-годинник",
                "Геймпад",
                "Бездротові навушники",
            ],
        },
        "Не заряджається (роз'єм)": {
            "mult": 0.75,
            "cost_pct": (0.10, 0.18),
            "allowed": [
                "Смартфон",
                "Ноутбук",
                "Планшет",
                "Смарт-годинник",
                "Ігрова консоль",
                "Геймпад",
                "Бездротові навушники",
            ],
        },
        "Не вмикається взагалі": {
            "mult": 0.40,
            "cost_pct": (0.30, 0.50),
            "allowed": [
                "Смартфон",
                "Ноутбук",
                "Планшет",
                "Смарт-годинник",
                "Монітор",
                "Ігрова консоль",
                "Геймпад",
                "Бездротові навушники",
            ],
        },
        "Плями / вигорання матриці": {
            "mult": 0.65,
            "cost_pct": (0.25, 0.40),
            "allowed": [
                "Смартфон",
                "Ноутбук",
                "Планшет",
                "Смарт-годинник",
                "Монітор",
            ],
        },
        "Утоплений / сліди корозії": {
            "mult": 0.35,
            "cost_pct": (0.35, 0.55),
            "allowed": [
                "Смартфон",
                "Ноутбук",
                "Планшет",
                "Смарт-годинник",
                "Геймпад",
                "Бездротові навушники",
            ],
        },
        "Заблокований (пароль / акаунт)": {
            "mult": 0.50,
            "cost_pct": (0.15, 0.30),
            "allowed": ["Смартфон", "Ноутбук", "Планшет", "Смарт-годинник"],
        },
        "Загублено один навушник": {
            "mult": 0.60,
            "cost_pct": (0.25, 0.35),
            "allowed": ["Бездротові навушники"],
        },
        "Рипить / тихий динамік": {
            "mult": 0.80,
            "cost_pct": (0.10, 0.20),
            "allowed": [
                "Смартфон",
                "Ноутбук",
                "Планшет",
                "Бездротові навушники",
            ],
        },
        "Дрифт стіків / зламані кнопки": {
            "mult": 0.75,
            "cost_pct": (0.15, 0.25),
            "allowed": ["Ігрова консоль", "Геймпад"],
        },
    }

    self.status_options = [
        "ідеальний",
        "хороший",
        "нормальний",
        "поганий",
        "жахливий",
    ]

    self.create_widgets()
    self.gen_item()

  def create_widgets(self):
    self.top_frame = ctk.CTkFrame(self, corner_radius=15)
    self.top_frame.pack(fill="x", padx=20, pady=10)

    self.lbl_balance = ctk.CTkLabel(
        self.top_frame,
        text=f"💰 Баланс: {self.balance} грн",
        font=ctk.CTkFont(size=20, weight="bold"),
        text_color="#2ecc71",
    )
    self.lbl_balance.pack(side="left", padx=20, pady=12)

    self.lbl_inv_count = ctk.CTkLabel(
        self.top_frame,
        text=f"📦 Товарів на складі: {len(self.inventory)}",
        font=ctk.CTkFont(size=16),
    )
    self.lbl_inv_count.pack(side="right", padx=20, pady=12)

    self.tabview = ctk.CTkTabview(self, width=910, height=640)
    self.tabview.pack(padx=20, pady=(0, 15))

    self.tab_buy = self.tabview.add("📥 Скупка")
    self.tab_sell = self.tabview.add("🛒 Склад та Продаж")
    self.tab_repair = self.tabview.add("🔧 Ремонт")

    self.setup_buy_tab()
    self.setup_sell_tab()
    self.setup_repair_tab()

  def setup_buy_tab(self):
    main_frame = ctk.CTkFrame(self.tab_buy, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    left_card = ctk.CTkFrame(main_frame, corner_radius=15)
    left_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

    lbl_card_title = ctk.CTkLabel(
        left_card,
        text="📥 Огляд пристрою від клієнта",
        font=ctk.CTkFont(size=18, weight="bold"),
    )
    lbl_card_title.pack(anchor="w", padx=20, pady=(15, 5))

    self.txt_item_info = ctk.CTkTextbox(
        left_card, font=ctk.CTkFont(size=15), wrap="word"
    )
    self.txt_item_info.pack(fill="both", expand=True, padx=15, pady=10)
    self.txt_item_info.configure(state="disabled")

    right_card = ctk.CTkFrame(main_frame, corner_radius=15, width=380)
    right_card.pack(side="right", fill="both", expand=True, padx=(10, 0))

    lbl_form_title = ctk.CTkLabel(
        right_card,
        text="🤝 Купівля пристрою",
        font=ctk.CTkFont(size=18, weight="bold"),
    )
    lbl_form_title.pack(anchor="w", padx=20, pady=(15, 15))

    lbl_price_input = ctk.CTkLabel(
        right_card,
        text="Запропонувати свою ціну (грн):",
        font=ctk.CTkFont(size=14),
    )
    lbl_price_input.pack(anchor="w", padx=20, pady=(5, 2))

    self.entry_price = ctk.CTkEntry(
        right_card, placeholder_text="Введіть ціну...", height=38
    )
    self.entry_price.pack(fill="x", padx=20, pady=(0, 15))

    btn_submit = ctk.CTkButton(
        right_card,
        text="Купити пристрій",
        font=ctk.CTkFont(size=16, weight="bold"),
        height=45,
        fg_color="#27ae60",
        hover_color="#219150",
        command=self.buy_item,
    )
    btn_submit.pack(fill="x", padx=20, pady=10)

    btn_skip = ctk.CTkButton(
        right_card,
        text="Відмовити клієнту",
        font=ctk.CTkFont(size=14),
        height=35,
        fg_color="#e74c3c",
        hover_color="#c0392b",
        command=self.skip_item,
    )
    btn_skip.pack(fill="x", padx=20, pady=(0, 15))

    self.lbl_buy_result = ctk.CTkLabel(
        right_card,
        text="",
        font=ctk.CTkFont(size=13),
        wraplength=320,
        text_color="#f39c12",
    )
    self.lbl_buy_result.pack(fill="x", padx=20, pady=10)

  def setup_sell_tab(self):
    main_frame = ctk.CTkFrame(self.tab_sell, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    self.scroll_sell = ctk.CTkScrollableFrame(
        main_frame, label_text="Товари на складі"
    )
    self.scroll_sell.pack(fill="both", expand=True)

  def setup_repair_tab(self):
    main_frame = ctk.CTkFrame(self.tab_repair, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    self.scroll_repair = ctk.CTkScrollableFrame(
        main_frame, label_text="Пристрої, що потребують ремонту"
    )
    self.scroll_repair.pack(fill="both", expand=True)

  def gen_item(self):
    self.cur_dev = random.choice(list(self.devices.keys()))
    min_p, max_p = self.devices[self.cur_dev]
    self.cur_base_price = random.randint(min_p // 100, max_p // 100) * 100

    valid_damages = [
        dmg_name
        for dmg_name, data in self.all_damages.items()
        if self.cur_dev in data["allowed"]
    ]

    dmg_count = random.choices([0, 1, 2, 3], weights=[25, 40, 25, 10])[0]
    self.cur_dmg_list = random.sample(
        valid_damages, k=min(dmg_count, len(valid_damages))
    )

    multiplier = 1.0
    est_min = 0
    est_max = 0

    for dmg in self.cur_dmg_list:
      data = self.all_damages[dmg]
      multiplier *= data["mult"]
      p_min, p_max = data["cost_pct"]
      est_min += self.cur_base_price * p_min
      est_max += self.cur_base_price * p_max

    self.cur_est_repair_min = int(est_min * 0.9)
    self.cur_est_repair_max = int(est_max * 1.1)
    self.cur_fair_price = int(self.cur_base_price * multiplier)

    if dmg_count == 0:
      self.cur_real_status = "ідеальний"
    elif dmg_count == 1:
      self.cur_real_status = "хороший"
    elif dmg_count == 2:
      self.cur_real_status = "нормальний"
    else:
      self.cur_real_status = "поганий"

    client_markup = random.uniform(0.85, 1.2)
    self.cur_client_price = int(self.cur_fair_price * client_markup)

    self.txt_item_info.configure(state="normal")
    self.txt_item_info.delete("1.0", tk.END)

    dmg_text = (
        "\n".join([f"  • {d}" for d in self.cur_dmg_list])
        if self.cur_dmg_list
        else "  • Ідеальний стан, без дефектів."
    )

    repair_est_text = (
        f"{self.cur_est_repair_min} - {self.cur_est_repair_max} грн"
        if self.cur_dmg_list
        else "Ремонт не потрібен"
    )

    info_str = (
        f"📱 Пристрій: {self.cur_dev}\n"
        f"💵 Ринкова ціна (ідеальний): ~{self.cur_base_price} грн\n"
        f"🗣️ Бажана ціна клієнта: {self.cur_client_price} грн\n"
        f"🛠️ Орієнтовна вартість ремонту: {repair_est_text}\n\n"
        f"🔍 Виявлені пошкодження:\n{dmg_text}"
    )

    self.txt_item_info.insert("1.0", info_str)
    self.txt_item_info.configure(state="disabled")
    self.entry_price.delete(0, tk.END)
    self.entry_price.insert(0, str(self.cur_client_price))

  def buy_item(self):
    try:
      offer = int(self.entry_price.get())
    except ValueError:
      messagebox.showwarning(
          "Помилка", "Будь ласка, введіть коректну числову ціну!"
      )
      return

    if offer > self.balance:
      messagebox.showerror("Помилка", "У вас недостатньо коштів на балансі!")
      return

    if offer < self.cur_fair_price * 0.6:
      self.lbl_buy_result.configure(
          text="😠 Клієнт обурився занадто низькою ціною і пішов!"
      )
      self.gen_item()
      return

    self.balance -= offer

    actual_repair_cost = 0
    for dmg in self.cur_dmg_list:
      data = self.all_damages[dmg]
      p_min, p_max = data["cost_pct"]
      actual_repair_cost += int(
          self.cur_base_price * random.uniform(p_min, p_max)
      )

    item_data = {
        "dev": self.cur_dev,
        "buy_price": offer,
        "base_price": self.cur_base_price,
        "fair_price": self.cur_fair_price,
        "status": self.cur_real_status,
        "damages": list(self.cur_dmg_list),
        "actual_repair_cost": actual_repair_cost,
        "spent_on_repair": 0,
        "is_repaired": len(self.cur_dmg_list) == 0,
    }

    self.inventory.append(item_data)
    self.lbl_buy_result.configure(
        text=f"✅ Успішно куплено за {offer} грн і відправлено на склад!"
    )

    self.update_ui_state()
    self.gen_item()

  def skip_item(self):
    self.lbl_buy_result.configure(text="🗑️ Ви відмовилися від угоди.")
    self.gen_item()

  def update_ui_state(self):
    self.lbl_balance.configure(text=f"💰 Баланс: {self.balance} грн")
    self.lbl_inv_count.configure(
        text=f"📦 Товарів на складі: {len(self.inventory)}"
    )

    self.refresh_sell_tab()
    self.refresh_repair_tab()

    if self.balance <= 0 and len(self.inventory) == 0:
      messagebox.showerror("БАНКРУТ!", "У вас закінчилися гроші та товари!")
      self.destroy()

  def refresh_sell_tab(self):
    for widget in self.scroll_sell.winfo_children():
      widget.destroy()

    if not self.inventory:
      lbl = ctk.CTkLabel(
          self.scroll_sell,
          text="Склад порожній. Купіть товари на вкладці 'Скупка'.",
          font=ctk.CTkFont(size=14),
      )
      lbl.pack(pady=20)
      return

    for idx, item in enumerate(self.inventory):
      card = ctk.CTkFrame(self.scroll_sell, corner_radius=10)
      card.pack(fill="x", padx=10, pady=5)

      total_cost = item["buy_price"] + item["spent_on_repair"]

      if item["spent_on_repair"] > 0:
        cost_info = (
            f"Купівля: {item['buy_price']} грн | Ремонт:"
            f" {item['spent_on_repair']} грн | 💰 Загальні витрати: {total_cost}"
            " грн"
        )
      else:
        cost_info = (
            f"Купівля: {item['buy_price']} грн | 💰 Загальні витрати:"
            f" {total_cost} грн"
        )

      status_str = (
          "✨ Відремонтовано"
          if item["is_repaired"]
          else f"⚠️ Стан: {item['status']}"
      )

      info_txt = f"📱 {item['dev']} | {status_str}\n📊 {cost_info}"

      lbl = ctk.CTkLabel(
          card,
          text=info_txt,
          font=ctk.CTkFont(size=13, weight="bold"),
          anchor="w",
          justify="left",
      )
      lbl.pack(side="left", padx=15, pady=10)

      entry_sell = ctk.CTkEntry(
          card, placeholder_text="Ціна продажу", width=120
      )
      entry_sell.pack(side="right", padx=10, pady=10)

      default_sell = (
          int(item["base_price"] * 1.1)
          if item["is_repaired"]
          else int(item["fair_price"] * 1.15)
      )
      entry_sell.insert(0, str(default_sell))

      btn_sell = ctk.CTkButton(
          card,
          text="Продати",
          width=90,
          fg_color="#27ae60",
          hover_color="#219150",
          command=lambda i=idx, e=entry_sell: self.sell_item(i, e),
      )
      btn_sell.pack(side="right", padx=5, pady=10)

  def sell_item(self, idx, entry_widget):
    try:
      sell_price = int(entry_widget.get())
    except ValueError:
      messagebox.showwarning("Помилка", "Введіть коректну ціну продажу!")
      return

    item = self.inventory[idx]

    max_acceptable_price = (
        item["base_price"] * 1.15
        if item["is_repaired"]
        else item["fair_price"] * 1.25
    )

    if sell_price > max_acceptable_price:
      messagebox.showwarning(
          "Ринковий відгук",
          "Ціна занадто висока! Покупці відмовляються купувати за цією ціною.",
      )
      return

    total_cost = item["buy_price"] + item["spent_on_repair"]
    profit = sell_price - total_cost
    self.balance += sell_price
    self.inventory.pop(idx)

    profit_str = (
        f"Чистий прибуток: +{profit} грн."
        if profit >= 0
        else f"Збиток: {profit} грн."
    )

    messagebox.showinfo(
        "Успішний продаж!",
        f"Ви продали {item['dev']} за {sell_price} грн!\n{profit_str}",
    )
    self.update_ui_state()

  def refresh_repair_tab(self):
    for widget in self.scroll_repair.winfo_children():
      widget.destroy()

    repair_needed = [
        (idx, item)
        for idx, item in enumerate(self.inventory)
        if not item["is_repaired"]
    ]

    if not repair_needed:
      lbl = ctk.CTkLabel(
          self.scroll_repair,
          text="Немає пристроїв, що потребують ремонту.",
          font=ctk.CTkFont(size=14),
      )
      lbl.pack(pady=20)
      return

    for idx, item in repair_needed:
      card = ctk.CTkFrame(self.scroll_repair, corner_radius=10)
      card.pack(fill="x", padx=10, pady=5)

      dmg_str = ", ".join(item["damages"])
      info_txt = (
          f"📱 {item['dev']}\nПошкодження: {dmg_str}\nТочна вартість ремонту:"
          f" {item['actual_repair_cost']} грн"
      )

      lbl = ctk.CTkLabel(
          card, text=info_txt, font=ctk.CTkFont(size=13), justify="left"
      )
      lbl.pack(side="left", padx=15, pady=10)

      btn_do_repair = ctk.CTkButton(
          card,
          text=f"Відремонтувати ({item['actual_repair_cost']} грн)",
          fg_color="#f39c12",
          hover_color="#d35400",
          command=lambda i=idx: self.repair_item(i),
      )
      btn_do_repair.pack(side="right", padx=15, pady=10)

  def repair_item(self, idx):
    item = self.inventory[idx]
    cost = item["actual_repair_cost"]

    if self.balance < cost:
      messagebox.showerror(
          "Недостатньо коштів", "У вас недостатньо коштів на балансі для ремонту!"
      )
      return

    self.balance -= cost
    item["spent_on_repair"] = cost
    item["is_repaired"] = True
    item["damages"] = []
    item["status"] = "ідеальний"

    messagebox.showinfo(
        "Ремонт завершено",
        f"Пристрій {item['dev']} успішно відремонтовано!\nЙого стан тепер"
        " ІДЕАЛЬНИЙ.",
    )
    self.update_ui_state()


if __name__ == "__main__":
  app = PawnshopGame()
  app.mainloop()