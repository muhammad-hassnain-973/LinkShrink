// DOM Elements
const urlInput = document.getElementById('urlInput');
const shortenBtn = document.getElementById('shortenBtn');
const btnText = document.querySelector('.btn-text');
const loadingSpinner = document.querySelector('.loading-spinner');
const errorMessage = document.getElementById('errorMessage');
const resultSection = document.getElementById('resultSection');
const shortUrlInput = document.getElementById('shortUrl');
const originalUrlSpan = document.getElementById('originalUrl');
const copyBtn = document.getElementById('copyBtn');
const copyText = document.querySelector('.copy-text');
const shortenAnotherBtn = document.getElementById('shortenAnotherBtn');

// State
let isLoading = false;

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Focus on input when page loads
    urlInput.focus();
    
    // Add event listeners
    shortenBtn.addEventListener('click', handleShortenUrl);
    urlInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleShortenUrl();
        }
    });
    
    copyBtn.addEventListener('click', handleCopyUrl);
    shortenAnotherBtn.addEventListener('click', handleShortenAnother);
    
    // Clear error when user starts typing
    urlInput.addEventListener('input', function() {
        hideError();
    });
});

// Main Functions
async function handleShortenUrl() {
    if (isLoading) return;
    
    const url = urlInput.value.trim();
    
    // Validate input
    if (!url) {
        showError('Please enter a URL to shorten');
        urlInput.focus();
        return;
    }
    
    // Basic URL validation
    if (!isValidUrl(url)) {
        showError('Please enter a valid URL (e.g., https://example.com)');
        urlInput.focus();
        return;
    }
    
    // Show loading state
    setLoadingState(true);
    hideError();
    
    try {
        const response = await fetch('/api/shorten', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Show success result
            showResult(data);
        } else {
            // Show error
            showError(data.error || 'Failed to shorten URL. Please try again.');
        }
    } catch (error) {
        console.error('Error shortening URL:', error);
        showError('Network error. Please check your connection and try again.');
    } finally {
        setLoadingState(false);
    }
}

function handleCopyUrl() {
    const shortUrl = shortUrlInput.value;
    
    // Use modern clipboard API if available
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(shortUrl).then(() => {
            showCopySuccess();
        }).catch(() => {
            fallbackCopyTextToClipboard(shortUrl);
        });
    } else {
        // Fallback for older browsers
        fallbackCopyTextToClipboard(shortUrl);
    }
}

function handleShortenAnother() {
    // Reset form
    urlInput.value = '';
    hideResult();
    hideError();
    urlInput.focus();
}

// Helper Functions
function isValidUrl(string) {
    try {
        // Add protocol if missing
        let url = string;
        if (!url.startsWith('http://') && !url.startsWith('https://')) {
            url = 'http://' + url;
        }
        
        new URL(url);
        
        // Additional validation
        const urlPattern = /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/;
        return urlPattern.test(string) || urlPattern.test(url);
    } catch (_) {
        return false;
    }
}

function setLoadingState(loading) {
    isLoading = loading;
    
    if (loading) {
        btnText.style.display = 'none';
        loadingSpinner.style.display = 'block';
        shortenBtn.disabled = true;
        urlInput.disabled = true;
    } else {
        btnText.style.display = 'block';
        loadingSpinner.style.display = 'none';
        shortenBtn.disabled = false;
        urlInput.disabled = false;
    }
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    
    // Auto-hide error after 5 seconds
    setTimeout(() => {
        hideError();
    }, 5000);
}

function hideError() {
    errorMessage.style.display = 'none';
}

function showResult(data) {
    // Get the current domain for the full short URL
    const currentDomain = window.location.origin;
    const fullShortUrl = currentDomain + data.short_url;
    
    // Update result elements
    shortUrlInput.value = fullShortUrl;
    originalUrlSpan.textContent = data.original_url;
    
    // Show result section
    resultSection.style.display = 'block';
    
    // Scroll to result
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // Select the short URL for easy copying
    shortUrlInput.select();
    shortUrlInput.setSelectionRange(0, 99999); // For mobile devices
}

function hideResult() {
    resultSection.style.display = 'none';
}

function showCopySuccess() {
    const originalText = copyText.textContent;
    const originalColor = copyBtn.style.backgroundColor;
    
    copyText.textContent = 'Copied!';
    copyBtn.classList.add('copied');
    
    setTimeout(() => {
        copyText.textContent = originalText;
        copyBtn.classList.remove('copied');
    }, 2000);
}

function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    
    // Avoid scrolling to bottom
    textArea.style.top = '0';
    textArea.style.left = '0';
    textArea.style.position = 'fixed';
    
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showCopySuccess();
        } else {
            console.error('Fallback: Copying text command was unsuccessful');
        }
    } catch (err) {
        console.error('Fallback: Oops, unable to copy', err);
    }
    
    document.body.removeChild(textArea);
}

// Analytics and tracking (placeholder for future implementation)
function trackEvent(eventName, properties = {}) {
    // This can be used to track user interactions
    // For example, with Google Analytics or other analytics services
    console.log('Event tracked:', eventName, properties);
}

// Track URL shortening
function trackUrlShortened(originalUrl, shortCode) {
    trackEvent('url_shortened', {
        original_url_length: originalUrl.length,
        short_code: shortCode
    });
}

// Track URL copying
function trackUrlCopied() {
    trackEvent('url_copied');
}

// Performance monitoring
window.addEventListener('load', function() {
    // Track page load time
    const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
    trackEvent('page_loaded', {
        load_time: loadTime
    });
});

// Error handling for uncaught errors
window.addEventListener('error', function(e) {
    console.error('Uncaught error:', e.error);
    trackEvent('javascript_error', {
        message: e.message,
        filename: e.filename,
        lineno: e.lineno
    });
});

// Service Worker registration (for future PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Uncomment when service worker is implemented
        // navigator.serviceWorker.register('/sw.js')
        //     .then(function(registration) {
        //         console.log('ServiceWorker registration successful');
        //     })
        //     .catch(function(err) {
        //         console.log('ServiceWorker registration failed: ', err);
        //     });
    });
}

