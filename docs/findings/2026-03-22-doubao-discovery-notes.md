# Doubao Discovery Notes - 中国 GEO 服务

- Question count: `8`
- Prompt variants tested: `web_default, web_ranked_analysis, web_source_emphasis`

## Variant Summary

- `web_default`: answers=8, with_urls=3, with_domains=5, with_source_labels=8, avg_web_benchmark_score=0.000
- `web_ranked_analysis`: answers=8, with_urls=7, with_domains=7, with_source_labels=8, avg_web_benchmark_score=0.000
- `web_source_emphasis`: answers=8, with_urls=1, with_domains=1, with_source_labels=8, avg_web_benchmark_score=0.000

## Top Domains

- `newrank.cn`: 11
- `71360.com`: 3
- `gsdata.cn`: 3
- `.71360.com`: 1
- `.newrank.cn`: 1
- `analysys.cn`: 1
- `baijingapp.com`: 1
- `bluefocus.com`: 1
- `chinaz.com`: 1
- `developer.doubao.com`: 1
- `geekbang.org`: 1
- `heraldim.com`: 1
- `iresearch.com.cn`: 1
- `netconcepts.cn`: 1
- `ogilvy.com.cn`: 1

## Top Actionable Platforms

- `36氪`: 10
- `钛媒体`: 2

## Initial Assessment

- Use this run to inspect whether Qwen tends to provide explicit citations, implicit brand mentions, or generic listicle-style answers.
- Compare prompt variants by how often they yield extractable sources and concrete decision criteria.
- Feed the raw answers into the next prompt iteration before locking the production prompt set.
