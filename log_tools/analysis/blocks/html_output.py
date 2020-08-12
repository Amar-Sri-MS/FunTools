#
# HTML output block
#
# Experimental, subject to rapid change.
#

import jinja2
import os

from blocks.block import Block

class HTMLOutput(Block):
    """ Creates HTML pages for the logs """

    def __init__(self):
        super().__init__()
        self.cfg = None

    def set_config(self, cfg):
        self.cfg = cfg

    def process(self, iters):

        # Assume our template is right next door to us.
        MODULE_PATH = os.path.realpath(__file__)
        MODULE_DIR = os.path.dirname(MODULE_PATH)

        jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(MODULE_DIR),
                                 trim_blocks=True,
                                 lstrip_blocks=True)
        template = jinja_env.get_template('log_template.html')

        pages = []
        page_body = []

        for _, _, uid, display_time, line in iters[0]:
            if not page_body:
                page_name = 'part.' + str(len(pages)) + '.html'
                pages.append((display_time, page_name))

            # The log lines are organized as table rows in the template
            page_body.append('<tr><td>{}</td> <td>{}</td> <td>{}</td></tr>'.format(uid, display_time, line))

            if len(page_body) >= self.cfg['lines_per_page']:
                self.write_page(page_name, page_body, jinja_env, template)
                page_body = []

        self.write_index(pages, jinja_env)

    def write_page(self, page_name, page_body, jinja_env, template):
        template_dict = {}
        template_dict['body'] = ''.join(page_body)
        result = template.render(template_dict, env=jinja_env)

        page_path = os.path.join(self.cfg['dir'], page_name)
        with open(page_path, 'w') as f:
            f.write(result)

    def write_index(self, pages, jinja_env):
        """ Writes an index for the generated pages """
        template = jinja_env.get_template('index_template.html')

        template_dict = {}
        template_dict['pages'] = pages
        result = template.render(template_dict, env=jinja_env)

        index_file = os.path.join(self.cfg['dir'], 'index.html')
        with open(index_file, 'w') as f:
            f.write(result)

