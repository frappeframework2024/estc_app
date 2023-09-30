// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Loan Repayment", {
    loan: function(frm) {
        frappe.call({
            "method": "estc_app.estc_loan.doctype.loan_repayment.loan_repayment.get_loan_amount_to_day",
            "args": {
                "loan": frm.doc.loan,
                "posting_date":frm.doc.posting_date
            },
            callback: function(r) {
                if(r.message != undefined){
                    console.log(r.message.total_amount);
                }
            }
        });
	}
});
