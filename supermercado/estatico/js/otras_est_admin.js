// otras_est_admin.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ otras_est_admin.js cargado');

    // ========== GRÁFICO 1: TOP 10 PRODUCTOS ==========
    const ctx1 = document.getElementById('graficoTopProductos');
    
    if (ctx1 && window.datosProductos && window.datosProductos.length > 0) {
        new Chart(ctx1.getContext('2d'), {
            type: 'bar',
            data: {
                labels: window.datosProductos.map(item => item.nombre),
                datasets: [{
                    label: 'Unidades vendidas',
                    data: window.datosProductos.map(item => item.total),
                    backgroundColor: 'rgba(54, 162, 235, 0.8)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    borderRadius: 5,
                    barPercentage: 0.7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            font: { size: 14, weight: 'bold' }
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            maxRotation: 45,
                            minRotation: 30,
                            font: { size: 11 }
                        },
                        title: {
                            display: true,
                            text: 'Productos',
                            font: { size: 14, weight: 'bold' }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Unidades vendidas',
                            font: { size: 14, weight: 'bold' }
                        },
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
        console.log('✅ Gráfico 1 creado correctamente');
    } else {
        console.warn('⚠️ No hay datos para el gráfico 1');
        if (ctx1) {
            ctx1.parentElement.innerHTML = `
                <p class="text-muted text-center py-4">
                    <i class="fas fa-box fa-2x d-block mb-2"></i>
                    No hay datos de productos vendidos
                </p>
            `;
        }
    }

    // ========== GRÁFICO 2: MONTO VENDIDO POR DÍA ==========
    const ctx2 = document.getElementById('graficoActividadDiaria');
    
    if (ctx2 && window.datosDias && window.datosDias.length > 0) {
        new Chart(ctx2.getContext('2d'), {
            type: 'bar',
            data: {
                labels: window.datosDias,
                datasets: [{
                    label: 'Monto vendido ($)',
                    data: window.datosValor,
                    backgroundColor: 'rgba(46, 204, 113, 0.8)',
                    borderColor: 'rgba(46, 204, 113, 1)',
                    borderWidth: 2,
                    borderRadius: 5,
                    barPercentage: 0.7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            font: { size: 14, weight: 'bold' }
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            maxRotation: 0,
                            font: { size: 13 }
                        },
                        title: {
                            display: true,
                            text: 'Días',
                            font: { size: 14, weight: 'bold' }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Monto vendido ($)',
                            font: { size: 14, weight: 'bold' }
                        }
                    }
                }
            }
        });
        console.log('✅ Gráfico 2 creado correctamente');
    } else {
        console.warn('⚠️ No hay datos para el gráfico 2');
        if (ctx2) {
            ctx2.parentElement.innerHTML = `
                <p class="text-muted text-center py-4">
                    <i class="fas fa-chart-bar fa-2x d-block mb-2"></i>
                    No hay pedidos en los últimos 30 días
                </p>
            `;
        }
    }
});