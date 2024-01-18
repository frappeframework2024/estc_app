// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Leave Count Adjustment", {
	refresh(frm) {

	},
});

function getEmployeeLeaveCount(fiscal_year,leave_type){
    frappe.call({
        args: {
            "fiscal_year": fiscal_year,
            "leave_type": leave_type
        },
        method: "estc_app.estc_hr.doctype.leave_count_adjustment.leave_count_adjustment.get_leave_count",
        callback: function (r) {
            
        }
    })
}
