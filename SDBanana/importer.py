import os
import math

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
    from sd.api.sdproperty import SDPropertyInheritanceMethod
    from sd.api.sdbasetypes import float2, int2

    SD_AVAILABLE = True
except ImportError:
    SD_AVAILABLE = False
    print("Warning: Substance Designer API not found. Import functionality disabled.")


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
            print(f"Folder creation error: {e}")
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
                            bitmap_node.setPosition(float2(0, 0))

                        # Set the bitmap resource path
                        bitmap_resource_property = bitmap_node.getPropertyFromId(
                            "bitmapresourcepath", SDPropertyCategory.Input
                        )
                        resource_url = SDValueString.sNew(resource.getUrl())
                        bitmap_node.setPropertyValue(
                            bitmap_resource_property, resource_url
                        )

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
                            print(f"Set bitmap node output size to {actual_width}x{actual_height}px (Absolute)")
                        except Exception as e:
                            print(f"Warning: Failed to set output size: {e}")
                            import traceback
                            traceback.print_exc()

                        success_msg += " and bitmap node created"
                    else:
                        success_msg += " (no active graph for node creation)"
                except Exception as e:
                    print(f"Warning: Failed to create bitmap node: {e}")
                    success_msg += " (node creation failed)"

            return True, success_msg

        except Exception as e:
            return False, f"Import Error: {str(e)}"
