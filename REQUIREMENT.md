# REQUIREMENT: sauravshah.com.np
* A site for personal blog
* Minimalist design, like a book, the fonts should also be very appealing to read, the background should be appealing like a book
* Option to toggler between night mode
* Option to enable reading mode, like warm light thing


### Basic layout
* This is a basic layout design, not ui/ux or any design inspiration to take from, just a rough idea

#### Home Page
* The homepage should contain the header, displaying my name, some intro and social links icons and a photo at the right
* Below that should be like a book table of contents, with links to the pages. This TOC is like high level contents topics like Treks, ...
![Homepage](./.data/MacBook%20Pro%2014_%20-%201.jpg)

#### Link Page
* Once the link in home page is clicked, it will redirect to another page, which can be another Table of Content or the content / blog itself
* This will also contain the title, some intro and some social links, which can be mine or another links. To the right, the photo section can be like a slideshow section displaying different photos, or just one photo is the slideshow contains only one photo. Dont put any option to view previous or next photo, just default timer based slideshow
* Below section can contain other links, which can redirect to another link or the content itself
![Link Page](./.data/MacBook%20Pro%2014_%20-%202.jpg)

#### Content Page
* Once a link to content page is clieked, a content page opens with title, some intro and social links. The slideshow design will exists here also
* Below section will contsin contents
* In the content, text, quotes, emojis, sldeshows, links, videos, photos, shorts, etc anything can be added
* it should support both english and nepali text
![Content Page](./.data/MacBook%20Pro%2014_%20-%203.jpg)

## Folder structure
```
|- content (folder which i update locally)
|--- Title1 (Index title for homepage)
|------ Title1 subtitle1 (Index title for title1 page)
|------------content.md (or some other format where i write the content)
|------------.data  (folder where data like videos, photos, etc are put)
|------ Title1 subtitle2
|--- Title2
|-----content.md
|-----.data
|--- Title3
|- site (folder where final static site is generated)
|- deploy.py (script to generate static site under folder site from contents of folder content)
```
* deloy.py script will create the required html files under site and this folder "site" is to be deployed as static site