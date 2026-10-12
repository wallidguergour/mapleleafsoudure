/* ================================================
   Chapitres des vidéos YouTube
   Les lecteurs youtube-nocookie.com sont déjà dans la page (_includes/youtube.html) :
   un clic sur un chapitre relance SON lecteur (même bloc .mls-video-bloc) à l'instant choisi.
================================================ */
(function () {
  'use strict';

  document.querySelectorAll('.mls-chapters [data-start]').forEach(function (bouton) {
    bouton.addEventListener('click', function () {
      var bloc = bouton.closest('.mls-video-bloc');
      var cadre = bloc && bloc.querySelector('.mls-video__frame');
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
