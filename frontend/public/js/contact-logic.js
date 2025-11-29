// js/contact-logic.js

/**
 * Inicializa los listeners del formulario de contacto (estrellas y envío).
 * Se llama después de que el formulario de contacto se carga dinámicamente.
 */
window.initializeContactFormLogic = function() {
    const form = document.getElementById('contactForm');
    const ratingStars = document.getElementById('ratingStars');
    const ratingValue = document.getElementById('ratingValue');
    const formMessage = document.getElementById('form-message');
    let selectedRating = 0;

    // Si los elementos no existen (porque la carga dinámica no ha terminado), salimos.
    if (!form || !ratingStars) return;

    // --- Lógica de Estrellas de Evaluación ---
    ratingStars.addEventListener('click', (e) => {
        if (e.target.classList.contains('star-rating')) {
            selectedRating = parseInt(e.target.dataset.rating);
            ratingValue.value = selectedRating;

            // Lógica visual: resalta las estrellas hasta la seleccionada
            ratingStars.querySelectorAll('.star-rating').forEach(star => {
                const starRating = parseInt(star.dataset.rating);
                if (starRating <= selectedRating) {
                    // Resalta (amarillo)
                    star.classList.add('text-warning');
                    star.classList.remove('text-muted');
                } else {
                    // Desactiva (gris)
                    star.classList.remove('text-warning');
                    star.classList.add('text-muted');
                }
            });

            // Si selecciona estrellas, quitamos la validación de error
            ratingValue.classList.remove('is-invalid');
        }
    });

    // --- Lógica de Envío del Formulario (a Python) ---
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        event.stopPropagation();

        // 1. Validación de Bootstrap y Estrellas
        if (!form.checkValidity() || selectedRating === 0) {
            form.classList.add('was-validated');
            if (selectedRating === 0) {
                 ratingValue.classList.add('is-invalid');
            }
            return;
        }

        // 2. Recolección de Datos
        const data = {
            name: document.getElementById('fullName').value,
            email: document.getElementById('email').value,
            subject: document.getElementById('subject').value,
            rating: selectedRating,
            message: document.getElementById('message').value
        };

        // 3. Envío de datos JSON al endpoint de Python
        // URL debe coincidir con la dirección donde corre tu servidor Flask (server.py)
        fetch('http://localhost:5000/api/send-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            // Manejar respuestas de error (4xx o 5xx) del servidor Python
            if (!response.ok) {
                return response.json().then(resData => {
                    // El servidor Python debería retornar un mensaje de error en JSON
                    throw new Error(resData.message || 'Error desconocido del servidor.');
                });
            }
            return response.json(); // Leemos la respuesta JSON de éxito
        })
        .then(resData => {
            // ÉXITO (Código 200 de Python)
            formMessage.style.display = 'block';
            formMessage.className = 'col-12 mt-3 alert alert-success';
            formMessage.innerHTML = '✅ **Mensaje enviado!** Gracias por tu consulta.';

            // Limpiar y resetear formulario y estrellas
            form.reset();
            form.classList.remove('was-validated');
            selectedRating = 0;
            ratingValue.value = '';
            ratingStars.querySelectorAll('.star-rating').forEach(star => {
                star.classList.remove('text-warning');
                star.classList.add('text-muted');
            });
        })
        .catch(error => {
            // ERROR (incluye errores de red o errores 400/500 de Python)
            console.error('Error al enviar:', error);
            formMessage.style.display = 'block';
            formMessage.className = 'col-12 mt-3 alert alert-danger';
            formMessage.innerHTML = `❌ **Error al enviar.** Intenta más tarde. Detalle: ${error.message}`;
        });
    });
};

// ====================================================================
// Lógica de carga de componentes e inicialización de la página (Movido de contacto.html)
// ====================================================================
document.addEventListener('DOMContentLoaded', () => {
    // Verificamos que la función de carga exista (definida en js/scripts.js)
    if (window.loadHtmlComponent) {

        // Carga la Navbar y Sidebar
        window.loadHtmlComponent('components/navbar.html', 'navbar-container');

        window.loadHtmlComponent('components/sidebar.html', 'sidebar-container').then(() => {
            // Lógica para resaltar el enlace activo (definida en js/active-link.js)
            if (window.highlightActiveLink) {
                window.highlightActiveLink();
            }
            // Lógica adicional de sesión/menús (si existe)
            if (window.checkSessionAndMenus) {
                 window.checkSessionAndMenus();
            }
        });

        // Carga el formulario de Contacto y LUEGO inicializa la lógica del formulario/estrellas
        window.loadHtmlComponent('components/contacto-form.html', 'contact-form-container')
            .then(() => {
                // Llamamos a la función de inicialización del formulario definida arriba
                if (window.initializeContactFormLogic) {
                    window.initializeContactFormLogic();
                }
            });
    } else {
        console.error("Error: La función loadHtmlComponent no está definida. Asegúrate de que js/scripts.js se cargue antes que este archivo.");
    }
});