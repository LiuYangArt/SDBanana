import os
import json

class PresetManager:
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), "presets.json")
        self.presets = []
        self.load()

    def load(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.presets = json.load(f)
            except Exception as e:
                print(f"Error loading presets: {e}")
                self.presets = []
        else:
            # Default presets
            self.presets = [
                {"name": "Upscale", "prompt": "Upscale to 4K"},
                {"name": "Make Grunge", "prompt": "生成一张Grunge Noise Alpha图，保持四方连续"}
            ]
            self.save()

    def save(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.presets, f, indent=4)
        except Exception as e:
            print(f"Error saving presets: {e}")

    def get_all_names(self):
        return [p["name"] for p in self.presets]

    def get_prompt(self, name):
        for p in self.presets:
            if p["name"] == name:
                return p["prompt"]
        return ""

    def add_preset(self, name, prompt):
        # Check if exists
        for p in self.presets:
            if p["name"] == name:
                return False, "Preset name already exists."
        
        self.presets.append({
            "name": name,
            "prompt": prompt
        })
        self.save()
        return True, "Preset added."

    def update_preset(self, name, new_prompt):
        for p in self.presets:
            if p["name"] == name:
                p["prompt"] = new_prompt
                self.save()
                return True, "Preset updated."
        return False, "Preset not found."

    def rename_preset(self, old_name, new_name):
        if old_name == new_name:
            return True, "Name unchanged."
            
        # Check if new name exists
        for p in self.presets:
            if p["name"] == new_name:
                return False, "New name already exists."

        for p in self.presets:
            if p["name"] == old_name:
                p["name"] = new_name
                self.save()
                return True, "Preset renamed."
        return False, "Preset not found."

    def delete_preset(self, name):
        for i, p in enumerate(self.presets):
            if p["name"] == name:
                del self.presets[i]
                self.save()
                return True, "Preset deleted."
        return False, "Preset not found."
