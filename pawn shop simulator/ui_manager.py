import os
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk


class UiManagerMixin:

  def setup_ui_containers(self):
    self.container = ctk.CTkFrame(self)
    self.container.pack(fill="both", expand=True)

    self.frame_menu = ctk.CTkFrame(self.container)
    self.frame_guide = ctk.CTkFrame(self.container)
    self.frame_game = ctk.CTkFrame(self.container)
    self.frame_night = ctk.CTkFrame(self.container)
    self.frame_saves = ctk.CTkFrame(self.container)

    for f in (
        self.frame_menu,
        self.frame_guide,
        self.frame_game,
        self.frame_night,
        self.frame_saves,
    ):
      f.place(x=0, y=0, relwidth=1, relheight=1)

    self.setup_menu_screen()
    self.setup_guide_screen()
    self.setup_game_screen()
    self.setup_night_screen()
    self.setup_saves_screen()


  def show_screen(self, screen_name):
    self.current_screen_name = screen_name
    frames = {
        "menu": self.frame_menu,
        "guide": self.frame_guide,
        "game": self.frame_game,
        "night": self.frame_night,
        "saves": self.frame_saves,
    }
    target = frames.get(screen_name)
    if target:
      target.tkraise()

    if screen_name == "saves":
      self.refresh_saves_list()
    elif screen_name == "night":
      self.render_night_screen()
    elif screen_name == "game":
      self.update_ui_state()


  def setup_menu_screen(self):
    center_box = ctk.CTkFrame(self.frame_menu, corner_radius=20, width=460, height=580)
    center_box.place(relx=0.5, rely=0.5, anchor="center")
    center_box.pack_propagate(False)

    lbl_logo = ctk.CTkLabel(
        center_box,
        text="📱 TechPawn",
        font=ctk.CTkFont(size=36, weight="bold"),
        text_color="#3498db",
    )
    lbl_logo.pack(pady=(35, 5))

    lbl_sub = ctk.CTkLabel(
        center_box,
        text="Симулятор ломбарду, ремонту та збірки ПК",
        font=ctk.CTkFont(size=14),
        text_color="#95a5a6",
    )
    lbl_sub.pack(pady=(0, 25))

    btn_new_game = ctk.CTkButton(
        center_box,
        text="▶️ Нова гра",
        font=ctk.CTkFont(size=18, weight="bold"),
        height=48,
        width=320,
        fg_color="#27ae60",
        hover_color="#219150",
        command=self.start_new_game,
    )
    btn_new_game.pack(pady=8)

    btn_saves = ctk.CTkButton(
        center_box,
        text="📂 Збереження",
        font=ctk.CTkFont(size=18, weight="bold"),
        height=48,
        width=320,
        fg_color="#2980b9",
        hover_color="#1f618d",
        command=lambda: self.show_screen("saves"),
    )
    btn_saves.pack(pady=8)

    btn_achievements = ctk.CTkButton(
        center_box,
        text="🏆 Досягнення",
        font=ctk.CTkFont(size=18, weight="bold"),
        height=48,
        width=320,
        fg_color="#f39c12",
        hover_color="#d68910",
        command=self.show_achievements_modal,
    )
    btn_achievements.pack(pady=8)

    btn_guide = ctk.CTkButton(
        center_box,
        text="📖 Інструкція до гри",
        font=ctk.CTkFont(size=18, weight="bold"),
        height=48,
        width=320,
        fg_color="#8e44ad",
        hover_color="#732d91",
        command=lambda: self.show_screen("guide"),
    )
    btn_guide.pack(pady=8)

    btn_exit = ctk.CTkButton(
        center_box,
        text="❌ Вихід",
        font=ctk.CTkFont(size=16),
        height=42,
        width=320,
        fg_color="#c0392b",
        hover_color="#962d22",
        command=self.destroy,
    )
    btn_exit.pack(pady=(12, 20))


  def setup_guide_screen(self):
    header = ctk.CTkFrame(self.frame_guide, corner_radius=12)
    header.pack(fill="x", padx=25, pady=(20, 10))

    btn_back = ctk.CTkButton(
        header,
        text="⬅️ Назад",
        font=ctk.CTkFont(size=15, weight="bold"),
        width=120,
        height=40,
        fg_color="#7f8c8d",
        hover_color="#636e72",
        command=lambda: self.show_screen(getattr(self, "previous_screen", "menu")),
    )
    btn_back.pack(side="left", padx=15, pady=10)

    lbl_title = ctk.CTkLabel(
        header,
        text="📖 Повна інструкція, механіки та секрети гри TechPawn",
        font=ctk.CTkFont(size=20, weight="bold"),
        text_color="#3498db",
    )
    lbl_title.pack(side="left", padx=15, pady=10)

    scroll = ctk.CTkScrollableFrame(
        self.frame_guide, label_text="Правила гри, шанси, економіка та підказки"
    )
    scroll.pack(fill="both", expand=True, padx=25, pady=(0, 20))

    def add_guide_section(title, lines, color="#3498db"):
      card = ctk.CTkFrame(scroll, corner_radius=12)
      card.pack(fill="x", padx=10, pady=8)

      lbl_sec_title = ctk.CTkLabel(
          card,
          text=title,
          font=ctk.CTkFont(size=16, weight="bold"),
          text_color=color,
          anchor="w",
      )
      lbl_sec_title.pack(fill="x", padx=15, pady=(12, 6))

      for line in lines:
        lbl_line = ctk.CTkLabel(
            card,
            text=line,
            font=ctk.CTkFont(size=13),
            anchor="w",
            justify="left",
            wraplength=880,
        )
        lbl_line.pack(fill="x", padx=15, pady=2)
      ctk.CTkLabel(card, text="").pack(pady=3)

    sections = [
        ("📱 Бренди та Категорії техніки", [
            "• Смартфони, планшети, смарт-годинники, ТВ та ТВ-приставки тепер представлені брендами: Масунг, Опел, Чедмі.",
            "• Додано електротранспорт: Електросамокат та Гіроборд зі своїми специфічними поломками (мотор-колесо, контролер, прокол шини).",
            "• Портативні консолі: СтімДек та СвітчКонсоль (дрифт стіків, дисплеї, охолодження APU).",
            "• Стережіться підробок! Без діагностики або перевірки копія коштує на -50% дешевше від оригіналу.",
        ], "#3498db"),
        ("⚡ Збірка ПК та Енергобаланс (200W - 1000W)", [
            "• Повна лінійка відеокарт: ATX 3050, 3060, 3070, 4060, 4070, 4080, 5070, 5080.",
            "• Процесори від Core-X3 до флагманського Core-X9.",
            "• Блоки живлення: 200W, 400W, 600W, 750W, 1000W.",
            "• БАЛАНС ЖИВЛЕННЯ: Сумарне споживання системи (CPU + GPU + RAM + Плата 50W) не повинно перевищувати потужність БЖ!",
            "• Преміум-моддинг ПК: встановлюйте RGB-підсвітку (+15%), кастомні кабелі (+10%) та водяне охолодження (+25%)!",
        ], "#9b59b6"),
        ("🔬 Сканер дефектів та Тест-стенд", [
            "• Ручний лазерний сканер: купуйте разово за 100 грн або один раз назавжди за 500 грн.",
            "• Скануйте зони пристрою кружечками для виявлення прихованих дефектів та реплік (ПК не сканується ручним сканером).",
            "• Вкладка 'Тест-стенд' перед Бухгалтерією: запускайте стрес-тести для 100% апаратної діагностики будь-якого заліза!",
        ], "#1abc9c"),
        ("🚨 3-Секундне QTE: Затримання злодія", [
            "• При перевірці бази розшуку викраденої техніки з'являється 3-секундний таймер QTE!",
            "• Встигніть натиснути '🚨 ЗАХОПИТИ ЗЛОДІЯ (3с)!', щоб поліція затримала його та виплатила вам премію +1500 грн!",
            "• Якщо час спливе — злодій вихопить техніку та накиває п'ятами.",
        ], "#e74c3c"),
        ("👥 5 Типів клієнтів, Експрес-ремонт та Trade-In", [
            "• Типи клієнтів: від Гіперактивного (кидає все і біжить збирати банани) до терплячого Дзен-клієнта.",
            "• Індикатор настрою клієнта відображає його готовність торгуватися.",
            "• Терміновий ремонт (Експрес, 1 день) оплачується за подвійним тарифом (2x)! Доступний також Trade-In обмін.",
        ], "#f39c12"),
    ]

    for title, lines, color in sections:
      add_guide_section(title, lines, color)


  def setup_game_screen(self):
    self.top_frame = ctk.CTkFrame(self.frame_game, height=60, corner_radius=12)
    self.top_frame.pack(fill="x", padx=20, pady=(15, 10))
    self.top_frame.pack_propagate(False)

    btn_menu_back = ctk.CTkButton(
        self.top_frame,
        text="⬅️ Меню",
        width=80,
        height=32,
        fg_color="#7f8c8d",
        hover_color="#636e72",
        command=lambda: self.show_screen("menu"),
    )
    btn_menu_back.pack(side="left", padx=(15, 5), pady=10)

    btn_quick_save = ctk.CTkButton(
        self.top_frame,
        text="💾 Сейв",
        width=70,
        height=32,
        fg_color="#2980b9",
        hover_color="#1f618d",
        command=self.quick_save,
    )
    btn_quick_save.pack(side="left", padx=5, pady=10)

    self.btn_sound = ctk.CTkButton(
        self.top_frame,
        text="🔊 Звук: УВІМК" if self.sound_enabled else "🔇 Звук: ВИМК",
        width=110,
        height=32,
        fg_color="#27ae60" if self.sound_enabled else "#7f8c8d",
        hover_color="#219150" if self.sound_enabled else "#636e72",
        command=self.toggle_sound,
    )
    self.btn_sound.pack(side="left", padx=5, pady=10)

    self.lbl_day = ctk.CTkLabel(
        self.top_frame,
        text=f"📅 День: {self.day}",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color="#f39c12",
    )
    self.lbl_day.pack(side="left", padx=15, pady=10)

    self.lbl_balance = ctk.CTkLabel(
        self.top_frame,
        text=f"💰 Баланс: {self.balance} грн",
        font=ctk.CTkFont(size=19, weight="bold"),
        text_color="#2ecc71",
    )
    self.lbl_balance.pack(side="left", padx=15, pady=10)

    btn_end_day = ctk.CTkButton(
        self.top_frame,
        text="🌙 Завершити день",
        font=ctk.CTkFont(size=14, weight="bold"),
        height=38,
        fg_color="#e67e22",
        hover_color="#d35400",
        command=self.end_day,
    )
    btn_end_day.pack(side="right", padx=(5, 15), pady=10)

    self.lbl_timer = ctk.CTkLabel(
        self.top_frame,
        text="⏱️ 15:00",
        font=ctk.CTkFont(size=17, weight="bold"),
        text_color="#3498db",
    )
    self.lbl_timer.pack(side="right", padx=10, pady=10)

    self.lbl_inv_count = ctk.CTkLabel(
        self.top_frame,
        text="",
        font=ctk.CTkFont(size=14),
    )
    self.lbl_inv_count.pack(side="right", padx=10, pady=10)

    self.lbl_parts_count = ctk.CTkLabel(
        self.top_frame,
        text="",
        font=ctk.CTkFont(size=14),
        text_color="#e67e22",
    )
    self.lbl_parts_count.pack(side="right", padx=10, pady=10)

    self.tabview = ctk.CTkTabview(self.frame_game, width=1020, height=730)
    self.tabview.pack(padx=20, pady=(0, 15), fill="both", expand=True)

    self.tab_buy = self.tabview.add("📥 Скупка / Замовлення")
    self.tab_sell = self.tabview.add("🛒 Склад та Вітрина")
    self.tab_parts = self.tabview.add("🔩 Запчастини")
    self.tab_repair = self.tabview.add("🔧 Ремонт")
    self.tab_market = self.tabview.add("🏪 Ринок деталей")
    self.tab_accessories = self.tabview.add("🎧 Аксесуари")
    self.tab_test_bench = self.tabview.add("🔬 Тест-стенд")
    self.tab_finance = self.tabview.add("📊 Бухгалтерія")

    self.setup_buy_tab()
    self.setup_sell_tab()
    self.setup_parts_tab()
    self.setup_repair_tab()
    self.setup_market_tab()
    self.setup_accessories_tab()
    self.setup_test_bench_tab()
    self.setup_finance_tab()


  def setup_buy_tab(self):
    main_frame = ctk.CTkFrame(self.tab_buy, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    left_card = ctk.CTkFrame(main_frame, corner_radius=15)
    left_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

    self.lbl_card_title = ctk.CTkLabel(
        left_card,
        text="📥 Огляд пропозиції клієнта",
        font=ctk.CTkFont(size=18, weight="bold"),
    )
    self.lbl_card_title.pack(anchor="w", padx=20, pady=(15, 2))

    patience_box = ctk.CTkFrame(left_card, fg_color="transparent")
    patience_box.pack(fill="x", padx=20, pady=(0, 6))

    self.lbl_patience_val = ctk.CTkLabel(
        patience_box,
        text="😊 Настрій: 100% | Тип: Звичайний",
        font=ctk.CTkFont(size=13, weight="bold"),
        text_color="#2ecc71"
    )
    self.lbl_patience_val.pack(anchor="w")

    self.bar_client_patience = ctk.CTkProgressBar(patience_box, height=8, width=400)
    self.bar_client_patience.set(1.0)
    self.bar_client_patience.pack(fill="x", pady=2)

    self.txt_item_info = ctk.CTkTextbox(left_card, font=ctk.CTkFont(size=14), wrap="word")
    self.txt_item_info.pack(fill="both", expand=True, padx=15, pady=8)
    self.txt_item_info.configure(state="disabled")

    right_card = ctk.CTkFrame(main_frame, corner_radius=15, width=380)
    right_card.pack(side="right", fill="both", expand=True, padx=(10, 0))

    self.lbl_form_title = ctk.CTkLabel(
        right_card,
        text="🤝 Дії та Рішення",
        font=ctk.CTkFont(size=18, weight="bold"),
    )
    self.lbl_form_title.pack(anchor="w", padx=20, pady=(15, 10))

    self.btn_scanner = ctk.CTkButton(
        right_card,
        text="🔍 Ручний сканер дефектів",
        font=ctk.CTkFont(size=14, weight="bold"),
        height=38,
        fg_color="#8e44ad",
        hover_color="#732d91",
        command=self.open_scanner_minigame,
    )
    self.btn_scanner.pack(fill="x", padx=20, pady=(0, 10))

    self.btn_check_stolen = ctk.CTkButton(
        right_card,
        text="🔍 Перевірити за базою IMEI (150 грн)",
        font=ctk.CTkFont(size=14, weight="bold"),
        height=38,
        fg_color="#34495e",
        hover_color="#2c3e50",
        command=self.check_stolen_status,
    )
    self.btn_check_stolen.pack(fill="x", padx=20, pady=(0, 15))

    self.btn_qte_police = ctk.CTkButton(
        right_card,
        text="🚨 ЗАХОПИТИ ЗЛОДІЯ (3с)!",
        font=ctk.CTkFont(size=15, weight="bold"),
        height=45,
        fg_color="#e74c3c",
        hover_color="#c0392b",
        command=self.claim_police_bounty,
    )

    self.lbl_price_input = ctk.CTkLabel(
        right_card,
        text="Запропонувати ціну (грн):",
        font=ctk.CTkFont(size=14, weight="bold"),
    )
    self.lbl_price_input.pack(anchor="w", padx=20, pady=(5, 2))

    self.entry_price = ctk.CTkEntry(right_card, font=ctk.CTkFont(size=16), height=40)
    self.entry_price.pack(fill="x", padx=20, pady=(0, 15))

    self.btn_submit_deal = ctk.CTkButton(
        right_card,
        text="Купити пристрій",
        font=ctk.CTkFont(size=15, weight="bold"),
        height=45,
        fg_color="#27ae60",
        hover_color="#219150",
        command=self.handle_deal_submit,
    )
    self.btn_submit_deal.pack(fill="x", padx=20, pady=(0, 10))

    self.btn_skip = ctk.CTkButton(
        right_card,
        text="Відмовитися (Наступний клієнт)",
        font=ctk.CTkFont(size=14),
        height=38,
        fg_color="#7f8c8d",
        hover_color="#636e72",
        command=self.skip_item,
    )
    self.btn_skip.pack(fill="x", padx=20, pady=(0, 15))

    self.lbl_buy_result = ctk.CTkLabel(
        right_card,
        text="",
        font=ctk.CTkFont(size=13, weight="bold"),
        text_color="#e67e22",
        wraplength=340,
    )
    self.lbl_buy_result.pack(fill="x", padx=20, pady=5)


  def setup_sell_tab(self):
    top_bar = ctk.CTkFrame(self.tab_sell, fg_color="transparent")
    top_bar.pack(fill="x", padx=10, pady=(5, 5))

    lbl = ctk.CTkLabel(
        top_bar,
        text="🛒 Товари на складі та вітрині (Вкажіть ціну та увімкніть 'На вітрину')",
        font=ctk.CTkFont(size=15, weight="bold"),
    )
    lbl.pack(side="left", padx=10, pady=8)

    btn_assemble_pc = ctk.CTkButton(
        top_bar,
        text="🖥️ Зібрати ПК (Конфігуратор)",
        font=ctk.CTkFont(size=14, weight="bold"),
        height=34,
        fg_color="#8e44ad",
        hover_color="#732d91",
        command=self.assemble_pc,
    )
    btn_assemble_pc.pack(side="right", padx=15, pady=8)

    self.scroll_sell = ctk.CTkScrollableFrame(self.tab_sell, label_text="Склад товарів")
    self.scroll_sell.pack(fill="both", expand=True, padx=10, pady=(0, 10))


  def refresh_sell_tab(self):
    for widget in self.scroll_sell.winfo_children():
      widget.destroy()

    if not self.inventory:
      lbl_empty = ctk.CTkLabel(
          self.scroll_sell,
          text="Склад порожній. Придбайте товари у вкладці 'Скупка'!",
          font=ctk.CTkFont(size=16),
          text_color="#95a5a6",
      )
      lbl_empty.pack(pady=40)
      return

    for idx, item in enumerate(self.inventory):
      card = ctk.CTkFrame(self.scroll_sell, corner_radius=12)
      card.pack(fill="x", padx=10, pady=6)

      left = ctk.CTkFrame(card, fg_color="transparent")
      left.pack(side="left", fill="both", expand=True, padx=15, pady=10)

      is_rep = item.get("is_repaired", True)
      status_txt = "✨ Ідеальний" if is_rep else f"⚠️ Дефекти: {len(item.get('damages', []))} шт."
      status_color = "#2ecc71" if is_rep else "#e74c3c"

      item_title = item.get("title", item["dev"])
      lbl_dev = ctk.CTkLabel(
          left,
          text=f"📱 {item_title} | Стан: {status_txt}",
          font=ctk.CTkFont(size=15, weight="bold"),
          text_color=status_color,
          anchor="w",
      )
      lbl_dev.pack(anchor="w")

      acc_list = item.get("accessories", [])
      acc_str = f" | Аксесуари: {', '.join(acc_list)}" if acc_list else ""
      lbl_sub = ctk.CTkLabel(
          left,
          text=f"Куплено за: {item['buy_price']} грн | Ринкова ціна: ~{item['fair_price']} грн{acc_str}",
          font=ctk.CTkFont(size=12),
          text_color="#bdc3c7",
          anchor="w",
      )
      lbl_sub.pack(anchor="w", pady=(2, 0))

      right = ctk.CTkFrame(card, fg_color="transparent")
      right.pack(side="right", padx=15, pady=10)

      e_price = ctk.CTkEntry(right, width=95, height=32, font=ctk.CTkFont(size=13))
      e_price.insert(0, str(item.get("target_sell_price", item["fair_price"])))
      e_price.pack(side="left", padx=5)

      is_on_sale = item.get("on_sale", False)
      btn_sale = ctk.CTkButton(
          right,
          text="Зняти" if is_on_sale else "На вітрину",
          width=95,
          height=32,
          fg_color="#e74c3c" if is_on_sale else "#27ae60",
          hover_color="#c0392b" if is_on_sale else "#219150",
          command=lambda i=idx, ep=e_price: self.toggle_showcase(i, ep),
      )
      btn_sale.pack(side="left", padx=5)

      btn_dismantle = ctk.CTkButton(
          right,
          text="Розібрати",
          width=85,
          height=32,
          fg_color="#8e44ad",
          hover_color="#732d91",
          command=lambda i=idx: self.dismantle_to_parts(i),
      )
      btn_dismantle.pack(side="left", padx=5)


  def setup_parts_tab(self):
    top_bar = ctk.CTkFrame(self.tab_parts, fg_color="transparent")
    top_bar.pack(fill="x", padx=10, pady=(5, 5))

    lbl = ctk.CTkLabel(
        top_bar,
        text="🔩 Склад запасних частин для ремонту гаджетів та ПК",
        font=ctk.CTkFont(size=15, weight="bold"),
    )
    lbl.pack(side="left", padx=10, pady=8)

    self.scroll_parts = ctk.CTkScrollableFrame(self.tab_parts, label_text="Запасні компоненти")
    self.scroll_parts.pack(fill="both", expand=True, padx=10, pady=(0, 10))


  def refresh_parts_tab(self):
    for widget in self.scroll_parts.winfo_children():
      widget.destroy()

    if not self.parts_inventory:
      lbl_empty = ctk.CTkLabel(
          self.scroll_parts,
          text="Склад запчастин порожній. Придбайте їх на Ринку деталей або розберіть пристрій!",
          font=ctk.CTkFont(size=16),
          text_color="#95a5a6",
      )
      lbl_empty.pack(pady=40)
      return

    for part_name, qty in self.parts_inventory.items():
      if qty <= 0:
        continue
      card = ctk.CTkFrame(self.scroll_parts, corner_radius=12)
      card.pack(fill="x", padx=10, pady=5)

      left = ctk.CTkFrame(card, fg_color="transparent")
      left.pack(side="left", fill="both", expand=True, padx=15, pady=8)

      lbl_name = ctk.CTkLabel(
          left,
          text=f"⚙️ {part_name}",
          font=ctk.CTkFont(size=14, weight="bold"),
          anchor="w",
      )
      lbl_name.pack(anchor="w")

      base_c = self.catalog.get(part_name, {}).get("base_cost", 300)
      lbl_info = ctk.CTkLabel(
          left,
          text=f"Кількість: {qty} шт. | Оціночна вартість здачі: ~{int(base_c*0.7)} грн/шт.",
          font=ctk.CTkFont(size=12),
          text_color="#bdc3c7",
          anchor="w",
      )
      lbl_info.pack(anchor="w")

      right = ctk.CTkFrame(card, fg_color="transparent")
      right.pack(side="right", padx=15, pady=8)

      entry_qty = ctk.CTkEntry(right, width=50, height=30)
      entry_qty.insert(0, "1")
      entry_qty.pack(side="left", padx=5)

      btn_sell = ctk.CTkButton(
          right,
          text="Здати (Продати)",
          width=120,
          height=30,
          fg_color="#e67e22",
          hover_color="#d35400",
          command=lambda pn=part_name, eq=entry_qty: self.sell_part(pn, eq),
      )
      btn_sell.pack(side="left", padx=5)


  def setup_repair_tab(self):
    top_bar = ctk.CTkFrame(self.tab_repair, fg_color="transparent")
    top_bar.pack(fill="x", padx=10, pady=(5, 5))

    lbl = ctk.CTkLabel(
        top_bar,
        text="🔧 Майстерня ремонту: замовлення клієнтів та техніка зі складу",
        font=ctk.CTkFont(size=15, weight="bold"),
    )
    lbl.pack(side="left", padx=10, pady=8)

    self.scroll_repair = ctk.CTkScrollableFrame(self.tab_repair, label_text="Пристрої, що потребують ремонту")
    self.scroll_repair.pack(fill="both", expand=True, padx=10, pady=(0, 10))


  def refresh_repair_tab(self):
    for widget in self.scroll_repair.winfo_children():
      widget.destroy()

    has_work = False

    if self.client_orders:
      has_work = True
      lbl_sec = ctk.CTkLabel(
          self.scroll_repair,
          text="📋 КЛІЄНТСЬКІ ЗАМОВЛЕННЯ НА РЕМОНТ:",
          font=ctk.CTkFont(size=15, weight="bold"),
          text_color="#f39c12",
          anchor="w",
      )
      lbl_sec.pack(fill="x", padx=10, pady=(10, 5))

      for idx, ord_item in enumerate(self.client_orders):
        card = ctk.CTkFrame(self.scroll_repair, corner_radius=12)
        card.pack(fill="x", padx=10, pady=5)

        left = ctk.CTkFrame(card, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=15, pady=8)

        st = "✅ Відремонтовано (Очікує видачі)" if ord_item["is_repaired"] else f"⚠️ Залишилося днів: {ord_item['days_left']}"
        exp_txt = " [⚡ ЕКСПРЕС]" if ord_item.get("is_express", False) else ""
        lbl_t = ctk.CTkLabel(
            left,
            text=f"🔧 {ord_item['dev']}{exp_txt} | {st}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2ecc71" if ord_item["is_repaired"] else "#f39c12",
            anchor="w",
        )
        lbl_t.pack(anchor="w")

        dmgs = ord_item.get("damages", [])
        dmg_str = ", ".join(dmgs) if dmgs else "Всі несправності усунено"
        lbl_d = ctk.CTkLabel(
            left,
            text=f"Винагорода: {ord_item['reward']} грн | Несправності: {dmg_str}",
            font=ctk.CTkFont(size=12),
            text_color="#bdc3c7",
            anchor="w",
        )
        lbl_d.pack(anchor="w")

        right = ctk.CTkFrame(card, fg_color="transparent")
        right.pack(side="right", padx=15, pady=8)

        if not ord_item["is_repaired"]:
          btn_rep = ctk.CTkButton(
              right,
              text="Ремонтувати",
              width=110,
              height=32,
              fg_color="#27ae60",
              hover_color="#219150",
              command=lambda i=idx: self.repair_client_order(i),
          )
          btn_rep.pack(side="left", padx=5)

        if ord_item["dev"] == "Системний блок (ПК)":
          btn_dism = ctk.CTkButton(
              right,
              text="Розібрати ПК",
              width=110,
              height=32,
              fg_color="#8e44ad",
              hover_color="#732d91",
              command=lambda i=idx: self.dismantle_client_order_pc(i),
          )
          btn_dism.pack(side="left", padx=5)

    broken_inv = [(i, it) for i, it in enumerate(self.inventory) if not it.get("is_repaired", True)]
    if broken_inv:
      has_work = True
      lbl_sec2 = ctk.CTkLabel(
          self.scroll_repair,
          text="📦 ВЛАСНІ ТОВАРИ ЗІ СКЛАДУ, ЩО ПОТРЕБУЮТЬ РЕМОНТУ:",
          font=ctk.CTkFont(size=15, weight="bold"),
          text_color="#3498db",
          anchor="w",
      )
      lbl_sec2.pack(fill="x", padx=10, pady=(15, 5))

      for idx, item in broken_inv:
        card = ctk.CTkFrame(self.scroll_repair, corner_radius=12)
        card.pack(fill="x", padx=10, pady=5)

        left = ctk.CTkFrame(card, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=15, pady=8)

        item_title = item.get("title", item["dev"])
        lbl_t = ctk.CTkLabel(
            left,
            text=f"📱 {item_title}",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        lbl_t.pack(anchor="w")

        dmgs = item.get("damages", [])
        dmg_str = ", ".join(dmgs) if dmgs else "Дефектів немає"
        lbl_d = ctk.CTkLabel(
            left,
            text=f"Несправності: {dmg_str}",
            font=ctk.CTkFont(size=12),
            text_color="#e74c3c",
            anchor="w",
        )
        lbl_d.pack(anchor="w")

        right = ctk.CTkFrame(card, fg_color="transparent")
        right.pack(side="right", padx=15, pady=8)

        btn_rep = ctk.CTkButton(
            right,
            text="Ремонтувати",
            width=110,
            height=32,
            fg_color="#27ae60",
            hover_color="#219150",
            command=lambda i=idx: self.repair_item(i),
        )
        btn_rep.pack(side="left", padx=5)

    if not has_work:
      lbl_empty = ctk.CTkLabel(
          self.scroll_repair,
          text="Немає пристроїв, що потребують ремонту. Прийміть замовлення або купіть поламаний гаджет!",
          font=ctk.CTkFont(size=16),
          text_color="#95a5a6",
      )
      lbl_empty.pack(pady=40)


  def setup_market_tab(self):
    top_bar = ctk.CTkFrame(self.tab_market, fg_color="transparent")
    top_bar.pack(fill="x", padx=10, pady=(5, 5))

    lbl = ctk.CTkLabel(
        top_bar,
        text="🏪 Ринок запасних частин: Аналоги (миттєво, 50% успіх) та Оригінали (1 день, 90% успіх)",
        font=ctk.CTkFont(size=14, weight="bold"),
    )
    lbl.pack(side="left", padx=10, pady=8)

    self.btn_refresh_market = ctk.CTkButton(
        top_bar,
        text="🔄 Оновити асортимент (100 грн)",
        font=ctk.CTkFont(size=13, weight="bold"),
        height=32,
        fg_color="#3498db",
        hover_color="#2980b9",
        command=lambda: self.refresh_market_stock(manual=True),
    )
    self.btn_refresh_market.pack(side="right", padx=10, pady=8)

    self.scroll_market = ctk.CTkScrollableFrame(self.tab_market, label_text="Каталог постачальників запчастин")
    self.scroll_market.pack(fill="both", expand=True, padx=10, pady=(0, 10))


  def render_market_tab(self):
    for widget in self.scroll_market.winfo_children():
      widget.destroy()

    if getattr(self, "free_market_refresh_active", False):
      self.btn_refresh_market.configure(text="🔄 Оновити асортимент (0 грн - Абонемент)", fg_color="#27ae60")
    else:
      self.btn_refresh_market.configure(text="🔄 Оновити асортимент (100 грн)", fg_color="#3498db")

    if not getattr(self, "market_items", []):
      lbl_empty = ctk.CTkLabel(
          self.scroll_market,
          text="На ринку наразі немає пропозицій. Натисніть 'Оновити асортимент'!",
          font=ctk.CTkFont(size=16),
          text_color="#95a5a6",
      )
      lbl_empty.pack(pady=40)
      return

    for idx, item in enumerate(self.market_items):
      card = ctk.CTkFrame(self.scroll_market, corner_radius=12)
      card.pack(fill="x", padx=10, pady=5)

      left = ctk.CTkFrame(card, fg_color="transparent")
      left.pack(side="left", fill="both", expand=True, padx=15, pady=8)

      lbl_name = ctk.CTkLabel(
          left,
          text=f"📦 {item['name']}",
          font=ctk.CTkFont(size=14, weight="bold"),
          anchor="w",
      )
      lbl_name.pack(anchor="w")

      analog_price = int(item['price'] * 0.65)
      lbl_sub = ctk.CTkLabel(
          left,
          text=f"Призначення: {item['dev']} ({item['damage']}) | Оригінал: {item['price']} грн | Аналог: {analog_price} грн",
          font=ctk.CTkFont(size=12),
          text_color="#bdc3c7",
          anchor="w",
      )
      lbl_sub.pack(anchor="w")

      right = ctk.CTkFrame(card, fg_color="transparent")
      right.pack(side="right", padx=15, pady=8)

      if item.get("bought", False):
        lbl_b = ctk.CTkLabel(right, text="✅ Куплено", font=ctk.CTkFont(size=13, weight="bold"), text_color="#2ecc71")
        lbl_b.pack(padx=10)
      else:
        btn_analog = ctk.CTkButton(
            right,
            text=f"⚡ Аналог ({analog_price} грн)",
            width=140,
            height=30,
            fg_color="#e67e22",
            hover_color="#d35400",
            command=lambda i=idx: self.buy_market_part_analog(i),
        )
        btn_analog.pack(side="left", padx=4)

        btn_orig = ctk.CTkButton(
            right,
            text=f"💎 Оригінал ({item['price']} грн)",
            width=150,
            height=30,
            fg_color="#2980b9",
            hover_color="#1f618d",
            command=lambda i=idx: self.buy_market_part_original(i),
        )
        btn_orig.pack(side="left", padx=4)


  def setup_accessories_tab(self):
    top_bar = ctk.CTkFrame(self.tab_accessories, fg_color="transparent")
    top_bar.pack(fill="x", padx=10, pady=(5, 5))

    lbl = ctk.CTkLabel(
        top_bar,
        text="🎧 Оптова закупівля аксесуарів (Підвищують вартість та привабливість гаджетів)",
        font=ctk.CTkFont(size=15, weight="bold"),
    )
    lbl.pack(side="left", padx=10, pady=8)

    self.scroll_accessories = ctk.CTkScrollableFrame(self.tab_accessories, label_text="Каталог оптових аксесуарів")
    self.scroll_accessories.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    self.render_accessories_tab()


  def render_accessories_tab(self):
    for widget in self.scroll_accessories.winfo_children():
      widget.destroy()

    for acc_key, acc_info in self.ACCESSORIES.items():
      card = ctk.CTkFrame(self.scroll_accessories, corner_radius=12)
      card.pack(fill="x", padx=15, pady=8)

      left = ctk.CTkFrame(card, fg_color="transparent")
      left.pack(side="left", fill="both", expand=True, padx=15, pady=10)

      lbl_t = ctk.CTkLabel(left, text=f"✨ {acc_info['name']}", font=ctk.CTkFont(size=16, weight="bold"), anchor="w")
      lbl_t.pack(anchor="w")

      cost = acc_info["cost"]
      if self.skills.get("wholesale_partner", False):
        cost = int(cost * 0.85)

      desc = (
          f"💰 Собівартість: {cost} грн | 📈 Бонус до ціни продажу: +{acc_info['price_bonus']} грн\n"
          f"⚡ Збільшення шансу швидкого продажу: +{int(acc_info['chance_bonus']*100)}%\n"
          f"📱 Підходить для: {', '.join(acc_info['allowed'])}"
      )
      lbl_d = ctk.CTkLabel(left, text=desc, font=ctk.CTkFont(size=13), text_color="#bdc3c7", anchor="w", justify="left")
      lbl_d.pack(anchor="w", pady=(3, 0))

      right = ctk.CTkFrame(card, fg_color="transparent")
      right.pack(side="right", padx=15, pady=10)

      btn_buy = ctk.CTkButton(
          right,
          text=f"Придбати ({cost} грн)",
          font=ctk.CTkFont(size=14, weight="bold"),
          width=150,
          height=36,
          fg_color="#27ae60",
          hover_color="#219150",
          command=lambda ak=acc_key: self.buy_market_accessory(ak),
      )
      btn_buy.pack()


  def setup_test_bench_tab(self):
    main_frame = ctk.CTkFrame(self.tab_test_bench, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    left_frame = ctk.CTkFrame(main_frame, corner_radius=15, width=420)
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

    lbl_l = ctk.CTkLabel(left_frame, text="📦 Комплектуючі та техніка на складі", font=ctk.CTkFont(size=16, weight="bold"))
    lbl_l.pack(anchor="w", padx=15, pady=(15, 5))

    self.scroll_bench_items = ctk.CTkScrollableFrame(left_frame, label_text="Оберіть товар для діагностики")
    self.scroll_bench_items.pack(fill="both", expand=True, padx=10, pady=10)

    right_frame = ctk.CTkFrame(main_frame, corner_radius=15, width=480)
    right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

    lbl_r = ctk.CTkLabel(right_frame, text="🔬 Професійний апаратний стенд", font=ctk.CTkFont(size=18, weight="bold"), text_color="#1abc9c")
    lbl_r.pack(anchor="w", padx=20, pady=(15, 5))

    lbl_sub = ctk.CTkLabel(right_frame, text="Комплексна перевірка навантаженням, перевірка ліній живлення та виявлення браку.", font=ctk.CTkFont(size=13), text_color="#bdc3c7")
    lbl_sub.pack(anchor="w", padx=20, pady=(0, 10))

    self.txt_bench_monitor = ctk.CTkTextbox(right_frame, font=ctk.CTkFont(size=13), wrap="word")
    self.txt_bench_monitor.pack(fill="both", expand=True, padx=15, pady=10)
    self.txt_bench_monitor.insert("1.0", "Оберіть будь-який пристрій або деталь ліворуч та натисніть 'Тестувати'...\n")
    self.txt_bench_monitor.configure(state="disabled")

    self.render_test_bench_tab()


  def render_test_bench_tab(self):
    for widget in self.scroll_bench_items.winfo_children():
      widget.destroy()

    if not self.inventory:
      lbl_empty = ctk.CTkLabel(self.scroll_bench_items, text="На складі немає техніки для тестування.", font=ctk.CTkFont(size=14), text_color="#95a5a6")
      lbl_empty.pack(pady=30)
      return

    for idx, item in enumerate(self.inventory):
      card = ctk.CTkFrame(self.scroll_bench_items, corner_radius=10)
      card.pack(fill="x", padx=5, pady=4)

      title = item.get("title", item["dev"])
      lbl_t = ctk.CTkLabel(card, text=f"⚙️ {title}", font=ctk.CTkFont(size=13, weight="bold"), anchor="w")
      lbl_t.pack(side="left", padx=10, pady=8, fill="x", expand=True)

      btn_test = ctk.CTkButton(
          card,
          text="Тестувати (100 грн)",
          font=ctk.CTkFont(size=12, weight="bold"),
          width=140,
          height=28,
          fg_color="#16a085",
          hover_color="#138d75",
          command=lambda i=idx: self.run_test_bench_diagnostic(i),
      )
      btn_test.pack(side="right", padx=10, pady=8)


  def setup_finance_tab(self):
    content = ctk.CTkFrame(self.tab_finance, fg_color="transparent")
    content.pack(fill="both", expand=True, padx=10, pady=10)

    self.frame_stats_cards = ctk.CTkFrame(content, corner_radius=12)
    self.frame_stats_cards.pack(fill="x", padx=5, pady=(0, 10))

    self.lbl_stats_summary = ctk.CTkLabel(
        self.frame_stats_cards,
        text="",
        font=ctk.CTkFont(size=15, weight="bold"),
    )
    self.lbl_stats_summary.pack(padx=20, pady=12)

    lbl_history = ctk.CTkLabel(
        content,
        text="📜 Журнал фінансових операцій (Доходи та Витрати):",
        font=ctk.CTkFont(size=15, weight="bold"),
        anchor="w",
    )
    lbl_history.pack(fill="x", padx=5, pady=(5, 5))

    self.scroll_transactions = ctk.CTkScrollableFrame(content, label_text="Історія транзакцій")
    self.scroll_transactions.pack(fill="both", expand=True, padx=5, pady=(0, 5))


  def refresh_finance_tab(self):
    rev = self.stats["total_revenue"]
    exp = self.stats["total_expenses"]
    profit = rev - exp

    bounties = self.stats.get("bounties_claimed", 0)
    self.lbl_stats_summary.configure(
        text=f"📦 Продано товарів: {self.stats['items_sold']} шт. | 🔧 Замовлень виконано: {self.stats['orders_completed']} шт. | 🖥️ Зібрано ПК: {self.stats['pcs_assembled']} шт. | 🚨 Злодіїв спіймано: {bounties}\n"
        f"💵 Загальний дохід: {rev} грн | 💸 Загальні витрати: {exp} грн | 📈 Чистий фінансовий результат: {profit} грн"
    )

    for widget in self.scroll_transactions.winfo_children():
      widget.destroy()

    if not self.transactions_history:
      lbl_empty = ctk.CTkLabel(
          self.scroll_transactions,
          text="Журнал фінансових операцій поки що порожній.",
          font=ctk.CTkFont(size=14),
          text_color="#95a5a6",
      )
      lbl_empty.pack(pady=20)
      return

    for t in self.transactions_history:
      card = ctk.CTkFrame(self.scroll_transactions, corner_radius=8)
      card.pack(fill="x", padx=5, pady=3)

      is_inc = (t["type"] == "дохід")
      sign = "+" if is_inc else "-"
      color = "#2ecc71" if is_inc else "#e74c3c"

      lbl_t = ctk.CTkLabel(
          card,
          text=f"День {t['day']} ({t['time']}) | {t['desc']}",
          font=ctk.CTkFont(size=13),
          anchor="w",
      )
      lbl_t.pack(side="left", padx=10, pady=6)

      lbl_a = ctk.CTkLabel(
          card,
          text=f"{sign}{t['amount']} грн",
          font=ctk.CTkFont(size=13, weight="bold"),
          text_color=color,
      )
      lbl_a.pack(side="right", padx=10, pady=6)


  def setup_night_screen(self):
    header = ctk.CTkFrame(self.frame_night, corner_radius=12)
    header.pack(fill="x", padx=25, pady=(20, 10))

    lbl_title = ctk.CTkLabel(
        header,
        text="🌙 Нічна фаза: Підсумки дня, Прокачка та Розширення",
        font=ctk.CTkFont(size=22, weight="bold"),
        text_color="#f39c12",
    )
    lbl_title.pack(side="left", padx=20, pady=12)

    self.lbl_night_balance = ctk.CTkLabel(
        header,
        text=f"💰 Баланс: {self.balance} грн",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color="#2ecc71",
    )
    self.lbl_night_balance.pack(side="right", padx=20, pady=12)

    self.scroll_night = ctk.CTkScrollableFrame(self.frame_night, label_text="Звіт дня та магазин покращень")
    self.scroll_night.pack(fill="both", expand=True, padx=25, pady=(0, 10))

    bottom_bar = ctk.CTkFrame(self.frame_night, corner_radius=12)
    bottom_bar.pack(fill="x", padx=25, pady=(0, 20))

    btn_achieve = ctk.CTkButton(
        bottom_bar,
        text="🏆 Досягнення",
        font=ctk.CTkFont(size=16, weight="bold"),
        height=48,
        width=180,
        fg_color="#f39c12",
        hover_color="#d68910",
        command=self.show_achievements_modal,
    )
    btn_achieve.pack(side="left", padx=20, pady=12)

    btn_next_day = ctk.CTkButton(
        bottom_bar,
        text="☀️ Почати наступний день",
        font=ctk.CTkFont(size=17, weight="bold"),
        height=48,
        fg_color="#27ae60",
        hover_color="#219150",
        command=self.start_next_day,
    )
    btn_next_day.pack(side="right", padx=20, pady=12)


  def render_night_screen(self):
    self.lbl_night_balance.configure(text=f"💰 Баланс: {self.balance} грн")

    for widget in self.scroll_night.winfo_children():
      widget.destroy()

    frame_rep = ctk.CTkFrame(self.scroll_night, corner_radius=12)
    frame_rep.pack(fill="x", padx=10, pady=8)

    lbl_rep_title = ctk.CTkLabel(
        frame_rep,
        text=f"📊 Фінансовий звіт за День {self.day}:",
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color="#3498db",
        anchor="w",
    )
    lbl_rep_title.pack(fill="x", padx=15, pady=(10, 5))

    rep = self.daily_report
    sold_count = len(rep.get("sold_items", []))
    rep_orders_count = len(rep.get("completed_orders", []))
    sales_rev = rep.get("sales_revenue", 0)
    rep_rev = rep.get("repair_revenue", 0)
    total_inc = sales_rev + rep_rev
    mand_exp = rep.get("mandatory_expenses", 1000)
    net_inc = total_inc - mand_exp
    net_color = "#2ecc71" if net_inc >= 0 else "#e74c3c"

    lines = [
        f"• Продано з вітрини: {sold_count} шт. на суму +{sales_rev} грн",
        f"• Виконано замовлень на ремонт: {rep_orders_count} шт. на суму +{rep_rev} грн",
        f"• Оренда та комунальні послуги: -{mand_exp} грн",
        f"• ЧИСТИЙ ПРИБУТОК ЗА ДЕНЬ: {net_inc:+d} грн",
    ]
    for l in lines:
      c = net_color if "ЧИСТИЙ ПРИБУТОК" in l else "#ffffff"
      ctk.CTkLabel(frame_rep, text=l, font=ctk.CTkFont(size=13, weight="bold" if "ЧИСТИЙ ПРИБУТОК" in l else "normal"), text_color=c, anchor="w").pack(fill="x", padx=15, pady=2)
    ctk.CTkLabel(frame_rep, text="").pack(pady=3)

    frame_skills = ctk.CTkFrame(self.scroll_night, corner_radius=12)
    frame_skills.pack(fill="x", padx=10, pady=8)

    lbl_sk_title = ctk.CTkLabel(
        frame_skills,
        text="🌳 Дерево перманентних навичок (Діють назавжди):",
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color="#2ecc71",
        anchor="w",
    )
    lbl_sk_title.pack(fill="x", padx=15, pady=(10, 5))

    for sk_key, sk_data in self.skills_info.items():
      row = ctk.CTkFrame(frame_skills, fg_color="transparent")
      row.pack(fill="x", padx=15, pady=4)

      is_owned = self.skills.get(sk_key, False)
      lbl_sn = ctk.CTkLabel(row, text=f"{sk_data['name']} ({sk_data['desc']})", font=ctk.CTkFont(size=13), anchor="w")
      lbl_sn.pack(side="left", fill="x", expand=True)

      if is_owned:
        ctk.CTkLabel(row, text="✅ Придбано", font=ctk.CTkFont(size=13, weight="bold"), text_color="#2ecc71").pack(side="right", padx=10)
      else:
        btn_sk = ctk.CTkButton(
            row,
            text=f"Придбати ({sk_data['cost']} грн)",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=150,
            height=30,
            fg_color="#27ae60",
            hover_color="#219150",
            command=lambda k=sk_key: self.buy_skill(k),
        )
        btn_sk.pack(side="right", padx=10)

    ctk.CTkLabel(frame_skills, text="").pack(pady=3)

    frame_storage = ctk.CTkFrame(self.scroll_night, corner_radius=12)
    frame_storage.pack(fill="x", padx=10, pady=8)

    ctk.CTkLabel(frame_storage, text="📦 Розширення місткості складів:", font=ctk.CTkFont(size=16, weight="bold"), text_color="#e67e22", anchor="w").pack(fill="x", padx=15, pady=(10, 5))

    row_dev = ctk.CTkFrame(frame_storage, fg_color="transparent")
    row_dev.pack(fill="x", padx=15, pady=5)
    cur_dev_lim = self.STORAGE_DEV_LIMITS[self.storage_dev_lvl]
    ctk.CTkLabel(row_dev, text=f"Склад пристроїв (Рівень {self.storage_dev_lvl}): поточний ліміт {cur_dev_lim} місць", font=ctk.CTkFont(size=13), anchor="w").pack(side="left")

    next_dev_lvl = self.storage_dev_lvl + 1
    if next_dev_lvl in self.STORAGE_DEV_LIMITS:
      cost_dev = {2: 2500, 3: 5000, 4: 9000}[next_dev_lvl]
      btn_up_dev = ctk.CTkButton(
          row_dev,
          text=f"Рівень {next_dev_lvl} (+{self.STORAGE_DEV_LIMITS[next_dev_lvl]} місць) — {cost_dev} грн",
          font=ctk.CTkFont(size=12, weight="bold"),
          width=230,
          height=30,
          fg_color="#e67e22",
          hover_color="#d35400",
          command=lambda cd=cost_dev, nl=next_dev_lvl: self.upgrade_dev_storage(cd, nl),
      )
      btn_up_dev.pack(side="right")
    else:
      ctk.CTkLabel(row_dev, text="⭐ МАКСИМАЛЬНИЙ РІВЕНЬ", font=ctk.CTkFont(size=12, weight="bold"), text_color="#2ecc71").pack(side="right")

    row_parts = ctk.CTkFrame(frame_storage, fg_color="transparent")
    row_parts.pack(fill="x", padx=15, pady=5)
    cur_parts_lim = self.STORAGE_PARTS_LIMITS[self.storage_parts_lvl]
    ctk.CTkLabel(row_parts, text=f"Склад деталей (Рівень {self.storage_parts_lvl}): поточний ліміт {cur_parts_lim} деталей", font=ctk.CTkFont(size=13), anchor="w").pack(side="left")

    next_parts_lvl = self.storage_parts_lvl + 1
    if next_parts_lvl in self.STORAGE_PARTS_LIMITS:
      cost_parts = {2: 1800, 3: 3500, 4: 6500}[next_parts_lvl]
      btn_up_parts = ctk.CTkButton(
          row_parts,
          text=f"Рівень {next_parts_lvl} (+{self.STORAGE_PARTS_LIMITS[next_parts_lvl]} дет.) — {cost_parts} грн",
          font=ctk.CTkFont(size=12, weight="bold"),
          width=230,
          height=30,
          fg_color="#e67e22",
          hover_color="#d35400",
          command=lambda cp=cost_parts, nl=next_parts_lvl: self.upgrade_parts_storage(cp, nl),
      )
      btn_up_parts.pack(side="right")
    else:
      ctk.CTkLabel(row_parts, text="⭐ МАКСИМАЛЬНИЙ РІВЕНЬ", font=ctk.CTkFont(size=12, weight="bold"), text_color="#2ecc71").pack(side="right")

    ctk.CTkLabel(frame_storage, text="").pack(pady=3)

    frame_serv = ctk.CTkFrame(self.scroll_night, corner_radius=12)
    frame_serv.pack(fill="x", padx=10, pady=8)

    ctk.CTkLabel(frame_serv, text="🏪 Маркетинг, Сервіси та Захист від поліції (на 1 день):", font=ctk.CTkFont(size=16, weight="bold"), text_color="#3498db", anchor="w").pack(fill="x", padx=15, pady=(10, 5))

    row_s1 = ctk.CTkFrame(frame_serv, fg_color="transparent")
    row_s1.pack(fill="x", padx=15, pady=4)
    ctk.CTkLabel(row_s1, text="Безкоштовні оновлення асортименту ринку (500 грн)", font=ctk.CTkFont(size=13), anchor="w").pack(side="left")
    if self.free_market_refresh_active:
      ctk.CTkLabel(row_s1, text="✅ Активовано", font=ctk.CTkFont(size=13, weight="bold"), text_color="#2ecc71").pack(side="right")
    else:
      ctk.CTkButton(row_s1, text="Придбати (500 грн)", width=170, height=28, command=self.buy_free_market_refresh).pack(side="right")

    row_s2 = ctk.CTkFrame(frame_serv, fg_color="transparent")
    row_s2.pack(fill="x", padx=15, pady=4)
    ctk.CTkLabel(row_s2, text="Рекламна кампанія вітрини (600 грн, +120% до швидкості продажів)", font=ctk.CTkFont(size=13), anchor="w").pack(side="left")
    if self.ads_active:
      ctk.CTkLabel(row_s2, text="✅ Запущено", font=ctk.CTkFont(size=13, weight="bold"), text_color="#2ecc71").pack(side="right")
    else:
      ctk.CTkButton(row_s2, text="Запустити (600 грн)", width=170, height=28, command=self.buy_ads).pack(side="right")

    row_s3 = ctk.CTkFrame(frame_serv, fg_color="transparent")
    row_s3.pack(fill="x", padx=15, pady=4)
    ctk.CTkLabel(row_s3, text=f"Послуги адвоката (Захист від конфіскації краденого, поточний: Рівень {self.lawyer_lvl})", font=ctk.CTkFont(size=13), anchor="w").pack(side="left")
    btn_lbox = ctk.CTkFrame(row_s3, fg_color="transparent")
    btn_lbox.pack(side="right")
    ctk.CTkButton(btn_lbox, text="Lvl 1 (500 грн)", width=95, height=28, command=lambda: self.hire_lawyer(1, 500)).pack(side="left", padx=2)
    ctk.CTkButton(btn_lbox, text="Lvl 2 (1100 грн)", width=105, height=28, command=lambda: self.hire_lawyer(2, 1100)).pack(side="left", padx=2)
    ctk.CTkButton(btn_lbox, text="Lvl 3 (2200 грн)", width=105, height=28, command=lambda: self.hire_lawyer(3, 2200)).pack(side="left", padx=2)

    ctk.CTkLabel(frame_serv, text="").pack(pady=3)


  def update_ui_state(self):
    self.lbl_day.configure(text=f"📅 День: {self.day}")
    self.lbl_balance.configure(text=f"💰 Баланс: {self.balance} грн")

    max_devs = self.STORAGE_DEV_LIMITS[self.storage_dev_lvl]
    occupied_devs = len(self.inventory) + len(self.client_orders)
    dev_color = "#e74c3c" if occupied_devs >= max_devs else "#ffffff"
    self.lbl_inv_count.configure(
        text=f"📦 Склад: {occupied_devs}/{max_devs} пристроїв",
        text_color=dev_color,
    )

    max_parts = self.STORAGE_PARTS_LIMITS[self.storage_parts_lvl]
    curr_parts = sum(self.parts_inventory.values())
    parts_color = "#e74c3c" if curr_parts >= max_parts else "#e67e22"
    self.lbl_parts_count.configure(
        text=f"🔩 Деталі: {curr_parts}/{max_parts}",
        text_color=parts_color,
    )

    self.refresh_sell_tab()
    self.refresh_parts_tab()
    self.refresh_repair_tab()
    self.refresh_finance_tab()


  def toggle_sound(self):
    self.sound_enabled = not self.sound_enabled
    if self.sound_enabled:
      self.btn_sound.configure(text="🔊 Звук: УВІМК", fg_color="#27ae60", hover_color="#219150")
    else:
      self.btn_sound.configure(text="🔇 Звук: ВИМК", fg_color="#7f8c8d", hover_color="#636e72")
