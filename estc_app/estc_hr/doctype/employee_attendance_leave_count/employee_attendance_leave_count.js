// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Attendance Leave Count", {
    refresh(frm) {
        frm.set_query('leave_type', (doc, cdt, cdn) => {
            
            return {
                filters: {
                    "is_group": 0,
                }
            };
        });
    },
});