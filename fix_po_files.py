import re
import os

def fix_po_file(filepath):
    """Fix unescaped double quotes in PO file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match msgid or msgstr lines with unescaped quotes
    def fix_quotes(match):
        line = match.group(0)
        # Extract the content between the outer quotes
        if line.startswith('msgid "') or line.startswith('msgstr "'):
            prefix = line[:line.index('"') + 1]
            suffix = line[line.rindex('"'):]
            middle = line[line.index('"') + 1:line.rindex('"')]
            # Escape any unescaped double quotes in the middle
            middle_fixed = middle.replace('\\"', '###ESCAPED###').replace('"', '\\"').replace('###ESCAPED###', '\\"')
            return prefix + middle_fixed + suffix
        return line
    
    # Fix msgid and msgstr lines
    content_fixed = re.sub(r'^(msgid|msgstr) ".*"$', fix_quotes, content, flags=re.MULTILINE)
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content_fixed)
    
    print(f"Fixed: {filepath}")

# Fix all PO files
po_files = [
    r"c:\Users\ODOO\Documents\ODOO 19\odoo\concrete\concrete_order\i18n\ar_001.po",
    r"c:\Users\ODOO\Documents\ODOO 19\odoo\concrete\concrete_order_cmdp\i18n\ar_001.po",
    r"c:\Users\ODOO\Documents\ODOO 19\odoo\concrete\concrete_order_sale\i18n\ar_001.po",
    r"c:\Users\ODOO\Documents\ODOO 19\odoo\concrete\concrete_order_stock_out\i18n\ar_001.po",
    r"c:\Users\ODOO\Documents\ODOO 19\odoo\concrete\concrete_order_zpl\i18n\ar_001.po"
]

for po_file in po_files:
    if os.path.exists(po_file):
        fix_po_file(po_file)
    else:
        print(f"Not found: {po_file}")

print("\nAll PO files have been fixed!")
