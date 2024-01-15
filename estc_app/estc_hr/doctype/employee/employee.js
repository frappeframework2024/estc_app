// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee", {
	onload(frm) {
        if(!frm.is_new()){
            frappe.call({
                "method": 'estc_app.estc_hr.doctype.employee.employee.get_current_employee_leave_balance',
                args: {
                    "name": frm.doc.name,
                },
                callback: function (r) {
                    frm.dashboard.add_indicator(__("AL: "+(r.message.max_leave)) ,"red")
                    frm.dashboard.add_indicator(__("AL Used: "+(r.message.use_leave)) ,"green") 
                    frm.dashboard.add_indicator(__("AL Balance: "+(r.message.balance)) ,"blue") 
    
                    frm.dashboard.add_indicator(__("Sick Leave: "+(r.message.max_sick_leave | 0)) ,"red")
                    frm.dashboard.add_indicator(__("Sick Leave Used: "+(r.message.use_sick_leave | 0)) ,"green") 
                    frm.dashboard.add_indicator(__("Sick Leave Balance: "+(r.message.sick_leave_balance | 0)) ,"blue") 
    
                    frm.dashboard.add_indicator(__("OT: "+(r.message.ot_leave| 0)) ,"red")
                    frm.dashboard.add_indicator(__("OT Used: "+(r.message.ot_leave | 0)) ,"green") 
                    frm.dashboard.add_indicator(__("OT Balance: "+(r.message.ot_balance | 0)) ,"blue") 
                }
            });
        }
        
        
    frm.set_query("department", function () {
        return {
            "filters": {
                "is_group": 0,
            }
        };
    })
	},
});
