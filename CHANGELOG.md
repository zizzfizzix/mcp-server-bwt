# Changelog

## [0.2.0](https://github.com/zizzfizzix/mcp-server-bwt/compare/v0.1.0...v0.2.0) (2026-09-25)


### ⚠ BREAKING CHANGES

* **tools:** calling a list tool without limit returns at most 50 rows instead of every row. Set BING_WEBMASTER_PAGE_SIZE=0 to restore the old behavior.

### Features

* **tooling:** run pytest in the lefthook pre-push hook ([#36](https://github.com/zizzfizzix/mcp-server-bwt/issues/36)) ([#38](https://github.com/zizzfizzix/mcp-server-bwt/issues/38)) ([2bde12e](https://github.com/zizzfizzix/mcp-server-bwt/commit/2bde12ef45be7675db2ca6a168cf0f9052557391))
* **tooling:** run the validation gate as git hooks via lefthook ([#18](https://github.com/zizzfizzix/mcp-server-bwt/issues/18)) ([#23](https://github.com/zizzfizzix/mcp-server-bwt/issues/23)) ([f8180e6](https://github.com/zizzfizzix/mcp-server-bwt/commit/f8180e678dde34f0d4f2e4b9ca3f51fb7122062a))
* **tools:** bound list tool results by default with offset/limit paging ([#41](https://github.com/zizzfizzix/mcp-server-bwt/issues/41)) ([de41fd9](https://github.com/zizzfizzix/mcp-server-bwt/commit/de41fd9151657040354cc29bca2adced24288105))
* **tools:** cache list tool results between pages ([#46](https://github.com/zizzfizzix/mcp-server-bwt/issues/46)) ([a370b85](https://github.com/zizzfizzix/mcp-server-bwt/commit/a370b85763a985fb745bac59afac8c09caa2e26f))


### Bug Fixes

* **deps:** migrate to mcp 2.x MCPServer and lift the &lt;2 pin ([#14](https://github.com/zizzfizzix/mcp-server-bwt/issues/14)) ([#17](https://github.com/zizzfizzix/mcp-server-bwt/issues/17)) ([07f1dc0](https://github.com/zizzfizzix/mcp-server-bwt/commit/07f1dc025a0852f8fb53725864798658889dc9c9))
* **deps:** pin mcp to 1.x and commit uv.lock ([#13](https://github.com/zizzfizzix/mcp-server-bwt/issues/13)) ([bad0595](https://github.com/zizzfizzix/mcp-server-bwt/commit/bad0595092115dbd779e5e0bcc5ef5261847e073)), closes [#8](https://github.com/zizzfizzix/mcp-server-bwt/issues/8)
* **packaging:** make README uvx and make commands work ([#24](https://github.com/zizzfizzix/mcp-server-bwt/issues/24)) ([#25](https://github.com/zizzfizzix/mcp-server-bwt/issues/25)) ([dde1c02](https://github.com/zizzfizzix/mcp-server-bwt/commit/dde1c02f7fdcd2aa769254723841efc4c8dbb509))
* provide entrypoint specified in pyproject.toml ([6e14683](https://github.com/zizzfizzix/mcp-server-bwt/commit/6e1468370bcf79649d072a85c3c66ac0598973f6))
* **services:** serialize API dates as UTC RFC 3339 ([#6](https://github.com/zizzfizzix/mcp-server-bwt/issues/6)) ([#28](https://github.com/zizzfizzix/mcp-server-bwt/issues/28)) ([31007bd](https://github.com/zizzfizzix/mcp-server-bwt/commit/31007bd166ff73fdb9bafd835573613eabce6ad7))
* **tools:** drop self from tool input schemas ([#10](https://github.com/zizzfizzix/mcp-server-bwt/issues/10)) ([#19](https://github.com/zizzfizzix/mcp-server-bwt/issues/19)) ([cb94421](https://github.com/zizzfizzix/mcp-server-bwt/commit/cb944217c3721ad434a8f95b817b4cd348afa062))


### Documentation

* **pipeline:** configure agent PR pipeline ([#12](https://github.com/zizzfizzix/mcp-server-bwt/issues/12)) ([8212eb4](https://github.com/zizzfizzix/mcp-server-bwt/commit/8212eb42d117110651b204e56fff2945723a3eca))
* **specs:** add spec for lefthook-git-hooks (FR [#18](https://github.com/zizzfizzix/mcp-server-bwt/issues/18)) ([#21](https://github.com/zizzfizzix/mcp-server-bwt/issues/21)) ([b86ff54](https://github.com/zizzfizzix/mcp-server-bwt/commit/b86ff54606043fd4ab329e61b916a7cf646f6b4b))
* **specs:** add spec for lefthook-pytest-pre-push (FR [#36](https://github.com/zizzfizzix/mcp-server-bwt/issues/36)) ([#37](https://github.com/zizzfizzix/mcp-server-bwt/issues/37)) ([4251c9f](https://github.com/zizzfizzix/mcp-server-bwt/commit/4251c9f2b8c55b5a4915cc98d081140755492f46))
* **specs:** add spec for pytest-validation-gate (FR [#30](https://github.com/zizzfizzix/mcp-server-bwt/issues/30)) ([#34](https://github.com/zizzfizzix/mcp-server-bwt/issues/34)) ([052e1f5](https://github.com/zizzfizzix/mcp-server-bwt/commit/052e1f5597b38f3ad96b991521198af442eb75b8))
* **specs:** add spec for release-please (FR [#16](https://github.com/zizzfizzix/mcp-server-bwt/issues/16)) ([#20](https://github.com/zizzfizzix/mcp-server-bwt/issues/20)) ([6a39c87](https://github.com/zizzfizzix/mcp-server-bwt/commit/6a39c877a8eb8864be1ffb3a60ba5811bb788913))
* **specs:** add spec for skip-validate-on-release-prs (FR [#31](https://github.com/zizzfizzix/mcp-server-bwt/issues/31)) ([#32](https://github.com/zizzfizzix/mcp-server-bwt/issues/32)) ([e01d01f](https://github.com/zizzfizzix/mcp-server-bwt/commit/e01d01f49ba1537352e4e00e73e33d96ada01657))
* **specs:** cache list tool results between pages ([#45](https://github.com/zizzfizzix/mcp-server-bwt/issues/45)) ([bf32d43](https://github.com/zizzfizzix/mcp-server-bwt/commit/bf32d436408e65a9374f044898176b10392b21f2))
* **specs:** CI workflow running the validation gate, required on main ([#26](https://github.com/zizzfizzix/mcp-server-bwt/issues/26)) ([bef094d](https://github.com/zizzfizzix/mcp-server-bwt/commit/bef094d7299aab0f2d2c41ac2ee5cecac0f75147))
* **specs:** paginate large list tool results ([#40](https://github.com/zizzfizzix/mcp-server-bwt/issues/40)) ([c614774](https://github.com/zizzfizzix/mcp-server-bwt/commit/c61477433995084fe3a42420d9ae372b4e931e41))
* **specs:** publish mcp-server-bwt to PyPI ([#42](https://github.com/zizzfizzix/mcp-server-bwt/issues/42)) ([f38c617](https://github.com/zizzfizzix/mcp-server-bwt/commit/f38c61764ab667574cb8f21ba700cbf6e2cf575e))
