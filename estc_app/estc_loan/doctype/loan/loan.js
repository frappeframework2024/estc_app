// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Loan", {
	
	refresh: function(frm) {
		frm.page.btn_secondary.show();
		if (frm.doc.status == 'Submitted' && frm.doc.docstatus == 1) {
			if(frm.doc.disbursed_amount<frm.doc.loan_amount && frm.doc.is_secured_loan == 0){
				frm.add_custom_button(__('Loan Disbursement'), function() {
					frm.trigger("make_loan_disbursement");
				});
			}
			if (frm.doc.disbursed_amount<frm.doc.loan_amount && frm.doc.is_secured_loan == 1 && frm.doc.security_pledge == 1){
				frm.add_custom_button(__('Loan Disbursement'), function() {
					frm.trigger("make_loan_disbursement");
				});
			}
			if(frm.doc.is_secured_loan == 1 && frm.doc.security_pledge == 0){
				frm.add_custom_button(__('Loan Security Pledge'), function() {
					frm.trigger("make_loan_security_pledge");
				});
			}
			if(frm.doc.disbursed_amount == frm.doc.loan_amount && frm.doc.status != "Write Off"){
				frm.add_custom_button(__('Mark As Write Off'), function() {
					frm.trigger("mark_as_write_off");
				});
			}
			if(frm.doc.disbursed_amount == frm.doc.loan_amount && frm.doc.status != "Write Off"){
				frm.add_custom_button(__('Loan Repayment'), function() {
					frm.trigger("make_loan_repayment");
				});
			}
		}
		if (frm.doc.status == "Write Off") {
			frm.add_custom_button(__('Show Write Off Detail'), function() {
				frm.trigger("show_write_off_detail");
			});
			frm.page.btn_secondary.hide()
			var a = document.getElementsByClassName('row form-dashboard-section form-links')
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
	make_loan_security_pledge: function (frm) {
		frappe.call({
			args: {
				"loan": frm.doc.name,
				"applicant_type": frm.doc.applicant_type,
				"applicant": frm.doc.applicant,
				"applicant_name": frm.doc.applicant_name
			},
			method: "estc_app.estc_loan.doctype.loan.loan.make_loan_security_pledge",
			callback: function (r) {
				if (r.message)
					var doc = frappe.model.sync(r.message)[0];
				frappe.set_route("Form", doc.doctype, doc.name);
			}
		})
	},
	make_loan_disbursement: function (frm) {
		frappe.call({
			args: {
				"loan": frm.doc.name,
				"applicant_type": frm.doc.applicant_type,
				"applicant": frm.doc.applicant,
				"loan_account": frm.doc.loan_account,
				"disbursed_account": frm.doc.disbursement_account,
				"pending_amount": frm.doc.loan_amount - frm.doc.disbursed_amount > 0 ? frm.doc.loan_amount - frm.doc.disbursed_amount : 0
			},
			method: "estc_app.estc_loan.doctype.loan.loan.make_loan_disbursement",
			callback: function (r) {
				if (r.message)
					var doc = frappe.model.sync(r.message)[0];
				frappe.set_route("Form", doc.doctype, doc.name);
			}
		})
	},
	make_loan_repayment: function (frm) {
		frappe.call({
			args: {
				"loan": frm.doc.name,
				"applicant_type": frm.doc.applicant_type,
				"applicant": frm.doc.applicant,
				"applicant_name": frm.doc.applicant_name
			},
			method: "estc_app.estc_loan.doctype.loan.loan.make_loan_repayment",
			callback: function (r) {
				if (r.message)
					var doc = frappe.model.sync(r.message)[0];
				frappe.set_route("Form", doc.doctype, doc.name);
			}
		})
	},
	mark_as_write_off: function (frm) {
		frappe.call({
			args: {
				"loan": frm.doc.name,
				"applicant_type": frm.doc.applicant_type,
				"applicant": frm.doc.applicant,
				"applicant_name": frm.doc.applicant_name,
				"total_amount": frm.doc.total_amount,
				"interest_amount": frm.doc.total_interest,
				"paid_amount": frm.doc.total_paid_amount,
				"loan_account": frm.doc.loan_account

			},
			method: "estc_app.estc_loan.doctype.loan.loan.mark_as_write_off",
			callback: function (r) {
				if (r.message)
					var doc = frappe.model.sync(r.message)[0];
					frappe.set_route("Form", doc.doctype, doc.name);
			}
		})
	},
	show_write_off_detail: function (frm) {
		frappe.call({
			args: {
				"loan": frm.doc.name
			},
			method: "estc_app.estc_loan.doctype.loan.loan.show_write_off_detail",
			callback: function (r) {
				if (r.message)
					frappe.set_route("Form", "Loan Write Off", r.message);
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
