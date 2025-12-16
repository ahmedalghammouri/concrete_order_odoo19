# Concrete Order - Sale Integration

## Overview
This module integrates Concrete Delivery Tickets with Odoo Sale Orders, allowing seamless tracking and management of concrete deliveries linked to sales.

## Features

### Concrete Delivery Ticket Enhancements
- Link delivery tickets to sale orders
- Link delivery tickets to specific sale order lines
- Automatic customer and product population from sale order
- Smart button to view related sale order

### Sale Order Enhancements
- Smart button showing linked delivery tickets count
- Total volume delivered display
- Quick access to all related delivery tickets

### Sale Order Line Enhancements
- Track total delivered volume per line
- Link to delivery tickets
- Computed field for delivered quantities

## Installation
1. Ensure `concrete_order`, `concrete_order_stock_out`, and `sale` modules are installed
2. Install this module from Apps menu
3. No additional configuration required

## Usage

### Creating a Delivery Ticket from Sale Order
1. Open a sale order (Sales > Orders > Orders)
2. Click the "Tickets" smart button
3. Create a new delivery ticket
4. Customer and product are auto-populated
5. Fill in delivery details and volume

### Linking Existing Ticket to Sale Order
1. Open a delivery ticket
2. Go to "Sale Order" tab
3. Select a sale order
4. Optionally select a specific sale order line
5. System auto-populates customer and product

### Monitoring Deliveries
- View ticket count and total volume in sale order
- Track delivered volume per sale order line
- Filter tickets by sale order

## Technical Details
- Extends: `concrete.delivery.ticket`, `sale.order`, `sale.order.line`
- Dependencies: `concrete_order`, `concrete_order_stock_out`, `sale`
- Version: 19.0.1.0.0
