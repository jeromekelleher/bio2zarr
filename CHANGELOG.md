# 0.2.2 2026-XX-XX

In development


# 0.2.1 2026-06-04

Feature release.

*New features*

- Support ``f2`` (16-bit) and ``f8`` (64-bit) float dtypes for INFO and FORMAT
  fields by editing the ``dtype`` in a storage schema. Update
  to ``vcf_zarr_version`` 0.5 in metadata. (#493).
- Add ``vcf2zarr create-index`` which builds a region index on a local VCZ store (#490).
- Add ``--ploidy`` option to ``vcf2zarr convert`` (#488)
- Add ``--zarr-format`` option to CLI to support both Zarr format version 2 and 3 (#483).

# 0.2.0 2026-04-15

Feature release: adds Zip output, (partial) support for Windows and improved
Python API.

*New features*

- Add zip VCZ output support to CLI and Python APIs (#462).

- Add ``zipzarr`` CLI to make converting between .vcz and .vcz.zip
  straightforward (#470)

- Add in-memory VCZ output to Python API; ``convert()`` functions
  (``vcf``, ``plink``, ``tskit``) and ``vcf.encode()`` now return a
  ``zarr.Group`` (#462).

- Add ``plink2zarr`` Python API documentation (#462).

- Preliminary Windows support for tskit and plink conversion (#460)

- Add ancestral allele output (``variant_AA``) to tskit output (#469)

- ``vcf2zarr inspect`` now accepts a ``.vcz.zip`` archive in addition
  to a directory store (#471).

*Breaking changes*

- The ``stored`` sizes reported by ``vcf2zarr inspect`` no longer include
  filesystem inode overhead; they now report the compressed bytes as
  returned by Zarr's ``Array.nbytes_stored()`` (#471).

- Change the metadata format for distributed encode to drop the
  unused ``dimension_separator`` field. The metadata
  format version has been bumped from ``0.1`` to ``0.2``: any
  in-progress distributed ``dencode`` run started with an earlier
  version will now fail with a format-version-mismatch error at
  ``dencode-partition``/``dencode-finalise`` time and must be
  restarted from ``dencode-init``. (#472)

*Bug fixes*

- ``vcf2zarr convert`` now accepts VCFs with zero variant records
  (plain, tabix-indexed, or CSI-indexed), producing a valid empty
  VCZ instead of crashing with an unrelated error (#478).

- Fix stdlib ``typing`` module shadowing caused by ``bio2zarr/typing.py``,
  which broke the ``bio2zarr`` console script entry point (#461).

- Missing GT incorrectly marked as phased (#454)

# 0.1.8 2026-03-02

Maintenance release

- Require Zarr Python version 3.1 or greater (#443)
- Drop support for Python 3.10

*Breaking changes*

- Consolidated metadata is no longer generated (#450).
  Consult https://zarr.readthedocs.io/en/stable/user-guide/consolidated_metadata/ for
  details on how to generate consolidated metadata if required.

# 0.1.7 2026-02-03

*Bug fixes*

- Fix issue with 0-dimensional arrays (#437)

- Fix issue with pandas 3.x (required in plink code; #439)

*Breaking changes*

- Require NumPy 2 (#426)

- Require tskit >= 1.0.

- The default `isolated_as_missing` behaviour for tskit conversion now follows
  tskit's default (currently `True`). To get the previous behaviour, create a
  model mapping using `ts.map_to_vcf_model(isolated_as_missing=False)` and pass
  it via the `model_mapping` parameter (or use `tskit2zarr convert --isolated-as-ancestral`).

- The `contig_id` and `isolated_as_missing` parameters to
  `bio2zarr.tskit.convert` have been removed; set these via
  `tskit.TreeSequence.map_to_vcf_model` and pass the returned mapping via the
  `model_mapping` parameter.

*Maintenance*

- Add support for Python 3.13

# 0.1.6 2025-05-23

- Initial Python API support for VCF and tskit one-shot conversion. Format
conversion is done using the functions ``bio2zarr.vcf.convert``
and ``bio2zarr.tskit.convert``.

- Initial version of supported plink2zarr (#390, #344, #382)

- Initial version of tskit2zarr (#232)

- Make format-specific dependencies optional (#385)

- Remove bed_reader dependency (#397, #400)

- Change default number of worker processes to zero (#404) to simplify
  debugging

*Breaking changes*

- Remove explicit sample, contig and filter lists from the schema.
  Existing ICFs will need to be recreated. (#343)

- Add dimensions and default compressor and filter settings to the schema.
  (#361)

- Various changes to existing experimental plink encoding (#390)

# 0.1.5 2025-03-31

- Add support for merging contig IDs across multiple VCFs (#335)

- Add support for unindexed (and uncompressed) VCFs (#337)

# 0.1.4 2025-03-10

- Fix bug in handling all-missing genotypes (#328)

# 0.1.3 2025-03-04

- Fix missing dependency issue for packaging

- Support out-of-order field definitions in the VCF header (#322, @ACEnglish)

# 0.1.2 2025-02-04

- Reduce memory requirement for encoding genotypes with large sample sizes

- Transpose default chunk sizes to 1000 variants and 10,000 samples (issue:300)

- Add chunksize options to mkschema (issue:294)

- Add experimental support for local alleles.

- Add experimental support for ``region_index``

Breaking changes

- ICF metadata format version bumped to ensure long-term compatility between numpy 1.26.x
  and numpy >= 2. Existing ICFs will need to be recreated.


# 0.1.1 2024-06-19

Maintenance release:

- Pin numpy to < 2
- Pin Zarr to < 3

# 0.1.0 2024-06-10

- Initial production-ready version.
- Add -Q/--no-progress flag to CLI
- Change num-partitions argument in dexplode-init and dencode-init
  to a named option.

# 0.0.10 2024-05-15
- Change output format of dexplode-init and dencode-init
- Bugfix for mac progress, and change of multiprocessing startup strategy.

# 0.0.9 2024-05-02

- Change on-disk format for explode and schema
- Support older tabix indexes
- Fix some bugs in explode

# 0.0.8 2024-04-30

- Change on-disk format of distributed encode and simplify
- Check for all partitions nominally completed encoding before doing
  anything destructive in dencode-finalise

# 0.0.6 2024-04-24

- Only use NOSHUFFLE by default on ``call_genotype`` and bool arrays.
- Add initial implementation of distributed encode

# 0.0.5 2024-04-17

- Fix bug in schema handling (compressor settings ignored)
- Move making ICF field partition directories into per-partition processing.
  Remove progress on the init mkdirs step.
- Turn off progress monitor on dexplode-partition
- Fix empty partition bug

# 0.0.4 2024-04-08

- Fix bug in --max-memory handling, and argument to a string like 10G
- Add compressor choice in explode, switch default to zstd
- Run mkdirs in parallel and provide progress
- Change dimension separator to "/" in Zarr
- Update min Zarr version to 2.17

# 0.0.3 2024-03-28

- Various refinements to the CLI

# 0.0.2 2024-03-27

- Merged 1D and 2D encode steps into one, and change rate reporting to bytes
- Add --max-memory for encode
- Change `chunk_width` to `samples_chunk_size` and `chunk_length` to `variants_chunk_size`
- Various updates to the intermediate chunked format, with breaking change to version 0.2
- Add distributed explode commands
