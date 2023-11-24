odoo.define('tournee.public_pages', function (require) {
"use strict";

// The purpose of this module is to adapt the image preview size on the public
// page of shared documents

require('web.dom_ready');

var $container = $('#wrap .o_docs_single_container.o_has_preview');
if ($container.length === 0) {
    return;
}

var $parent = $container.parent();
var $image = $container.find('> img');
var $actions = $container.find('.o_docs_single_actions');

var checkResize = _.throttle(function () {
    $image.css('max-height', $parent.height() - $actions.outerHeight());
}, 100);

$image.on('load', function () {
    checkResize();
    $image.css('opacity', 1);
    $container.find('.o_loading_img').remove();
    clearInterval(intervalId)
});

window.addEventListener('resize', checkResize, false);
// Add function to execute every 1000ms to display the image when is loaded
var intervalId = window.setInterval(function(){
    if ($image[0].complete === true) {
        checkResize();
        $image.css('opacity', 1);
        $container.find('.o_loading_img').remove();
        clearInterval(intervalId)
    }
}, 1000);
});
