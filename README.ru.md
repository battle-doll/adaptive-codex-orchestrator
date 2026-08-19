# Adaptive Codex Orchestrator

[English](README.md) · [한국어](README.ko.md) ·
[日本語](README.ja.md) · [简体中文](README.zh-CN.md) · **Русский**

> Adaptive Codex Orchestrator — независимый общественный проект. Он не связан
> с OpenAI, не спонсируется и не одобряется OpenAI и не является официальным
> продуктом OpenAI.

Adaptive Codex Orchestrator — локальный, автономный оркестрационный модуль для
Codex. Детерминированный управляющий слой на Python обрабатывает корейские и
английские команды, состояние, идентификатор проекта и контекст hooks для
необязательного режима **Ultra Orchestration**. Выбранная пользователем
родительская модель по-прежнему отвечает за требования, архитектуру, решение
о делегировании, проверку результатов, интеграцию, итоговую валидацию и ответ.

Текущая версия `0.1.0` — кандидат для публичной проверки. Публикация исходного
кода на GitHub, отправка на проверку OpenAI, одобрение и отдельное действие
разработчика Publish — разные состояния; открытый репозиторий не означает, что
последующие этапы уже завершены.

## Возможности и границы

- Состояние one-shot, session, project и общий default плагина хранится в
  `${PLUGIN_DATA}/state-v1.json`.
- Для делегирования рассматриваются только ограниченные, обратимые и независимо
  проверяемые задачи.
- Профиль `balanced` по умолчанию допускает не более 4 workers за один ход
  родительской модели и 1 одновременного writer.
- Вместо исходного пути проекта сохраняется SHA-256 hash нормализованного корня.
- Если trusted hooks недоступны, `$adaptive-orchestration <task>` применяет
  политику только к текущей задаче.

Плагин не меняет родительскую модель, reasoning level, model selector,
разрешения, sandbox или глобальную конфигурацию Codex. Он не заявляет, что
Ultra reasoning проверен, и не утверждает, что `gpt-5.3-codex-spark` реально
использовался без подтверждения host. Управляющему слою не нужны API key, OAuth,
внешняя учётная запись, telemetry или сетевые запросы. Он не сохраняет prompt,
transcript, source code или исходный абсолютный путь проекта.

## Поддерживаемые поверхности

Проверенные цели — Codex app и CLI. Для постоянного управления на естественном
языке нужны поддерживаемые и доверенные пользователем hooks. Нельзя считать,
что обычный разговор ChatGPT запускает локальные Codex hooks, предоставляет
`PLUGIN_DATA`, те же события очистки или настройки subagent. Проверенный
контракт не поддерживает плагины в Codex IDE extension.

Для предполагаемой работы пользователь вручную выбирает Sol и настройку Ultra
reasoning/intelligence. Плагин не делает этот выбор и не может надёжно проверить
Ultra. Подробности: [Compatibility](plugins/adaptive-codex-orchestrator/docs/COMPATIBILITY.md).

## Локальная установка

В manifest записан publisher `battle-doll`, а
[GitHub repository](https://github.com/battle-doll/adaptive-codex-orchestrator),
homepage, privacy и terms URL обозначены как публичные адреса-кандидаты. Это не
означает, что публикация состоялась: перед использованием или подачей нужно
проверить доступность и содержание всех адресов.
До установки проверьте `.codex-plugin/plugin.json`, `hooks/hooks.json`,
`hooks/runtime.py` и решите, доверяете ли вы hooks.

После проверки фактического значения `.agents/plugins/marketplace.json`
владелец репозитория вручную выполняет следующие команды. Они изменяют состояние
Codex.

```text
codex plugin marketplace add <absolute-repository-root>
codex plugin list --marketplace adaptive-codex-orchestrator --available --json
codex plugin add adaptive-codex-orchestrator@adaptive-codex-orchestrator
```

После установки или переустановки начните новую задачу Codex. Default personal
marketplace обнаруживается автоматически; для него не следует выполнять
`marketplace add`.

## Команды управления

Детерминированное распознавание команд сейчас поддерживает **только корейский и
английский языки**. Русская документация не означает поддержку русских команд.
Используйте, например, следующие английские команды:

```text
Turn on Ultra Orchestration for this session.
Use Ultra Orchestration for this task only.
Enable Ultra Orchestration for this repository.
Enable Ultra Orchestration globally.
Switch to the fast profile.
Show orchestration status.
Turn off Ultra Orchestration.
```

Запрос status не меняет состояние. Явное отрицание, конфликтующие scope/profile,
цитаты, code blocks и случайные примеры в длинном тексте обрабатываются безопасно.
Команда управления и реальная задача могут применяться в одном ходе.

Приоритет состояния:

```text
one-shot > session > project > global > disabled
```

Обычное отключение без scope создаёт session OFF override, не удаляя project
или global preference.

| Profile | Workers за ход родителя | Одновременные writers | Retry делегирования |
| --- | ---: | ---: | ---: |
| `conservative` | 2 | 1 | 0; 1 только при явно восстановимой ошибке |
| `balanced` | 4 | 1 | 1 |
| `fast` | 6 | обычно 1; 2 только при полном разделении | 1 |

Более низкий host limit имеет приоритет. Два writer в `fast` допустимы только
при полностью раздельных файлах, отдельных worktrees или подтверждённом
разделении production/test.

## Политика делегирования

Для быстрого worker подходят чётко ограниченные текстовые задачи: поиск файлов
и symbols, трассировка короткого call path, анализ конкретной ошибки, небольшое
подтверждённое исправление, focused tests и механические изменения. Архитектура,
неясная первопричина, authentication/authorization/cryptography, database
migration, разрушительные операции, public API, крупные зависимости, сложная
concurrency, интеграция и окончательная оценка проверки остаются у родителя.

Nested delegation по умолчанию запрещён. Каждый worker получает ограниченный
контракт со scope, разрешёнными файлами, запрещёнными действиями, требуемыми
доказательствами и validation. Родитель проверяет каждый результат и сообщает
только о действительно созданных workers.

## Безопасность, конфиденциальность и сброс

Управляющий слой использует локальный код стандартной библиотеки и не выполняет
внешних сетевых запросов. State содержит только mode/profile, hash project key,
session key и lifecycle flags. Prompt разбирается в памяти текущего event и не
записывается в log или state.

Для сброса завершите затронутые sessions и получите точный `PLUGIN_DATA`,
назначенный host для `adaptive-codex-orchestrator`. Убедитесь, что это каталог
данных данного плагина, а не plugin source, repository root, home, `.codex` root
или общий родительский каталог. Удаляйте только этот каталог либо только
`state-v1.json`. Не используйте wildcard или неразрешённую environment variable
как цель рекурсивного удаления.

- [Исходный Security](SECURITY.md)
- [Исходный Privacy](PRIVACY.md)
- [Исходный Terms](TERMS.md)
- [Поддержка на русском](plugins/adaptive-codex-orchestrator/docs/i18n/SUPPORT.ru.md)

## Проверка и статус публикации

[Локальная запись от 2026-08-19](plugins/adaptive-codex-orchestrator/docs/VALIDATION.md) фиксирует PASS на Windows /
Python 3.12.10: 108 tests (0 failures, 1 намеренный skip), 31 policy evals и
1 969 package assertions. GitHub Actions настроен для Windows, macOS, Linux и
Python 3.9/3.12, но remote CI не запускался в рамках этой локальной записи.

Publisher `battle-doll`, указанные в manifest публичные URL-кандидаты и два PNG
зафиксированы. Нейтральные `assets/logo.png` и `assets/composer-icon.png`
предназначены для повторного использования
в четырёх light/dark upload slots портала. Пакет относится к skills-only и не
имеет пользовательского UI инструмента MCP, поэтому product UI screenshots в
текущем объёме проверки не нужны. Также подготовлены
[5 позитивных и 3 негативных reviewer cases](plugins/adaptive-codex-orchestrator/evals/reviewer-cases.json).
До публикации остаются проверка доступности и содержания каждого URL,
legal/trademark review, clean
install из реального публичного источника и сверка актуальных требований портала.
См. [Submission](plugins/adaptive-codex-orchestrator/docs/i18n/SUBMISSION.ru.md) и [Проверку публикации](plugins/adaptive-codex-orchestrator/docs/i18n/PUBLISHING.ru.md).

Исходный код предоставляется по [MIT License](LICENSE). Этот перевод носит
информационный характер и не заменяет поддерживаемую английскую документацию,
[Terms](TERMS.md) или непереведённый текст `MIT License`.
