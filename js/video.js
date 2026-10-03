/* ================================================
   Vidéo YouTube en chargement différé
   L'iframe youtube-nocookie.com n'est créée qu'au clic
   (sur la miniature ou sur un chapitre).
================================================ */
(function () {
  'use strict';

  function lancer(frame, debut) {
    var id = frame.getAttribute('data-youtube-id');
    if (!id) return;
    var src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) +
      '?autoplay=1&rel=0' + (debut ? '&start=' + parseInt(debut, 10) : '');
    var iframe = document.createElement('iframe');
    iframe.src = src;
    iframe.title = frame.getAttribute('data-youtube-title') || 'Vidéo YouTube';
    iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    iframe.referrerPolicy = 'strict-origin-when-cross-origin';
    iframe.allowFullscreen = true;
    frame.innerHTML = '';
    frame.appendChild(iframe);
  }

  document.querySelectorAll('.mls-video__frame').forEach(function (frame) {
    var bouton = frame.querySelector('.mls-video__play');
    if (bouton) {
      bouton.addEventListener('click', function () { lancer(frame, 0); });
    }
  });

  document.querySelectorAll('.mls-chapters [data-start]').forEach(function (bouton) {
    bouton.addEventListener('click', function () {
      var frame = document.querySelector('.mls-video__frame');
      if (!frame) return;
      lancer(frame, bouton.getAttribute('data-start'));
      frame.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
  });
})();
