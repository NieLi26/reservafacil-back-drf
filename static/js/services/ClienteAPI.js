async function getCliente(rut) {
    const url = `/api/v1/booking/cliente/json/${rut}/`
    
    try {
        const resp = await fetch(url)
        if ( !resp.ok ) {
            if (resp.status === 404) {
                const result = await resp.json();
                return result
            }
            
            throw new Error('Error HTTP: ' + resp.status);
        }
        const result = await resp.json()
        return result
    } catch (error) {
        console.error(error);
        Toastify({
            text: error,
            duration: 3000,
            newWindow: true,
            close: true,
            gravity: "top", // `top` or `bottom`
            position: "right", // `left`, `center` or `right`
            stopOnFocus: true, // Prevents dismissing of toast on hover
            style: {
                background: "#E52B50",
            },
            onClick: function(){} // Callback after click
        }).showToast();
    }
}

async function getClientes(params = {}) {
    console.log(params);
    let url = `/api/v1/booking/cliente/json/?`

    const urlQuery = Object.entries(params)
        .map(([key, value]) => `${key}=${value}`)
        .join('&');
    url += urlQuery;

    try {
        const resp = await fetch(url)
        if ( !resp.ok ) {
            throw new Error('Error HTTP: ' + resp.status);
        }
        const result = await resp.json()
        return result
    } catch (error) {
        console.error(error);
        Toastify({
            text: error,
            duration: 3000,
            newWindow: true,
            close: true,
            gravity: "top", // `top` or `bottom`
            position: "right", // `left`, `center` or `right`
            stopOnFocus: true, // Prevents dismissing of toast on hover
            style: {
                background: "#E52B50",
            },
            onClick: function(){} // Callback after click
        }).showToast();
    }
}

async function createCliente(data) {
    const url = `/api/v1/booking/cliente/json/`
    const formData = new FormData();
    for (let [key, value] of Object.entries(data) ) {
        formData.append(key, value);
    }

    const options = {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin',                
        body: formData
    }

    try {
        const resp = await fetch(url, options)
        if ( !resp.ok ) {
            if (resp.status === 422) {
                const result = await resp.json();
                return result
            }
            throw new Error('Error HTTP: ' + resp.status);
        }
        const result = await resp.json()
        return result
    } catch (error) {
        console.error(error);
        Toastify({
            text: error,
            duration: 3000,
            newWindow: true,
            close: true,
            gravity: "top", // `top` or `bottom`
            position: "right", // `left`, `center` or `right`
            stopOnFocus: true, // Prevents dismissing of toast on hover
            style: {
                background: "#E52B50",
            },
            onClick: function(){} // Callback after click
        }).showToast();
    }
}

// sin formData porque peticion PUT
async function updateCliente(rut, data) {
    const url = `/api/v1/booking/cliente/json/${rut}/`
    // const formData = new FormData(data);
    const options = {
        method: 'PUT',
        headers: {'X-CSRFToken': csrftoken, 
                    'content-type': 'application/json'},
        mode: 'same-origin',
        body: JSON.stringify(data)
    }
    
    try {
        const resp = await fetch(url, options)
        if ( !resp.ok ) {
            if (resp.status === 403) {
                const result = await resp.json();
                return result
            }

            if (resp.status === 404) {
                const result = await resp.json();
                return result
            }

            if (resp.status === 422) {
                const result = await resp.json();
                return result
            }

            throw new Error('Error HTTP: ' + resp.status);
        }
        const result = await resp.json()
        return result
    } catch (error) {
        console.error(error);
        Toastify({
            text: error,
            duration: 3000,
            newWindow: true,
            close: true,
            gravity: "top", // `top` or `bottom`
            position: "right", // `left`, `center` or `right`
            stopOnFocus: true, // Prevents dismissing of toast on hover
            style: {
                background: "#E52B50",
            },
            onClick: function(){} // Callback after click
        }).showToast();
    }
}

// sin formData porque peticion DELETE
async function deleteCliente(rut) {
    const url = `/api/v1/booking/cliente/json/${rut}/`
    const options = {
        method: 'DELETE',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin',
    }

    try {
        const resp = await fetch(url, options)
        if ( !resp.ok ) {
            if (resp.status === 403) {
                const result = await resp.json();
                return result
            }
            
            if (resp.status === 404) {
                const result = await resp.json();
                return result
            }
            throw new Error('Error HTTP: ' + resp.status);
        } 

        return {
            'success': 'Cliente Eliminado Correctamente'
        }
    } catch (error) {
        console.error(error);
        Toastify({
            text: error,
            duration: 3000,
            newWindow: true,
            close: true,
            gravity: "top", // `top` or `bottom`
            position: "right", // `left`, `center` or `right`
            stopOnFocus: true, // Prevents dismissing of toast on hover
            style: {
                background: "#E52B50",
            },
            onClick: function(){} // Callback after click
        }).showToast();
    }
}