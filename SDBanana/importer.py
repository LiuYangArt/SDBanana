import os

try:
    import sd
    from sd.api.sdpackage import SDPackage
    from sd.api.sdresourcebitmap import SDResourceBitmap
    from sd.api.sdgraph import SDGraph
    from sd.api.sdnode import SDNode
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

    def import_image(self, file_path):
        """
        Imports an image file as a resource into the current package 
        and creates a node in the current graph.
        """
        if not SD_AVAILABLE:
            return False, "Substance Designer API not available."

        if not os.path.exists(file_path):
            return False, "File not found."

        # Get Current Graph and Package
        # Note: This logic assumes the user has a graph open and focused.
        # We might need to iterate or get the 'active' one.
        
        # Strategy: Get the package of the currently selected graph or just the first user package.
        # SD API doesn't always have a clear "Active Document" like Photoshop.
        # We'll try to get the package that contains the currently visible graph.
        
        # For now, let's grab the first user package if available.
        packages = self.pkg_mgr.getUserPackages()
        if not packages or len(packages) == 0:
            return False, "No package open in Substance Designer."
        
        package = packages[0] # Default to first package
        
        # Import Resource
        try:
            # Check if resource already exists? 
            # SD usually handles duplicates or we can rename.
            # createResource(resourcePath, resourceType)
            # resourceType for bitmap is SDResourceBitmap? Or just use the class type?
            # The API usually expects the type class or an enum.
            # Based on docs, createResource takes (path, type_id/class).
            
            # Let's try importing.
            resource = package.createResource(file_path, SDResourceBitmap.sClass())
            if not resource:
                return False, "Failed to create resource."
            
            # Now add to Graph
            # We need the current graph.
            # Is there a way to get the active graph?
            # ui_mgr = self.app.getQtForPythonUIMgr() ? No.
            
            # Let's search for a graph in the package.
            graphs = package.getChildrenResources(False) # False = non-recursive?
            target_graph = None
            
            # Filter for SDGraph
            for child in graphs:
                if issubclass(type(child), SDGraph) or child.getClassName() == "SDGraph":
                    target_graph = child
                    break
            
            if not target_graph:
                return False, "No graph found in the package."
            
            # Create Node
            # newInstanceNode(resource)
            node = target_graph.newInstanceNode(resource)
            if node:
                # Position the node?
                # node.setPosition(float2(0, 0))
                return True, f"Image imported to graph '{target_graph.getIdentifier()}'"
            else:
                return False, "Failed to create node instance."

        except Exception as e:
            return False, f"Import Error: {str(e)}"
