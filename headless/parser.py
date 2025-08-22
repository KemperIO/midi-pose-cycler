"""Markdown table parser for headless configuration."""

import re
from typing import List, Dict, Any, Optional
from .models import FormTable, DanceTable, DanceRow, HeadlessConfig
from .const import DEFAULT_PRE_HOLD, DEFAULT_POST_HOLD


class MarkdownTableParser:
    """Parse markdown tables into configuration objects."""
    
    @staticmethod
    def parse_table(text: str) -> List[Dict[str, str]]:
        """Parse a single markdown table into list of row dictionaries."""
        lines = text.strip().split('\n')
        
        # Find the actual table start (skip title lines)
        table_start = 0
        for i, line in enumerate(lines):
            if '|' in line and not line.strip().startswith('#'):
                table_start = i
                break
        
        lines = lines[table_start:]
        if len(lines) < 3:  # Need at least header, separator, and one data row
            return []
        
        # Extract headers
        header_line = lines[0]
        headers = [h.strip() for h in header_line.split('|')[1:-1]]
        
        # Skip separator line
        # Parse data rows
        rows = []
        for line in lines[2:]:
            if '|' not in line:
                continue
            values = [v.strip() for v in line.split('|')[1:-1]]
            if len(values) == len(headers):
                row = {headers[i]: values[i] for i in range(len(headers))}
                # Remove notes column if present
                row.pop('notes', None)
                rows.append(row)
        
        return rows
    
    @staticmethod
    def find_table_sections(text: str) -> Dict[str, str]:
        """Find and categorize table sections in markdown text."""
        sections = {}
        
        # Split by headers to find distinct sections, but keep headers
        # Look for lines starting with ## or containing "Table"
        parts = re.split(r'(?=##\s)', text)
        if len(parts) == 1:
            # Try splitting by double newlines if no headers found
            parts = re.split(r'\n\s*\n+', text)
        
        for i, part in enumerate(parts):
            part_lower = part.lower()
            if '|' not in part:
                continue
                
            # Identify table type by content/headers
            # Identify by content - be more specific
            # Video table - has video in header or audio/render specific fields
            if ('video' in part_lower and 'table' in part_lower) or ('audiofile' in part_lower and 'renderdir' in part_lower):
                sections['video'] = part
            # Dance table - has poseCatalog and track columns
            elif 'posecatalog' in part_lower and 'track' in part_lower:
                sections['dance'] = part
            # Form table - everything else with standard form fields
            elif ('form' in part_lower and 'table' in part_lower) or 'actionname' in part_lower or 'midifile' in part_lower:
                sections['form'] = part
        
        return sections
    
    @staticmethod
    def parse_form_table(table_text: str) -> FormTable:
        """Parse form table into FormTable object."""
        rows = MarkdownTableParser.parse_table(table_text)
        
        # Convert list of rows to single dict (form is key-value pairs)
        form_data = {}
        for row in rows:
            # Try different column name variations
            key = row.get('Form label') or row.get('Field') or row.get('Key') or ''
            value = row.get('value') or row.get('Value') or ''
            
            if key:
                # Normalize key names
                key_normalized = key.replace(' ', '')
                form_data[key_normalized] = value
        
        # Create FormTable with parsed values
        form = FormTable(
            actionNameToCreate=form_data.get('actionNameToCreate', ''),
            bpm=float(form_data.get('bpm', 120)) if form_data.get('bpm') else 120,
            beatsPerBar=int(form_data.get('beatsPerBar', 4)) if form_data.get('beatsPerBar') else 4,
            blendFileToOutputAction=form_data.get('blendFileToOutputAction', ''),
            poseBlendFile=form_data.get('poseBlendFile', ''),
            poseCatalog=form_data.get('poseCatalog', ''),
            midiFile=form_data.get('midiFile', '')
        )
        
        return form
    
    @staticmethod
    def parse_video_table(table_text: str, form: FormTable) -> None:
        """Parse video table and update FormTable object."""
        rows = MarkdownTableParser.parse_table(table_text)
        
        for row in rows:
            key = row.get('Form label') or row.get('Field') or row.get('Key') or ''
            value = row.get('value') or row.get('Value') or ''
            
            if 'shouldCreateVideo' in key:
                form.shouldCreateVideo = value.lower() in ['yes', 'true', '1']
            elif 'audioFile' in key:
                form.audioFile = value if value else None
            elif 'renderDir' in key:
                form.renderDir = value if value else None
            elif 'charFile' in key:
                form.charFile = value if value else None
    
    @staticmethod
    def parse_dance_table(table_text: str) -> DanceTable:
        """Parse dance table into DanceTable object."""
        rows = MarkdownTableParser.parse_table(table_text)
        dance = DanceTable()
        
        for row in rows:
            # Handle empty values with defaults
            pre_hold_str = row.get('preHold', '').strip()
            post_hold_str = row.get('postHold', '').strip()
            
            cycle_mode = row.get('cycle mode', '') or row.get('cycleMode', '')
            interpolation = row.get('interpolation', '')
            
            dance_row = DanceRow(
                poseCatalog=row.get('poseCatalog', ''),
                track=row.get('track', ''),
                cycleMode=cycle_mode if cycle_mode else 'loop',
                interpolation=interpolation if interpolation else 'cubic',
                preHold=int(pre_hold_str) if pre_hold_str else DEFAULT_PRE_HOLD,
                postHold=int(post_hold_str) if post_hold_str else DEFAULT_POST_HOLD
            )
            dance.add_row(dance_row)
        
        return dance
    
    @staticmethod
    def parse(markdown_text: str) -> HeadlessConfig:
        """Parse complete markdown input into HeadlessConfig."""
        sections = MarkdownTableParser.find_table_sections(markdown_text)
        
        # Parse form table (required)
        if 'form' not in sections:
            raise ValueError("Form table not found in input")
        form = MarkdownTableParser.parse_form_table(sections['form'])
        
        # Parse video table if present
        if 'video' in sections:
            MarkdownTableParser.parse_video_table(sections['video'], form)
        
        # Parse dance table (required)
        if 'dance' not in sections:
            raise ValueError("Dance table not found in input")
        dance = MarkdownTableParser.parse_dance_table(sections['dance'])
        
        return HeadlessConfig(form=form, dance=dance)