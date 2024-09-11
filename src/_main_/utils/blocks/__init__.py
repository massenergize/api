from database.models import Block, BlockSection, BlockRow, BlockColumn, BlockContent

# from, BlockContentHeading, BlockContentParagraph, BlockContentImage, BlockContentFormInput)

def get_block_json(block_id):
    """
    Main function that retrieves block data and serializes it into JSON.
    """
    try:
        block = Block.objects.get(id=block_id)
    except Block.DoesNotExist:
        return None

    block_json = {
        'block_id': str(block.id),
        'name': block.name,
        'layout_grid_count': block.layout_grid_count,
        'sections': get_block_sections(block)
    }

    return block_json

def get_block_sections(block):
    """
    Helper function to get BlockSections and their rows.
    """
    sections_data = []
    sections = BlockSection.objects.filter(block=block).order_by('order')

    for section in sections:
        section_data = {
            'section_id': str(section.id),
            'title': section.title,
            'order': section.order,
            'rows': get_block_rows(section)
        }
        sections_data.append(section_data)

    return sections_data

def get_block_rows(section):
    """
    Helper function to get BlockRows and their columns.
    """
    rows_data = []
    rows = BlockRow.objects.filter(section=section).order_by('order')

    for row in rows:
        row_data = {
            'row_id': str(row.id),
            'order': row.order,
            'columns': get_block_columns(row)
        }
        rows_data.append(row_data)

    return rows_data

def get_block_columns(row):
    """
    Helper function to get BlockColumns and their content.
    """
    columns_data = []
    columns = BlockColumn.objects.filter(row=row).order_by('id')

    for column in columns:
        column_data = {
            'column_id': str(column.id),
            'column_space': column.column_space,
            'content': get_block_content(column)
        }
        columns_data.append(column_data)

    return columns_data

def get_block_content(column):
    """
    Helper function to get BlockContent and serialize specific content types.
    """
    content_data_list = []
    contents = BlockContent.objects.filter(column=column).order_by('order')

    for content in contents:
        content_data = {
            'content_id': str(content.id),
            'content_type': content.content_type,
            'order': content.order,
            'style': content.style,
            'className': content.class_name,
        }
        get_specific_content_type(content, content_data)
        content_data_list.append(content_data)

    return content_data_list

def get_specific_content_type(content, content_data):
    """
    Helper function to serialize specific content types (heading, paragraph, image, form_input).
    """
    if content.content_type == 'heading':
        heading = BlockContentHeading.objects.get(content=content)
        content_data['text'] = heading.text
        content_data['level'] = heading.level

    elif content.content_type == 'paragraph':
        paragraph = BlockContentParagraph.objects.get(content=content)
        content_data['text'] = paragraph.text
        content_data['align'] = paragraph.align

    elif content.content_type == 'image':
        image = BlockContentImage.objects.get(content=content)
        content_data['src'] = image.src
        content_data['alt'] = image.alt
        content_data['width'] = image.width
        content_data['height'] = image.height

    elif content.content_type == 'form_input':
        form_input = BlockContentFormInput.objects.get(content=content)
        content_data['input_type'] = form_input.input_type
        content_data['name'] = form_input.name
        content_data['label'] = form_input.label
        content_data['placeholder'] = form_input.placeholder
        content_data['options'] = form_input.options
        content_data['value'] = form_input.value
        content_data['required'] = form_input.required
        content_data['disabled'] = form_input.disabled
