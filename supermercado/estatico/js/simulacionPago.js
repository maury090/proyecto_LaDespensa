// simulacionPago.js

document.addEventListener('DOMContentLoaded', function() {
    
    // ========== 1. ACTUALIZAR MÉTODO DE ENTREGA ==========
    const radios = document.querySelectorAll('input[name="metodoEntrega"]');
    const inputHidden = document.getElementById('metodoEntregaInput');
    
    if (radios.length > 0 && inputHidden) {
        radios.forEach(radio => {
            radio.addEventListener('change', function() {
                inputHidden.value = this.value;
            });
        });
    }
    
    // ========== 2. CONFIRMAR PEDIDO (Validación adicional) ==========
    const formConfirmar = document.querySelector('form[action*="confirmar-pedido"]');
    
    if (formConfirmar) {
        formConfirmar.addEventListener('submit', function(e) {
            // Verificar si el carrito está vacío (por si acaso)
            const totalElement = document.querySelector('.total-carrito');
            if (totalElement && totalElement.textContent.trim() === '$0') {
                e.preventDefault();
                mostrarMensaje('❌ Tu carrito está vacío. Agrega productos antes de continuar.', 'error');
                return false;
            }
            
            // Mostrar mensaje de procesamiento
            mostrarMensaje('⏳ Procesando tu pedido...', 'info');
        });
    }
    
    // ========== 3. FUNCIÓN PARA MOSTRAR MENSAJES FLOTANTES ==========
    function mostrarMensaje(mensaje, tipo) {
        // Eliminar mensaje anterior
        const msgAnterior = document.querySelector('.alert-flotante');
        if (msgAnterior) {
            msgAnterior.remove();
        }
        
        // Crear nuevo mensaje
        const div = document.createElement('div');
        div.className = `alert-flotante alert alert-${tipo === 'success' ? 'success' : tipo === 'error' ? 'danger' : 'info'}`;
        div.style.position = 'fixed';
        div.style.top = '80px';
        div.style.left = '50%';
        div.style.transform = 'translateX(-50%)';
        div.style.zIndex = '9999';
        div.style.minWidth = '300px';
        div.style.textAlign = 'center';
        div.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        div.style.borderRadius = '8px';
        div.innerHTML = `
            <strong>${tipo === 'success' ? '✅' : tipo === 'error' ? '❌' : '⏳'}</strong> ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%);"></button>
        `;
        
        document.body.appendChild(div);
        
        // Auto cerrar después de 4 segundos
        setTimeout(() => {
            if (div) {
                div.classList.remove('show');
                setTimeout(() => div.remove(), 300);
            }
        }, 4000);
    }
});