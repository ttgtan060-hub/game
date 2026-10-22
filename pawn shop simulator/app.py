import os
import customtkinter as ctk
from data_manager import DataManagerMixin
from sound_manager import SoundManagerMixin
from save_manager import SaveManagerMixin
from game_logic import GameLogicMixin
from ui_manager import UiManagerMixin

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class PawnshopGame(
    ctk.CTk,
    DataManagerMixin,
    SoundManagerMixin,
    SaveManagerMixin,
    GameLogicMixin,
    UiManagerMixin,
):

  def __init__(self):
    super().__init__()

    self.title("📱 TechPawn: Скупка, Ремонт, Ринок деталей, Вітрина та Прокачка")
    self.geometry("1060x840")
    self.resizable(False, False)

    target_saves = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "saves"
    )
    try:
      os.makedirs(target_saves, exist_ok=True)
      t_file = os.path.join(target_saves, ".perm_test")
      with open(t_file, "w") as f:
        f.write("1")
      os.remove(t_file)
      self.saves_dir = target_saves
    except (PermissionError, OSError):
      user_docs = os.path.join(os.path.expanduser("~"), "Documents", "TechPawn Simulator", "saves")
      os.makedirs(user_docs, exist_ok=True)
      self.saves_dir = user_docs
    self.selected_save_filename = None

    self.load_game_data()

    self.day = 1
    self.balance = 30000
    self.inventory = []
    self.parts_inventory = {}
    self.parts_costs = {}
    self.market_items = []
    self.market_original_items = []
    self.pending_deliveries = []
    self.client_orders = []

    self.storage_dev_lvl = 1
    self.storage_parts_lvl = 1
    self.free_market_refresh_active = False
    self.ads_active = False
    self.lawyer_lvl = 0
    self.pc_parts = {
        "case": False,
        "mobo": False,
        "cpu_ram": False,
        "psu": False,
        "database": False,
    }
    self.location_lvl = 1
    self.active_loan = None
    self.mystery_boxes_bought_today = {"small": False, "medium": False, "vip": False}
    self.scanner_license_permanent = False
    self.skills = {
        "soldering_master": False,
        "bargaining_art": False,
        "neon_sign": False,
        "wholesale_partner": False,
        "scanner_permanent": False,
    }
    self.tools_wear = {k: 20 for k in self.TOOL_INFO.keys()}
    self.reputation_stars = 1
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
    self.sound_enabled = True
    self.tools = {
        "screwdriver_set": False,
        "soldering_station": False,
        "screen_separator": False,
        "battery_tester": False,
        "programmer": False,
        "ultrasonic_bath": False,
    }
    self.day_time_left = self.DAY_DURATION_SECONDS
    self.day_timer_running = False
    self.day_timer_after_id = None

    self.cur_is_repair_order = False
    self.cur_is_express = False
    self.cur_is_trade_in = False
    self.cur_trade_in_target_idx = None
    self.cur_client_patience_type = 3
    self.cur_client_patience = 100
    self.cur_brand = ""
    self.cur_is_fake = False
    self.cur_dev = ""
    self.cur_base_price = 0
    self.cur_fair_price = 0
    self.cur_real_status = "нормальний"
    self.cur_dmg_list = []
    self.cur_est_repair_min = 0
    self.cur_est_repair_max = 0
    self.cur_client_price = 0
    self.cur_fair_repair_cost = 0
    self.cur_client_max_repair_budget = 0
    self.cur_repair_reward = 0
    self.cur_is_stolen = False
    self.cur_is_checked = False
    self.qte_police_timer_id = None
    self.qte_police_active = False

    self.daily_report = {
        "rent": 800,
        "utilities": 200,
        "sold_items": [],
        "completed_orders": [],
        "abandoned_devices": [],
        "failed_orders": [],
        "police_incidents": [],
        "net_income": 0,
    }

    self.init_catalog()
    self.setup_ui_containers()
    self.show_screen("menu")


  def destroy(self):
    self.stop_day_timer()
    if getattr(self, "qte_police_timer_id", None):
      try:
        self.after_cancel(self.qte_police_timer_id)
      except Exception:
        pass
    super().destroy()


def run_game():
  app = PawnshopGame()
  app.mainloop()
