/**
 * CCA Exam Management System - Global CSRF Auto-Protection
 * Integrates transparently with Flask-WTF CSRFProtect.
 */
(function() {
    function getCsrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : (window.csrfToken || '');
    }

    // Automatically inject hidden csrf_token input into all POST forms
    function injectCsrfInputs(container) {
        const token = getCsrfToken();
        if (!token) return;
        const forms = (container || document).querySelectorAll('form[method*="POST" i], form[method*="post" i]');
        forms.forEach(function(form) {
            let input = form.querySelector('input[name="csrf_token"]');
            if (!input) {
                input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'csrf_token';
                form.appendChild(input);
            }
            input.value = token;
        });
    }

    // Global helper for dynamic POST submissions (replaces window.location.href for deletions/actions)
    window.submitPostAction = function(url, extraData) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = url;
        const token = getCsrfToken();
        if (token) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'csrf_token';
            input.value = token;
            form.appendChild(input);
        }
        if (extraData && typeof extraData === 'object') {
            for (const key in extraData) {
                const hidden = document.createElement('input');
                hidden.type = 'hidden';
                hidden.name = key;
                hidden.value = extraData[key];
                form.appendChild(hidden);
            }
        }
        document.body.appendChild(form);
        form.submit();
    };

    // Automatically attach X-CSRFToken header to all fetch() calls
    if (window.fetch) {
        const originalFetch = window.fetch;
        window.fetch = function(url, options) {
            options = options || {};
            const method = (options.method || 'GET').toUpperCase();
            if (method !== 'GET' && method !== 'HEAD') {
                const token = getCsrfToken();
                if (token) {
                    if (!options.headers) {
                        options.headers = {};
                    }
                    if (options.headers instanceof Headers) {
                        if (!options.headers.has('X-CSRFToken')) {
                            options.headers.append('X-CSRFToken', token);
                        }
                    } else if (typeof options.headers === 'object') {
                        if (!options.headers['X-CSRFToken'] && !options.headers['x-csrftoken']) {
                            options.headers['X-CSRFToken'] = token;
                        }
                    }
                }
            }
            return originalFetch(url, options);
        };
    }

    // Automatically attach X-CSRFToken header to all XMLHttpRequest calls
    if (window.XMLHttpRequest) {
        const origOpen = XMLHttpRequest.prototype.open;
        const origSend = XMLHttpRequest.prototype.send;
        XMLHttpRequest.prototype.open = function(method, url) {
            this._csrf_method = method;
            return origOpen.apply(this, arguments);
        };
        XMLHttpRequest.prototype.send = function() {
            if (this._csrf_method && this._csrf_method.toUpperCase() !== 'GET' && this._csrf_method.toUpperCase() !== 'HEAD') {
                const token = getCsrfToken();
                if (token) {
                    try {
                        this.setRequestHeader('X-CSRFToken', token);
                    } catch(e) {}
                }
            }
            return origSend.apply(this, arguments);
        };
    }

    document.addEventListener('DOMContentLoaded', function() {
        injectCsrfInputs();
        if (window.MutationObserver) {
            new MutationObserver(function(mutations) {
                mutations.forEach(function(m) {
                    if (m.addedNodes) {
                        m.addedNodes.forEach(function(n) {
                            if (n.nodeType === 1) injectCsrfInputs(n);
                        });
                    }
                });
            }).observe(document.body, { childList: true, subtree: true });
        }
    });
})();
