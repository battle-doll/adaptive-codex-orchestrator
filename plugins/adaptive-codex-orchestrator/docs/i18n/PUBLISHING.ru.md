# Checklist проверки публикации

[English](../PUBLISHING.md) · [한국어](PUBLISHING.ko.md) ·
[日本語](PUBLISHING.ja.md) · [简体中文](PUBLISHING.zh-CN.md) · **Русский**

Это русский перевод-инструкция к [английскому Publishing
Checklist](../PUBLISHING.md). При расхождениях действует поддерживаемый английский
оригинал.

## Текущий статус

Adaptive Codex Orchestrator `0.1.0` — неопубликованный public-review candidate.
Содержимое repository не означает отправку, одобрение, deployment или
принятие marketplace. Публикация — явное действие repository owner после
прохождения всех применимых gate.

Проект является независимым community tool. Нельзя создавать впечатление, что
он связан, спонсируется или одобряется OpenAI либо является официальным
продуктом OpenAI.

## Package и public metadata

- [ ] Проверить `.codex-plugin/plugin.json` текущим официальным/установленным
      validator.
- [ ] Убедиться, что package folder и manifest name в точности равны
      `adaptive-codex-orchestrator`.
- [ ] Согласовать версии в manifest, `pyproject.toml`, marketplace и
      `CHANGELOG.md`.
- [ ] Окончательно проверить ownership и отображение publisher/developer
      `battle-doll`, записанного в manifest.
- [ ] Проверить доступность и содержание обозначенных manifest публичных
      адресов-кандидатов: [GitHub repository](https://github.com/battle-doll/adaptive-codex-orchestrator),
      homepage, privacy и terms. Для общей поддержки предназначены
      [GitHub Issues](https://github.com/battle-doll/adaptive-codex-orchestrator/issues),
      для чувствительных сообщений — [закрытое advisory](https://github.com/battle-doll/adaptive-codex-orchestrator/security/advisories/new);
      доступность каждого канала проверяется до использования.
- [ ] Убедиться, что `LICENSE` и `MIT` metadata в manifest согласованы.
- [ ] Текущий validator отклоняет поле manifest `hooks`; сохранить default
      discovery через `hooks/hooks.json`.
- [ ] Не добавлять неподдерживаемые `supportURL` и `brandColorDark`.
- [ ] Убедиться, что starter prompts не преувеличивают capabilities, лимиты длины
      или поддержку команд, которая сейчас ограничена корейским и английским.

## Assets и evidence

- [ ] Проверить оригинальность `assets/icon.svg` и `assets/logo.svg`, читаемость
      в малом размере и контраст на светлом/тёмном фоне.
- [ ] Убедиться в отсутствии логотипов OpenAI/ChatGPT, скопированного Codex
      artwork, вводящего в заблуждение оформления, bundled font и недоступных
      внешних assets.
- [x] Подготовлены `assets/logo.png` (256×256) и `assets/composer-icon.png` (48×48),
      исходные SVG сохранены. Два нейтральных PNG предназначены для повторного использования
      в четырёх light/dark upload slots.
- [x] Зафиксировано, что пакет skills-only и не имеет пользовательского UI
      инструмента MCP, поэтому product UI screenshots в текущем объёме проверки
      не нужны. Перед подачей проверить, не изменились ли требования портала.
- [ ] Повторить unit, hook fixture, state, parser, path и policy-eval проверки из
      [Validation](../VALIDATION.md) и [Testing](../TESTING.md).
- [x] Подготовлены [5 позитивных и 3 негативных reviewer cases](../../evals/reviewer-cases.json)
      с воспроизводимым setup и expected result.
- [ ] Провести human review документов [Security](../SECURITY.md),
      [Privacy](../PRIVACY.md) и [Terms](../TERMS.md). Они не являются
      юридической консультацией.

## Ручная проверка local marketplace

Сначала подтвердите, что фактическое name в
`.agents/plugins/marketplace.json` равно
`adaptive-codex-orchestrator`. Следующие команды меняют состояние Codex и
выполняются owner вручную.

```text
codex plugin marketplace add <absolute-repository-root>
codex plugin list --marketplace adaptive-codex-orchestrator --available --json
codex plugin add adaptive-codex-orchestrator@adaptive-codex-orchestrator
```

В новой задаче Codex проверьте hook trust, disabled behavior, четыре scopes, три
profiles, status, cleanup, compatibility mode, bounded delegation и fallback
`$adaptive-orchestration`. Не запускайте `marketplace add` для default personal
marketplace.

## Непосредственно перед submission

1. Перепроверить актуальные официальные plugin, hook, subagent, model и
   public-submission schema.
2. Проверить установку из реального public source в clean environment.
3. Подтвердить ownership, HTTPS, redirects и содержимое всех public URL и
   publisher claims.
4. Убедиться в отсутствии secrets, private paths, prompts, source fixtures,
   local cachebusters и отсутствующих assets.
5. Провести итоговый review code, docs, security, privacy, terms, brand и
   compatibility.
6. Выполнять submission только по актуальной официальной процедуре после явного
   разрешения owner.

Нельзя считать checklist выполненным только из-за PASS local validation.

## Действия только owner

- Окончательно проверить ownership, доступность и содержание publisher
  `battle-doll` и обозначенных manifest публичных URL-кандидатов.
- Получить требуемую legal/trademark review.
- Проверить в актуальном portal повторное использование 2 PNG в 4 light/dark
  slots; если пакет остаётся skills-only, product UI screenshots не создавать.
- Вручную проверить в portal подготовленные 5 positive и 3 negative cases.
- Выполнить clean install с реального public source на поддерживаемых платформах.
- Явно разрешить tag, push, release и submission.
- После публикации поддерживать public support и private security-reporting
  channels.

Этот перевод не меняет название, права или отказ от гарантий
[MIT License](../../LICENSE) и не заменяет [английский оригинал](../PUBLISHING.md).
