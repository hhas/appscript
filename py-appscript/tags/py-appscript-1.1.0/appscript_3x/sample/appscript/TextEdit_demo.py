#!/usr/bin/env python3

# Demonstrates various references and commands in action.

from appscript import *

textedit = app('TextEdit') # get an application object for TextEdit


# tell application "TextEdit" to activate
textedit.activate()


# tell application "TextEdit" to make new document at end of documents
textedit.documents.end.make(new=k.document)


# tell application "TextEdit" to set text of document 1 to "Hello World\n"
textedit.documents[1].text.set('Hello World\n')


# tell application "TextEdit" to get a reference to every window
print(textedit.windows)


# tell application "TextEdit" to get a reference to document 1
print(textedit.documents)


# tell application "TextEdit" to get every document
print(textedit.documents.get())


# tell application "TextEdit" to get a reference to document 1
print(textedit.documents[1])


# tell application "TextEdit" to get document 1
print(textedit.documents[1].get())


# tell application "TextEdit" to get window id 3210
# print(textedit.windows.ID(3210).get())


# tell application "TextEdit" to get a reference to text of document 1
print(textedit.documents[1].text)


# tell application "TextEdit" to get text of document 1
print(textedit.documents[1].text.get())


# tell application "TextEdit" to make new document at end of documents
textedit.documents.end.make(new=k.document)


# tell application "TextEdit" to set text of document 1 to "Happy Happy Joy Joy\n"
textedit.documents[1].text.set('Happy Happy Joy Joy\n')


# tell application "TextEdit" to get text of every document
print(textedit.documents.text.get())


# tell application "TextEdit" to count each word of text of document 1
print(textedit.documents[1].text.count(each=k.word))


# tell application "TextEdit" to get words 3 thru -1 of document 1
print(textedit.documents[1].words[3:-1].get())


# tell application "TextEdit" to set size of character 1 of every word 
#         of document 1 to 24
textedit.documents[1].words.characters[1].size.set(24)


# tell application "TextEdit" to set color of any word of document 1 to {65535, 0, 0}
textedit.documents[1].words.any.color.set([65535, 0, 0])


# tell application "TextEdit" to make new paragraph at 
#         (after last paragraph of text of document 1) with data "Silly Rabbit\n"
textedit.documents[1].text.paragraphs.last.after.make(
        new=k.paragraph, with_data='Silly Rabbit\n')


# tell application "TextEdit" to get paragraph after paragraph 1 of document 1
print(textedit.documents[1].paragraphs[1].next(k.paragraph).get())


# tell application "TextEdit" to make new document at end of documents 
#         with properties {text:"foo\nbar\n\n\nbaz\n\nfub\n"}
textedit.documents.end.make(new=k.document, 
        with_properties={k.text: 'foo\nbar\n\n\nbaz\n\nfub\n'})


# tell application "TextEdit" to get every paragraph of text of document 1
print(textedit.documents[1].text.paragraphs.get())


# tell application "TextEdit" to get every paragraph of document 1 
#         where it is not "\n" -- get non-empty paragraphs
print(textedit.documents[1].paragraphs[its != '\n'].get())


# tell application "TextEdit" to get text of every document 
#         whose text begins with "H"
print(textedit.documents[its.text.beginswith('H')].text.get())



# The following examples don't work in TextEdit but will work in, 
# for example, Tex-Edit Plus:
#
#  # tell application "Tex-Edit Plus" to get words (character 5) 
#  #         thru (paragraph 9) of document 1
#  print(app('Tex-Edit Plus').documents[1] \
#           .words[con.characters[5]:con.paragraphs[9]].get())
#
#
#  # tell application "Tex-Edit Plus" to get every word of text 
#  #         of document 1 whose color is {0, 0, 0}
#  print(app('Tex-Edit Plus').documents[1].text.paragraphs \
#          [its.color.equals((0, 0, 0))].get())