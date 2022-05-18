$(document).ready(function() {
  var list = $(".main-div");
  var numToShow = 10;
  var button = $(".button-show-more");
  var numInList = list.length;
  list.hide();
  if (numInList <= numToShow) {
    button.hide();
  }
  list.slice(0, numToShow).show();
  button.click(function() {
    var showing = list.filter(':visible').length;
    list.slice(showing - 1, showing + numToShow).fadeIn();
    var lastComment = list.last();
    if (lastComment.css("display") === "block") {
      button.hide();
    }
  });
});
