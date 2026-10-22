import datetime
import glob
import json
import os
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk


class SaveManagerMixin:

  def setup_saves_screen(self):
    header = ctk.CTkFrame(self.frame_saves, corner_radius=12)
    header.pack(fill="x", padx=25, pady=(20, 10))

    lbl_h = ctk.CTkLabel(
        header, text="📂 Менеджер збережень", font=ctk.CTkFont(size=22, weight="bold")
    )
    lbl_h.pack(side="left", padx=20, pady=12)

    content = ctk.CTkFrame(self.frame_saves, fg_color="transparent")
    content.pack(fill="both", expand=True, padx=25, pady=(0, 10))

    left_frame = ctk.CTkFrame(content, corner_radius=15, width=440)
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

    lbl_info_title = ctk.CTkLabel(
        left_frame, text="ℹ️ Деталі збереження", font=ctk.CTkFont(size=18, weight="bold")
    )
    lbl_info_title.pack(anchor="w", padx=20, pady=(20, 10))

    self.txt_save_info = ctk.CTkTextbox(left_frame, font=ctk.CTkFont(size=14), wrap="word", height=240)
    self.txt_save_info.pack(fill="x", padx=20, pady=(0, 15))
    self.txt_save_info.insert("1.0", "Оберіть збереження зі списку праворуч...")
    self.txt_save_info.configure(state="disabled")

    lbl_create = ctk.CTkLabel(
        left_frame, text="💾 Створити нове збереження поточної гри:", font=ctk.CTkFont(size=14, weight="bold")
    )
    lbl_create.pack(anchor="w", padx=20, pady=(10, 5))

    save_input_row = ctk.CTkFrame(left_frame, fg_color="transparent")
    save_input_row.pack(fill="x", padx=20, pady=(0, 15))

    self.entry_save_name = ctk.CTkEntry(
        save_input_row, placeholder_text="Назва збереження (напр. Сейв 1)", width=240, height=38
    )
    self.entry_save_name.pack(side="left", fill="x", expand=True, padx=(0, 10))

    btn_do_save = ctk.CTkButton(
        save_input_row,
        text="Зберегти",
        font=ctk.CTkFont(size=14, weight="bold"),
        height=38,
        width=110,
        fg_color="#27ae60",
        hover_color="#219150",
        command=self.create_save_from_input,
    )
    btn_do_save.pack(side="right")

    right_frame = ctk.CTkFrame(content, corner_radius=15)
    right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

    lbl_list_title = ctk.CTkLabel(
        right_frame, text="📜 Файли збережень", font=ctk.CTkFont(size=18, weight="bold")
    )
    lbl_list_title.pack(anchor="w", padx=20, pady=(20, 10))

    self.scroll_saves = ctk.CTkScrollableFrame(right_frame, label_text="Доступні слоти збереження")
    self.scroll_saves.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    bottom_bar = ctk.CTkFrame(self.frame_saves, corner_radius=12)
    bottom_bar.pack(fill="x", padx=25, pady=(0, 20))

    btn_close = ctk.CTkButton(
        bottom_bar,
        text="⬅️ Закрити",
        font=ctk.CTkFont(size=16, weight="bold"),
        height=48,
        width=180,
        fg_color="#7f8c8d",
        hover_color="#636e72",
        command=lambda: self.show_screen("menu"),
    )
    btn_close.pack(side="left", padx=20, pady=12)

    btn_delete = ctk.CTkButton(
        bottom_bar,
        text="🗑️ Видалити",
        font=ctk.CTkFont(size=16, weight="bold"),
        height=48,
        width=180,
        fg_color="#c0392b",
        hover_color="#962d22",
        command=self.delete_selected_save,
    )
    btn_delete.pack(side="right", padx=20, pady=12)

    btn_load = ctk.CTkButton(
        bottom_bar,
        text="▶️ Завантажити",
        font=ctk.CTkFont(size=16, weight="bold"),
        height=48,
        width=200,
        fg_color="#2980b9",
        hover_color="#1f618d",
        command=self.load_selected_save,
    )
    btn_load.pack(side="right", padx=10, pady=12)


  def refresh_saves_list(self):
    for widget in self.scroll_saves.winfo_children():
      widget.destroy()

    files = sorted(
        glob.glob(os.path.join(self.saves_dir, "*.json")),
        key=os.path.getmtime,
        reverse=True,
    )

    if not files:
      lbl = ctk.CTkLabel(
          self.scroll_saves,
          text="Збережень поки немає.\nВведіть назву зліва та збережіть гру!",
          font=ctk.CTkFont(size=14),
          text_color="#95a5a6",
      )
      lbl.pack(pady=40)
      self.update_save_info_text(None)
      return

    for fpath in files:
      fname = os.path.basename(fpath)
      is_sel = (fname == self.selected_save_filename)

      card = ctk.CTkFrame(
          self.scroll_saves,
          corner_radius=8,
          fg_color="#2c3e50" if is_sel else "#1e272e",
      )
      card.pack(fill="x", padx=5, pady=4)

      mtime = datetime.datetime.fromtimestamp(os.path.getmtime(fpath)).strftime("%Y-%m-%d %H:%M")

      btn = ctk.CTkButton(
          card,
          text=f"📁 {fname}\n🕒 {mtime}",
          font=ctk.CTkFont(size=13, weight="bold"),
          anchor="w",
          fg_color="transparent",
          hover_color="#34495e",
          command=lambda fn=fname: self.select_save_file(fn),
      )
      btn.pack(fill="both", expand=True, padx=8, pady=4)


  def select_save_file(self, fname):
    self.selected_save_filename = fname
    self.refresh_saves_list()

    fpath = os.path.join(self.saves_dir, fname)
    try:
      with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)
      self.update_save_info_text(data)
    except Exception as e:
      self.update_save_info_text({"error": str(e)})


  def update_save_info_text(self, data):
    self.txt_save_info.configure(state="normal")
    self.txt_save_info.delete("1.0", tk.END)

    if not data:
      self.txt_save_info.insert("1.0", "Оберіть збереження зі списку праворуч...")
    elif "error" in data:
      self.txt_save_info.insert("1.0", f"Помилка читання файлу: {data['error']}")
    else:
      txt = (
          f"📁 Файл: {self.selected_save_filename}\n"
          f"📅 День: {data.get('day', 1)}\n"
          f"💰 Баланс: {data.get('balance', 0)} грн\n"
          f"📦 Товарів на складі: {len(data.get('inventory', []))}\n"
          f"🔩 Запчастин на складі: {sum(data.get('parts_inventory', {}).values())}\n"
          f"📋 Клієнтських замовлень: {len(data.get('client_orders', []))}\n"
          f"🕒 Час збереження: {data.get('saved_at', 'Невідомо')}\n"
      )
      self.txt_save_info.insert("1.0", txt)

    self.txt_save_info.configure(state="disabled")


  def create_save_from_input(self):
    name = self.entry_save_name.get().strip()
    if not name:
      name = f"Save_Day{self.day}_{datetime.datetime.now().strftime('%H%M%S')}"

    safe_name = "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).rstrip()
    if not safe_name:
      safe_name = f"Save_Day{self.day}"
    filename = f"{safe_name}.json"

    fpath = os.path.join(self.saves_dir, filename)
    save_data = {
        "day": self.day,
        "balance": self.balance,
        "inventory": self.inventory,
        "parts_inventory": self.parts_inventory,
        "parts_costs": self.parts_costs,
        "client_orders": self.client_orders,
        "storage_dev_lvl": self.storage_dev_lvl,
        "storage_parts_lvl": self.storage_parts_lvl,
        "free_market_refresh_active": self.free_market_refresh_active,
        "ads_active": self.ads_active,
        "lawyer_lvl": self.lawyer_lvl,
        "pc_parts": self.pc_parts,
        "sound_enabled": self.sound_enabled,
        "tools": self.tools,
        "skills": getattr(self, "skills", {}),
        "scanner_license_permanent": getattr(self, "scanner_license_permanent", False),
        "pending_deliveries": getattr(self, "pending_deliveries", []),
        "tools_wear": getattr(self, "tools_wear", {}),
        "reputation_stars": getattr(self, "reputation_stars", 1),
        "location_lvl": self.location_lvl,
        "active_loan": self.active_loan,
        "mystery_boxes_bought_today": self.mystery_boxes_bought_today,
        "stats": self.stats,
        "transactions_history": self.transactions_history,
        "day_time_left": self.day_time_left,
        "saved_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    try:
      with open(fpath, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
      messagebox.showinfo("Успіх", f"Гру успішно збережено у файл '{filename}'!")
      self.selected_save_filename = filename
      self.refresh_saves_list()
      self.select_save_file(filename)
    except Exception as e:
      messagebox.showerror("Помилка збереження", f"Не вдалося зберегти гру:\n{e}")


  def load_selected_save(self):
    if not self.selected_save_filename:
      messagebox.showwarning("Увага", "Будь ласка, оберіть збереження для завантаження!")
      return

    fpath = os.path.join(self.saves_dir, self.selected_save_filename)
    if not os.path.exists(fpath):
      messagebox.showerror("Помилка", "Файл збереження не знайдено!")
      return

    try:
      with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)

      self.day = data.get("day", 1)
      self.balance = data.get("balance", 30000)
      self.inventory = data.get("inventory", [])
      self.parts_inventory = data.get("parts_inventory", {})
      self.parts_costs = data.get("parts_costs", {})
      self.client_orders = data.get("client_orders", [])
      self.storage_dev_lvl = data.get("storage_dev_lvl", 1)
      self.storage_parts_lvl = data.get("storage_parts_lvl", 1)
      self.free_market_refresh_active = data.get(
          "free_market_refresh_active", data.get("discount_market_active", False)
      )
      self.ads_active = data.get("ads_active", False)
      self.lawyer_lvl = data.get("lawyer_lvl", 0)
      self.pc_parts = data.get("pc_parts", {
          "case": False, "mobo": False, "cpu_ram": False, "psu": False, "database": False
      })
      self.sound_enabled = data.get("sound_enabled", True)
      self.tools = data.get("tools", {
          "screwdriver_set": False, "soldering_station": False, "screen_separator": False,
          "battery_tester": False, "programmer": False, "ultrasonic_bath": False
      })
      self.skills = data.get("skills", {
          "soldering_master": False, "bargaining_art": False, "neon_sign": False,
          "wholesale_partner": False, "scanner_permanent": False
      })
      self.scanner_license_permanent = data.get("scanner_license_permanent", self.skills.get("scanner_permanent", False))
      self.pending_deliveries = data.get("pending_deliveries", [])
      self.tools_wear = data.get("tools_wear", {k: 20 for k in self.TOOL_INFO.keys()})
      self.reputation_stars = data.get("reputation_stars", 1)
      self.location_lvl = data.get("location_lvl", 1)
      self.active_loan = data.get("active_loan", None)
      self.mystery_boxes_bought_today = data.get("mystery_boxes_bought_today", {"small": False, "medium": False, "vip": False})
      self.stats = data.get("stats", {
          "total_revenue": 0, "total_expenses": 0, "items_sold": 0,
          "orders_completed": 0, "pcs_assembled": 0, "police_confiscated": 0,
      })
      self.transactions_history = data.get("transactions_history", [])
      self.day_time_left = data.get("day_time_left", self.DAY_DURATION_SECONDS)

      self.refresh_market_stock()
      self.gen_item()
      self.show_screen("game")
      self.start_day_timer()
      messagebox.showinfo("Завантаження", f"Збереження '{self.selected_save_filename}' успішно завантажено!")
    except Exception as e:
      messagebox.showerror("Помилка", f"Не вдалося завантажити збереження:\n{e}")


  def delete_selected_save(self):
    if not self.selected_save_filename:
      messagebox.showwarning("Увага", "Будь ласка, оберіть збереження для видалення!")
      return

    confirm = messagebox.askyesno(
        "Підтвердження видалення",
        f"Чи справді ви хочете видалити збереження '{self.selected_save_filename}'?",
    )
    if confirm:
      fpath = os.path.join(self.saves_dir, self.selected_save_filename)
      try:
        if os.path.exists(fpath):
          os.remove(fpath)
        messagebox.showinfo("Видалено", f"Збереження '{self.selected_save_filename}' видалено.")
        self.selected_save_filename = None
        self.refresh_saves_list()
        self.update_save_info_text(None)
      except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося видалити файл:\n{e}")


  def quick_save(self):
    filename = f"QuickSave_Day{self.day}.json"
    fpath = os.path.join(self.saves_dir, filename)
    save_data = {
        "day": self.day,
        "balance": self.balance,
        "inventory": self.inventory,
        "parts_inventory": self.parts_inventory,
        "parts_costs": self.parts_costs,
        "client_orders": self.client_orders,
        "storage_dev_lvl": self.storage_dev_lvl,
        "storage_parts_lvl": self.storage_parts_lvl,
        "free_market_refresh_active": self.free_market_refresh_active,
        "ads_active": self.ads_active,
        "lawyer_lvl": self.lawyer_lvl,
        "pc_parts": self.pc_parts,
        "sound_enabled": self.sound_enabled,
        "tools": self.tools,
        "skills": getattr(self, "skills", {}),
        "scanner_license_permanent": getattr(self, "scanner_license_permanent", False),
        "pending_deliveries": getattr(self, "pending_deliveries", []),
        "tools_wear": getattr(self, "tools_wear", {}),
        "reputation_stars": getattr(self, "reputation_stars", 1),
        "location_lvl": self.location_lvl,
        "active_loan": self.active_loan,
        "mystery_boxes_bought_today": self.mystery_boxes_bought_today,
        "stats": self.stats,
        "transactions_history": self.transactions_history,
        "day_time_left": self.day_time_left,
        "saved_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    try:
      with open(fpath, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)
      messagebox.showinfo("Швидке збереження", f"Гру збережено у '{filename}'!")
    except Exception as e:
      messagebox.showerror("Помилка", f"Не вдалося зберегти:\n{e}")
