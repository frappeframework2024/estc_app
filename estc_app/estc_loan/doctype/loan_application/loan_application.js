// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Loan Application", {
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
