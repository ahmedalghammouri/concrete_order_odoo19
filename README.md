# Concrete Order Module

## Overview
The Concrete Order module extends Odoo's manufacturing functionality to handle concrete delivery tickets and work orders with integrated spreadsheet printing capabilities.

## Features

### 1. Manufacturing Work Orders
- Custom concrete delivery ticket generation
- Integration with Odoo's manufacturing module
- Automated spreadsheet template population

### 2. Spreadsheet Integration
- **Template Management**: CDT (Concrete Delivery Ticket) templates
- **Auto-Print Functionality**: Programmatic spreadsheet printing
- **Template Processing**: Dynamic data population from work orders

### 3. Print Action
- **Action**: `action_print_spreadsheet`
- **Functionality**: Opens spreadsheet in new window and triggers automatic print
- **Method**: Simulates Ctrl+P keypress to leverage Odoo's native print handling

## File Structure

```
concrete_order/
├── __manifest__.py          # Module manifest
├── models/
│   └── __init__.py         # Model imports
├── static/src/js/
│   └── print_spreadsheet.js # Print action implementation
├── temp/                   # Template storage
│   └── CDT*.log           # Concrete delivery ticket templates
└── README.md              # This file
```

## Technical Implementation

### Print Spreadsheet Action
Located in `static/src/js/print_spreadsheet.js`

**How it works:**
1. Opens spreadsheet URL in new window
2. Waits for spreadsheet to load (3 seconds)
3. Dispatches Ctrl+P keyboard event
4. Leverages existing `useSpreadsheetPrint` hook from Odoo
5. Auto-closes window after printing (5 seconds)

**Key Code:**
```javascript
const ctrlPEvent = new KeyboardEvent('keydown', {
    key: 'p',
    ctrlKey: true,
    bubbles: true,
    cancelable: true
});
window.dispatchEvent(ctrlPEvent);
```

### Template System
- Templates stored in `temp/` directory
- JSON format with spreadsheet configuration
- Contains cell data, styling, and layout information
- Manufacturing delivery ticket format (CDT00006)

## Usage

### Printing Spreadsheets
```python
# Trigger print action
action = {
    'type': 'ir.actions.client',
    'tag': 'action_print_spreadsheet',
    'params': {
        'spreadsheet_id': spreadsheet_id
    }
}
```

### Template Structure
Templates include:
- Sheet dimensions and layout
- Cell content and formulas
- Styling and formatting
- Border and merge configurations
- Company and order information

## Dependencies
- `base` - Core Odoo functionality
- `mrp` - Manufacturing module
- `documents` - Document management
- `spreadsheet` - Spreadsheet functionality

## Installation
1. Place module in Odoo addons directory
2. Update app list
3. Install "Concrete Order" module
4. Configure manufacturing work orders

## Configuration
No additional configuration required. The module integrates seamlessly with existing manufacturing workflows.

## Compatibility
- **Odoo Version**: 19.0+
- **Dependencies**: Manufacturing, Documents, Spreadsheet modules
- **Browser**: Modern browsers with JavaScript support

## Support
For issues or customizations, refer to the module's technical documentation or contact the development team.