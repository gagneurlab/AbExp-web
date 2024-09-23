def run_abexp(snv_input, genome, max_score_only, tissues, extra_info):
    # Get the user's input from the form
    try:
        path_to_prec = f'data/resources/precomputed/absplice/{genome}/multisample/'

        variants_to_run = []
        output = []

        if genome == 'hg38':
            gtf = gffutils.FeatureDB('data/resources/gencode.hg38.annotation.db')
        else:
            gtf = gffutils.FeatureDB('data/resources/gencode.hg19.annotation.db')

        # run the tool or retrieve precomputed scores for each variant in the input
        for snv in snv_input:

            chr_name, pos, ref, alt = split_variant(snv)

            if len(alt) > 1 or extra_info:
                variants_to_run.append(snv)
            else:
                gene_ids = get_ensembl_gene_id(f"chr{chr_name}", pos, gtf)

                result = []

                for gene_id in gene_ids:
                    res = get_precomputed_scores_from_vcf(chr_name, pos, ref, alt, gene_id, tissues, path_to_prec)

                    if res.shape[0] == 0:
                        continue
                    result.append(res)
                if len(result) == 0:
                    variants_to_run.append(snv)
                else:
                    output += result

        if len(variants_to_run) > 0:
            output.append(run_tool(variants_to_run, genome, tissues, GENOME_MAPPER, splicemap5_hg38, splicemap3_hg38,
                                   splicemap5_hg19, splicemap3_hg19, extra_info))

        df_out = pd.concat(output).round(2)
        csv_output = df_out.sort_values(by=['variant', 'AbSplice_DNA'], ascending=[True, False]).to_csv(index=False)

        del output

        # extract max score if needed
        if max_score_only:
            max_values = df_out.groupby('variant')['AbSplice_DNA'].max().reset_index()
            df_max = pd.merge(df_out, max_values, on=['variant', 'AbSplice_DNA'], how='inner').drop_duplicates(
                subset='variant')
            df_max['tissue'] = 'Max score over tissues'
            df_final = df_max.sort_values(by='AbSplice_DNA', ascending=False)
            del df_max
            del max_values
        else:
            df_final = df_out.sort_values(by=['variant', 'AbSplice_DNA'], ascending=[True, False])

        del df_out

        # prepare output for html rendering
        if extra_info:
            expected_order = [
                'variant', 'gene_id', 'AbSplice_DNA', 'tissue', 'junction', 'ref_psi', 'delta_psi',
                'delta_score', 'splice_site_is_expressed', 'splice_site', 'event_type',
                # 'delta_logit_psi', 'median_n', 'acceptor_gain',
                # 'acceptor_loss', 'donor_gain', 'donor_loss', 'acceptor_gain_position',
                # 'acceptor_loss_position', 'donor_gain_position', 'donor_loss_position'
            ]
            df_final['splice_site_is_expressed'] = df_final['splice_site_is_expressed'].replace({0: 'No', 1: 'Yes'})
        else:
            expected_order = ['variant', 'gene_id', 'AbSplice_DNA', 'tissue', 'delta_psi', 'delta_score']

        final_output = df_final[expected_order].values.tolist()

        del df_final

        current_gene_id = ''
        current_gene_names = []
        for i in range(len(final_output)):
            new_gene_id = final_output[i][1]
            if new_gene_id != current_gene_id:
                current_gene_id = new_gene_id
                current_gene_names = list(gene_map[gene_map['gene_id'] == current_gene_id]['gene_name'].values)
                final_output[i].append(current_gene_names)
            else:
                final_output[i].append(current_gene_names)

        unique_variant_values = set()
        unique_gene_id_values = set()
        unique_tissue_values = set()
        if extra_info:
            unique_junction_values = set()
            unique_splice_site_values = set()
            unique_event_type_values = set()
        for row in final_output:
            unique_variant_values.add(row[0])
            unique_gene_id_values.add(row[1])
            unique_tissue_values.add(row[3])
            if extra_info:
                unique_junction_values.add(row[4])
                unique_splice_site_values.add(row[9])
                unique_event_type_values.add(row[10])

        if extra_info:
            return render_template('result_extra_info.html', output=final_output,
                                   unique_column1_values=sorted(unique_variant_values),
                                   unique_column2_values=sorted(unique_gene_id_values),
                                   unique_column4_values=sorted(unique_tissue_values),
                                   unique_junction_values=sorted(unique_junction_values),
                                   unique_splice_site_values=sorted(unique_splice_site_values),
                                   unique_event_type_values=sorted(unique_event_type_values),
                                   unique_yes_no_values=['Yes', 'No'], genome=genome, csv_output=csv_output)
        else:
            return render_template('result.html', output=final_output,
                                   unique_column1_values=sorted(unique_variant_values),
                                   unique_column2_values=sorted(unique_gene_id_values),
                                   unique_column4_values=sorted(unique_tissue_values), genome=genome,
                                   csv_output=csv_output)

    except Exception as e:
        error_message = str(e)
        flash(error_message, 'error')
        return redirect(url_for('index'))

