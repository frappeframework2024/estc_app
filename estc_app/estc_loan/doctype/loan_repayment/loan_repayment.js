// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Loan Repayment", {
    refresh:function(frm){
        if(frm.doc.loan != null && frm.doc.total_amount == 0 && frm.is_new){
            frappe.call({
                "method": "estc_app.estc_loan.doctype.loan_repayment.loan_repayment.get_loan_amount_to_day",
                "args": {
                    "loan": frm.doc.loan,
                    "posting_date":frm.doc.posting_date
                },
                callback: function(r) {
                    if(r.message != undefined){
                        frm.set_value("payment_date", r.message.max_payment_date);
                        frm.set_value("total_amount", r.message.total_payment);
                        frm.set_value("payment_amount", frm.doc.total_amount + frm.doc.penalty_amount - frm.doc.write_off_amount);
                    }
                }
            })
        }
    },
    loan: function(frm) {
        frappe.call({
            "method": "estc_app.estc_loan.doctype.loan_repayment.loan_repayment.get_loan_amount_to_day",
            "args": {
                "loan": frm.doc.loan,
                "posting_date":frm.doc.posting_date
            },
            callback: function(r) {
                if(r.message != undefined){
                    frm.set_value("payment_date", r.message.max_payment_date);
                    frm.set_value("total_amount", r.message.total_payment);
                    frm.set_value("payment_amount", frm.doc.total_amount + frm.doc.penalty_amount - frm.doc.write_off_amount);
                }
            }
        });
	},
    posting_date: function(frm) {
        frappe.call({
            "method": "estc_app.estc_loan.doctype.loan_repayment.loan_repayment.get_loan_amount_to_day",
            "args": {
                "loan": frm.doc.loan,
                "posting_date":frm.doc.posting_date ?? Date.now()
            },
            callback: function(r) {
                if(r.message != undefined){
                    frm.set_value("payment_date", r.message.max_payment_date);
                    frm.set_value("total_amount", r.message.total_payment);
                    frm.set_value("payment_amount",  frm.doc.total_amount + frm.doc.penalty_amount - frm.doc.write_off_amount);
                }
            }
        });
	},
    penalty_amount:function(frm){
        frm.set_value("payment_amount",  frm.doc.total_amount + frm.doc.penalty_amount - frm.doc.write_off_amount);
    },
    write_off_amount:function(frm){
        frm.set_value("payment_amount",  frm.doc.total_amount + frm.doc.penalty_amount - frm.doc.write_off_amount);
    }
});
