// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Loan", {
	refresh(frm) {

	},
	repayment_method: function(frm) {
		if(frm.doc.repayment_method == "Repay Fixed Amount per Period"){
			frm.set_value("interest_rate", 0);
			frm.set_value("repayment_period", 0);
		}
		else{
			frm.set_value("monthly_repayment", 0);
		}
	},
    applicant: function(frm) {
		if (frm.doc.applicant) {
			frappe.model.with_doc(frm.doc.applicant_type, frm.doc.applicant, function() {
				var applicant = frappe.get_doc(frm.doc.applicant_type, frm.doc.applicant);
				frm.set_value("applicant_name",applicant.employee_name || applicant.customer_name);
			});
		}
		else {
			frm.set_value("applicant_name", null);
		}
        frm.refresh_fields("applicant_name");
	}
});
