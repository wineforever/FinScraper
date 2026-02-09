const state = {
  reports: [],
  stockId: "",
  stockName: "",
  reportTypeLabel: "",
  year: "",
};

const form = document.getElementById("searchForm");
const queryInput = document.getElementById("query");
const reportTypeSelect = document.getElementById("reportType");
const yearSelect = document.getElementById("year");
const statusEl = document.getElementById("status");
const summaryEl = document.getElementById("summary");
const resultsBody = document.getElementById("resultsBody");
const checkAll = document.getElementById("checkAll");
const downloadSelectedBtn = document.getElementById("downloadSelected");
const loadingEl = document.getElementById("loading");
const emptyEl = document.getElementById("emptyState");

const currentYear = new Date().getFullYear();
for (let y = currentYear; y >= 2000; y -= 1) {
  const option = document.createElement("option");
  option.value = String(y);
  option.textContent = `${y}年`;
  yearSelect.appendChild(option);
}
yearSelect.value = "";

function setStatus(message, tone = "info") {
  statusEl.textContent = message;
  statusEl.dataset.tone = tone;
}

function setLoading(isLoading) {
  loadingEl.classList.toggle("hidden", !isLoading);
}

function setEmpty(isEmpty) {
  emptyEl.classList.toggle("hidden", !isEmpty);
}

function buildDownloadUrl(report) {
  const params = new URLSearchParams({
    stock_id: state.stockId,
    bulletin_id: report.id,
    title: report.title,
  });
  return `/api/report/pdf?${params.toString()}`;
}

function triggerDownload(url) {
  const link = document.createElement("a");
  link.href = url;
  link.download = "";
  link.target = "_self";
  link.rel = "noopener";
  link.style.display = "none";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function updateSummary() {
  if (!state.reports.length) {
    summaryEl.textContent = "请先查询报告。";
    return;
  }
  const yearLabel = state.year ? `${state.year}年` : "全部年份";
  summaryEl.textContent = `${state.stockName} (${state.stockId}) · ${state.reportTypeLabel} · ${yearLabel} · 共 ${state.reports.length} 条`;
}

function renderResults() {
  resultsBody.innerHTML = "";
  checkAll.checked = false;
  downloadSelectedBtn.disabled = true;

  if (!state.reports.length) {
    setEmpty(true);
    updateSummary();
    return;
  }

  setEmpty(false);
  state.reports.forEach((report) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td class="col-check">
        <input type="checkbox" class="row-check" data-id="${report.id}" checked>
      </td>
      <td class="col-date">${report.date}</td>
      <td>${report.title}</td>
      <td class="col-action">
        <button class="action-btn" data-id="${report.id}">下载</button>
      </td>
    `;
    resultsBody.appendChild(row);
  });

  if (state.reports.length) {
    const checks = resultsBody.querySelectorAll(".row-check");
    checks.forEach((checkbox) => {
      checkbox.checked = true;
    });
    checkAll.checked = true;
    downloadSelectedBtn.disabled = false;
  }

  updateSummary();
}

function getSelectedReports() {
  const selectedIds = Array.from(
    resultsBody.querySelectorAll(".row-check:checked")
  ).map((input) => input.dataset.id);
  return state.reports.filter((report) => selectedIds.includes(report.id));
}

async function downloadSelected() {
  const selected = getSelectedReports();
  if (!selected.length) {
    setStatus("请先勾选要下载的报告。", "warn");
    return;
  }

  downloadSelectedBtn.disabled = true;
  for (let i = 0; i < selected.length; i += 1) {
    const report = selected[i];
    setStatus(`正在下载 ${i + 1}/${selected.length}：${report.title}`);
    triggerDownload(buildDownloadUrl(report));
    await new Promise((resolve) => setTimeout(resolve, 400));
  }
  setStatus("批量下载已触发，请留意浏览器下载提示。");
  downloadSelectedBtn.disabled = false;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = queryInput.value.trim();
  const reportType = reportTypeSelect.value;
  const year = yearSelect.value;

  if (!query) {
    setStatus("请输入股票代码或名称。", "warn");
    return;
  }

  setLoading(true);
  setEmpty(false);
  setStatus("正在抓取报告列表...");
  resultsBody.innerHTML = "";

  try {
    const params = new URLSearchParams({
      query,
      report_type: reportType,
    });
    if (year) {
      params.set("year", year);
    }
    const response = await fetch(`/api/reports?${params.toString()}`);
    if (!response.ok) {
      const detail = await response.json().catch(() => ({}));
      throw new Error(detail.detail || "抓取失败");
    }
    const data = await response.json();
    state.reports = data.reports || [];
    state.stockId = data.stock_id;
    state.stockName = data.stock_name;
    state.reportTypeLabel = data.report_type_label || reportType;
    state.year = year;

    renderResults();
    setStatus(`已抓取 ${state.reports.length} 条报告。`);
  } catch (error) {
    setStatus(error.message || "抓取失败", "error");
    state.reports = [];
    renderResults();
  } finally {
    setLoading(false);
  }
});

resultsBody.addEventListener("click", (event) => {
  const target = event.target;
  if (target.matches(".action-btn")) {
    const report = state.reports.find((item) => item.id === target.dataset.id);
    if (report) {
      setStatus(`正在下载：${report.title}`);
      triggerDownload(buildDownloadUrl(report));
    }
  }
});

resultsBody.addEventListener("change", (event) => {
  if (!event.target.matches(".row-check")) {
    return;
  }
  const selected = getSelectedReports();
  downloadSelectedBtn.disabled = selected.length === 0;
  checkAll.checked =
    selected.length > 0 && selected.length === state.reports.length;
});

checkAll.addEventListener("change", () => {
  const checks = resultsBody.querySelectorAll(".row-check");
  checks.forEach((checkbox) => {
    checkbox.checked = checkAll.checked;
  });
  const selected = getSelectedReports();
  downloadSelectedBtn.disabled = selected.length === 0;
});

downloadSelectedBtn.addEventListener("click", downloadSelected);
