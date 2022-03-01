
function searchBySongsCheckBox() {
    var checkbox = document.getElementById('search-by-songs-checkbox');
    var searchTextInput = document.getElementById('search-text-input');

    if (checkbox.checked == true) {
        searchTextInput.placeholder = 'Search by Song';
    }
    else {
        searchTextInput.placeholder = 'Search by Song Lyrics';
    }
    
    console.log()
}