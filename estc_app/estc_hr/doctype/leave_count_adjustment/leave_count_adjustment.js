// Copyright (c) 2024, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Leave Count Adjustment", {
	refresh(frm) {
        frm.set_query('leave_type', (doc, cdt, cdn) => {
			
			return {
				filters: {
					"is_group": 0,
				}
			};
		});
	},
     leave_type(frm,cdt, cdn){
        if(frm.doc.fiscal_year && frm.doc.leave_type && frm.doc.default_leave_count){
            console.log(frm.doc.leave_count)
            getEmployeeLeaveCount(frm.doc.fiscal_year,frm.doc.leave_type,frm.doc.default_leave_count).then((data)=>{
                if (frm.doc.leave_count){
                    frm.clear_table('leave_count');
                }
                data.forEach((row)=>{
                    let entry = frm.add_child("leave_count");
                    entry.employee = row.name
                    entry.employee_name = row.employee_name
                    entry.leave_count_reference = row.leave_count_ref
                    entry.balance = row.max_leave - row.use_leave
                    entry.max_leave = row.max_leave
                    entry.used = row.use_leave
                    frm.refresh_field("leave_count");
                })
            })
            
        } 
    },
     fiscal_year(frm,cdt, cdn){
        if(frm.doc.fiscal_year && frm.doc.leave_type && frm.doc.default_leave_count){
            if (frm.doc.leave_count){
                frm.clear_table('leave_count');
            }
            getEmployeeLeaveCount(frm.doc.fiscal_year,frm.doc.leave_type,frm.doc.default_leave_count).then((data)=>{
                data.forEach((row)=>{
                    let entry = frm.add_child("leave_count");
                    entry.employee = row.name
                    entry.employee_name = row.employee_name
                    entry.leave_count_reference = row.leave_count_ref
                    entry.balance = row.max_leave - row.use_leave
                    entry.max_leave = row.max_leave
                    entry.used = row.use_leave || 0
                    frm.refresh_field("leave_count");
                })
            })
            
        }
        
    },
     default_leave_count(frm,cdt, cdn){
        if(frm.doc.fiscal_year && frm.doc.leave_type && frm.doc.default_leave_count){
            if (frm.doc.leave_count){
                frm.clear_table('leave_count');
            }
            getEmployeeLeaveCount(frm.doc.fiscal_year,frm.doc.leave_type,frm.doc.default_leave_count).then((data)=>{
                data.forEach((row)=>{
                    let entry = frm.add_child("leave_count");
                    entry.employee = row.name
                    entry.employee_name = row.employee_name
                    entry.leave_count_reference = row.leave_count_ref
                    entry.balance = row.max_leave - row.use_leave
                    entry.max_leave = row.max_leave
                    entry.used = row.use_leave || 0
                    frm.refresh_field("leave_count");
                })
            })
            
        }
        
    }
});

frappe.ui.form.on('Employee Leave Count Adjustment', {
    max_leave(frm,cdt, cdn){
        let doc=   locals[cdt][cdn];
        doc.balance = doc.max_leave - doc.used
        frm.refresh_field('leave_count');
    },
    used(frm,cdt, cdn){
        let doc=   locals[cdt][cdn];
        doc.balance = doc.max_leave - doc.used
        frm.refresh_field('leave_count');
    }

})

 function getEmployeeLeaveCount(fiscal_year,leave_type,default_count){
    return new Promise((resolve, reject) => {
        frappe.call({
            args: {
                "fiscal_year": fiscal_year,
                "leave_type": leave_type,
                "default_count": default_count,
            },
            method: "estc_app.estc_hr.doctype.leave_count_adjustment.leave_count_adjustment.get_employee_leave_count",
            callback: function (r) {
                resolve(r.message);
            },
           
        });
    });
}
