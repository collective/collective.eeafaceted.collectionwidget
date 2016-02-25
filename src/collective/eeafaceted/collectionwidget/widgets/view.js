Faceted.TagsCloudCollectionWidget = function(wid) {
  Faceted.TagsCloudWidget.call(this, wid);
}
Faceted.TagsCloudCollectionWidget.prototype = Object.create( Faceted.TagsCloudWidget.prototype );
Faceted.TagsCloudCollectionWidget.prototype.constructor = Faceted.TagsCloudCollectionWidget;

/* override the tag_click function to reset every advanced criteria when changing selected collection */
Faceted.TagsCloudCollectionWidget.prototype.tag_click =
  function(tag, evt){
    /* redirect if contained <a> href is not javascript:; */
    href = $('a', tag)[0].href;
    if (href != 'javascript:;' ) {
      window.location.href = href;
      return
    }
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
Faceted.TagsCloudCollectionWidget.prototype.count =
  function(tag, evt){ }

/* override reset method to unselect all tags, and not try to select a 'all'
 * option that is not visible in our case */
Faceted.TagsCloudCollectionWidget.prototype.reset = function() { this.unselect(this.tags) }

/* we should not be able to unselect a selected element, just be able to select another one */
Faceted.TagsCloudCollectionWidget.prototype.do_query =
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
Faceted.TagsCloudCollectionWidget.prototype.update =
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
    else {  // executed on initialization
      var selected = $('#'+this.wid+'_widget li.faceted-tag-selected');
      if (selected.length) {  // do nothing if there is no default
        showRelevantAdvancedCriteria(selected);
        updatePageTitle(selected);
      }
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
          keepit = false;
          $.each(keptCriteriaClasses,
                 function(index, css_class) {
            /* if we find a widget using one of the keptCriteriaClasses, we keep it */
            if (Faceted.Widgets[k] && Faceted.Widgets[k].widget.attr('class').indexOf(css_class) != -1) {
              keepit = true;
            };
            if (!keepit) {
              delete Faceted.Query[k];
            };
            keepit = false;
        });
});
}

/* only show advanced criteria that are not managed by selected collection */
showRelevantAdvancedCriteria = function(tag) {
  keptCriteria = jQuery(tag).data()['keptCriteria']
  advancedCriteria = jQuery(tag).parent().data()['advancedCriteria']
  /* disable checkboxes base on kept criteria */
  $.each(keptCriteria, function(criterion_id, enabled_checkboxes) {
    var available_checkboxes = $('#'+criterion_id+'_widget input');
    // set selected items for the criterion
    Faceted.Query[criterion_id] = enabled_checkboxes;
    available_checkboxes.each(function(idx, checkbox) {
        var $checkbox = $(checkbox);
        if ($.inArray($checkbox.attr('value'), enabled_checkboxes) > -1) {
            $checkbox.prop('checked', true);
            $checkbox.prop('disabled', false);
        } else {
            // only disable if enabled_checkboxes is not empty
            if (enabled_checkboxes.length) {
              $checkbox.prop('disabled', true);
            } else {
              $checkbox.prop('disabled', false);
            }
        }
    });
  });
  // Faceted will rerender the criterion with the checkboxes checked after that
}

updatePageTitle = function(tag) {
  var currentTitleTag = $('#content h1.documentFirstHeading')[0];
  var label = $('a .term-label', tag);
  if (label.length) {
    currentTitleTag.innerHTML = label[0].innerHTML;
  }
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

Faceted.initializeTagsCloudCollectionWidget = function(evt){
  jQuery('div.faceted-tagscloud-collection-widget').each(function(){
    var wid = jQuery(this).attr('id');
    wid = wid.split('_')[0];
    Faceted.Widgets[wid] = new Faceted.TagsCloudCollectionWidget(wid);
  });
};

jQuery(document).ready(function(){
  jQuery(Faceted.Events).bind(
    Faceted.Events.INITIALIZE,
    Faceted.initializeTagsCloudCollectionWidget);
});
