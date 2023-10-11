frappe.listview_settings['Leave Request'] = {
    get_indicator: function(doc) {
		const status_colors = {
			"Draft": "yellow",
			"Submitted": "blue",
			"Write Off": "red",
		};
		return [__(doc.status), status_colors[doc.status], "status,=,"+doc.status];
	},
    formatters: {
        photo: function (value, field, doc) {
            return `<img src='${doc.photo || "/assets/estc_app/images/avatar-2.png"}' style='border-radius: 50%;height:35px; margin-right:10px;margin-left:5px'/>`;
        },
        

    },
}