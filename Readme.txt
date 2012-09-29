
Pyepub converts text based files into Epub3 books. It's primarly designed for iBooks but is Epub3 compliant
After creating ebub with this script it can be automatically checked against epub3check if it is available on your system.

The 1st character of each line determines the processing that occurs (more on this later)
So with a minimum amount of effort a text file can be converted into an Epub

In addition to the main text file, you need to setup a configuration file typically called pyepub.cfg. There is an example in the example directory. Some configuration parameters are general while others are book specific

There are 2 python scripts. 1 which has everything required (epub3_utils.py) and 1 which use a GUI (pyepub.py)
pyepub.py requires some python packages: simplejson, PySide and PyQt. The latter two need to be downloaded from (http://qt-project.org/wiki/PySideDownloads). simplejson can be installed by 'pip' or 'easy_install'

The configuration file has 3 sections;
1) mostly ebook meta-data
2) and 3) config/setup book
These correspond to 3 GUI pages.
Some items in 2) are paired with items in 3)
For example if you put "y'" for 'use_biblio' then in filemap there needs to be an entry for 'biblio'
GUI will take care of this in page 2 for you to ensure integrity, but there is still some interdepence between items

The main options are
    1) Read in a bibliography and format as a page. This also contains abbreviations for some book
    2) Add a list of abbreviations based on 1)
    3) Add an index
    4) index based on People or Place names
    5) index based on references for Biblical or Koranic verses of form such as (IV:4) , i.e Roman Chapter:Verse
    6) A page that list contents sorted alphabetical
    7) Alphabetical contents based on alternate language in parenthesis
    8) A page with list of figures
    9) A page with list of tables.

"lev_toc" : Heading levels at this or lower will go into main Table of Contents
"lev_break": Heading levels at this or above will cause page break and start processing in new xhtml file
"enough_lines": If this many lines reached, force new xhtml file.
Last 2 options avoid having xhtml files too large which was a problem in some ereaders.

In addition to obvious text file names, you can either use default generated css or attach your own. Get familar with default before attempting to change as it determines look of book completely.

Example config file
-----------------------

{
 "config": [
{
"title":"Mixed Book - draft",
"author":"Anonymous",
"creator":"",
"language":"en",
"publisher": "EPUB",
"published": "2012",
"design":"",
"translators":"None",
"cover design":"",
"cover photo":"",
"copyright":"2012",
"subject":"Non-Fiction",
"date":"2010",
"revision":"",
"description":"TBD",
"isbn":" 09-002170-22",
"web": "<a href=\"http://www.yahoo.com/\">www.yahoo.com</a>",
"rights":"All rights reserved. No part of this publication may be reproduced, stored in a retrieval system, or transmitted in any form or by any means, electronic, mechanical photocopying, recording, or otherwise, without prior permission of the copyright owner."
},
  {
   "enough_lines": "500",
   "keep_efiles": "y",
   "lev_break": "2",
   "lev_toc": "2",
   "sample": "",
   "unicode": "y",
   "use_abbrev": "y",
   "use_biblio": "y",
   "use_figures": "y",
   "use_footnotes": "y",
   "use_italics": "y",
   "use_nameref": "y",
   "use_bookref": "y",
   "use_romanref": "y",
   "use_sorted_toc": "y",
   "use_sorted_unicode": "y",
   "use_wordref": "y"
  },
  {
   "biblio": "biblio.txt",
   "css": "",
   "filemap": [
    "title",
    "main",
	"abbrev",
	"biblio",
	"nameref",
	"wordref",
	"romanref",
	"sorted_toc",
	"sorted_unicode",
	"figures",
	"tables"
   ],
   "footnotes": "footnotes.txt",
   "headings": "headings.txt",
   "input": "example.txt",
   "nameref": "index_names.txt",
   "output": "example.epub",
   "wordref": "index_words.txt"
  }
 ]
}

----------
File format


this is the file format........
First char of line : Meaning .......
char     Paragraph type
TAB      indent 1st character
TAB+TAB  indent whole paragraph
{...}    Poem
%       Poem
{{..}}   same as poem for now......
u'—'     Poet
u'—'(...     Book Abbreviation
\.../    Figure. Slashes are on separate lines
|..|..|  Table
<[0-9]>  heading type
<c>      Center line
*        Italic line
+        Page break
†        Footnote. Also place † almost anywhere in text
!...}    Poem for text that goes right-to-left
"""
