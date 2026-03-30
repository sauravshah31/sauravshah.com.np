// ============================================
// Theme Management
// ============================================

// Load saved theme preferences
function loadThemePreferences() {
    // Check if user has manually set night mode preference
    const nightModePreference = localStorage.getItem('nightMode');
    
    if (nightModePreference === 'true') {
        document.body.classList.add('night-mode');
        document.getElementById('nightModeToggle').classList.add('active');
    } else if (nightModePreference === 'false') {
        // User explicitly disabled night mode
        document.body.classList.remove('night-mode');
        document.getElementById('nightModeToggle').classList.remove('active');
    } else {
        // No preference set, use system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.body.classList.add('night-mode');
            document.getElementById('nightModeToggle').classList.add('active');
        }
    }
}

// Night Mode Toggle
document.getElementById('nightModeToggle').addEventListener('click', function() {
    document.body.classList.toggle('night-mode');
    this.classList.toggle('active');
    
    // Save preference
    const isActive = document.body.classList.contains('night-mode');
    localStorage.setItem('nightMode', isActive);
});

// ============================================
// Slideshow Functionality
// ============================================

/**
 * Load a single image URL, retrying up to maxRetries times on failure.
 * Returns the loaded HTMLImageElement, or null if all attempts fail.
 */
async function loadImageWithRetry(url, maxRetries = 5) {
    for (let attempt = 0; attempt < maxRetries; attempt++) {
        const img = await new Promise(resolve => {
            const el = new Image();
            el.onload  = () => resolve(el);
            el.onerror = () => resolve(null);
            el.src = url;
        });
        if (img) return img;
        // Exponential back-off: 500 ms, 1 s, 1.5 s, 2 s …
        if (attempt < maxRetries - 1) {
            await new Promise(r => setTimeout(r, 500 * (attempt + 1)));
        }
    }
    return null; // all retries exhausted
}

/**
 * Initialise a single slideshow container.
 * URLs are read from data-slides (JSON array).
 * All images are loaded in parallel via Promise.all; only successfully
 * loaded images are inserted into the DOM — no blank/alt-text placeholders.
 */
async function initializeSlideshow(container) {
    let urls;
    try {
        urls = JSON.parse(container.dataset.slides || '[]');
    } catch (e) {
        return;
    }
    if (!urls.length) return;

    const interval = parseInt(container.dataset.interval) || 3000;

    // Load all images in parallel (each with its own retry budget)
    const results = await Promise.all(urls.map(url => loadImageWithRetry(url)));
    const images  = results.filter(img => img !== null);

    if (!images.length) return; // every image failed — leave container empty

    // Insert only the successfully loaded images
    images.forEach((img, i) => {
        img.classList.add('slide');
        if (i === 0) img.classList.add('active');
        container.appendChild(img);
    });

    // Start auto-advance only when there is more than one image
    if (images.length > 1) {
        let current = 0;
        setInterval(() => {
            images[current].classList.remove('active');
            current = (current + 1) % images.length;
            images[current].classList.add('active');
        }, interval);
    }
}

function initializeSlideshows() {
    document.querySelectorAll('.slideshow[data-slides]').forEach(container => {
        initializeSlideshow(container); // fire-and-forget; runs in background
    });
}

// ============================================
// Smooth Scroll for Anchor Links
// ============================================

function initializeSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            e.preventDefault();
            const target = document.querySelector(href);
            
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// ============================================
// Lazy Loading for Images
// ============================================

function initializeLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    observer.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// ============================================
// Video Auto-pause on Scroll Out
// ============================================

function initializeVideoAutoPause() {
    if ('IntersectionObserver' in window) {
        const videoObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                const video = entry.target;
                if (!entry.isIntersecting && !video.paused) {
                    video.pause();
                }
            });
        }, {
            threshold: 0.5
        });
        
        document.querySelectorAll('video').forEach(video => {
            videoObserver.observe(video);
        });
    }
}

// ============================================
// Keyboard Navigation
// ============================================

function initializeKeyboardNavigation() {
    document.addEventListener('keydown', (e) => {
        // Escape key to go back
        if (e.key === 'Escape') {
            const backLink = document.querySelector('.back-link');
            if (backLink) {
                backLink.click();
            }
        }
        
        // N key for night mode
        if (e.key === 'n' || e.key === 'N') {
            if (!isInputFocused()) {
                document.getElementById('nightModeToggle').click();
            }
        }
    });
}

function isInputFocused() {
    const activeElement = document.activeElement;
    return activeElement && (
        activeElement.tagName === 'INPUT' ||
        activeElement.tagName === 'TEXTAREA' ||
        activeElement.isContentEditable
    );
}

// ============================================
// System Theme Change Listener
// ============================================

function initializeSystemThemeListener() {
    // Listen for system theme changes
    if (window.matchMedia) {
        const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        darkModeQuery.addEventListener('change', (e) => {
            // Only apply system preference if user hasn't manually set a preference
            const nightModePreference = localStorage.getItem('nightMode');
            
            if (nightModePreference === null) {
                if (e.matches) {
                    document.body.classList.add('night-mode');
                    document.getElementById('nightModeToggle').classList.add('active');
                } else {
                    document.body.classList.remove('night-mode');
                    document.getElementById('nightModeToggle').classList.remove('active');
                }
            }
        });
    }
}

// ============================================
// Initialize Everything on Page Load
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    loadThemePreferences();
    initializeSystemThemeListener();
    initializeSlideshows();
    initializeSmoothScroll();
    initializeLazyLoading();
    initializeVideoAutoPause();
    initializeKeyboardNavigation();
    initializeImageProtection();
    initializeCommentForm();
    
    // Add fade-in animation
    document.body.style.opacity = '0';
    setTimeout(() => {
        document.body.style.transition = 'opacity 0.3s ease';
        document.body.style.opacity = '1';
    }, 10);
});

// ============================================
// Image Protection
// ============================================

function initializeImageProtection() {
    document.querySelectorAll('img').forEach(img => {
        // Prevent drag-to-new-tab / drag-to-desktop
        img.setAttribute('draggable', 'false');
        img.addEventListener('dragstart', e => e.preventDefault());

        // Prevent right-click context menu (Save image / Open in new tab)
        img.addEventListener('contextmenu', e => e.preventDefault());
    });

    // Also block right-click on image-containing wrappers so the
    // browser's "Save image" option can't be triggered via the parent
    const imageWrappers = document.querySelectorAll(
        '.header-photo, .header-slideshow, .gallery, ' +
        '.slideshow, .photo-embed, .video-container, .short-video'
    );
    imageWrappers.forEach(el => {
        el.addEventListener('contextmenu', e => e.preventDefault());
    });
}

// ============================================
// Comment Form Submission
// ============================================

function initializeCommentForm() {
    const form = document.getElementById('commentForm');
    if (!form) return;

    const submitBtn = document.getElementById('commentSubmit');
    const statusEl = document.getElementById('formStatus');

    function setStatus(message, type) {
        statusEl.textContent = message;
        statusEl.className = 'form-status ' + type;
    }

    function clearStatus() {
        statusEl.textContent = '';
        statusEl.className = 'form-status';
    }

    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        clearStatus();

        // Basic client-side validation
        const name = form.querySelector('[name="name"]').value.trim();
        const message = form.querySelector('[name="message"]').value.trim();

        if (!name) {
            setStatus('Please enter your name. "fellow human" also works 😊', 'error');
            form.querySelector('[name="name"]').focus();
            return;
        }
        if (!message) {
            setStatus('Please write a message before sending.', 'error');
            form.querySelector('[name="message"]').focus();
            return;
        }

        // Build payload
        const payload = {
            access_key: form.querySelector('[name="access_key"]').value,
            title: "sauravshah.com.np - " + form.querySelector('[name="title"]').value,
            name: name,
            email: form.querySelector('[name="email"]').value.trim(),
            message: message
        };

        // Disable button while submitting
        submitBtn.disabled = true;
        submitBtn.querySelector('span').textContent = 'Sending…';

        try {
            const response = await fetch('https://formly.email/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
                redirect: 'manual'
            });

            const success = response.type === 'opaqueredirect' || response.status === 0 || response.ok;

            if (success) {
                setStatus('Thank you! Your message has been sent.', 'success');
                form.reset();
            } else {
                setStatus('Something went wrong. Please try again.', 'error');
            }
        } catch (err) {
            // Network errors or CORS opaque responses land here
            // For no-cors / opaque responses the fetch resolves, not rejects,
            // so a catch here means a genuine network failure.
            setStatus('Could not send message. Check your connection and try again.', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.querySelector('span').textContent = 'Send Message';
        }
    });
}

// ============================================
// Print Functionality
// ============================================

// Remove theme classes before printing
window.addEventListener('beforeprint', () => {
    document.body.classList.remove('night-mode');
});

// Restore theme classes after printing
window.addEventListener('afterprint', () => {
    loadThemePreferences();
});
