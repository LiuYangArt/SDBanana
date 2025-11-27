import os
import json
import urllib.request
import urllib.error
import ssl

class ProviderManager:
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), "providers.json")
        self.providers = []
        self.load()

    def load(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.providers = json.load(f)
            except Exception as e:
                print(f"Error loading providers: {e}")
                self.providers = []
        else:
            # Default providers if file doesn't exist
            self.providers = [
                {
                    "name": "Yunwu Gemini",
                    "apiKey": "",
                    "baseUrl": "https://yunwu.zeabur.app/v1beta",
                    "model": "gemini-3-pro-image-preview"
                },
                {
                    "name": "GPTGod NanoBanana Pro",
                    "apiKey": "",
                    "baseUrl": "https://api.gptgod.online/v1/chat/completions",
                    "model": "gemini-3-pro-image-preview"
                }
            ]
            self.save()

    def save(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.providers, f, indent=4)
        except Exception as e:
            print(f"Error saving providers: {e}")

    def get_provider(self, name):
        for p in self.providers:
            if p["name"] == name:
                return p
        return None

    def add_provider(self, name, api_key="", base_url="", model=""):
        # Check if exists
        for p in self.providers:
            if p["name"] == name:
                return False, "Provider name already exists."
        
        self.providers.append({
            "name": name,
            "apiKey": api_key,
            "baseUrl": base_url,
            "model": model
        })
        self.save()
        return True, "Provider added."

    def update_provider(self, original_name, api_key, base_url, model):
        for p in self.providers:
            if p["name"] == original_name:
                p["apiKey"] = api_key
                p["baseUrl"] = base_url
                p["model"] = model
                self.save()
                return True, "Provider updated."
        return False, "Provider not found."

    def delete_provider(self, name):
        for i, p in enumerate(self.providers):
            if p["name"] == name:
                del self.providers[i]
                self.save()
                return True, "Provider deleted."
        return False, "Provider not found."

    def get_all_names(self):
        return [p["name"] for p in self.providers]

    def test_connection(self, provider_config):
        api_key = provider_config.get("apiKey", "")
        base_url = provider_config.get("baseUrl", "")
        name = provider_config.get("name", "")
        
        if not api_key or not base_url:
            return False, "Missing API Key or Base URL."

        api_url = ""
        headers = {"Content-Type": "application/json"}
        
        # Logic adapted from PS_Banana.jsx
        if name == "Google Gemini" or name == "Yunwu Gemini":
            # Gemini style: .../models?key=API_KEY
            # Ensure no trailing slash for base_url before appending
            if base_url.endswith("/"):
                base_url = base_url[:-1]
            api_url = f"{base_url}/models?key={api_key}"
            
        elif "gptgod" in name.lower() or "gptgod" in base_url.lower():
            # GPTGod / OpenAI style
            # We want to hit /models
            if "/chat/completions" in base_url:
                api_url = base_url.replace("/chat/completions", "/models")
            else:
                if not base_url.endswith("/"):
                    base_url += "/"
                api_url = base_url + "models"
            
            headers["Authorization"] = f"Bearer {api_key}"
        else:
            # Custom / OpenAI compatible fallback
            if "v1" in base_url:
                api_url = base_url
                if "/chat/completions" in api_url:
                    api_url = api_url.replace("/chat/completions", "")
                if not api_url.endswith("/"):
                    api_url += "/"
                api_url += "models"
                headers["Authorization"] = f"Bearer {api_key}"
            else:
                return True, "Custom provider: Cannot automatically test. Please verify manually."

        try:
            # Create request
            req = urllib.request.Request(api_url, headers=headers, method="GET")
            
            # Create SSL context (ignore verification for simplicity/compatibility if needed, 
            # but standard is better. Let's start with standard.)
            # If users have cert issues, we might need ssl._create_unverified_context()
            context = ssl.create_default_context()
            
            with urllib.request.urlopen(req, context=context, timeout=10) as response:
                status = response.status
                response_body = response.read().decode('utf-8')
                
                if 200 <= status < 300:
                    try:
                        data = json.loads(response_body)
                        # Check for error fields even in 200 response (some APIs are weird)
                        if "error" in data:
                            return False, f"API Error: {data['error'].get('message', 'Unknown error')}"
                        return True, "Connection successful!"
                    except json.JSONDecodeError:
                        return False, "Invalid JSON response."
                else:
                    return False, f"HTTP Error: {status}"

        except urllib.error.HTTPError as e:
            return False, f"HTTP Error: {e.code} - {e.reason}"
        except urllib.error.URLError as e:
            return False, f"Connection Error: {e.reason}"
        except Exception as e:
            return False, f"Error: {str(e)}"

