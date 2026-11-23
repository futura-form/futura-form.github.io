var _____WB$wombat$assign$function_____=function(name){return (globalThis._wb_wombat && globalThis._wb_wombat.local_init && globalThis._wb_wombat.local_init(name))||globalThis[name];};if(!globalThis.__WB_pmw){globalThis.__WB_pmw=function(obj){this.__WB_source=obj;return this;}}{
let window = _____WB$wombat$assign$function_____("window");
let self = _____WB$wombat$assign$function_____("self");
let document = _____WB$wombat$assign$function_____("document");
let location = _____WB$wombat$assign$function_____("location");
let top = _____WB$wombat$assign$function_____("top");
let parent = _____WB$wombat$assign$function_____("parent");
let frames = _____WB$wombat$assign$function_____("frames");
let opener = _____WB$wombat$assign$function_____("opener");
!function(t){var n=t(window),a=n.height();n.resize((function(){a=n.height()})),t.fn.parallax=function(o,r,i){var s,c,e=t(this);function l(){var i=n.scrollTop();e.each((function(){var n=t(this),l=n.offset().top;l+s(n)<i||l>i+a||!e.data("sppbparallax")||e.css("backgroundPosition",o+" "+Math.round((c-i)*r)+"px")}))}e.data("sppbparallax",!0),e.css("backgroundAttachment","fixed"),e.each((function(){c=e.offset().top})),s=i?function(t){return t.outerHeight(!0)}:function(t){return t.height()},(arguments.length<1||null===o)&&(o="50%"),(arguments.length<2||null===r)&&(r=.15),(arguments.length<3||null===i)&&(i=!0),n.bind("scroll",l).resize(l),l()},t.fn.parallaxDestroy=function(n,a){var o=t(this);o.data("sppbparallax")&&(n?o.css("backgroundPosition",n):o.css("backgroundPosition","0% 0%"),a?o.css("backgroundAttachment",a):o.css("backgroundAttachment","inherit"),o.data("sppbparallax",!1))}}(jQuery);
}

/*
     FILE ARCHIVED ON 11:13:17 Feb 27, 2026 AND RETRIEVED FROM THE
     INTERNET ARCHIVE ON 16:02:02 Nov 17, 2026.
     JAVASCRIPT APPENDED BY WAYBACK MACHINE, COPYRIGHT INTERNET ARCHIVE.

     ALL OTHER CONTENT MAY ALSO BE PROTECTED BY COPYRIGHT (17 U.S.C.
     SECTION 108(a)(3)).
*/
/*
playback timings (ms):
  capture_cache.get: 2.02
  load_resource: 363.174 (2)
  PetaboxLoader3.resolve: 57.274
  PetaboxLoader3.datanode: 262.393 (3)
  revisit.resolve: 213.342
  loaddict: 83.435
*/