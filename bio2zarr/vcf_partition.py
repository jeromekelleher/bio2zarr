from typing import Any, Dict, Optional, Sequence, Union
import re
import itertools

import fsspec
import numpy as np
from cyvcf2 import VCF
import humanfriendly

from bio2zarr.csi import CSI_EXTENSION, read_csi
from bio2zarr.tbi import TABIX_EXTENSION, read_tabix
from bio2zarr.typing import PathType
from bio2zarr.utils import ceildiv, get_file_length


# TODO create a Region dataclass that will sort correctly, and has
# a str method that does the correct thing

def region_filter(variants, region=None):
    """Filter out variants that don't start in the given region."""
    if region is None:
        return variants
    else:
        start = get_region_start(region)
        return itertools.filterfalse(lambda v: v.POS < start, variants)


def get_region_start(region: str) -> int:
    """Return the start position of the region string."""
    if re.search(r":\d+-\d*$", region):
        contig, start_end = region.rsplit(":", 1)
        start, end = start_end.split("-")
    else:
        return 1
    return int(start)


def region_string(contig: str, start: int, end: Optional[int] = None) -> str:
    if end is not None:
        return f"{contig}:{start}-{end}"
    else:
        return f"{contig}:{start}-"



def get_tabix_path(
    vcf_path: PathType, storage_options: Optional[Dict[str, str]] = None
) -> Optional[str]:
    url = str(vcf_path)
    storage_options = storage_options or {}
    tbi_path = url + TABIX_EXTENSION
    with fsspec.open(url, **storage_options) as openfile:
        fs = openfile.fs
        if fs.exists(tbi_path):
            return tbi_path
        else:
            return None


def get_csi_path(
    vcf_path: PathType, storage_options: Optional[Dict[str, str]] = None
) -> Optional[str]:
    url = str(vcf_path)
    storage_options = storage_options or {}
    csi_path = url + CSI_EXTENSION
    with fsspec.open(url, **storage_options) as openfile:
        fs = openfile.fs
        if fs.exists(csi_path):
            return csi_path
        else:
            return None


def read_index(
    index_path: PathType, storage_options: Optional[Dict[str, str]] = None
) -> Any:
    url = str(index_path)
    if url.endswith(TABIX_EXTENSION):
        return read_tabix(url, storage_options=storage_options)
    elif url.endswith(CSI_EXTENSION):
        return read_csi(url, storage_options=storage_options)
    else:
        raise ValueError("Only .tbi or .csi indexes are supported.")


def get_sequence_names(vcf_path: PathType, index: Any) -> Any:
    try:
        # tbi stores sequence names
        return index.sequence_names
    except AttributeError:
        # ... but csi doesn't, so fall back to the VCF header
        return VCF(vcf_path).seqnames


def partition_into_regions(
    vcf_path: PathType,
    *,
    index_path: Optional[PathType] = None,
    num_parts: Optional[int] = None,
    target_part_size: Union[None, int, str] = None,
    storage_options: Optional[Dict[str, str]] = None,
) -> Optional[Sequence[str]]:
    """
    Calculate genomic region strings to partition a compressed VCF or BCF file into roughly equal parts.

    A ``.tbi`` or ``.csi`` file is used to find BGZF boundaries in the compressed VCF file, which are then
    used to divide the file into parts.

    The number of parts can specified directly by providing ``num_parts``, or by specifying the
    desired size (in bytes) of each (compressed) part by providing ``target_part_size``.
    Exactly one of ``num_parts`` or ``target_part_size`` must be provided.

    Both ``num_parts`` and ``target_part_size`` serve as hints: the number of parts and their sizes
    may be more or less than these parameters.

    Parameters
    ----------
    vcf_path
        The path to the VCF file.
    index_path
        The path to the VCF index (``.tbi`` or ``.csi``), by default None. If not specified, the
        index path is constructed by appending the index suffix (``.tbi`` or ``.csi``) to the VCF path.
    num_parts
        The desired number of parts to partition the VCF file into, by default None
    target_part_size
        The desired size, in bytes, of each (compressed) part of the partitioned VCF, by default None.
        If the value is a string, it may be specified using standard abbreviations, e.g. ``100MB`` is
        equivalent to ``100_000_000``.
    storage_options:
        Any additional parameters for the storage backend (see ``fsspec.open``).

    Returns
    -------
    The region strings that partition the VCF file, or None if the VCF file should not be partitioned
    (so there is only a single partition).

    Raises
    ------
    ValueError
        If neither of ``num_parts`` or ``target_part_size`` has been specified.
    ValueError
        If both of ``num_parts`` and ``target_part_size`` have been specified.
    ValueError
        If either of ``num_parts`` or ``target_part_size`` is not a positive integer.
    """
    if num_parts is None and target_part_size is None:
        raise ValueError("One of num_parts or target_part_size must be specified")

    if num_parts is not None and target_part_size is not None:
        raise ValueError("Only one of num_parts or target_part_size may be specified")

    if num_parts is not None and num_parts < 1:
        raise ValueError("num_parts must be positive")

    if target_part_size is not None:
        if isinstance(target_part_size, int):
            target_part_size_bytes = target_part_size
        else:
            target_part_size_bytes = humanfriendly.parse_size(target_part_size)
        if target_part_size_bytes < 1:
            raise ValueError("target_part_size must be positive")

    # Calculate the desired part file boundaries
    file_length = get_file_length(vcf_path, storage_options=storage_options)
    if num_parts is not None:
        target_part_size_bytes = file_length // num_parts
    elif target_part_size_bytes is not None:
        num_parts = ceildiv(file_length, target_part_size_bytes)
    # FIXME - changing semantics from sgkit version here.
    # if num_parts == 1:
    #     return None
    part_lengths = np.array([i * target_part_size_bytes for i in range(num_parts)])

    if index_path is None:
        index_path = get_tabix_path(vcf_path, storage_options=storage_options)
        if index_path is None:
            index_path = get_csi_path(vcf_path, storage_options=storage_options)
            if index_path is None:
                raise ValueError("Cannot find .tbi or .csi file.")

    # Get the file offsets from .tbi/.csi
    index = read_index(index_path, storage_options=storage_options)
    sequence_names = get_sequence_names(vcf_path, index)
    file_offsets, region_contig_indexes, region_positions = index.offsets()

    # Search the file offsets to find which indexes the part lengths fall at
    ind = np.searchsorted(file_offsets, part_lengths)

    # Drop any parts that are greater than the file offsets
    # (these will be covered by a region with no end)
    ind = np.delete(ind, ind >= len(file_offsets))  # type: ignore[no-untyped-call]

    # Drop any duplicates
    ind = np.unique(ind)  # type: ignore[no-untyped-call]

    # Calculate region contig and start for each index
    region_contigs = region_contig_indexes[ind]
    region_starts = region_positions[ind]

    # Build region query strings
    regions = []
    for i in range(len(region_starts)):
        contig = sequence_names[region_contigs[i]]
        start = region_starts[i]

        if i == len(region_starts) - 1:  # final region
            regions.append(region_string(contig, start))
        else:
            next_contig = sequence_names[region_contigs[i + 1]]
            next_start = region_starts[i + 1]
            end = next_start - 1  # subtract one since positions are inclusive
            if next_contig == contig:  # contig doesn't change
                regions.append(region_string(contig, start, end))
            else:
                # contig changes, so need two regions (or possibly more if any
                # sequences were skipped)
                regions.append(region_string(contig, start))
                for ri in range(region_contigs[i] + 1, region_contigs[i + 1]):
                    regions.append(sequence_names[ri])
                regions.append(region_string(next_contig, 1, end))

    # https://github.com/pystatgen/sgkit/issues/1200
    # Turns out we need this for correctness. It's just that the
    # tests aren't particularly comprehensive. There must be some way we can
    # detect stuff that's in the index, and not in the header?

    # Add any sequences at the end that were not skipped
    for ri in range(region_contigs[-1] + 1, len(sequence_names)):
        regions.append(sequence_names[ri])

    return regions
