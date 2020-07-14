from mako.template import Template
from multiprocessing import Pool
from media import Media

email_html_template_body = """
<style>
body {
   font-family: Courier New;
   max-width: 320px;
}
p {
   text-align: justify;
}
</style>
${body}
"""

email_html_template = """
<section>
   <h${level}>${title}</h${level}>
   <p>${text}</p>
   % if email:
   <img src="${src}" alt="${alt}">  
   % endif
</section>
"""

def generate_email_section(section):
    return Template(email_html_template).render(level=section.level, title=section.title, text=section.text, src=Media(section.media.src).gif(), alt=section.media.alt, email=(section.media.opts.find('!email') == -1))

def generate_email_(sections):
    pool = Pool()
    res = pool.map(generate_email_section, sections)

    return Template(email_html_template_body).render(body=''.join(res))

def generate(sections):
    with open('out/email.html', 'w') as f: 
        f.write(generate_email_(sections))
