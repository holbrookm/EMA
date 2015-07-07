//
$("#dialog-message").dialog({
    modal: true,
    draggable: false,
    resizable: false,
    position: ['center', 'top'],
    show: 'blind',
    hide: 'blind',
    width: 250,
    height: 250,
    dialogClass: 'ui-dialog-osx',
    buttons: {
        "I've read and understand this": function() {
            $(this).dialog("close");
        }
    }
});
