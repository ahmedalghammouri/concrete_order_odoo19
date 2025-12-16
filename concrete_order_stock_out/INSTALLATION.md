# Installation Guide

## Prerequisites
- Odoo 19.0
- `concrete_order` module installed
- `stock` module installed

## Installation Steps

1. **Restart Odoo Server**
   ```
   Restart your Odoo service to detect the new module
   ```

2. **Update Apps List**
   - Go to Apps menu
   - Click "Update Apps List"
   - Confirm the update

3. **Install Module**
   - Search for "Concrete Order - Stock Integration"
   - Click Install

4. **Verify Installation**
   - Open a delivery order (Inventory > Delivery Orders > Outgoing)
   - You should see a "Tickets" smart button
   - Open a concrete delivery ticket
   - You should see "Stock Operations" section with "Delivery Order" field

## Module Structure
```
concrete_order_stock_out/
├── models/
│   ├── __init__.py
│   ├── concrete_delivery_ticket.py  # Extends concrete.delivery.ticket
│   └── stock_picking.py             # Extends stock.picking
├── views/
│   ├── concrete_delivery_ticket_views.xml  # Ticket form/list enhancements
│   └── stock_picking_views.xml             # Delivery order enhancements
├── security/
│   └── ir.model.access.csv
├── __init__.py
├── __manifest__.py
└── README.md
```

## Key Features Added

### To Concrete Delivery Ticket:
- `delivery_id`: Link to stock.picking (delivery order)
- `location_id`: Source warehouse location
- `demand_qty`: Expected quantity from delivery order
- `variance_qty`: Difference between delivered and demanded
- `fulfillment_percent`: Percentage of demand fulfilled
- `action_update_delivery()`: Sync quantities to stock moves

### To Stock Picking:
- `ticket_count`: Number of linked delivery tickets
- `total_volume_delivered`: Sum of all ticket volumes
- `action_view_delivery_tickets()`: View all related tickets

## Troubleshooting

### Module Not Appearing
- Ensure the module is in the correct addons path
- Check Odoo logs for any import errors
- Verify all dependencies are installed

### Fields Not Showing
- Clear browser cache
- Restart Odoo server
- Update the module if already installed

### Permission Issues
- Ensure users have proper access rights to stock and concrete_order modules
