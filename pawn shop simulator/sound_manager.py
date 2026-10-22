import winsound


class SoundManagerMixin:

  def play_sound(self, sound_type):
    if not getattr(self, "sound_enabled", True):
      return
    try:
      alias_map = {
          "deal": "SystemAsterisk",
          "repair": "SystemExclamation",
          "error": "SystemHand",
          "click": "SystemDefault",
      }
      alias = alias_map.get(sound_type, "SystemDefault")
      winsound.PlaySound(alias, winsound.SND_ALIAS | winsound.SND_ASYNC)
    except Exception:
      pass


  def toggle_sound(self):
    self.sound_enabled = not self.sound_enabled
    if hasattr(self, "btn_sound"):
      self.btn_sound.configure(
          text="🔊 Звук: УВІМК" if self.sound_enabled else "🔇 Звук: ВИМК",
          fg_color="#27ae60" if self.sound_enabled else "#7f8c8d",
          hover_color="#219150" if self.sound_enabled else "#636e72",
      )
    if self.sound_enabled:
      self.play_sound("click")
