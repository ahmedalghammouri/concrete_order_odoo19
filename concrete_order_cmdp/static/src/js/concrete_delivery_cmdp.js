/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class ConcreteDeliveryCMDPInterface extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        
        this.state = useState({
            activeTab: 'overview',
            barcode: "",
            deliveries: [],
            deliveryOrders: [],
            fleetQueue: [],
            searchText: "",
            selectedDelivery: null,
            analytics: {
                completed_today: 0,
                in_progress: 0,
                avg_time: "15m",
                waiting_count: 0,
                total_volume_today: 0,
            },
            quickStats: {
                draft: 0,
                confirmed: 0,
                in_transit: 0,
            },
            recentActivity: [],
            loading: false,
            lastRefresh: new Date(),
        });

        this.refreshInterval = null;

        onWillStart(async () => {
            await this.loadDeliveries();
            await this.loadDeliveryOrders();
            await this.loadFleetQueue();
            await this.loadAnalytics();
            await this.loadRecentActivity();
        });

        onMounted(() => {
            this.refreshInterval = setInterval(async () => {
                await this.refreshData();
            }, 60000);
            document.addEventListener('keydown', this.handleKeyPress.bind(this));
        });

        onWillUnmount(() => {
            if (this.refreshInterval) clearInterval(this.refreshInterval);
            document.removeEventListener('keydown', this.handleKeyPress.bind(this));
        });
    }

    async loadDeliveries() {
        try {
            this.state.deliveries = await this.orm.call(
                "concrete.delivery.ticket",
                "get_pending_deliveries",
                []
            );
        } catch (error) {
            this.notification.add("Failed to load deliveries", { type: "danger" });
        }
    }

    async loadDeliveryOrders() {
        try {
            this.state.deliveryOrders = await this.orm.call(
                "concrete.delivery.ticket",
                "get_delivery_orders",
                []
            );
        } catch (error) {
            console.error("Error loading delivery orders:", error);
        }
    }

    async loadFleetQueue() {
        try {
            this.state.fleetQueue = await this.orm.call(
                "concrete.delivery.ticket",
                "get_fleet_queue",
                []
            );
        } catch (error) {
            console.error("Error loading fleet queue:", error);
        }
    }

    async onBarcodeInput(ev) {
        if (ev.key === "Enter" && this.state.barcode) {
            await this.scanBarcode();
        }
    }

    async scanBarcode() {
        if (!this.state.barcode) return;
        
        try {
            const delivery = await this.orm.call(
                "concrete.delivery.ticket",
                "action_scan_barcode",
                [this.state.barcode]
            );
            
            if (delivery && delivery.id) {
                this.action.doAction({
                    type: "ir.actions.act_window",
                    res_model: "concrete.delivery.ticket",
                    res_id: delivery.id,
                    views: [[false, "form"]],
                    view_mode: "form",
                    target: "current",
                });
            }
            this.state.barcode = "";
        } catch (error) {
            this.notification.add(error.message || "Barcode not found", { type: "danger" });
            this.state.barcode = "";
        }
    }

    async createFromDeliveryOrder(deliveryId) {
        try {
            const ticket = await this.orm.call(
                "concrete.delivery.ticket",
                "create_from_delivery",
                [deliveryId]
            );
            
            if (ticket && ticket.id) {
                this.action.doAction({
                    type: "ir.actions.act_window",
                    res_model: "concrete.delivery.ticket",
                    res_id: ticket.id,
                    views: [[false, "form"]],
                    view_mode: "form",
                    target: "current",
                });
            }
        } catch (error) {
            this.notification.add(error.message || "Error creating ticket", { type: "danger" });
        }
    }

    async openDelivery(deliveryId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "concrete.delivery.ticket",
            res_id: deliveryId,
            views: [[false, "form"]],
            view_mode: "form",
            target: "current",
        });
    }

    async createNewDelivery() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "concrete.delivery.ticket",
            views: [[false, "form"]],
            view_mode: "form",
            target: "current",
        });
    }

    async onSearch() {
        await this.loadDeliveries();
        await this.loadDeliveryOrders();
    }

    setActiveTab(tab) {
        this.state.activeTab = tab;
    }

    getStateLabel(state) {
        const labels = {
            draft: 'Draft',
            confirmed: 'Confirmed',
            in_transit: 'In Transit',
            delivered: 'Delivered',
            done: 'Done',
            assigned: 'Ready',
            waiting: 'Waiting'
        };
        return labels[state] || state;
    }

    async loadAnalytics() {
        try {
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            const todayStr = today.toISOString().split('T')[0] + ' 00:00:00';
            
            const completedToday = await this.orm.searchRead(
                "concrete.delivery.ticket",
                [["state", "=", "done"], ["delivery_date", ">=", todayStr]],
                ["volume_m3"],
                { limit: 500 }
            );
            
            const inProgress = await this.orm.searchRead(
                "concrete.delivery.ticket",
                [["state", "in", ["draft", "confirmed", "in_transit"]]],
                ["state"],
                { limit: 100 }
            );
            
            let totalVolume = 0;
            completedToday.forEach(d => {
                if (d.volume_m3) totalVolume += d.volume_m3;
            });
            
            const draftCount = inProgress.filter(d => d.state === 'draft').length;
            const confirmedCount = inProgress.filter(d => d.state === 'confirmed').length;
            const inTransitCount = inProgress.filter(d => d.state === 'in_transit').length;
            
            this.state.analytics = {
                completed_today: completedToday.length,
                in_progress: inProgress.length,
                avg_time: "15m",
                waiting_count: draftCount,
                total_volume_today: Math.round(totalVolume),
            };
            
            this.state.quickStats = {
                draft: draftCount,
                confirmed: confirmedCount,
                in_transit: inTransitCount,
            };
        } catch (error) {
            console.error("Error loading analytics:", error);
        }
    }

    async loadRecentActivity() {
        try {
            const recent = await this.orm.searchRead(
                "concrete.delivery.ticket",
                [],
                ["name", "vehicle_id", "state", "write_date", "volume_m3", "customer_id"],
                { limit: 8, order: "write_date desc" }
            );
            this.state.recentActivity = recent;
        } catch (error) {
            console.error("Error loading recent activity:", error);
        }
    }

    async refreshData() {
        try {
            await this.loadDeliveries();
            await this.loadDeliveryOrders();
            await this.loadFleetQueue();
            await this.loadAnalytics();
            await this.loadRecentActivity();
            this.state.lastRefresh = new Date();
        } catch (error) {
            console.error("Error refreshing data:", error);
        }
    }

    getActivityColor(state) {
        const colors = {
            draft: '#6c757d',
            confirmed: '#17a2b8',
            in_transit: '#ffc107',
            delivered: '#9b59b6',
            done: '#28a745'
        };
        return colors[state] || '#6c757d';
    }

    getActivityIcon(state) {
        const icons = {
            draft: 'fa-file',
            confirmed: 'fa-check',
            in_transit: 'fa-truck',
            delivered: 'fa-map-marker',
            done: 'fa-check-circle'
        };
        return icons[state] || 'fa-circle';
    }

    getActivityTime(writeDate) {
        const now = Date.now();
        const activityTime = new Date(writeDate + ' UTC').getTime();
        const diffMinutes = Math.floor((now - activityTime) / 60000);
        if (diffMinutes < 1) return 'Just now';
        if (diffMinutes < 60) return `${diffMinutes}m ago`;
        const hours = Math.floor(diffMinutes / 60);
        if (hours < 24) return `${hours}h ago`;
        return `${Math.floor(hours / 24)}d ago`;
    }

    getLastRefreshTime() {
        const now = new Date();
        const diff = Math.floor((now - this.state.lastRefresh) / 1000);
        if (diff < 60) return `${diff}s ago`;
        const mins = Math.floor(diff / 60);
        if (mins < 60) return `${mins}m ago`;
        const hours = Math.floor(mins / 60);
        return `${hours}h ago`;
    }

    async handleKeyPress(ev) {
        if (ev.target.tagName === 'INPUT') return;
        
        switch(ev.key) {
            case 'F1':
                ev.preventDefault();
                await this.createNewDelivery();
                break;
            case 'F2':
                ev.preventDefault();
                await this.refreshData();
                this.notification.add('Data refreshed', { type: 'success' });
                break;
        }
    }

    getWorkflowProgress(state) {
        const steps = { draft: 20, confirmed: 40, in_transit: 60, delivered: 80, done: 100 };
        return steps[state] || 0;
    }

    getWorkflowColor(state) {
        const colors = { draft: '#6c757d', confirmed: '#17a2b8', in_transit: '#ffc107', delivered: '#9b59b6', done: '#28a745' };
        return colors[state] || '#6c757d';
    }

    openDeliveryList(filter) {
        let domain = [];
        let name = "Deliveries";
        
        if (filter === "draft") {
            domain = [["state", "=", "draft"]];
            name = "Draft Deliveries";
        } else if (filter === "in_progress") {
            domain = [["state", "in", ["confirmed", "in_transit"]]];
            name = "In Progress Deliveries";
        } else if (filter === "done") {
            domain = [["state", "=", "done"]];
            name = "Completed Deliveries";
        }
        
        this.action.doAction({
            type: "ir.actions.act_window",
            name: name,
            res_model: "concrete.delivery.ticket",
            views: [[false, "list"], [false, "form"]],
            view_mode: "list,form",
            domain: domain,
            target: "current",
        });
    }

    getQueueColor(estimatedWait) {
        if (estimatedWait <= 30) return 'success';
        if (estimatedWait <= 45) return 'warning';
        return 'danger';
    }

    formatTime(minutes) {
        const h = Math.floor(minutes / 60);
        const m = minutes % 60;
        return h > 0 ? `${h}:${m.toString().padStart(2, '0')}` : `${m}m`;
    }

    isOverdue(scheduledDate) {
        if (!scheduledDate) return false;
        return new Date(scheduledDate) < new Date();
    }
}

ConcreteDeliveryCMDPInterface.template = "concrete_order_cmdp.CMDPInterface";

registry.category("actions").add("concrete_delivery_cmdp_interface", ConcreteDeliveryCMDPInterface);
