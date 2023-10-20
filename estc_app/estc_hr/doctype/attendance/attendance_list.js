frappe.listview_settings['Attendance'] = {
    hide_name_column: true,
    formatters: {
        photo: function (value, field, doc) {
            return `<img src='${doc.photo || "/assets/estc_app/images/avatar-2.png"}' style='border-radius: 50%;height:35px; margin-right:10px;margin-left:5px'/>`;
        },
        status: function (value, field, doc) {
            color = 'green'
            if( value == 'Absent') color = 'red'
            return `<span class="ellipsis" title="Status: Present">
                <span class="filterable indicator-pill ${color} ellipsis" data-filter="status,=,Present">
                    <span class="ellipsis"> ${value}</span>
                </span>
            </span>`;
        },

    }
}