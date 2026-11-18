# Contributing

Thanks for helping! Bug reports, new icons, example diagrams and docs fixes are all welcome.
Please follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Setup

```sh
npm install
python3 build.py examples/ --outdir out      # Windows: py build.py examples\ --outdir out
python3 scripts/check.py out
```

## Before you open a pull request

- Rebuild the examples you touched and look at the output.
- Keep `build.py` dependency-free (Python standard library only, 3.9+) and cross-platform: use `pathlib`, read and write
  files as UTF-8, never `shell=True`.
- Keep `"htmlLabels": false` in `mermaid.json`. Typst and many viewers can't render HTML labels.
- Update `CHANGELOG.md` under "Unreleased".

## Contributing icons

- Flat, single-colour (`#049FD9`) SVG with a `viewBox`.
- You must own the artwork or it must be under a licence compatible with this repo (MIT, Apache-2.0, CC0, BSD, CC-BY 4.0 with attribution).
  Do **not** submit Cisco's own artwork, vendor logos or anything copied from a proprietary stencil set.
- Add the file to `icons/README.md`, record its source and licence in `icons/NOTICE.md`, and add an annotation in `REUSE.toml` if it isn't MIT.
  CI runs `reuse lint`.

## AI-assisted contributions

AI-assisted contributions are fine. Please say so in the pull request, review and test everything yourself, and make sure any
generated icons or text don't copy material under an incompatible licence.

## Licence of contributions

By contributing you agree your work is licensed under this repository's licences (MIT for code and docs;
the licence of origin for third-party icons, as recorded in `icons/NOTICE.md`).
