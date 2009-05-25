#!/usr/bin/env python
# -*- coding: utf-8 -*-
#     Original idea from : 
#       Maxime Biais <maxime@biais.org>
#     but has been nearly all rewritten since...
#    Marc Poulhiès <marc.poulhies@epfl.ch>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id: latex2twiki.py,v 1.2 2005/07/27 12:40:53 poulhies Exp $

import sys, re

bullet_level=0
bdoc = None
end_line = 1

verbatim_mode = 0

def dummy():
    pass

def inc_bullet():
	global bullet_level
	bullet_level += 1

def dec_bullet():
	global bullet_level
	bullet_level -= 1

def start_doc():
	global bdoc;
	bdoc = 1

def do_not_el():
	global end_line
	end_line = None

def do_el():
	global end_line;
	end_line = 1

def decide_el():
	global end_line
	if bullet_level == 0:
		return "\n"
	else:
		return " "

def start_verbatim():
	global verbatim_mode
	verbatim_mode = 1

def end_verbatim():
	global verbatim_mode
	verbatim_mode = 0
	
conv_table = { '>':'&gt;',
			   '<':'&lt;'}

def translate_to_html(char):
	global verbatim_mode
	global conv_table
	if verbatim_mode == 0:
		return conv_table[char]
	else:
		return char

def header(i):
	return ur"%s \1 %s" % (i*'=', i*'=')

NONE = "__@NONE@__"

tr_list2 = [
	#(ur">", (lambda: translate_to_html('>')), dummy),
	#(ur"<", (lambda: translate_to_html('<')), dummy),
	(ur"(?im)\$\$?([^$]*?)\$?\$", (lambda: ur'<math>\1</math>'), dummy),
	(ur"\\footnotesize", None, dummy),
	(ur"\\footnote{(.*?)}", (lambda :ur"<ref>\1</ref>"), dummy),
	(ur"\\index{(.*?)}", None, dummy), #todo
	(ur"\\ldots", (lambda : "..."), dummy),
	(ur"(?i)\\Pagebreak", (lambda : ur""), dummy), #pagebreak
	(ur"\-{3}", (lambda : "—"), dummy),
	(ur"{\\em (.*?)}", (lambda : ur"''\1''"), dummy), #cursivas
	(ur"(?im)^\\pro ", (lambda : "#"), dummy), #lista ordenada
	(ur"(?im)^\\spro ", (lambda : "*"), dummy), #lista sin orden
	(ur"\\ldots", (lambda : "..."), dummy),
	(ur"\\begin\{document}", None, start_doc),
	(ur"\\\\$", (lambda : "\n\n"), dummy),
	(ur"\\\$", (lambda : "$"), dummy),
	(ur"\\emph{(.*?)}", (lambda : ur"_\1_"), dummy),
	(ur"(?i)\\textit{(.*?)}", (lambda :ur"''\1''"), dummy),
	(ur"(?i)\\texttt{(.*?)}", (lambda : ur"<tt>\1</tt>"), dummy),
	(ur"(?i)\\textbf{(.*?)}", (lambda : ur"'''\1'''"), dummy),
	(ur"(?i)\\url{(.*?)}", (lambda : ur"\1"), dummy),
	(ur"\\begin{verbatim}", (lambda : "<verbatim>"), start_verbatim),
	(ur"\\end{verbatim}", (lambda : "</verbatim>"), end_verbatim),
	(ur"\\begin{itemize}", (lambda : "\n"), inc_bullet),
	(ur"\\end{itemize}", None, dec_bullet),
	(ur"\\item (.*?)", (lambda : ur"\n" + (ur"   " * bullet_level) + ur"* \1"), dummy),
	(ur"\\item\[(.*?)\][\n ]*", (lambda : ur":\1 "), dummy),
	(ur"\\begin{.*?}", None, dummy),
	(ur"\\end{.*?}", None, dummy),
	(ur"``(.*?)''", (lambda :ur'"\1"'), dummy),
	(ur"(?i)\\subsubsection{(.*?)}", (lambda : header(4)), dummy),
	(ur"(?i)\\subsection{(.*?)}", (lambda : header(3)), dummy),
	(ur"(?i)\\section{(.*?)}", (lambda : header(2)), dummy),
	(ur"(?i)\\chaptere?{(.*?)}", (lambda : header(1)), dummy),
	(ur"(?i)\\index{(.*?)}", None, dummy),
	(ur"\\_", (lambda :"_"), dummy),
	(ur"\\tableofcontents",None, dummy),
	(ur"\\null",None, dummy),
	(ur"\\newpage",None, dummy),
	(ur"\\thispagestyle{.*?}", None, dummy),
	(ur"\\maketitle", None, dummy),
	(ur"\\-", None, dummy),
	(ur"\\clearpage", (lambda : ur'<br clear="all" />'), dummy),
	(ur"\\cleardoublepage", (lambda : ur'<br clear="all" />'), dummy),
	(ur"\\markboth{}{}", None, dummy), #todo
	(ur"\\addcontentsline.*", None, dummy), #todo
	#(ur"\n$", decide_el, dummy),
	#(ur"(?im)(\w)[\n\r]+(\w)", (lambda :ur'\1 \2'), dummy),
	#(ur"[^\\]?\{", None, dummy),
	#(ur"[^\\]?\}", None, dummy),
	(ur"(?im)^\%.*$\n", None, dummy), #quitamos comentarios
	(ur"\\\\", (lambda: ur'\n'), dummy), 
	(ur"\\tt ([^\}]*)", (lambda: ur'<tt>\1</tt>'), dummy), 
	(ur"\\small ([^\}]*)", (lambda: ur'<small>\1</small>'), dummy), 
	(ur"\\centerline{(.*?)}", (lambda: ur'<center>\1</center>'), dummy), 
	(ur"\\copyright", (lambda: ur'©'), dummy), 
    ]

#in_stream  = sys.stdin;
path=''
if len(sys.argv)==2:
	arg1=sys.argv[1]
	f=open(arg1, 'r')
	s=arg1.split('\\')
	path='\\'.join(s[:len(s)-1])+'\\'
else:
	print 'Introduce un parametro con el nombre del fichero que contienen el codigo fuente en latex'
	sys.exit()
out_stream = sys.stdout

#for i in in_stream.readlines():
salida=''
salida=unicode(f.read(), 'utf-8')


#INICIO PRE-PROCESADO

#metemos los inputs
m=re.compile(ur'\\input\{(?P<filename>[^\}]*?)\}').finditer(salida)
for i in m:
	filename=path+i.group('filename')+'.tex'
	try:
		g=open(filename, 'r')
		salida=re.sub(ur'\\input\{%s\}' % i.group('filename'), unicode(g.read(), 'utf-8'), salida)
		g.close()
	except:
		print 'Fichero %s no encontrado' % filename

#salida=re.sub(ur'([^\n])\n([^\n])', ur'\1 \2', salida) #metemos espacios al concatenar lineas consecutivas
salida=re.sub(ur'\n\n\n+', ur'\n\n', salida) #quitamos saltos excesivos
salida=re.sub(ur'(?m)^\s*', ur'', salida) #quitamos espacios inicio línea

#FIN PRE-PROCESADO


#INICIO PROCESADO
for reg, sub, fun in tr_list2:
	p = re.compile(reg)
	if p.search(salida):
		fun()
	if sub != None:
		salida = p.sub(sub(), salida)
	else:
		salida = p.sub("", salida)
#FIN PROCESADO


#post-procesado
salida=re.sub(ur'\n\n\n+', ur'\n\n', salida) #quitamos saltos excesivos
salida=re.sub(ur'\n\n+([\*\#])', ur'\n\1', salida) #quitamos saltos en listas

f.close()
f=open('salida.wiki', 'w')
if re.search(ur'<ref[> ]', salida):
	salida+='\n\n== Referencias ==\n<references />'

f.write(salida.encode('utf-8'))
f.close()
