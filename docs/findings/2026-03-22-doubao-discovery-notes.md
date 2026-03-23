# Doubao Discovery Notes - 中国 GEO 服务

- Question count: `8`
- Prompt variants tested: `web_default, web_ranked_analysis, web_source_emphasis`

## Variant Summary

- `web_default`: answers=8, with_urls=5, with_domains=8, with_source_labels=7, avg_web_benchmark_score=0.000
- `web_ranked_analysis`: answers=8, with_urls=6, with_domains=6, with_source_labels=8, avg_web_benchmark_score=0.000
- `web_source_emphasis`: answers=8, with_urls=1, with_domains=1, with_source_labels=8, avg_web_benchmark_score=0.000

## Top Domains

- `newrank.cn`: 12
- `seowhy.com`: 6
- `gsdata.cn`: 3
- `36kr.com`: 2
- `business.zhihu.com`: 2
- `chinaz.com`: 2
- `pingwest.com`: 2
- `accenture.cn`: 1
- `bluefocus.com`: 1
- `cifnews.com`: 1
- `gexiao.cn`: 1
- `guoji.cc`: 1
- `guoji.tech`: 1
- `huitun.com`: 1
- `iyiou.com`: 1

## Top Actionable Platforms

- `36氪`: 8
- `知乎`: 2
- `小红书`: 1
- `钛媒体`: 1

## Initial Assessment

- Use this run to inspect whether Qwen tends to provide explicit citations, implicit brand mentions, or generic listicle-style answers.
- Compare prompt variants by how often they yield extractable sources and concrete decision criteria.
- Feed the raw answers into the next prompt iteration before locking the production prompt set.
