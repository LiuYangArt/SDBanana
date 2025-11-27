import os
from datetime import datetime
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL (Pillow) not found. WebP conversion disabled. Exporting as PNG.")

try:
    import sd
    from sd.api.sdnode import SDNode
    from sd.api.sdgraph import SDGraph
    from sd.api.sdproperty import SDPropertyCategory
    from sd.api.sdvaluetexture import SDValueTexture
    SD_AVAILABLE = True
except ImportError:
    SD_AVAILABLE = False
    print("Warning: Substance Designer API not found. Export functionality disabled.")

class NodeExporter:
    def __init__(self, output_dir=None):
        if SD_AVAILABLE:
            self.ctx = sd.getContext()
            self.app = self.ctx.getSDApplication()
            self.ui_mgr = self.app.getQtForPythonUIMgr()
        else:
            self.ctx = None
            self.ui_mgr = None
        
        # Set output directory
        if output_dir is None:
            import tempfile
            self.output_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'SD_Banana')
        else:
            self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def get_selected_nodes(self):
        """Get currently selected nodes from the active graph."""
        if not SD_AVAILABLE or not self.ui_mgr:
            return []
        
        try:
            selection = self.ui_mgr.getCurrentGraphSelectedNodes()
            return selection if selection else []
        except Exception as e:
            print(f"Error getting selected nodes: {e}")
            return []
    
    def export_selected_nodes(self):
        """Export all currently selected nodes to WebP format (or PNG if PIL is missing)."""
        if not SD_AVAILABLE:
            return False, "Substance Designer API not available."
        
        try:
            # Get current graph
            graph = self.ui_mgr.getCurrentGraph()
            if not graph:
                print("DEBUG: No active graph found.")
                return False, "No active graph found."
            print(f"DEBUG: Active graph found: {graph.getIdentifier()}")

            # Get selected nodes
            selected_nodes = self.get_selected_nodes()
            if not selected_nodes or len(selected_nodes) == 0:
                print("DEBUG: No nodes selected.")
                return False, "No nodes selected. Please select at least one node."
            print(f"DEBUG: Selected {len(selected_nodes)} nodes: {[n.getIdentifier() for n in selected_nodes]}")
            
            # Compute graph to ensure outputs are ready
            print("DEBUG: Computing graph...")
            graph.compute()
            
            exported_count = 0
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            
            for node in selected_nodes:
                node_id = node.getIdentifier()
                print(f"DEBUG: Processing node: {node_id}")
                
                # Get output properties
                output_props = node.getProperties(SDPropertyCategory.Output)
                if not output_props:
                    print(f"DEBUG: Node {node_id} has no output properties.")
                    continue
                
                for prop in output_props:
                    prop_id = prop.getId()
                    print(f"DEBUG: Checking property: {prop_id}")
                    
                    # Get property value
                    value = node.getPropertyValue(prop)
                    
                    # Check if it is a texture
                    if isinstance(value, SDValueTexture):
                        texture = value.get()
                        if texture:
                            # Try to save directly as WebP first
                            webp_filename = f"{node_id}_{prop_id}_{timestamp}.webp"
                            target_path = os.path.join(self.output_dir, webp_filename)
                            
                            direct_save_success = False
                            try:
                                print(f"DEBUG: Attempting direct save to: {target_path}")
                                texture.save(target_path)
                                # Verify if file exists and has size
                                if os.path.exists(target_path) and os.path.getsize(target_path) > 0:
                                    direct_save_success = True
                                    exported_count += 1
                                    print("DEBUG: Direct WebP save successful.")
                                else:
                                    print("DEBUG: Direct WebP save failed (file empty or missing).")
                            except Exception as e:
                                print(f"DEBUG: Direct WebP save failed with error: {e}")
                            
                            if not direct_save_success:
                                print("DEBUG: Falling back to PNG export + PIL conversion.")
                                # Fallback to PNG
                                png_filename = f"{node_id}_{prop_id}_{timestamp}.png"
                                temp_path = os.path.join(self.output_dir, png_filename)
                                
                                try:
                                    texture.save(temp_path)
                                    
                                    # Convert to WebP if available
                                    if PIL_AVAILABLE:
                                        if self.convert_to_webp(temp_path, target_path):
                                            exported_count += 1
                                            # Remove temp PNG
                                            try:
                                                os.remove(temp_path)
                                            except:
                                                pass
                                        else:
                                            # Keep PNG if conversion fails
                                            exported_count += 1
                                    else:
                                        exported_count += 1
                                except Exception as e:
                                    print(f"DEBUG: Fallback export failed: {e}")

                        else:
                             print(f"DEBUG: Property {prop_id} has no texture data.")
                    else:
                        print(f"DEBUG: Property {prop_id} value is not SDValueTexture: {type(value)}")

            if exported_count > 0:
                format_msg = "WebP" if PIL_AVAILABLE else "PNG (PIL not installed)"
                return True, f"Successfully exported {exported_count} images as {format_msg} to {self.output_dir}"
            else:
                print("DEBUG: Export failed - exported_count is 0")
                return False, "Export failed: No images were generated."

        except Exception as e:
            return False, f"Export Error: {str(e)}"

    def export_node(self, node):
        """Deprecated: Single node export is handled in batch by export_selected_nodes"""
        pass
    
    def convert_to_webp(self, source_path, target_path, quality=90):
        """Convert an image to WebP format."""
        if not PIL_AVAILABLE:
            return False
            
        try:
            with Image.open(source_path) as img:
                img.save(target_path, 'WEBP', quality=quality)
            return True
        except Exception as e:
            print(f"Error converting to WebP: {e}")
            return False
