// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Loan", {
	
	refresh: function(frm) {
		if (frm.doc.docstatus == 1 && frm.doc.disbursed_amount<frm.doc.loan_amount) {
			frm.add_custom_button(__('Loan Disbursement'), function() {
				frm.trigger("make_loan_disbursement");
			},__('Create'));
		}
		if (frm.doc.docstatus == 1 && frm.doc.disbursed_amount == frm.doc.loan_amount) {
			frm.add_custom_button(__('Loan Repayment'), function() {
				frm.trigger("make_loan_disbursement");
			},__('Create'));
		}
	},
	onload: function (frm) {
		frm.set_query("loan_application", function () {
			return {
				"filters": {
					"applicant": frm.doc.applicant,
					"docstatus": 1,
					"status": "Approved"
				}
			};
		})
	},
	make_loan_disbursement: function (frm) {
		frappe.call({
			args: {
				"loan": frm.doc.name,
				"applicant_type": frm.doc.applicant_type,
				"applicant": frm.doc.applicant_name,
				"pending_amount": frm.doc.loan_amount - frm.doc.disbursed_amount > 0 ? frm.doc.loan_amount - frm.doc.disbursed_amount : 0,
				"as_dict": 1
			},
			method: "estc_app.estc_loan.doctype.loan.loan.make_loan_disbursement",
			callback: function (r) {
				if (r.message)
					var doc = frappe.model.sync(r.message)[0];
				frappe.set_route("Form", doc.doctype, doc.name);
			}
		})
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
	},
	loan_application: function(frm) {
		if (frm.doc.loan_application) {
			frappe.db.get_doc("Loan Application", frm.doc.loan_application).then(doc => {
				frm.set_value("applicant_type",doc.applicant_type);
				frm.set_value("applicant",doc.applicant);
				frm.set_value("loan_type",doc.loan_type);
				frm.set_value("interest_rate",doc.interest_rate);
				frm.set_value("loan_amount",doc.loan_amount);
			});	
		}   
	},
	loan_type: function(frm) {
		if (frm.doc.loan_type) {
			frappe.db.get_doc("Loan Type", frm.doc.loan_type).then(doc => {
				frm.set_value("interest_rate",doc.interest_rate);
			});	
		}   
	}
});
