/** @odoo-module **/

import { registry } from "@web/core/registry";

registry.category("actions").add("action_print_spreadsheet", async function (_, action) {
    if (!action.params?.spreadsheet_id) {
        console.error("Missing spreadsheet_id parameter");
        return;
    }
    
    const spreadsheetId = action.params.spreadsheet_id;
    const url = `${window.location.origin}/odoo/documents/spreadsheet/${spreadsheetId}`;
    
    const printWindow = window.open(url, '_blank');
    
    if (printWindow) {
        printWindow.onload = function() {
            setTimeout(() => {
                const script = printWindow.document.createElement('script');
                script.textContent = `
                    (function() {
                        console.log('Waiting for spreadsheet to load...');
                        function waitAndTriggerPrint() {
                            setTimeout(() => {
                                console.log('Triggering Ctrl+P');
                                
                                const ctrlPEvent = new KeyboardEvent('keydown', {
                                    key: 'p',
                                    ctrlKey: true,
                                    bubbles: true,
                                    cancelable: true
                                });
                                
                                window.dispatchEvent(ctrlPEvent);
                                
                                setTimeout(() => {
                                    console.log('Closing window');
                                }, 5000);
                            }, 3000);
                        }
                        
                        waitAndTriggerPrint();
                    })();
                `;
                printWindow.document.head.appendChild(script);
            }, 2000);
        };
    } else {
        console.error("Failed to open print window - popup blocked?");
    }
});

// window.close();