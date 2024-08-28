// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Fiscal Year", {
	onload(frm) {

	},
    refresh(frm){
        frm.add_custom_button(__('Update Employee Leave'), function(){
            
        frappe.call({
            method: "estc_app.estc_system_setting.doctype.fiscal_year.fiscal_year.update_employee_data",
            "args": {
                "fiscal_year_name": frm.doc.name
            },
            callback:(res)=>{

            }
        })
    
            
        },(__('Action')));
        frm.add_custom_button(__('Generate Employee Carry Over'), function(){
            frappe.call({
                method: "estc_app.estc_system_setting.doctype.fiscal_year.fiscal_year.generate_employee_carry_over",
                "args": {
                    "docname": frm.doc.name
                },
                callback: function (r) {
                    frappe.show_alert({
                        message: __("Generated success."),
                        indicator: "green",
                    });
                    frm.reload_doc()

                }
            })
        },(__('Action')));
    }
});
