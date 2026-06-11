document.addEventListener('DOMContentLoaded', function() {
    
    const btnAgregar = document.getElementById('btnAgregarCarrito');
    
    if (btnAgregar) {
        btnAgregar.addEventListener('click', function(e) {
            e.preventDefault();
            
            const productoId = this.getAttribute('data-producto-id');
            
            // Función para obtener el token CSRF de las cookies
            function getCsrfToken() {
                const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
                return cookie ? cookie.split('=')[1] : '';
            }
            
            fetch(`/carrito/agregar/${productoId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Mostrar toast
                    mostrarToast(data.message, 'success');
                    
                    // Actualizar contador del navbar
                    actualizarContadorCarrito(data.total_items);
                } else {
                    mostrarToast(data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarToast('❌ Error al agregar producto', 'error');
            });
        });
    }
    
    // Función para mostrar el toast
    function mostrarToast(mensaje, tipo) {
        let toast = document.getElementById('toastMensaje');
        
        if (!toast) {
            // Crear el toast si no existe
            toast = document.createElement('div');
            toast.id = 'toastMensaje';
            toast.className = 'toast-custom';
            document.body.appendChild(toast);
        }
        
        toast.textContent = tipo === 'success' ? `✅ ${mensaje}` : `❌ ${mensaje}`;
        toast.style.display = 'block';
        toast.style.opacity = '1';
        
        // Ocultar después de 3 segundos
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                toast.style.display = 'none';
            }, 300);
        }, 3000);
    }
    
    // Función para actualizar el contador del carrito en el navbar
    function actualizarContadorCarrito(total) {
        const contadorCarrito = document.querySelector('.badge.bg-danger.rounded-pill');
        const carritoLink = document.querySelector('a[href*="ver_carrito"]');
        
        if (total > 0) {
            if (contadorCarrito) {
                contadorCarrito.textContent = total;
            } else if (carritoLink) {
                const badge = document.createElement('span');
                badge.className = 'badge bg-danger rounded-pill ms-1';
                badge.textContent = total;
                carritoLink.appendChild(badge);
            }
        } else if (contadorCarrito) {
            contadorCarrito.remove();
        }
    }
});