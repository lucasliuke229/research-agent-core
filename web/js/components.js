/* ═══════════════════════════════════════════════════════════════════════
   Components — all UI widgets
   Registered on RA.Components namespace
   ═══════════════════════════════════════════════════════════════════════ */
window.RA = window.RA || {};
window.RA.Components = (function() {
  'use strict';
  var A = null; // set by App after init

  /* ── AppHeader ────────────────────────────────────────────────────── */
  function AppHeader() {}
  AppHeader.prototype.init = function() {
    var self = this;
    document.getElementById('btn-new-task').addEventListener('click', function() {
      A.resetTask();
    });
    document.getElementById('btn-terminal-toggle').addEventListener('click', function() {
      A.toggleTerminal();
    });
  };

  /* ── TaskSidebar ──────────────────────────────────────────────────── */
  function TaskSidebar() {}
  TaskSidebar.prototype.init = function() {
    document.getElementById('sidebar-list').addEventListener('click', function(e) {
      var item = e.target.closest('.sidebar-item');
      if (!item) return;
      document.querySelectorAll('.sidebar-item').forEach(function(b){b.classList.remove('active')});
      item.classList.add('active');
      var idx = parseInt(item.dataset.idx||'0');
      A.loadHistoryTask(idx);
    });
  };
  TaskSidebar.prototype.render = function(history) {
    var list = document.getElementById('sidebar-list');
    if (!history || history.length===0) {
      list.innerHTML = '<div class="sidebar-empty">暂无历史任务</div>';
      return;
    }
    list.innerHTML = history.map(function(h,i) {
      var statusClass = h.status==='success'?'success':h.status==='failed'?'failed':'pending';
      return '<button class="sidebar-item'+(i===0?' active':'')+'" data-idx="'+i+'">'+
        escapeHtml(h.summary||'未命名任务')+
        '<span class="meta"><span class="status-pill '+statusClass+'">'+h.status+'</span> &middot; '+escapeHtml(h.elapsed||'')+'</span>'+
        '</button>';
    }).join('');
  };

  /* ── TaskComposer ─────────────────────────────────────────────────── */
  function TaskComposer() {}
  TaskComposer.prototype.init = function() {
    var self = this;

    // Run mode buttons
    document.getElementById('mode-full').addEventListener('click', function() {
      A.setRunMode('full');
    });
    document.getElementById('mode-custom').addEventListener('click', function() {
      A.setRunMode('custom');
    });
    document.getElementById('mode-single').addEventListener('click', function() {
      A.setRunMode('single');
    });

    // Module chips
    A.Adapter.moduleList().forEach(function(mod) {
      var el = document.getElementById('mod-chip-'+mod.id);
      if (!el) return;
      el.addEventListener('click', function() {
        A.toggleModule(mod.id);
      });
    });

    // Edit plan button
    var editBtn = document.getElementById('btn-edit-plan');
    if (editBtn) {
      editBtn.addEventListener('click', function() {
        var el = document.getElementById('exec-plan-steps');
        if (!el) return;
        var editing = el.classList.contains('editing');
        if (!editing) {
          el.classList.add('editing');
          editBtn.textContent = '保存计划';
          el.querySelectorAll('.exec-step').forEach(function(step) {
            step.classList.add('editable');
            step.querySelector('.exec-step-text').setAttribute('contenteditable','true');
          });
        } else {
          el.classList.remove('editing');
          editBtn.textContent = '编辑计划';
          el.querySelectorAll('.exec-step').forEach(function(step) {
            step.classList.remove('editable');
            step.querySelector('.exec-step-text').setAttribute('contenteditable','false');
          });
        }
      });
    }

    // Run button
    document.getElementById('btn-run').addEventListener('click', function() {
      A.runTask();
    });

    // Cmd+Enter to run
    document.getElementById('task-input').addEventListener('keydown', function(e) {
      if (e.key==='Enter' && (e.metaKey||e.ctrlKey)) {
        e.preventDefault();
        A.runTask();
      }
    });
  };
  TaskComposer.prototype.setRunning = function(running) {
    var btn = document.getElementById('btn-run');
    btn.disabled = running;
    btn.innerHTML = running ? '<span class="spinner"></span> 运行中...' : '开始运行';
  };
  TaskComposer.prototype.setRunMode = function(mode) {
    ['full','custom','single'].forEach(function(m) {
      var el = document.getElementById('mode-'+m);
      if (el) el.classList.toggle('selected', m===mode);
    });
    this._updateModuleChips(mode);
  };
  TaskComposer.prototype.toggleModule = function(modId) {
    var mode = A.state.runMode;
    if (mode==='full') return; // can't toggle in full mode
    var chip = document.getElementById('mod-chip-'+modId);
    var sel = chip.classList.contains('selected');
    if (mode==='single') {
      // Deselect all, select only this one
      if (sel) return;
      A.Adapter.moduleList().forEach(function(m) {
        var c = document.getElementById('mod-chip-'+m.id);
        if (c) c.classList.remove('selected');
      });
      chip.classList.add('selected');
    } else {
      chip.classList.toggle('selected');
    }
    A.onModulesChanged();
  };
  TaskComposer.prototype._updateModuleChips = function(mode) {
    var self = this;
    A.Adapter.moduleList().forEach(function(mod) {
      var chip = document.getElementById('mod-chip-'+mod.id);
      if (!chip) return;
      if (mode==='full') {
        chip.classList.add('selected');
      } else if (mode==='single') {
        chip.classList.remove('selected');
        if (mod.id==='literature') chip.classList.add('selected');
      }
      chip.classList.remove('disabled');
    });
  };
  TaskComposer.prototype.getSelectedModules = function() {
    var sel = [];
    A.Adapter.moduleList().forEach(function(mod) {
      var chip = document.getElementById('mod-chip-'+mod.id);
      if (chip && chip.classList.contains('selected')) sel.push(mod.id);
    });
    return sel;
  };

  /* ── ExecutionPlan ────────────────────────────────────────────────── */
  function ExecutionPlan() {}
  ExecutionPlan.prototype.render = function(steps) {
    var el = document.getElementById('exec-plan');
    var stepsEl = document.getElementById('exec-plan-steps');
    if (!el || !stepsEl) return;
    if (!steps || steps.length===0) { el.classList.remove('visible'); return; }
    el.classList.add('visible');
    stepsEl.classList.remove('editing');
    document.getElementById('btn-edit-plan').textContent = '编辑计划';
    stepsEl.innerHTML = steps.map(function(s,i) {
      return '<div class="exec-step">'+
        '<span class="exec-step-num">'+(i+1)+'</span>'+
        '<span class="exec-step-text">'+escapeHtml(s.text)+'</span>'+
        '</div>';
    }).join('');
  };

  /* ── PipelineProgress ─────────────────────────────────────────────── */
  function PipelineProgress() {}
  PipelineProgress.prototype.render = function(pipelineState) {
    var el = document.getElementById('pipeline-list');
    if (!el) return;
    el.innerHTML = '';
    el.classList.add('visible');

    pipelineState.forEach(function(p) {
      var row = document.createElement('div');
      row.className = 'pipeline-row' + (p.status==='running'?' running':'');
      var iconMap = {pending:'⋯',running:'●',success:'✓',failed:'✗',warning:'⚠',skipped:'—'};
      var icon = iconMap[p.status] || '?';
      var summary = '';
      if (p.status==='success') summary = p.summary||'完成';
      else if (p.status==='failed') summary = p.error||'执行失败';
      else if (p.status==='running') summary = '运行中...';
      else if (p.status==='skipped') summary = '未执行';
      else summary = '等待执行';

      row.innerHTML =
        '<span class="pipeline-status '+p.status+'">'+icon+'</span>'+
        '<span class="pipeline-name">'+escapeHtml(p.label)+'</span>'+
        '<span class="pipeline-summary">'+escapeHtml(summary)+'</span>'+
        '<span class="pipeline-time">'+escapeHtml(p.elapsed||'')+'</span>'+
        (p.status==='failed' ?
          '<span class="pipeline-actions"><button onclick="RA.App.retryModule(\''+p.id+'\')">重试</button></span>'
        : '');
      el.appendChild(row);
    });
  };

  /* ── ResultTabs ───────────────────────────────────────────────────── */
  function ResultTabs() {}
  ResultTabs.prototype.init = function() {
    var self = this;
    document.querySelectorAll('.tab-btn').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var tab = this.dataset.tab;
        self.switchTab(tab);
      });
    });
  };
  ResultTabs.prototype.switchTab = function(tabId) {
    document.querySelectorAll('.tab-btn').forEach(function(b){b.classList.toggle('active', b.dataset.tab===tabId)});
    document.querySelectorAll('.tab-panel').forEach(function(p){p.classList.toggle('active', p.id==='tab-'+tabId)});
  };
  ResultTabs.prototype.show = function() {
    var el = document.getElementById('result-tabs');
    if (el) el.classList.add('visible');
  };
  ResultTabs.prototype.hide = function() {
    var el = document.getElementById('result-tabs');
    if (el) el.classList.remove('visible');
  };
  ResultTabs.prototype.renderAll = function(result) {
    this.renderOverview(result);
    this.renderLiterature(result);
    this.renderReport(result);
    this.renderProcess(result);
    this.renderLogs(result);
    this.show();
    this.switchTab('overview');
  };
  ResultTabs.prototype.renderOverview = function(result) {
    var el = document.getElementById('tab-overview');
    if (!el) return;
    var summaryText = result.summary || '暂无摘要';
    var keywordsHtml = (result.keywords||[]).map(function(k){return '<span class="overview-keyword">'+escapeHtml(k)+'</span>'}).join('');
    el.innerHTML =
      '<p style="font-size:0.95rem;font-weight:500;margin-bottom:16px;white-space:pre-line;">'+escapeHtml(summaryText)+'</p>'+
      (keywordsHtml ? '<div style="margin-bottom:16px;">'+keywordsHtml+'</div>' : '')+
      (result.error ? '<div class="error-banner">'+escapeHtml(result.error)+'</div>' : '')+
      (result.hasWarnings ? '<div class="warning-banner">部分模块存在警告，请查看详情。</div>' : '')+
      '<div class="overview-grid">'+
        '<div class="overview-stat"><div class="overview-stat-label">完成模块</div><div class="overview-stat-value">'+result.successCount+' / '+result.totalCount+'</div></div>'+
        '<div class="overview-stat"><div class="overview-stat-label">总耗时</div><div class="overview-stat-value">'+escapeHtml(result.elapsed||'—')+'</div></div>'+
        '<div class="overview-stat"><div class="overview-stat-label">文献数量</div><div class="overview-stat-value">'+(result.literatureCount!==null ? result.literatureCount : '—')+'</div></div>'+
        '<div class="overview-stat"><div class="overview-stat-label">输出字数</div><div class="overview-stat-value">'+result.totalWords.toLocaleString()+'</div></div>'+
      '</div>';
  };
  ResultTabs.prototype.renderLiterature = function(result) {
    var el = document.getElementById('tab-literature');
    if (!el) return;
    var litResult = (result.results||[]).find(function(r){return r.module==='literature'});
    if (!litResult) { el.innerHTML='<div class="lit-placeholder">文献调研模块未运行，暂无数据。</div>'; return; }
    if (litResult.status==='failed') { el.innerHTML='<div class="error-banner">文献调研失败：'+escapeHtml(litResult.error||'')+'</div>'; return; }

    // Try to parse structured literature from AI response
    var report = (litResult.data && litResult.data.full_report) ? litResult.data.full_report : '';
    var papers = _parsePapersFromReport(report);

    if (papers.length===0) {
      el.innerHTML = '<div class="lit-placeholder">'+
        '<p style="margin-bottom:8px;font-weight:600;">AI 文献调研报告</p>'+
        '<p style="font-size:0.82rem;">报告中未检测到结构化文献条目。文献信息以自然语言形式嵌入在报告中，请查看「完整报告」标签页。</p>'+
        '<p style="font-size:0.75rem;color:var(--text-muted);margin-top:8px;">注意：当前为示例展示。真实的文献结构化提取将在后续版本中改进。</p>'+
        '</div>';
      return;
    }

    el.innerHTML = papers.map(function(p) {
      return '<div class="lit-card">'+
        '<h4>'+escapeHtml(p.title)+'</h4>'+
        '<div class="authors">'+escapeHtml(p.authors||'')+'</div>'+
        '<div class="venue">'+escapeHtml([p.year,p.venue].filter(Boolean).join(' · '))+'</div>'+
        (p.relevance ? '<div class="relevance">'+escapeHtml(p.relevance)+'</div>' : '')+
        (p.doi ? '<div class="doi">'+escapeHtml(p.doi)+'</div>' : '')+
        '</div>';
    }).join('');
  };
  ResultTabs.prototype.renderReport = function(result) {
    var el = document.getElementById('tab-report');
    if (!el) return;
    // Collect all full_reports and summaries
    var parts = [];
    (result.results||[]).forEach(function(r) {
      if (r.data && r.data.full_report) parts.push(r.data.full_report);
      else if (r.summary) parts.push('### '+escapeHtml(r.module)+'\n\n'+r.summary);
    });
    var markdown = parts.join('\n\n---\n\n') || '暂无报告内容。';
    el.innerHTML =
      '<div class="report-content" id="report-body">'+simpleMarkdown(markdown)+'</div>'+
      '<div class="report-actions">'+
        '<button class="btn-ghost" onclick="RA.App.copyReport()">复制报告</button>'+
        '<button class="btn-ghost" onclick="RA.App.downloadReport()">下载 txt</button>'+
        '<button class="btn-ghost" disabled title="PDF 导出功能尚未实现">导出 PDF</button>'+
      '</div>';
  };
  ResultTabs.prototype.renderProcess = function(result) {
    var el = document.getElementById('tab-process');
    if (!el) return;
    el.innerHTML = '<div class="process-timeline">'+
      (result.results||[]).map(function(r) {
        return '<div class="process-step">'+
          '<div class="process-step-header">'+escapeHtml(r.module)+' &middot; '+
            '<span class="status-pill '+r.status+'">'+r.status+'</span></div>'+
          '<div class="process-step-meta">开始：'+escapeHtml(r.startedAt||'—')+' &middot; 耗时：'+escapeHtml(r.elapsed||'—')+'</div>'+
          '<div style="font-size:0.8rem;margin-top:2px;">'+escapeHtml(r.summary||'')+'</div>'+
          (r.data && r.data.query_plan ? '<div style="font-size:0.75rem;color:var(--text-muted);margin-top:2px;">检索策略：'+escapeHtml(JSON.stringify(r.data.query_plan))+'</div>' : '')+
        '</div>';
      }).join('')+
      '</div>';
  };
  ResultTabs.prototype.renderLogs = function(result) {
    var el = document.getElementById('tab-logs');
    if (!el) return;
    var allLogs = result.logs || [];
    A.LogViewer.render(allLogs);
  };

  /* ── LogViewer ────────────────────────────────────────────────────── */
  function LogViewer() {}
  LogViewer.prototype.init = function() {
    var self = this;
    document.querySelectorAll('.log-filter').forEach(function(btn) {
      btn.addEventListener('click', function() {
        document.querySelectorAll('.log-filter').forEach(function(b){b.classList.remove('active')});
        this.classList.add('active');
        self._filterLogs(this.dataset.level||'all');
      });
    });
    document.getElementById('btn-copy-logs').addEventListener('click', function() {
      var text = document.getElementById('log-container').innerText;
      navigator.clipboard.writeText(text).then(function() {
        var btn = document.getElementById('btn-copy-logs');
        btn.textContent = '已复制!';
        setTimeout(function(){btn.textContent='复制日志'},1500);
      });
    });
  };
  LogViewer.prototype.render = function(logs, filter) {
    filter = filter || 'all';
    var el = document.getElementById('log-container');
    if (!el) return;
    el.innerHTML = logs.map(function(line) {
      var cls = ''; var level = 'info';
      if (line.toLowerCase().indexOf('error')!==-1 || line.toLowerCase().indexOf('fail')!==-1) { cls='error'; level='error'; }
      else if (line.toLowerCase().indexOf('warning')!==-1 || line.toLowerCase().indexOf('warn')!==-1) { cls='warning'; level='warning'; }
      var mod = _extractLogModule(line);
      var time = _extractLogTime(line);
      var msg = line.replace(/^\[.*?\]\s*/, '');
      return '<div class="log-entry '+cls+'" data-level="'+level+'">'+
        (time ? '<span class="log-time">'+escapeHtml(time)+'</span>' : '')+
        (mod ? '<span class="log-module">'+escapeHtml(mod)+'</span>' : '<span class="log-module">sys</span>')+
        '<span class="log-msg">'+escapeHtml(msg)+'</span>'+
        '</div>';
    }).join('');
  };
  LogViewer.prototype._filterLogs = function(level) {
    document.querySelectorAll('#log-container .log-entry').forEach(function(entry) {
      if (level==='all') { entry.style.display='flex'; return; }
      entry.style.display = entry.dataset.level===level ? 'flex' : 'none';
    });
  };

  /* ── RunInspector ─────────────────────────────────────────────────── */
  function RunInspector() {}
  RunInspector.prototype.render = function(result, modules, runMode) {
    var el = document.getElementById('inspector-content');
    if (!el) return;
    var st = result.status||'pending';
    var pillClass = st==='success'?'success':st==='failed'?'failed':st==='partial'?'partial':st==='running'?'running':'pending';
    el.innerHTML =
      '<div class="inspect-section">'+
        '<div class="inspect-label">运行状态</div>'+
        '<span class="status-pill '+pillClass+'">'+st+'</span>'+
      '</div>'+
      '<div class="inspect-section">'+
        '<div class="inspect-label">任务信息</div>'+
        '<div class="inspect-row"><span class="key">任务 ID</span><span class="val text-mono text-xs">'+escapeHtml(result.taskId||'—')+'</span></div>'+
        '<div class="inspect-row"><span class="key">开始时间</span><span class="val text-xs">'+escapeHtml((result.startedAt||'').slice(0,19)||'—')+'</span></div>'+
        '<div class="inspect-row"><span class="key">总耗时</span><span class="val">'+escapeHtml(result.elapsed||'—')+'</span></div>'+
        '<div class="inspect-row"><span class="key">运行模式</span><span class="val">'+(runMode==='full'?'完整流水线':runMode==='single'?'单模块':'自定义')+'</span></div>'+
        '<div class="inspect-row"><span class="key">当前模型</span><span class="val text-sm">'+escapeHtml(_getCurrentModel()||'—')+'</span></div>'+
        '<div class="inspect-row"><span class="key">选择模块</span><span class="val text-sm">'+escapeHtml((modules||[]).join(', ')||'—')+'</span></div>'+
      '</div>'+
      '<div class="inspect-section">'+
        '<div class="inspect-label">输出统计</div>'+
        '<div class="inspect-row"><span class="key">文献数量</span><span class="val">'+(result.literatureCount!==null?result.literatureCount:'—')+'</span></div>'+
        '<div class="inspect-row"><span class="key">输出字数</span><span class="val">'+result.totalWords.toLocaleString()+'</span></div>'+
        '<div class="inspect-row"><span class="key">存在警告</span><span class="val">'+(result.hasWarnings?'是':'否')+'</span></div>'+
      '</div>'+
      '<div class="inspect-section">'+
        '<div class="inspect-label">快捷操作</div>'+
        '<div class="inspect-actions">'+
          '<button class="inspect-action" onclick="RA.App.rerun()">⟳ 重新运行</button>'+
          '<button class="inspect-action" disabled title="尚未实现">📋 克隆任务</button>'+
          '<button class="inspect-action" disabled title="尚未实现">💾 保存为模板</button>'+
          '<button class="inspect-action" onclick="RA.App.downloadReport()">⬇ 导出报告</button>'+
          '<button class="inspect-action" onclick="RA.App.copyReport()">📄 复制结果</button>'+
        '</div>'+
      '</div>';
  };
  RunInspector.prototype.clear = function() {
    var el = document.getElementById('inspector-content');
    if (!el) return;
    el.innerHTML =
      '<div class="inspect-section"><div class="inspect-label">运行状态</div><span class="status-pill pending">就绪</span></div>'+
      '<div class="inspect-section"><div class="inspect-label">任务信息</div><p class="text-sm" style="color:var(--text-muted)">尚未运行任务</p></div>'+
      '<div class="inspect-section"><div class="inspect-label">快捷操作</div>'+
        '<div class="inspect-actions">'+
          '<button class="inspect-action" disabled title="尚未运行任务">⟳ 重新运行</button>'+
          '<button class="inspect-action" disabled title="尚未运行任务">📋 克隆任务</button>'+
        '</div></div>';
  };

  /* ── private helpers ─────────────────────────────────────────────── */

  function escapeHtml(str) {
    if (!str) return '';
    if (typeof str !== 'string') str = String(str);
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function simpleMarkdown(md) {
    if (!md) return '';
    var html = escapeHtml(md);
    // Very basic markdown: headings, bold, italic, lists
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    html = html.replace(/^\- (.+)$/gm, '<li>$1</li>');
    html = html.replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>');
    // Collapse consecutive <li>
    html = html.replace(/(<li>.*<\/li>\n?)+/g, function(m) { return '<ul>'+m+'</ul>'; });
    // Paragraphs: blank line separation
    html = html.replace(/\n\n/g, '</p><p>');
    html = '<p>'+html+'</p>';
    // Clean up empty paragraphs
    html = html.replace(/<p><\/p>/g, '');
    html = html.replace(/<p><h/g, '<h');
    html = html.replace(/<\/h([1-6])><\/p>/g, '</h$1>');
    html = html.replace(/<p><ul>/g, '<ul>');
    html = html.replace(/<\/ul><\/p>/g, '</ul>');
    return html;
  }

  function _parsePapersFromReport(report) {
    // Naive extraction: look for lines matching "title / author / year" patterns
    var papers = [];
    if (!report) return papers;
    var lines = report.split('\n');
    var current = null;
    for (var i=0; i<lines.length; i++) {
      var line = lines[i].trim();
      if (!line) continue;
      // Match patterns like "1. Title (Author, Year)" or "- Title, Author et al. (Year)"
      var match = line.match(/^[\d]+[\.\)]\s*(.+)/);
      if (match) {
        if (current) papers.push(current);
        current = { title: match[1].trim(), authors:'', year:'', venue:'', relevance:'', doi:'' };
        continue;
      }
      var match2 = line.match(/^[-•]\s*(.+)/);
      if (match2 && !current) {
        current = { title: match2[1].trim(), authors:'', year:'', venue:'', relevance:'', doi:'' };
        continue;
      }
      if (current) {
        var authorMatch = line.match(/^(?:作者|Author|by)[：:]\s*(.+)/i);
        if (authorMatch) { current.authors = authorMatch[1].trim(); continue; }
        var yearMatch = line.match(/^(?:年份|Year|发表)[：:]\s*(\d{4})/i);
        if (yearMatch) { current.year = yearMatch[1]; continue; }
        var doiMatch = line.match(/(10\.\d{4,}\/[\w\-\.]+)/);
        if (doiMatch) { current.doi = doiMatch[1]; continue; }
        var relMatch = line.match(/^(?:贡献|贡献|关系|Contribution)[：:]\s*(.+)/i);
        if (relMatch) { current.relevance = relMatch[1].trim(); continue; }
      }
    }
    if (current) papers.push(current);
    return papers;
  }

  function _getCurrentModel() {
    try {
      var c = JSON.parse(localStorage.getItem('ra-llm-config')||'{}');
      return c.model || '';
    } catch(e) { return ''; }
  }

  function _extractLogModule(line) {
    var match = line.match(/^\s*(\w+)\s*[：:]/);
    return match ? match[1] : '';
  }
  function _extractLogTime(line) {
    var match = line.match(/\[([^\]]+)\]/);
    return match ? match[1] : '';
  }

  /* ── SettingsPanel ──────────────────────────────────────────────────── */
  function SettingsPanel() {}
  SettingsPanel.prototype.init = function() {
    var self = this;
    document.getElementById('btn-settings-open').addEventListener('click', function() {
      self.open();
    });
    document.getElementById('btn-settings-close').addEventListener('click', function() {
      self.close();
    });
    document.getElementById('btn-settings-cancel').addEventListener('click', function() {
      self.close();
    });
    document.getElementById('btn-settings-save').addEventListener('click', function() {
      self.save();
    });
    // Close on overlay click
    document.getElementById('settings-modal').addEventListener('click', function(e) {
      if (e.target.id==='settings-modal') self.close();
    });
    // Escape to close
    document.addEventListener('keydown', function(e) {
      if (e.key==='Escape') {
        var m = document.getElementById('settings-modal');
        if (m.classList.contains('open')) self.close();
      }
    });

    // Fetch presets from backend
    this._loadPresets();
  };

  SettingsPanel.prototype._loadPresets = async function() {
    try {
      var resp = await fetch('/api/config');
      var info = await resp.json();
      this._config = info;
      this._renderPresets(info.presets||[]);
    } catch(e) {
      // Fallback: use built-in presets
      this._config = { model:'', base_url:'', has_api_key:false, presets:[] };
    }
  };

  SettingsPanel.prototype._renderPresets = function(presets) {
    var grid = document.getElementById('preset-grid');
    if (!grid) return;
    grid.innerHTML = presets.map(function(p) {
      return '<button class="preset-card" data-id="'+p.id+'">'+p.name+
        '<span class="preset-desc">'+escapeHtml(p.description||'')+'</span></button>';
    }).join('');

    var self = this;
    grid.addEventListener('click', function(e) {
      var card = e.target.closest('.preset-card');
      if (!card) return;
      grid.querySelectorAll('.preset-card').forEach(function(c){c.classList.remove('selected')});
      card.classList.add('selected');
      var id = card.dataset.id;
      var preset = (self._config.presets||[]).find(function(p){return p.id===id});
      if (preset) {
        document.getElementById('settings-base-url').value = preset.base_url||'';
        document.getElementById('settings-model').value = (preset.models||[])[0]||'';
      }
    });
  };

  SettingsPanel.prototype.open = function() {
    // Populate fields from localStorage or current config
    var saved = this._loadStored();
    if (saved.model) document.getElementById('settings-model').value = saved.model;
    if (saved.base_url) document.getElementById('settings-base-url').value = saved.base_url;
    if (saved.api_key) document.getElementById('settings-api-key').value = saved.api_key;

    document.getElementById('settings-modal').classList.add('open');
  };

  SettingsPanel.prototype.close = function() {
    document.getElementById('settings-modal').classList.remove('open');
  };

  SettingsPanel.prototype.save = function() {
    var cfg = {
      model:    document.getElementById('settings-model').value.trim(),
      base_url: document.getElementById('settings-base-url').value.trim(),
      api_key:  document.getElementById('settings-api-key').value.trim(),
    };
    localStorage.setItem('ra-llm-config', JSON.stringify(cfg));
    this.close();
  };

  SettingsPanel.prototype.getConfig = function() {
    return this._loadStored();
  };

  SettingsPanel.prototype._loadStored = function() {
    try {
      return JSON.parse(localStorage.getItem('ra-llm-config')||'{}');
    } catch(e) { return {}; }
  };

  function setApp(app) { A = app; }

  // Expose
  return {
    AppHeader:      AppHeader,
    TaskSidebar:    TaskSidebar,
    TaskComposer:   TaskComposer,
    ExecutionPlan:  ExecutionPlan,
    PipelineProgress:PipelineProgress,
    ResultTabs:     ResultTabs,
    LogViewer:      LogViewer,
    RunInspector:   RunInspector,
    SettingsPanel:  SettingsPanel,
    setApp:         setApp,
  };
})();
