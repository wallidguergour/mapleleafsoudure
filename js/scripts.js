/**
*	Cvio - Resume/CV Template (HTML)
*	Author: beshleyua
*	Author URL: http://themeforest.net/user/beshleyua
*	Copyright © Cvio by beshleyua. All Rights Reserved.
**/

( function( $ ) {
	'use strict';

	window.onpageshow = function(event) {if (event.persisted) {window.location.reload() }};

	$(window).on("load", function() {

		/*
			Preloader
		*/
		var preload = $('.preloader');
		preload.find('.spinner').fadeOut(function(){
			preload.fadeOut();
		});

		/*
			Lines Animations
		*/
		$('.lines').addClass('finish');
		setTimeout(function(){
			$('.lines').addClass('ready');
		}, 2000);

		/*
			Typed Subtitle
		*/
		if(($('.typed-subtitle').length) && ($('.h-subtitle p').length > 1)){
			$('.typed-subtitle').each(function(){
				$(this).typed({
					stringsElement: $(this).prev('.typing-subtitle'),
					loop: true
				});
			});
		}
		
		/*
			Typed Breadcrumbs
		*/
		setTimeout(function(){
			$('.h-subtitles').addClass('ready');
			if($('.typed-bread').length){
				$('.typed-bread').typed({
					stringsElement: $('.typing-bread'),
					showCursor: false
				});
			}
		}, 1000);

		/*
			One Page Nav
		*/
		var url_hash = location.hash;
		var sectionElem = $(url_hash);
		if(url_hash.indexOf('#section-') == 0 && sectionElem.length){
			$('body, html').animate({scrollTop: $(url_hash).offset().top - 68}, 400);
		}

		/*
			Jarallax
		*/
		if($('.jarallax').length){
			$('.jarallax').jarallax();
		}

		/*
			Started Slider
		*/
		if($('.started-carousel').length){
			var started_slider = new Swiper ('.started-carousel .swiper-container', {
				init: false,
				loop: false,
				spaceBetween: 0,
				effect: 'fade',
				slidesPerView: 1,
				simulateTouch: false,
				autoplay: {
					delay: 6000,
					disableOnInteraction: false,
					waitForTransition: false,
				},
				navigation: {
					nextEl: '.started .swiper-button-next',
					prevEl: '.started .swiper-button-prev',
				},
			});
			started_slider.on('slideChange', function () {
				var index = started_slider.realIndex;
				var total = started_slider.slides.length;

				$('.started-carousel .swiper-slide').removeClass('first');
				$('.started-carousel .swiper-slide').each(function(i, slide){
					if((index-1)>=i) {
						$(slide).addClass('swiper-clip-active');
					} else {
						$(slide).removeClass('swiper-clip-active');
					}
				});
				$('.started-carousel .swiper-slide').each(function(i, slide){
					$(slide).css({'z-index': total - i});
				});
			});
			started_slider.init();
		}

		/*
			Testimonials Slider
		*/
		if($('.reviews-carousel').length){
			var rev_slider = new Swiper ('.reviews-carousel .swiper-container', {
				loop: true,
				spaceBetween: 70,
				slidesPerView: 2,
				autoplay: {
					delay: 6000
				},
				navigation: {
					nextEl: '.reviews-carousel .swiper-button-next',
					prevEl: '.reviews-carousel .swiper-button-prev',
				},
				breakpoints: {
					720: {
						slidesPerView: 1,
						spaceBetween: 40,
					},
					1200: {
						slidesPerView: 2,
						spaceBetween: 70,
					},
				}
			});
		}

		/*
			Refresh Scroll
		*/
		function scroll_refresh(){
			$(window).scrollTop($(window).scrollTop()+1);
		}
		setTimeout(scroll_refresh, 100);

	});

	/*
		Set full height in blocks
	*/
	var width = $(window).width();
	var height = $(window).height();

	/*
		Set Height Started Section
	*/
	$('.section.started').css({'height': height});
	$('.logged-in .section.started').css({'height': height-32});
	if(width < 783) {
		$('.section.started').css({'height': height});
		$('.logged-in .section.started').css({'height': height-46});
	}

	/*
		Grained
	*/
	if(!$('.grained-off').length){
	var grained_options = {
		'animate': true,
		'patternWidth': 400,
		'patternHeight': 400,
		'grainOpacity': 0.15,
		'grainDensity': 3,
		'grainWidth': 1,
		'grainHeight': 1
	}
	grained('#grained_container', grained_options);
	}
	
	/*
		Cursor Effects
	*/
	if(width > 1199) {
		$(document).on('mousemove', function(e){ 
			var x = e.pageX;
			var y = e.pageY;
			var newposX = x;
			var newposY = y;
			$('.cursor-follower').css('transform','translate3d('+newposX+'px,'+newposY+'px,0px)');
		});
		$('a, .btn-group').on({
			mouseenter: function (e) {
				cursor_over();
			},
			mouseleave: function (e) {
				cursor_out();
			}
		});
	}
	function cursor_over(){
		$(".cursor-follower").stop().animate({width: 86, height: 86, opacity: 0.1, margin: '-43px 0 0 -43px'}, 500);
	}
	function cursor_out(){
		$(".cursor-follower").stop().animate({width: 26, height: 26, opacity: 0.4, margin: '-13px 0 0 -13px'}, 500);
	}

	/*
		Hover Masks
	*/
	$('.hover-masks a').each(function() {
		var mask_val = $(this).html();
		$(this).wrapInner('<span class="mask-lnk"></span>');
		$(this).append('<span class="mask-lnk mask-lnk-hover">' + mask_val + '</span>');
	});

	/*
		Hover Button Effect
	*/
	$('.hover-animated .circle').on({
		mouseenter: function (e) {
			if ($(this).find(".ink").length === 0) {
				$(this).prepend("<span class='ink'></span>");
			}
			var ink = $(this).find(".ink");
			ink.removeClass("animate");
			if (!ink.height() && !ink.width()) {
				var d = Math.max($(this).outerWidth(), $(this).outerHeight());
				ink.css({
					height: d,
					width: d
				});
			}
			var x = e.pageX - $(this).offset().left - ink.width() / 2;
			var y = e.pageY - $(this).offset().top - ink.height() / 2;
			ink.css({
				top: y + 'px',
				left: x + 'px'
			}).addClass("ink-animate");
			$('.cursor-follower').addClass('hide');
		},
		mouseleave: function (e) {
			var ink = $(this).find(".ink");
			var x = e.pageX - $(this).offset().left - ink.width() / 2;
			var y = e.pageY - $(this).offset().top - ink.height() / 2;
			ink.css({
				top: y + 'px',
				left: x + 'px'
			}).removeClass("ink-animate");
			$('.cursor-follower').removeClass('hide');
		}
	});
	
	/*
		Animation Between Pages
	*/
	$('header .top-menu, .typed-bread, .popup-box .bts, .animate-to-page').on('click', 'a', function(){
		var link = $(this).attr('href');
		if(link.indexOf('#section-') == 0){
			if(!$('body').hasClass('home')){
				location.href = '/'+link;
			}

			$('body, html').animate({scrollTop: $(link).offset().top - 68}, 400);
			if($('header').hasClass('active')){
				$('.menu-btn').trigger('click');
			}
		} else {
			$('.lines').removeClass('finish');
			$('.lines').removeClass('ready');
			$('.lines').addClass('no-lines');
			setTimeout(function() {
				location.href = "" + link;
			}, 2500);
		}
		return false;
	});
	
	/*
		On Scroll 
	*/
	$(window).on('scroll', function(){

		/* add/remove background-enabled class */
		if ($(this).scrollTop() >= $('.section.started').height()) {
			$('body').removeClass('background-enabled');
		} else {
			if((!$('header').hasClass('active')) && $('.video-bg').length) {
				$('body').addClass('background-enabled');
			}
		}

		/* add/remove header/footer fixed class */
		if (($(this).scrollTop() >= 100) && ($('.section').length>1)) {
			$('.header').addClass('fixed');
			$('.footer').addClass('fixed');
			$('.mouse_btn').fadeOut();
		}
		if (($(this).scrollTop() <= 100) && ($('.section').length>1)) {
			$('.header').removeClass('fixed');
			$('.footer').removeClass('fixed');
			$('.mouse_btn').fadeIn();
		}
		
	});

	/*
		Menu on Mobile
	*/
	$('header').on('click', '.menu-btn', function(){
		if($('header').hasClass('active')){
			$('header').removeClass('active');
			$('.footer .soc').fadeIn();
			$('body').addClass('loaded');
			if($('.video-bg').length) {
				$('body').addClass('background-enabled');
			}
		} else {
			$('header').addClass('active');
			$('.footer .soc').hide();
			$('body').removeClass('loaded');
			$('body').removeClass('background-enabled');
		}
		
		return false;
	});

	/*
		Download CV on Mobile
	*/
	$('.section.about').on('click touchstart', '.btn', function(){
		location.href = $(this).attr('href');
	});
	
	/*
		Mouse Button Scroll
	*/
	$('.section').on('click', '.mouse_btn', function(){
		$('body, html').animate({
			scrollTop: height - 150
		}, 800);
	});
	if($('.section').length>1){
		$('.mouse_btn').show();
	}
	
	/*
		Portfolio, popups, parallaxe, compétences, formulaire de contact et carte du thème Cvio :
		retirés (non utilisés sur le site, librairies absentes, provoquaient l'erreur imagesLoaded).
	*/

} )( jQuery );
