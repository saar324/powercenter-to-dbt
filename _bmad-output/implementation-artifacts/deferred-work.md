- source_spec: `_bmad-output/implementation-artifacts/spec-fivetran-source-report.md`
  summary: Support report-only PowerCenter exports that contain source definitions but no mappings.
  evidence: Native review B5/E1 and coordinator probe reproduce the existing baseline read_xml guard No mappings found. This MVP preserves the existing mapping-export input boundary; README/report must state it. A future additive reader mode needs a source-only fixture and a conversion-guard regression.
