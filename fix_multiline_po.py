import re

def fix_po_file_comprehensive(filepath):
    """Fix all unescaped quotes in PO file, including multi-line entries"""
    print(f"Processing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into lines for processing
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Only process lines that start with " (continuation lines in multi-line strings)
        if line.strip().startswith('"') and not line.strip().startswith('#'):
            # This is a string continuation line
            # Extract the content
            stripped = line.strip()
            if stripped.endswith('"') and len(stripped) > 1:
                # Get leading whitespace
                leading_space = line[:len(line) - len(line.lstrip())]
                # Extract content between quotes
                content_part = stripped[1:-1]
                # Escape unescaped quotes
                content_part = content_part.replace('\\"', '\x00ESCAPED\x00')
                content_part = content_part.replace('"', '\\"')
                content_part = content_part.replace('\x00ESCAPED\x00', '\\"')
                # Reconstruct line
                fixed_lines.append(leading_space + '"' + content_part + '"')
            else:
                fixed_lines.append(line)
        elif line.startswith('msgid "') or line.startswith('msgstr "'):
            # Single line msgid/msgstr
            if line.rstrip().endswith('"'):
                if line.startswith('msgid "'):
                    prefix = 'msgid "'
                else:
                    prefix = 'msgstr "'
                
                start_idx = len(prefix)
                end_idx = line.rstrip().rfind('"')
                
                if start_idx < end_idx:
                    content_part = line[start_idx:end_idx]
                    # Escape unescaped quotes
                    content_part = content_part.replace('\\"', '\x00ESCAPED\x00')
                    content_part = content_part.replace('"', '\\"')
                    content_part = content_part.replace('\x00ESCAPED\x00', '\\"')
                    fixed_lines.append(prefix + content_part + '"')
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Write back
    with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(fixed_lines))
    
    print(f"  [OK] Fixed")

# Fix the problematic file
po_file = r"c:\Users\ODOO\Documents\ODOO 19\odoo\concrete\concrete_order_stock_out\i18n\ar_001.po"
fix_po_file_comprehensive(po_file)
print("\nDone!")
