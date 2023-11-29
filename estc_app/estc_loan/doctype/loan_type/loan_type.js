// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Loan Type", {
	onload:function(frm) {
        frm.set_query("disbursement_account", function(){
            return {
                "filters": [
                    ["Account", "is_group", "!=", "1"]
                ]
            }
        });
        frm.set_query("payment_account", function(){
            return {
                "filters": [
                    ["Account", "is_group", "!=", "1"]
                ]
            }
        });
        frm.set_query("loan_account", function(){
            return {
                "filters": [
                    ["Account", "is_group", "!=", "1"]
                ]
            }
        });
	},
    payment_account(frm) {

	},
});
