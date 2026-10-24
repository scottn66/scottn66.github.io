// Plotly's modebar is a row of <a> icons with data-title and no text.
// Give each control a name, and expose the non-link buttons to the keyboard.
(function () {
  function label(root) {
    var buttons = (root || document).querySelectorAll('a.modebar-btn');
    for (var i = 0; i < buttons.length; i++) {
      var btn = buttons[i];
      var name = btn.getAttribute('data-title') || 'Chart control';
      if (!btn.getAttribute('aria-label')) btn.setAttribute('aria-label', name);
      var href = btn.getAttribute('href');
      if (href) {
        if (!btn.getAttribute('title')) btn.setAttribute('title', name);
        continue;
      }
      btn.setAttribute('role', 'button');
      if (!btn.hasAttribute('tabindex')) btn.setAttribute('tabindex', '0');
      if (btn._keybound) continue;
      btn._keybound = true;
      btn.addEventListener('keydown', function (event) {
        if (event.key !== ' ' && event.key !== 'Enter') return;
        event.preventDefault();
        event.currentTarget.click();
      });
    }
  }

  // Each chart's modebar logo is an inline SVG with <g id="symbol">.
  // Nothing references that id, and repeating it fails the duplicate-id check.
  function dropModebarIds(root) {
    var nodes = (root || document).querySelectorAll('.modebar [id]');
    for (var i = 0; i < nodes.length; i++) nodes[i].removeAttribute('id');
  }

  function bind() {
    label(document);
    dropModebarIds(document);
    var plots = document.querySelectorAll('.plotly-graph-div');
    for (var i = 0; i < plots.length; i++) {
      var gd = plots[i];
      if (typeof gd.on !== 'function' || gd._modebarBound) continue;
      gd._modebarBound = true;
      gd.on('plotly_afterplot', function () {
        label(document);
        dropModebarIds(document);
      });
    }
  }

  bind();
  window.addEventListener('load', bind);
})();
