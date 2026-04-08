const toggleBtn = document.getElementById('toggleBtn');
const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('mainContent');

toggleBtn.addEventListener('click', () => {
    // Alterna la clase 'active' para móviles
    sidebar.classList.toggle('active');
    
    // Alterna clases para comportamiento en escritorio (opcional)
    sidebar.classList.toggle('collapsed');
    mainContent.classList.toggle('expanded');
});