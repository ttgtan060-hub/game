import random
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class PawnshopGame(ctk.CTk):

  def __init__(self):
    super().__init__()

    self.title("📱 TechPawn: Скупка та Оцінка Техніки")
    self.geometry("900x700")
    self.resizable(False, False)

    self.balance = 25000
    self.score = 0
    self.penalties = 0
    self.day = 1

    self.cur_dev = ""
    self.cur_base_price = 0
    self.cur_fair_price = 0
    self.cur_real_status = "нормальний"
    self.cur_dmg_list = []

    self.devices = {
        "Смартфон": (4000, 25000),
        "Ноутбук": (10000, 45000),
        "Планшет": (5000, 20000),
        "Смарт-годинник": (2000, 10000),
        "Монітор": (3000, 15000),
        "Ігрова консоль": (8000, 22000),
        "Бездротові навушники": (1000, 6000),
    }

    self.all_damages = {
        "Мікроцарапини на склі": 0.95,
        "Тріщина на екрані": 0.75,
        "Глибокі сколи корпусу": 0.85,
        "Зігнутий навпіл корпус": 0.30,
        "Зношена батарея (<70%)": 0.80,
        "Не заряджається (пошкоджений роз'єм)": 0.70,
        "Не вмикається взагалі": 0.40,
        "Плями на матриці / вигорання": 0.65,
        "Утоплений / сліди корозії": 0.35,
        "Не працює Wi-Fi / Bluetooth": 0.80,
        "Заблокований (забули пароль)": 0.50,
    }

    self.status_options = [
        "ідеальний",
        "хороший",
        "нормальний",
        "поганий",
        "жахливий",
    ]
    self.status_ranks = {
        "ідеальний": 5,
        "хороший": 4,
        "нормальний": 3,
        "поганий": 2,
        "жахливий": 1,
    }

    self.create_widgets()
    self.gen_item()

  def create_widgets(self):
    self.top_frame = ctk.CTkFrame(self, corner_radius=15)
    self.top_frame.pack(fill="x", padx=20, pady=15)

    self.lbl_balance = ctk.CTkLabel(
        self.top_frame,
        text=f"💰 Баланс: {self.balance} грн",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color="#2ecc71",
    )
    self.lbl_balance.pack(side="left", padx=20, pady=15)

    self.lbl_score = ctk.CTkLabel(
        self.top_frame,
        text=f"⭐ Бали: {self.score}",
        font=ctk.CTkFont(size=18, weight="bold"),
    )
    self.lbl_score.pack(side="left", padx=20, pady=15)

    self.lbl_penalties = ctk.CTkLabel(
        self.top_frame,
        text=f"⚠️ Штрафи: {self.penalties}/3",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color="#e74c3c",
    )
    self.lbl_penalties.pack(side="right", padx=20, pady=15)

    self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
    self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

    self.left_card = ctk.CTkFrame(self.main_frame, corner_radius=15, width=420)
    self.left_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

    self.lbl_card_title = ctk.CTkLabel(
        self.left_card,
        text="📥 Огляд пристрою від клієнта",
        font=ctk.CTkFont(size=18, weight="bold"),
    )
    self.lbl_card_title.pack(anchor="w", padx=20, pady=(15, 5))

    self.txt_item_info = ctk.CTkTextbox(
        self.left_card,
        font=ctk.CTkFont(size=15),
        wrap="word",
        activate_scrollbars=True,
    )
    self.txt_item_info.pack(fill="both", expand=True, padx=15, pady=10)
    self.txt_item_info.configure(state="disabled")

    self.right_card = ctk.CTkFrame(
        self.main_frame, corner_radius=15, width=400
    )
    self.right_card.pack(side="right", fill="both", expand=True, padx=(10, 0))

    self.lbl_form_title = ctk.CTkLabel(
        self.right_card,
        text="📝 Оціночний лист",
        font=ctk.CTkFont(size=18, weight="bold"),
    )
    self.lbl_form_title.pack(anchor="w", padx=20, pady=(15, 15))

    self.lbl_price_input = ctk.CTkLabel(
        self.right_card,
        text="Запропонувати ціну купівлі (грн):",
        font=ctk.CTkFont(size=14),
    )
    self.lbl_price_input.pack(anchor="w", padx=20, pady=(5, 2))

    self.entry_price = ctk.CTkEntry(
        self.right_card, placeholder_text="Наприклад: 5500", height=38
    )
    self.entry_price.pack(fill="x", padx=20, pady=(0, 15))

    self.lbl_status_input = ctk.CTkLabel(
        self.right_card,
        text="Визначте реальний стан:",
        font=ctk.CTkFont(size=14),
    )
    self.lbl_status_input.pack(anchor="w", padx=20, pady=(5, 2))

    self.combo_status = ctk.CTkOptionMenu(
        self.right_card, values=self.status_options, height=38
    )
    self.combo_status.pack(fill="x", padx=20, pady=(0, 20))
    self.combo_status.set(self.status_options[2])

    self.btn_submit = ctk.CTkButton(
        self.right_card,
        text="🤝 Укласти угоду",
        font=ctk.CTkFont(size=16, weight="bold"),
        height=45,
        fg_color="#27ae60",
        hover_color="#219150",
        command=self.process_deal,
    )
    self.btn_submit.pack(fill="x", padx=20, pady=10)

    self.btn_skip = ctk.CTkButton(
        self.right_card,
        text="❌ Відмовити клієнту",
        font=ctk.CTkFont(size=14),
        height=35,
        fg_color="#e74c3c",
        hover_color="#c0392b",
        command=self.skip_deal,
    )
    self.btn_skip.pack(fill="x", padx=20, pady=(0, 15))

    self.bottom_frame = ctk.CTkFrame(self, corner_radius=15, height=120)
    self.bottom_frame.pack(fill="x", padx=20, pady=(5, 15))

    self.lbl_result = ctk.CTkLabel(
        self.bottom_frame,
        text="Очікування дій оцінщика...",
        font=ctk.CTkFont(size=14),
        justify="left",
    )
    self.lbl_result.pack(padx=20, pady=15, anchor="w")

  def gen_item(self):
    self.cur_dev = random.choice(list(self.devices.keys()))
    min_p, max_p = self.devices[self.cur_dev]
    self.cur_base_price = random.randint(min_p // 100, max_p // 100) * 100

    dmg_count = random.choices([0, 1, 2, 3, 4], weights=[20, 35, 25, 15, 5])[0]
    available_damages = list(self.all_damages.keys())

    if self.cur_dev in ["Монітор", "Бездротові навушники"]:
      if "Зігнутий навпіл корпус" in available_damages:
        available_damages.remove("Зігнутий навпіл корпус")

    self.cur_dmg_list = random.sample(
        available_damages, k=min(dmg_count, len(available_damages))
    )

    multiplier = 1.0
    for dmg in self.cur_dmg_list:
      multiplier *= self.all_damages[dmg]

    self.cur_fair_price = int(self.cur_base_price * multiplier)

    if dmg_count == 0:
      self.cur_real_status = "ідеальний"
    elif dmg_count == 1:
      self.cur_real_status = "хороший"
    elif dmg_count == 2:
      self.cur_real_status = "нормальний"
    elif dmg_count == 3:
      self.cur_real_status = "поганий"
    else:
      self.cur_real_status = "жахливий"

    client_markup = random.uniform(0.9, 1.25)
    self.cur_client_price = int(self.cur_fair_price * client_markup)

    self.txt_item_info.configure(state="normal")
    self.txt_item_info.delete("1.0", tk.END)

    dmg_text = (
        "\n".join([f"  • {d}" for d in self.cur_dmg_list])
        if self.cur_dmg_list
        else "  • Ідеальний стан, без дефектів."
    )

    info_str = (
        f"📱 Пристрій: {self.cur_dev}\n"
        f"💵 Базовий орієнтир: ~{self.cur_base_price} грн\n"
        f"🗣️ Бажана ціна клієнта: {self.cur_client_price} грн\n\n"
        f"🔍 Виявлені пошкодження:\n{dmg_text}"
    )

    self.txt_item_info.insert("1.0", info_str)
    self.txt_item_info.configure(state="disabled")
    self.entry_price.delete(0, tk.END)

  def process_deal(self):
    try:
      player_price = int(self.entry_price.get())
    except ValueError:
      messagebox.showwarning(
          "Помилка", "Будь ласка, введіть коректну числову ціну!"
      )
      return

    if player_price > self.balance:
      messagebox.showerror("Помилка", "У вас недостатньо коштів на балансі!")
      return

    selected_status = self.combo_status.get()
    player_rank = self.status_ranks[selected_status]
    real_rank = self.status_ranks[self.cur_real_status]
    rank_diff = abs(player_rank - real_rank)

    got_penalty = False
    msg_price = ""
    msg_status = ""

    if player_price > self.cur_client_price * 1.1:
      got_penalty = True
      msg_price = (
          "❌ Занадто висока ціна! Ви сильно переплатили за цей пристрій."
      )
    elif player_price < self.cur_fair_price * 0.6:
      msg_price = (
          "😠 Клієнт розізлився через занадто низьку пропозицію і пішов!"
      )
      self.end_turn(msg_price, success=False)
      return
    else:
      msg_price = "✅ Ціна була успішно узгоджена з клієнтом."

    if rank_diff == 0:
      self.score += 3
      msg_status = f"🎯 Стан оцінено ідеально ({selected_status})! (+3 бали)"
    elif rank_diff == 1:
      self.score += 1
      msg_status = f"👌 Стан оцінено близько до правди (Реальний: {self.cur_real_status}). (+1 бал)"
    else:
      got_penalty = True
      msg_status = f"❌ Груба помилка в оцінці стану! (Реальний стан був: {self.cur_real_status})."

    if not got_penalty:
      resell_price = int(self.cur_fair_price * 1.25)
      profit = resell_price - player_price
      self.balance += profit
      msg_overall = (
          f"✨ Угода вигідна! Ви купили за {player_price} грн і продали за"
          f" {resell_price} грн (Прибуток: +{profit} грн)."
      )
    else:
      self.penalties += 1
      self.balance -= player_price // 2
      msg_overall = f"⚠️ Ви отримали ШТРАФ! (Збитки від оцінки: -{player_price // 2} грн)"

    self.end_turn(
        f"{msg_price}\n{msg_status}\n{msg_overall}", success=not got_penalty
    )

  def skip_deal(self):
    self.end_turn("🗑️ Ви відмовилися від угоди. Клієнт пішов.", success=True)

  def end_turn(self, result_text, success=True):
    self.lbl_balance.configure(text=f"💰 Баланс: {self.balance} грн")
    self.lbl_score.configure(text=f"⭐ Бали: {self.score}")
    self.lbl_penalties.configure(text=f"⚠️ Штрафи: {self.penalties}/3")
    self.lbl_result.configure(text=result_text)

    if self.penalties >= 3:
      messagebox.showerror(
          "ПРОГРАШ!", "Ви отримали 3 штрафи! Ваш ломбард зачинено."
      )
      self.destroy()
      return
    elif self.balance <= 0:
      messagebox.showerror("БАНКРУТ!", "У вас закінчилися гроші! Гра закінчена.")
      self.destroy()
      return

    self.gen_item()


if __name__ == "__main__":
  app = PawnshopGame()
  app.mainloop()