from src.util import rpad_string, lrpad_string


class CharacterSet:
    minimal = {
        'corner': '#',
        'horizontal': '-',
        'vertical': '|'
    }


class TranscriptFileGenerator:
    def __init__(self, text, meta, character_set=None):
        self.text = text
        self.meta = meta
        self.character_set = CharacterSet.minimal if character_set is None else character_set

    def compile(self):
        meta_text = (PropertiesTextTemplate(self.meta)).compile()
        block_text = (BlockTextTemplate(meta_text, 'info', self.character_set)).compile()
        return block_text + '\n\n' + self.text


class BlockTextTemplate:
    def __init__(self, text, title, character_set, padding=1, min_length=-1):
        self.text = text
        self.title = title
        self.character_set = character_set
        self.padding = padding
        self.min_length = min_length

    def compile(self):
        result = []
        c_corner = self.character_set['corner']
        c_vertical = self.character_set['vertical']
        c_horizontal = self.character_set['horizontal']
        lines = self.text.split('\n')
        max_length = self.get_max_line_length(lines)

        if max_length < self.min_length:
            max_length = self.min_length

        # Build initial title, to see if it is longer than the lines to come
        header_title = rpad_string('', c_horizontal, 2) \
                       + '[ ' + self.title + ' ]' \
                       + rpad_string('', c_horizontal, 2)

        # Finish title
        if len(header_title) >= max_length:
            max_length = len(header_title)
            result.append(c_corner + header_title + c_corner)
        else:
            padding = max_length - len(header_title)
            result.append(c_corner + rpad_string(header_title, c_horizontal, padding) + c_corner)

        # Pad each line and add vertical bars
        for line in lines:
            padding = max_length - len(line) - 2 * self.padding
            line = c_vertical \
                   + rpad_string('', ' ', self.padding) \
                   + rpad_string(line, ' ', padding) \
                   + rpad_string('', ' ', self.padding) \
                   + c_vertical
            result.append(line)

        # Compile footer
        footer = c_corner + rpad_string('', c_horizontal, max_length) + c_corner
        result.append(footer)

        return '\n'.join(result)

    def get_max_line_length(self, lines):
        max_length = 0
        for line in lines:
            length = len(line) + 2 * self.padding
            if length > max_length:
                max_length = length
        return max_length


class PropertiesTextTemplate:
    def __init__(self, properties, property_separator=':', align_separator=True, spacing=1):
        self.properties = properties
        self.property_separator = property_separator
        self.align_separator = align_separator
        self.spacing = spacing

    def compile(self):
        # Find largest property name
        max_property_length = 0
        for name, value in self.properties.items():
            if len(name) > max_property_length:
                max_property_length = len(name)
        # Create lines
        lines = []
        for name, value in self.properties.items():
            padding = max_property_length - len(name) if self.align_separator else 0
            text = rpad_string(name, ' ', padding) \
                   + lrpad_string(self.property_separator, ' ', self.spacing) \
                   + str(value)
            lines.append(text)
        return '\n'.join(lines)
