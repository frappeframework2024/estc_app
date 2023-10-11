frappe.listview_settings['Leave Request'] = {
    formatters: {
        photo: function (value, field, doc) {
            return `<img src='${value || "/assets/estc_app/images/avatar-2.png"}' style='border-radius: 50%;height:35px; margin-right:10px;margin-left:5px'/>`;
        },
		status: function (value, field, doc) {
            return `<img src='${doc.photo || "/assets/estc_app/images/avatar-2.png"}' style='border-radius: 50%;height:35px; margin-right:10px;margin-left:5px'/>`;
        },
		
    },
}
