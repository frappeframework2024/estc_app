// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("OT Request", {
	onload(frm){
        if(frm.is_new()){
            frappe.call({
                "method": 'estc_app.estc_hr.doctype.employee.employee.get_current_employee',
                callback: function (r) {
                    frm.set_value('employee',r.message.employee.name)
                    current =new Date();
			        frm.set_value("posting_date", current);
                }
            });
            
            
        }
        
    },
});
