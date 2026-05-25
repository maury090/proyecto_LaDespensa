// Esperamos a que el DOM esté cargado
document.addEventListener('DOMContentLoaded', function() {
    
    const formulario = document.getElementById('registroForm');

    // ========== FUNCIÓN PARA VALIDAR RUT CHILENO ==========
    function validarRut(rutCompleto) {
        // Limpiar el RUT: eliminar puntos, guiones y espacios
        let rutLimpio = rutCompleto.replace(/\./g, '').replace(/-/g, '').replace(/\s/g, '');
        
        // Verificar formato básico (solo números y posible K al final)
        if (!/^[0-9]+[0-9kK]{1}$/.test(rutLimpio)) return false;
        
        // Separar cuerpo y dígito verificador
        let cuerpo = rutLimpio.slice(0, -1);
        let dvIngresado = rutLimpio.slice(-1).toUpperCase();
        
        // Calcular dígito verificador esperado (algoritmo módulo 11)
        let suma = 0;
        let multiplicador = 2;
        
        // Recorrer el cuerpo de derecha a izquierda
        for (let i = cuerpo.length - 1; i >= 0; i--) {
            suma += parseInt(cuerpo.charAt(i)) * multiplicador;
            multiplicador++;
            if (multiplicador === 8) {
                multiplicador = 2;
            }
        }
        
        let resto = suma % 11;
        let dvEsperado = 11 - resto;
        
        // Convertir según las reglas del RUT chileno
        if (dvEsperado === 11) {
            dvEsperado = '0';
        } else if (dvEsperado === 10) {
            dvEsperado = 'K';
        } else {
            dvEsperado = dvEsperado.toString();
        }
        
        // Comparar dígito ingresado con el esperado
        return dvIngresado === dvEsperado;
    }

    // ========== FUNCIÓN PARA MOSTRAR MENSAJES FLOTANTES ==========
    function mostrarMensaje(mensaje, tipo) {
        // Eliminar mensaje anterior si existe
        const msgAnterior = document.querySelector('.alert-flotante');
        if (msgAnterior) {
            msgAnterior.remove();
        }
        
        // Crear nuevo mensaje
        const div = document.createElement('div');
        div.className = `alert-flotante alert alert-${tipo === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
        div.style.position = 'fixed';
        div.style.top = '80px';
        div.style.left = '50%';
        div.style.transform = 'translateX(-50%)';
        div.style.zIndex = '9999';
        div.style.minWidth = '300px';
        div.style.maxWidth = '500px';
        div.style.textAlign = 'center';
        div.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        div.style.borderRadius = '8px';
        div.innerHTML = `
            <strong>${tipo === 'success' ? '✅' : '❌'}</strong> ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%);"></button>
        `;
        
        document.body.appendChild(div);
        
        // Auto cerrar después de 5 segundos
        setTimeout(() => {
            if (div) {
                div.classList.remove('show');
                setTimeout(() => div.remove(), 300);
            }
        }, 5000);
    }

    // ========== FUNCIÓN PARA LIMPIAR ERRORES PREVIOS ==========
    function limpiarErrores() {
        const errores = document.querySelectorAll('.error-msg');
        errores.forEach(error => error.textContent = '');
        
        const inputs = document.querySelectorAll('.form-control');
        inputs.forEach(input => {
            input.classList.remove('is-invalid', 'is-valid');
        });
    }

    // ========== FUNCIÓN PARA MARCAR CAMPO COMO INVÁLIDO ==========
    function marcarError(campoId, mensaje) {
        const campo = document.getElementById(campoId);
        const errorDiv = document.getElementById(`error-${campoId}`);
        if (campo) campo.classList.add('is-invalid');
        if (errorDiv) errorDiv.textContent = mensaje;
    }

    // ========== EVENTO DE ENVÍO DEL FORMULARIO ==========
    formulario.addEventListener('submit', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        // Limpiar errores previos
        limpiarErrores();
        
        // Obtener valores de los campos
        const nombre = document.getElementById('fname').value.trim();
        const apellido = document.getElementById('lname').value.trim();
        const rut = document.getElementById('rut').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('pwd1').value;
        const password2 = document.getElementById('pwd2').value;
        const checkbox = document.getElementById('remember').checked;
        
        let isValid = true;
        
        // ========== 1. VALIDACIÓN DE NOMBRE ==========
        const regexLetras = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$/;
        if (!nombre) {
            marcarError('fname', 'El nombre es obligatorio');
            isValid = false;
        } else if (nombre.length < 3) {
            marcarError('fname', 'El nombre debe tener al menos 3 caracteres');
            isValid = false;
        } else if (!regexLetras.test(nombre)) {
            marcarError('fname', 'El nombre solo puede contener letras');
            isValid = false;
        } else {
            document.getElementById('fname').classList.add('is-valid');
        }
        
        // ========== 2. VALIDACIÓN DE APELLIDO ==========
        if (!apellido) {
            marcarError('lname', 'El apellido es obligatorio');
            isValid = false;
        } else if (apellido.length < 3) {
            marcarError('lname', 'El apellido debe tener al menos 3 caracteres');
            isValid = false;
        } else if (!regexLetras.test(apellido)) {
            marcarError('lname', 'El apellido solo puede contener letras');
            isValid = false;
        } else {
            document.getElementById('lname').classList.add('is-valid');
        }
        
        // ========== 3. VALIDACIÓN DE RUT (con letra K soportada) ==========
        if (!rut) {
            marcarError('rut', 'El RUT es obligatorio');
            isValid = false;
        } else if (!validarRut(rut)) {
            marcarError('rut', 'RUT no válido. Ejemplo: 12345678K o 123456789');
            isValid = false;
        } else {
            document.getElementById('rut').classList.add('is-valid');
        }
        
        // ========== 4. VALIDACIÓN DE EMAIL ==========
        const regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email) {
            marcarError('email', 'El correo electrónico es obligatorio');
            isValid = false;
        } else if (!regexEmail.test(email)) {
            marcarError('email', 'Formato de email no válido');
            isValid = false;
        } else {
            document.getElementById('email').classList.add('is-valid');
        }
        
        // ========== 5. VALIDACIÓN DE CONTRASEÑA ==========
        if (!password) {
            marcarError('pwd1', 'La contraseña es obligatoria');
            isValid = false;
        } else if (password.length < 6) {
            marcarError('pwd1', 'La contraseña debe tener al menos 6 caracteres');
            isValid = false;
        } else {
            document.getElementById('pwd1').classList.add('is-valid');
        }
        
        // ========== 6. VALIDACIÓN DE CONFIRMACIÓN ==========
        if (!password2) {
            marcarError('pwd2', 'Debes confirmar tu contraseña');
            isValid = false;
        } else if (password !== password2) {
            marcarError('pwd2', 'Las contraseñas no coinciden');
            isValid = false;
        } else if (password2.length >= 6) {
            document.getElementById('pwd2').classList.add('is-valid');
        }
        
        // ========== 7. VALIDACIÓN DE TÉRMINOS Y CONDICIONES ==========
        if (!checkbox) {
            document.getElementById('error-checkbox').textContent = 'Debes aceptar los términos y condiciones';
            isValid = false;
        } else {
            document.getElementById('error-checkbox').textContent = '';
        }
        
        // ========== 8. SI TODO ES VÁLIDO, ENVIAR A DJANGO ==========
        if (isValid) {
            // Mostrar mensaje de carga
            mostrarMensaje('⏳ Procesando registro...', 'info');
            
            // Crear FormData con los datos del formulario
            const formData = new FormData(formulario);
            
            // Enviar por AJAX
            fetch('/crearUsuario/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    mostrarMensaje(data.message, 'success');
                    // Redirigir después de 2 segundos
                    setTimeout(() => {
                        window.location.href = data.redirect_url || '/login/';
                    }, 2000);
                } else {
                    mostrarMensaje(data.message || 'Error en el registro', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarMensaje('❌ Error de conexión con el servidor', 'error');
            });
        } else {
            // Mostrar mensaje de error general
            mostrarMensaje('❌ Por favor, corrige los errores en el formulario', 'error');
        }
    });
});