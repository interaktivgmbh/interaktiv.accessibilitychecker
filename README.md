# interaktiv.accessibilitychecker

[![PyPI](https://img.shields.io/pypi/v/interaktiv.accessibilitychecker)](https://pypi.org/project/interaktiv.accessibilitychecker/)
[![CI](https://github.com/interaktivgmbh/interaktiv.accessibilitychecker/actions/workflows/main.yml/badge.svg)](https://github.com/interaktivgmbh/interaktiv.accessibilitychecker/actions/workflows/main.yml)

AI-based accessibility check for Plone pages.

This add-on is the backend for the AI check of
[volto-accessibility-checker](https://github.com/interaktivgmbh/volto-accessibility-checker).
It analyzes the content of a page with AI to find potential accessibility
issues that rule-based tools can't reliably detect, for example alt texts that
may not match the image or link texts whose purpose is unclear. The results are
hints for editors: the AI explains why something may be an issue, but never
suggests a fix.

## Prerequisites

Tested with Plone 6.

This add-on requires [interaktiv.aiclient](https://github.com/interaktivgmbh/interaktiv.aiclient)
to talk to the AI. It's installed automatically as a dependency.

The check has no UI of its own. Install the Volto add-on
[volto-accessibility-checker](https://github.com/interaktivgmbh/volto-accessibility-checker)
to run it from the toolbar.

## Configuration

Install the add-on in the Plone control panel under **Add-ons**. This also
installs the AI Client.

Then open the **AI Client** control panel, enter your OpenRouter API key and
select a model. The model must support:

* structured output (`response_format` with a JSON schema), because the
  results are returned in a fixed format
* image input, so the alt texts can be compared with the images

Requests are only routed to providers that support all request parameters, so
a model without structured output fails instead of returning unusable results.

> [!IMPORTANT]
> Every check sends the page title, the description, all blocks and the images
> of image blocks to OpenRouter and the provider of the selected model. Make
> sure this is acceptable for your content before you enable the check.

## Features

The AI checks the page title, the description and all blocks in the order they
are rendered, including nested blocks. Images of image blocks are sent along
with the content. SVG images are converted to PNG, since OpenRouter doesn't
accept them.

The following criteria are checked. The WCAG references show which success
criteria a check supports. They don't represent a complete conformance
assessment.

| ID   | Criterion                              | WCAG                             |
|------|----------------------------------------|----------------------------------|
| KI01 | Alt text matches the image             | 1.1.1 Non-text Content           |
| KI02 | Alt text fits the context              | 1.1.1 Non-text Content           |
| KI03 | Link texts are meaningful              | 2.4.4 Link Purpose (In Context)  |
| KI04 | Headings are meaningful                | 2.4.6 Headings and Labels        |
| KI05 | Content is logically structured        | 1.3.2 Meaningful Sequence        |
| KI06 | Instructions don't rely on visual cues | 1.3.3 Sensory Characteristics    |

Each criterion gets a result:

* `pass` - no issue found
* `fail` - at least one issue found, with a severity of `minor`, `moderate`,
  `serious` or `critical`
* `incomplete` - the AI couldn't judge it reliably and it needs a manual review

The results are AI assessments that editors should review. A `pass` doesn't
guarantee WCAG conformance, and a `fail` isn't necessarily a confirmed
violation. The severity is a prioritization by the AI, WCAG itself doesn't
define these levels.

Failed criteria list the affected blocks, each with a short hint in the
requested language. Hints that don't belong to a block, for example about the
page as a whole, are returned separately.

### Permissions

Running the check requires the `interaktiv.accessibilitychecker: Run AI check`
permission. By default, it's granted to Manager, Site Administrator, Editor,
Reviewer and Owner. In addition, the user must be allowed to edit the page in
its current workflow state.

### REST API

The check is available as the `@accessibility-check` endpoint on every content
item with blocks:

```shell
curl -X POST http://localhost:8080/Plone/my-page/@accessibility-check \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -u admin:admin \
  -d '{"language": "en"}'
```

`language` sets the language of the titles, descriptions and hints. If it isn't
one of the site's available languages, the language of the page is used.

The response contains one result per criterion:

```json
[
  {
    "criterion": "KI01",
    "title": "Alt text matches the image",
    "description": "The alternative text accurately describes the essential content of the image.",
    "result": "fail",
    "severity": "serious",
    "affected_blocks": ["9f1a0c2e-..."],
    "hints": {"9f1a0c2e-...": "The alt text describes a dog, but the image shows a cat."},
    "unassigned_hints": []
  }
]
```

| Field              | Description                                                  |
|--------------------|--------------------------------------------------------------|
| `criterion`        | ID of the criterion, e.g. `KI01`                             |
| `title`            | Title of the criterion in the requested language             |
| `description`      | Description of the criterion in the requested language       |
| `result`           | `pass`, `fail` or `incomplete`                               |
| `severity`         | Severity of the issue, missing for `pass`                    |
| `affected_blocks`  | UUIDs of the affected blocks                                 |
| `hints`            | Hint per affected block, keyed by block UUID                 |
| `unassigned_hints` | Hints that don't belong to a block                           |

The endpoint responds with `401` if the user isn't allowed to run the check,
and with `502` if the AI doesn't answer or the answer can't be read.

## Adding this add-on to your project

Install the add-on using `pip`:

```shell
pip install interaktiv.accessibilitychecker
```

or if you're using uv:

```shell
uv pip install interaktiv.accessibilitychecker
```

### Install from source

You can also install the add-on from the source. In your `mx.ini` file, add:

```ini
[interaktiv.accessibilitychecker]
url = git@github.com:interaktivgmbh/interaktiv.accessibilitychecker.git
rev = v1.0.0
extras = test
```

Or using https:

```ini
[interaktiv.accessibilitychecker]
url = https://github.com/interaktivgmbh/interaktiv.accessibilitychecker.git
rev = v1.0.0
extras = test
```

## Contribute

- [Issue tracker](https://github.com/interaktivgmbh/interaktiv.accessibilitychecker/issues)
- [Source code](https://github.com/interaktivgmbh/interaktiv.accessibilitychecker/)

## License

The project is licensed under GPLv2.
