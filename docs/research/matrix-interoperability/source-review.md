# Preliminary documentary review

The initial review `SR-390` examines the Matrix README at [the pinned revision](https://github.com/trustoverip/aimwg-agent-fiduciary-duties/blob/140b558791bab5bacdbe5245df0aada93d2b27bd/Assurance%20Matrix/README.md), not an operational system. Its two open findings concern the lack of demonstrated native interchange and the distinction between proposed permission-withdrawal tests and operational evidence. The [initial synthetic fixture](evaluate.py) remains a historical research artifact, separate from the later [source-backed worked assessment](worked-assessment.md).

```sh
python3 review/validate_spec_review.py docs/research/matrix-interoperability/matrix-source-review.yaml --risks docs/research/matrix-interoperability/risks.yaml
```

The existing review contract validates the record structure and example-local risk references. It does not establish that the Matrix is compatible with RAHP or that revocation is enforced. The subsequent workbook and WLA source inspection and controlled reference experiment are identified separately in the [source lock](source-lock.json). The review records are draft, prepared with AI assistance; independent human review is required.
