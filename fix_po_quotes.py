import os
import re

def fix_po_line(line):
    """Fix a single line in PO file by escaping unescaped quotes"""
    # Only process msgid and msgstr lines
    if not (line.startswith('msgid "') or line.startswith('msgstr "')):
        return line
    
    # Find the prefix (msgid " or msgstr ")
    if line.startswith('msgid "'):
        prefix = 'msgid "'
    else:
        prefix = 'msgstr "'
    
    # Check if line ends with "
    if not line.rstrip().endswith('"'):
        return line
    
    # Extract content between quotes
    start_idx = len(prefix)
    end_idx = line.rstrip().rfind('"')
    
    if start_idx >= end_idx:
        return line
    
    content = line[start_idx:end_idx]
    
    # Replace unescaped quotes with escaped ones
    # First, temporarily mark already escaped quotes
    content = content.replace('\\"', '\x00ESCAPED\x00')
    # Escape all remaining quotes
    content = content.replace('"', '\\"')
    # Restore the already escaped quotes
    content = content.replace('\x00ESCAPED\x00', '\\"')
    
    # Reconstruct the line
    return prefix + content + '"\n'

def fix_po_file(filepath):
    """Fix all unescaped quotes in a PO file"""
    print(f"Processing: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        fixed_lines = []
        for i, line in enumerate(lines, 1):
            try:
                fixed_line = fix_po_line(line)
                fixed_lines.append(fixed_line)
            except Exception as e:
                print(f"  Error on line {i}: {e}")
                fixed_lines.append(line)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        
        print(f"  [OK] Fixed successfully")
        return True
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        return False

# List of PO files to fix
po_files = [
    r"c:\Users\ODOO\Documents\ODOO 19\odoo\concrete\concrete_order\i18n\ar_001.po",
    r"c:\Users\ODOO\Documents\ODOO 19\odoo\concrete\concrete_order_cmdp\i18n\ar_001.po",
    r"c:\Users\ODOO\Documents\ODOO 19\odoo\concrete\concrete_order_sale\i18n\ar_001.po",
    r"c:\Users\ODOO\Documents\ODOO 19\odoo\concrete\concrete_order_stock_out\i18n\ar_001.po",
    r"c:\Users\ODOO\Documents\ODOO 19\odoo\concrete\concrete_order_zpl\i18n\ar_001.po"
]

print("=" * 60)
print("Fixing PO files - Escaping double quotes")
print("=" * 60)

success_count = 0
for po_file in po_files:
    if os.path.exists(po_file):
        if fix_po_file(po_file):
            success_count += 1
    else:
        print(f"Not found: {po_file}")

print("=" * 60)
print(f"Completed: {success_count}/{len(po_files)} files fixed successfully")
print("=" * 60)
