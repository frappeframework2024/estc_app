frappe.listview_settings['Attendance'] = {
    hide_name_column: true,
    add_fields:['late','leave_early','checkin_time','checkout_time'],
    get_indicator(doc) {
        if (doc.status == "Present")
            return  [`<span style="font-size: 12px;background-color:#17ab07; color:white; padding: 2px 10px;border-radius: 10px;">${__(doc.status)}</span>`]; 
        if (doc.status.includes("Absent"))
            return  [`<span style="font-size: 12px;background-color:#f74931; color:white; padding: 2px 10px;border-radius: 10px;">${__(doc.status)}</span>`]; 
        if (doc.status.includes("On Leave"))
            return  [`<span style="font-size: 12px;background-color:#108dc7; color:white; padding: 2px 10px;border-radius: 10px;">${__(doc.status)}</span>`]; 
    },
    formatters: {
        
        photo: function (value, field, doc) {
            
            return `<img src='${doc.photo || "/assets/estc_app/images/avatar-2.png"}' style='border-radius: 50%;height:35px; margin-right:10px;margin-left:5px'/>`;
        },
        checkin_time: function (value, field, doc){
            if(doc.status == "Present" && Number(doc.late || 0) > 0){
                return `
                    ${frappe.datetime.str_to_user(value)}
                    <div class="ellipsis">
                        <span class="filterable indicator-pill blue ellipsis" style="height:20px" data-filter="status,=,Present">
                            <span class="ellipsis" style="font-size: 10px;">Late :${secondsToHms(doc.late)}</span>
                        </span>
                    </div>
            `
            }else{
                return frappe.datetime.str_to_user(value)
            }
            
        },
        checkout_time: function (value, field, doc){
            if(doc.status == "Present" && Number(doc.leave_early || 0) > 0){
                return `
                    ${frappe.datetime.str_to_user(value)}
                    <div class="ellipsis">
                        <span class="filterable indicator-pill orange ellipsis" style="height:20px" data-filter="status,=,Present">
                            <span class="ellipsis" style="font-size: 10px;">Early:${secondsToHms(doc.leave_early)}</span>
                        </span>
                    </div>
            `
            }else{
                return frappe.datetime.str_to_user(value)
            }
            
        },
        status: function (value, field, doc) {
            let color = 'green'
                if(doc.status=="Absent"){
                    let color = 'red'
                    return `<span class="ellipsis" title="Status: ${value}">
                                <span class="filterable indicator-pill ${color} ellipsis" data-filter="status,=,Absent">
                                    <span class="ellipsis"> ${value}</span>
                                </span>
                            </span>`;
                }
                if(doc.status=="Present"){
                    
                    return `<span class="ellipsis" title="Status: ${value}">
                                <span class="filterable indicator-pill ${color} ellipsis" data-filter="status,=,Present">
                                    <span class="ellipsis"> ${value}</span>
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
            color = 'green'
            return `<span class="ellipsis" title="Status: ${value}">
                        <span class="filterable indicator-pill ${color} ellipsis" data-filter="status,=,Present">
                            <span class="ellipsis"> ${value}</span>
                        </span>
                    </span>`;
           
        },

    }
}

function secondsToHms(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;

    const formattedHours = hours < 10 ? `0${hours}` : hours;
    const formattedMinutes = minutes < 10 ? `0${minutes}` : minutes;
    const formattedSeconds = remainingSeconds < 10 ? `0${remainingSeconds}` : remainingSeconds;
    return `${formattedHours}:${formattedMinutes}:${formattedSeconds}`;
}