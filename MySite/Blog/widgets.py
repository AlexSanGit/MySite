from django.forms import ClearableFileInput, FileInput, CheckboxInput


class MultipleFileInput(ClearableFileInput):
    template_name = 'blog/multiple_file_input.html'
    input_class = FileInput
    checkbox_input_class = CheckboxInput
    needs_multipart_form = True
