document.addEventListener('DOMContentLoaded', function() {
    
    // ========== FILTRO POR CATEGORÍA ==========
    const selectCategoria = document.getElementById('filtroCategoria');
    const tabla = document.getElementById('tablaProductos');
    
    if (selectCategoria && tabla) {
        const filas = tabla.querySelectorAll('tbody tr');

        function filtrarProductos() {
            const categoriaSeleccionada = selectCategoria.value;
            
            filas.forEach(fila => {
                const categoria = fila.getAttribute('data-categoria') || '';
                
                if (categoriaSeleccionada === 'todas' || categoria === categoriaSeleccionada) {
                    fila.style.display = '';
                } else {
                    fila.style.display = 'none';
                }
            });
        }

        selectCategoria.addEventListener('change', filtrarProductos);
    }

    // ========== MODAL DE ELIMINACIÓN ==========
    const modalEliminar = document.getElementById('modalEliminar');
    
    if (modalEliminar) {
        modalEliminar.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            const productoId = button.getAttribute('data-id');
            const productoNombre = button.getAttribute('data-nombre');
            
            const modalBody = document.getElementById('modalMensaje');
            if (modalBody) {
                modalBody.innerHTML = `¿Estás seguro de eliminar el producto "<strong>${productoNombre}</strong>"? Esta acción no se puede deshacer.`;
            }
            
            const btnConfirmar = document.getElementById('btnConfirmarEliminar');
            if (btnConfirmar) {
                btnConfirmar.href = `/admin/supermercado/producto/${productoId}/delete/`;
            }
        });
    }
});