"""
Detailed API Decomposition Script for Live 11 API.

This script creates per-module reference files containing:
- Method signatures with arguments and types
- Return types
- Property types and descriptions
- Organized for systematic implementation

Output: One markdown file per module in the api_modules/ directory
"""

import xml.etree.ElementTree as ET
import os
import re

XML_PATH = r"c:\Users\hobo\Desktop\ableton-mcp\ableton-mcp\live_api_docs_download\live_api_11.pretty.xml"
OUTPUT_DIR = r"c:\Users\hobo\Desktop\ableton-mcp\ableton-mcp\api_modules"

def parse_format_string(format_str):
    """Parse a method format string to extract arguments and return type."""
    if not format_str:
        return {"args": [], "return_type": "None"}
    
    # Pattern: method_name( (Type)arg1, (Type)arg2, ... ) → ReturnType
    # Also handles: method_name( (Type)self ) → ReturnType
    
    result = {"args": [], "return_type": "None"}
    
    # Extract return type
    if "→" in format_str:
        parts = format_str.split("→")
        result["return_type"] = parts[-1].strip()
    
    # Extract arguments
    # Find content between first ( and last )
    match = re.search(r'\(\s*(.+)\s*\)\s*→', format_str)
    if match:
        args_str = match.group(1)
        # Split by comma, but handle nested parentheses
        arg_parts = []
        depth = 0
        current = ""
        for char in args_str:
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
            elif char == ',' and depth == 0:
                arg_parts.append(current.strip())
                current = ""
                continue
            current += char
        if current.strip():
            arg_parts.append(current.strip())
        
        for arg in arg_parts:
            # Pattern: (Type)name or (Type)name=default
            arg_match = re.match(r'\(([^)]+)\)(\w+)(?:=(.+))?', arg.strip())
            if arg_match:
                arg_type = arg_match.group(1)
                arg_name = arg_match.group(2)
                default = arg_match.group(3)
                if arg_name not in ['self', 'arg1']:  # Skip self references
                    result["args"].append({
                        "name": arg_name,
                        "type": arg_type,
                        "default": default
                    })
    
    return result


def generate_module_markdown(module_name, module_data):
    """Generate a detailed markdown reference for a module."""
    lines = []
    lines.append(f"# Live.{module_name} Module Reference\n")
    lines.append(f"Auto-generated from Live 11 API documentation.\n")
    lines.append("---\n")
    
    # Built-ins
    if module_data.get("built_ins"):
        lines.append("## Module-Level Functions\n")
        for builtin in module_data["built_ins"]:
            name = builtin.get("name", "")
            desc = builtin.get("description", "")
            format_str = builtin.get("format", "")
            
            parsed = parse_format_string(format_str)
            
            lines.append(f"### `{name}`\n")
            if desc:
                lines.append(f"**Description:** {desc}\n")
            if parsed["args"]:
                lines.append("**Arguments:**")
                for arg in parsed["args"]:
                    default_str = f" = {arg['default']}" if arg.get('default') else ""
                    lines.append(f"- `{arg['name']}` ({arg['type']}){default_str}")
                lines.append("")
            lines.append(f"**Returns:** `{parsed['return_type']}`\n")
            lines.append("---\n")
    
    # Classes
    for class_name, class_data in module_data.get("classes", {}).items():
        # Skip internal container classes
        if class_name.endswith("Vector") or class_name == "LimitationError":
            continue
            
        lines.append(f"## Class: {class_name}\n")
        
        if class_data.get("description"):
            lines.append(f"*{class_data['description']}*\n")
        
        # Properties
        if class_data.get("properties"):
            lines.append("### Properties\n")
            lines.append("| Property | Type | Description | Access |")
            lines.append("|----------|------|-------------|--------|")
            for prop in class_data["properties"]:
                name = prop.get("name", "")
                desc = prop.get("description", "")[:100]  # Truncate
                # Infer access from description
                access = "R/W" if "Get/Set" in desc or "Read/write" in desc else "R"
                # Try to infer type from description
                type_hint = "unknown"
                if "bool" in desc.lower() or "true" in desc.lower() or "false" in desc.lower():
                    type_hint = "bool"
                elif "float" in desc.lower():
                    type_hint = "float"
                elif "int" in desc.lower():
                    type_hint = "int"
                elif "string" in desc.lower() or "name" in name.lower():
                    type_hint = "str"
                elif "list" in desc.lower() or "access to" in desc.lower():
                    type_hint = "list"
                lines.append(f"| `{name}` | {type_hint} | {desc}... | {access} |")
            lines.append("")
        
        # Methods
        if class_data.get("methods"):
            lines.append("### Methods\n")
            for method in class_data["methods"]:
                name = method.get("name", "")
                desc = method.get("description", "")
                format_str = method.get("format", "")
                
                parsed = parse_format_string(format_str)
                
                lines.append(f"#### `{name}`\n")
                if desc:
                    lines.append(f"{desc}\n")
                
                if parsed["args"]:
                    lines.append("**Arguments:**\n")
                    for arg in parsed["args"]:
                        default_str = f" *(default: {arg['default']})*" if arg.get('default') else ""
                        lines.append(f"- `{arg['name']}`: `{arg['type']}`{default_str}")
                    lines.append("")
                
                lines.append(f"**Returns:** `{parsed['return_type']}`\n")
        
        # Sub-classes (like View)
        for sub_class in class_data.get("sub_classes", []):
            sub_name = sub_class.get("name", "")
            lines.append(f"### Sub-Class: {class_name}.{sub_name}\n")
            
            if sub_class.get("properties"):
                lines.append("**Properties:**")
                for prop in sub_class["properties"]:
                    lines.append(f"- `{prop}`")
                lines.append("")
            
            if sub_class.get("methods"):
                lines.append("**Methods:**")
                for method in sub_class["methods"]:
                    lines.append(f"- `{method}`")
                lines.append("")
        
        lines.append("---\n")
    
    return "\n".join(lines)


def extract_detailed_api(xml_path):
    """Extract detailed API information including format strings."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    modules = {}
    
    live_module = root.find(".//Module[@name='Live']")
    if live_module is None:
        print("ERROR: Could not find Live module")
        return modules
    
    for module in live_module.findall("Module"):
        module_name = module.get("name", "Unknown")
        module_data = {
            "classes": {},
            "built_ins": []
        }
        
        # Extract Built-In functions with format strings
        for builtin in module.findall("Built-In"):
            name = builtin.get("name", "")
            if name:
                desc_elem = builtin.find("Doc[@type='Description']")
                format_elem = builtin.find("Doc[@type='Format']")
                module_data["built_ins"].append({
                    "name": name,
                    "description": desc_elem.text if desc_elem is not None and desc_elem.text else "",
                    "format": format_elem.text if format_elem is not None and format_elem.text else ""
                })
        
        # Extract Classes with full details
        for cls in module.findall("Class"):
            class_name = cls.get("name", "Unknown")
            class_data = {
                "description": "",
                "methods": [],
                "properties": [],
                "sub_classes": []
            }
            
            desc_elem = cls.find("Doc[@type='Description']")
            if desc_elem is not None and desc_elem.text:
                class_data["description"] = desc_elem.text
            
            # Methods with format strings
            for method in cls.findall("Method"):
                method_name = method.get("name", "")
                if method_name and not method_name.endswith("_listener()"):
                    desc_elem = method.find("Doc[@type='Description']")
                    format_elem = method.find("Doc[@type='Format']")
                    class_data["methods"].append({
                        "name": method_name,
                        "description": desc_elem.text if desc_elem is not None and desc_elem.text else "",
                        "format": format_elem.text if format_elem is not None and format_elem.text else ""
                    })
            
            # Properties
            for prop in cls.findall("Property"):
                prop_name = prop.get("name", "")
                if prop_name and not prop_name.startswith("_"):
                    desc_elem = prop.find("Doc[@type='Description']")
                    class_data["properties"].append({
                        "name": prop_name,
                        "description": desc_elem.text if desc_elem is not None and desc_elem.text else ""
                    })
            
            # Sub-classes
            for sub_cls in cls.findall("Class"):
                sub_class_name = sub_cls.get("name", "Unknown")
                sub_class_data = {
                    "name": sub_class_name,
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
                    class_data["sub_classes"].append(sub_class_data)
            
            module_data["classes"][class_name] = class_data
        
        modules[module_name] = module_data
    
    return modules


if __name__ == "__main__":
    print("Extracting detailed Live 11 API structure...")
    
    if not os.path.exists(XML_PATH):
        print(f"ERROR: XML file not found at {XML_PATH}")
        exit(1)
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}")
    
    # Extract API
    modules = extract_detailed_api(XML_PATH)
    print(f"Found {len(modules)} modules")
    
    # Generate per-module markdown files
    for module_name, module_data in modules.items():
        md_content = generate_module_markdown(module_name, module_data)
        output_path = os.path.join(OUTPUT_DIR, f"{module_name}.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"  Created: {module_name}.md")
    
    # Create index file
    index_lines = ["# Live 11 API Module Index\n"]
    index_lines.append("Auto-generated reference files for systematic implementation.\n")
    index_lines.append("---\n")
    index_lines.append("| Module | Classes | Methods | Properties | Reference |")
    index_lines.append("|--------|---------|---------|------------|-----------|")
    
    for module_name, module_data in sorted(modules.items()):
        class_count = len(module_data["classes"])
        method_count = sum(len(c["methods"]) for c in module_data["classes"].values()) + len(module_data["built_ins"])
        prop_count = sum(len(c["properties"]) for c in module_data["classes"].values())
        index_lines.append(f"| {module_name} | {class_count} | {method_count} | {prop_count} | [{module_name}.md]({module_name}.md) |")
    
    index_path = os.path.join(OUTPUT_DIR, "INDEX.md")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("\n".join(index_lines))
    print(f"  Created: INDEX.md")
    
    print("\nDone! Per-module reference files created.")
