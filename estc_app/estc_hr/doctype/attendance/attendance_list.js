frappe.listview_settings['Attendance'] = {
    hide_name_column: true,
    add_fields:['log_type'],
    formatters: {
        
        photo: function (value, field, doc) {
            return `<img src='${doc.photo || "/assets/estc_app/images/avatar-2.png"}' style='border-radius: 50%;height:35px; margin-right:10px;margin-left:5px'/>`;
        },
        status: function (value, field, doc) {
            if (doc.leave_request){
                let color = 'green'
                if(doc.status=="Absent"){
                    let color = 'red'
                    return `<span class="ellipsis" title="Status: Absent">
                                <span class="filterable indicator-pill ${color} ellipsis" data-filter="status,=,Present">
                                    <span class="ellipsis"> ${value} (${doc.log_type})</span>
                                </span>b
                            </span>`;
                }else{
                    color = 'blue'
                    return `<span class="ellipsis" title="Status: ${value}">
                                <span class="filterable indicator-pill ${color} ellipsis" data-filter="status,=,Present">
                                    <span class="ellipsis"> ${value} (${doc.log_type})</span>
                                </span>
                            </span>`;
                }
            }else{
                let color = 'green'
                if(doc.log_type=="IN"){
                    return `<span class="ellipsis" title="Status: Present">
                                <span class="filterable indicator-pill ${color} ellipsis" data-filter="status,=,Present">
                                    <span class="ellipsis"> ${value} (${doc.log_type})</span>
                                </span>
                            </span>`;
                }else{
                    color = 'blue'
                    return `<span class="ellipsis" title="Status: Present">
                                <span class="filterable indicator-pill ${color} ellipsis" data-filter="status,=,Present">
                                    <span class="ellipsis"> ${value} (${doc.log_type})</span>
                                </span>
                            </span>`;
                }
            }
        },

    }
}