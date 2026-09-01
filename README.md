# Daily AI Comic｜每天自動畫一篇漫畫

一個放在 GitHub 上「每天自己寫、自己畫、自己排版、自己發布」的四格漫畫自動化專案。

## 自動流程
GitHub Actions 每天 08:30（台灣時間）啟動 → 選題 → GPT-5.6 Luna 寫四格腳本 → GPT-Image-2 畫四張無文字分鏡 → Pillow 加入繁中對白並合成 → 輸出到 `docs/comics/YYYY-MM-DD.png` → 更新 `docs/latest.png` 與 GitHub Pages。

## 正式生成
在 Repository → Settings → Secrets and variables → Actions 新增：

`OPENAI_API_KEY = 你的 OpenAI API key`

排程若找不到 API key，會自動使用 DRY RUN，避免 Actions 整體失敗。

## 手動測試
Actions → Daily AI Comic → Run workflow，保留 `dry_run=true` 可完整測試而不呼叫 AI API。

## GitHub Pages
Settings → Pages：Source 選 `Deploy from a branch`，Branch 選 `main`，Folder 選 `/docs`。

## 主要設定
角色、題材與畫風都在 `config.yaml`。文字模型預設 `gpt-5.6-luna`，圖片模型預設 `gpt-image-2`。
