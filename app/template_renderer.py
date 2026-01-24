import os
from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateRenderer:
    def __init__(self, templates_dir: str = None):
        if templates_dir is None:
            templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "templates")
        
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def render(self, template_name: str = "base.html", **context) -> str:
        return self.env.get_template(template_name).render(**context)
    
    def render_to_file(self, output_path: str, template_name: str = "base.html", **context):
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.render(template_name, **context))


_renderer = None

def get_renderer() -> TemplateRenderer:
    global _renderer
    if _renderer is None:
        _renderer = TemplateRenderer()
    return _renderer


def render_index() -> str:
    return get_renderer().render("base.html")
