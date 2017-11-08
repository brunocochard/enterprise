/*!
 * Start Bootstrap - SB Admin 2 v3.3.7+1 (http://startbootstrap.com/template-overviews/sb-admin-2)
 * Copyright 2013-2016 Start Bootstrap
 * Licensed under MIT (https://github.com/BlackrockDigital/startbootstrap/blob/gh-pages/LICENSE)
 */
$(function() {
    $('#side-menu').metisMenu();
});

$(function() {

    var substringMatcher = function(strs) {
      return function findMatches(q, cb) {
        var matches, substringRegex;
        matches = [];
        substrRegex = new RegExp(q, 'i');
        $.each(strs, function(i, str) {
          if (substrRegex.test(str)) { matches.push(str); }
        });
        cb(matches);
      };
    };

    var applicationServices = ['Channel > Mobile >  Koko > EBTNTB2C05', 
      'Credit Card > Application >  CRD-NT-USE-13', 
      'Credit Card > Application >  CRD-NT-CAP-01'
    ];

    $('#APNewRequest').typeahead({
      hint: true,
      highlight: true,
      minLength: 1
    }, {
      name: 'APNewRequest',
      source: substringMatcher(applicationServices)
    });

    $('#APNewChange').typeahead({
      hint: true,
      highlight: true,
      minLength: 1
    }, {
      name: 'APNewChange',
      source: substringMatcher(applicationServices)
    });

    $('#APNewIncident').typeahead({
      hint: true,
      highlight: true,
      minLength: 1
    }, {
      name: 'APNewIncident',
      source: substringMatcher(applicationServices)
    });

    var currentServiceRequest = [
      'MyBank > 0009710609063 > 配合AML上線，增加外匯匯出匯款說明文字', 
      'MyBank > 0009710609064 > 調整臺幣定存解約可於非營業日執行', 
      'MyBank > 0040010607053 > 信託開戶PEPS檢核改為檢核customer hub',
      'Credit Card > 0008810609054 > EPOS 特店回傳卡號',
      'Credit Card > 0009310609038 > 調整AML送查欄位規則 & 基本檢核內容'
    ];

    $('#currentServiceRequest').typeahead({
      hint: true,
      highlight: true,
      minLength: 1
    }, {
      name: 'currentServiceRequest',
      source: substringMatcher(currentServiceRequest)
    });

    $('#chasedServiceRequest').typeahead({
      hint: true,
      highlight: true,
      minLength: 1
    }, {
      name: 'chasedServiceRequest',
      source: substringMatcher(currentServiceRequest)
    });
});




//Loads the correct sidebar on window load,
//collapses the sidebar on window resize.
// Sets the min-height of #page-wrapper to window size
$(function() {
    $(window).bind("load resize", function() {
        var topOffset = 50;
        var width = (this.window.innerWidth > 0) ? this.window.innerWidth : this.screen.width;
        if (width < 768) {
            $('div.navbar-collapse').addClass('collapse');
            topOffset = 100; // 2-row-menu
        } else {
            $('div.navbar-collapse').removeClass('collapse');
        }

        var height = ((this.window.innerHeight > 0) ? this.window.innerHeight : this.screen.height) - 1;
        height = height - topOffset;
        if (height < 1) height = 1;
        if (height > topOffset) {
            $("#page-wrapper").css("min-height", (height) + "px");
        }
    });

    var url = window.location;
    // var element = $('ul.nav a').filter(function() {
    //     return this.href == url;
    // }).addClass('active').parent().parent().addClass('in').parent();
    var element = $('ul.nav a').filter(function() {
        return this.href == url;
    }).addClass('active').parent();

    while (true) {
        if (element.is('li')) {
            element = element.parent().addClass('in').parent();
        } else {
            break;
        }
    }
});
