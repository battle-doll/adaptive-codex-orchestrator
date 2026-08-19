# Запись о публичной подаче

[English](SUBMISSION.md) · [한국어](SUBMISSION.ko.md) · [日本語](SUBMISSION.ja.md) ·
[简体中文](SUBMISSION.zh-CN.md) · **Русский**

Дата проверки: **2026-08-19**

Статус: **подготовлено локально; ещё не подано, не одобрено и не опубликовано**.

Это краткая запись для публичной проверки. Подробные действия владельца
приведены в [Publishing](../PUBLISHING.md), а выполненные локальные проверки —
в [Validation](../VALIDATION.md). Документ не разрешает tag, push, release,
развёртывание, регистрацию marketplace или внешнюю подачу.

## Метаданные подачи

[Точные значения portal listing](SUBMISSION.md#exact-portal-listing-candidate) в
английской версии дословно отражают текущий manifest. Основные значения:

- package `adaptive-codex-orchestrator`, version `0.1.0`
- display name `Adaptive Codex Orchestrator`
- subtitle `Adaptive task orchestration`
- publisher `battle-doll`, category `Developer Tools`, license `MIT`
- runtime mode `Ultra Orchestration`, requested worker `gpt-5.3-codex-spark`
- color `#7168E8`, `./assets/composer-icon.png` (48×48), `./assets/logo.png` (256×256).
  Два нейтральных PNG повторно используются в четырёх light/dark upload slots;
  дополнительные PNG не создаются
- языки управляющих команд: только корейский и английский

Английская версия также содержит точные long description, 8 capabilities,
3 starter prompts и предлагаемый release note. Перед подачей их необходимо
сверить с актуальной официальной схемой портала.

## Обозначенные публичные адреса-кандидаты

Publisher, записанный в manifest, — [battle-doll](https://github.com/battle-doll).
Repository/website:
[GitHub repository](https://github.com/battle-doll/adaptive-codex-orchestrator),
homepage: [README](https://github.com/battle-doll/adaptive-codex-orchestrator#readme),
privacy: [PRIVACY.md](https://github.com/battle-doll/adaptive-codex-orchestrator/blob/main/PRIVACY.md),
terms: [TERMS.md](https://github.com/battle-doll/adaptive-codex-orchestrator/blob/main/TERMS.md),
публичная политика поддержки:
[SUPPORT.md](https://github.com/battle-doll/adaptive-codex-orchestrator/blob/main/SUPPORT.md),
кандидат для общей поддержки:
[GitHub Issues](https://github.com/battle-doll/adaptive-codex-orchestrator/issues),
кандидат для чувствительных сообщений о безопасности:
[закрытое GitHub advisory](https://github.com/battle-doll/adaptive-codex-orchestrator/security/advisories/new).

Такое обозначение не доказывает доступность, проверку содержания или публикацию.
Перед использованием и подачей необходимо проверить HTTPS, владение, содержание
и доступность закрытых advisory. Чувствительные данные нельзя отправлять в Issues.

## Материалы для рецензента и оставшиеся условия

[Reviewer cases](../../evals/reviewer-cases.json) содержат ровно **5 позитивных
и 3 негативных сценария** с воспроизводимой настройкой и ожидаемым поведением.
Они не заменяют автономный набор из 31 policy scenarios.

Владелец должен повторно проверить актуальные требования к manifest, hook,
skill, model, assets, screenshots, legal links и portal; подтвердить publisher,
URL, `MIT License`, version, повторное использование 2 PNG в 4 slots, policies и
release note. Сейчас пакет skills-only и не имеет пользовательского UI
инструмента MCP, поэтому product UI screenshots не нужны. Требуются полная
автономная проверка и чистая установка из реального публичного источника.
Подача допускается только по актуальному официальному процессу после явного
разрешения. Локальная проверка не означает одобрение marketplace.

Управляющие команды распознаются только на корейском и английском. Перевод не
добавляет поддержку команд на японском, упрощённом китайском или русском.
