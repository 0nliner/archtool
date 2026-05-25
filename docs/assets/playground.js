(function () {
  var outputs = {
    basic: [
      { t: 'cmd',     s: '$ python entrypoints/run.py' },
      { t: 'blank',   s: '' },
      { t: 'info',    s: '  archtool  scanning app.users' },
      { t: 'blank',   s: '' },
      { t: 'ok',      s: '  ✓  UserRepo      →  UserRepoABC' },
      { t: 'ok',      s: '  ✓  UserService   →  UserServiceABC' },
      { t: 'wire',    s: '     UserService.repo  ←  UserRepo' },
      { t: 'blank',   s: '' },
      { t: 'result',  s: '{"id": 1, "name": "Alice"}' },
    ],
    multi: [
      { t: 'cmd',     s: '$ python entrypoints/run.py' },
      { t: 'blank',   s: '' },
      { t: 'info',    s: '  archtool  scanning 2 modules' },
      { t: 'blank',   s: '' },
      { t: 'mod',     s: '  app.users' },
      { t: 'ok',      s: '  ✓  UserRepo      →  UserRepoABC' },
      { t: 'ok',      s: '  ✓  UserService   →  UserServiceABC' },
      { t: 'blank',   s: '' },
      { t: 'mod',     s: '  app.orders' },
      { t: 'ok',      s: '  ✓  OrderRepo     →  OrderRepoABC' },
      { t: 'ok',      s: '  ✓  OrderService  →  OrderServiceABC' },
      { t: 'wire',    s: '     OrderService.user_svc  ←  UserService  (cross-module)' },
      { t: 'blank',   s: '' },
      { t: 'result',  s: '{"user": {"id": 1, "name": "Alice"}, "status": "placed"}' },
    ],
    layer: [
      { t: 'cmd',     s: '$ python entrypoints/run.py' },
      { t: 'blank',   s: '' },
      { t: 'info',    s: '  archtool  scanning app.fraud' },
      { t: 'blank',   s: '' },
      { t: 'err',     s: 'TopLevelLayerUsingException' },
      { t: 'blank',   s: '' },
      { t: 'errtxt',  s: '  Layer boundary violation at startup.' },
      { t: 'blank',   s: '' },
      { t: 'errtxt',  s: "  'FraudService'  lives in  DomainLayer" },
      { t: 'errtxt',  s: "  depends on  'FraudControllerABC'  →  ApplicationLayer" },
      { t: 'blank',   s: '' },
      { t: 'errtxt',  s: '  DomainLayer cannot depend on ApplicationLayer.' },
      { t: 'errtxt',  s: '  Dependencies must flow downward only.' },
    ],
  };

  var delays = { blank: 50, cmd: 80, info: 100, mod: 100, ok: 90, wire: 90, result: 110, err: 80, errtxt: 80 };

  function init() {
    var tabs    = document.querySelectorAll('.pg-tab');
    var panes   = document.querySelectorAll('.pg-pane');
    var runBtn  = document.getElementById('pg-run');
    var output  = document.getElementById('pg-output');
    if (!runBtn || !output) return;

    var activeTab = 'basic';
    var timer = null;

    function resetOutput() {
      output.innerHTML = '<div class="pg-hint">Click ▶ Run to execute</div>';
      runBtn.disabled = false;
      runBtn.textContent = '▶ Run';
    }

    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        clearTimeout(timer);
        tabs.forEach(function (t) { t.classList.remove('pg-tab--active'); });
        panes.forEach(function (p) { p.classList.remove('pg-pane--active'); });
        tab.classList.add('pg-tab--active');
        activeTab = tab.dataset.tab;
        var pane = document.getElementById('pg-pane-' + activeTab);
        if (pane) pane.classList.add('pg-pane--active');
        resetOutput();
      });
    });

    runBtn.addEventListener('click', function () {
      clearTimeout(timer);
      output.innerHTML = '';
      runBtn.disabled = true;
      runBtn.textContent = '● Running';

      var lines = outputs[activeTab];
      var i = 0;

      function next() {
        if (i >= lines.length) {
          runBtn.disabled = false;
          runBtn.textContent = '▶ Run';
          return;
        }
        var line = lines[i++];
        var el = document.createElement('div');
        el.className = 'pg-line pg-line--' + line.t;
        el.textContent = line.s || ' ';
        output.appendChild(el);
        output.scrollTop = output.scrollHeight;
        timer = setTimeout(next, delays[line.t] || 80);
      }

      next();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
