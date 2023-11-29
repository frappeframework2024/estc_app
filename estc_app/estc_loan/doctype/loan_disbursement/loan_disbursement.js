// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Loan Disbursement", {
    loan: function(frm) {
        frappe.call({
            "method": "estc_app.estc_loan.doctype.loan_disbursement.loan_disbursement.get_loan_maount",
            "args": {
                "loan": frm.doc.loan
            },
            callback: function(r) {
                if(r.message != undefined){
                    frm.set_value("disbursed_amount", r.message);
                }
            }
        });
	},
});
