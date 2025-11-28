import os
import math
import zlib

try:
    import sd
    from sd.api.sdpackage import SDPackage
    from sd.api.sdresourcebitmap import SDResourceBitmap
    from sd.api.sdresourcefolder import SDResourceFolder
    from sd.api.sdresource import EmbedMethod
    from sd.api.sdgraph import SDGraph
    from sd.api.sdproperty import SDPropertyCategory
    from sd.api.sdvaluestring import SDValueString
    from sd.api.sdvalueint2 import SDValueInt2
    from sd.api.sdvaluebool import SDValueBool
    from sd.api.sdproperty import SDPropertyInheritanceMethod
    from sd.api.sdbasetypes import float2, int2

    SD_AVAILABLE = True
except ImportError:
    SD_AVAILABLE = False


# --- Utility: quick PNG grayscale detection (no external libs) ---
# Returns True if PNG is grayscale (color_type 0/4), False if color (2/3/6), None if not PNG or error

def is_png_rgb_equal_quick(path: str):
    try:
        with open(path, 'rb') as f:
            sig = f.read(8)
            if sig != b'\x89PNG\r\n\x1a\n':
                return None
            length = int.from_bytes(f.read(4), 'big')
            ctype = f.read(4)
            if ctype != b'IHDR':
                return None
            ihdr = f.read(length)
            color_type = ihdr[9]  # 0=Gray,2=RGB,3=Indexed,4=Gray+Alpha,6=RGB+Alpha
            f.read(4)  # CRC
            return color_type in (0, 4)
    except Exception:
        return None


# ---- 完整 PNG 校验（8-bit、非交错 Truecolor/Truecolor+Alpha） ----

def _paeth(a, b, c):
    p = a + b - c
    pa = abs(p - a); pb = abs(p - b); pc = abs(p - c)
    if pa <= pb and pa <= pc: return a
    if pb <= pc: return b
    return c

def _unfilter_scanline(ftype, scanline, prev, bpp):
    res = bytearray(scanline)
    if ftype == 0:
        return res
    elif ftype == 1:  # Sub
        for i in range(bpp, len(res)):
            res[i] = (res[i] + res[i - bpp]) & 0xFF
    elif ftype == 2:  # Up
        if prev is None: prev = bytearray(len(res))
        for i in range(len(res)):
            res[i] = (res[i] + prev[i]) & 0xFF
    elif ftype == 3:  # Average
        if prev is None: prev = bytearray(len(res))
        for i in range(len(res)):
            left = res[i - bpp] if i >= bpp else 0
            up = prev[i]
            res[i] = (res[i] + ((left + up) // 2)) & 0xFF
    elif ftype == 4:  # Paeth
        if prev is None: prev = bytearray(len(res))
        for i in range(len(res)):
            left = res[i - bpp] if i >= bpp else 0
            up = prev[i]
            up_left = prev[i - bpp] if i >= bpp else 0
            res[i] = (res[i] + _paeth(left, up, up_left)) & 0xFF
    else:
        raise ValueError("Unsupported PNG filter")
    return res

def is_png_rgb_equal_full(path: str):
    """真正解码像素判断 R/G/B 是否完全一致。仅支持 bit_depth=8、interlace=0 的 color_type=2/6。灰度(0/4)直接返回 True。非 PNG 或不支持返回 None。"""
    try:
        with open(path, 'rb') as f:
            data = f.read()
        if data[:8] != b'\x89PNG\r\n\x1a\n':
            return None
        i = 8
        # IHDR
        length = int.from_bytes(data[i:i+4], 'big'); i += 4
        if data[i:i+4] != b'IHDR': return None
        i += 4
        ihdr = data[i:i+length]; i += length
        i += 4  # CRC
        width = int.from_bytes(ihdr[0:4], 'big')
        height = int.from_bytes(ihdr[4:8], 'big')
        bit_depth = ihdr[8]
        color_type = ihdr[9]
        interlace = ihdr[12]
        if color_type in (0, 4):
            return True
        if color_type not in (2, 6) or bit_depth != 8 or interlace != 0:
            return None
        # Collect IDAT
        idat = bytearray()
        while i + 8 <= len(data):
            clen = int.from_bytes(data[i:i+4], 'big'); i += 4
            ctype = data[i:i+4]; i += 4
            cdata = data[i:i+clen]; i += clen
            i += 4  # CRC
            if ctype == b'IDAT':
                idat.extend(cdata)
            elif ctype == b'IEND':
                break
        raw = zlib.decompress(bytes(idat))
        bpp = 4 if color_type == 6 else 3
        stride = width * bpp
        pos = 0
        prev = None
        for _ in range(height):
            ftype = raw[pos]; pos += 1
            scan = raw[pos:pos+stride]; pos += stride
            row = _unfilter_scanline(ftype, scan, prev, bpp)
            for j in range(0, len(row), bpp):
                r, g, b = row[j], row[j+1], row[j+2]
                if not (r == g == b):
                    return False
            prev = row
        return True
    except Exception:
        return None

# --- JPEG quick grayscale check ---

def is_jpeg_rgb_equal_quick(path: str):
    try:
        with open(path, 'rb') as f:
            data = f.read()
        if not data.startswith(b'\xFF\xD8'):
            return None
        i = 2
        while i < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            while i < len(data) and data[i] == 0xFF:
                i += 1
            if i >= len(data):
                break
            marker = data[i]; i += 1
            if marker in (0xD8, 0xD9) or (0xD0 <= marker <= 0xD7):
                continue
            if i + 2 > len(data):
                break
            seglen = int.from_bytes(data[i:i+2], 'big'); i += 2
            if marker in (0xC0, 0xC1, 0xC2):
                if i + seglen - 2 > len(data):
                    break
                components = data[i + 5]
                return components == 1
            i += seglen - 2
        return None
    except Exception:
        return None

# --- Format detection ---

def detect_image_format(path: str):
    try:
        with open(path, 'rb') as f:
            header = f.read(12)
        if header.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'png'
        if header.startswith(b'\xFF\xD8'):
            return 'jpeg'
        if header[0:4] == b'RIFF' and header[8:12] == b'WEBP':
            return 'webp'
        if header.startswith(b'GIF87a') or header.startswith(b'GIF89a'):
            return 'gif'
        if header.startswith(b'BM'):
            return 'bmp'
        return None
    except Exception:
        return None

# --- Unified quick grayscale by format ---

def is_image_grayscale_quick(path: str):
    fmt = detect_image_format(path)
    if fmt == 'png':
        return is_png_rgb_equal_quick(path)
    if fmt == 'jpeg':
        return is_jpeg_rgb_equal_quick(path)
    return None

class ImageImporter:
    def __init__(self):
        if SD_AVAILABLE:
            self.ctx = sd.getContext()
            self.app = self.ctx.getSDApplication()
            self.pkg_mgr = self.app.getPackageMgr()
        else:
            self.ctx = None

    def _get_or_create_folder(self, package, folder_name="SDBanana"):
        """Get or create a resource folder in the package."""
        try:
            # Check if folder already exists
            resources = package.getChildrenResources(False)
            for resource in resources:
                if (
                    resource.getClassName() == "SDResourceFolder"
                    and resource.getIdentifier() == folder_name
                ):
                    return resource

            # Create new folder
            folder = SDResourceFolder.sNew(package)
            if folder:
                folder.setIdentifier(folder_name)
                return folder
            return None
        except Exception as e:

            return None
    
    def _calculate_dimensions(self, resolution, aspect_ratio):
        """
        Calculate image dimensions based on resolution and aspect ratio.
        
        Args:
            resolution: "1K", "2K", or "4K"
            aspect_ratio: String like "1:1", "16:9", "9:16", etc.
            
        Returns:
            tuple: (width_power, height_power) as powers of 2 (e.g., 10 for 1024)
        """
        # Base size as power of 2
        # 1K = 1024 = 2^10
        # 2K = 2048 = 2^11  
        # 4K = 4096 = 2^12
        base_size_powers = {
            "1K": 10,
            "2K": 11,
            "4K": 12
        }
        base_power = base_size_powers.get(resolution, 10)
        
        # Parse aspect ratio
        try:
            ratio_parts = aspect_ratio.split(":")
            if len(ratio_parts) == 2:
                w_ratio = float(ratio_parts[0])
                h_ratio = float(ratio_parts[1])
            else:
                w_ratio, h_ratio = 1.0, 1.0
        except:
            w_ratio, h_ratio = 1.0, 1.0
        
        # For square (1:1), both dimensions use base power
        if w_ratio == h_ratio:
            return base_power, base_power
        
        # For non-square, adjust based on ratio
        # The larger dimension keeps the base power
        # The smaller dimension is reduced accordingly
        if w_ratio > h_ratio:
            # Landscape: width is larger
            width_power = base_power
            # Calculate height power (reduce by ratio)
            ratio = h_ratio / w_ratio
            height_power = base_power + int(round(math.log2(ratio)))
            return width_power, height_power
        else:
            # Portrait: height is larger
            height_power = base_power
            # Calculate width power (reduce by ratio)
            ratio = w_ratio / h_ratio
            width_power = base_power + int(round(math.log2(ratio)))
            return width_power, height_power

    def import_image(self, file_path, create_bitmap_node=True, insert_position=None, resolution="1K", aspect_ratio="1:1"):
        """
        Imports an image file as a resource into the current package
        (into SDBanana folder). Creates a bitmap node in the current graph if requested.

        Args:
            file_path: Path to the image file to import
            create_bitmap_node: If True, creates a bitmap node in the current active graph
            insert_position: Optional tuple(float, float) to position the bitmap node
            resolution: Resolution setting used for generation ("1K", "2K", "4K")
            aspect_ratio: Aspect ratio of the generated image (e.g., "1:1", "16:9")
        """
        if not SD_AVAILABLE:
            return False, "Substance Designer API not available."

        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"

        try:
            # Get user packages
            packages = self.pkg_mgr.getUserPackages()
            if not packages or len(packages) == 0:
                return False, "No package open in Substance Designer."

            package = packages[0]  # Use first user package

            # Get or create SDBanana folder
            folder = self._get_or_create_folder(package, "SDBanana")
            parent = folder if folder else package

            # Try different embed methods
            resource = None
            tried_methods = []

            # Method 1: Try CopiedAndLinked (copies file and links to copy)
            try:
                resource = SDResourceBitmap.sNewFromFile(
                    parent, file_path, EmbedMethod.CopiedAndLinked
                )
                if resource:
                    tried_methods.append("CopiedAndLinked (success)")
            except Exception as e:
                tried_methods.append(f"CopiedAndLinked (failed: {e})")

            # Method 2: Fallback to Linked if CopiedAndLinked failed
            if not resource:
                try:
                    resource = SDResourceBitmap.sNewFromFile(
                        parent, file_path, EmbedMethod.Linked
                    )
                    if resource:
                        tried_methods.append("Linked (success)")
                except Exception as e:
                    tried_methods.append(f"Linked (failed: {e})")

            if not resource:
                error_detail = "; ".join(tried_methods)
                return False, f"Failed to create resource. Attempts: {error_detail}"

            # Set a clean identifier (filename without path)
            filename = os.path.splitext(os.path.basename(file_path))[0]
            try:
                resource.setIdentifier(filename)
            except:
                pass  # If identifier setting fails, continue anyway

            # Resource imported successfully!
            folder_msg = f"in folder 'SDBanana'" if folder else "in package"
            success_msg = f"Resource imported {folder_msg}"

            # Create bitmap node in current graph if requested
            if create_bitmap_node:
                try:
                    uiMgr = self.app.getQtForPythonUIMgr()
                    graph = uiMgr.getCurrentGraph()

                    if graph:
                        # Create bitmap node
                        bitmap_node = graph.newNode("sbs::compositing::bitmap")

                        # Set node position
                        if insert_position and isinstance(insert_position, (tuple, list)) and len(insert_position) == 2:
                            bitmap_node.setPosition(float2(insert_position[0], insert_position[1]))
                        else:
                            bitmap_node.setPosition(float2(50, 50))

                        # Set the bitmap resource path
                        bitmap_resource_property = bitmap_node.getPropertyFromId(
                            "bitmapresourcepath", SDPropertyCategory.Input
                        )
                        resource_url = SDValueString.sNew(resource.getUrl())
                        bitmap_node.setPropertyValue(
                            bitmap_resource_property, resource_url
                        )

                        # Auto set Color Mode based on image header
                        try:
                            fmt = detect_image_format(file_path)
                            is_gray = is_image_grayscale_quick(file_path)
                            applied = False
                            if is_gray is not None:
                                try:
                                    color_switch_prop = bitmap_node.getPropertyFromId('colorswitch', SDPropertyCategory.Input)
                                    if color_switch_prop:
                                        bitmap_node.setPropertyValue(color_switch_prop, SDValueBool.sNew(is_gray is False))

                                        applied = True
                                except Exception:
                                    pass
                                if not applied:
                                    mode_value = SDValueString.sNew("grayscale" if is_gray else "color")
                                    for pid in ("bitmapcolormode", "colormode", "colorMode"):
                                        try:
                                            prop = bitmap_node.getPropertyFromId(pid, SDPropertyCategory.Input)
                                            if prop:
                                                bitmap_node.setPropertyValue(prop, mode_value)

                                                applied = True
                                                break
                                        except Exception:
                                            pass
                            elif fmt == 'png':
                                # Fallback: use full PNG pixel check when quick result is None
                                full_gray = is_png_rgb_equal_full(file_path)
                                if full_gray is not None:
                                    try:
                                        color_switch_prop = bitmap_node.getPropertyFromId('colorswitch', SDPropertyCategory.Input)
                                        if color_switch_prop:
                                            bitmap_node.setPropertyValue(color_switch_prop, SDValueBool.sNew(full_gray is False))

                                        else:
                                            raise Exception('colorswitch not found')
                                    except Exception:
                                        mode_value = SDValueString.sNew("grayscale" if full_gray else "color")
                                        for pid in ("bitmapcolormode", "colormode", "colorMode"):
                                            try:
                                                prop = bitmap_node.getPropertyFromId(pid, SDPropertyCategory.Input)
                                                if prop:
                                                    bitmap_node.setPropertyValue(prop, mode_value)

                                                    break
                                            except Exception:
                                                pass
                        except Exception as e:
                            pass

                        # Set output size to Absolute and use calculated dimensions
                        try:
                            # Calculate dimensions from resolution and aspect ratio
                            width_power, height_power = self._calculate_dimensions(resolution, aspect_ratio)
                            actual_width = 2 ** width_power
                            actual_height = 2 ** height_power
                            
                            # Set the inheritance method for $outputsize to Absolute
                            # This changes the dropdown from "Relative to Parent" to "Absolute"
                            bitmap_node.setInputPropertyInheritanceMethodFromId(
                                "$outputsize",
                                SDPropertyInheritanceMethod.Absolute
                            )
                            
                            # Set the actual output size value (as power of 2)
                            bitmap_node.setInputPropertyValueFromId(
                                "$outputsize",
                                SDValueInt2.sNew(int2(width_power, height_power))
                            )

                        except Exception as e:
                            pass

                        success_msg += " and bitmap node created"
                    else:
                        success_msg += " (no active graph for node creation)"
                except Exception as e:
                    pass
                    success_msg += " (node creation failed)"

            return True, success_msg

        except Exception as e:
            return False, f"Import Error: {str(e)}"
