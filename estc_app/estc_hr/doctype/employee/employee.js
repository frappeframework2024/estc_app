// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee", {
	refresh(frm) {
        frappe.call("estc_app.estc_hr.doctype.employee.employee.get_current_employee_leave_balance").then(r=>{
            console.log(r.message)
            frm.dashboard.add_indicator(__("AL: "+r.message.max_leave) ,"red")
            frm.dashboard.add_indicator(__("Used: "+r.message.use_leave) ,"green") 
            frm.dashboard.add_indicator(__("Balance: "+r.message.balance) ,"blue") 

            frm.dashboard.add_indicator(__("Sick Leave: "+r.message.max_sick_leave) ,"red")
            frm.dashboard.add_indicator(__("Sick Leave Used: "+r.message.use_sick_leave) ,"green") 
            frm.dashboard.add_indicator(__("Sick Leave Balance: "+r.message.sick_leave_balance) ,"blue") 

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
