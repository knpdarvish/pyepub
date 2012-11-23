#!/usr/bin/python
# -*- coding: utf-8 -*-
#
import re,sys,fileinput
import operator
import commands
import string
import os
import shutil
import zipfile
import glob
import json
import datetime
import codecs
import unicodedata
import uuid

start_blue = '\033[34m'
start_red = '\033[31m'
start_bold_red = '\033[31;1m'
end_color = '\033[0;0m'
#

ver_type_ascii = "This version may not have the correct characters from that used in original print book and has been changed to be readable by various software programs and devices. "


def use_ascii():
	global full_unicode
	global ver_type
	full_unicode = 0
	ver_type = ver_type_ascii

# get ext
ext = re.compile('\.\w+')
the = re.compile('(The )|(THE )')
indef = re.compile('(a )|(A )')
auth = re.compile('Author:')
reg  = re.compile('^<\w')
ireg  = re.compile('(<[a-z]+>)|(</[a-z]+>)')
unhtml  = re.compile('(<[^<]+>)')
wreg = re.compile(ur'(^\w)|(^\")|(^\')|(^\‘)',re.UNICODE)
#wreg = re.compile(ur'^\‘',re.UNICODE)
# Start of line expressions
preg = re.compile('^{')     # start poem
freg = re.compile('^!')     # start farsi poem
ereg = re.compile('^}')     # end poem
spreg =  re.compile(ur"^\+") # page break
sfreg =  re.compile(ur"^†") # footnote
csreg = re.compile(ur"\\")  # start figure
cereg = re.compile(ur"/")   # end figure
atreg = re.compile(ur"—|-")   # poet
atreg1 = re.compile(ur"—")   # poet
tblreg = re.compile(ur"\|") # table
astreg = re.compile(ur"\*") # italic line
npreg  = re.compile(ur"^%") # new -> poem
tempsub = ur"‡"
dagger  = ur"†"
frefs     = re.compile(ur'†',re.UNICODE)
#frefs     = re.compile(r'(\$[0-9]+\$)|(\$\$)') - older $ $
#cnt  = re.compile('^<c>') # for marking content insertion place
start_2tab  = re.compile('^\t\t')
start_tab  = re.compile('^\t')
start_space  = re.compile('^\s')
leading_spaces = re.compile('\s')
blank_line = re.compile('^$')

# for arabic phrases
aphrases = re.compile(r'\((.+)\)',re.UNICODE)
amprefs     = re.compile(r'\&')
# to remove paren
pw   = re.compile('\(|\)',re.UNICODE)
end_apos   = re.compile("\'$",re.UNICODE)
end_poss   = re.compile("\'s$",re.UNICODE)
end_angle_br   = re.compile("<$|>$",re.UNICODE)
starting_apos   = re.compile("^\'",re.UNICODE)
boundary_apos   = re.compile("(^\')|(\'$)",re.UNICODE)
fpar = re.compile('\(')
# for book refs
book_refs1     = re.compile(r'\"ref\">\(([A-Z]+)\)')
book_refs2     = re.compile(r'\(([A-Z]+)\s([\-,0-9]+)\)')
book_refs3     = re.compile(r'\(([A-Z]+)\s([A-Z]+)\s([,\-0-9]+)\)')
# base element of reference
brefs    = re.compile(r'[A-Z]+')
nrefs    = re.compile(r'([0-9]+)\.')
#krefs     = re.compile(r'\([:\-A-Z 0-9]+\)')
krefs     = re.compile(r'\([A-Z]+:[ 0-9]+\)')
crefs     = re.compile(':')

title_clean   = re.compile(ur'’|‘|"|\?|:',re.UNICODE)
allbrefs     = re.compile(r'\([:\-A-Za-z 0-9]+\)')

start_paren = re.compile(r'\(',re.UNICODE)

# used in htmlize_index & old_phrases
####fphrases = re.compile(ur"\([\w'-’‘]+\)",re.UNICODE)
fphrases = re.compile(ur"\([-,'’‘\w ]+\)",re.UNICODE)
# used in htmlize_index
wphrases = re.compile(ur"\([\w’‘]+\)",re.UNICODE)

# set to enable various debug print statements
debug_option = False
debug_parse = False
debug_break = False
debug_toc = False

# if having issues with this, set "extra_text" to None and download http://www.unicode.org/Public/UCA/latest/allkeys.txt and include in same directory as this script
extra_text = """\
0000  ; [.0000.0000.0000.0000] # [0000] NULL (in 6429)
0001  ; [.0000.0000.0000.0000] # [0001] START OF HEADING (in 6429)
0002  ; [.0000.0000.0000.0000] # [0002] START OF TEXT (in 6429)
0003  ; [.0000.0000.0000.0000] # [0003] END OF TEXT (in 6429)
0004  ; [.0000.0000.0000.0000] # [0004] END OF TRANSMISSION (in 6429)
0005  ; [.0000.0000.0000.0000] # [0005] ENQUIRY (in 6429)
0006  ; [.0000.0000.0000.0000] # [0006] ACKNOWLEDGE (in 6429)
0007  ; [.0000.0000.0000.0000] # [0007] BELL (in 6429)
0008  ; [.0000.0000.0000.0000] # [0008] BACKSPACE (in 6429)
0009  ; [*0201.0020.0002.0009] # HORIZONTAL TABULATION (in 6429)
000A  ; [*0202.0020.0002.000A] # LINE FEED (in 6429)
000B  ; [*0203.0020.0002.000B] # VERTICAL TABULATION (in 6429)
000C  ; [*0204.0020.0002.000C] # FORM FEED (in 6429)
000D  ; [*0205.0020.0002.000D] # CARRIAGE RETURN (in 6429)
000E  ; [.0000.0000.0000.0000] # [000E] SHIFT OUT (in 6429)
000F  ; [.0000.0000.0000.0000] # [000F] SHIFT IN (in 6429)
0010  ; [.0000.0000.0000.0000] # [0010] DATA LINK ESCAPE (in 6429)
0011  ; [.0000.0000.0000.0000] # [0011] DEVICE CONTROL ONE (in 6429)
0012  ; [.0000.0000.0000.0000] # [0012] DEVICE CONTROL TWO (in 6429)
0013  ; [.0000.0000.0000.0000] # [0013] DEVICE CONTROL THREE (in 6429)
0014  ; [.0000.0000.0000.0000] # [0014] DEVICE CONTROL FOUR (in 6429)
0015  ; [.0000.0000.0000.0000] # [0015] NEGATIVE ACKNOWLEDGE (in 6429)
0016  ; [.0000.0000.0000.0000] # [0016] SYNCHRONOUS IDLE (in 6429)
0017  ; [.0000.0000.0000.0000] # [0017] END OF TRANSMISSION BLOCK (in 6429)
0018  ; [.0000.0000.0000.0000] # [0018] CANCEL (in 6429)
0019  ; [.0000.0000.0000.0000] # [0019] END OF MEDIUM (in 6429)
001A  ; [.0000.0000.0000.0000] # [001A] SUBSTITUTE (in 6429)
001B  ; [.0000.0000.0000.0000] # [001B] ESCAPE (in 6429)
001C  ; [.0000.0000.0000.0000] # [001C] FILE SEPARATOR (in 6429)
001D  ; [.0000.0000.0000.0000] # [001D] GROUP SEPARATOR (in 6429)
001E  ; [.0000.0000.0000.0000] # [001E] RECORD SEPARATOR (in 6429)
001F  ; [.0000.0000.0000.0000] # [001F] UNIT SEPARATOR (in 6429)
0020  ; [*020A.0020.0002.0020] # SPACE
0021  ; [*026E.0020.0002.0021] # EXCLAMATION MARK
0022  ; [*02F5.0020.0002.0022] # QUOTATION MARK
0023  ; [*0362.0020.0002.0023] # NUMBER SIGN
0024  ; [.11E1.0020.0002.0024] # DOLLAR SIGN
0025  ; [*0363.0020.0002.0025] # PERCENT SIGN
0026  ; [*035F.0020.0002.0026] # AMPERSAND
0027  ; [*02EE.0020.0002.0027] # APOSTROPHE
0028  ; [*02FF.0020.0002.0028] # LEFT PARENTHESIS
0029  ; [*0300.0020.0002.0029] # RIGHT PARENTHESIS
002A  ; [*0357.0020.0002.002A] # ASTERISK
002B  ; [*0550.0020.0002.002B] # PLUS SIGN
002C  ; [*0234.0020.0002.002C] # COMMA
002D  ; [*0223.0020.0002.002D] # HYPHEN-MINUS
002E  ; [*0281.0020.0002.002E] # FULL STOP
002F  ; [*035C.0020.0002.002F] # SOLIDUS
0030  ; [.1205.0020.0002.0030] # DIGIT ZERO
0031  ; [.1206.0020.0002.0031] # DIGIT ONE
0032  ; [.1207.0020.0002.0032] # DIGIT TWO
0033  ; [.1208.0020.0002.0033] # DIGIT THREE
0034  ; [.1209.0020.0002.0034] # DIGIT FOUR
0035  ; [.120A.0020.0002.0035] # DIGIT FIVE
0036  ; [.120B.0020.0002.0036] # DIGIT SIX
0037  ; [.120C.0020.0002.0037] # DIGIT SEVEN
0038  ; [.120D.0020.0002.0038] # DIGIT EIGHT
0039  ; [.120E.0020.0002.0039] # DIGIT NINE
003A  ; [*0247.0020.0002.003A] # COLON
003B  ; [*0243.0020.0002.003B] # SEMICOLON
003C  ; [*0554.0020.0002.003C] # LESS-THAN SIGN
003D  ; [*0555.0020.0002.003D] # EQUALS SIGN
003E  ; [*0556.0020.0002.003E] # GREATER-THAN SIGN
003F  ; [*0273.0020.0002.003F] # QUESTION MARK
0040  ; [*0356.0020.0002.0040] # COMMERCIAL AT
0041  ; [.120F.0020.0008.0041] # LATIN CAPITAL LETTER A
0100  ; [.120F.0020.0008.0041][.0000.005B.0002.0304] # LATIN CAPITAL LETTER A WITH MACRON; QQCM
0042  ; [.1225.0020.0008.0042] # LATIN CAPITAL LETTER B
0043  ; [.123D.0020.0008.0043] # LATIN CAPITAL LETTER C
0044  ; [.1250.0020.0008.0044] # LATIN CAPITAL LETTER D
1E0C  ; [.1250.0020.0008.0044][.0000.0070.0002.0323] # LATIN CAPITAL LETTER D WITH DOT BELOW; QQCM
0045  ; [.126B.0020.0008.0045] # LATIN CAPITAL LETTER E
0046  ; [.12A3.0020.0008.0046] # LATIN CAPITAL LETTER F
0047  ; [.12B0.0020.0008.0047] # LATIN CAPITAL LETTER G
0048  ; [.12D3.0020.0008.0048] # LATIN CAPITAL LETTER H
1E24  ; [.12D3.0020.0008.0048][.0000.0070.0002.0323] # LATIN CAPITAL LETTER H WITH DOT BELOW; QQCM
0049  ; [.12EC.0020.0008.0049] # LATIN CAPITAL LETTER I
012A  ; [.12EC.0020.0008.0049][.0000.005B.0002.0304] # LATIN CAPITAL LETTER I WITH MACRON; QQCM
004A  ; [.1305.0020.0008.004A] # LATIN CAPITAL LETTER J
004B  ; [.131E.0020.0008.004B] # LATIN CAPITAL LETTER K
004C  ; [.1330.0020.0008.004C] # LATIN CAPITAL LETTER L
004D  ; [.135F.0020.0008.004D] # LATIN CAPITAL LETTER M
004E  ; [.136D.0020.0008.004E] # LATIN CAPITAL LETTER N
004F  ; [.138E.0020.0008.004F] # LATIN CAPITAL LETTER O
0050  ; [.13B3.0020.0008.0050] # LATIN CAPITAL LETTER P
0051  ; [.13C8.0020.0008.0051] # LATIN CAPITAL LETTER Q
0052  ; [.13DA.0020.0008.0052] # LATIN CAPITAL LETTER R
0053  ; [.1410.0020.0008.0053] # LATIN CAPITAL LETTER S
1E62  ; [.1410.0020.0008.0053][.0000.0070.0002.0323] # LATIN CAPITAL LETTER S WITH DOT BELOW; QQCM
0054  ; [.1433.0020.0008.0054] # LATIN CAPITAL LETTER T
1E6C  ; [.1433.0020.0008.0054][.0000.0070.0002.0323] # LATIN CAPITAL LETTER T WITH DOT BELOW; QQCM
0055  ; [.1453.0020.0008.0055] # LATIN CAPITAL LETTER U
016A  ; [.1453.0020.0008.0055][.0000.005B.0002.0304] # LATIN CAPITAL LETTER U WITH MACRON; QQCM
0056  ; [.147B.0020.0008.0056] # LATIN CAPITAL LETTER V
0057  ; [.148D.0020.0008.0057] # LATIN CAPITAL LETTER W
0058  ; [.1497.0020.0008.0058] # LATIN CAPITAL LETTER X
0059  ; [.149C.0020.0008.0059] # LATIN CAPITAL LETTER Y
005A  ; [.14AD.0020.0008.005A] # LATIN CAPITAL LETTER Z
1E92  ; [.14AD.0020.0008.005A][.0000.0070.0002.0323] # LATIN CAPITAL LETTER Z WITH DOT BELOW; QQCM
0061  ; [.120F.0020.0002.0061] # LATIN SMALL LETTER A
0101  ; [.120F.0020.0002.0061][.0000.005B.0002.0304] # LATIN SMALL LETTER A WITH MACRON; QQCM
0062  ; [.1225.0020.0002.0062] # LATIN SMALL LETTER B
0063  ; [.123D.0020.0002.0063] # LATIN SMALL LETTER C
0064  ; [.1250.0020.0002.0064] # LATIN SMALL LETTER D
1E0D  ; [.1250.0020.0002.0064][.0000.0070.0002.0323] # LATIN SMALL LETTER D WITH DOT BELOW; QQCM
0065  ; [.126B.0020.0002.0065] # LATIN SMALL LETTER E
0066  ; [.12A3.0020.0002.0066] # LATIN SMALL LETTER F
0067  ; [.12B0.0020.0002.0067] # LATIN SMALL LETTER G
0068  ; [.12D3.0020.0002.0068] # LATIN SMALL LETTER H
1E25  ; [.12D3.0020.0002.0068][.0000.0070.0002.0323] # LATIN SMALL LETTER H WITH DOT BELOW; QQCM
0069  ; [.12EC.0020.0002.0069] # LATIN SMALL LETTER I
012B  ; [.12EC.0020.0002.0069][.0000.005B.0002.0304] # LATIN SMALL LETTER I WITH MACRON; QQCM
006A  ; [.1305.0020.0002.006A] # LATIN SMALL LETTER J
006B  ; [.131E.0020.0002.006B] # LATIN SMALL LETTER K
006C  ; [.1330.0020.0002.006C] # LATIN SMALL LETTER L
006D  ; [.135F.0020.0002.006D] # LATIN SMALL LETTER M
006E  ; [.136D.0020.0002.006E] # LATIN SMALL LETTER N
006F  ; [.138E.0020.0002.006F] # LATIN SMALL LETTER O
0070  ; [.13B3.0020.0002.0070] # LATIN SMALL LETTER P
0071  ; [.13C8.0020.0002.0071] # LATIN SMALL LETTER Q
0072  ; [.13DA.0020.0002.0072] # LATIN SMALL LETTER R
0073  ; [.1410.0020.0002.0073] # LATIN SMALL LETTER S
1E63  ; [.1410.0020.0002.0073][.0000.0070.0002.0323] # LATIN SMALL LETTER S WITH DOT BELOW; QQCM
0074  ; [.1433.0020.0002.0074] # LATIN SMALL LETTER T
1E6D  ; [.1433.0020.0002.0074][.0000.0070.0002.0323] # LATIN SMALL LETTER T WITH DOT BELOW; QQCM
0075  ; [.1453.0020.0002.0075] # LATIN SMALL LETTER U
016B  ; [.1453.0020.0002.0075][.0000.005B.0002.0304] # LATIN SMALL LETTER U WITH MACRON; QQCM
0076  ; [.147B.0020.0002.0076] # LATIN SMALL LETTER V
0077  ; [.148D.0020.0002.0077] # LATIN SMALL LETTER W
0078  ; [.1497.0020.0002.0078] # LATIN SMALL LETTER X
0079  ; [.149C.0020.0002.0079] # LATIN SMALL LETTER Y
007A  ; [.14AD.0020.0002.007A] # LATIN SMALL LETTER Z
1E93  ; [.14AD.0020.0002.007A][.0000.0070.0002.0323] # LATIN SMALL LETTER Z WITH DOT BELOW; QQCM
2000  ; [*020A.0020.0004.2000] # EN QUAD; QQK
2001  ; [*020A.0020.0004.2001] # EM QUAD; QQK
2002  ; [*020A.0020.0004.2002] # EN SPACE; QQK
2003  ; [*020A.0020.0004.2003] # EM SPACE; QQK
2004  ; [*020A.0020.0004.2004] # THREE-PER-EM SPACE; QQK
2005  ; [*020A.0020.0004.2005] # FOUR-PER-EM SPACE; QQK
2006  ; [*020A.0020.0004.2006] # SIX-PER-EM SPACE; QQK
2007  ; [*020A.0020.001B.2007] # FIGURE SPACE; QQK
2008  ; [*020A.0020.0004.2008] # PUNCTUATION SPACE; QQK
2009  ; [*020A.0020.0004.2009] # THIN SPACE; QQK
200A  ; [*020A.0020.0004.200A] # HAIR SPACE; QQK
2010  ; [*0229.0020.0002.2010] # HYPHEN
2011  ; [*0229.0020.001B.2011] # NON-BREAKING HYPHEN; QQK
2012  ; [*022A.0020.0002.2012] # FIGURE DASH
2013  ; [*022B.0020.0002.2013] # EN DASH
2014  ; [*022C.0020.0002.2014] # EM DASH
2015  ; [*022D.0020.0002.2015] # HORIZONTAL BAR
2016  ; [*055A.0020.0002.2016] # DOUBLE VERTICAL LINE
2017  ; [*021E.0020.0002.2017] # DOUBLE LOW LINE
2018  ; [*02EF.0020.0002.2018] # LEFT SINGLE QUOTATION MARK
2019  ; [*02F0.0020.0002.2019] # RIGHT SINGLE QUOTATION MARK
201A  ; [*02F1.0020.0002.201A] # SINGLE LOW-9 QUOTATION MARK
201B  ; [*02F2.0020.0002.201B] # SINGLE HIGH-REVERSED-9 QUOTATION MARK
201C  ; [*02F6.0020.0002.201C] # LEFT DOUBLE QUOTATION MARK
201D  ; [*02F7.0020.0002.201D] # RIGHT DOUBLE QUOTATION MARK
201E  ; [*02F8.0020.0002.201E] # DOUBLE LOW-9 QUOTATION MARK
201F  ; [*02F9.0020.0002.201F] # DOUBLE HIGH-REVERSED-9 QUOTATION MARK
2020  ; [*036A.0020.0002.2020] # DAGGER
2021  ; [*036B.0020.0002.2021] # DOUBLE DAGGER
2022  ; [*036C.0020.0002.2022] # BULLET
2023  ; [*036D.0020.0002.2023] # TRIANGULAR BULLET
2024  ; [*0281.0020.0004.2024] # ONE DOT LEADER; QQK
2025  ; [*0281.0020.0004.2025][*0281.0020.0004.2025] # TWO DOT LEADER; QQKN
2026  ; [*0281.0020.0004.2026][*0281.0020.0004.2026][*0281.0020.001F.2026] # HORIZONTAL ELLIPSIS; QQN
2027  ; [*036E.0020.0002.2027] # HYPHENATION POINT
2028  ; [*0208.0020.0002.2028] # LINE SEPARATOR
2029  ; [*0209.0020.0002.2029] # PARAGRAPH SEPARATOR
202F  ; [*020A.0020.001B.202F] # NARROW NO-BREAK SPACE; QQK
2030  ; [*0365.0020.0002.2030] # PER MILLE SIGN
2031  ; [*0367.0020.0002.2031] # PER TEN THOUSAND SIGN
2032  ; [*0372.0020.0002.2032] # PRIME
2033  ; [*0372.0020.0004.2033][*0372.0020.0004.2033] # DOUBLE PRIME; QQKN
2034  ; [*0372.0020.0004.2034][*0372.0020.0004.2034][*0372.0020.001F.2034] # TRIPLE PRIME; QQKN
2035  ; [*0373.0020.0002.2035] # REVERSED PRIME
2036  ; [*0373.0020.0004.2036][*0373.0020.0004.2036] # REVERSED DOUBLE PRIME; QQKN
2037  ; [*0373.0020.0004.2037][*0373.0020.0004.2037][*0373.0020.001F.2037] # REVERSED TRIPLE PRIME; 
2038  ; [*0376.0020.0002.2038] # CARET
2039  ; [*02F3.0020.0002.2039] # SINGLE LEFT-POINTING ANGLE QUOTATION MARK
203A  ; [*02F4.0020.0002.203A] # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
203B  ; [*0377.0020.0002.203B] # REFERENCE MARK
203C  ; [*026E.0020.0004.203C][*026E.0020.0004.203C] # DOUBLE EXCLAMATION MARK; QQKN
203D  ; [*027F.0020.0002.203D] # INTERROBANG
203E  ; [*0213.0020.0002.203E] # OVERLINE
203F  ; [*0378.0020.0002.203F] # UNDERTIE
2040  ; [*037A.0020.0002.2040] # CHARACTER TIE
2041  ; [*037C.0020.0002.2041] # CARET INSERTION POINT
2042  ; [*037D.0020.0002.2042] # ASTERISM
2043  ; [*036F.0020.0002.2043] # HYPHEN BULLET
2044  ; [*035D.0020.0002.2044] # FRACTION SLASH
2045  ; [*030B.0020.0002.2045] # LEFT SQUARE BRACKET WITH QUILL
2046  ; [*030C.0020.0002.2046] # RIGHT SQUARE BRACKET WITH QUILL
2047  ; [*0273.0020.0004.2047][*0273.0020.0004.2047] # DOUBLE QUESTION MARK; QQKN
2048  ; [*0273.0020.0004.2048][*026E.0020.0004.2048] # QUESTION EXCLAMATION MARK; QQKN
2049  ; [*026E.0020.0004.2049][*0273.0020.0004.2049] # EXCLAMATION QUESTION MARK; QQKN
204A  ; [*0361.0020.0002.204A] # TIRONIAN SIGN ET
204B  ; [*0353.0020.0002.204B] # REVERSED PILCROW SIGN
204C  ; [*0370.0020.0002.204C] # BLACK LEFTWARDS BULLET
204D  ; [*0371.0020.0002.204D] # BLACK RIGHTWARDS BULLET
204E  ; [*0358.0020.0002.204E] # LOW ASTERISK
204F  ; [*0245.0020.0002.204F] # REVERSED SEMICOLON
2050  ; [*037B.0020.0002.2050] # CLOSE UP
2051  ; [*0359.0020.0002.2051] # TWO ASTERISKS ALIGNED VERTICALLY
2052  ; [*0369.0020.0002.2052] # COMMERCIAL MINUS SIGN
2053  ; [*022E.0020.0002.2053] # SWUNG DASH
2054  ; [*0379.0020.0002.2054] # INVERTED UNDERTIE
2055  ; [*02D3.0020.0002.2055] # FLOWER PUNCTUATION MARK
2056  ; [*02D4.0020.0002.2056] # THREE DOT PUNCTUATION
2057  ; [*0372.0020.0004.2057][*0372.0020.0004.2057][*0372.0020.001F.2057][*0372.0020.001F.2057] 
2058  ; [*02D5.0020.0002.2058] # FOUR DOT PUNCTUATION
2059  ; [*02D6.0020.0002.2059] # FIVE DOT PUNCTUATION
205A  ; [*02D7.0020.0002.205A] # TWO DOT PUNCTUATION
205B  ; [*02D8.0020.0002.205B] # FOUR DOT MARK
205C  ; [*02D9.0020.0002.205C] # DOTTED CROSS
205D  ; [*02DA.0020.0002.205D] # TRICOLON
205E  ; [*02DB.0020.0002.205E] # VERTICAL FOUR DOTS
205F  ; [*020A.0020.0004.205F] # MEDIUM MATHEMATICAL SPACE; QQK
2061  ; [.0000.0000.0000.2061] # FUNCTION APPLICATION
2062  ; [.0000.0000.0000.2062] # INVISIBLE TIMES
2063  ; [.0000.0000.0000.2063] # INVISIBLE SEPARATOR
2064  ; [.0000.0000.0000.2064] # INVISIBLE PLUS
207A  ; [*0550.0020.0014.207A] # SUPERSCRIPT PLUS SIGN; QQK
207B  ; [*055C.0020.0014.207B] # SUPERSCRIPT MINUS; QQK
207C  ; [*0555.0020.0014.207C] # SUPERSCRIPT EQUALS SIGN; QQK
207D  ; [*02FF.0020.0014.207D] # SUPERSCRIPT LEFT PARENTHESIS; QQK
207E  ; [*0300.0020.0014.207E] # SUPERSCRIPT RIGHT PARENTHESIS; QQK
208A  ; [*0550.0020.0015.208A] # SUBSCRIPT PLUS SIGN; QQK
208B  ; [*055C.0020.0015.208B] # SUBSCRIPT MINUS; QQK
208C  ; [*0555.0020.0015.208C] # SUBSCRIPT EQUALS SIGN; QQK
208D  ; [*02FF.0020.0015.208D] # SUBSCRIPT LEFT PARENTHESIS; QQK
208E  ; [*0300.0020.0015.208E] # SUBSCRIPT RIGHT PARENTHESIS; QQK
"""

xml_hdr = """\
<?xml version="1.0" encoding="UTF-8"?>
<ncx version="2005-1"    xml:lang="en"   xmlns="http://www.daisy.org/z3986/2005/ncx/">
<!-- This file Copyright 2012 created by epub3_utils.py -->
"""

xhtml_hdr = string.Template("""\
<?xml version="1.0" encoding="UTF-8" ?>
<html xmlns="http://www.w3.org/1999/xhtml"
 xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en-US">
<head>
<meta charset="utf-8"/>
<title>${title}</title>
<link href="${css}" type="text/css" rel="stylesheet"/>
</head>
<body>
<!-- This file Copyright 2012 created by epub3_utils.py -->
""")

generic_form = string.Template("""\
<?xml version="1.0" encoding="UTF-8" ?>
<html xmlns="http://www.w3.org/1999/xhtml"
 xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en-US">
<head>
<meta charset="utf-8" />
<title>NO TITLE IN GENERIC FORM!</title>
<link href="css/main.css" type="text/css" rel="stylesheet"/>
</head> 
<!-- This file Copyright 2012 created by epub3_utils.py -->
<body>
<div class="body">
${content}
</div>
</body>
</html>
""")


popup_form = string.Template("""\
<?xml version="1.0" encoding="UTF-8" ?>
<html xmlns="http://www.w3.org/1999/xhtml"
 xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en-US">
<head>
<meta charset="utf-8" />
<title>NO TITLE IN GENERIC FORM!</title>
<link href="css/main.css" type="text/css" rel="stylesheet"/>
</head> 
<!-- This file Copyright 2012 created by epub3_utils.py -->
<body>
<div class="body" id="top">
${content}
${popups}
</div>
</body>
</html>
""")


title_form = string.Template("""\
<?xml version="1.0" encoding="UTF-8" ?>
<html xmlns="http://www.w3.org/1999/xhtml" 
 xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en-US">
<head>
<meta charset="utf-8" />
<!-- This file Copyright 2012 created by epub3_utils.py -->

<title>${title}</title>


<!-- AUTHOR="${author}" -->
<!-- PUBLISHER="${publisher}" -->
<!-- ISBN="${isbn}" -->
<link href="${css}" type="text/css" rel="stylesheet"/>

</head> 
<body>
<p>${coverdesign}</p>
<p>${coverphoto}</p>
<p>${translators}</p>
<p>${design}</p>
<p>${isbn}</p>
<p>${publisher}</p>
<p>${web}</p>
<p>${software}</p>
<p>Version 1.${ver} created on ${time}</p>
<p>${ver_type}</p>
<p>${extra}</p>
${content}
</body>
</html>
""")

content_form=string.Template("""\
<?xml version="1.0" encoding="UTF-8" ?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="uuid" version="3.0" 
prefix="ibooks: http://vocabulary.itunes.apple.com/rdf/ibooks/vocabulary-extensions-1.0/">
<metadata xmlns:opf="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="ISBN">${isbn}</dc:identifier>
<dc:identifier id="uuid">urn:uuid:${uniq}</dc:identifier>
<dc:title>${title}</dc:title>
<dc:language>en-US</dc:language>
<dc:creator>${author}</dc:creator>
<dc:publisher>${publisher}</dc:publisher>
<dc:description>${description} </dc:description>
<dc:rights>${copyright}</dc:rights>
<dc:subject>${subject}</dc:subject>
<meta property="dcterms:modified">${time}</meta>
<meta property="ibooks:version">1.0.${ver}</meta>
<!-- Version 1.${ver} created on ${time} -->
<!-- needed for mobi conversion -->
<meta name="cover" content="img_cover" />        
<!-- This file Copyright 2012 created by epub3_utils.py ${scr_ver} -->
</metadata>
<manifest>

<!-- NCX -->
<item id="ncx"  href="toc.ncx"  media-type="application/x-dtbncx+xml"/>
<item id="toc" properties="nav"  href="toc.xhtml"  media-type="application/xhtml+xml"/>

<!-- CSS Style Sheets -->
<item id="main-css"  href="css/main.css"  media-type="text/css"/>
<!-- item id="pagetemplate" href="page-template.xpgt" media-type="application/vnd.adobe-page-template+xml"/ -->

<!-- item id="translits"  href="translits.xhtml"  media-type="application/xhtml+xml"/ -->

${file_defs}

 </manifest>
 <spine toc="ncx">

${file_items}

 </spine>
</package>
<!-- ${uniq} -->
""")

toc_form=string.Template("""\
<?xml version="1.0" encoding="UTF-8"?>
<ncx version="2005-1"    xml:lang="en"   xmlns="http://www.daisy.org/z3986/2005/ncx/">

<head>
<!-- This file Copyright 2012 created by epub3_utils.py -->
<!-- The following four metadata items are required for all
     NCX documents, including those conforming to the relaxed
     constraints of OPS 2.0 -->

<meta name="dtb:uid" content="urn:uuid:${uniq}"/>
<meta name="dtb:depth" content="1"/>
<meta name="dtb:totalPageCount" content="0"/>
<meta name="dtb:maxPageNumber" content="0"/>
</head>

<!-- ${title} (version ${ver}) -->
<docTitle><text>${title}</text></docTitle>
<docAuthor><text>${author}</text></docAuthor>

<navMap>

<!-- id="c126cfe8-d3ab-11de-ba13-001cc0a62c0b"  -->


""")

nav_form=string.Template("""\
<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en-US">
<!-- id="c126cfe8-d3ab-11de-ba13-001cc0a62c0b"  -->
<head>
<title>${title}</title>
<link rel="stylesheet" href="css/main.css" type="text/css"/>
<meta charset="utf-8"/>
</head>
<body>
<section class="frontmatter TableOfContents" epub:type="frontmatter toc">
<header>
<h1>Contents</h1>
</header>
<nav xmlns:epub="http://www.idpf.org/2007/ops" epub:type="toc" id="toc">
<ol>


""")

old_random_form = string.Template("""\
<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en-US">
<head>
<title>Randomize</title>
<script src="jquery-1.6.2.min.js" type="text/javascript"></script>
<script type="text/javascript">
//<![CDATA[
$$(function(){

$$('.hello').click(function(){
    var myrandom=Math.round(Math.random()*(document.links.length-1))
    window.location=document.links[myrandom].href
});

});
//]]>
</script>
</head>
<body>
<h1 class="hello">Random Topic!</h1>
${links}
</body>
</html>
""")

random_form = string.Template("""\
<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en-US">
<head>
<title>Randomize</title>
<script src="jquery-1.6.2.min.js" type="text/javascript"></script>
<script type="text/javascript">
function addLoadEvent(func) {
    var oldonload = window.onload;
    if (typeof window.onload != 'function') {
        window.onload = func;
    } else {
        window.onload = function() {
            if (oldonload) {
                oldonload();
            }
            func();
        }
    }
}

addLoadEvent(function() {
    document.body.style.backgroundColor = 'yellow';
    var myrandom=Math.round(Math.random()*(document.links.length-1))
    window.location=document.links[myrandom].href
})
</script>
</head>
<body>
<h1 class="hello">Random Topic!</h1>
${links}
</body>
</html>
""")

default_cfg = """\
{ "config": [
{
"title":"Test Book",
"author":"Me",
"creator":"Jay",
"language":"en",
"publisher": "My Publications",
"published": "New York",
"translators":"None",
"cover design":"Joshua",
"design":"Amy",
"cover photo":"",
"copyright":"Copyright @ 2012 Me",
"subject":"Ebooks",
"date":"2010",
"revision":"",
"description":"How to make epub3",
"isbn":"0-933546-XX-X", 
"rights":"All rights reserved. No part of this publication may be reproduced, stored in a retrieval system, or transmitted in any form or by any means, electronic, mechanical photocopying, recording, or otherwise, without prior permission of the copyright owner."
},
{
"use_biblio":"",
"use_italics":"",
"use_romanref":"",
"use_nameref":"",
"use_wordref":"",
"use_sorted_toc":"",
"use_sorted_unicode":"",
"use_abbrev":"",
"use_figures":"",
"lev_break":4,
"lev_toc":4,
"unicode":"y",
"enough_lines":500,
"run_epubcheck":"java -jar ~/Dropbox/epubcheck/epubcheck-3.0b5.jar",
"sample":""
},
{
"headings":"headings.txt",
"filemap":["title","main"],
"biblio":"biblio.txt",
"css":"",
"nameref":"index_names.txt",
"wordref":"index_words.txt",
"input":"Text.txt",
"output":"Test.epub"
}
]
}
"""

default_headings = """\
{
"cover" : "Cover",
"title" : "Title",
"centers" : "Centers",
"knp" : "About",
"random" : "Go To A Random Heading",
"other" :  "Other Titles",
"abbrev" :  "Abbreviations",
"main" :  "",
"footnotes" :  "Footnotes",
"biblio" :  "Bibliograpy",
"sorted_toc" :  "Sorted Contents",
"sorted_unicode" :  "Sorted Contents by Persian/Arabic titles",
"bookref" :  "Index for Book References",
"wordref" :  "Index for Persian/Arabic Terms",
"nameref" :  "Index for Names",
"romanref" :  "Index for References from Koran (Roman Numeral Chapter:Verse)",
"back" :  "Back Cover"
}
"""

default_css = """\
 body {
  widows: 0;
  orphans: 0
}

em { font-style: italic; }
/*
em { color : red; }
span.nm { color : orange; }
span.ref { color: green; }
*/

pre { 
font-style: italic; 
font-weight: bold; 
color: blue;
white-space: -pre-wrap;
margin-left: 6%;
}

h1,h2,h3,h4,h5 {  text-align: center; }

/*
 h1 { page-break-before:always;} 
h3 { text-decoration:underline;}
*/

/* Uncomment to have links invisible
a:link, a:visited, a:hover, a:active {
    -webkit-text-fill-color: black;
}
*/


p { text-indent: 0%; }
p { text-align: justify; }

span.ref {
    margin:0;
    padding :0;
}


table.translits {
border-collapse:separate;
border-width:5px;
}

.under { text-decoration: underline; }
.center { text-align: center; }
.par { text-indent: 4%; }
.ind { margin-left: 8%; }
.book_ref { margin-left: 8%; }

.poem { 
margin: 0;
padding : 0;
font-style: italic; 
font-size: smaller;
white-space: -pre-wrap;
margin-left: 2%;
}
.farsi { 
font-family : Iowan;
margin: 0;   /* ? */
padding : 0; /* ? */
text-align: right;
font-style: italic; 
white-space: -pre-wrap;
/* use these for indented poems */
margin-left: 15%; 
text-indent: -15%
}

/*
.toc2 { font-size: 100%;}
.toc3 { font-size: 100%;}
.toc4 { margin-left: 10%; font-size: 80%; }
.toc5 { margin-left: 20%; font-size: 70%; }

.toc2,.toc3,.toc4,.toc5 {  text-align: left; }
*/

img.logo2 {
    display: block;
    margin-left: auto;
    margin-right: auto;
}

.references {
    -moz-column-count:4; 
    -webkit-column-count:2; 
    column-count:2;
}

div.images, img, div.images p.image-caption { margin: 0 auto; padding: 0; text-align: center; font-style: italic; font-size: 90%; } 
div.images { overflow: auto; } 
div.images, img { max-height: 99%; max-width: 99%; clear: both; } 
div.images p.image-caption { margin-bottom: 1em; } 

li {
	margin-top: 1em;
}
"""	     

container_form = """\
<?xml version="1.0" encoding="UTF-8" ?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles>
<rootfile full-path="OPS/content.opf" media-type="application/oebps-package+xml"/>
</rootfiles>
</container>
"""

# pyuca - Unicode Collation Algorithm
# Version: 2006-01-27
# James Tauber
# http://jtauber.com/
#    http://www.unicode.org/Public/UCA/latest/allkeys.txt

class Trie:

    def __init__(self):
        self.root = [None, {}]

    def add(self, key, value):
        curr_node = self.root
        for part in key:
            curr_node = curr_node[1].setdefault(part, [None, {}])
        curr_node[0] = value

    def find_prefix(self, key):
        curr_node = self.root
        remainder = key
        for part in key:
            if part not in curr_node[1]:
                break
            curr_node = curr_node[1][part]
            remainder = remainder[1:]
        return (curr_node[0], remainder)


class Collator:

    def __init__(self, filename):

        self.table = Trie()
        self.load(filename)

    def load(self, filename):
	    # If Global extra_text exists, use it, otherwise get from file!
	    if extra_text:
		    lines = extra_text.split('\n')
	    else:
		    lines = open(filename)
	    for line in lines:
		    if line.startswith("#") or line.startswith("%"):
			continue
		    if line.strip() == "":
			continue
		    line = line[:line.find("#")] + "\n"
		    line = line[:line.find("%")] + "\n"
		    line = line.strip()

		    if line.startswith("@"):
			pass
		    else:
			semicolon = line.find(";")
			charList = line[:semicolon].strip().split()
			x = line[semicolon:]
			collElements = []
			while True:
			    begin = x.find("[")
			    if begin == -1:
				break                
			    end = x[begin:].find("]")
			    collElement = x[begin:begin+end+1]
			    x = x[begin + 1:]

			    alt = collElement[1]
			    chars = collElement[2:-1].split(".")

			    collElements.append((alt, chars))
			integer_points = [int(ch, 16) for ch in charList]
			self.table.add(integer_points, collElements)

    def sort_key(self, string):
        
        collation_elements = []

        lookup_key = [ord(ch) for ch in string]
        while lookup_key:
            value, lookup_key = self.table.find_prefix(lookup_key)
            if not value:
                # @@@
                raise Exception
            collation_elements.extend(value)
    
        sort_key = []
        
        for level in range(4):
            if level:
                sort_key.append(0)
            for element in collation_elements:
                sort_key.append(int(element[1][level], 16))
                
        return tuple(sort_key)

path = os.path.dirname( os.path.realpath(__file__))
rezip = re.compile("library.zip")
if (rezip.search(path)):
    path2 = os.path.dirname(path)
else:
    path2 = path

#appdir = os.path.dirname(sys.argv[0])
#print "appdir = ",appdir

coll = Collator(path2+'/allkeys.txt')
#PBDBG = open("temp.txt","w")

#default 'globals'
full_unicode = 1
ver_type = " "
# lines before new file forced. This is estimated to keep size from getting too big
#Max_Lines = 500 # was 100

debug = False

def zip_files(dir, zip_file):
    os.chdir('efiles')
    with zipfile.ZipFile(zip_file, 'w', compression=zipfile.ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk("."):
            for file in files:
                fpath = os.path.join(root, file)
                zip.write(fpath, compress_type=zipfile.ZIP_DEFLATED)
    os.chdir('..')

def check_attr(cfgd,name,filem=None):
	key = check_key(cfgd,name)
	if (key):
		if (filem): filem.append(name)
		return(True)
	else:
		return(False)

def check_key(cfgd,name):
	try:
		key = cfgd[name]
	except:
		key = None
	return(key)
    

# a simple class with a write method
class WritableObject:
    def __init__(self):
        self.content = []
    def write(self, string):
        self.content.append(string)
 

def capitalize_english(l):
    l = frefs.sub("",l)
    # Also handle exceptions!!!
    #flet = re.compile("\s\w")
    #if fpar.search(l):
    t = l.title()
    start_lower = False
    s = ''
    for letter in t:
        if (letter == '('):
            start_lower = True
        elif (letter == ')'):
            start_lower = False
        if (start_lower):
            s += letter.lower()
        else:
            s += letter
    
    words = s.split()
    s1 = ''
    # If Word is a Roman Numeral, convert back to Uppercase!
    for w in words:
	    val = todec(w.upper())
	    if (val>0):
		    s1 += w.upper()+' '
	    else:
		    s1 += w+' '

    s = re.sub(ur'’(\w)',lambda m: m.group(0).lower(),s1)
    return(s)

def read_config(fname):
    if (os.path.isfile(fname)):
        print "found ",fname," now reading...."
        s = utffile2str(fname)
        g_cfg = json.loads(s)
    else:
        print "Couldn't find config file",fname, "using default cfg"
        g_cfg = json.loads(default_cfg)
    return g_cfg

 
def md_to_xhtml(book_dict,logfile=None):
	sample=None
        outdump = WritableObject()
        if (logfile): sys.stdout = outdump
	############
        attr_dict = book_dict[0]
        opts_dict = book_dict[1]
        cfg_dict = book_dict[2]
        sample = check_key(attr_dict,'use_sample')
	sample_modulo  = 6
	sample_last    = 5
	# if index_size is > than this, break apart into smaller chunks
	index_limit    = 16000
	temp_debug_index = 0

        if 'keep_efiles' in opts_dict:
            debug_efiles = opts_dict['keep_efiles']
        else:
            debug_efiles = False

	if 'use_random' in opts_dict:
		use_random  = opts_dict['use_random']
	else:
		use_random = False


	if 'single_file' in opts_dict:
		# define to create a html file with all of the main chapters,
		# without references, table of contents, etc.
		# it only contains text in the main ".txt" file
		alfile = "efiles/OPS/single.xhtml"
	else:
		print "separate files"
		alfile = None

        try:
            lev_break = int(opts_dict['lev_break']) + 1
            lev_toc = int(opts_dict['lev_toc']) + 1
            max_lines = int(opts_dict['enough_lines'])
        except:
            print "lev_break, enough_lines and lev_toc must be integers!, exiting!"
            sys.exit()
        # only put in TOC if less than this!!!

        no_unicode = check_attr(opts_dict,'ascii')
        if (no_unicode):  use_ascii()

	script_ver = cfg_dict['script_ver']
	#print "SCRIPT VER = ",script_ver
        # lines before new file forced. This is estimated to keep size from getting too big

        use_italics = check_attr(opts_dict,'use_italics')
        use_roman = check_attr(opts_dict,'use_romanref')
        use_name_index  = check_attr(opts_dict,'use_nameref')
        use_index = check_attr(opts_dict,'use_wordref')
        use_phrases = check_attr(opts_dict,'use_wordref')
        use_sorted_toc     = check_attr(opts_dict,'use_sorted_toc')
        use_sorted_unicode = check_attr(opts_dict,'use_sorted_unicode')
        use_biblio = check_attr(opts_dict,'use_biblio')
        use_bookref = check_attr(opts_dict,'use_bookref')
        use_abbrev = check_attr(opts_dict,'use_abbrev')
        use_figures = check_attr(opts_dict,'use_figures')
	use_headings = check_attr(cfg_dict,'headings')
        
	# files
        input_filename    = cfg_dict['input']
        output_filename   = cfg_dict['output']
	if (use_biblio):
		biblio_filename   = cfg_dict['biblio']
	if (use_headings):
		headings_file     = cfg_dict['headings']
	else:
		headings_file = ''

        css_filename      = cfg_dict['css']

	filemap           = cfg_dict['filemap']

	# Check filemap vs options integrity
	if (use_biblio and ('biblio' not in filemap)) or \
		    (not use_biblio and ('biblio' in filemap)):
		print "biblio and use_biblio not in sync"
		sys.exit(1)

	if (use_bookref and ('bookref' not in filemap)) or \
		    (not use_bookref and ('bookref' in filemap)):
		print "bookref and use_bookref not in sync"
		sys.exit(1)

	if (use_abbrev and ('abbrev' not in filemap)) or \
		    (not use_abbrev and ('abbrev' in filemap)):
		print "abbrev and use_abbrev not in sync"
		sys.exit(1)
	
	if (use_sorted_toc and ('sorted_toc' not in filemap)) or \
		    (not use_sorted_toc and ('sorted_toc' in filemap)):
		print "sorted_toc and use_sorted_toc not in sync"
		sys.exit(1)

	if (use_sorted_unicode and ('sorted_unicode' not in filemap)) or \
		    (not use_sorted_unicode and ('sorted_unicode' in filemap)):
		print "sorted_unicode and use_sorted_unicode not in sync"
		sys.exit(1)

	if (use_figures and ('figures' not in filemap)) or \
		    (not use_figures and ('figures' in filemap)):
		print "figures and use_figures not in sync"
		sys.exit(1)
        # ?

	if (not os.path.isfile(headings_file)): 
            print "Headings file",headings_file," missing, using default headings"

	# MUST BE "main"!!!! for now
	chaptername = "main"

	#----------------------------------Create basic files
	if (not os.path.isdir("efiles")):
		os.makedirs("efiles")

	dirf = open("efiles/mimetype","w")
	dirf.write("application/epub+zip")
	dirf.close()

	if (not os.path.isdir("efiles/OPS/css")):
		os.makedirs("efiles/OPS/css")

	if (os.path.isfile(css_filename)):
		shutil.copy2(css_filename,'efiles/OPS/css/main.css')
                print "\t\t\tcopying ",css_filename, " to " ,'efiles/OPS/css/main.css'
	else:
		print "Didn't find css file",css_filename," using defaults"
		cssf = open("efiles/OPS/css/main.css","w")
		cssf.write(default_css)
		cssf.close()

	if (not os.path.isdir("efiles/META-INF")):
		os.makedirs("efiles/META-INF")

	xssf = open("efiles/META-INF/container.xml","w")
	xssf.write(container_form)
	xssf.close()

        #------------------------------------
        # copy images.........
        copied_jpgs = []

        #print os.listdir('.')

	if (not os.path.isdir("efiles/OPS/images")):
		os.makedirs("efiles/OPS/images")

        for i in glob.glob('*.jpg'):
            (root,ext) = i.split(".jpg")
            copied_jpgs.append(root)
            print "\t\t\tcopying ",i, " to " ,'efiles/OPS/images/'+i
            shutil.copyfile(i,'efiles/OPS/images/'+i)

	if (os.path.isdir("images")):
            os.chdir('images')
            for i in glob.glob('*.jpg'):
                (root,ext) = i.split(".jpg")
                copied_jpgs.append(root)
                print "\t\t\tcopying ",i, " to " ,'../efiles/OPS/images/'+i
                shutil.copyfile(i,'../efiles/OPS/images/'+i)
            os.chdir('..')
 
        for i in glob.glob('*.xhtml'):
            (root,ext) = i.split(".xhtml")
            if root in filemap:
                print "\t\t\tcopying ",i, " to " ,'efiles/OPS/'+i
                shutil.copyfile(i,'efiles/OPS/'+i)
            else:
                print "extraneous file ",i," not copied to epub"

        jslist = []
        for i in glob.glob('*.js'):
            (root,ext) = i.split(".js")
            if root in filemap:
                print "\t\t\tcopying ",i, " to " ,'efiles/OPS/'+i
            else:
                print "adding file ",i
	    jslist.append(root)
	    shutil.copyfile(i,'efiles/OPS/'+i)
        

	#----------------------------------

	# Get dictionary mapping various documents with their headings
	if (os.path.isfile(headings_file)):
		s = utffile2str(headings_file)
		try:
			filedict = json.loads(s)
		except:
			print "Problem with file ",headings_file, " using default headings"
			filedict = json.loads(default_headings)
	else:
		print "headings file ",headings_file, "not found -> using default headings"
		filedict = json.loads(default_headings)
	# Get 'filemap' for what is included in EPUB
        if (filemap == ""): filemap = ['main']

        print "Epub file/page order (main==book chapters): "
	for f in filemap: print "\t\t\t",f
	# Copy filemap to filelist + add various other necessary things
	filelist = filemap[:]

        # needed?
	#filelist.insert(0,'titlepage')

	####use_index = None
	#print "FILEMAP = ",filemap
	print start_blue+"Processing: ",input_filename+end_color

        jpeglist = ['cover']
        if 'back' in filemap:
            jpeglist.append('back')


	unicode_dict = {} # unicode index
	roman_dict = {} # romanic link dictionary
	abbrev_dict = {} # abbrev link dictionary
	abbrev_lookup = {} # abbrev
	name_dict = {} # name index

	ftnlist = [] # footnote list
	figlist = [] # figure list
	tbllist = [] # table list
	#wdict = {} # word index

	# output files
	abbrev_file   = "efiles/OPS/abbrev.xhtml"
	biblio_file   = "efiles/OPS/biblio.xhtml"
	bref_file     = "efiles/OPS/bookref.xhtml"
	index_file    = "efiles/OPS/wordref.xhtml"
	name_file     = "efiles/OPS/nameref.xhtml"
	sorted_file   = "efiles/OPS/sorted_toc.xhtml"
	usorted_file  = "efiles/OPS/sorted_unicode.xhtml"
	toc_file      = "efiles/OPS/toc.ncx"
	toc3_file     = "efiles/OPS/toc.xhtml"
	content_file  = "efiles/OPS/content.opf"
	roman_file    = "efiles/OPS/romanref.xhtml"
	fig_file      = "efiles/OPS/figures.xhtml"
	table_file    = "efiles/OPS/tables.xhtml"
	title_file    = "efiles/OPS/title.xhtml"
	random_file   = "efiles/OPS/random.xhtml"

	# Debug output
	dbfile = "Unused.txt"

	all_content = ''

	if (os.path.isdir(".git")):
		x = commands.getstatusoutput('git shortlog -s')
		ver_s = string.split(x[1])
		ver = string.strip(ver_s[0])
	else:
		ver = "0"

	############################################
	# Abbreviations
	############################################
	if (use_biblio):
		biblio_dict = biblio_proc(biblio_filename,use_abbrev,abbrev_file,biblio_file)

		# Create new dict with abbreviations as keys and titles as values
		if (biblio_dict):
			abbrev_lookup = biblio_abbrev(biblio_dict)
	############################################
	# Copy Titles, Abbrevs,
	############################################

	(hlines,content_list,scontent_list,sfarsi_list,fig_list,table_list,fnlist) = rawfiles2html([input_filename],lev_break,max_lines)
	headings = len(hlines)

	# get phrases from file
	# Note everything in here should be lowercase!!! or it won't work!!!!!
	phr = utffile2list("phrases.txt")

	# get index from file
	if (use_name_index):
		name_index = utffile2list(cfg_dict['nameref'])

	if (use_index or use_phrases):
		word_index = utffile2list(cfg_dict['wordref'])

	#new_names = []
	#for ix in name_index:
	#	words = re.split(r"[\(]+",ix) # allows names with stuff after in paren
	#	new_names.append(words[0])


	pw   = re.compile('\(|\)',re.UNICODE)
	img  = re.compile('<img src=')
	tbl  = re.compile('<table class=')
	end_table  = re.compile('</table>')
	end_tr  = re.compile('</tr>')

	phr_noparen = []
	for p in phr: phr_noparen.append(pw.sub("",p))

	#print phr_noparen

	# Add sorted farsi contents to Phrases .... try for now....
	if (use_sorted_unicode):
		for tup in sfarsi_list:
			(f,a,b) = tup
			phr.append("("+f+")")

	#print word_index


	############################################
	# MAIN loop
	############################################
	used_fig_list = []
	fig_count = 0
	tbl_count = 0
	fn_count = 1
	lc = 0

	for h in xrange(0,headings):
		cfile = "efiles/OPS/"+chaptername+'%03d' % h+".xhtml"
                print "\t\t\t","processing ",cfile
		new_content = ''
		if(not alfile): lc = 0
		no_embed = 0
		in_table = 0
		valid_lc = 0
		for line in hlines[h]:
			has_img = img.search(line)
			if (has_img): no_embed = 1
			else: no_embed = 0
                        #print "h=",h,line.strip()
			new_line = re.sub('Author:','<i>Author</i>:',line)
			if(end_table.search(line)): in_table = 0
			if(tbl.search(line)):       in_table = 1
			add_span_line = not temp_debug_index and not end_table.search(line) and not in_table
			if(add_span_line):
				#new_line = new_line+"<span id=\"line"+str(lc)+"\"></span>"
				new_line = "<span id=\"line"+str(lc)+"\"></span>"+new_line
				valid_lc = lc

			# only use line counts that have a valid span indicator, so some markers may be slightly off
			marker = (h,valid_lc)
			#----------------------------------------------
			# search for names in each line and put anchor
			#----------------------------------------------
			if(use_name_index):
				(new_line,name_dict) = htmlize_name_index(new_line,name_index,name_dict,marker,no_embed)

			#----------------------------------------------
			# just htmlize footnotes - which have pattern in text
			#----------------------------------------------
			(new_line,ftnlist) = htmlize_footnotes(new_line,ftnlist,fnlist,marker,no_embed)

			#----------------------------------------------
			# look for index words so they can be emphasized
			# phrases are inside paren such as (eshq-e)
			#----------------------------------------------
			if(use_phrases):
				(new_line,unicode_dict) = htmlize_index(new_line,phr,phr_noparen,unicode_dict,marker,no_embed,1)
			# also words in word_index
			if(use_index):
				(new_line,unicode_dict) = htmlize_index(new_line,word_index,word_index,unicode_dict,marker,no_embed,None)


			if (use_italics):
				new_line = italize_index(new_line,phr,phr_noparen,unicode_dict,marker,no_embed)

			#----------------------------------------------
			# HTMLize References
			# Book References are Uppercase + Numbers only
			#----------------------------------------------
			(new_line,abbrev_dict) = htmlize_book_refs(new_line,abbrev_dict,abbrev_lookup,marker)

			#----------------------------------------------
			# Roman References has ":" + Uppercase + Numbers
			#----------------------------------------------
			(new_line,roman_dict) = htmlize_krefs(new_line,roman_dict,marker)

			if (has_img):
				(junk,title1) = line.split("alt=")
				(fig_title,junk) = title1.split("/")
				#print "Fig title = ",fig_title
				if (string.strip(fig_title)==''):
					#print fig_count,marker
					figlist.append([fig_count,marker])
				else:
					#print fig_title,marker
					figlist.append([fig_title,marker])
				fig_count += 1
			if(tbl.search(line)):
				tbllist.append([table_list[tbl_count],marker])
				tbl_count += 1
			new_content += new_line
			lc = lc+1
			if(alfile): all_content += new_line
		if (not alfile): 
			if (sample):
				if (sample_last):
					if (h > sample_last):
						new_content = '<i>This section is blank in sample copy! </i>'
					else:
						used_fig_list += fig_list[h]
				elif (h%sample_modulo): 
					new_content = '<i>Only every '+str(sample_modulo)+'th page/section is non-blank in sample copy! </i>'
				else:
					used_fig_list += fig_list[h]
			else:
				used_fig_list += fig_list[h]
		else:
				used_fig_list += fig_list[h]

                if (not alfile):
                    mkgenhtml(cfile,new_content)
                        


	# Single HTML file than can be used for simple PDF
	#if(alfile): mkgenhtml(alfile,all_content)
	if(alfile): chaptername = ''

	##--------------------POST PROCESSING------------------------------
	# Needed variables: all of the use_...
	# filenames...
	# Dictionaries: abbrev_dict,unicode_dict,name_dict,roman_dict, filedict, biblio_dict
	# Lists: scontent_list, figlist, tbllist, content_list, 
	# filemap, used_fig_list,jpeglist
	#
	# integer: headings
	# JSON: title
	# For usage: phr,phr_noparen,word_index,name_index
	#
	#

	#print "Starting post processing"

	#print "Size of ..."
	#print "abbrev_dict = ",sys.getsizeof(abbrev_dict)
	index_size = sys.getsizeof(unicode_dict)
	#print "Index dictionary unicode_dict = ",index_size
	#print "Name index dictionary name_dict = ",sys.getsizeof(name_dict)
	#print "roman_dict = ",sys.getsizeof(roman_dict)
	#print "filedict = ",sys.getsizeof(filedict)
	#print "biblio_dict = ",sys.getsizeof(biblio_dict)

	#for k,v in roman_dict.iteritems(): print k.encode('utf-8'),v


	#print "ftnlist = ",ftnlist

	############################################
	# Sorted contents
	############################################

	if(use_sorted_toc): 
		s = create_sorted_contents(scontent_list,chaptername)
		all_content +=	mkgen(sorted_file,s)

	if(use_sorted_unicode): 
		s = create_sorted_contents(sfarsi_list,chaptername)
		all_content +=	mkgen(usorted_file,s)
		#list2utffile(sfarsi_list,"tmp.list")

	#print "sorted farsi = ",sfarsi_list

	############################################
	# Biblio
	############################################

	if use_abbrev: 
		s = make_biblio(biblio_dict)
		all_content +=	mkgen(biblio_file,s)
		s = create_biblio_refs(abbrev_dict,chaptername)
                if (use_bookref):
                    all_content +=	mkgen(bref_file,s)

	############################################
	# INDEX
	############################################

	#for k,v in unicode_dict.iteritems(): print k.encode('utf-8')
	# Note: not combining unicode_dict + wdict for now!

	##################################################
	# Index - Either 1 file or separated 
	##################################################
	if (index_size > index_limit):
		print "Splitting indexes"
		index_file_list = ref_create_index_split(unicode_dict,chaptername)
		ind = filelist.index("wordref")
		for sep in index_file_list:
			filelist.insert(ind+1,sep)
			sep_letter = re.sub("wordref_","Index for ",sep)
			#if (string.strip(sep_letter) == 'Index for y'): sep_letter = "Index for z & non-english"
			#print "sep_letter = ",sep_letter
			filedict[sep] = sep_letter
			ind += 1
		ind = filemap.index("wordref")
		for sep in index_file_list:
			filemap.insert(ind+1,sep)
			ind += 1
			#print "sep = ",sep
	else:
		s = ref_create_index(unicode_dict,chaptername)
		if(alfile): all_content += "<p class=\"chapter\" id=\"wordref\"></p>\n"
		if (use_index): all_content +=	mkgen(index_file,s)

	#print "filelist = ",filelist

	############################################
	# INDEX for names
	############################################
	if(use_name_index): 
		s = create_name_index(name_dict,chaptername)
		all_content +=	mkgen(name_file,s)


	############################################
	# Romanic References........
	############################################

	if(use_roman): 
		s = roman_refs(roman_dict,chaptername)
		all_content +=	mkgen(roman_file,s)

	############################################
	# List of figures
	############################################
	if(figlist):
		s = create_fig_refs(figlist,chaptername)
		if(alfile):
			all_content += "<p class=\"chapter\" id=\"figures\"></p>\n"
		if (use_figures): all_content += mkgen(fig_file,s)

	############################################
	# List of Tables
	############################################
	if(tbllist):
		s = create_table_refs(tbllist,chaptername)
		all_content +=	mkgen(table_file,s)

	############################################
	# Create title.xhtml + header for main file
	############################################
	if(alfile):
		(title_form,title) = title_proc(attr_dict,title_file,all_content,ver.script_ver)
	else:
		(title_form,title) = title_proc(attr_dict,title_file,'',ver,script_ver)
		if 'title' in filemap:
			PY = open(title_file,"w")
			PY.write(title_form.encode('utf-8'))
			PY.close()
			
	############################################
	# Make Table of Contents file 'toc_file'
	############################################
	uniq = mktoc(alfile,toc_file,title,ver,content_list,filemap,filedict,lev_toc)

	# Epub3 version
	uniq3 = mknav(alfile,toc3_file,title,ver,content_list,filemap,filedict,lev_toc)
	
	if (use_random):
		mkrand(random_file,content_list)

	if(alfile):
		PB = open(alfile,"w")
		PB.write(re_utf(title_form))
		PB.close()
		#mkgenhtml(alfile,all_content)


	# Add figure jpgs to list needed in EPUB
	jpeglist +=  used_fig_list
        for check in copied_jpgs:
            if check in jpeglist:
                pass
            else:
                jpeglist.append(check)
                print "adding ",check, "to jpeglist"
	#print "jpeglist = ",jpeglist


	############################################
	# Make Contents file 'content_file'
	############################################
	mkcontent(alfile,content_file,filelist,jpeglist,jslist,headings,title,ver,script_ver,uniq)


	############################################
	# Copy images from ./images dir to Epub build location
	############################################
	ok = commands.getstatusoutput('mkdir ./efiles/OPS/images')
	if (ok):
		for i in used_fig_list:
			commands.getstatusoutput("cp ./images/"+i+".jpg ./efiles/OPS/images/ ")

 	##################################################
	# Check Usage
	##################################################
	unused_items = ''

	if (use_phrases):
		not_used_phrases = check_usage_lowercase(phr_noparen,unicode_dict)
		for p in not_used_phrases:
			unused_items += p+"\n"
			print p, " index item not used!"
	else:
		pass
		#print "Not using phrase index"

	if (use_index):
		(used_index,not_used_index) = check_usage(word_index,unicode_dict)
		for p in not_used_index:
			unused_items += p+"\n"
			#print p, " index item not used!"
	else:
		pass
		#print "Not using general index"

	if(use_name_index): 
		# check unused phrases?
		(used_names,not_used_names) = check_usage(name_index,name_dict)
		for p in not_used_names:
			unused_items += p+"\n"
			print p, " name item not used!"
		if (len(unused_items)>0): list2utffile(not_used_names,"unused_names.txt")
		list2utffile(used_names,"used_names.txt")
	else:
		pass
		#print "Not using name index"

	# Write unused items to file
	if (debug): str2utffile(unused_items,dbfile)
	#print unused_items
	#zipper('efiles',outputfile)
	zip_files('efiles','../'+output_filename)
	if (debug_efiles):
            print "keeping efiles..."
        else:
            print "removing efiles..."
            shutil.rmtree('efiles')

        if (logfile): sys.stdout = sys.__stdout__              # remember to reset sys.stdout!
        # convert list to string and then write to file
        l = " ".join(outdump.content)
	if (len(l)>1):
		str2utffile(l,'pyepub.log')



def sortedDictValues(adict):
    keys = adict.keys()
    keys.sort()
    return map(adict.get, keys)

def mkcontent(alfile,content_file,filelist,jpeglist,jslist,headings,title,ver,scr_ver,uniq):
	PF = open(content_file,"w")
	(file_defs,file_items) = mkitems(alfile,filelist,headings)
	file_defs += mkjpglist(jpeglist)
	file_defs += mkjslist(jslist)
	t = datetime.datetime.now()
	s = content_form.substitute( { 
			'title' : title['title'], 
			'ver' : ver,
			'scr_ver' : scr_ver,
			'author' : title['author'], 
			'publisher' : title['publisher'], 
			'uniq' : uniq,
			'isbn' : title['isbn'], 
			'file_items' : file_items,
			'file_defs' : file_defs,
			'subject' : title['subject'],
			'date' : title['date'], 
			'time' : t.strftime("%Y-%m-%dT%TZ"),
			'copyright' : title['copyright'], 
			'description' : title['description'] } )
	PF.write(re_utf(s))
	PF.close()
	return(uniq)

	


def mkitems(alfile,list,headings):
	file_defs = ''
	file_items = ''
	if(alfile):
		c = 'single'
		file_items +=  mkref(c)
		file_defs  +=  mkxhtmlitem(c)
		for h in list:	
			if(h != 'main'):
				#print "h = ",h
				file_items +=  mkref(h)
				file_defs  +=  mkxhtmlitem2(h,c)
		return(file_defs,file_items)
	else:
		for h in list:	
			if(h == 'main'):
				for i in xrange(0,headings):
					c = h+'%03d'%i
					file_items +=  mkref(c)
					file_defs  +=  mkxhtmlitem(c)
			else:
				file_defs  +=  mkxhtmlitem(h)
				file_items +=  mkref(h)
		return(file_defs,file_items)


def mkjpglist(list):
	s = ''
	for i in list:
		s += "<item id=\"img_"+i+"\"  href=\"images/"+i+".jpg\"  media-type=\"image/jpeg\"/>\n"
	return(s)

def mkjslist(list):
	s = ''
	for i in list:
		s += "<item id=\"js_"+i+"\"  href=\""+i+".js\"  media-type=\"text/plain\"/>\n"
	return(s)

def mkxhtmllist(list):
	s = ''
	for i in list:	s += mkxhtmlitem(i)
	return(s)

def mkxhtmlitem(i):
	if (i=='random'):
		s = "<item id=\""+i+"\"  href=\""+i+".xhtml\"  media-type=\"application/xhtml+xml\" properties=\"scripted\"/>\n"
	else:
		s = "<item id=\""+i+"\"  href=\""+i+".xhtml\"  media-type=\"application/xhtml+xml\"/>\n"
	return(s)

def mkxhtmlitem2(i,r):
	s = "<item id=\""+i+"\"  href=\""+r+".xhtml\"  media-type=\"application/xhtml+xml\"/>\n"
	return(s)

def mkreflist(list):
	s = ''
	for i in list:	s += mkref(i)
	return(s)

def mkref(i):
	s = "<itemref idref=\""+i+"\"  linear=\"yes\"/>\n"
	return(s)


def mknavpoint(root,frag,title,c):
	s = "<navPoint class=\"section\" id=\"sec"+str(c)+"\" playOrder=\""+str(c)+"\">"
	s += "<navLabel><text>"+title+"</text></navLabel>"
	if(frag!=""):
		s += "<content src=\""+frag+".xhtml#"+root+"\"/></navPoint>\n"
	else:
		s += "<content src=\""+root+".xhtml\"/></navPoint>\n"
	return(s)

def mknavpoint_open(root,frag,title,c):
	s = "<navPoint class=\"section\" id=\"sec"+str(c)+"\" playOrder=\""+str(c)+"\">"
	s += "<navLabel><text>"+title+"</text></navLabel>"
	if(frag!=""):
		s += "<content src=\""+frag+".xhtml#"+root+"\"/>\n"
	else:
		s += "<content src=\""+root+".xhtml\"/>\n"
	return(s)

def mknavpoint_open_frag(root,frag,title,c):
	s = "<navPoint class=\"section\" id=\"sec"+str(c)+"\" playOrder=\""+str(c)+"\">"
	s += "<navLabel><text>"+title+"</text></navLabel>"
	if(root==""):
		s += "<content src=\"#head"+str(frag)+"\"/>\n"
	else:
		s += "<content src=\""+root+".xhtml#head"+str(frag)+"\"/>\n"
	return(s)



def mktoc(alfile,tfile,title,ver,content_list,filemap,filedict,lev_toc):
	otherletters = re.compile("wordref_")
	PB = open(tfile,"w")
	uniq = str(uuid.uuid4())
	s = toc_form.substitute( {'title' : title['title'], 
				  'author' : title['author'],
				  'ver' : ver ,
				  'uniq' : uniq })
	c = 1
	lev = 0
	wordref_found = 0
	if(alfile):
		r = 'single'
	else:
		r = ''
	# order is important!
	#print filemap
	for k in filemap:
		# assume k in filemap is also in filedict!
		try:
			v = filedict[k]
		except:
			print "Missing heading for ",k,"-> using",k
			print start_bold_red+"Please add to headings.txt"+end_color
			v = k
		#print "k,v in toc = ",k,v
		if(k == 'main'):
			prev_lev = 1
			levs_open = 0
			first = 1
			#print "nav..main"
			for l in content_list:
				(t,f,n,lev) = l
				#print "t,n,lev = ",t,n,lev
				if (lev < lev_toc):
					# Remove Footnote ref from here
                                        t = capitalize_english(t) # capitalize()
                                        #print "(title,filename,frag,level) = ",l
					rot = "main"+'%03d'%f
					if(alfile): rot = 'single'
					stmp = mknavpoint_open_frag(rot,n,t,c)
					if (first == 1):
						first = 0
					elif (lev > prev_lev):
						levs_open += 1
					elif (lev == prev_lev):
						stmp = "</navPoint>\n" + stmp
					elif (lev < prev_lev):
						#print "lev,prev_lel = ",lev,prev_lev
						#levs_open += 1
						for i in xrange(0,prev_lev-lev+1):
							levs_open -= 1
							stmp = "</navPoint>\n" + stmp
					c = c+1
					prev_lev = lev
					#sys.stdout.write(str(lev))
					s += stmp
                        #for i in xrange(0,lev/2):	s += "</navPoint>\n"
                        if (lev >= lev_toc):
                            for i in xrange(0,lev_toc-1): s += "</navPoint>\n"
                        else:
                            for i in xrange(0,lev):	s += "</navPoint>\n"
			#print "lev = ",lev, levs_open, s
		elif(k == 'wordref'):
			#print "nav..wordref"
			s += mknavpoint_open(k,r,v,c)
			c = c+1
			wordref_found = 1
		elif(wordref_found == 1) and (not otherletters.match(k)):
			#print "nav..wordref_found/not otherletters"
			#print "K = ",k,v
			s += "</navPoint>\n"
			s += mknavpoint(k,r,v,c)
			wordref_found = 0
			c = c+1
		else:
			#print "nav..else"
			#print "K = ",k,v
			s += mknavpoint(k,r,v,c)
			c = c+1
        #print "last k?",k
        if (k == 'wordref'):
            # need to end differently this case
            s += "</navPoint>\n"
            
		
	s += "</navMap>\n</ncx>\n"
	PB.write(re_utf(s))
	PB.close()
	return(uniq)

def mkrand(rfile,content_list):
	PB = open(rfile,"w")
	cont = ''
	for l in content_list:
		(t,f,n,lev) = l
		cont += "<a href=\"main"+'%03d'%f+".xhtml#head"+str(n)+"\"></a>"
	s = random_form.substitute({"links": cont})
	PB.write(re_utf(s))
	PB.close()


def addnavp(root,frag,title,c):
	s = "\n<li>"
	if(frag!=""):
		s += "<a href=\""+frag+".xhtml#"+root+"\">"
	else:
		s += "<a href=\""+root+".xhtml\">"
	s += title+"</a></li>"
	#print "addnav",s
	return(s)

def addnavp_open(root,frag,title,c):
	s = "\n<li>"
	if(frag!=""):
		s += "<a href=\""+frag+".xhtml#"+root+">"
	else:
		s += "<a href=\""+root+".xhtml\">"
	s += title+"</a></li>"
	#print "addnavp_open",s
	return(s)

def addnavp_open_frag(root,frag,title,c):
	s = "\n<li>"
	if(root==""):
		s += "<a href=\"#head"+str(frag)+"\">"
	else:
		s += "<a href=\""+root+".xhtml#head"+str(frag)+"\">"
	s += title+"</a>"
	#print "addnavp_open_frag",s
	return(s)

# Epub Nav Doc
def mknav(alfile,tfile,title,ver,content_list,filemap,filedict,lev_toc):
	otherletters = re.compile("wordref_")
	PB = open(tfile,"w")
	uniq = str(uuid.uuid4())
	s = nav_form.substitute( {'title' : title['title'], 
				  'author' : title['author'],
				  'ver' : ver ,
				  'uniq' : uniq })
	c = 1
	lev = 0
	wordref_found = 0
	if(alfile):
		r = 'single'
	else:
		r = ''
	# order is important!
	#print filemap
	for k in filemap:
		# assume k in filemap is also in filedict!
		try:
			v = filedict[k]
		except:
			print "Missing heading for ",k,"-> using ",k
			print start_bold_red+"Please add to headings.txt"+end_color
			v = k
		#print "k,v in toc = ",k,v
		if(k == 'main'):
			prev_lev = 1
			levs_open = 0
			first = 1
			for l in content_list:
				(t,f,n,lev) = l
				if (debug_toc): print "lev,t,n = ",lev,t,n
				if (lev < lev_toc):
					# Remove Footnote ref from here
                                        t = capitalize_english(t) # capitalize()
					rot = "main"+'%03d'%f
					if(alfile): rot = 'single'
					stmp = addnavp_open_frag(rot,n,t,c)
					if (first == 1):
                                            # print "first"
                                            first = 0
					elif (lev > prev_lev):
                                            levs_open += 1
                                            #print "lev inc"
                                            stmp = "<ol>" + stmp
					elif (lev == prev_lev):
                                            #print "lev == "
                                            stmp = "</li>" + stmp
					elif (lev < prev_lev):
                                            #print "lev dec "
                                            stmp2 = ""
                                            for i in xrange(0,prev_lev-lev):
                                                #print "lev dec.."
                                                levs_open -= 1
                                                stmp2 = "</li></ol>" + stmp2
                                            stmp = stmp2+"</li>"+stmp
					c = c+1
					prev_lev = lev
					c = c+1
					s += stmp
			#print "end_levels"
                        if (debug_toc): 
                            print "finished with Main, level = ",lev," lev_toc = ",lev_toc
                        if (lev>1): 
                            if (lev >= lev_toc):
                                for i in xrange(0,lev_toc-2): s += "</li>\n</ol>"
                            else:
                                for i in xrange(0,lev-1):	s += "</li>\n</ol>"
                            s += "</li>\n"
                        else:
                            s += "</li>\n"
		elif(k == 'wordref'):
			s += addnavp_open(k,r,v,c)
			c = c+1
			wordref_found = 1
		elif(wordref_found == 1) and (not otherletters.match(k)):
			#print "K = ",k,v
			s += "\n"
			s += addnavp(k,r,v,c)
			wordref_found = 0
			c = c+1
		else:
                    s += addnavp(k,r,v,c)
                    c = c+1
		
	s += "</ol></nav></section></body></html>\n"
	PB.write(re_utf(s))
	PB.close()
	return(uniq)

def image_constr(count, title,cap):
	s = "<div class=\"images\"><img src=\"images/FIG"+'%03d'%count
	s += ".jpg\" alt=\""+title
	s += "\"/><p class=\"image-caption\">" + cap[1:]
	return(s)

def marker_to_link(root,marker,c,offset=0):
	(h,l) = marker
	if(root==''):
		s  = "<a href=\"#line"+str(l)+"\">\t("+str(h-offset)+","+str(l)+")</a>"
	else:
		s  = "<a href=\""+root+'%03d'%h + ".xhtml#line"+str(l)+"\">\t("+str(h-offset)+","+str(l)+")</a>"
	return(s)

def wrap_h(n,l,lev):
#	s = "<br /><p class=\"chapter\" id=\""+n+"\"><h"+str(lev)+">"+l+"</h"+str(lev)+"><br /></p>"
	s = "<div class=\"chapter\" id=\""+n+"\"><h"+str(lev)+">"+l+"</h"+str(lev)+"></div>"
	return(s)


def add_to_dict(dict,k,add):
	if(dict.has_key(k)):
		old = dict[k]
		if add in old:
			pass
		else:
			old.append(add)
			dict[k] = old
	else:
		dict[k] = [add]
	return(dict)

def inc_dict(dict,k):
	if(dict.has_key(k)):
		dict[k] += 1
	else:
		dict[k] = 1
	return(dict)


# return list of non-used items
def check_usage(ref,created):
	not_used = []
	used = []
	for i in ref:
		if i in created.keys():
			used.append(i)
		else:
			not_used.append(i)
	return(used,not_used)

# non-used items but 1st transform keys in created to lowercase
def check_usage_lowercase(ref,created):
	not_used = []
	cr = []
	for k in created.keys():
		cr.append(k.lower())
	for i in ref:
		if i in cr:
			pass
		else:
			not_used.append(i)
	return(not_used)

############
def str2utffile(l,fn):
	PTMP = open(fn,"w")
	PTMP.write(re_utf(l))
	PTMP.close()

def list2utffile(lis,fn):
	PTMP = open(fn,"w")
	if (len(lis)>1):
		for l in lis:
			PTMP.write(l.encode('utf-8')+"\n")
	else:
		try:
			PTMP.write(lis[0].encode('utf-8')+"\n")
		except:
			print lis
	PTMP.close()



def utffile2str(fn):
	s = ''
	try:
		b = codecs.open(fn,encoding='utf-8')
		for l in b: s += l
		b.close()
	except:
		print "Couldn't open/find ",fn
	return(s)

def utffile2list(fn):
	s = []
	try:
		b = codecs.open(fn,encoding='utf-8')
		for l in b: s.append(l.strip())
		b.close()
	except:
		print "Couldn't open/find ",fn
	return(s)

def mkgen(fn,content):
	s = generic_form.substitute({'content' : content})
	PB = open(fn,"w")
	PB.write(re_utf(s))
	PB.close()
	return(content)


def mkgenhtml(fn,content):
	s = generic_form.substitute({'content' : content})
	PB = open(fn,"w")
	PB.write(re_utf(s))
	PB.close()

def mkgenpopuphtml(fn,content,popups):
	s = popup_form.substitute({'content' : content, 'popups' : popups})
	PB = open(fn,"w")
	PB.write(re_utf(s))
	PB.close()

def mkgentxt(fn,content):
	PB = open(fn,"w")
	PB.write(re_utf(content))
	PB.close()

def rawfile_spaces(fl):
	res = []
	dim = {}
	tmp1 = codecs.open(fl,encoding='utf-8')
	pre = 0
	use_pre = 0
	for line in tmp1:
		reflen = len(line)
		blank = string.lstrip(line)
		new_line = string.lstrip(line)
		srplen = len(new_line)
		# now remove right whitespace
		new_line = string.rstrip(new_line)
		new_len = len(new_line)
		diff =  reflen - srplen
		if (use_pre and (new_len > 0)):
			#if (diff > 20):	print diff," diff ",line
			if (diff == 0):
				if (pre): new_line = "}\n"+new_line
				pre = 0
			elif (diff == 1):
				if (pre): new_line = "}\n\t"+new_line
				pre = 0
			elif (diff < 3):
				if (pre): new_line = "}\n\t\t"+new_line
				pre = 0
			else:
				if(not pre):
					new_line = "{"+new_line
					pre = 1
			res.append( ((new_line+"\n"), diff ) )
			inc_dict(dim,diff)
		else:
			# blank, still add
			res.append( ("\n", 0) )
	return(dim,res)

def rawfiles2html(flist,lev_break,Max_Lines):
	tmp1 = ''
	tcQ=0
	atc=0
	doing_poem=0
	farsi=0
	doing_image=0
	doing_table = 0
	fig_title=''
	table_titles=[]
	cap_count = 1
	line_count = 0
	line_count_this_heading = 0
	content_list  = []
	scontent_list = []
	sfarsi_list = []
	fig_list = []
	html = []
	tmplist  = []
        fnlist = [] # footnote list
	tmp_fig_list  = []
	#xt_content = ''
	for f in flist:
		tmp1 = codecs.open(f,encoding='utf-8')
		for line in tmp1:
			#xt_content += line
			# html-ize "&"
			line = amprefs.sub("&amp;",line)
			rem = line.split('>',1)
			reflen = len(line)
			srplen = len(string.lstrip(line))
			norm_proc = not doing_image and not doing_poem
			# match line beginning with a character
			if (cereg.match(line) and doing_image):
				if (debug_option): print "option end fig 1", line
				tmplist.append("</p></div>\n")
				doing_image = 0
				#print "clearing doing_image"
				new_line = '' #line[2:]
			elif (ereg.match(line) and doing_poem):
				if (debug_option): print "option end poem 2", line
				#if (farsi):
				#	tmplist.append("</pre>\n")
				#else:
				#	tmplist.append("</pre>\n")
				doing_poem = 0
				new_line = line[1:]
			elif (tblreg.match(line)):
				if (debug_option): print "option start table 3", line
				# Table
				if(doing_table == 0):
					table_count = len(table_titles)+1
					#print "starting table",line
					s = "<table class=\"table"+str(table_count)+"\"><tr>\n"
				else:   s = "<tr>"
				cells = line.split("|")
				# remove 1st & last elements of list
				cells = cells[1:-1]
				for cell in cells:
					s += "<td>"+cell+"</td>\n"
				s += "</tr>"
				doing_table = 1
				new_line = s
				tmplist.append(new_line+"\n")
				#print new_line
                        elif (sfreg.match(line)):
                            if (debug_option): print "option footnote",line
                            new_line = ''
                            fnlist.append(line+"\n")
                        elif (spreg.match(line)):
                            if (debug_option): print "option page-break",line
			    new_line = '<div style="page-break-before:always;"></div>'
			    tmplist.append(new_line+"\n")
			# must be end of table, MUST have blank line or no extra processing
			elif (doing_table):
				if (debug_option): print "option table 4", line
				doing_table = 0
				table_titles.append(string.strip(line))
				new_line = "</table>"
				tmplist.append(new_line+"\n")
			elif (doing_poem):
				if (debug_option): print "option poem 5", line
				new_line = line[:-1]
				before_chop_len = len(new_line)
				new_line = new_line.lstrip()
				diff_len = before_chop_len-len(new_line)
				if (diff_len > 0):
					#print diff_len, " for line",new_line
					for i in xrange(0,diff_len):
						new_line = "&#160;"+new_line
				if (blank_line.match(line)):
					tmplist.append("<p></p>\n")
				else:
                                    if (farsi):
					tmplist.append("<p class=\"farsi\">"+new_line+"</p>\n")
                                    else:
					tmplist.append("<p class=\"poem\">"+new_line+"</p>\n")
			#
			else: 
				#
				if (start_2tab.match(line)):
					if (debug_option): print "option 6", line
					#print "2 tabs ",line
					# Complete indented paragraph
					new_line = "<p class=\"ind\">" + line + "</p>"
				elif (start_tab.match(line)):
					if (debug_option): print "option 7", line
					#print "1 tabs ",line
					# Class par - used for indenting 1st part of line
					new_line = "<p class=\"par\">" + line + "</p>"
				elif (wreg.match(line)):
					if (debug_option): print "option 8", line
					if(doing_image):
						new_line = line
					else:
						new_line = "<p class=\"default\">" + line + "</p>"
				elif (preg.match(line)):
					if (debug_option): print "option start poem 9", line
					# starting poem
					#new_line = "<p class='pre'>" + line[1:] # remove "{"
					new_line = "<p></p> "
					doing_poem = 1
					farsi = 0
				elif (freg.match(line)):
					if (debug_option): print "option start farsi poem 10", line
					#new_line = "<p class='farsi'>" + line[1:] # remove "["
					new_line = "<p></p> "
					doing_poem = 1
					farsi = 1
				elif (atreg.match(line)):
					if (debug_option): print "option poem/ref attribution", line
                                        if (line[1] == '('):
                                            # Strip leading "-"  use class ref
                                            new_line = "<p class=\"ref\">" + line[1:] + "</p><p></p>"
                                        else:
                                            new_line = "<p class=\"poet\">" + line + "</p><p></p>"
				elif (astreg.match(line)):
					if (debug_option): print "option italic attribution", line
					new_line = "<p><em>" + line[1:] + "</em></p>"
				elif (npreg.match(line)):
					if (debug_option): print "option new poem", line
					new_line = line[1:-1]
					before_chop_len = len(new_line)
					new_line = new_line.lstrip()
					diff_len = before_chop_len-len(new_line)
					if (diff_len > 0):
						#print diff_len, " for line",new_line
						for i in xrange(0,diff_len):
							new_line = "&#160;"+new_line
					new_line = "<p class=\"poem\">" + new_line + "</p>"
				elif (csreg.match(line)):
					if (debug_option): print "option start fig 11", line
					# starting image caption
					fig_title = string.strip(line[1:])
					new_line = image_constr(cap_count,fig_title,line)
					doing_image = 1
					tmp_fig_list.append("FIG"+'%03d'%cap_count)
					cap_count += 1
					#print "setting cap",cap_count
				elif (ereg.match(line)):
					if (debug_option): print "option end poem 12", line
					# ending poem
					tmplist.append("<p>ENDPOEM</p>\n")
					doing_poem = 0
				elif (reg.match(line)):
					if (debug_parse): print "option Heading? 13", line
					# <\w>
					sp = reg.match(line)
					l = (sp.group(0))[-1]
					# for debug_parse....
					#sys.stdout.write(l)
					#
					cap_line = (rem[1][:-1]).strip()
					#print "character found on line ",l,sp.group(0),
					try:
						# heading types are numeric
						lev = int(l)
                                                #print "found level = ",lev
                                                ebreak = (line_count_this_heading > Max_Lines)
						if ((lev < lev_break) or ebreak):
                                                    if (debug_parse or debug_break): 
                                                        print "xhtml page ",atc," break",lev_break,
                                                        print " lcth ",line_count_this_heading,line.strip()
                                                    if (debug_break):
                                                        if (ebreak and (lev > 1)):
                                                            print "Breaking due to Max_Lines begin exceeded at level ",lev, line
                                                        else:
                                                            print "Otherwise breaking at level ",lev,line
                                                    if (tcQ > 0 or ebreak): 
                                                        html.append(tmplist)
                                                        fig_list.append(tmp_fig_list)
                                                        tmplist = []
                                                        tmp_fig_list = []
                                                    line_count_this_heading = 0
                                                    atc += 1

						mtc = atc-1
						if (mtc<0): mtc = 0

						new_line = wrap_h("head"+str(tcQ), cap_line,lev)
						if (start_paren.search(cap_line)):
							# Strip paren and everything between
							#print "line = ",cap_line
							(eng,farsp) = cap_line.rsplit("(",1)
							#print eng,"------",farsp
							#print "f = ",farsp
							(fars,p) = farsp.rsplit(")",1) # add ,1 for now!!!
							sfarsi_list.append( (fars, mtc, tcQ) )
							strp_line = capitalize_english(eng)
						else:
							strp_line = capitalize_english(cap_line)
							#print "strp_line = ",strp_line
						# Search for "The ..", move "The" to end of line for sorted
						# content. i.e "The Self" becomes "Self, The"
						tmpthe = the.match(strp_line)
						if(tmpthe):
							strp_line = the.sub('',strp_line)
							strp_line = strp_line.rstrip()+", The"
						
						indefA = indef.match(strp_line)
						if (indefA):
							strp_line = indef.sub('',strp_line)
							strp_line = strp_line.rstrip()+", A"
							#new_line = cap_line

						#print "Append to content list ",cap_line, mtc, tc, lev
                                                #print "(1,2,3,4) = ",cap_line, mtc, tc, lev
						content_list.append( (cap_line, mtc, tcQ, lev) )
						scontent_list.append( (strp_line, mtc, tcQ) )

						#kgentxt(cap_line+".txt",txt_content)
						txt_content = ''
						tcQ = tcQ+1
					except:
						# line starting <p ...., can go as is
						if (l=='p'):
							new_line = line
						elif (l=='c'):
							new_line = "<p class='center'>"+line[3:]+"</p>"
						else:
							print "exception for ",l,"...",line
						#if (debug_parse): print "exception for ",l,"...",line
						#new_line = line[:-1]
				else: 
					if (debug_parse): print "option else 13", line
					tline = string.strip(line)
					if ((len(tline)>1) and debug_parse):
						print "line = ",line_count," 1st char =\"",tline[0],"\"",tline
					new_line = line[:-1]
                                        if (len(tline)==0):
                                            new_line = "<br></br>"
                                        # ??????????????? NOW COMMENT OUT NEXT LINE
					#new_line = "<p></p>"
                                        #???????????????????

					#tmplist.append("<p>ELSEELSE</p>\n")
				#if(doing_image): tmplist.append(new_line.strip())
				#else: 		tmplist.append(new_line+"\n")
		 		tmplist.append(new_line+"\n")
				# cap or pre 
				#tmplist.append(line+"\n")

			line_count += 1
			line_count_this_heading += 1
	html.append(tmplist) # not sure if this is bullet proof
	fig_list.append(tmp_fig_list)
	return(html,content_list,scontent_list,sfarsi_list,fig_list,table_titles,fnlist)

### used in rawfile2txt
def txtlinesub(line):
	line = preg.sub("",line)
	line = ereg.sub("",line)
	line = cereg.sub("",line)
	line = csreg.sub("",line)
	line = tblreg.sub("",line)
	line = allbrefs.sub("",line)
	line = astreg.sub("",line)
	line = atreg1.sub("",line)
	return(line)

####
def rawfile2txt(f,author,title,levels):
	use_ascii()
	txt_content = ''
	txt_file_list = '#!/bin/csh\n'
	tc = 0
	tmp1 = codecs.open(f,encoding='utf-8')
	for line in tmp1:
		# remove <i> or </i> 
		line = ireg.sub("",line)
		# remove footnote
		if sfreg.match(line):	line = ''
		# remove footnote references
		line = frefs.sub("",line)
		# remove line with leading %
		#line = npreg.sub("",line)
		if (npreg.match(line)): line = ''
		if (atreg1.search(line)): line = ''
		if (reg.match(line)):
			# <\w>
			sp = reg.match(line)
			l = (sp.group(0))[-1]
			rem = line.split('>',1)
			cap_line = (rem[1][:-1]).strip()
			#print "character found on line ",l,sp.group(0),
			# heading types are numeric
			try:
				lev = int(l)
				if (lev < levels):
					if (tc>0):
						fn = "./txt/"+'%03d'%tc+".txt"
						tstr = '%03d'%tc
						txt_file_list += "cat 5.mp3 >> "+tstr+".mp3\n"
						eng = title_clean.sub("",eng)
						eng = capitalize_english(eng)
						txt_file_list += "id3v2 -t \""+eng+"\" -a \""
						txt_file_list += author+"\" -A \""+title+"\" -y 2012 -g speech -T "+tstr+" "+tstr+".mp3\n"
						txt_file_list += "eyeD3 --remove-image "+tstr+".mp3\n"
						txt_file_list += "eyeD3 --add-image=cover.jpg:FRONT_COVER "+tstr+".mp3\n"
						txt_file_list += "mv "+tstr+".mp3 \""+author+"_"+tstr+"_"+eng+"\".mp3\n"
						#print fn
						mkgentxt(de_unify(fn),txt_content)
					tc = tc+1
					if (start_paren.search(cap_line)):
						(eng,farsp) = cap_line.split("(",1)
						eng = eng.strip()
					else:
						eng = cap_line.strip()

					txt_content = cap_line+".\n"
				else:
					txt_content += txtlinesub(cap_line)
			except:
				# non-numeric 
				line = unhtml.sub("",line)
				txt_content += txtlinesub(line)

		else:
			txt_content += txtlinesub(line)

	mkgentxt("./txt/txt.csh",txt_file_list)

#----
def conv_rawfiles(flist):
	pre=0
	html = []
	tmp1 = codecs.open(flist,encoding='utf-8')
	for line in tmp1:
		sp = reg.match(line)
		if (not start_space.match(line) and pre):
			html.append("}\n")
			pre = 0
		if (sp):
			l = (sp.group(0))[-1]
			if (l=='p'):	new_line = line[3:]
			elif (l=='b'):	new_line = "\t" + line[3:]
			elif (l=='i'):	new_line = "\t\t" + line[3:]
			elif (l=='q'):
				new_line = "{" + line[3:]
				pre = 1
			else:
				new_line = line[:-1]
			html.append(new_line+"\n")
		else:
			html.append(line)
	return(html)


# input file, out abbreviation file, output biblio filename (for use in abbrev file)
def biblio_proc(bibfile,use_abbrev,abrfile,obfile=""):
	abb = []
        (root,sfile) = os.path.split(obfile)
	s = utffile2str(bibfile)
	if(s != ''):
		x = json.loads(s)
		biblio_dict = x['bib']
		l = len(biblio_dict)
		for i in xrange(l):
			try:
				s =  "<p><a href=\""+sfile+"#"+biblio_dict[i]['abbrev'] + "\">"
				s += biblio_dict[i]['abbrev']+ "</a> : "+biblio_dict[i]['title'] + "</p>\n"
				abb.append(s)
			except:
				pass
		# sort abbreviations!
		out = sorted(abb)

		l = ''
		for line in out:	l += line
		if (use_abbrev): 
			print "Creating Abbreviation file",abrfile
			mkgenhtml(abrfile,l)
		return(biblio_dict)
	else:
		return(None)

# Create dictionary of "abbrev":"title/name"
def biblio_abbrev(biblio_dict):
	abb = {}
	l = len(biblio_dict)
	for i in xrange(l):
		ok = True
		try:
			has_abbrev = biblio_dict[i]['abbrev']
		except:
			ok = False
		if (ok):
			# Just use "last" name by splitting on ','
			names = (biblio_dict[i]['author']).split(",")
			titl = biblio_dict[i]['title']
			words = titl.split()
			abb[has_abbrev] = names[0] + " : "+ words[0]
			#abb[has_abbrev] = biblio_dict[i]['title'] + " : " + names[0]
	return(abb)

############################################
# Romanic References........
############################################

def roman_refs(kdict,file=""):
	s = "<div id=\"Index_Roman\"><h1>Index for Koran References (Chapter/Verse)</h1></div><br />\n<div class=\"references\">\n"

	for k in sorted(kdict.keys()):
		items = kdict[k]
		#print "k = ",k,items
		chap = int(k)/1000
		verse = int(k) - 1000*chap
		rk = toroman(int(chap))
		if (chap == 0):
			s += "<p>Error"
		else:
			s += "<p>"+rk+":"+str(verse)+"  "
		item_num=0
		for (h,l) in items:
			s += marker_to_link(file,(h,l),item_num+1)
			if (len(items) > 1 and item_num < len(items)-1) :	s += ","
			item_num = item_num+1
		s += "</p>\n"
	s += "</div>\n"
	return(s)



############################################
# go through reference dictionary
############################################
def make_biblio(biblio_dict):
	WRAP = 5
	l = len(biblio_dict)
	lstr = "<div id=\"Bibliography\"><h1>Bibliography</h1></div><br />\n"
	prev_aut = ''
	t = ''
	# for each book, write out info + create reference links back to text
	for i in xrange(l):
		aut = biblio_dict[i]['author']
		# if no author, use translator
		if (aut == ''): aut = biblio_dict[i]['translator']
		if (aut == prev_aut): aut = ''
		prev_aut = biblio_dict[i]['author']
		if (biblio_dict[i].has_key('abbrev')):
			t += "<p class=\"under\">"+aut+"</p><span class=\"ref\" id=\""
			t += biblio_dict[i]['abbrev']+"\"></span>"
			t += "<p class='book_ref'><em>"
			t += biblio_dict[i]['title']+"</em>\n"
		else:
			t += "<p class=\"under\">"+aut+"</p>"
			t += "<p class='book_ref'><em>"
			t += biblio_dict[i]['title']+"</em>\n"
		try:
			s = biblio_dict[i]['published']
		except:
			s = ''
		t += s+"</p>\n"
		try:
			s = biblio_dict[i]['description']
			t += "<p class='book_ref'>Description: "+s+"</p>\n"
		except:
			s = ''
		if (biblio_dict[i].has_key('abbrev')):
			k = biblio_dict[i]['abbrev']
			t += "<p class='book_ref'>Abbreviation: "+k+"</p>\n"


	lstr += de_unify(t)
	return(lstr)

############################################
# go through reference dictionary
############################################
def create_biblio_refs(aldict,fileroot=''):
	WRAP = 5
	lstr = "<div id=\"Book_References\"><h1>Book References</h1></div><br />\n<div class=\"references\">\n"
	t = ''
	# for each book, write out info + create reference links back to text
	for i in sorted(aldict.keys()):
		t += "<p>"+i
		j = aldict[i]
		c = 1
		for (h,l) in j:
			t += marker_to_link(fileroot,(h,l),c)+","
			if(c > 1 and (c%WRAP == 0)): t += "<br />"
			c = c+1
			# add handle last element
		t += "</p>\n"
	t += "</div>\n"
	lstr += de_unify(t)
	return(lstr)

############################################
# go through reference dictionary
############################################
def create_biblio(biblio_dict,aldict,fileroot=''):
	WRAP = 5
	l = len(biblio_dict)
	lstr = "<div id=\"Bibliography\"><h1>Bibliography</h1></div><br />\n"
	prev_aut = ''
	t = ''
	# for each book, write out info + create reference links back to text
	for i in xrange(l):
		aut = biblio_dict[i]['author']
		# if no author, use translator
		if (aut == ''): aut = biblio_dict[i]['translator']
		if (aut == prev_aut): aut = ''
		prev_aut = biblio_dict[i]['author']
		if (biblio_dict[i].has_key('abbrev')):
			t += "<p class=\"under\">"+aut+"</p><span class=\"ref\" id=\""
			t += biblio_dict[i]['abbrev']+"\"></span>"
			t += "<p class='book_ref'><em>"
			t += biblio_dict[i]['title']+"</em>\n"
		else:
			t += "<p class=\"under\">"+aut+"</p>"
			t += "<p class='book_ref'><em>"
			t += biblio_dict[i]['title']+"</em>\n"
		try:
			s = biblio_dict[i]['published']
		except:
			s = ''
		t += s+"</p>\n"
		try:
			s = biblio_dict[i]['description']
			t += "<p class='book_ref'>Description: "+s+"</p>\n"
		except:
			s = ''
		if (biblio_dict[i].has_key('abbrev')):
			k = biblio_dict[i]['abbrev']
			t += "<p class='book_ref'>Abbreviation: "+k
			t += ", References:-\n"
			if biblio_dict[i]['abbrev'] in aldict.keys():
				j = aldict[k]
				c = 1
				for (h,l) in j:
					t += marker_to_link(fileroot,(h,l),c)+","
					if(c > 1 and (c%WRAP == 0)): t += "<br />"
					c = c+1
				# add handle last element
			t += "</p>\n"


	lstr += de_unify(t)
	return(lstr)


def create_fig_refs(flist,file=""):
	s = "<div id=\"Figures\"><h1>List of Figures</h1></div><br />\n"
	fc = 0
	for l in flist:
		#print "l=",l
		(title,(h,l)) = l
		fc = fc+1
		s += "<p>Figure "+str(fc)
		if (file==""):
			s += "<a href=\"#line"+str(l)+"\">\t"+title+"</a>"
		else:
			s += "<a href=\""+file+'%03d'%h + ".xhtml#line"+str(l)+"\">\t"+title+"</a>"
		s += "</p>\n"
	return(s)

def create_table_refs(flist,file=""):
	s = "<div id=\"Tables\"><h1>List of Tables</h1></div><br />\n"
	fc = 0
	for l in flist:
		#print "l=",l
		(title,(h,l)) = l
		fc = fc+1
		if(string.strip(title) == ''): title = "no title supplied"
		s += "<p>Table "+str(fc)
		if(file==''):
			s += "<a href=\"#line"+str(l)+"\">\t"+title+"</a>"
		else:
			s += "<a href=\""+file+'%03d'%h + ".xhtml#line"+str(l)+"\">\t"+title+"</a>"
		s += "</p>\n"
	return(s)


############################################
# Sorted contents
############################################
def create_sorted_contents(content_list,fileroot=""):
	s = "<h1>Sorted Contents</h1><br />\n"
	sep_char = "+"
	find_plus = re.compile(r'\+')
	newlist = []
	
	# Create new list of strings with Title as artificial 1st part of string
	# this will be removed after sorting and before writing 

	# if "title" has a "+" in it, we're SCREWED!
	# i.e change sep_char above

	for l in content_list:
		(lnk,atc,tc) = l
		#print lnk,atc,tc
		if (find_plus.search(lnk)):
			print "Problem with processing, found ",sep_char, " in titles"
		newlist.append(lnk+sep_char+"<p><a href=\""+fileroot+'%03d'%atc+".xhtml#head"+
			       str(tc)+"\">"+lnk+"</a></p>\n")
		
	# newlist is list of format (title,"+",link)
	# after sorting, remove everything except link part
	for l in sorted(newlist,key=coll.sort_key):
		(lnk,lnk_html) = l.split(sep_char)
		s += lnk_html
	return(s)


############################################
# INDEX
############################################
def ref_create_index(ldict,file='',offset=0):
	s = "<div id=\"Index\"><h1>General Index</h1></div><br />\n<div class=\"references\" style=\"oeb-column-number:auto\">\n"

	# sort phrases and write to file
	for k in sorted(ldict.keys(), key=coll.sort_key):
		# remove parenthesis
		kmp   = pw.sub("",k)
		s += "<p>"+de_unify(kmp)
		#print k,ldict[k]
		items = ldict[k]
		item_num=0
		# iterate through links and create html links back to document
		for (h,l) in items:
			# replaced kmp with 'index'
			s += marker_to_link(file,(h,l),item_num+1,offset)
			if (len(items) > 1 and item_num < len(items)-1) :
				s += ","
			item_num = item_num+1
		s += "</p>\n"
	s += "</div>\n"
	return(s)

############################################
# Split index
############################################
def ref_create_index_split(ldict,file=''):
	first_char = 'z'
	started = 0
	last_ascii = 0
        # sort phrases and write to file
	s = "<div id=\"General_Indexes\"><h1>General Index</h1></div>"
	mkgenhtml("efiles/wordref.xhtml",s)
	index_file_list = []
	s = ''
	#for k in sorted(ldict.keys(), key=coll.sort_key):
	# Need to use English Chars here, but lower case...
	for k in sorted(ldict.keys(), lambda x, y: cmp(x.lower(), y.lower())):
		#print "1st char = ",k[0],k
		if(k[0].lower() != first_char):
			if(not last_ascii):
				#print "Changed 1st char = ",k[0],k
				if(started):
					s += "</div>\n"
					mkgenhtml("efiles/wordref_"+first_char+".xhtml",s)
					index_file_list.append("wordref_"+first_char)
				s = "<div id=\"Index_"+k[0].lower()+"\">"
				s += "<h2>General Index for "+k[0].lower()+"</h2>"
				s += "</div><br />\n<div class=\"references\" style=\"oeb-column-number:auto\">\n"
				first_char = k[0].lower()
				started = 1
				if (k[0].lower() == 'z'): last_ascii = 1

		#print "char = ",char, k
		# remove parenthesis
		kmp   = pw.sub("",k)
		s += "<p>"+de_unify(kmp)
		items = ldict[k]
		item_num=0
		# iterate through links and create html links back to document
		for (h,l) in items:
			# replaced kmp with 'index'
			s += marker_to_link(file,(h,l),item_num+1)
			if (len(items) > 1 and item_num < len(items)-1) :
				s += ","
			item_num = item_num+1
		s += "</p>\n"

	s += "</div>\n"
	mkgenhtml("efiles/wordref_"+first_char+".xhtml",s)
	index_file_list.append("wordref_"+first_char)
	return(index_file_list)

############################################
# name INDEX
############################################
def create_name_index(ilink,fileroot=""):
	s = "<div id=\"Index_for_Names\"><h1>Index for Names</h1></div><br />\n<div class=\"references\" style=\"oeb-column-number:auto\">\n"
	# sort phrases and write to file
        #### May want to change this to write out original index_names list
        # and then search for matches, etc
	#tmp_list = []
	for k in sorted(ilink.keys(), key=coll.sort_key):
		#tmp_list.append(k)
		k_space = fpar.sub(' (',k)
		# add space between name and (
		stmp = "<p>"+k_space
		s += de_unify(stmp)
		# get 1st word
		words = re.split(r"[\(]+",k)
		fword = words[0]
		items = ilink[k]
		item_num=0
		# iterate through links and create html links back to document
		for (h,l) in items:
			s += marker_to_link(fileroot,(h,l),item_num+1)
			if (len(items) > 1 and item_num < len(items)-1) :	s += ","
			item_num = item_num+1
		s += "</p>\n"
	s += "</div>\n"
	return(s)

#----------------------------------------------
# just htmlize footnotes - which have pattern in text
#----------------------------------------------
def htmlize_footnotes(new_line,ftnlist,fnlist,marker,no_embed):
    fnl_pre = "<sup><a epub:type=\"noteref\" href=\"#Foot"
    if (no_embed):
	    return(new_line,ftnlist)
    if (frefs.search(new_line)):
        use_footnotes = []
        ftmp  =  frefs.findall(new_line)
        # num of footnotes on this line (could be > 1)
        nf = len(ftmp)
        fnn = len(ftnlist)
	save_fnn = fnn
	# iterate through all on this line
	for i in xrange(0,nf):
		fnn += 1
                # replace each '†' with html + temp char
                fnl = fnl_pre+str(fnn)+"\">"+tempsub+"</a></sup>"
                new_line = re.sub(dagger,fnl,new_line,1)
                ftnlist.append(marker)
                if (len(fnlist) > 0):
                    get_fn = fnlist.pop(0)
		    #print "got footnote ", get_fn
                    use_footnotes.append(get_fn)
                else:
                    print "mismatch in footnotes"
	# replace all temp chars with '†' again
	new_line = re.sub(tempsub,dagger,new_line)
	#print " footnote line", new_line
        fnn = save_fnn+1
        for fn in use_footnotes:
		#l = amprefs.sub("&amp;",fn) # already done!
		l = frefs.sub("",fn) # Remove dagger itself 
		s = "<aside epub:type=\"footnote\" id=\"Foot"+str(fnn)
		s = s+"\"><p class=\"popup\">"+l+"</p></aside>\n"
		new_line += s
		fnn = fnn+1
	#print " footnote amended line", new_line.encode('utf-8')
    return(new_line,ftnlist)


#----------------------------------------------
# HTMLize References
# Book References are Uppercase + Numbers only
#----------------------------------------------
def htmlize_book_refs(new_line,aldict,abbrev_lookup,marker):
	mr = book_refs3.findall(new_line)
	#for n in mr: print "Found ref? ",n
	# get basic ref
	if (mr):
		# assume only 1 match
		mrp = mr[0][0]
		#print "line = ",new_line," mr = ",mr
		# Get actual abbreviation by splitting and lookup at first word
		try:
			full_title = abbrev_lookup[mrp]
			new_mrp = full_title+" - "+mrp
			# count refs to this book in dict
			mrsub = re.compile(mrp)
			new_line = mrsub.sub(new_mrp,new_line)
			# reconstruct ref
			#base = mr[0][0]+" "+mr[0][1]
			base = mr[0][0]
			aldict = add_to_dict(aldict,base,marker)
		except:
			print start_bold_red+"Issue with Abbreviation?",mrp+end_color,marker

	mr2 = book_refs2.findall(new_line)
	#for n in mr: print "Found ref? ",n
	# get basic ref
	if (mr2):
		#if (len(mr2) > 1): print "multiple refs at line ",mr2,len(mr2)
		for i in xrange(0,len(mr2)):
			# assume only 1 match
			mrp = mr2[i][0]
			# Get actual abbreviation by splitting and lookup at first word
			try:
				full_title = abbrev_lookup[mrp]
				new_mrp = full_title+" - "+mrp
				# count refs to this book in dict
				mrsub = re.compile(mrp)
				new_line = mrsub.sub(new_mrp,new_line)
				# reconstruct ref
				#base = mr2[i][0]+" "+mr2[i][1]
				base = mr2[i][0]
				aldict = add_to_dict(aldict,base,marker)
			except:
				print start_bold_red+"Issue with Abbreviation?",mrp+end_color,marker

		#if (len(mr2) > 1): print "multiple refs at line ",new_line

	mr1 = book_refs1.findall(new_line)
	if (mr1):
		# assume only 1 match
		#print start_bold_red+"Exception case",mr1[0]+end_color
		mrp = mr1[0]
		try:
			full_title = abbrev_lookup[mrp]
			new_mrp = full_title+" - "+mrp
			mrsub = re.compile(mrp)
			new_line = mrsub.sub(new_mrp,new_line)
		# reconstruct ref
			base = mrp
			aldict = add_to_dict(aldict,base,marker)
		except:
			print start_bold_red+"Issue with Abbreviation?",mrp+end_color,marker

	return(new_line,aldict)

#----------------------------------------------
# look for phrases so they can be emphasized
# phrases are inside paren such as (eshq-e)
#----------------------------------------------

def htmlize_index(new_line,phr,phr2,ldict,marker,no_embed,use_paren):
	saved_line = new_line
	if(use_paren):
		mf = fphrases.findall(new_line)
	else:
		mf = []
	# ">" for words at start of line
	#mf2 = re.split(ur"[ \b\t,.;:\?\!\]\[><’‘“”\"^\)]",new_line)
	mf2 = re.split(ur"[ \b\t,.;:\?\!\]\[><‘“”\"^\)]",new_line)
	for m in mf2: 
		# remove paren
		tmp = pw.sub("",m)
		# remove ending apostrophe
		tmp = end_apos.sub("",tmp)
		# remove ending 's
		tmp = end_poss.sub("",tmp)
		# remove angle brackets < and >
		#tmp = end_angle_br.sub("",tmp)
		# removing starting '
		tmp = starting_apos.sub("",tmp)
		mf.append(tmp)
	# check for single words in paren & add to list (removing duplicates)
	mf3 = wphrases.findall(new_line)
	for m in mf3: mf.append(pw.sub("",m))
	mf = list(set(mf))
	#print "mf = ",mf
	if (mf):
		for n in mf:
			# check if in list
			xf   = n
			if n.lower() in phr:
				#print "n.lower() of ",n.lower()," is in phr"
				if(use_paren):
					newx = re.compile(r"\("+xf+"\)",re.UNICODE)
					yf   = pw.sub("",n)
				else:
					newx = re.compile(xf,re.UNICODE)
					yf   = xf
				# links are "index"+number (replaced yf with index)
				if(not no_embed):
					new_line = newx.sub("<span class=\"ref\"><span class=\"idx\">"+xf
							    +"</span></span>",new_line,1)
				# make list of links
				nl = n.lower()
#--------------------------------------------------------------------------------------------------------------------------------------------------
# should this be
#				sub_word   = pw.sub("",n)
# or
#				sub_word   = pw.sub("",nl)
#?
# use lower case always?
#--------------------------------------------------------------------------------------------------------------------------------------------------
				sub_word   = pw.sub("",n)
				#print "n = ",n," sub_word = ",sub_word
				ldict = add_to_dict(ldict,sub_word,marker)
				#print ldict
				# Non-paren list
			#if n.lower() in phr2:
			if n in phr2:
				#print "n of ",n," is in phr2"
				newx = re.compile(xf,re.UNICODE)
				yf   = xf

				######################################
				where = saved_line.find(xf)
				temp_s = ''
				for i in xrange(0,59):
					i_off = i + where - 30
					if (i_off > 0 and i_off < len(saved_line)):
						temp_s += saved_line[i_off]
				#print "Item ",n," ",temp_s
				temp_s = n + " / " + temp_s + "\n"
				#PBDBG.write(temp_s.encode('utf-8'))
				####temp debug

				# links are "index"+number (replaced yf with index)
				if (not no_embed):
					new_line = newx.sub("<span class=\"ref\"><span class=\"idx\">"+xf
							    +"</span></span>",new_line,1)
				# make list of links
				#nl = n.lower()
				nl = n
				sub_word   = pw.sub("",nl)
				ldict = add_to_dict(ldict,sub_word,marker)
				#print ldict
	return(new_line,ldict)


def italize_index(new_line,phr,phr_noparen,ldict,marker,no_embed):
	# find phrases in parenthesis
	mf = fphrases.findall(new_line)
	##	print "paren mf = ",mf
	# ">" for words at start of line
	#	mf_paren = re.split(ur"[ \b\t,.;:\?\!\]\[><‘“”\"^\)]",new_line)
	#	no longer split on ‘ 
	mf_paren = re.split(ur"[ \b\t,.;:\?\!\]\[><“”\"^\)]",new_line)
	##	print "split mf",mf
	for m in mf_paren: 
		# remove paren
		tmp = pw.sub("",m)
		# remove ending apostrophe
		tmp = end_apos.sub("",tmp)
		# remove ending 's
		tmp = end_poss.sub("",tmp)
		# remove angle brackets < and >
		#tmp = end_angle_br.sub("",tmp)
		# removing starting '
		tmp = starting_apos.sub("",tmp)
		mf.append(tmp)
		##print "adding ",tmp," to mf"
	##	print "summed mf",mf
	# check for single words in paren & add to list (removing duplicates)
	mf3 = wphrases.findall(new_line)
	##print "Mf3 = ",mf3
	for m in mf3: mf.append(pw.sub("",m))
	mf = list(set(mf))
	#print "final mf =",mf
	

	if (mf):
		for p in phr:
			for n in mf:
				if (n.lower() == p):
					#print "found ",n," in phr"
					newx = re.compile(r"\("+n+"\)",re.UNICODE)
					if(not no_embed):
						new_line = newx.sub("<span class=\"em\">"+n+"</span>",new_line)
		#if n in phr_noparen:
		for p in phr_noparen:
			if " " in p:
				pass
			else:
				for n in mf:
					#print "p,n",p,n
					if (n.lower() == p):
						#print "found ",n," in phr_noparen"
						newx = re.compile(n,re.UNICODE)
						if (not no_embed):
							new_line = newx.sub("<span class=\"em\">"+n+"</span>",new_line)
	return(new_line)


#----------------------------------------------
# Roman References has ":" + Uppercase + Numbers
#----------------------------------------------
def htmlize_krefs(new_line,kdict,marker):
	mk = krefs.findall(new_line)
	for n in mk:
		if (crefs.search(n)):
			# remove paren
			base = pw.sub("",n)
			# get chap,verse
			(chap,verse) = base.split(":")
			dec_chap = todec(chap)
			if (dec_chap == 0):
				# original not in Roman Numeral format!
				print "(",chap,'->',str(dec_chap),")",
				tchap = "%03d" % int(chap)
			else:
				tchap = "%03d" % dec_chap
			fverse = verse.split("-")
			tverse = "%03d" % int(fverse[0])
			tbase = (str(tchap)+str(tverse)) # for now
			kdict = add_to_dict(kdict,tbase,marker)
	return(new_line,kdict)


#----------------------------------------------
# search for names in each line and put anchor
#----------------------------------------------
def htmlize_name_index(new_line,index,ilink,marker,no_embed):
	index_n = 0
	for ix in index:
		words = re.split(r"[\(]+",ix) # allows names with stuff after in paren
		fword = words[0]
		index_n += 1
		# search for 1st word but use complete line as key
		fw = re.compile(fword)
		fw_check = re.compile("<span class=\"nm\">"+fword)
		# check if new word is subset of previous word before adding
		if(not fw_check.search(new_line)):
			if(not no_embed):
				new_line = fw.sub("<span class=\"nm\">"+fword+"</span>",new_line)
				where = new_line.find("<span class=\"nm\">"+fword)
				# still 'emp' but don't link to name with '-' before it
				if (where > 0 and new_line[where-1] != '-'):
					ilink = add_to_dict(ilink,ix,marker)
			else:
				where = new_line.find(fword)
				# still 'emp' but don't link to name with '-' before it
				if (where > 0 and new_line[where-1] != '-'):
					ilink = add_to_dict(ilink,ix,marker)
	return(new_line,ilink)
#----------------------------------------------





#---------------------------------------------------
# process metadata for book in JSON format & return
#
#---------------------------------------------------
def title_proc(title,tfile,content,ver,script_ver):
	t = datetime.datetime.now()
	if(len(title) > 0):
		extra = title['rights'] + "<br />" + title['description']
		#print "ver = ",ver
		draft = re.compile('draft')
		# If title contains draft add version info
		if (draft.search(title['title'])):
			title['title'] = title['title']+" version "+ver

		design = ""
		trans  = ""
		isbn  = ""
		coverdesign = ""
		coverphoto = ""
		web = ""
		publisher = ""
		software = ""
		if (title['translators']): trans = "Translators : "+title['translators']
		if (title['design']): design = "Designed by : "+title['design']
		if (title['revision']): ver = title['revision']+ver
		if (title['cover design']): coverdesign = "Cover design : "+title['cover design']
		if (title['cover photo']): coverphoto = "Cover Image : "+title['cover photo']
		if (title['isbn']): isbn = "ISBN : "+title['isbn']
		if (title['publisher']): publisher = "Published by : "+title['publisher']
		# these not in older pyepub.cfg files
		if (check_attr(title,'web')): web = "Website : "+title['web']
		if (check_attr(title,'software')): software = "Generated using "+title['software']+" version "+script_ver

		st = title_form.substitute( { 
				'extra' : extra,
				'title' : title['title'],
				'author' : title['author'], 
				'isbn' : isbn, 
				'copyright' : title['copyright'], 
				'coverdesign' : coverdesign,
				'design' : design,
				'coverphoto' : coverphoto,
				'translators' : trans,
				'publisher' : publisher,
				'web' : web, 
				'ver' : ver,
				'content' : content,
				'software' : software,
				'ver_type' : ver_type.decode('utf-8'),
				"time" : t.strftime("%Y-%m-%d at %H:%M:%S"),
				"css" : "css/main.css"} )
		#for k,n in biblio_dict.iteritems(): print k, ":", n
		ss = xhtml_hdr.substitute( { 
				'title' : title['title'], 
				"css" : "css/main.css"} )
		return(st,title)
	else:
		return('')


def re_utf(s):
	s = de_unify(s)
	s = s.encode('utf-8')
	return(s)


def de_unify(s):
	if(full_unicode): 
		return(s)
	else:
		ss = unicodedata.normalize('NFKD', unicode(s)).encode('ASCII', 'ignore')
		return(ss)

# Go through cmplist, removing elements that are in reflist
# return new list
def subtract_from_list(reflist,cmplist):
	newlist = []
	for cmp in cmplist:
		if cmp in reflist:
			pass
		else:
			newlist.append(cmp)
	return(newlist)

# print flattened biblio for cut & paste, etc, putting "author" 1st
def print_flat_biblio(bibfile):
	s = utffile2str(bibfile)
	x = json.loads(s)
	k = x['bib']
	for l in k: 
		print "{",
		has_abbrev = 0

		ss = "\"author\":\""+string.strip(l['author'])+"\","
		print ss.encode('utf-8'),
		ss = "\"title\":\""+string.strip(l['title'])+"\","
		print ss.encode('utf-8'),

		for i in sorted(l):
			if (i=="title" or i=="author"):
				pass
			else:
				ss = "\""+string.strip(i)+"\":\""+string.strip(l[i])+"\","
				print ss.encode('utf-8'),
		
		print "}"

# used below
def create_footnotes_from_file(ftnfile):
    fc = 0
    ftnlist = []
    for l in fileinput.input(ftnfile):
        l = amprefs.sub("&amp;",l)
        ls = nrefs.sub("",l,1)
        if (nrefs.match(l)):
            fc = fc+1
            l = "†"+ls
            ftnlist.append(l)
    return(ftnlist)

# Legacy footnote handling - take footnotes from file create new file with footnotes inserted
def insert_footnotes(ftnfile,fname):
    ofname = fname+".new"
    # Create list of footnotes for insertion
    fnlist = create_footnotes_from_file(ftnfile)
    ofrefs    = re.compile(ur'†|‡|(\$\$)',re.UNICODE)
    PY = open(ofname,"w")
    tmp1 = codecs.open(fname,encoding='utf-8')
    fnc = 0
    for line in tmp1:
        marks = ofrefs.findall(line)
	# replace old format with new
        line = ofrefs.sub(ur'†',line)
        PY.write(line.encode('utf-8'))
        if (len(marks) > 0):
            fms = len(marks)
            #insert footnotes
            for f in xrange(0,fms):
                gen_fn = fnlist.pop(0)
                PY.write(gen_fn)
            #print len(marks),line
    PY.close()


 
# Some functions to convert to 
# and from Roman numerals
# for numbers n with
# 0 < n < 5000
#
# (c) 2/2008 Goetz Schwandtner <schwandtner@googlemail.com>
#
# see www.schwandtner.info

def rdigit(dig, chrs):
    "returns digit from chrs-1,5,10"
    if dig==9:
        return chrs[0]+chrs[2]
    if dig==4:
        return chrs[0]+chrs[1]
    if dig>4:
        return chrs[1]+(dig-5)*chrs[0]
    else:
        return dig*chrs[0]
        
def toroman(n):
    "roman numeral string of n<4000"
    return "M"*(n/1000)+rdigit(n/100%10,"CDM")+rdigit(n/10%10,"XLC")+rdigit(n%10,"IVX")

def ddigit(digs, dstr):
    "first digits value, rest dstr"
    if dstr[0:2]==digs[0]+digs[2]:
        return 9,dstr[2:]
    if dstr[0:2]==digs[0]+digs[1]:
        return 4,dstr[2:]
    v,i=0,0
    if dstr[0]==digs[1]:
        v,i=5,1
    while dstr[i]==digs[0]:
        v,i=v+1,i+1
    if i<5:
        return v,dstr[i:]
    else:
        return 0

def todec(s):
    "decimal value of Roman number s"
    m,s=ddigit("Mxx",s+".")
    c,s=ddigit("CDM",s)
    x,s=ddigit("XLC",s)
    i,s=ddigit("IVX",s)
    if s==".":
        return m*1000+c*100+x*10+i
    else:
        return 0

# File name ".pkg" is just a zip file with all needed files to make epub using this software
def process_pkg_file(fname,unzip_name):
	zf = zipfile.ZipFile(fname)
	os.mkdir(unzip_name)
	for name in zf.namelist():
		name_plus = unzip_name+"/"+name
		if name.endswith('/'):
			if not os.path.exists(name_plus):
				os.mkdir(name_plus)
	for i, name in enumerate(zf.namelist()):
		name_plus = unzip_name+"/"+name
		if not name.endswith('/'):
			outfile = open(name_plus, "wb")
			outfile.write(zf.read(name))
			outfile.flush()
			outfile.close()
			if name.endswith('.cfg'):
				cfg_name = name
	return(cfg_name)


if __name__ == '__main__':
    if (len(sys.argv) > 1):
        fname = sys.argv[1]
	script_path = os.path.dirname(os.path.realpath(__file__))
	# Get version number of this script!!! 
	if (os.path.isdir(script_path+"/.git")):
		(status,script_ver) = commands.getstatusoutput("cd "+script_path+"; git rev-parse --short HEAD ")
	else:
		script_ver = '0'
        if (os.path.isfile(fname)):
		iszip = re.compile(".pkg")
		using_pkg = False
		cfg_name = None
		if iszip.search(fname):
			using_pkg = True
			(root,ext) = fname.split(".pkg")
			unzip_name = root+"_unzipped"
			if (os.path.isdir(unzip_name)):
				print unzip_name+" already exists, please run from there using .cfg file"
			else:
				cfg_name = process_pkg_file(fname,unzip_name)
				if (cfg_name):
					fname = cfg_name
					os.chdir(unzip_name)
		if ((using_pkg and cfg_name) or not using_pkg):
			s = utffile2str(fname)
			global_cfg = json.loads(s)
			global_cfg['config'][2]['script_ver'] = script_ver
			md_to_xhtml(global_cfg['config'])
			try:
				epubcheck_cmd = global_cfg['config'][1]['run_epubcheck']
				cmd = epubcheck_cmd+" "+global_cfg['config'][2]['output']
				print "Running Epubcheck...",cmd
				(status,output) = commands.getstatusoutput(cmd)
				print output

				if (os.path.isdir(".git")):
					x = commands.getstatusoutput('git shortlog -s')
					ver_s = string.split(x[1])
					ver = string.strip(ver_s[0])
					orig_name = (global_cfg['config'][2]['output'])
					fnames = orig_name.split(".epub")
					output_filename = fnames[0]+"_"+ver+".epub"
					commands.getstatusoutput("mv "+orig_name+" "+output_filename)
				sys.exit(status)
			except:
				pass
        else:
            print fname,"not found"
    else:
        print "please add filename"
