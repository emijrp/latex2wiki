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
	return r"%s \1 %s" % (i*'=', i*'=')

NONE = "__@NONE@__"

tr_list2 = [
	#(r">", (lambda: translate_to_html('>')), dummy),
	#(r"<", (lambda: translate_to_html('<')), dummy),
	(r"(?im)\$\$?([^$]*?)\$?\$", (lambda: r'<math>\1</math>'), dummy),
	(r"\\footnotesize", None, dummy),
	(r"\\footnote{(.*?)}", (lambda :r"<ref>\1</ref>"), dummy),
	(r"\\index{(.*?)}", None, dummy), #todo
	(r"\\ldots", (lambda : "..."), dummy),
	(r"(?i)\\Pagebreak", (lambda : r""), dummy), #pagebreak
	(r"\-{3}", (lambda : "—"), dummy),
	(r"{\\em (.*?)}", (lambda : r"''\1''"), dummy), #cursivas
	(r"(?im)^\\pro ", (lambda : "#"), dummy), #lista ordenada
	(r"(?im)^\\spro ", (lambda : "*"), dummy), #lista sin orden
	(r"\\ldots", (lambda : "..."), dummy),
	(r"\\begin\{document}", None, start_doc),
	(r"\\\\$", (lambda : "\n\n"), dummy),
	(r"\\\$", (lambda : "$"), dummy),
	(r"\\emph{(.*?)}", (lambda : r"_\1_"), dummy),
	(r"(?i)\\textit{(.*?)}", (lambda :r"''\1''"), dummy),
	(r"(?i)\\texttt{(.*?)}", (lambda : r"<tt>\1</tt>"), dummy),
	(r"(?i)\\textbf{(.*?)}", (lambda : r"'''\1'''"), dummy),
	(r"(?i)\\url{(.*?)}", (lambda : r"\1"), dummy),
	(r"\\begin{verbatim}", (lambda : "<verbatim>"), start_verbatim),
	(r"\\end{verbatim}", (lambda : "</verbatim>"), end_verbatim),
	(r"\\begin{itemize}", (lambda : "\n"), inc_bullet),
	(r"\\end{itemize}", None, dec_bullet),
	(r"\\item (.*?)", (lambda : r"\n" + (r"   " * bullet_level) + r"* \1"), dummy),
	(r"\\item\[(.*?)\]", (lambda : r":\1"), dummy),
	(r"\\begin{.*?}", None, dummy),
	(r"\\end{.*?}", None, dummy),
	(r"``(.*?)''", (lambda :r'"\1"'), dummy),
	(r"(?i)\\subsubsection{(.*?)}", (lambda : header(4)), dummy),
	(r"(?i)\\subsection{(.*?)}", (lambda : header(3)), dummy),
	(r"(?i)\\section{(.*?)}", (lambda : header(2)), dummy),
	(r"(?i)\\chaptere?{(.*?)}", (lambda : header(1)), dummy),
	(r"(?i)\\index{(.*?)}", None, dummy),
	(r"\\_", (lambda :"_"), dummy),
	(r"\\tableofcontents",None, dummy),
	(r"\\null",None, dummy),
	(r"\\newpage",None, dummy),
	(r"\\thispagestyle{.*?}", None, dummy),
	(r"\\maketitle", None, dummy),
	(r"\\-", None, dummy),
	(r"\\clearpage", (lambda : r'<br clear="all" />'), dummy),
	(r"\\cleardoublepage", (lambda : r'<br clear="all" />'), dummy),
	(r"\\markboth{}{}", None, dummy), #todo
	(r"\\addcontentsline.*", None, dummy), #todo
	#(r"\n$", decide_el, dummy),
	#(r"(?im)(\w)[\n\r]+(\w)", (lambda :r'\1 \2'), dummy),
	#(r"[^\\]?\{", None, dummy),
	#(r"[^\\]?\}", None, dummy),
	(r"(?im)^\%.*$\n", None, dummy), #quitamos comentarios
	(r"\\\\", (lambda: r'\n'), dummy), 
	(r"\\tt ([^\}]*)", (lambda: r'<tt>\1</tt>'), dummy), 
	(r"\\small ([^\}]*)", (lambda: r'<small>\1</small>'), dummy), 
	(r"\\centerline{(.*?)}", (lambda: r'<center>\1</center>'), dummy), 
	(r"\\copyright", (lambda: r'©'), dummy), 
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
salida=f.read()


#INICIO PRE-PROCESADO

#metemos los inputs
m=re.compile(r'\\input\{(?P<filename>[^\}]*?)\}').finditer(salida)
for i in m:
	filename=path+i.group('filename')+'.tex'
	try:
		g=open(filename, 'r')
		salida=re.sub(r'\\input\{%s\}' % i.group('filename'), g.read(), salida)
		g.close()
	except:
		print 'Fichero %s no encontrado' % filename

#salida=re.sub(r'([^\n])\n([^\n])', r'\1 \2', salida) #metemos espacios al concatenar lineas consecutivas
salida=re.sub(r'\n\n\n+', r'\n\n', salida) #quitamos saltos excesivos
salida=re.sub(r'(?m)^\s*', r'', salida) #quitamos espacios inicio línea

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
salida=re.sub(r'\n\n\n+', r'\n\n', salida) #quitamos saltos excesivos
salida=re.sub(r'\n\n+([\*\#])', r'\n\1', salida) #quitamos saltos en listas

f.close()
f=open('salida.wiki', 'w')
if re.search(r'<ref[> ]', salida):
	salida+='\n\n== Referencias ==\n<references />'

f.write(salida)
f.close()
