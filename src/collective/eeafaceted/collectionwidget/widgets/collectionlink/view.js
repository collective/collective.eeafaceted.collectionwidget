/* override the tag_click function to reset every advanced criteria when changing selected collection */
Faceted.TagsCloudWidget.prototype.tag_click =
  function(tag, evt){
    /* Added by collective.eeafaceted.collectionwidget */
    /* clear every criteria when selecting another collection in the collectionwidget */
    clearCriteria(tag);

    /* hide the advanced criteria */
    /* Faceted.Sections.advanced.hide("fast"); */

    /* Here we could set arbitrarilly criteria, for example : Faceted.Query['c1'] = ["private"]; */
    showRelevantAdvancedCriteria(tag);

    /* Update current page title */
    updatePageTitle(tag);

    /* do the query, default in eea.facetednavigation */
    this.do_query(tag);
  }

/* override the count method so it is not applied or it unselect currently selected item??? */
Faceted.TagsCloudWidget.prototype.count =
  function(tag, evt){ }

/* we should not be able to unselect a selected element, just be able to select another one */
Faceted.TagsCloudWidget.prototype.do_query =
  function(tag, evt){
    var value=jQuery(tag).attr('id').replace(this.wid, '');
    value = value.replace(/_-_/g, ' ');
    var selected_value = '';
    if(this.selected.length){
      selected_value = jQuery(this.selected[0]).attr('id').replace(this.wid, '');
      selected_value = selected_value.replace(/_-_/g, ' ');
    }
    if(value == selected_value){
      /* XXX begin addition */
      /* comment 2 lines that are unselecting already selected element */
      /* this.select(jQuery('#' + this.wid + 'all', this.widget)); */
      /* value = []; */
      /* XXX end addition */
    }else{
      this.select(tag);
    }
    Faceted.Form.do_query(this.wid, value);
  }

/* if user go immediately on a search using saved URL, make sure relevant advanced search criteria are hidden */
Faceted.TagsCloudWidget.prototype.update =
  function(tag, evt){
    /* XXX begin addition */
    /* get selected collection from url if any because at this stage, it is still the default element that is selected */
    url = window.location.toString()
    var queryString = url.substring( url.indexOf('#') + 1 );
    parameters = $.getQueryParameters(queryString);
    if (parameters[this.wid]) {
      /* get the tag and proceed */
      var selected = $('li#'+this.wid+parameters[this.wid]);
      showRelevantAdvancedCriteria(selected);
      updatePageTitle(selected);
    }
    else {
      updatePageTitle($('.faceted-tag-selected', tag)[0]);
    }

    /* XXX end addition */
    jQuery('#' + this.wid, this.widget).tagcloud(this.config);
  }

/* clear every advanced criteria by removing it from Faceted.Query */
clearAdvancedCriteria = function(tag) {
  advancedCriteria = jQuery(tag).parent().data()['advancedCriteria'];
  $.each(Faceted.Query,
         function(k, v){
          if (advancedCriteria.indexOf(k) != -1) {
            delete Faceted.Query[k];
            };
         })
}

/* clear every criteria by removing it from Faceted.Query but keep some elements */
clearCriteria = function(tag) {
  /* the criterion type is found by evaluating the class applied on the widget... */
  var keptCriteriaClasses = ['faceted-resultsperpage-widget', ];
  $.each(Faceted.Query,
         function(k, v){
          found = false;
          $.each(keptCriteriaClasses,
                 function(index, css_class) {
            if (Faceted.Widgets[k] && Faceted.Widgets[k].widget.attr('class').indexOf(css_class) != -1) {
              found = true;
            };
            if (!found) {
              delete Faceted.Query[k];
            };
            found = false;
        });
});
}

/* only show advanced criteria that are not managed by selected collection */
showRelevantAdvancedCriteria = function(tag) {
  keptCriteria = jQuery(tag).data()['keptCriteria']
  advancedCriteria = jQuery(tag).parent().data()['advancedCriteria']
  /* hide every advanced criteria */
  $.each(advancedCriteria, function(k, criterion_id) {
    $('div#'+criterion_id+'_widget').hide();
  })
  /* show kept criteria */
  $.each(keptCriteria, function(k, criterion_id) {
    $('div#'+criterion_id+'_widget').show();
  })
}

updatePageTitle = function(tag) {
  currentTitleTag = $('#content h1.documentFirstHeading')[0];
  currentTitleTag.innerHTML = $('a', tag)[0].innerHTML;
}

/* method for parsing query parameters */
jQuery.extend({
  getQueryParameters : function(str) {
    return (str || document.location.search).replace(/(^\?)/,'').split("&").map(function(n){
      return n = n.split("="),
      ( !this[n[0]] ? this[n[0]] = n[1] : ((typeof this[n[0]] === 'object') ? this[n[0]].push(n[1]) : this[n[0]]=[this[n[0]], n[1]]) ),
      this
    }.bind({}))[0];
  }
});