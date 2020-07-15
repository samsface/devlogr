import glob, os, mistune, pprint, subprocess, argparse, praw, getpass
from mako.template import Template
from multiprocessing import Pool
import uuid

class media:
    src = ''
    alt = ''
    opts = ''

class doc_section:
    level = 0
    title = ''
    media = ''
    text  = ''

def get_title(ast):
    for a in ast:
        if a['type'] == 'heading':
            return a['children'][0]['text']

    raise Exception('no title in ast')

def get_level(ast):
    for a in ast:
        if a['type'] == 'heading':
            return a['level']

    raise Exception('no title in ast')

def get_media_(ast):
    res = []
    for a in ast:
        if 'children' in a and a['type'] == 'paragraph':
            res.append(get_media(a['children']))
        elif a['type'] == 'image':
            m = media()
            m.src = a['src']
            m.alt = a['alt'].split(';')[0]
            m.opts = ';'.join(a['alt'].split(';')[1:])
            res.append(m)

    return res

def get_text_(ast):
    res = []
    for a in ast:
        if 'children' in a and a['type'] == 'paragraph':
            res.append(get_text(a['children']))
        elif a['type'] == 'text':
            res.append(a['text'])

    return res

def get_media(ast):
    res = get_media_(ast)
    if len(res) > 1:
        raise Exception('section can only have one media', ast)
    if len(res) == 0:
        raise Exception('section is missing media', ast)

    return res[0]

def get_text(ast):
    res = get_text_(ast)
    if len(res) > 1:
        raise Exception('section can only have one text', res)
    if len(res) == 0:
        raise Exception('section is missing text')

    return res[0]

def get_sections(ast):
    sections = []

    for a in ast:
        if a['type'] == 'heading':
            sections.append([])
        sections[-1].append(a)

    return sections

def make_doc_section(ast_section):
    section = doc_section()

    section.level = get_level(ast_section)
    section.title = get_title(ast_section)
    section.media = get_media(ast_section)
    section.text  = get_text(ast_section)
    
    return section

class Script:

    @staticmethod
    def get_script():
        doc = open('script.md', 'r').read()

        markdown = mistune.create_markdown(renderer=mistune.AstRenderer())
        markdown_ast = markdown(doc)

        doc_ast = {}

        sections = [make_doc_section(s) for s in get_sections(markdown_ast)]

        return sections
