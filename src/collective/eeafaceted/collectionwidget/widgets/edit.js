FacetedEdit.TagsCloudCollectionWidget = function(wid) {
  FacetedEdit.TagsCloudWidget.call(this, wid);
}
FacetedEdit.TagsCloudCollectionWidget.prototype = Object.create( FacetedEdit.TagsCloudWidget.prototype );
FacetedEdit.TagsCloudCollectionWidget.prototype.constructor = FacetedEdit.TagsCloudCollectionWidget;

FacetedEdit.initializeTagsCloudCollectionWidget = function(evt){
  jQuery('div.faceted-tagscloud-collection-widget').each(function(){
    var wid = jQuery(this).attr('id');
    wid = wid.split('_')[0];
    FacetedEdit.Widgets[wid] = new FacetedEdit.TagsCloudCollectionWidget(wid);
  });
};

jQuery(document).ready(function(){
  jQuery(FacetedEdit.Events).bind(
    FacetedEdit.Events.INITIALIZE_WIDGETS,
    FacetedEdit.initializeTagsCloudCollectionWidget);
});
