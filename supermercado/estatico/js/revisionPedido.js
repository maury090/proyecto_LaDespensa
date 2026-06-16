document.addEventListener('DOMContentLoaded', function() {
    
    const retiroRadio = document.getElementById('retiroTienda');
    const despachoRadio = document.getElementById('despachoDomicilio');
    const totalFinal = document.getElementById('totalFinal');
    const filaDespacho = document.getElementById('filaDespacho');
    
    
    const totalOriginal = parseInt(document.getElementById('totalFinal').getAttribute('data-total-original'));
    const costoDespacho = parseInt(document.getElementById('totalFinal').getAttribute('data-costo-despacho'));
    
    function actualizarTotal() {
        if (despachoRadio && despachoRadio.checked) {
            const nuevoTotal = totalOriginal + costoDespacho;
            totalFinal.textContent = '$' + nuevoTotal;
            if (filaDespacho) {
                filaDespacho.style.display = 'table-row';
            }
        } else {
            totalFinal.textContent = '$' + totalOriginal;
            if (filaDespacho) {
                filaDespacho.style.display = 'none';
            }
        }
    }
    
    // agregar funcion a radiobuttons
    if (retiroRadio) {
        retiroRadio.addEventListener('change', actualizarTotal);
    }
    if (despachoRadio) {
        despachoRadio.addEventListener('change', actualizarTotal);
    }
    
    // si el despacho está deshabilitado, forzar retiro en tienda
    if (despachoRadio && despachoRadio.disabled) {
        if (retiroRadio) {
            retiroRadio.checked = true;
        }
        actualizarTotal();
    }
    
    actualizarTotal();
});