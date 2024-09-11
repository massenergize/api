
class PageBlockEngine:
	def __init__(self, ):
		pass
	
	def save_block_sections(self, block, sections):
		try:
			sections_to_create = []
			sections_to_update = []
			for section_data in sections:
				if 'section_id' in section_data:
					sections_to_update.append(
						BlockSection(
							id=section_data['section_id'],
							block=block,
							title=section_data.get('title'),
							order=section_data.get('order')
						)
					)
				else:
					sections_to_create.append(
						BlockSection(
							block=block,
							title=section_data.get('title'),
							order=section_data.get('order')
						)
					)
			
			# Bulk create or update sections
			if sections_to_create:
				BlockSection.objects.bulk_create(sections_to_create)
			if sections_to_update:
				BlockSection.objects.bulk_update(sections_to_update, ['title', 'order'])
			
			# Save rows for each section
			for section in sections_to_update + sections_to_create:
				section_data = next((s for s in sections if s.get('section_id') == section.id), None)
				if section_data:
					self.save_block_rows(section, section_data.get('rows', []))
			
			return True, None
		except Exception as e:
			return None, str(e)

	
	def save_block_rows(self, section, rows):
		try:
			rows_to_create = []
			rows_to_update = []
			for row_data in rows:
				if 'row_id' in row_data:
					rows_to_update.append(BlockRow(id=row_data['row_id'], section=section, order=row_data.get('order')))
				else:
					rows_to_create.append(BlockRow(section=section, order=row_data.get('order')))
			
			# Bulk create or update rows
			if rows_to_create:
				BlockRow.objects.bulk_create(rows_to_create)
			if rows_to_update:
				BlockRow.objects.bulk_update(rows_to_update, ['order'])
			
			# Save columns for each row
			for row in rows_to_update + rows_to_create:
				row_data = next((r for r in rows if r.get('row_id') == row.id), None)
				if row_data:
					self.save_block_columns(row, row_data.get('columns', []))
					
			return True, None
		
		except Exception as e:
			return None, str(e)
	
	def save_block_columns(self, row, columns):
		try:
			columns_to_create = []
			columns_to_update = []
			for column_data in columns:
				if 'column_id' in column_data:
					columns_to_update.append(
						BlockColumn(id=column_data['column_id'], row=row,column_space=column_data.get('column_space', 12)
						)
					)
				else:
					columns_to_create.append(BlockColumn(row=row, column_space=column_data.get('column_space', 12)))
			
			# Bulk create or update columns
			if columns_to_create:
				BlockColumn.objects.bulk_create(columns_to_create)
			if columns_to_update:
				BlockColumn.objects.bulk_update(columns_to_update, ['column_space'])
			
			# Save content for each column
			for column in columns_to_update + columns_to_create:
				column_data = next((c for c in columns if c.get('column_id') == column.id), None)
				if column_data:
					self.save_block_content(column, column_data.get('content', []))
					
			return True, None
		except Exception as e:
			return None, str(e)

	def save_block_content(self, column, content_data_list):
		try:
			content_to_create = []
			content_to_update = []
			for content_data in content_data_list:
				if 'content_id' in content_data:
					content_to_update.append(
						BlockContent(**content_data, id=content_data['content_id'], column=column)
					)
				else:
					content_to_create.append(BlockContent(**content_data, column=column))
			
			# Bulk create or update content
			if content_to_create:
				BlockContent.objects.bulk_create(content_to_create)
			if content_to_update:
				BlockContent.objects.bulk_update(content_to_update, ['content_type', 'order', 'style', 'className'])
				
			return True, None
		except Exception as e:
			return None, str(e)
	
	def save_block_data(self, block_json):
		try:
			block_id = block_json.get('block_id', None)
			block_name = block_json.get('block_name', None)
			layout_grid_count = block_json.get('layout_grid_count', 12)
			
			block, _ = Block.objects.update_or_create(
				block_id=block_id,
				defaults={
					'block_name': block_name,
					'layout_grid_count': layout_grid_count
				}
			)
			self.save_block_sections(block, block_json.get('sections', []))
			return block, None
	
		except Exception as e:
			return None, str(e)

