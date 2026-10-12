/* ================================================
   Chapitres de la vidéo YouTube
   Le lecteur youtube-nocookie.com est déjà dans la page (_includes/youtube.html) :
   un clic sur un chapitre relance la vidéo à l'instant choisi.
================================================ */
(function () {
  'use strict';

  document.querySelectorAll('.mls-chapters [data-start]').forEach(function (bouton) {
    bouton.addEventListener('click', function () {
      var cadre = document.querySelector('.mls-video__frame');
      var iframe = cadre && cadre.querySelector('iframe');
      var id = cadre && cadre.getAttribute('data-youtube-id');
      if (!iframe || !id) return;
      var debut = parseInt(bouton.getAttribute('data-start'), 10) || 0;
      iframe.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) +
        '?rel=0&autoplay=1&start=' + debut;
      cadre.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  });
})();
