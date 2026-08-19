# Поддержка

[English](SUPPORT.md) · [한국어](SUPPORT.ko.md) ·
[日本語](SUPPORT.ja.md) · [简体中文](SUPPORT.zh-CN.md) · **Русский**

> Adaptive Codex Orchestrator `0.1.0` — неопубликованный public-review
> candidate. [GitHub Issues](https://github.com/battle-doll/adaptive-codex-orchestrator/issues)
> обозначен кандидатом для общей поддержки; до использования нужно проверить
> доступность, а срок ответа не обещается.

Проект является независимым community tool, не связанным, не спонсируемым и не
одобряемым OpenAI. Поддержка предоставляется best effort и не заменяет
профессиональную security, legal, privacy или production review.

## Перед обращением

Ознакомьтесь с [README](README.ru.md), [Compatibility](../COMPATIBILITY.md),
[Security](../SECURITY.md), [Privacy](../PRIVACY.md) и
[Validation](../VALIDATION.md). Подготовьте:

- plugin version и operating system;
- используемую поверхность: Codex app или CLI;
- сведения о том, был ли `hooks/hooks.json` проверен и trusted host;
- возникает ли проблема с persistent hooks или только с fallback
  `$adaptive-orchestration <task>`;
- expected/observed behavior, minimal reproduction и соответствующий validation
  output.

Не публикуйте credentials, API keys, private prompts/transcripts, proprietary
source, repository content, account identifiers или private absolute paths.

## Частые проблемы

- **Режим не сохраняется:** нужны supported/trusted hooks и writable
  `PLUGIN_DATA`. Если hooks недоступны, используйте
  `$adaptive-orchestration <task>` только для текущей задачи.
- **Compatibility notice:** плагин не меняет родительскую модель. Вручную
  выберите нужную модель и Ultra setting. Плагин не заявляет об успешной
  проверке Ultra.
- **Spark не подтверждён:** host может не сообщать availability или model
  identity для `gpt-5.3-codex-spark`. Для каждой делегированной подзадачи
  разрешена только одна попытка spawn. При ошибке, лимите или отсутствии
  поддержки нельзя делать retry или подменять модель на host-default; работа
  немедленно возвращается родителю.
- **Ошибка Git/project identity:** используется SHA-256 digest нормализованного
  working directory; исходный путь не сохраняется.
- **State повреждён или недоступен для записи:** обычная работа Codex
  продолжается. Сохранённый повреждённый backup может содержать произвольные
  bytes и должен считаться потенциально чувствительным локальным свидетельством.

## Безопасный сброс

Завершите затронутые sessions и получите точный `PLUGIN_DATA`, назначенный host
для `adaptive-codex-orchestrator`. Убедитесь, что это каталог данных плагина, а
не source, repository root, home, `.codex` root или общий parent. Удаляйте только
этот каталог либо только `state-v1.json`. Не используйте wildcard,
неразрешённую environment variable или общий каталог как цель рекурсивного
удаления.

## Сообщение об уязвимости

Не раскрывайте exploit details, credentials, prompts, proprietary source или
private paths в public issue. Обозначенный кандидат для сообщений о безопасности —
[закрытое GitHub advisory](https://github.com/battle-doll/adaptive-codex-orchestrator/security/advisories/new),
которое необходимо включить и проверить до использования. Если оно недоступно,
не передавайте чувствительные сведения и сначала запросите у maintainer частный
канал.

Укажите affected version, platform/Codex surface, minimal reproduction, impact
и необходимость trusted hooks. До публикации maintainer отдельной политики
гарантия response time отсутствует. Авторитетная процедура описана в
[Security](../SECURITY.md).

## Статус публикации

В manifest записан publisher `battle-doll`, а
[GitHub repository](https://github.com/battle-doll/adaptive-codex-orchestrator),
website, privacy и terms обозначены публичными адресами-кандидатами. GitHub
Issues предназначен для общей поддержки, закрытые advisory — для сообщений о
безопасности. Обозначение не доказывает доступность или публикацию и проверяется
до использования.
Пока owner не завершит [проверку публикации](PUBLISHING.ru.md), не проверит все
URL и явно не разрешит подачу, плагин нельзя называть опубликованным или
одобренным marketplace.

Управляющие команды распознаются только на корейском и английском. Перевод не
добавляет поддержку команд на японском, упрощённом китайском или русском.

При расхождениях действуют [английский Support](SUPPORT.md),
[Terms](../TERMS.md) и непереведённый [MIT License](../../LICENSE).
