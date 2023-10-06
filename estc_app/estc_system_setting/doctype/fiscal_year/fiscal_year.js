// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Fiscal Year", {
	onload(frm) {
        frappe.call({
            method: "estc_app.estc_system_setting.doctype.fiscal_year.fiscal_year.get_annual_leave_setting",
            callback: function (r) {
                console.log(frm.doc)
            }
        })
       
            
        

	},
    refresh(frm){
        frm.add_custom_button(__('Update Employee Leave'), function(){
            frm.save().then((result) => {
                frappe.call({
                    method: "estc_app.estc_system_setting.doctype.fiscal_year.fiscal_year.update_employee_data",
                    "args": {
                        "fiscal_year_name": frm.doc.name
                    }
                })
            })
            
        });
    }
});
