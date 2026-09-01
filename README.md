# Daily Zero-Credit Comic｜零額度自動漫畫

這個專案每天自動產生一篇原創四格漫畫，完全不呼叫 OpenAI、Hugging Face 或其他付費 AI API。

## 自動流程

GitHub Actions 每天台灣時間 08:30 啟動 → 依日期建立固定隨機種子 → 從題材與劇情模板組合今日故事 → Pillow 程式化繪製角色、場景、表情與道具 → 自動加入繁中對白 → 產出 `docs/comics/YYYY-MM-DD.png` → 更新 `docs/latest.png` 與 GitHub Pages → bot 自動 commit。

## 成本

- OpenAI API：0
- 圖片 API：0
- LLM API：0
- 不需要自己的電腦保持開機
- 只使用 GitHub Actions + Python + Pillow

## 每日排程

`.github/workflows/daily-comic.yml` 使用：

```yaml
- cron: "30 0 * * *"
```

也就是台灣時間每天約 08:30 執行。GitHub 排程可能有數分鐘延遲。

## 手動生成

到 GitHub → Actions → Daily Zero-Credit Comic → Run workflow。

## GitHub Pages

Settings → Pages：

- Source：Deploy from a branch
- Branch：main
- Folder：/docs

網站：`https://xieyaozhong.github.io/Comic/`

## 漫畫設定

角色名稱、題材與網站標題在 `config.yaml`。劇情模板與程式繪圖引擎在 `src/generate.py`。

## 產出 metadata

每篇漫畫的 JSON 會標記：

```json
{
  "generator": "procedural-python-v2",
  "api_cost": 0,
  "dry_run": false
}
```

這代表漫畫是正式的零 API 版本，不是 DRY RUN 占位圖。
