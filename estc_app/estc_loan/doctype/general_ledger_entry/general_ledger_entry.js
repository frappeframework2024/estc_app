// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("General Ledger Entry", {
	refresh: function(frm) {
		frm.page.btn_primary.hide()
	}
});
