/**
 * CCA Exam Management System - Live Notification Badge (polling)
 * Polls /api/notifications/unread_count and refreshes every bell badge on the page
 * (sidebar + top header) without a page reload.
 *  - Polls only while the tab is visible (saves server load on idle tabs).
 *  - Backs off on network/server errors.
 *  - Stops when the session expires (server returns 401).
 */
(function () {
    if (window.__notifPollInit) return;   // sidebar may be included more than once
    window.__notifPollInit = true;

    var ENDPOINT = '/api/notifications/unread_count';
    var BASE_INTERVAL = 4000;    // 4 seconds for responsive real-time updates
    var MAX_INTERVAL = 60000;    // 1 minute when errors occur
    var interval = BASE_INTERVAL;
    var timer = null;
    var lastCount = null;
    var lastSignature = null;
    var pendingReload = false;
    var stopped = false;
    var baseTitle = document.title.replace(/^\(\d+\+?\)\s*/, '');

    function label(n) { return n > 99 ? '99+' : String(n); }

    function clearBadges(link) {
        // Remove the Jinja-rendered or previously injected badges
        link.querySelectorAll('span').forEach(function (s) {
            if (s.isConnected && s.querySelector('.animate-ping')) s.remove();
        });
        link.querySelectorAll('span.bg-red-500, [data-notif-badge]').forEach(function (s) { s.remove(); });
    }

    function renderLink(link, n) {
        clearBadges(link);
        if (n <= 0) return;
        var bell = link.querySelector('i.fa-bell');
        var isSidebar = !!link.querySelector('.nav-text');

        // Pulsing dot on the bell icon
        var dot = document.createElement('span');
        dot.setAttribute('data-notif-badge', '');
        if (isSidebar && bell) {
            dot.className = 'absolute -top-1 -right-1 flex h-2.5 w-2.5';
            dot.innerHTML = '<span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>' +
                            '<span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-red-500"></span>';
            bell.appendChild(dot);
        } else {
            dot.className = 'absolute top-0 right-0 flex h-4 min-w-[1rem]';
            dot.innerHTML = '<span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>' +
                            '<span class="relative inline-flex rounded-full h-4 min-w-[1rem] px-1 bg-red-500 text-white text-[10px] font-bold items-center justify-center">' + label(n) + '</span>';
            link.appendChild(dot);
        }

        // Count pill next to the "Notifications" text in the sidebar
        if (isSidebar) {
            var pill = document.createElement('span');
            pill.setAttribute('data-notif-badge', '');
            pill.className = 'nav-text ml-auto bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full';
            pill.textContent = label(n);
            link.appendChild(pill);
        }
    }

    function showToast(n) {
        // Inline styles so the toast also works on pages without Tailwind (e.g. student timetable)
        var t = document.createElement('a');
        t.href = '/notifications';
        t.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:9999;display:flex;align-items:center;gap:12px;' +
                          'background:#fff;border:1px solid #e5e7eb;box-shadow:0 10px 25px rgba(0,0,0,.15);border-radius:10px;' +
                          'padding:12px 16px;font:14px Inter,sans-serif;color:#1f2937;text-decoration:none;transition:opacity .5s;cursor:pointer;';
        t.innerHTML = '<i class="fa-solid fa-bell" style="color:#668054"></i><span>You have <b>' + label(n) +
                      '</b> unread notification' + (n === 1 ? '' : 's') + '. Click to view.</span>';
        t.addEventListener('click', function (e) {
            if (typeof window.openUniversalNotifModal === 'function') {
                e.preventDefault();
                window.openUniversalNotifModal();
                t.remove();
            } else if (typeof window.openStudentNotifModal === 'function') {
                e.preventDefault();
                window.openStudentNotifModal();
                t.remove();
            }
        });
        document.body.appendChild(t);
        setTimeout(function () { t.style.opacity = '0'; }, 6000);
        setTimeout(function () { t.remove(); }, 6600);
    }

    function render(n) {
        // Tailwind-styled bells (admin / proctor / secretary header)
        document.querySelectorAll('a[href="/notifications"]:not([data-notif-manual])').forEach(function (link) { renderLink(link, n); });

        // Plain-CSS bells manage their own badge: just set the number and show/hide it
        document.querySelectorAll('[data-notif-count]').forEach(function (el) {
            el.textContent = label(n);
            el.style.display = n > 0 ? '' : 'none';
        });

        var header = document.getElementById('header-unread-badge');   // notifications.html
        if (header) {
            header.textContent = label(n) + ' New';
            header.style.display = n > 0 ? '' : 'none';
        }

        document.title = (n > 0 ? '(' + label(n) + ') ' : '') + baseTitle;

        if (lastCount !== null && n > lastCount) showToast(n);
        lastCount = n;
    }
    window.__updateNotifBellCount = render;

    function isUserBusyInModalOrInput() {
        var active = document.activeElement;
        if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.tagName === 'SELECT')) {
            if (active.id !== 'searchInput' && active.id !== 'userSearchInput') {
                return true;
            }
        }
        var openModals = document.querySelectorAll(
            '#universalNotifModal:not(.hidden), #studentNotifModal:not(.hidden), #my-account-modal:not(.hidden), #change-password-modal:not(.hidden), [role="dialog"]:not(.hidden)'
        );
        for (var i = 0; i < openModals.length; i++) {
            var m = openModals[i];
            if (m.offsetParent !== null || window.getComputedStyle(m).display !== 'none') {
                return true;
            }
        }
        return false;
    }

    function triggerLivePageRefresh(reasonText) {
        if (window.__liveRefreshing) return;
        window.__liveRefreshing = true;
        var banner = document.createElement('div');
        banner.style.cssText = 'position:fixed;bottom:20px;left:50%;transform:translateX(-50%);z-index:99999;' +
                               'display:flex;align-items:center;gap:10px;background:#1f2937;color:#fff;' +
                               'padding:10px 18px;border-radius:999px;font:600 13px Inter,sans-serif;' +
                               'box-shadow:0 10px 25px rgba(0,0,0,.25);';
        banner.innerHTML = '<i class="fa-solid fa-arrows-rotate fa-spin" style="color:#86efac;"></i>' +
                           '<span>' + (reasonText || 'Syncing latest schedule & status updates...') + '</span>';
        document.body.appendChild(banner);
        setTimeout(function () {
            window.location.reload();
        }, 450);
    }

    function checkLiveSignature(sig) {
        if (!sig) return;
        if (lastSignature === null) {
            lastSignature = sig;
            return;
        }
        if (sig !== lastSignature) {
            var oldPub = (lastSignature.split('|')[0] || '');
            var newPub = (sig.split('|')[0] || '');
            var pubChanged = (oldPub !== newPub);
            lastSignature = sig;
            if (pubChanged) {
                pendingReload = 'Timetable publication status updated — refreshing...';
            } else if (!window.__disableLiveHardReload) {
                pendingReload = 'New proctor / collection update received — refreshing...';
            }
        }
        if (pendingReload && !isUserBusyInModalOrInput()) {
            var msg = pendingReload;
            pendingReload = false;
            triggerLivePageRefresh(msg);
        }
    }

    function schedule() {
        clearTimeout(timer);
        if (!stopped && document.visibilityState === 'visible') {
            timer = setTimeout(poll, interval);
        }
    }

    function poll() {
        if (stopped) return;
        fetch(ENDPOINT, { credentials: 'same-origin', cache: 'no-store', headers: { 'Accept': 'application/json' } })
            .then(function (r) {
                if (r.status === 401) { stopped = true; return null; }   // session expired: stop polling
                if (!r.ok) throw new Error('HTTP ' + r.status);
                return r.json();
            })
            .then(function (data) {
                if (data && typeof data.unread_count === 'number') {
                    interval = BASE_INTERVAL;
                    render(data.unread_count);
                    if (typeof data.live_signature === 'string') {
                        checkLiveSignature(data.live_signature);
                    }
                }
            })
            .catch(function () {
                interval = Math.min(interval * 2, MAX_INTERVAL);         // back off on errors
            })
            .then(schedule);
    }

    function start() {
        document.addEventListener('visibilitychange', function () {
            if (document.visibilityState === 'visible') poll();   // refresh right away when user returns
            else clearTimeout(timer);
        });
        setTimeout(poll, 600);   // capture baseline signature immediately after page load
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
    else start();
})();
