from __future__ import annotations

import html
import re
from typing import Dict, List, Optional
from urllib.parse import quote

import requests
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

LIST_BASE_URL = "https://money.finance.sina.com.cn"
DETAIL_BASE_URL = "https://vip.stock.finance.sina.com.cn"
SUGGEST_URL = "https://suggest3.sinajs.cn/suggest"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

REPORT_TYPE_MAP: Dict[str, str] = {
    "ndbg": "ndbg",
    "yjdbg": "yjdbg",
    "zqbg": "zqbg",
    "sjdbg": "sjdbg",
    "annual": "ndbg",
    "q1": "yjdbg",
    "half": "zqbg",
    "q3": "sjdbg",
    "年报": "ndbg",
    "一季报": "yjdbg",
    "中报": "zqbg",
    "半年报": "zqbg",
    "三季报": "sjdbg",
    "all": "all",
    "全部": "all",
    "全部类型": "all",
}

REPORT_TYPE_LABEL: Dict[str, str] = {
    "ndbg": "年报",
    "yjdbg": "一季报",
    "zqbg": "中报",
    "sjdbg": "三季报",
    "all": "全部类型",
}

REPORT_LIST_ROUTE: Dict[str, Dict[str, str]] = {
    "ndbg": {"path": "vCB_Bulletin", "page_type": "ndbg"},
    "yjdbg": {"path": "vCB_BulletinYi", "page_type": "yjdbg"},
    "zqbg": {"path": "vCB_BulletinZhong", "page_type": "zqbg"},
    "sjdbg": {"path": "vCB_BulletinSan", "page_type": "sjdbg"},
}

PDF_URL_CACHE: Dict[str, str] = {}

app = FastAPI(title="FinScraper")


def resolve_report_type(report_type: str) -> str:
    key = (report_type or "").strip()
    if not key:
        raise HTTPException(status_code=400, detail="报告类型不能为空")
    key_lower = key.lower()
    if key_lower in REPORT_TYPE_MAP:
        return REPORT_TYPE_MAP[key_lower]
    if key in REPORT_TYPE_MAP:
        return REPORT_TYPE_MAP[key]
    raise HTTPException(status_code=400, detail="不支持的报告类型")


def parse_suggest(text: str) -> List[List[str]]:
    match = re.search(r'var\s+suggestvalue\s*=\s*"(.*?)"', text)
    if not match:
        return []
    payload = match.group(1).strip()
    if not payload:
        return []
    entries = []
    for raw in payload.split(";"):
        if not raw:
            continue
        fields = raw.split(",")
        if fields:
            entries.append(fields)
    return entries


def resolve_stock(query: str) -> Dict[str, str]:
    query = (query or "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="请输入股票代码或名称")

    url = f"{SUGGEST_URL}/type=11,12,13,14,15&key={quote(query)}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.encoding = "gbk"
    entries = parse_suggest(resp.text)

    if not entries:
        if re.fullmatch(r"\d{6}", query):
            return {"stock_id": query, "stock_name": query}
        raise HTTPException(status_code=404, detail="未找到匹配的股票")

    for fields in entries:
        if len(fields) >= 4 and re.fullmatch(r"\d{6}", fields[2]):
            name = ""
            if len(fields) > 4 and fields[4].strip():
                name = fields[4].strip()
            elif len(fields) > 6 and fields[6].strip():
                name = fields[6].strip()
            return {
                "stock_id": fields[2],
                "stock_name": name or fields[0] or fields[2],
                "symbol": fields[3],
            }

    raise HTTPException(status_code=404, detail="未找到匹配的股票")


def extract_report_year(title: str, date_text: str) -> str:
    match = re.search(r"((?:19|20)\d{2})年", title)
    if not match:
        match = re.search(r"(?:19|20)\d{2}", title)
    if match:
        return match.group(1)
    return date_text[:4] if date_text else ""


def fetch_report_list(stock_id: str, report_type: str) -> List[Dict[str, str]]:
    route = REPORT_LIST_ROUTE.get(report_type)
    if not route:
        return []
    url = (
        f"{LIST_BASE_URL}/corp/go.php/{route['path']}/stockid/{stock_id}/"
        f"page_type/{route['page_type']}.phtml"
    )
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.encoding = "gb18030"
    page_html = resp.text

    match = re.search(r'<div class="datelist">(.*?)</div>', page_html, re.S)
    if not match:
        return []

    fragment = match.group(1)
    pattern = re.compile(
        r'(\d{4}-\d{2}-\d{2})&nbsp;\s*'
        r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>',
        re.S,
    )
    items: List[Dict[str, str]] = []
    for date_text, href, title in pattern.findall(fragment):
        detail_url = html.unescape(href)
        if detail_url.startswith("/"):
            detail_url = f"{DETAIL_BASE_URL}{detail_url}"
        id_match = re.search(r"(?:[?&]id=)(\d+)", detail_url)
        bulletin_id = id_match.group(1) if id_match else ""
        items.append(
            {
                "id": bulletin_id,
                "title": title.strip(),
                "date": date_text,
                "detail_url": detail_url,
                "report_year": extract_report_year(title, date_text),
            }
        )

    return items


def fetch_report_list_all(stock_id: str) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    for report_type in REPORT_LIST_ROUTE:
        items.extend(fetch_report_list(stock_id, report_type))

    seen = set()
    deduped: List[Dict[str, str]] = []
    for item in items:
        key = item["id"] or item["detail_url"]
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    deduped.sort(key=lambda x: x["date"], reverse=True)
    return deduped


def extract_download_link(html: str) -> str:
    anchor_pattern = re.compile(
        r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]{0,30})</a>',
        re.I,
    )
    for href, text in anchor_pattern.findall(html):
        if "下载" in text or "PDF" in text:
            if ".pdf" in href.lower() or "download" in href.lower():
                return href

    match = re.search(r'href=["\']([^"\']+\\.pdf)["\']', html, re.I)
    if match:
        return match.group(1)
    return ""


def fetch_pdf_url(stock_id: str, bulletin_id: str) -> str:
    cache_key = f"{stock_id}:{bulletin_id}"
    if cache_key in PDF_URL_CACHE:
        return PDF_URL_CACHE[cache_key]

    detail_url = (
        f"{DETAIL_BASE_URL}/corp/view/vCB_AllBulletinDetail.php?"
        f"stockid={stock_id}&id={bulletin_id}"
    )
    resp = requests.get(detail_url, headers=HEADERS, timeout=20)
    resp.encoding = "gb18030"
    pdf_url = extract_download_link(resp.text)
    if not pdf_url:
        raise HTTPException(status_code=404, detail="未找到PDF链接")

    pdf_url = html.unescape(pdf_url)
    if pdf_url.startswith("//"):
        pdf_url = f"https:{pdf_url}"
    elif pdf_url.startswith("/"):
        pdf_url = f"{DETAIL_BASE_URL}{pdf_url}"

    PDF_URL_CACHE[cache_key] = pdf_url
    return pdf_url


def sanitize_filename(text: str) -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|]", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:120] if cleaned else "report"


@app.get("/api/reports")
def api_reports(
    query: str = Query(..., description="股票代码或名称"),
    report_type: str = Query(..., description="报告类型"),
    year: Optional[int] = Query(None, description="年份"),
):
    stock_info = resolve_stock(query)
    page_type = resolve_report_type(report_type)

    if page_type == "all":
        reports = fetch_report_list_all(stock_info["stock_id"])
    else:
        reports = fetch_report_list(stock_info["stock_id"], page_type)
    if year:
        year_str = str(year)
        reports = [
            item
            for item in reports
            if (item.get("report_year") or item["date"][:4]) == year_str
        ]

    return {
        "stock_id": stock_info["stock_id"],
        "stock_name": stock_info.get("stock_name", stock_info["stock_id"]),
        "report_type": page_type,
        "report_type_label": REPORT_TYPE_LABEL.get(page_type, page_type),
        "year": year,
        "reports": reports,
    }


@app.get("/api/report/pdf")
def api_report_pdf(
    stock_id: str = Query(..., description="股票代码"),
    bulletin_id: str = Query(..., description="公告ID"),
    title: Optional[str] = Query(None, description="文件名"),
):
    if not re.fullmatch(r"\d{6}", stock_id):
        raise HTTPException(status_code=400, detail="股票代码格式错误")
    if not bulletin_id:
        raise HTTPException(status_code=400, detail="公告ID不能为空")

    detail_url = (
        f"{DETAIL_BASE_URL}/corp/view/vCB_AllBulletinDetail.php?"
        f"stockid={stock_id}&id={bulletin_id}"
    )
    try:
        pdf_url = fetch_pdf_url(stock_id, bulletin_id)
    except Exception:
        return RedirectResponse(detail_url)

    pdf_headers = {**HEADERS, "Referer": detail_url}
    try:
        resp = requests.get(pdf_url, headers=pdf_headers, stream=True, timeout=30)
        if resp.status_code != 200:
            return RedirectResponse(detail_url)
    except Exception:
        return RedirectResponse(detail_url)

    filename = sanitize_filename(title or f"{stock_id}_{bulletin_id}") + ".pdf"
    quoted_name = quote(filename)
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{quoted_name}"
    }

    return StreamingResponse(
        resp.iter_content(chunk_size=1024 * 128),
        media_type="application/pdf",
        headers=headers,
    )


app.mount("/", StaticFiles(directory="web", html=True), name="web")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
