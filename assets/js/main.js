var _____WB$wombat$assign$function_____=function(name){return (globalThis._wb_wombat && globalThis._wb_wombat.local_init && globalThis._wb_wombat.local_init(name))||globalThis[name];};if(!globalThis.__WB_pmw){globalThis.__WB_pmw=function(obj){this.__WB_source=obj;return this;}}{
let window = _____WB$wombat$assign$function_____("window");
let self = _____WB$wombat$assign$function_____("self");
let document = _____WB$wombat$assign$function_____("document");
let location = _____WB$wombat$assign$function_____("location");
let top = _____WB$wombat$assign$function_____("top");
let parent = _____WB$wombat$assign$function_____("parent");
let frames = _____WB$wombat$assign$function_____("frames");
let opener = _____WB$wombat$assign$function_____("opener");
/**
 * @package Helix Ultimate Framework
 * @author JoomShaper https://www.joomshaper.com
 * @copyright Copyright (c) 2010 - 2018 JoomShaper
 * @license http://www.gnu.org/licenses/gpl-2.0.html GNU/GPLv2 or Later
 */

jQuery(function($) {

  // Stikcy Header
  if ($('body').hasClass('sticky-header')) {
    var header = $('#sp-header');

    if ($('#sp-header').length) {
      var headerHeight = header.outerHeight();
      var stickyHeaderTop = header.offset().top;
      var stickyHeader = function() {
        var scrollTop = $(window).scrollTop();
        if (scrollTop > stickyHeaderTop) {
          header.addClass('header-sticky');
        } else {
          if (header.hasClass('header-sticky')) {
            header.removeClass('header-sticky');
          }
        }
      };
      stickyHeader();
      $(window).scroll(function() {
        stickyHeader();
      });
    }

    if ($('body').hasClass('layout-boxed')) {
      var windowWidth = header.parent().outerWidth();
      header.css({ "max-width": windowWidth, "left": "auto" });
    }
  }

  // go to top
  $(window).scroll(function() {
    if ($(this).scrollTop() > 100) {
      $('.sp-scroll-up').fadeIn();
    } else {
      $('.sp-scroll-up').fadeOut(400);
    }
  });

  $('.sp-scroll-up').click(function() {
    $("html, body").animate({
      scrollTop: 0
    }, 600);
    return false;
  });

  // Preloader
  $(window).on('load', function() {
    $('.sp-preloader').fadeOut(500, function() {
      $(this).remove();
    });
  });

  //mega menu
  $('.sp-megamenu-wrapper').parent().parent().css('position', 'static').parent().css('position', 'relative');
  $('.sp-menu-full').each(function() {
    $(this).parent().addClass('menu-justify');
  });

  // Offcanvs
  $('#offcanvas-toggler').on('click', function(event) {
    event.preventDefault();
    $('.offcanvas-init').addClass('offcanvas-active');
  });

  $('.close-offcanvas, .offcanvas-overlay').on('click', function(event) {
    event.preventDefault();
    $('.offcanvas-init').removeClass('offcanvas-active');
  });

  $(document).on('click', '.offcanvas-inner .menu-toggler', function(event) {
    event.preventDefault();
    $(this).closest('.menu-parent').toggleClass('menu-parent-open').find('>.menu-child').slideToggle(400);
  });

  // Tooltip
	var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"], .hasTooltip'));
	var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
		return new bootstrap.Tooltip(tooltipTriggerEl,{
			html: true
		  });
	});

	// Popover
	var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
	var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
		return new bootstrap.Popover(popoverTriggerEl);
	});

  // Article Ajax voting
  $('.article-ratings .rating-star').on('click', function(event) {
    event.preventDefault();
    var $parent = $(this).closest('.article-ratings');

    var request = {
      'option': 'com_ajax',
      'template': template,
      'action': 'rating',
      'rating': $(this).data('number'),
      'article_id': $parent.data('id'),
      'format': 'json'
    };

    $.ajax({
      type: 'POST',
      data: request,
      beforeSend: function() {
        $parent.find('.fa-spinner').show();
      },
      success: function(response) {
        var data = $.parseJSON(response);
        $parent.find('.ratings-count').text(data.message);
        $parent.find('.fa-spinner').hide();

        if (data.status) {
          $parent.find('.rating-symbol').html(data.ratings)
        }

        setTimeout(function() {
          $parent.find('.ratings-count').text('(' + data.rating_count + ')')
        }, 3000);
      }
    });
  });



  // Top Search
    $(".search-open-icon").on('click', function() {
        $(".top-search-input-wrap, .top-search-overlay").fadeIn(200);
        $(this).hide();
        $('.search-close-icon').show().css('display', 'inline-block');
        $('body.off-canvas-menu-init').css({
            'overflow-y': 'hidden'
        });
        $('#sp-header').css({
            'z-index': '999'
        });
        $('.top-search-input-wrap').css('height', '100vh');
    });

    $(".search-close-icon, .top-search-overlay").on('click', function() {
        $(".top-search-input-wrap, .top-search-overlay").fadeOut(200);
        $('.search-close-icon').hide();
        $('.search-open-icon').show();
        $('body.off-canvas-menu-init').css({
            'overflow-y': 'initial'
        });
        $('#sp-header').css({
            'z-index': '99'
        });
        $('.top-search-input-wrap').css('height', '100%');
    });

    // press esc to hide search
    $(document).keyup(function(e) {
        if (e.keyCode == 27) { // esc keycode
            $(".top-search-input-wrap").fadeOut(200);
            $(".search-close-icon").fadeOut(200);
            $(".search-open-icon").delay(200).fadeIn(200);
            $('body.off-canvas-menu-init').css({
                'overflow-y': 'initial'
            });
        }
    });
    // End Top Search


















});
}

/*
     FILE ARCHIVED ON 17:21:26 Feb 27, 2026 AND RETRIEVED FROM THE
     INTERNET ARCHIVE ON 16:02:05 Nov 17, 2026.
     JAVASCRIPT APPENDED BY WAYBACK MACHINE, COPYRIGHT INTERNET ARCHIVE.

     ALL OTHER CONTENT MAY ALSO BE PROTECTED BY COPYRIGHT (17 U.S.C.
     SECTION 108(a)(3)).
*/
/*
playback timings (ms):
  capture_cache.get: 0.473
  load_resource: 598.364 (2)
  PetaboxLoader3.resolve: 429.296 (2)
  PetaboxLoader3.datanode: 95.843 (3)
  revisit.resolve: 540.7
  loaddict: 112.288
*/