# L4.4 storage

Raw native/control rows, comparison, configuration, logs and summaries are kept
in Git. `native_cache/` remains on the local filesystem; do not delete it. It
contains reusable stationary/profile checkpoints and can be regenerated from
the frozen sources and registered parameters. A SHA256/size manifest is written
at the end of the run; cache binaries are excluded from Git.
