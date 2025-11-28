import os

try:
    import sd
    from sd.api.sdpackage import SDPackage
    from sd.api.sdresourcebitmap import SDResourceBitmap
    from sd.api.sdresourcefolder import SDResourceFolder
    from sd.api.sdresource import EmbedMethod
    from sd.api.sdgraph import SDGraph
    from sd.api.sdproperty import SDPropertyCategory
    from sd.api.sdvaluestring import SDValueString
    from sd.api.sdbasetypes import float2

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

    def import_image(self, file_path, create_bitmap_node=True, insert_position=None):
        """
        Imports an image file as a resource into the current package
        (into SDBanana folder). Creates a bitmap node in the current graph if requested.

        Args:
            file_path: Path to the image file to import
            create_bitmap_node: If True, creates a bitmap node in the current active graph
            insert_position: Optional tuple(float, float) to position the bitmap node
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

                        success_msg += " and bitmap node created"
                    else:
                        success_msg += " (no active graph for node creation)"
                except Exception as e:
                    print(f"Warning: Failed to create bitmap node: {e}")
                    success_msg += " (node creation failed)"

            return True, success_msg

        except Exception as e:
            return False, f"Import Error: {str(e)}"
