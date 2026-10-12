(function () {
  'use strict';
  var KEY = 'tasknet_age_13_or_over';
  try {
    if (sessionStorage.getItem(KEY) === 'yes') return;
  } catch (e) { /* If storage is unavailable, ask on each page load. */ }

  function showGate() {
    if (document.getElementById('tasknet-age-gate')) return;
    var overlay = document.createElement('div');
    overlay.id = 'tasknet-age-gate';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-labelledby', 'tasknet-age-title');
    overlay.innerHTML = '<div class="age-card"><h2 id="tasknet-age-title">Before you continue</h2>' +
      '<p>Are you 13 years old or above?</p>' +
      '<div class="age-actions"><button type="button" class="age-yes">Yes, I’m 13 or above</button>' +
      '<button type="button" class="age-no">No, I’m under 13</button></div>' +
      '<div class="age-error" hidden>You have to be 13 or above to use this website.</div></div>';
    document.body.appendChild(overlay);
    document.documentElement.style.overflow = 'hidden';

    overlay.querySelector('.age-yes').addEventListener('click', function () {
      try { sessionStorage.setItem(KEY, 'yes'); } catch (e) {}
      overlay.remove();
      document.documentElement.style.overflow = '';
    });
    overlay.querySelector('.age-no').addEventListener('click', function () {
      overlay.querySelector('.age-error').hidden = false;
      overlay.querySelector('.age-actions').hidden = true;
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', showGate, { once: true });
  } else {
    showGate();
  }
})();
