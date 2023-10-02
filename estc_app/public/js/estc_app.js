window.addEventListener('load', function () {
 
    if (frappe.session.user != 'Administrator'){
        const getParent = document.querySelector('#page-Workspaces')
        if(getParent){ 
            const childElement = getParent.querySelector('.flex.col.page-actions.justify-content-end')
            childElement.style.display = 'none'
        }
    }

    const navBar = document.querySelector('body')
    navBar.classList.add('full-width');


    


    frappe.router.on('change', () => {
        if (frappe.session.user != 'Administrator'){
            const getParent = document.querySelector('#page-Workspaces')
            if(getParent){ 
                const childElement = getParent.querySelector('.flex.col.page-actions.justify-content-end')
                childElement.style.display = 'none'
            }
        }

        this.setTimeout(function(){
       
            let kanban = document.querySelector('[data-view="Kanban"]')
            let gantt = document.querySelector('[data-view="Gantt"]')
            if (kanban){
                kanban.remove()
            }
            if (gantt){
                gantt.remove()
            }
        },2000)

    
    })

})
 