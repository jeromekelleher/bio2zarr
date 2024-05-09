---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Bash
  language: bash
  name: bash
---
# Vcf2zarr tutorial

This is a step-by-step tutorial showing you how to convert your 
VCF data into Zarr format. There's three different ways to 
convert your data, basically providing different levels of 
convenience and flexibility corresponding to what you might
need for small, intermediate and large datasets.

## Small

```{code-cell} bash
vcf2zarr convert ../tests/data/vcf/sample.vcf.gz sample.zarr -vf
```

## Intermediate

## Large
