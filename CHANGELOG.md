# Changelog

This file includes a history of past releases. Changes that were not yet added to a release are in the [changelog.d/](./changelog.d) folder.

<!--
⚠️ DO NOT ADD YOUR CHANGES TO THIS FILE! (unless you want to modify existing changelog entries in this file)
Changelog entries are managed by scriv. After you have made some changes to this plugin, create a changelog entry with:

    scriv create

Edit and commit the newly-created file in changelog.d.

If you need to create a new release, create a separate commit just for that. It is important to respect these
instructions, because git commits are used to generate release notes:
  - Modify the version number in `__about__.py`.
  - Collect changelog entries with `scriv collect`
  - The title of the commit should be the same as the new version: "vX.Y.Z".
-->

<!-- scriv-insert-here -->

<a id='changelog-19.0.1'></a>
## v19.0.1 (2025-03-12)

- [Improvement] Migrate packaging from setup.py/setuptools to pyproject.toml/hatch. (by @Danyal-Faheem)
  - For more details view tutor core PR: https://github.com/overhangio/tutor/pull/1163

- [Improvement] Add hatch_build.py in sdist target to fix the installation issues (by @dawoudsheraz)

<a id='changelog-19.0.0'></a>
## v19.0.0 (2024-10-31)
- [Feature] Add a new bucket to handle private media for openedx-learning. (by @Faraz32123)

- 💥 [Deprecation] Drop support for python 3.8 and set Python 3.9 as the minimum supported python version. (by @Faraz32123)

- 💥[Improvement] Rename Tutor's two branches (by @DawoudSheraz):
  * Rename **master** to **release**, as this branch runs the latest official Open edX release tag.
  * Rename **nightly** to **main**, as this branch runs the Open edX master branches, which are the basis for the next Open edX release.

- 💥[Feature] Upgrade to Sumac. (by @Faraz32123)

<a id='changelog-18.0.1'></a>
## v18.0.1 (2024-10-31)

- [Feature] Add support for discovery media files in minio and a separate bucket for discovery in Minio. (by @Faraz32123)
- [BugFix] Add PROFILE_IMAGE_BACKEND settings in minio using patch named `openedx-lms-production-settings` so that profile images persist in k8s deployment of openedx and profile images can work for both local and dev environment. (by @Faraz32123)

<a id='changelog-18.0.0'></a>
## v18.0.0 (2024-06-20)

- 💥[Feature] Upgrade to Redwood (by @Fahadkhalid210)
- [Bugfix] Make plugin compatible with Python 3.12 by removing dependency on `pkg_resources`. (by @regisb)
- [Bugfix] Fix a 500 error on downloading profile information as CSV when the minio plugin is enabled. (by @FahadKhalid210)
- [Feature] add separated grades bucket and manage querystring by config variable. (by @henrrypg)

<a id='changelog-17.0.0'></a>
## v17.0.0 (2023-12-09)

- 💥[Feature] Upgrade to Quince. (by @Fahadkhalid210)
- [Bugfix] Make LMS/Studio connnect to the right port in dev mode. (by @ormsbee)

<a id='changelog-16.0.2'></a>
## v16.0.2 (2023-12-08)

- [Improvement] Added Typing to code, Makefile and test action to the repository and formatted code with Black and isort. (by @CodeWithEmad)

<a id='changelog-16.0.1'></a>
## v16.0.1 (2023-06-15)

- [Bugfix] Fix "'type' object is not subscriptable" error. (by @regisb)
- [Improvement] Add a scriv-compliant changelog. (by @regisb)
