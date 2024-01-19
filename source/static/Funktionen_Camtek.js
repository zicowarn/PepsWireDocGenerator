function onImgLoad(item) {
        if (item.mwIsInitialized === undefined) 
        {
                item.mwIsInitialized = true;
                item.mwImgSrc = item.src;
                item.mwPreviewSrc = '../preview.jpg';
                item.mwIsPreview = true;
                item.src = item.mwPreviewSrc;
        }
}

function onImgClick(item) {
        item.mwIsPreview = !item.mwIsPreview;
    if (item.mwIsPreview) {
                item.src = item.mwPreviewSrc;
    }
        else {
                item.src = item.mwImgSrc;
        }
}