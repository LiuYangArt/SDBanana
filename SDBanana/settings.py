import os
import json

class SettingsManager:
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), "settings.json")
        self.settings = {
            "debug_mode": False,
            "save_generated_images": False
        }
        self.load()

    def load(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Update defaults with loaded values (preserves new keys if defaults change)
                    self.settings.update(loaded_settings)
            except Exception as e:
                print(f"Error loading settings: {e}")
        else:
            self.save()

    def save(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save()
