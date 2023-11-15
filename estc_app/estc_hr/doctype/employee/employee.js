// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee", {
	refresh(frm) {
        frappe.call("estc_app.estc_hr.doctype.employee.employee.get_current_employee_leave_balance").then(r=>{
            console.log(r.message)
            frm.dashboard.add_indicator(__("Max Leave: "+r.message.max_leave) ,"red")
            frm.dashboard.add_indicator(__("Use Leave: "+r.message.use_leave) ,"green") 
            frm.dashboard.add_indicator(__("Balance: "+r.message.balance) ,"blue") 

    });
    frm.set_query("department", function () {
        return {
            "filters": {
                "is_group": 0,
            }
        };
    })
	},
});
