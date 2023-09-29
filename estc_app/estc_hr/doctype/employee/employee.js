// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee", {
	refresh(frm) {
        let sum = frm.doc.leave_setting;
        frappe.call("estc_app.estc_hr.doctype.employee.employee.get_current_employee_leave_balance").then(r=>{
            r.message.max_leave = frm.dashboard.add_indicator(__("Max Leave: {0}",[sum.reduce((n, d) => n + d.max_leave,0)]) ,"red")
            r.message.use_leave = frm.dashboard.add_indicator(__("Use Leave: {0}",[sum.reduce((n, d) => n + d.use_leave,0)]) ,"green") 
            r.message.balance   = frm.dashboard.add_indicator(__("Balance: {0}",[sum.reduce((n, d) => n + d.balance,0)]) ,"blue") 
                
                
              })
	},
});
