/* sales.js : Soudeur à Coup Sûr */

/* ---- Shims pour plugins Cvio non chargés (évite TypeErrors dans scripts.js) ---- */
if (typeof jQuery !== 'undefined') {
  if (!jQuery.fn.magnificPopup) {
    jQuery.fn.magnificPopup = function () { return this; };
  }
  if (!jQuery.fn.imagesLoaded) {
    jQuery.fn.imagesLoaded = function (cb) { if (cb) cb(); return this; };
  }
  if (!jQuery.fn.isotope) {
    jQuery.fn.isotope = function () { return this; };
  }
}

(function ($) {
  'use strict';

  /* ---- Back to top ---- */
  var $backToTop = $('#backToTop');
  $(window).on('scroll', function () {
    $backToTop.toggleClass('show', $(this).scrollTop() > 300);
  });
  $backToTop.on('click', function () {
    $('html, body').animate({ scrollTop: 0 }, 400);
  });

  /* ---- Smooth scroll pour les CTA de contenu (hors nav header) ---- */
  $('.wrapper a[href^="#section-"]').on('click', function (e) {
    var target = $(this).attr('href');
    if ($(target).length) {
      e.preventDefault();
      $('html, body').animate({ scrollTop: $(target).offset().top - 68 }, 400);
    }
  });

  /* ---- FAQ accordéon (classes cvio-faq) ---- */
  $(document).on('click', '.cvio-faq__q', function () {
    var $item = $(this).closest('.cvio-faq__item');
    var isOpen = $item.hasClass('open');
    $('.cvio-faq__item').removeClass('open');
    if (!isOpen) {
      $item.addClass('open');
    }
  });

  /* ---- Validation formulaire opt-in ---- */
  if ($('#optin-form').length) {
    $('#optin-form').validate({
      rules: {
        email: { required: true, email: true }
      },
      messages: {
        email: {
          required: 'Veuillez entrer votre adresse e-mail.',
          email:    'Adresse e-mail invalide.'
        }
      },
      submitHandler: function (form) {
        /* [[ À COMPLÉTER : brancher l'action réelle du formulaire email ]] */
        $(form).find('button[type="submit"]').text('Inscription enregistrée !').prop('disabled', true);
      }
    });
  }

})(jQuery);
