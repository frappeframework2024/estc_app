frappe.listview_settings['Leave Status'] = {
    formatters: {
        color: function (value, field, doc) {
            return `<div style="background:${value};width: 35px;height:35px;border-radius: 50%;"></div>`;
        },
        

    },
}
