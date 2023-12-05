frappe.listview_settings['Attendance'] = {
    hide_name_column: true,
    add_fields:['log_type','late','leave_early'],
    formatters: {
        
        photo: function (value, field, doc) {
            
            return `<img src='${doc.photo || "/assets/estc_app/images/avatar-2.png"}' style='border-radius: 50%;height:35px; margin-right:10px;margin-left:5px'/>`;
        },
        attendance_date: function (value, field, doc){
            if(doc.late && doc.status == "Present"){
                return `
                    ${frappe.datetime.str_to_user(value)}
                    <div class="ellipsis">
                        <span class="filterable indicator-pill blue ellipsis" style="height:20px" data-filter="status,=,Present">
                            <span class="ellipsis" style="font-size: 10px;">Late :${doc.late}</span>
                        </span>
                    </div>
            `
            }else if(doc.leave_early && doc.status == "Present"){
                return `
                    ${frappe.datetime.str_to_user(value)}
                    <div class="ellipsis">
                        <span class="filterable indicator-pill red ellipsis" style="height:20px" data-filter="status,=,Present">
                            <span class="ellipsis" style="font-size: 10px;">Early :${doc.leave_early}</span>
                        </span>
                    </div>
            `
            }else {
                return frappe.datetime.str_to_user(value)
            
            }
            
        },
        status: function (value, field, doc) {
            let color = 'green'
                if(doc.status=="Absent"){
                    let color = 'red'
                    return `<span class="ellipsis" title="Status: ${value}">
                                <span class="filterable indicator-pill ${color} ellipsis" data-filter="status,=,Present">
                                    <span class="ellipsis"> ${value}</span>
                                </span>
                            </span>`;
                }
                if(doc.status=="Present"){
                    if (doc.log_type == "OUT"){
                        color = 'orange'
                    }else{
                        color = 'green'
                    }
                    
                    return `<span class="ellipsis" title="Status: ${value}">
                                <span class="filterable indicator-pill ${color} ellipsis" data-filter="status,=,Present">
                                    <span class="ellipsis"> ${value}  (${doc.log_type})</span>
                                </span>
                            </span>`;
                }
                if(doc.leave_request){
                    color = 'green'
                    return `<span class="ellipsis" title="Status: ${value}">
                                <span class="filterable indicator-pill ${color} ellipsis" data-filter="status,=,Present">
                                    <span class="ellipsis"> ${value}</span>
                                </span>
                            </span>`;
                }
                
           
        },

    }
}