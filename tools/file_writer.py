"""File writer tool for Agent Code."""

from pathlib import Path
from typing import Dict, Any
import aiofiles
from ui.display import display_success, display_error
from .path_resolver import PathResolver


class FileWriter:
    """Tool for writing content to files."""
    
    def __init__(self, workspace_path: str):
        """Initialize the file writer with workspace path."""
        self.workspace_path = Path(workspace_path).resolve()
        self.path_resolver = PathResolver(workspace_path)
        
    async def write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Write content to a file."""
        try:
            if not file_path:
                return {
                    "success": False,
                    "error": "No file path provided",
                    "output": ""
                }
            
            # Resolve path relative to workspace
            full_path = self.path_resolver.resolve_path(file_path)
            
            # Process content with intelligent escape sequence handling
            processed_content = self._process_content(content)
            
            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(full_path, mode='w', encoding='utf-8') as f:
                await f.write(processed_content)
            
            display_success(f"Wrote file: {file_path} ({len(processed_content)} characters)")
            
            return {
                "success": True,
                "output": f"Successfully wrote {len(processed_content)} characters to {file_path}",
                "file_path": str(full_path),
                "size": len(processed_content)
            }
            
        except Exception as e:
            error_msg = f"Failed to write file {file_path}: {e}"
            display_error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "output": ""
            }
    
    def _process_content(self, content: str) -> str:
        """
        Intelligently process content to handle escape sequences for any file format.
        
        This function uses a generic approach that works across multiple languages
        and file formats by detecting patterns rather than language-specific syntax.
        """
        if not content:
            return content
            
        # Detect file type from common patterns to apply appropriate processing
        file_context = self._detect_content_context(content)
        
        # Apply generic escape sequence processing
        processed_content = self._process_escape_sequences(content, file_context)
        
        return processed_content
    
    def _detect_content_context(self, content: str) -> dict:
        """
        Detect the type of content and context to apply appropriate processing.
        
        Returns a context dictionary with detected patterns and characteristics.
        """
        context = {
            'has_escaped_quotes': False,
            'has_escaped_newlines': False,
            'has_escaped_tabs': False,
            'quote_style': 'mixed',  # 'single', 'double', 'mixed'
            'likely_language': 'text',  # 'python', 'javascript', 'json', 'html', 'css', 'text'
            'likely_overescaped': False
        }
        
        # Check for escaped sequences
        context['has_escaped_quotes'] = '\\"' in content or "\\'" in content
        context['has_escaped_newlines'] = '\\n' in content and content.count('\\n') > content.count('\n')
        context['has_escaped_tabs'] = '\\t' in content and content.count('\\t') > content.count('\t')
        
        # Detect quote style preference
        double_quotes = content.count('"') + content.count('\\"')
        single_quotes = content.count("'") + content.count("\\'")
        
        if double_quotes > single_quotes * 2:
            context['quote_style'] = 'double'
        elif single_quotes > double_quotes * 2:
            context['quote_style'] = 'single'
        else:
            context['quote_style'] = 'mixed'
        
        # Detect likely language/format
        context['likely_language'] = self._detect_language(content)
        
        # Detect if content appears over-escaped
        context['likely_overescaped'] = self._is_likely_overescaped(content)
        
        return context
    
    def _detect_language(self, content: str) -> str:
        """Detect the likely programming language or file format."""
        content_lower = content.lower()
        
        # JSON detection
        if content.strip().startswith(('{', '[')):
            return 'json'
        
        # HTML/XML detection
        if '<' in content and '>' in content:
            if any(tag in content_lower for tag in ['<html>', '<div>', '<span>', '<p>', '<body>']):
                return 'html'
            elif content.strip().startswith('<?xml') or '</' in content:
                return 'xml'
        
        # CSS detection
        if '{' in content and '}' in content and ':' in content:
            if any(prop in content_lower for prop in ['color:', 'font-', 'margin:', 'padding:']):
                return 'css'
        
        # JavaScript detection
        if any(keyword in content for keyword in ['function ', 'const ', 'let ', 'var ', '=>']):
            return 'javascript'
        
        # Python detection
        if any(keyword in content for keyword in ['def ', 'import ', 'class ', '__name__', 'print(']):
            return 'python'
        
        # Shell script detection
        if content.startswith('#!') or any(cmd in content for cmd in ['#!/bin/', 'echo ', '$(', '${', 'export ']):
            return 'shell'
        
        # Markdown detection
        if any(marker in content for marker in ['# ', '## ', '- ', '* ', '```', '[', '](']):
            return 'markdown'
        
        return 'text'
    
    def _is_likely_overescaped(self, content: str) -> bool:
        """
        Determine if content appears to be over-escaped.
        
        Over-escaped content typically has more escaped sequences than actual characters.
        """
        # Count various escape patterns
        escaped_quotes = content.count('\\"') + content.count("\\'")
        escaped_newlines = content.count('\\n')
        escaped_tabs = content.count('\\t')
        
        # Count actual characters
        actual_quotes = content.count('"') + content.count("'") - escaped_quotes
        actual_newlines = content.count('\n')
        actual_tabs = content.count('\t')
        
        # If we have significantly more escaped than actual, it's likely over-escaped
        total_escaped = escaped_quotes + escaped_newlines + escaped_tabs
        total_actual = actual_quotes + actual_newlines + actual_tabs
        
        return total_escaped > 0 and (total_escaped >= total_actual or total_escaped > 3)
    
    def _process_escape_sequences(self, content: str, context: dict) -> str:
        """
        Process escape sequences based on the detected context.
        
        This is the main processing function that applies transformations
        based on the content analysis.
        """
        if not context['likely_overescaped']:
            return content
        
        processed = content
        
        # Handle quotes based on detected language and patterns
        if context['has_escaped_quotes']:
            processed = self._process_quotes(processed, context)
        
        # Handle newlines and tabs
        if context['has_escaped_newlines']:
            processed = processed.replace('\\n', '\n')
        
        if context['has_escaped_tabs']:
            processed = processed.replace('\\t', '\t')
        
        # Handle other escape sequences
        processed = processed.replace('\\r', '\r')
        
        # Handle escaped backslashes (do this last)
        processed = processed.replace('\\\\', '\\')
        
        return processed
    
    def _process_quotes(self, content: str, context: dict) -> str:
        """
        Process quotes based on the detected language and context.
        
        This handles quotes differently based on the file type and patterns.
        """
        language = context['likely_language']
        
        if language == 'json':
            # JSON requires double quotes, so convert escaped doubles to doubles
            content = content.replace('\\"', '"')
            # But preserve escaped singles if they're inside strings
            return content
        
        elif language in ['python', 'javascript']:
            # For programming languages, use context-aware quote processing
            return self._process_programming_quotes(content)
        
        elif language == 'html':
            # HTML attributes typically use double quotes
            content = content.replace('\\"', '"')
            return content
        
        elif language == 'css':
            # CSS can use both, preserve the dominant style
            if context['quote_style'] == 'double':
                content = content.replace('\\"', '"')
            elif context['quote_style'] == 'single':
                content = content.replace("\\'", "'")
            else:
                # Mixed - process both
                content = content.replace('\\"', '"')
                content = content.replace("\\'", "'")
            return content
        
        else:
            # For text and unknown formats, process both types
            content = content.replace('\\"', '"')
            content = content.replace("\\'", "'")
            return content
    
    def _process_programming_quotes(self, content: str) -> str:
        """
        Process quotes in programming languages using pattern matching.
        
        This looks for common patterns where quotes are used in programming
        contexts and converts escaped quotes appropriately.
        """
        import re
        
        # More comprehensive patterns that handle various quote scenarios
        patterns = [
            # Simple escaped quotes within strings (most common case)
            (r'\\"([^"\\]*)\\"', r'"\1"'),  # \\"text\\" -> "text"
            (r"\\'([^'\\]*)\\'", r"'\1'"),  # \\'text\\' -> 'text'
            
            # Mixed scenarios: \\"text" or "text\\"
            (r'\\"([^"]*)"', r'"\1"'),      # \\"text" -> "text"
            (r'"\\"([^"]*)', r'"\1"'),      # "\\"text -> "text (this shouldn't happen but just in case)
            (r'"([^"]*)\\"', r'"\1"'),      # "text\\" -> "text"
            
            # Same for single quotes
            (r"\\'([^']*)'", r"'\1'"),      # \\'text' -> 'text'
            (r"'\\'([^']*)", r"'\1'"),      # '\\'text -> 'text (this shouldn't happen but just in case)
            (r"'([^']*)\\'", r"'\1'"),      # 'text\\' -> 'text'
            
            # Context-specific patterns
            # Function calls: func(\\"string\\") 
            (r'(\w+\s*\(\s*[^)]*)\\"([^"]*)\\"', r'\1"\2"'),
            (r"(\w+\s*\(\s*[^)]*)\\'([^']*)\\'", r"\1'\2'"),
            
            # Variable assignments: var = \\"string\\"
            (r'(\w+\s*[=:]\s*)\\"([^"]*)\\"', r'\1"\2"'),
            (r"(\w+\s*[=:]\s*)\\'([^']*)\\'", r"\1'\2'"),
            
            # Comparisons: if x == \\"string\\"
            (r'([=!<>]+\s*)\\"([^"]*)\\"', r'\1"\2"'),
            (r"([=!<>]+\s*)\\'([^']*)\\'", r"\1'\2'"),
            
            # Return statements: return \\"string\\"
            (r'(return\s+)\\"([^"]*)\\"', r'\1"\2"'),
            (r"(return\s+)\\'([^']*)\\'", r"\1'\2'"),
        ]
        
        # Apply patterns in order, being careful not to double-process
        processed = content
        for pattern, replacement in patterns:
            processed = re.sub(pattern, replacement, processed)
        
        return processed
