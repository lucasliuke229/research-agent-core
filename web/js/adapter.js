/* ═══════════════════════════════════════════════════════════════════════
   Adapter — data transformer
   Converts raw API responses into UI-friendly structured objects.

   All components read from these adapted shapes;
   no component directly parses the raw backend response.
   ═══════════════════════════════════════════════════════════════════════ */

window.RA = window.RA || {};
window.RA.Adapter = (function() {
  'use strict';

  // Module metadata — names and display labels
  var MODULES = [
    { id:'literature',  label:'文献调研', icon:'📚' },
    { id:'theory',      label:'理论分析', icon:'🧪' },
    { id:'computation', label:'数值计算', icon:'💻' },
    { id:'experiment',  label:'实验设计', icon:'🔬' },
    { id:'report',      label:'报告汇总', icon:'📄' },
  ];

  /**
   * Parse raw API response into UI-ready task result object.
   */
  function fromResponse(raw) {
    if (!raw) return emptyResult();

    var results = (raw.results || []).map(function(r) {
      return fromModuleResult(r);
    });

    var status = raw.status || 'pending';

    return {
      taskId:      raw.task_id || '',
      taskType:    raw.task_type || '',
      status:      status,
      summary:     raw.summary || '',
      files:       raw.files || [],
      logs:        raw.logs || [],
      error:       raw.error || null,
      results:     results,
      startedAt:   raw.started_at || '',
      finishedAt:  raw.finished_at || '',
      elapsed:     _calcElapsed(raw.started_at, raw.finished_at),
      // Derived
      successCount: results.filter(function(r){return r.status==='success'}).length,
      totalCount:   results.length,
      hasErrors:    !!raw.error || results.some(function(r){return r.status==='failed'}),
      hasWarnings:  results.some(function(r){return r.status==='warning'}),
      keywords:     _extractKeywords(results),
      literatureCount: _countLiterature(results),
      totalWords:   _countWords(results),
    };
  }

  function fromModuleResult(r) {
    return {
      module:     r.module || '',
      status:     r.status || 'pending',
      summary:    r.summary || '',
      data:       r.data || {},
      files:      r.files || [],
      logs:       r.logs || [],
      error:      r.error || null,
      startedAt:  r.started_at || '',
      finishedAt: r.finished_at || '',
      elapsed:    _calcElapsed(r.started_at, r.finished_at),
    };
  }

  function emptyResult() {
    return {
      taskId:'', taskType:'', status:'pending', summary:'',
      files:[], logs:[], error:null, results:[], startedAt:'', finishedAt:'',
      elapsed:'', successCount:0, totalCount:0, hasErrors:false, hasWarnings:false,
      keywords:[], literatureCount:0, totalWords:0,
    };
  }

  /**
   * Build execution plan from selected modules and task text.
   */
  function buildExecPlan(taskText, selectedModules) {
    var plans = {
      literature:  ['确定核心检索关键词与数据库', '检索并筛选相关文献', '按研究方向聚类', '提取代表性工作与贡献', '生成文献调研报告'],
      theory:      ['梳理领域核心理论框架', '识别关键公式与推导', '分析不同理论的适用范围与矛盾'],
      computation: ['建立数学模型', '设计数值求解策略', '评估计算复杂度与误差'],
      experiment:  ['明确研究假设与变量', '设计实验方案与对照组', '确定样本量与统计方法'],
      report:      ['汇总各模块结果', '整合关键发现与结论', '生成结构化研究报告'],
    };
    var steps = [];
    (selectedModules||[]).forEach(function(modId, idx) {
      var modPlan = plans[modId] || ['执行 ' + modId];
      modPlan.forEach(function(step) {
        steps.push({ module:modId, text:step });
      });
    });
    return steps;
  }

  /**
   * Build pipeline state from selected modules and optional results.
   */
  function buildPipelineState(selectedModules, results) {
    var resultMap = {};
    (results||[]).forEach(function(r) { resultMap[r.module] = r; });

    return MODULES.map(function(mod) {
      var wasSelected = (selectedModules||[]).indexOf(mod.id) !== -1;
      var res = resultMap[mod.id];
      if (res) {
        return { id:mod.id, label:mod.label, selected:true, status:res.status, summary:res.summary, error:res.error, elapsed:res.elapsed || '' };
      }
      if (wasSelected) {
        return { id:mod.id, label:mod.label, selected:true, status:'pending', summary:'', error:null, elapsed:'' };
      }
      return { id:mod.id, label:mod.label, selected:false, status:'skipped', summary:'', error:null, elapsed:'' };
    });
  }

  function moduleList() { return MODULES; }

  /* ── private helpers ─────────────────────────────────────────────── */

  function _calcElapsed(started, finished) {
    if (!started || !finished) return '';
    var start = new Date(started).getTime();
    var end   = new Date(finished).getTime();
    var diff  = (end - start) / 1000;
    if (diff < 60) return Math.round(diff) + ' 秒';
    if (diff < 3600) return Math.round(diff/60) + ' 分 ' + Math.round(diff%60) + ' 秒';
    return Math.floor(diff/3600) + ' 时 ' + Math.round((diff%3600)/60) + ' 分';
  }

  function _extractKeywords(results) {
    var kw = [];
    results.forEach(function(r) {
      if (r.data && r.data.keywords) {
        kw = kw.concat(r.data.keywords);
      }
    });
    return kw.slice(0, 20);
  }

  function _countLiterature(results) {
    var lit = results.find(function(r) { return r.module==='literature'; });
    if (lit && lit.data && lit.data.literature_count) return lit.data.literature_count;
    return null;
  }

  function _countWords(results) {
    var total = 0;
    results.forEach(function(r) {
      if (r.summary) total += r.summary.length;
      if (r.data && r.data.full_report) total += r.data.full_report.length;
    });
    return total;
  }

  return {
    MODULES:         MODULES,
    fromResponse:    fromResponse,
    fromModuleResult:fromModuleResult,
    buildExecPlan:   buildExecPlan,
    buildPipelineState: buildPipelineState,
    moduleList:      moduleList,
  };
})();
