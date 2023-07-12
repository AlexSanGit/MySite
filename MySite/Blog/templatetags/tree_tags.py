from django import template

register = template.Library()


@register.simple_tag
def render_category_tree(categories, selected_category):
    def render_node(node):
        children_html = ""
        if node.children.exists():
            children_html = '<ul class="subcategory-list">'
            for child in node.children.all():
                children_html += render_node(child)
            children_html += "</ul>"

        selected_class = "selected" if node == selected_category else ""
        return f'<li class="{selected_class}"><a href="{node.get_absolute_url}">{node.name}</a>{children_html}</li>'

    root_nodes = categories.filter(parent=None)
    tree_html = '<ul class="category-list">'
    for node in root_nodes:
        tree_html += render_node(node)
    tree_html += "</ul>"

    return tree_html
