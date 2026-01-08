"""
Deterministic API Extractor for Live 11 API Documentation.

This script parses the live_api_11.pretty.xml file and extracts:
1. All Module names
2. All Class names within each module
3. All Method names within each class
4. All Property names within each class

Output is a structured JSON file for systematic comparison against
existing handler implementations.
"""

import xml.etree.ElementTree as ET
import json
import os

XML_PATH = r"c:\Users\hobo\Desktop\ableton-mcp\ableton-mcp\live_api_docs_download\live_api_11.pretty.xml"
OUTPUT_PATH = r"c:\Users\hobo\Desktop\ableton-mcp\ableton-mcp\api_extraction.json"

def extract_api_structure(xml_path):
    """Parse the XML and extract the full API structure."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    api_structure = {
        "version": root.get("version", "unknown"),
        "modules": {}
    }
    
    # Find the Live module
    live_module = root.find(".//Module[@name='Live']")
    if live_module is None:
        print("ERROR: Could not find Live module")
        return api_structure
    
    # Iterate through all child modules
    for module in live_module.findall("Module"):
        module_name = module.get("name", "Unknown")
        module_data = {
            "classes": {},
            "built_ins": []
        }
        
        # Extract Built-In functions (module-level)
        for builtin in module.findall("Built-In"):
            builtin_name = builtin.get("name", "")
            if builtin_name:
                desc_elem = builtin.find("Doc[@type='Description']")
                desc = desc_elem.text if desc_elem is not None and desc_elem.text else ""
                module_data["built_ins"].append({
                    "name": builtin_name,
                    "description": desc[:200] if desc else ""
                })
        
        # Extract Classes
        for cls in module.findall("Class"):
            class_name = cls.get("name", "Unknown")
            class_data = {
                "description": "",
                "methods": [],
                "properties": [],
                "sub_classes": []
            }
            
            # Class description
            desc_elem = cls.find("Doc[@type='Description']")
            if desc_elem is not None and desc_elem.text:
                class_data["description"] = desc_elem.text[:200]
            
            # Extract methods (excluding listeners)
            for method in cls.findall("Method"):
                method_name = method.get("name", "")
                if method_name and not method_name.endswith("_listener()"):
                    desc_elem = method.find("Doc[@type='Description']")
                    desc = desc_elem.text if desc_elem is not None and desc_elem.text else ""
                    class_data["methods"].append({
                        "name": method_name,
                        "description": desc[:200] if desc else ""
                    })
            
            # Extract properties
            for prop in cls.findall("Property"):
                prop_name = prop.get("name", "")
                if prop_name and not prop_name.startswith("_"):
                    desc_elem = prop.find("Doc[@type='Description']")
                    desc = desc_elem.text if desc_elem is not None and desc_elem.text else ""
                    class_data["properties"].append({
                        "name": prop_name,
                        "description": desc[:200] if desc else ""
                    })
            
            # Extract sub-classes (nested classes like View)
            for sub_cls in cls.findall("Class"):
                sub_class_name = sub_cls.get("name", "Unknown")
                sub_class_data = {
                    "methods": [],
                    "properties": []
                }
                
                for method in sub_cls.findall("Method"):
                    method_name = method.get("name", "")
                    if method_name and not method_name.endswith("_listener()"):
                        sub_class_data["methods"].append(method_name)
                
                for prop in sub_cls.findall("Property"):
                    prop_name = prop.get("name", "")
                    if prop_name and not prop_name.startswith("_"):
                        sub_class_data["properties"].append(prop_name)
                
                if sub_class_data["methods"] or sub_class_data["properties"]:
                    class_data["sub_classes"].append({
                        "name": sub_class_name,
                        **sub_class_data
                    })
            
            module_data["classes"][class_name] = class_data
        
        api_structure["modules"][module_name] = module_data
    
    return api_structure


def generate_summary(api_structure):
    """Generate a human-readable summary."""
    summary_lines = []
    summary_lines.append("=" * 60)
    summary_lines.append("LIVE 11 API EXTRACTION SUMMARY")
    summary_lines.append("=" * 60)
    summary_lines.append(f"API Version: {api_structure['version']}")
    summary_lines.append(f"Total Modules: {len(api_structure['modules'])}")
    summary_lines.append("")
    
    total_methods = 0
    total_properties = 0
    
    for module_name, module_data in sorted(api_structure["modules"].items()):
        class_count = len(module_data["classes"])
        builtin_count = len(module_data["built_ins"])
        
        method_count = sum(
            len(c["methods"]) + sum(len(sc.get("methods", [])) for sc in c.get("sub_classes", []))
            for c in module_data["classes"].values()
        )
        prop_count = sum(
            len(c["properties"]) + sum(len(sc.get("properties", [])) for sc in c.get("sub_classes", []))
            for c in module_data["classes"].values()
        )
        
        total_methods += method_count + builtin_count
        total_properties += prop_count
        
        summary_lines.append(f"Module: {module_name}")
        summary_lines.append(f"  Classes: {class_count}, Built-ins: {builtin_count}")
        summary_lines.append(f"  Methods: {method_count}, Properties: {prop_count}")
        
        # List class names
        for cls_name in sorted(module_data["classes"].keys()):
            summary_lines.append(f"    - {cls_name}")
    
    summary_lines.append("")
    summary_lines.append("=" * 60)
    summary_lines.append(f"TOTALS: {total_methods} methods, {total_properties} properties")
    summary_lines.append("=" * 60)
    
    return "\n".join(summary_lines)


if __name__ == "__main__":
    print("Extracting Live 11 API structure...")
    
    if not os.path.exists(XML_PATH):
        print(f"ERROR: XML file not found at {XML_PATH}")
        exit(1)
    
    api_structure = extract_api_structure(XML_PATH)
    
    # Save JSON output
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(api_structure, f, indent=2, ensure_ascii=False)
    print(f"JSON output saved to: {OUTPUT_PATH}")
    
    # Print summary
    summary = generate_summary(api_structure)
    print(summary)
    
    # Save summary to text file
    summary_path = OUTPUT_PATH.replace(".json", "_summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"Summary saved to: {summary_path}")
