import os
import json


DEFAULT_SYSTEM_INSTRUCTION = """
# CRITICAL REQUIREMENT: SEAMLESS TILING

All generated textures must be strictly **Seamless Tiling** (continuous 4-way across both U and V axes).
**Seamless Tiling Rules (Non-negotiable):**
- **Eliminate Hotspots:** Avoid distinct "hotspots" or unique, high-contrast details that create visible repetition patterns (gridding effects) when the texture is tiled at large scales (e.g., a 10x10 array).
- **Perfect Edge Matching:** Details flowing off the right edge must match perfectly with the left edge; the same applies to the top and bottom edges.
- **Consistent Structure:** For brick, tile, or pave patterns, grout lines and structural elements must remain mathematically consistent across borders.
---
## Quality Assurance Guidelines (AAA Standard)
**1. Albedo/Base Color De-lighting**
- The Albedo map must contain purely chromatic/diffuse color data.
- It must be completely **delighted**, free of any baked-in shadows, ambient occlusion (AO), or directional lighting information.
**2. Height/Depth Map Logic**
- If an input reference image is provided, generate physically accurate height/depth displacement based on its content.
- The height map must be pure displacement data and **must not** contain any baked Ambient Occlusion (AO) or lighting information.
**3. Visual Hierarchy** The texture must possess distinct levels of detail to ensure it reads well at various distances:
- **Macro:** Large primary shapes and forms.
- **Meso:** Secondary forms, medium details, and edge definition.
- **Micro:** Fine surface texture, pores, and grain.
**4. Visual Storytelling & Wear**
- The material must exhibit realistic wear and tear appropriate to its physical properties, implying a history of use.
- Examples include weathering, scratches, oxidation/rust, structural damage, or sun-fading.
- **Do not** generate "pristine" or brand-new textures unless explicitly requested.
**5. PBR Definition**
- **Metallic Definition:** The metallic map must clearly and binarily distinguish between dielectrics (non-metals, usually black/0.0) and conductors (metals, usually white/1.0).
- **Albedo/basecolor Value Validation (Critical PBR Compliance):** The brightness range of the Albedo map must correspond to the material type defined in the Metallic map:
    - **For Dielectrics (Non-metals):** Albedo brightness must fall within physically accurate darker-to-mid ranges (typically sRGB 30-220). Absolutely avoid pure black (0) or pure white (255).
    - **For Conductors (Metals):** The Albedo represents reflective F0 color and must be bright (typically sRGB 180-255).
- **Roughness:** Nuanced and varied roughness maps are critical for achieving photorealism. Avoid uniform roughness values; incorporate surface imperfections that affect light reflections.
"""


class SettingsManager:
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), "settings.json")
        self.settings = {
            "debug_mode": False,
            "save_generated_images": False,
            "selected_provider": None,
            "system_instruction": DEFAULT_SYSTEM_INSTRUCTION,
        }
        self.load()

    def load(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded_settings = json.load(f)
                    # Update defaults with loaded values (preserves new keys if defaults change)
                    self.settings.update(loaded_settings)
            except Exception as e:
                print(f"Error loading settings: {e}")
        else:
            self.save()

    def save(self):
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save()
