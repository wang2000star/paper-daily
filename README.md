# Paper Daily · arXiv 论文日报

公开网站：https://paperdaily.wfz521.com/

**当前研究范围仅限 arXiv**：数学、计算机科学、网络与信息安全、密码学。网页按日期、领域、细分主题、阅读深度和关键词筛选；点击论文标题或“展开总结”原地阅读，再次点击收起。原始论文链接独立。

## 来源与阅读范围

- 唯一主动研究来源是 arXiv 官方新公告列表、RSS、摘要页及可合法取得的 arXiv 全文。`data/sources.json` 仅列 arXiv，不调用外部论文数据库、出版商、机构网站或作者网站继续研究。
- 作者与机构只依据所读 arXiv 版本署名；未披露或未核实明确说明，不向外部网站补查，不猜当前职务、经历或个人相关性。
- 优先阅读全文；最低须实际取得并阅读完整标题和摘要。仅标题、检索片段、打不开摘要者只记检索缺口，不生成论文卡片。
- `reading_depth=abstract` 显著标“摘要级解读”；保存 `abstract_review={source_url,complete_abstract_accessed:true,read_confirmed:true,scope}`，必须有真实阅读依据。
- `partial` / `full_review` 保存 `substantive_review` 的 `content_urls`、`scope`、`method_evidence`、`result_evidence`、`conditions_evidence`。局部正文阅读不等于全文证明审核或实验复现。未读部分不补猜。
- 总结包含中英文标题、全部作者、署名机构、研究问题、主要结果、方法、条件与局限、日期版本和原文链接。重要结果按作者主张转述，不冒充独立验证。
- 不执行论文代码、不开展实验、不转载原始摘要或论文全文。代码链接如已在原稿核实可保留，但不运行。

## AOE 日界与去重

- 每日 AOE 24:00（UTC−12）更新，即 UTC 次日 12:00、北京时间次日 20:00。固定 UTC−12，无夏令时；自动任务原有启用状态和日程不变。
- 截止 T 只统计 `[T−24h,T)` 内首次公开公告的论文，归档日期为刚结束的 AOE 自然日。不改为七天回看，不发布尚未结束的完整窗口。
- arXiv 提交日期不是公告日期；RSS 批次时间是来源提供的批次证据，不伪称独立观测的精确首次可访问秒数。保存 `public_at`、`public_time_source`、`public_time_precision`、`date_note` 和 `eligibility`。
- 时间范围完全落在窗口内才能 `confirmed`。只有日期、时区不明或边界不能确定时，已读条目放 `pending_papers`，另列且不计确认新增。
- 按稳定 arXiv 编号合并跨分类、重复公告及版本；`replaced` / 修订不计作新论文。保留实际核实的版本变化，不靠更新时间杜撰内容变化。
- `editorial_note` 和检索日志区分目录发现、完整摘要实际阅读、核心正文审阅、确认新增与时间待核实。获取整个目录不等于读完全部论文，不把选读冒充全量覆盖。

## 当前文件结构

- `index.html`、`assets/`：无外部依赖的静态网页；无来源选择器或按来源分组。
- `data/issues.json`：当前 arXiv 日期索引，`source_scope=arxiv_only`；每项明确 `path` 与 `report`，前端按索引载入。
- `data/arxiv/YYYY-MM-DD.json`：当前每期结构化数据，所有确认及待核实条目的 `source` 必须是 `arxiv`。
- `reports/arxiv/YYYY-MM-DD.md`：当前每期中文 Markdown。下载按钮只链接当前 arXiv 报告。
- `data/retrieval/arxiv/YYYY-MM-DD.json`：该期官方入口、时间证据、实际检索/阅读数量及缺口。
- `data/arxiv/seen.json`：当前范围的已收录稳定身份与首次正式期次，供跨日去重。
- 历史文件原位保留，不进入当前网页索引或统计；校验器验证已有内容未被覆盖。

## 每日增量流程

1. 读取本规范、当前来源目录、日期索引与 `data/arxiv/seen.json`，先检查本期是否已经发布；保留远程用户更改。
2. 全面检索本期 24 小时窗口内四领域的 arXiv 官方新公告，完成分页与跨分类去重；先建立全部候选清单，再逐篇阅读标题和完整摘要进行筛选，不能先随意抽取小样本。记录目录发现、摘要已筛、未筛和失败数量。
3. 在全体候选摘要筛选基础上，按问题重要性、方法/理论新意、证据强度、技术实用性及可解释价值选择值得详细总结的研究，记录入选理由；不以热度或编号代替判断。优先再读入选稿全文。未完成全体摘要筛选时明确标为进行中/阶段性选读，不宣称已全面筛选；没有合格新增时可发零篇，不用旧稿凑数。
4. 写入 `data/arxiv/YYYY-MM-DD.json`、相应检索日志，更新当前日期索引及当前去重表。重跑是更正或补录，不重复声称论文首次发表。
5. 执行：
   ```sh
   python3 tools/render_markdown.py
   python3 tools/validate.py
   python3 tools/test_time_validation.py
   node --check assets/app.js
   node tools/test_ui.cjs
   ```
6. 交互更改还需检查桌面/手机、键盘、重复展开收起、组合筛选、清除、日期载入及 Markdown 下载路径。展开状态在同一期筛选中保留，成功切换期次后重置。
7. 保存至 Space「学术论文日报」，原规范/源码归档保持同一文件身份；公开 ZIP 仅含源码与原创总结，不含原始论文、抓取缓存、运行数据或私密信息。
8. 非强制提交到 `wang2000star/paper-daily` 的 main；保留 `CNAME`，不改 DNS、凭据或仓库权限。核验远端提交、Pages 部署及线上实际字节，不把提交成功当成已上线。

## 运行边界

日报由已设置的每日任务采集、整理、存档并提交；本站是 GitHub Pages 静态展示端，不虚构仓库内的联网摘要后台。默认不发邮件；无第三方追踪，不在前端放密钥，不依赖查看者电脑。

仅整理公开学术资料，不含私人研究进度或内部笔记。原文版权属于作者与出版方；未取得独立许可前，不推定本仓库赋予超出版权法的再许可。
