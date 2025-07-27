from flask import Blueprint, request, jsonify, redirect, url_for
from src.models.url import Url, db
import validators
import re

url_bp = Blueprint('url', __name__)

def is_valid_url(url):
    """Validate if the provided URL is valid"""
    if not url:
        return False
    
    # Add http:// if no protocol is specified
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    return validators.url(url)

def normalize_url(url):
    """Normalize the URL by adding protocol if missing"""
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    return url

@url_bp.route('/shorten', methods=['POST'])
def shorten_url():
    """Create a shortened URL"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        original_url = data['url'].strip()
        
        if not original_url:
            return jsonify({'error': 'URL cannot be empty'}), 400
        
        # Validate URL
        if not is_valid_url(original_url):
            return jsonify({'error': 'Invalid URL format'}), 400
        
        # Normalize URL
        original_url = normalize_url(original_url)
        
        # Check if URL already exists
        existing_url = Url.query.filter_by(original_url=original_url).first()
        if existing_url:
            return jsonify({
                'success': True,
                'short_url': f'/{existing_url.short_code}',
                'original_url': existing_url.original_url,
                'short_code': existing_url.short_code,
                'created_at': existing_url.created_at.isoformat(),
                'click_count': existing_url.click_count
            }), 200
        
        # Generate short code
        short_code = Url.generate_short_code()
        
        # Create new URL entry
        new_url = Url(
            original_url=original_url,
            short_code=short_code
        )
        
        db.session.add(new_url)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'short_url': f'/{short_code}',
            'original_url': original_url,
            'short_code': short_code,
            'created_at': new_url.created_at.isoformat(),
            'click_count': 0
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@url_bp.route('/stats/<short_code>', methods=['GET'])
def get_url_stats(short_code):
    """Get statistics for a shortened URL"""
    try:
        url_entry = Url.query.filter_by(short_code=short_code).first()
        
        if not url_entry:
            return jsonify({'error': 'Short URL not found'}), 404
        
        return jsonify({
            'success': True,
            'stats': url_entry.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@url_bp.route('/<short_code>')
def redirect_url(short_code):
    """Redirect to the original URL"""
    try:
        # Validate short code format (alphanumeric only)
        if not re.match(r'^[a-zA-Z0-9]+$', short_code):
            return jsonify({'error': 'Invalid short code format'}), 400
        
        url_entry = Url.query.filter_by(short_code=short_code).first()
        
        if not url_entry:
            return jsonify({'error': 'Short URL not found'}), 404
        
        # Increment click count
        url_entry.increment_click_count()
        
        # Redirect to original URL
        return redirect(url_entry.original_url, code=301)
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

