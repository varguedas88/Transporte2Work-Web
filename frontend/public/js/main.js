// SLIDER AUTOMÁTICO
document.addEventListener('DOMContentLoaded', function () {
  const slides = document.querySelectorAll('.slide');
  let currentIndex = 0;

  function showNextSlide() {
    slides[currentIndex].classList.remove('active');
    currentIndex = (currentIndex + 1) % slides.length;
    slides[currentIndex].classList.add('active');
  }

  // Cambia de imagen cada 5 segundos
  setInterval(showNextSlide, 5000);

  // MENÚ MÓVIL (hamburguesa)
  const hamburger = document.querySelector('.hamburger');
  const navMenu = document.querySelector('.nav-menu');

  if (hamburger && navMenu) {
    hamburger.addEventListener('click', () => {
      navMenu.classList.toggle('active');
      // Animación simple para ícono (opcional)
      hamburger.classList.toggle('active');
    });

    // Cerrar menú al hacer clic en un enlace (móvil)
    document.querySelectorAll('.nav-menu a').forEach(link => {
      link.addEventListener('click', () => {
        navMenu.classList.remove('active');
        hamburger.classList.remove('active');
      });
    });
  }
});
