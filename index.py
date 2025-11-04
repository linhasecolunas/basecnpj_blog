#!/usr/bin/env python3
import os
import re
from pathlib import Path
from datetime import datetime

def parse_simple_yaml(text):
    """Parser simples de YAML para frontmatter básico"""
    data = {}
    for line in text.split('\n'):
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            
            # Trata listas simples (tags)
            if value.startswith('[') and value.endswith(']'):
                value = [v.strip().strip('"').strip("'") for v in value[1:-1].split(',')]
            
            data[key] = value
    return data

def extract_frontmatter(file_path):
    """Extrai o frontmatter de um arquivo markdown"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Procura por --- ... ---
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return None
        
        frontmatter_text = match.group(1)
        return parse_simple_yaml(frontmatter_text)
    except Exception as e:
        print(f"Erro ao ler {file_path}: {e}")
        return None

def find_all_posts():
    """Encontra todos os posts no diretório content/"""
    posts = []
    content_dir = Path('content')
    
    for item in content_dir.iterdir():
        if item.is_dir():
            index_file = item / 'index.md'
            if index_file.exists():
                frontmatter = extract_frontmatter(index_file)
                if frontmatter and 'title' in frontmatter and 'date' in frontmatter:
                    url = f"/{item.name}/"
                    
                    # Parse da data
                    date_str = str(frontmatter['date'])
                    try:
                        # Tenta ISO format primeiro
                        if 'T' in date_str:
                            date = datetime.fromisoformat(date_str.split('+')[0].split('-03:00')[0])
                        else:
                            date = datetime.strptime(date_str, '%Y-%m-%d')
                    except:
                        date = datetime.now()
                    
                    posts.append({
                        'title': frontmatter['title'],
                        'url': url,
                        'date': date,
                        'description': frontmatter.get('description', ''),
                        'tags': frontmatter.get('tags', []) if isinstance(frontmatter.get('tags', []), list) else []
                    })
    
    posts.sort(key=lambda x: x['date'], reverse=True)
    return posts

def generate_index():
    """Gera o arquivo _index.md com a lista de posts"""
    posts = find_all_posts()
    
    with open('content/_index.md', 'w', encoding='utf-8') as f:
        f.write("---\n")
        f.write("type: \"docs\"\n")
        f.write("toc: false\n")
        f.write("---\n\n")
        
        for post in posts:
            date_formatted = post['date'].strftime('%d/%m/%Y')
            f.write(f"### [{post['title']}]({post['url']})\n\n")
            f.write(f"📅 {date_formatted}\n\n")
            
            if post['description']:
                f.write(f"{post['description']}\n\n")
            
            if post['tags']:
                tags_str = ' '.join([f'`{tag}`' for tag in post['tags']])
                f.write(f"Tags: {tags_str}\n\n")
            
            f.write(f"[Ler mais →]({post['url']})\n\n")
            f.write("---\n\n")
    
    print(f"✅ Gerado _index.md com {len(posts)} posts!")

if __name__ == '__main__':
    generate_index()