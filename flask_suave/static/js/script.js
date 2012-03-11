var remove_flash = function(flash, duration) {
    /**
     * Hide a flash.
     */
    if(duration == undefined) {
        duration = 500;
    };
    flash.stop(true, true).animate({left: '100%', 'margin-left': '20px'}, duration, function() {
        flash.remove();
        fade_first_flash();
    });
}

var fade_first_flash = function() {
    /**
     * Hide the first flash then call the next one.
     */
    $('ul.flashes li:first-child').animate({display: 'block'}, 3000, function() {
        remove_flash($(this));
    });
}

var string_to_slug = function(str) {
  str = str.replace(/^\s+|\s+$/g, ''); // trim
  str = str.toLowerCase();
  
  // remove accents, swap ñ for n, etc
  var from = "àáäâèéëêìíïîòóöôùúüûñç·/_,:;";
  var to   = "aaaaeeeeiiiioooouuuunc------";
  for (var i=0, l=from.length ; i<l ; i++) {
    str = str.replace(new RegExp(from.charAt(i), 'g'), to.charAt(i));
  }

  str = str.replace(/[^a-z0-9 -]/g, '') // remove invalid chars
    .replace(/\s+/g, '-') // collapse whitespace and replace by -
    .replace(/-+/g, '-'); // collapse dashes

  return str;
}

var generate_page_list = function(current_page, number_pages) {
    string = '<ul class="pagination">';
    for(i=1; i<= number_pages; i++) {
        if(i == current_page) {
            selected = ' class="selected"';
        } else {
            selected = '';
        }
        string += '<li' + selected + '><a href="#">' + i + '</a></li>';
    }
    string += '</ul>';
    return string;
}
var populate_table = function(table) {
    /**
     * Populate a table with articles.
     */

    var status = table.attr('status');
    var filter = table.attr('filter');
    var page = table.attr('page');
    var url = table.attr('url');
    var cols = $('tr.header th', table).length;
    if(status == undefined) {
        status = 'any';
    }
    if(page == undefined) {
        page = 1;
    }

    var per_page = 20;

    var d = {
        page: page,
        status: status,
        per_page: per_page
    };
    if(filter != undefined) {
        d['filter'] = filter;
    }
    $.getJSON(url, d, function(data) {
        if(data['num_pages'] < page && data['num_pages'] != 0) {
            table.attr('page', data['num_pages']);
            return populate_table(table)
        }
        $('tr', table).each(function() {
            tr = $(this);
            if(!tr.hasClass('header')) {
                tr.remove();
            }
        });
        for(a in data['items']) {
            a = data['items'][a];
            tr = ich.table_row(a);
            table.append(tr);
        }
        if(data['num_pages'] > 1) {
            var foot = '<tr class="footer"><td colspan="' + cols + '"></td></tr>';
            table.append(foot);
            list = generate_page_list(table.attr('page'), data['num_pages']);
            foot_html = list + '<span>Showing ' + per_page + ' results per page...</span>';
        $('tr.footer td', table).html(foot_html);
        }
    });
}

var populate_tables = function() {
    $('table.js-pop').each(function() {
        populate_table($(this));
    });
}
$(function() {
    // Table population filtering and pagination.
    $('nav').on('keyup', '#filter', function() {
        filter = $(this).val();
        $('table.js-pop').attr('filter', filter);
        populate_tables();
    });
    $('table.js-pop').on('click', 'ul.pagination a', function(event) {
        event.preventDefault();
        page = $(this).text();
        table = $(this).closest('table.js-pop');
        table.attr('page', page);
        populate_table(table);
    })
});
$(function() {
    // Slug autogeneration
    if($('input#slug').val() == '') {
        $('input#slug').attr('auto', 'auto');
    }
    $('input#title').on('keyup', function() {
        if($('input#slug').attr('auto') == 'auto') {
            $('input#slug').val(string_to_slug($(this).val()));
        };
    });

    $('input#slug').on('change', function() {
        $('input#slug').attr('auto', 'no');
    });
});

$(function() {
    // Slowly disappear the flashes
    fade_first_flash();
    $('ul.flashes li').on('click', function() {
        remove_flash($(this), 200);
    })
});

$(function() {
    // Full row selection
    $('table tr').on('click', function() {
        if($(this).hasClass('selected')) {
            $(this).removeClass('selected')
        } else if(!$(this).hasClass('header')) {
            $(this).addClass('selected');
        }
    });

    $('h2').on('click', function() {
        $(this).animate({
            height: '200px'
        });
    })
});


$(function() {
    // Advanced / Basic form hiding parts.
    $('fieldset.advanced').before('<a href="#" class="advanced_hider">Advanced +</a>');
    $('fieldset.advanced').hide();
    $('a.advanced_hider').on('click', function(event) {
        event.preventDefault();
        t = $(this);
        if($(this).attr('vis') == 'shown') {
            t.next().slideToggle();
            t.attr('vis', 'hidden');
            t.text('Advanced +');
        } else {
            t.next().slideToggle();
            t.attr('vis', 'shown');
            t.text('Advanced -');          
        }
    });
});