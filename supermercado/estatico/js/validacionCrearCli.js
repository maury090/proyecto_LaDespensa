// Esperamos a que el DOM esté cargado
document.addEventListener('DOMContentLoaded', function() {
    
    const formulario = document.getElementById('registroForm');

    // Función para validar el RUT chileno (Algoritmo Módulo 11)
    function validarRut(rutCompleto) {
        if (!/^[0-9]+[0-9kK]{1}$/.test(rutCompleto)) return false;
        let rut = rutCompleto.slice(0, -1);
        let dv = rutCompleto.slice(-1).toUpperCase();
        let suma = 0;
        let multiplicador = 2;
        for (let i = rut.length - 1; i >= 0; i--) {
            suma += parseInt(rut.charAt(i)) * multiplicador;
            multiplicador = multiplicador === 7 ? 2 : multiplicador + 1;
        }
        let dvEsperado = 11 - (suma % 11);
        if (dvEsperado === 11) dvEsperado = '0';
        if (dvEsperado === 10) dvEsperado = 'K';
        return dv.toString() === dvEsperado.toString();
    }

    formulario.addEventListener('submit', function(e) {
        // 1. DETENER EL ENVÍO INMEDIATAMENTE PARA VALIDAR
        e.preventDefault();
        e.stopPropagation();
        
        console.log("Iniciando validación de campos obligatorios...");

        let isValid = true;
        
        // 2. Referencias a todos los campos
        const fields = {
            fname: { input: document.getElementById('fname'), error: document.getElementById('error-fname'), name: "Nombre" },
            lname: { input: document.getElementById('lname'), error: document.getElementById('error-lname'), name: "Apellido" },
            rut: { input: document.getElementById('rut'), error: document.getElementById('error-rut'), name: "RUT" },
            email: { input: document.getElementById('email'), error: document.getElementById('error-email'), name: "Email" },
            pwd1: { input: document.getElementById('pwd1'), error: document.getElementById('error-pwd1'), name: "Contraseña" },
            pwd2: { input: document.getElementById('pwd2'), error: document.getElementById('error-pwd2'), name: "Confirmación" }
        };

        const regexLetras = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$/;
        const regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const checkbox = document.getElementById('remember');

        // 3. LIMPIEZA TOTAL DE ESTADOS PREVIOS
        Object.values(fields).forEach(f => {
            f.error.textContent = '';
            f.input.classList.remove('is-invalid', 'is-valid');
        });

        // 4. VALIDACIÓN DE CAMPOS VACÍOS (OBLIGATORIEDAD)
        Object.values(fields).forEach(f => {
            if (f.input.value.trim() === "") {
                f.error.textContent = `El campo ${f.name} es obligatorio.`;
                f.input.classList.add('is-invalid');
                isValid = false;
            }
        });

        // 5. VALIDACIONES ESPECÍFICAS (Solo si no están vacíos)
        if (isValid) {
            // Validación Nombre
            if (fields.fname.input.value.trim().length < 3) {
                fields.fname.error.textContent = "Mínimo 3 caracteres.";
                fields.fname.input.classList.add('is-invalid');
                isValid = false;
            } else if (!regexLetras.test(fields.fname.input.value)) {
                fields.fname.error.textContent = "Solo letras.";
                fields.fname.input.classList.add('is-invalid');
                isValid = false;
            } else {
                fields.fname.input.classList.add('is-valid');
            }

            // Validación Apellido
            if (fields.lname.input.value.trim().length < 3) {
                fields.lname.error.textContent = "Mínimo 3 caracteres.";
                fields.lname.input.classList.add('is-invalid');
                isValid = false;
            } else if (!regexLetras.test(fields.lname.input.value)) {
                fields.lname.error.textContent = "Solo letras.";
                fields.lname.input.classList.add('is-invalid');
                isValid = false;
            } else {
                fields.lname.input.classList.add('is-valid');
            }

            // Validación RUT
            const rutLimpio = fields.rut.input.value.replace(/\./g, '').replace(/-/g, '');
            if (!validarRut(rutLimpio)) {
                fields.rut.error.textContent = "RUT no válido.";
                fields.rut.input.classList.add('is-invalid');
                isValid = false;
            } else {
                fields.rut.input.classList.add('is-valid');
            }

            // Validación Email
            if (!regexEmail.test(fields.email.input.value)) {
                fields.email.error.textContent = "Email inválido.";
                fields.email.input.classList.add('is-invalid');
                isValid = false;
            } else {
                fields.email.input.classList.add('is-valid');
            }

            // Validación Contraseña Largo
            if (fields.pwd1.input.value.length < 6) {
                fields.pwd1.error.textContent = "Mínimo 6 caracteres.";
                fields.pwd1.input.classList.add('is-invalid');
                isValid = false;
            } else {
                fields.pwd1.input.classList.add('is-valid');
            }

            // Validación Coincidencia
            if (fields.pwd1.input.value !== fields.pwd2.input.value) {
                fields.pwd2.error.textContent = "Las contraseñas no coinciden.";
                fields.pwd2.input.classList.add('is-invalid');
                isValid = false;
            } else {
                fields.pwd2.input.classList.add('is-valid');
            }
        }

        // 6. VALIDACIÓN TÉRMINOS Y CONDICIONES
        if (isValid && !checkbox.checked) {
            alert("Debe aceptar los términos y condiciones.");
            isValid = false;
        }

        // 7. RESULTADO FINAL
        if (isValid) {
            // Mostramos el mensaje de éxito
            alert("¡Usuario creado con éxito!"); 
            
            console.log("Validación completada. Datos listos para el backend de Django.");

            // OPCIONAL: Si quieres que el formulario se limpie después del éxito:
            // formulario.reset();
            // Object.values(fields).forEach(f => f.input.classList.remove('is-valid'));

            // Cuando estés listo para conectar con tu base de datos, 
            // descomenta la siguiente línea:
            // formulario.submit(); 
        } else {
            console.log("Existen errores en el formulario. Registro denegado.");
        }
    });
});