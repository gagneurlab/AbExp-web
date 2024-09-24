def parse_variant(variant):
    if len(variant.split(':')) == 3:
        parts = variant.split(':')
        ref, alt = parts[2].split('&gt;')
    elif len(variant.split('-')) == 4:
        parts = variant.split('-')
        ref = parts[2]
        alt = parts[3]
    elif len(variant.split()) == 4:
        parts = variant.split()
        ref = parts[2]
        alt = parts[3]
    else:
        error_message = "Invalid SNV input format. Expected format: 'chromosome:position:ref>alt' or 'chromosome-position-ref-alt' or 'chromosome position ref alt'."
        raise ValueError(error_message)

    ref = ref.upper()
    alt = alt.upper()

    chromosome = parts[0]

    if not chromosome.startswith('chr'):
        chromosome = 'chr' + chromosome

    position = int(parts[1])

    # Validate the input

    if chromosome[3:] not in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16',
                              '17', '18', '19', '20', '21', '22', 'X', 'Y', 'MT']:
        error_message = f"{chromosome} is not a valid chromosome name"
        raise ValueError(error_message)

    if position < 0 or position > 248956422:
        error_message = f"{position} is not a valid position"
        raise ValueError(error_message)

    for c in ref:
        if c not in ['A', 'T', 'G', 'C', '.']:
            error_message = f"{c} is not a valid nucletotide"
            raise ValueError(error_message)

    for c in alt:
        if c not in ['A', 'T', 'G', 'C', '.']:
            error_message = f"{c} is not a valid nucletotide"
            raise ValueError(error_message)

    return f"{chromosome}:{position}:{ref}>{alt}"


def parse_input(snv_input):
    # Check that all characters in the input are letters, numbers or allowed special symbols
    check_input = "".join(snv_input.split())
    for symb in [':', '&gt;', '-']:
        check_input = check_input.replace(symb, '')
    if not check_input.isalnum():
        error_message = "Invalid characters in the input."
        raise ValueError(error_message)

    max_count = 10
    split_input = snv_input.strip().split('\n')
    if len(split_input) > max_count:
        error_message = f"The input must not contain more than {max_count} variants."
        raise ValueError(error_message)
    proc_input = set()
    for variant in split_input:
        proc_input.add(parse_variant(variant.strip()))
    return list(proc_input)


def split_variant(variant):
    chrom, pos, ref_alt = variant.split(':')
    ref, alt = ref_alt.split('>')
    pos = int(pos)

    if chrom.startswith('chr'):
        chrom = chrom[3:]

    return chrom, pos, ref, alt


def get_ensembl_gene_id(chrom, pos, gtf):
    genes = gtf.region((chrom, pos - 1, pos), featuretype="gene")
    # genes_pos, genes_neg = [], []
    gene_ids = []

    for gene in genes:
        if gene[3] > pos or gene[4] < pos:
            continue
        gene_ids.append(gene["gene_id"][0].split('.')[0])

    return gene_ids
    # if gene[6] == '+':
    #     genes_pos.append(gene_id)
    # elif gene[6] == '-':
    #     genes_neg.append(gene_id)

    # return genes_pos, genes_neg
