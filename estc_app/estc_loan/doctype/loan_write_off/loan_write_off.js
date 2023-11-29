// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Loan Write Off", {
	refresh(frm) {
        frm.page.btn_secondary.hide()
        frm.set_query("write_off_account", function(){
            return {
                "filters": [
                    ["Account", "is_group", "!=", "1"]
                ]
            }
        });
	},
    loan:function(frm){
            frappe.db.get_doc("Loan", frm.doc.loan).then(doc => {
            frm.set_value("applicant_type",doc.applicant_type);
            frm.set_value("applicant",doc.applicant);
            frm.set_value("applicant_name",doc.applicant_name);
            frm.set_value("loan_amount",doc.total_amount);
            frm.set_value("interest_amount",doc.total_interest);
            frm.set_value("paid_amount",doc.total_paid_amount);
            frm.set_value("balance",doc.total_amount - doc.total_paid_amount);
            frm.set_value("loan_account",doc.loan_account);
            frm.set_value("write_off_by", frappe.session.user_fullname);
        });	
    }
});
