from html.parser import HTMLParser
from html.entities import name2codepoint
import re
import string

class MyHTMLParser(HTMLParser):
            def __init__(self, field, end):
                self.requests = []
                
                self.end_index = end
                self.field = field
                
                self.in_unordered_list = False
                self.in_ordered_list = False
                self.list_nesting_level = 0
                self.last_tag = None

                self.new_line_insert = {'insertText': {'location': {'index': end}, 'text': '\n'}}
                self.required_beginning = [self.new_line_insert for i in range(2)]
                self.text_edit_newline = ''.join(chr(i) for i in [13, 10])

                self.elements_stack = []
                self.styles_stack = []

                self.no_capitals_pattern = re.compile("[^A-Z]")

                super().__init__()

            # Helper functions to create Google Doc request objects 

            def get_requests(self):
                self.insert_heading()
                while self.requests[:2] != self.required_beginning:
                    self.insert_text('\n')
                return self.requests
            
            def insert_heading(self):
                self.requests.append({
                    'insertText': {
                        'location': {
                            'index': self.end_index,
                        },
                        'text': self.field + '\n'
                    }
                })
                self.requests.append({
                    'updateTextStyle': {
                        'range': {
                            'startIndex': self.end_index,
                            'endIndex': self.end_index + len(self.field)
                        },
                        'textStyle': {
                            'bold': True,
                            'underline': True,
                            'foregroundColor': {'color': {'rgbColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0}}}
                        },
                        'fields': 'bold, underline, foregroundColor'
                    }
                })
                self.requests.append({
                    'deleteParagraphBullets': {
                        'range': {
                            'startIndex': self.end_index,
                            'endIndex':  self.end_index + 1
                        },
                    }
                })
            
            def insert_text(self, text):
                self.requests.insert(0, {
                    'insertText': {
                        'location': {
                            'index': self.end_index,
                        },
                        'text': text
                    }
                })
            
            def insert_styling(self, attrs, is_bold, is_italics, link_url, length):
                #TODO: either check if sub-dicts exists in 'textStyle' or make the default have all necessary fields as empty dicts
                # coloring a link overwrites its style 
                
                styles = {
                    'updateTextStyle': {
                        'range': {
                            'startIndex': self.end_index,
                            'endIndex': self.end_index + length
                        },
                        'textStyle': {},
                        'fields': '*'
                    }
                }

                if link_url:
                    styles['updateTextStyle']['textStyle'] = {
                        'link': {'url': link_url},
                        'foregroundColor': {'color': {'rgbColor': {'red': 0.06666667, 'green': 0.33333334, 'blue': 0.8}}},
                        'underline': True,
                    }
                
                styles['updateTextStyle']['textStyle']['bold'] = is_bold
                styles['updateTextStyle']['textStyle']['italic'] = is_italics

                for attr in attrs:
                    if attr[0] == 'style':
                        style = attr[1].split(':')
                        style[0] = style[0].strip()
                        style[1] = style[1].strip().rstrip(';')

                        if style[0].strip() == "text-decoration":
                            if style[1] == "underline":
                                styles['updateTextStyle']['textStyle']['underline'] = True
                        elif style[0] == "color":
                                hex_val = style[1].lstrip(' #')
                                lv = len(hex_val)
                                rgb = tuple(int(hex_val[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
                                rgb = [x / 255 for x in rgb]
                                styles['updateTextStyle']['textStyle'] = {'foregroundColor': {'color': {'rgbColor': {'red': rgb[0], 'green': rgb[1], 'blue': rgb[2]}}}}
                        elif style[0] == "font-family":
                            # styles['updateTextStyle']['textStyle']['weightedFontFamily'] = {'fontFamily': style[1].strip(), 'weight': 400}
                            styles['updateTextStyle']['textStyle'] = {'weightedFontFamily': {'fontFamily': style[1].split(',')[0].strip().strip("'")}}
                        elif style[0] == "font-size":
                            styles['updateTextStyle']['textStyle'] = {'fontSize': {'magnitude': style[1].rstrip('pt;'), 'unit': 'PT'}}

                self.requests.insert(1, styles)
                
                if self.in_unordered_list:
                    self.requests.insert(2, {
                        'createParagraphBullets': {
                            'range': {
                                'startIndex': self.end_index,
                                'endIndex':  self.end_index + length
                            },
                            'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE',
                        }
                    })
                elif self.in_ordered_list:
                    self.requests.insert(2, {
                        'createParagraphBullets': {
                            'range': {
                                'startIndex': self.end_index,
                                'endIndex':  self.end_index + length
                            },
                            'bulletPreset': 'NUMBERED_DECIMAL_NESTED',
                        }
                    })
                else:
                    self.requests.insert(2, {'deleteParagraphBullets': {'range': {'startIndex': self.end_index, 'endIndex': self.end_index + length}}})


            # HTMLParser specific class functions

            def handle_starttag(self, tag, attrs):
                # print("Start tag:", tag, self.list_nesting_level)
                # for attr in attrs:
                #     print("     attr:", attr)
                
                self.elements_stack.append(tag)
                self.styles_stack.append(attrs)

                if tag == "ul":
                    if self.in_unordered_list:
                        self.list_nesting_level += 1

                    self.in_unordered_list = True

                if tag == "ol":
                    if self.in_ordered_list:
                        self.list_nesting_level += 1

                    self.in_ordered_list = True

            def handle_endtag(self, tag):
                # print("End tag  :", tag)
                
                self.elements_stack.pop()
                self.styles_stack.pop()

                if tag == 'p' or tag == 'li' and self.list_nesting_level == 0:
                    self.insert_text('\n')

                self.last_tag = tag

                if tag == "ul":
                    if self.list_nesting_level:
                        self.list_nesting_level -= 1
                    else:
                        self.in_unordered_list = False
                        self.requests.insert(1, {'deleteParagraphBullets': {'range': {'startIndex': self.end_index, 'endIndex': self.end_index + 1}}})
                    
                if tag == "ol":
                    if self.list_nesting_level:
                        self.list_nesting_level -= 1
                    else:
                        self.in_ordered_list = False
                        self.requests.insert(1, {'deleteParagraphBullets': {'range': {'startIndex': self.end_index, 'endIndex': self.end_index + 1}}})

            def handle_data(self, data):
                # print("Data     :", data)
                
                if self.elements_stack and self.styles_stack:
                    curr_elem = self.elements_stack[-1]
                    curr_style = self.styles_stack[-1]
                    is_bold = False
                    is_italics = False
                    link_url = None

                    data = data.strip()
                    if not data:
                        return

                    if curr_elem == "strong":
                        is_bold = True
                    
                    if curr_elem == "em":
                        is_italics = True
                    
                    if curr_elem == "a":
                        for style in curr_style:
                            if style[0] == 'href':
                                link_url = style[1]
                                break
                    else:
                        data += " "
                        
                    if curr_elem in ["p", "span", "strong", "em"]:
                        # if doesnt start with capital, add leading space
                        if re.match(self.no_capitals_pattern, data[0]):
                            data = " " + data

                    if curr_elem == "li" and self.list_nesting_level:
                        data = '\n' + '\t' * self.list_nesting_level + data

                    self.insert_text(data)
                    self.insert_styling(curr_style, is_bold, is_italics, link_url, len(data))

                elif self.last_tag not in ["p", "ol", "ul"]:
                    self.insert_text('\n')
                    self.requests.insert(1, {'deleteParagraphBullets': {'range': {'startIndex': self.end_index, 'endIndex': self.end_index + 1}}})