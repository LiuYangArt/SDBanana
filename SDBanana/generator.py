import os
import json
import base64
import time
import urllib.request
import urllib.error
import ssl
from datetime import datetime

class ImageGenerator:
    def __init__(self, provider_manager):
        self.provider_manager = provider_manager
        # AppData/Local/SD_Banana
        self.output_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'SD_Banana')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_image(self, prompt, provider_name, resolution="1K", search_web=False, debug_mode=False):
        provider = self.provider_manager.get_provider(provider_name)
        if not provider:
            return False, "Provider not found."

        api_key = provider.get("apiKey", "")
        base_url = provider.get("baseUrl", "")
        model = provider.get("model", "")

        if not api_key or not base_url:
            return False, "Missing API Key or Base URL."

        # Determine API Type and Construct Payload
        is_gptgod = "gptgod" in provider_name.lower() or "gptgod" in base_url.lower()
        
        payload = {}
        api_url = ""
        headers = {
            "Content-Type": "application/json"
        }

        if is_gptgod:
            # GPTGod / OpenAI Format
            api_url = base_url
            headers["Authorization"] = f"Bearer {api_key}"
            
            # Resolution Handling for GPTGod (Model Switching)
            actual_model = model
            if "gptgod.online" in base_url and model == "gemini-3-pro-image-preview":
                if resolution == "2K":
                    actual_model = "gemini-3-pro-image-preview-2k"
                elif resolution == "4K":
                    actual_model = "gemini-3-pro-image-preview-4k"
            
            messages = [{"role": "user", "content": prompt}]
            
            # TODO: Add Search Web tool if supported by GPTGod in this format?
            # Usually OpenAI format doesn't support 'tools' in the same way for image gen unless it's chat completion.
            # Assuming Chat Completion endpoint for GPTGod based on PS_Banana.jsx
            
            payload = {
                "model": actual_model,
                "messages": messages,
                "stream": False
            }
            
        else:
            # Gemini Format (Google / Yunwu)
            # URL: .../models/{model}:generateContent?key={key}
            if base_url.endswith("/"):
                base_url = base_url[:-1]
            api_url = f"{base_url}/models/{model}:generateContent?key={api_key}"
            
            # Resolution/Aspect Ratio for Gemini
            # Enforce 1:1 Aspect Ratio as requested
            generation_config = {
                "responseModalities": ["image"],
                "imageConfig": {
                    "aspectRatio": "1:1" 
                }
            }
            
            if resolution:
                generation_config["imageConfig"]["imageSize"] = resolution

            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": generation_config
            }
            
            if search_web:
                payload["tools"] = [{"google_search": {}}]

        # Debug Log
        if debug_mode:
            print(f"--- DEBUG ---")
            print(f"URL: {api_url}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            print(f"-------------")

        # Execute Request
        try:
            req = urllib.request.Request(api_url, data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")
            
            # SSL Context
            context = ssl.create_default_context()
            
            with urllib.request.urlopen(req, context=context, timeout=300) as response:
                if response.status != 200:
                    return False, f"HTTP Error: {response.status}"
                
                response_body = response.read().decode('utf-8')
                response_json = json.loads(response_body)
                
                if debug_mode:
                    print(f"Response: {json.dumps(response_json, indent=2)}")

                # Parse Response and Save Image
                return self._process_response(response_json, is_gptgod)

        except urllib.error.HTTPError as e:
            return False, f"HTTP Error: {e.code} - {e.reason}"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def _process_response(self, response_json, is_gptgod):
        image_data = None
        image_url = None

        # Extract Image Data
        if is_gptgod:
            # Check for URL
            if "image" in response_json:
                image_url = response_json["image"]
            elif "images" in response_json and response_json["images"]:
                image_url = response_json["images"][0]
            elif "data" in response_json and response_json["data"] and "url" in response_json["data"][0]:
                image_url = response_json["data"][0]["url"]
            # Check for Markdown image in content
            elif "choices" in response_json and response_json["choices"]:
                content = response_json["choices"][0]["message"]["content"]
                # Simple regex check for markdown image
                import re
                match = re.search(r'!\[.*?\]\((https?://[^)]+)\)', content)
                if match:
                    image_url = match.group(1)
                else:
                    match = re.search(r'(https?://[^\s]+\.(png|jpg|jpeg|webp|gif))', content, re.IGNORECASE)
                    if match:
                        image_url = match.group(1)
        else:
            # Gemini
            if "candidates" in response_json and response_json["candidates"]:
                parts = response_json["candidates"][0]["content"]["parts"]
                for part in parts:
                    if "inlineData" in part:
                        image_data = part["inlineData"]["data"] # Base64
                        break
                    # Check for text containing url? Usually Gemini returns inlineData for images.

        # Save Image
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        filename = f"sd_banana_{timestamp}.png" # Default to png, might change if webp
        filepath = os.path.join(self.output_dir, filename)

        if image_data:
            # Decode Base64
            try:
                with open(filepath, "wb") as f:
                    f.write(base64.b64decode(image_data))
                return True, filepath
            except Exception as e:
                return False, f"Failed to save base64 image: {e}"

        elif image_url:
            # Download URL
            try:
                # Determine extension from URL if possible
                if ".webp" in image_url.lower():
                    filename = f"sd_banana_{timestamp}.webp"
                    filepath = os.path.join(self.output_dir, filename)
                
                req = urllib.request.Request(image_url, headers={"User-Agent": "Mozilla/5.0"})
                context = ssl.create_default_context()
                with urllib.request.urlopen(req, context=context, timeout=60) as img_resp:
                    with open(filepath, "wb") as f:
                        f.write(img_resp.read())
                return True, filepath
            except Exception as e:
                return False, f"Failed to download image from URL: {e}"
        
        return False, "No image found in response."
