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

        self.output_dir = os.path.join(os.getenv("LOCALAPPDATA"), "SD_Banana")

        if not os.path.exists(self.output_dir):

            os.makedirs(self.output_dir)

    def _convert_image_to_base64(self, image_path):
        """Convert an image file to a base64 string."""

        if not os.path.exists(image_path):

            return None

        try:

            with open(image_path, "rb") as image_file:

                return base64.b64encode(image_file.read()).decode("utf-8")

        except Exception as e:

            print(f"Error converting image to base64: {e}")

            return None

    def generate_image(
        self,
        prompt,
        provider_name,
        resolution="1K",
        search_web=False,
        debug_mode=False,
        input_image_path=None,
    ):

        # ==========================================

        # Definition of the AAA Material Artist Prompt

        # ==========================================
        material_artist_instruction = """
        角色：作为一名在顶级AAA游戏开发工作室工作的资深材质艺术家，擅长于创建照片级真实感、高保真度的PBR纹理。
        目标：根据用户需求绘制精彩的纹理贴图。 **关键要求：** 所有纹理必须严格是“无缝平铺”（四向连续）。
        无缝平铺规则（不可协商）：
        - 避免明显的“热点(hotspot)”，以避免此贴图在10x10平铺时产生网格效果。
        - Details flowing off the right edge must match perfectly with the left edge, same for top and bottom.
        - For brick/tile patterns, grout lines must be mathematically consistent at borders.
        质量保证指南（AAA标准）：
        1. 颜色贴图 (albedo/basecolor)去光照：albedo/basecolor贴图必须只包含颜色数据。不得有烘焙阴影或光照。
        2. 高度图(heightmap)/深度图(depthmap)：如果有参考图输入（input image），根据参考图内容制作符合现实逻辑的高度/深度。
        3. 视觉层次：包括宏观Macro（形状）、中观Meso（次要形式）和微观Micro（纹理/毛孔）细节。
        4. 视觉叙事：纹理必须有符合这个物体的使用痕迹，暗示它的历史（例如风化、划痕、氧化、破损、褪色等）。除非另有要求，否则不要制作“原始(pristine)”纹理。
        5. PBR定义：金属度(metallic)贴图清楚区分电介质和导体(dielectrics and conductors)。粗糙度(roughness)的变化是实现真实感的关键。
        """

        # ==========================================

        # Integrating into your existing logic

        # ==========================================

        # Append seamless tiling instruction

        system_prompt = f"**SYSTEM INSTRUCTION:** \n{material_artist_instruction}"

        user_prompt = f"**USER INSTRUCTION:** {prompt}"

        prompt = f"{user_prompt}\n\n{system_prompt}"

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

        is_openrouter = (
            "openrouter" in provider_name.lower() or "openrouter.ai" in base_url.lower()
        )

        is_google_official = (
            "generativelanguage.googleapis.com" in base_url.lower()
            or (
                "google" in provider_name.lower()
                and "gemini" in provider_name.lower()
                and "yunwu" not in provider_name.lower()
            )
        )

        payload = {}
        api_url = ""

        headers = {"Content-Type": "application/json"}

        # Prepare Image Data if input_image_path is provided

        base64_image = None

        mime_type = "image/png"  # Default

        if input_image_path:

            base64_image = self._convert_image_to_base64(input_image_path)

            if not base64_image:

                return False, f"Failed to process input image: {input_image_path}"

            if input_image_path.lower().endswith(".webp"):

                mime_type = "image/webp"

            elif input_image_path.lower().endswith(
                ".jpg"
            ) or input_image_path.lower().endswith(".jpeg"):

                mime_type = "image/jpeg"

        if is_openrouter:

            # OpenRouter Format (similar to OpenAI but with modalities and image_config)

            api_url = base_url

            headers["Authorization"] = f"Bearer {api_key}"

            # Build content list
            content = prompt

            # If there's an input image, we need to use content array format

            if base64_image:

                content = [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
                    },
                ]

            messages = [{"role": "user", "content": content}]

            # Build image_config based on resolution

            image_config = {"aspect_ratio": "1:1"}  # Default to square

            # Map resolution to OpenRouter's image_size format

            if resolution == "1K":

                image_config["image_size"] = "1K"

            elif resolution == "2K":

                image_config["image_size"] = "2K"

            elif resolution == "4K":

                image_config["image_size"] = "4K"

            payload = {
                "model": model,
                "messages": messages,
                "modalities": ["image", "text"],
                "image_config": image_config,
            }

        elif is_google_official:

            # Google Official Gemini API (uses snake_case, not camelCase)

            # URL: .../models/{model}:generateContent?key={key}

            if base_url.endswith("/"):

                base_url = base_url[:-1]

            api_url = f"{base_url}/models/{model}:generateContent?key={api_key}"

            # Google official API uses snake_case (response_modalities, image_config, aspect_ratio, image_size)

            generation_config = {
                "response_modalities": ["IMAGE"],  # Uppercase and snake_case
                "image_config": {"aspect_ratio": "1:1"},  # snake_case
            }

            if resolution:

                generation_config["image_config"][
                    "image_size"
                ] = resolution  # snake_case

            parts = [{"text": prompt}]

            if base64_image:

                parts.append(
                    {"inline_data": {"mime_type": mime_type, "data": base64_image}}
                )

            payload = {
                "contents": [{"parts": parts}],
                "generationConfig": generation_config,  # Still uses camelCase for top-level key
            }

            if search_web:

                payload["tools"] = [{"google_search": {}}]

        elif is_gptgod:

            # GPTGod / OpenAI Format

            api_url = base_url

            headers["Authorization"] = f"Bearer {api_key}"

            # Resolution Handling for GPTGod (Model Switching)
            actual_model = model

            if "gptgod.online" in base_url and model == "gemini-3-pro-image-preview":

                if resolution == "1K":

                    actual_model = "gemini-3-pro-image-preview"  # 1K uses base model

                elif resolution == "2K":

                    actual_model = "gemini-3-pro-image-preview-2k"

                elif resolution == "4K":

                    actual_model = "gemini-3-pro-image-preview-4k"

                # If no match, keep original model (fallback)

            content_list = [{"type": "text", "text": prompt}]

            if base64_image:

                content_list.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
                    }
                )

            messages = [{"role": "user", "content": content_list}]

            # TODO: Add Search Web tool if supported by GPTGod in this format?

            # Usually OpenAI format doesn't support 'tools' in the same way for image gen unless it's chat completion.

            # Assuming Chat Completion endpoint for GPTGod based on PS_Banana.jsx

            payload = {"model": actual_model, "messages": messages, "stream": False}

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
                "imageConfig": {"aspectRatio": "1:1"},
            }

            if resolution:

                generation_config["imageConfig"]["imageSize"] = resolution

            parts = [{"text": prompt}]

            if base64_image:

                parts.append(
                    {"inline_data": {"mime_type": mime_type, "data": base64_image}}
                )

            payload = {
                "contents": [{"parts": parts}],
                "generationConfig": generation_config,
            }

            if search_web:

                payload["tools"] = [{"google_search": {}}]

        # Debug Log

        if debug_mode:

            print(f"--- DEBUG MODE ENABLED ---")

            print(f"Output Directory: {self.output_dir}")

            print(f"Provider: {provider_name}")

            print(f"Resolution Setting: {resolution}")

            print(f"Is GPTGod: {is_gptgod}")

            print(f"Is OpenRouter: {is_openrouter}")

            print(f"Is Google Official: {is_google_official}")

            if is_gptgod:

                print(f"Original Model: {model}")

                print(f"Actual Model (after resolution): {actual_model}")

            print(f"URL: {api_url}")

            # Truncate base64 for console logging

            log_payload = json.loads(json.dumps(payload))

            if is_openrouter or is_gptgod:

                # Handle OpenRouter and GPTGod format

                if "messages" in log_payload and log_payload["messages"]:

                    content = log_payload["messages"][0].get("content", [])

                    if isinstance(content, list) and len(content) > 1:

                        if "image_url" in content[1]:

                            content[1]["image_url"]["url"] = "<BASE64_IMAGE_DATA>"

            else:

                if "contents" in log_payload and log_payload["contents"]:

                    parts = log_payload["contents"][0].get("parts", [])

                    if len(parts) > 1:

                        if "inline_data" in parts[1]:

                            parts[1]["inline_data"]["data"] = "<BASE64_IMAGE_DATA>"

            print(f"Payload: {json.dumps(log_payload, indent=2)}")

            print(f"-------------")

            # Save full payload to file

            try:

                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

                log_filename = f"debug_payload_{timestamp}.json"

                log_path = os.path.join(self.output_dir, log_filename)

                with open(log_path, "w", encoding="utf-8") as f:

                    json.dump(payload, f, indent=4, ensure_ascii=False)

                print(f"Debug payload saved to: {log_path}")

            except Exception as e:

                print(f"Failed to save debug payload: {e}")

        # Execute Request

        try:

            req = urllib.request.Request(
                api_url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )

            # SSL Context

            context = ssl.create_default_context()

            with urllib.request.urlopen(req, context=context, timeout=300) as response:

                if response.status != 200:

                    return False, f"HTTP Error: {response.status}"

                response_body = response.read().decode("utf-8")

                response_json = json.loads(response_body)

                if debug_mode:

                    print(f"Response: {json.dumps(response_json, indent=2)}")

                # Parse Response and Save Image

                return self._process_response(
                    response_json, is_gptgod, is_openrouter, is_google_official
                )

        except urllib.error.HTTPError as e:

            return False, f"HTTP Error: {e.code} - {e.reason}"

        except Exception as e:

            return False, f"Error: {str(e)}"

    def _process_response(
        self, response_json, is_gptgod, is_openrouter=False, is_google_official=False
    ):

        image_data = None

        image_url = None

        # Extract Image Data

        if is_openrouter:

            # OpenRouter format: choices[0].message.images[].image_url.url

            if "choices" in response_json and response_json["choices"]:

                message = response_json["choices"][0].get("message", {})

                if "images" in message and message["images"]:

                    # Get the first image

                    image_info = message["images"][0]

                    if "image_url" in image_info:

                        image_url_data = image_info["image_url"].get("url", "")

                        # Check if it's a base64 data URL

                        if image_url_data.startswith("data:image"):

                            # Extract base64 data from data URL

                            # Format: data:image/png;base64,xxxxx

                            if ";base64," in image_url_data:

                                image_data = image_url_data.split(";base64,")[1]

                        else:

                            # It's a regular URL
                            image_url = image_url_data

        elif is_gptgod:

            # Check for URL

            if "image" in response_json:

                image_url = response_json["image"]

            elif "images" in response_json and response_json["images"]:

                image_url = response_json["images"][0]

            elif (
                "data" in response_json
                and response_json["data"]
                and "url" in response_json["data"][0]
            ):

                image_url = response_json["data"][0]["url"]

            # Check for Markdown image in content

            elif "choices" in response_json and response_json["choices"]:

                content = response_json["choices"][0]["message"]["content"]

                # Simple regex check for markdown image
                import re

                match = re.search(r"!\[.*?\]\((https?://[^)]+)\)", content)

                if match:

                    image_url = match.group(1)

                else:

                    match = re.search(
                        r"(https?://[^\s]+\.(png|jpg|jpeg|webp|gif))",
                        content,
                        re.IGNORECASE,
                    )

                    if match:

                        image_url = match.group(1)

        else:

            # Gemini Format (Google Official or Yunwu/Third-party proxies)

            # Response format is the same: candidates[0].content.parts[].inlineData.data

            if "candidates" in response_json and response_json["candidates"]:

                parts = response_json["candidates"][0]["content"]["parts"]

                for part in parts:

                    if "inlineData" in part:

                        image_data = part["inlineData"]["data"]  # Base64

                        break

                    # Check for text containing url? Usually Gemini returns inlineData for images.

        # Save Image

        timestamp = datetime.now().strftime("%Y%m%d%H%M")

        filename = f"sd_banana_{timestamp}.png"  # Default to png, might change if webp

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

                req = urllib.request.Request(
                    image_url, headers={"User-Agent": "Mozilla/5.0"}
                )

                context = ssl.create_default_context()

                with urllib.request.urlopen(
                    req, context=context, timeout=60
                ) as img_resp:

                    with open(filepath, "wb") as f:

                        f.write(img_resp.read())

                return True, filepath

            except Exception as e:

                return False, f"Failed to download image from URL: {e}"

        return False, "No image found in response."
