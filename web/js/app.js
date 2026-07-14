/* ═══════════════════════════════════════════════════════════════════════
   App — main controller
   Holds global state, wires components together, handles API calls.
   ═══════════════════════════════════════════════════════════════════════ */
window.RA = window.RA || {};
window.RA.App = (function() {
  'use strict';

  // ── State ──────────────────────────────────────────────────────────
  var state = {
    runMode:      'full',          // 'full' | 'custom' | 'single'
    isRunning:    false,
    taskHistory:  [],              // [{ summary, status, elapsed, taskText, modules, result }]
    currentResult: null,           // RA.Adapter.fromResponse() result
    lastSelectedModules: [],       // module ids from last run
  };

  // ── Component instances ─────────────────────────────────────────────
  var composer  = new RA.Components.TaskComposer();
  var sidebar   = new RA.Components.TaskSidebar();
  var execPlan  = new RA.Components.ExecutionPlan();
  var pipeline  = new RA.Components.PipelineProgress();
  var tabs      = new RA.Components.ResultTabs();
  var logViewer = new RA.Components.LogViewer();
  var inspector = new RA.Components.RunInspector();
  var settings  = new RA.Components.SettingsPanel();
  var header    = new RA.Components.AppHeader();

  // Expose for onclick handlers
  var Adapter = RA.Adapter;
  var A = window.RA.App; // global ref for onclick="RA.App.xxx()"

  /* ── Init ─────────────────────────────────────────────────────────── */
  function init() {
    // Wire components to access App state and Adapter
    RA.Components.setApp(window.RA.App);
    RA.Components.Adapter = Adapter;

    header.init();
    composer.init();
    sidebar.init();
    tabs.init();
    logViewer.init();
    settings.init();
    inspector.clear();

    // Default: full pipeline, all modules selected
    composer.setRunMode('full');
    execPlan.render(Adapter.buildExecPlan('', Adapter.moduleList().map(function(m){return m.id})));
    renderSidebar();
  }

  /* ── Run Mode ─────────────────────────────────────────────────────── */
  function setRunMode(mode) {
    state.runMode = mode;
    composer.setRunMode(mode);
    onModulesChanged();
  }

  function toggleModule(modId) {
    composer.toggleModule(modId);
  }

  function onModulesChanged() {
    var modules = composer.getSelectedModules();
    state.lastSelectedModules = modules;
    var taskText = document.getElementById('task-input').value;
    execPlan.render(Adapter.buildExecPlan(taskText, modules));
    pipeline.render(Adapter.buildPipelineState(modules, null));
  }

  /* ── Run Task ─────────────────────────────────────────────────────── */
  async function runTask() {
    var taskText = document.getElementById('task-input').value.trim();
    if (!taskText) {
      document.getElementById('task-input').focus();
      return;
    }

    var modules = composer.getSelectedModules();
    if (modules.length===0) return;

    state.isRunning = true;
    composer.setRunning(true);

    // Determine task_type
    var taskType = state.runMode==='full' ? 'full' : modules[0];
    // For single mode, use the selected module id
    // For custom mode, we still only run one (backend limitation) — use first selected
    // Future: backend will support custom pipeline

    // Show pipeline with pending state
    pipeline.render(Adapter.buildPipelineState(modules, null));

    // Simulate running animation
    var simIdx = 0;
    var simInterval = setInterval(function() {
      if (simIdx < modules.length) {
        var stateList = Adapter.buildPipelineState(modules, null);
        for (var i=0; i<simIdx; i++) stateList[i].status = 'success';
        stateList[simIdx].status = 'running';
        pipeline.render(stateList);
        simIdx++;
      }
    }, 400);

    try {
      var response = await fetch('/api/run', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ task:taskText, task_type:taskType, llm_config:settings.getConfig() }),
      });
      clearInterval(simInterval);

      if (!response.ok) throw new Error('服务器返回错误 '+response.status);

      var raw = await response.json();
      var result = Adapter.fromResponse(raw);
      state.currentResult = result;

      // Update pipeline
      pipeline.render(Adapter.buildPipelineState(modules, result.results));

      // Update results
      tabs.renderAll(result);

      // Update inspector
      inspector.render(result, modules, state.runMode);

      // Add to history
      state.taskHistory.unshift({
        summary:    result.summary||taskText.slice(0,60),
        status:     result.status,
        elapsed:    result.elapsed,
        taskText:   taskText,
        modules:    modules.slice(),
        result:     result,
        timestamp:  new Date().toISOString(),
      });
      renderSidebar();

    } catch(err) {
      clearInterval(simInterval);

      // Show failed pipeline
      var failedState = Adapter.buildPipelineState(modules, []);
      failedState.forEach(function(p){ p.status='failed'; p.error=err.message; });
      pipeline.render(failedState);

      var errResult = Adapter.emptyResult();
      errResult.status = 'failed';
      errResult.error = err.message;
      errResult.startedAt = new Date().toISOString();
      state.currentResult = errResult;
      tabs.renderAll(errResult);
      inspector.render(errResult, modules, state.runMode);

      state.taskHistory.unshift({
        summary:    taskText.slice(0,60),
        status:     'failed',
        elapsed:    '',
        taskText:   taskText,
        modules:    modules.slice(),
        result:     errResult,
        timestamp:  new Date().toISOString(),
      });
      renderSidebar();

    } finally {
      state.isRunning = false;
      composer.setRunning(false);
    }
  }

  /* ── History ──────────────────────────────────────────────────────── */
  function renderSidebar() {
    sidebar.render(state.taskHistory);
  }

  function loadHistoryTask(idx) {
    var h = state.taskHistory[idx];
    if (!h) return;
    document.getElementById('task-input').value = h.taskText||'';
    if (h.result) {
      state.currentResult = h.result;
      var modules = h.modules||[];
      pipeline.render(Adapter.buildPipelineState(modules, h.result.results));
      tabs.renderAll(h.result);
      inspector.render(h.result, modules, state.runMode);
    }
  }

  function resetTask() {
    document.getElementById('task-input').value = '';
    state.currentResult = null;
    var modules = composer.getSelectedModules();
    execPlan.render(Adapter.buildExecPlan('', modules));
    pipeline.render(Adapter.buildPipelineState(modules, null));
    tabs.hide();
    inspector.clear();
    document.getElementById('task-input').focus();
  }

  /* ── Actions ──────────────────────────────────────────────────────── */
  function rerun() { runTask(); }
  function retryModule(modId) { runTask(); } // Simple: rerun entire task for now
  function copyReport() {
    var el = document.getElementById('report-body');
    var text = el ? el.innerText : '';
    navigator.clipboard.writeText(text).then(function(){});
  }
  function downloadReport() {
    var el = document.getElementById('report-body');
    var text = el ? el.innerText : (state.currentResult ? state.currentResult.summary : '');
    var blob = new Blob([text], {type:'text/plain;charset=utf-8'});
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url; a.download = 'research-report.txt';
    a.click();
    URL.revokeObjectURL(url);
  }

  /* ── Terminal ─────────────────────────────────────────────────────── */
  function toggleTerminal() {
    var panel = document.getElementById('terminal-panel');
    var isOpen = panel.classList.contains('open');
    if (isOpen) {
      closeTerminal();
      panel.classList.remove('open');
      document.body.classList.remove('has-terminal');
      document.getElementById('btn-terminal-toggle').classList.remove('active');
    } else {
      panel.classList.add('open');
      document.body.classList.add('has-terminal');
      document.getElementById('btn-terminal-toggle').classList.add('active');
      openTerminal();
      setTimeout(function(){ panel.scrollIntoView({behavior:'smooth'}); }, 100);
    }
  }

  var term=null, termWs=null, termFit=null;
  function openTerminal() {
    if (term) return;
    term = new Terminal({
      fontSize:13,
      fontFamily:'"SF Mono","Fira Code","Cascadia Code","Menlo",monospace',
      theme:{background:'#1a1b26',foreground:'#c0caf5',cursor:'#c0caf5',selectionBackground:'#33467C'},
      cursorBlink:true,cursorStyle:'bar',allowProposedApi:true,
    });
    if (typeof XtermAddonFit!=='undefined') {
      termFit = new XtermAddonFit.FitAddon();
      term.loadAddon(termFit);
    }
    term.open(document.getElementById('terminal-body'));
    if (termFit) termFit.fit();

    var proto = location.protocol==='https:'?'wss:':'ws:';
    termWs = new WebSocket(proto+'//'+location.host+'/ws/terminal');
    termWs.binaryType = 'arraybuffer';
    termWs.onopen = function() {
      term.writeln('\x1b[32m已连接到终端。可在此运行 bash 命令，包括 claude。\x1b[0m\n');
    };
    termWs.onmessage = function(event) {
      if (event.data instanceof ArrayBuffer) term.write(new Uint8Array(event.data));
    };
    termWs.onclose = function() { term.writeln('\r\n\x1b[33m终端连接已关闭。\x1b[0m'); };
    term.onData(function(data) {
      if (termWs && termWs.readyState===WebSocket.OPEN) termWs.send(data);
    });
    term.onResize(function(_a) {
      if (termWs && termWs.readyState===WebSocket.OPEN)
        termWs.send(JSON.stringify({type:'resize',cols:_a.cols,rows:_a.rows}));
    });
    window.addEventListener('resize', onTermResize);
  }
  function onTermResize() { if (termFit) termFit.fit(); }
  function closeTerminal() {
    if (termWs) { termWs.close(); termWs=null; }
    if (term) { term.dispose(); term=null; }
    termFit=null;
    window.removeEventListener('resize', onTermResize);
  }

  // Keyboard shortcut: Ctrl+` to toggle terminal
  document.addEventListener('keydown', function(e) {
    if (e.key==='`' && (e.ctrlKey||e.metaKey)) { e.preventDefault(); toggleTerminal(); }
  });

  /* ── Public API ───────────────────────────────────────────────────── */
  return {
    init:              init,
    runTask:           runTask,
    setRunMode:        setRunMode,
    toggleModule:      toggleModule,
    onModulesChanged:  onModulesChanged,
    loadHistoryTask:   loadHistoryTask,
    resetTask:         resetTask,
    rerun:             rerun,
    retryModule:       retryModule,
    copyReport:        copyReport,
    downloadReport:    downloadReport,
    toggleTerminal:    toggleTerminal,
    get state() { return state; },
    get Adapter() { return Adapter; },
    get composer() { return composer; },
    get sidebar() { return sidebar; },
    get execPlan() { return execPlan; },
    get pipeline() { return pipeline; },
    get tabs() { return tabs; },
    get LogViewer() { return logViewer; },
    get inspector() { return inspector; },
  };
})();

// Boot on DOM ready
document.addEventListener('DOMContentLoaded', function() {
  window.RA.App.init();
});
