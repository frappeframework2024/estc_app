// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("HR Setting", {
	employee_background(frm) {
        frappe.call({
            "method": 'estc_app.estc_system_setting.doctype.hr_setting.hr_setting.update_image_to_employee',
            args: {
                "image":frm.doc.employee_background
            },
            callback: function (r) {
               
            }
        });
	},
});
