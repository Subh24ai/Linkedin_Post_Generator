import json
import sys
import os
from pathlib import Path
import pandas as pd
from tqdm import tqdm
from llm_helper import llm, refresh_llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

def process_posts(raw_file_path, processed_file_path="data/processed_posts.json", batch_size=10):
    """
    Process raw LinkedIn posts to extract metadata and unify tags
    
    Args:
        raw_file_path: Path to raw posts JSON file
        processed_file_path: Output path for processed posts
        batch_size: Number of posts to process in one batch (for progress tracking)
    """
    # Ensure output directory exists
    Path(processed_file_path).parent.mkdir(exist_ok=True, parents=True)
    
    print(f"Loading posts from {raw_file_path}...")
    with open(raw_file_path, encoding='utf-8') as file:
        posts = json.load(file)
        
        # Process in batches with progress bar
        enriched_posts = []
        print(f"Processing {len(posts)} posts...")
        
        # Configure LLM with higher temperature for more varied metadata extraction
        refresh_llm(temperature=0.3, max_tokens=500)
        
        for i in tqdm(range(0, len(posts), batch_size), desc="Extracting metadata"):
            batch = posts[i:i+batch_size]
            
            for post in batch:
                try:
                    # Skip if already processed
                    if 'tags' in post and 'line_count' in post and 'language' in post:
                        enriched_posts.append(post)
                        continue
                        
                    metadata = extract_metadata(post['text'])
                    post_with_metadata = {**post, **metadata}
                    enriched_posts.append(post_with_metadata)
                except Exception as e:
                    print(f"Error processing post: {str(e)[:100]}...")
                    # Add with default metadata
                    enriched_posts.append({
                        **post, 
                        'tags': ['Other'],
                        'line_count': len(post['text'].split('\n')),
                        'language': 'English'
                    })
        
        # Reset LLM to default settings
        refresh_llm()
        
        print("Unifying tags...")
        unified_tags = get_unified_tags(enriched_posts)
        
        # Apply unified tags
        for post in enriched_posts:
            if 'tags' in post:
                current_tags = post['tags']
                new_tags = [unified_tags.get(tag, tag) for tag in current_tags]
                post['tags'] = list(set(new_tags))  # Remove duplicates
            else:
                post['tags'] = ['Other']

    # Save processed posts
    print(f"Saving processed posts to {processed_file_path}...")
    with open(processed_file_path, encoding='utf-8', mode="w") as outfile:
        json.dump(enriched_posts, outfile, indent=4, ensure_ascii=False)
    
    # Generate statistics
    generate_statistics(enriched_posts)
    
    print("Processing complete!")
    return enriched_posts

def extract_metadata(post):
    """
    Extract metadata from post text using LLM
    
    Args:
        post: Text content of the post
        
    Returns:
        Dictionary with keys: line_count, language, tags
    """
    template = '''
    You are given a LinkedIn post. Extract the following metadata:
    1. Number of lines in the post
    2. Language (English, Hinglish, Hindi, or other)
    3. Up to 3 topic tags that best represent this post
    
    Return a valid JSON object with exactly three keys:
    - line_count: Integer representing number of lines
    - language: String (English, Hinglish, Hindi, or other language name)
    - tags: Array of strings (maximum 3 tags)
    
    Post:
    {post}
    
    JSON RESPONSE:
    '''

    pt = PromptTemplate.from_template(template)
    chain = pt | llm
    response = chain.invoke(input={"post": post})

    try:
        json_parser = JsonOutputParser()
        result = json_parser.parse(response.content)
        
        # Validate and clean up result
        if not isinstance(result.get('line_count'), int):
            result['line_count'] = len(post.split('\n'))
            
        if not isinstance(result.get('tags'), list):
            result['tags'] = ['Other']
            
        # Ensure tags are properly formatted
        result['tags'] = [tag.strip() for tag in result.get('tags', ['Other'])]
        
        return result
    except Exception as e:
        # Fallback to basic metadata extraction
        lines = post.split('\n')
        return {
            'line_count': len(lines),
            'language': 'English',
            'tags': ['Other']
        }

def get_unified_tags(posts_with_metadata):
    """
    Create a unified tag mapping to consolidate similar tags
    
    Args:
        posts_with_metadata: List of posts with metadata including tags
        
    Returns:
        Dictionary mapping original tags to unified tags
    """
    unique_tags = set()
    
    # Extract all unique tags
    for post in posts_with_metadata:
        if 'tags' in post and isinstance(post['tags'], list):
            unique_tags.update(post['tags'])
    
    # If too few tags, no need to unify
    if len(unique_tags) < 5:
        return {tag: tag for tag in unique_tags}
        
    unique_tags_list = ', '.join(unique_tags)

    template = '''
    I will give you a list of tags from LinkedIn posts. Create a unified tag mapping with these requirements:
    
    1. Similar tags should be mapped to a single standardized tag
       Examples:
       - "Jobseekers", "Job Hunting" → "Job Search"
       - "Motivation", "Inspiration" → "Motivation"
       - "Personal Growth", "Self Improvement" → "Self Improvement"
    
    2. Use title case for all unified tags (e.g., "Job Search", "Career Advice")
    
    3. Limit the final set to 10-15 broad categories maximum
    
    4. Output must be a valid JSON object mapping original tags to unified tags
       Format: {"original_tag1": "Unified Tag", "original_tag2": "Unified Tag"}
    
    Tags to unify:
    {tags}
    
    JSON RESPONSE:
    '''
    
    try:
        pt = PromptTemplate.from_template(template)
        chain = pt | llm
        response = chain.invoke(input={"tags": str(unique_tags_list)})
        
        json_parser = JsonOutputParser()
        unified_tags = json_parser.parse(response.content)
        
        # Validate result
        if not isinstance(unified_tags, dict):
            raise ValueError("Invalid unified tags response")
            
        # Ensure all unique tags are included
        for tag in unique_tags:
            if tag not in unified_tags:
                unified_tags[tag] = tag
                
        return unified_tags
    except Exception as e:
        print(f"Error unifying tags: {str(e)}")
        # Fallback: return identity mapping
        return {tag: tag for tag in unique_tags}

def generate_statistics(posts):
    """
    Generate statistics about the processed posts
    
    Args:
        posts: List of processed posts with metadata
    """
    if not posts:
        return
        
    # Create directory for statistics
    stats_dir = Path("data/statistics")
    stats_dir.mkdir(exist_ok=True, parents=True)
    
    # Extract basic stats
    total_posts = len(posts)
    languages = {}
    tags = {}
    line_counts = []
    
    for post in posts:
        # Language stats
        lang = post.get('language', 'Unknown')
        languages[lang] = languages.get(lang, 0) + 1
        
        # Tag stats
        for tag in post.get('tags', []):
            tags[tag] = tags.get(tag, 0) + 1
            
        # Line count stats
        line_counts.append(post.get('line_count', 0))
    
    # Create stats
    stats = {
        "total_posts": total_posts,
        "languages": languages,
        "tags": tags,
        "line_count_avg": sum(line_counts) / len(line_counts) if line_counts else 0,
        "line_count_min": min(line_counts) if line_counts else 0,
        "line_count_max": max(line_counts) if line_counts else 0,
    }
    
    # Save statistics
    with open(stats_dir / "post_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)
    
    # Create CSV versions for analysis
    try:
        # Tags CSV
        pd.DataFrame([{"tag": k, "count": v} for k, v in tags.items()]) \
            .to_csv(stats_dir / "tag_stats.csv", index=False)
            
        # Languages CSV
        pd.DataFrame([{"language": k, "count": v} for k, v in languages.items()]) \
            .to_csv(stats_dir / "language_stats.csv", index=False)
    except Exception as e:
        print(f"Error creating statistics CSVs: {e}")
    
    print(f"Generated statistics saved to {stats_dir}")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')  # Ensure UTF-8 encoding for output
    
    # Default paths
    raw_path = "data/raw_posts.json"
    processed_path = "data/processed_posts.json"
    
    # Allow command line arguments to override defaults
    if len(sys.argv) > 1:
        raw_path = sys.argv[1]
    if len(sys.argv) > 2:
        processed_path = sys.argv[2]
    
    process_posts(raw_path, processed_path)