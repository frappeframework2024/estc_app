// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("OT Request", {

	onload(frm){
        renderTemplate(frm);
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
    refresh(frm){
        renderTemplate(frm);
    },
    after_save(frm){
        frm.refresh();
        // renderTemplate(frm)
    }

});

function renderTemplate(frm) {
        const html = frappe.render_template("ot_work_times", {doc:frm.doc,is_new:frm.is_new()})
        $(frm.fields_dict['ot_work_times'].wrapper).html(html);
        frm.refresh_field('ot_work_times');
    
	
}
