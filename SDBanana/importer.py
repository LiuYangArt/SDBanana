import os

try:
    import sd
    from sd.api.sdpackage import SDPackage
    from sd.api.sdresourcebitmap import SDResourceBitmap
    from sd.api.sdresourcefolder import SDResourceFolder
    from sd.api.sdresource import EmbedMethod
    from sd.api.sdgraph import SDGraph  
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
                if resource.getClassName() == "SDResourceFolder" and resource.getIdentifier() == folder_name:
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

    def import_image(self, file_path):
        """
        Imports an image file as a resource into the current package 
        (into SDBanana folder) and creates a bitmap node in the current graph.
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
            
            package = packages[0] # Use first user package
            
            # Get or create SDBanana folder
            folder = self._get_or_create_folder(package, "SDBanana")
            parent = folder if folder else package
            
            # Create bitmap resource from file
            # Try Embedded first, fallback to Linked if it fails
            resource = None
            embed_method = EmbedMethod.Linked  # Use Linked for reliability
            
            try:
                resource = SDResourceBitmap.sNewFromFile(
                    parent,
                    file_path,
                    embed_method
                )
            except Exception as e:
                # If embedding fails, the error will be caught by outer try-catch
                raise Exception(f"Failed to import with {embed_method}: {str(e)}")
            
            if not resource:
                return False, "Failed to create bitmap resource."
            
            # Set a clean identifier (filename without path)
            filename = os.path.splitext(os.path.basename(file_path))[0]
            try:
                resource.setIdentifier(filename)
            except:
                pass  # If identifier setting fails, continue anyway
            
            # Find a graph to place the node
            # Search recursively for graphs
            all_resources = package.getChildrenResources(True) # Recursive
            target_graph = None
            
            for child in all_resources:
                class_name = child.getClassName()
                if class_name == "SDGraph":
                    target_graph = child
                    break
            
            if not target_graph:
                return True, f"Resource imported to folder '{folder.getIdentifier() if folder else 'root'}' but no graph found. Please manually add to your graph."
            
            # Create bitmap node in the graph
            node = target_graph.newInstanceNode(resource)
            
            if node:
                folder_info = f" in folder '{folder.getIdentifier()}'" if folder else ""
                return True, f"Image imported{folder_info} and added to graph '{target_graph.getIdentifier()}'"
            else:
                return True, f"Resource imported but could not create node in graph."

        except Exception as e:
            return False, f"Import Error: {str(e)}"
