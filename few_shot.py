import json
import os
from pathlib import Path

class FewShotPosts:
    """Class to manage few-shot examples for post generation"""
    
    def __init__(self, file_path="data/processed_posts.json"):
        self.file_path = file_path
        self.posts = self._load_posts()
        self.tags = self._extract_tags()
        
    def _load_posts(self):
        """Load posts from the JSON file"""
        if not os.path.exists(self.file_path):
            return []
            
        with open(self.file_path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    
    def _extract_tags(self):
        """Extract all unique tags from posts"""
        if not self.posts:
            return ["Job Search", "Motivation", "Career Advice", "Leadership", "Self Improvement"]
            
        all_tags = set()
        for post in self.posts:
            if 'tags' in post and isinstance(post['tags'], list):
                all_tags.update(post['tags'])
        
        return sorted(list(all_tags))
    
    def get_tags(self):
        """Get all available tags"""
        return self.tags
    
    def get_filtered_posts(self, length=None, language=None, tag=None, max_examples=5):
        """
        Get posts filtered by length, language, and tag
        
        Args:
            length: "Short", "Medium", or "Long"
            language: "English", "Hinglish", etc.
            tag: Topic tag
            max_examples: Maximum number of examples to return
            
        Returns:
            List of matching posts
        """
        filtered_posts = self.posts.copy()
        
        # Apply length filter
        if length and filtered_posts:
            if length == "Short":
                filtered_posts = [p for p in filtered_posts if p.get('line_count', 0) <= 5]
            elif length == "Medium":
                filtered_posts = [p for p in filtered_posts if 6 <= p.get('line_count', 0) <= 10]
            elif length == "Long":
                filtered_posts = [p for p in filtered_posts if p.get('line_count', 0) >= 11]
        
        # Apply language filter
        if language and filtered_posts:
            filtered_posts = [p for p in filtered_posts if p.get('language', '').lower() == language.lower()]
        
        # Apply tag filter
        if tag and filtered_posts:
            filtered_posts = [p for p in filtered_posts if tag in p.get('tags', [])]
        
        # Return at most max_examples posts
        return filtered_posts[:max_examples]
    
    def add_post(self, post_text, metadata=None):
        """
        Add a new post to the collection
        
        Args:
            post_text: The text content of the post
            metadata: Dictionary with keys like tags, language, line_count
        """
        if metadata is None:
            metadata = {}
            
        new_post = {
            "text": post_text,
            **metadata
        }
        
        self.posts.append(new_post)
        
        # Save to file
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.posts, f, indent=4, ensure_ascii=False)
        
        # Refresh tags
        self.tags = self._extract_tags()