// add criteria_ids to this array if you want to enable strength select for it
const criteria_with_strength_selects = ['pp1', 'ps1', 'bp1']
// this dictionary contains the links for the reference articles of the acmg specifications (masks)
const reference_links = {
    'none': ' https://pubmed.ncbi.nlm.nih.gov/25741868/',
    'TP53': 'https://pubmed.ncbi.nlm.nih.gov/33300245/',
    'CDH1': 'https://pubmed.ncbi.nlm.nih.gov/30311375/',
    'task-force': '#'
}
// this dictionary contains all buttons which should be disabled if one if them is activated
// !! you need to add both directions for this to work properly
// SPECIFIC FOR TP53 spec: PS4 not applicable when BA1 or BS1 are present, PM1 disables pm5
const disable_groups = {
    // very strong pathogenic
    'pvs1': [],
    // strong pathogenic
    'ps1': [],
    'ps2': [],
    'ps3': [],
    'ps4': [],
    // moderate pathogenic
    'pm1': [],
    'pm2': [],
    'pm3': [],
    'pm4': [],
    'pm5': [],
    'pm6': [],
    // supporting pathogenic
    'pp1': ['bs4'],
    'pp2': [],
    'pp3': [],
    'pp4': [],
    'pp5': [],
    // supporting benign
    'bp1': [],
    'bp2': [],
    'bp3': [],
    'bp4': [],
    'bp5': [],
    'bp6': [],
    'bp7': [],
    // strong benign
    'bs1': [],
    'bs2': [],
    'bs3': [],
    'bs4': ['pp1'],
    // stand alone benign
    'ba1': []
}

// this dict contains the default strengths for each mask
const default_strengths = {
    'none': {
        // very strong pathogenic
        'pvs1': 'pvs',
        // strong pathogenic
        'ps1': 'ps', 'ps2': 'ps', 'ps3': 'ps', 'ps4': 'ps',
        // moderate pathogenic
        'pm1': 'pm', 'pm2': 'pm', 'pm3': 'pm', 'pm4': 'pm', 'pm5': 'pm', 'pm6': 'pm',
        // supporting pathogenic
        'pp1': 'pp', 'pp2': 'pp', 'pp3': 'pp', 'pp4': 'pp', 'pp5': 'pp',
        // supporting benign
        'bp1': 'bp', 'bp2': 'bp', 'bp3': 'bp', 'bp4': 'bp', 'bp5': 'bp', 'bp6': 'bp', 'bp7': 'bp',
        // strong benign
        'bs1': 'bs', 'bs2': 'bs', 'bs3': 'bs', 'bs4': 'bs',
        // stand alone benign
        'ba1': 'ba'
    },
    'TP53': {
        // very strong pathogenic
        'pvs1': 'pvs',
        // strong pathogenic
        'ps1': 'ps', 'ps2': 'ps', 'ps3': 'ps', 'ps4': 'ps',
        // moderate pathogenic
        'pm1': 'pm', 'pm2': 'pm', 'pm3': 'pm', 'pm4': 'pm', 'pm5': 'pm', 'pm6': 'pm',
        // supporting pathogenic
        'pp1': 'pp', 'pp2': 'pp', 'pp3': 'pp', 'pp4': 'pp', 'pp5': 'pp',
        // supporting benign
        'bp1': 'bp', 'bp2': 'bp', 'bp3': 'bp', 'bp4': 'bp', 'bp5': 'bp', 'bp6': 'bp', 'bp7': 'bp',
        // strong benign
        'bs1': 'bs', 'bs2': 'bs', 'bs3': 'bs', 'bs4': 'bs',
        // stand alone benign
        'ba1': 'ba'
    },
    'CDH1': {
        // very strong pathogenic
        'pvs1': 'pvs',
        // strong pathogenic
        'ps1': 'ps', 'ps2': 'ps', 'ps3': 'ps', 'ps4': 'ps',
        // moderate pathogenic
        'pm1': 'pm', 'pm2': 'pm', 'pm3': 'pm', 'pm4': 'pm', 'pm5': 'pm', 'pm6': 'pm',
        // supporting pathogenic
        'pp1': 'pp', 'pp2': 'pp', 'pp3': 'pp', 'pp4': 'pp', 'pp5': 'pp',
        // supporting benign
        'bp1': 'bp', 'bp2': 'bp', 'bp3': 'bp', 'bp4': 'bp', 'bp5': 'bp', 'bp6': 'bp', 'bp7': 'bp',
        // strong benign
        'bs1': 'bs', 'bs2': 'bs', 'bs3': 'bs', 'bs4': 'bs',
        // stand alone benign
        'ba1': 'ba'
    },
    'task-force': {
        // very strong pathogenic
        'pvs1': 'pvs',
        // strong pathogenic
        'ps1': 'ps', 'ps2': 'ps', 'ps3': 'ps', 'ps4': 'ps',
        // moderate pathogenic
        'pm1': 'pm', 'pm2': 'pm', 'pm3': 'pm', 'pm4': 'pm', 'pm5': 'pm', 'pm6': 'pm',
        // supporting pathogenic
        'pp1': 'pp', 'pp2': 'pp', 'pp3': 'pp', 'pp4': 'pp', 'pp5': 'pp',
        // supporting benign
        'bp1': 'bp', 'bp2': 'bp', 'bp3': 'bp', 'bp4': 'bp', 'bp5': 'bp', 'bp6': 'bp', 'bp7': 'bp',
        // strong benign
        'bs1': 'bs', 'bs2': 'bs', 'bs3': 'bs', 'bs4': 'bs',
        // stand alone benign
        'ba1': 'ba'
    }
}

// this dict contains all criteria which should be disabled for a specific mask
const not_activateable_buttons = {
    'none': [],
    'TP53': ['pm3', 'pm4', 'pp2', 'pp4', 'pp5', 'bp1', 'bp3', 'bp5', 'bp6'], // this is in disable group and if it is in not activateable buttons as well it will stay disabled: , 'bs4'
    'CDH1': [],
    'task-force': []
}




// this dictionary contains all criteria descriptions depending on mask 
const criteria_descriptions = {
    'none': {
        // very strong pathogenic
        "pvs1":
            `Null variant (nonsense, frameshift, canonical +/-1 or 2 splice sites, initiation \
            codon, single or multi-exon deletion) in a gene where loss of function (LOF) \
            is a known mechanism of disease \r\n\
                Caveats: \r\n\
                - Beware of genes where LOF is not a known disease mechanism (e.g. GFAP, MYH7) \r\n\
                - Use caution interpreting LOF variants at the extreme 3' end of a gene \r\n\
                - Use caution with splice variants that are predicted to lead to exon skipping but leave the remainder of the protein intact \r\n\
                - Use caution in the presence of multiple transcripts`,
        
        // strong pathogenic
        "ps1":
            `Same amino acid change as a previously established pathogenic variant \
            regardless of nucleotide change. \r\n\r\n\
                Example:	Val->Leu caused by either G>C or G>T in the same codon \r\n\
                Caveat:	Beware of changes that impact splicing rather than at the amino acid/protein level`,
        "ps2":
            `De novo (both maternity and paternity confirmed) in a patient with the \
            disease and no family history. \r\n \r\n\
            Note: Confirmation of paternity only is insufficient. Egg donation, surrogate \
            motherhood, errors in embryo transfer, etc. can contribute to non-maternity.`,
        "ps3":
            `Well-established in vitro or in vivo functional studies supportive of a \
            damaging effect on the gene or gene product. \r\n\r\n\
            Note: Functional studies that have been validated and shown to be \
            reproducible and robust in a clinical diagnostic laboratory setting are \
            considered the most well-established.`,
        "ps4":
            "The prevalence of the variant in affected individuals is significantly \
            increased compared to the prevalence in controls. \r\n\r\n\
                Note 1: Relative risk (RR) or odds ratio (OR), as obtained from case-control \
            studies, is >5.0 and the confidence interval around the estimate of RR or OR \
            does not include 1.0. See manuscript for detailed guidance. \r\n\r\n\
                Note 2: In instances of very rare variants where case-control studies may \
            not reach statistical significance, the prior observation of the variant in \
            multiple unrelated patients with the same phenotype, and its absence in \
            controls, may be used as moderate level of evidence.",
        
        // moderate pathogenic
        "pm1":
            "Located in a mutational hot spot and/or critical and well-established \
            functional domain (e.g. active site of an enzyme) without benign variation.",
        "pm2":
            "Absent from controls (or at extremely low frequency if recessive)\
            in Exome Sequencing Project, 1000 Genomes or ExAC. \r\n\r\n\
            Caveat: Population data for indels may be poorly called by next generation \
            sequencing.",
        "pm3":
            "For recessive disorders, detected in trans with a pathogenic variant. \r\n\r\n \
            Note: This requires testing of parents (or offspring) to determine phase.",
        "pm4":
            "Protein length changes due to in-frame deletions/insertions in a non-repeat \
            region or stop-loss variants.",
        "pm5":
            "Novel missense change at an amino acid residue where a different \
            missense change determined to be pathogenic has been seen before. \r\n\r\n \
            Example: Arg156His is pathogenic; now you observe Arg156Cys. \r\n\
            Caveat: Beware of changes that impact splicing rather than at the amino \
            acid/protein level.",
        "pm6":
            "Assumed de novo, but without confirmation of paternity and maternity.",
        
        // supporting pathogenic
        'pp1':
            "Co-segregation with disease in multiple affected family members in a gene \
            definitively known to cause the disease. \r\n\r\n\
            Note: May be used as stronger evidence with increasing segregation data.",
        "pp2":
            "Missense variant in a gene that has a low rate of benign missense variation \
            and where missense variants are a common mechanism of disease.",
        "pp3":
            "Multiple lines of computational evidence support a deleterious effect on \
            the gene or gene product (conservation, evolutionary, splicing impact, etc). \r\n\r\n\
            Caveat: As many in silico algorithms use the same or very similar input for \
            their predictions, each algorithm should not be counted as an independent \
            criterion. PP3 can be used only once in any evaluation of a variant.",
        "pp4":
            "Patient's phenotype or family history is highly specific for a disease with a \
            single genetic etiology.",
        "pp5":
            "Reputable source recently reports variant as pathogenic but the evidence is \
            not available to the laboratory to perform an independent evaluation.",
        
        // stand alone benign
        "ba1":
            "Allele frequency is above 5% in Exome Sequencing Project, 1000 Genomes, \
            or ExAC.",
        
        // strong benign
        "bs1":
            "Allele frequency is greater than expected for disorder.",
        "bs2":
            "Observed in a healthy adult individual for a recessive (homozygous), \
            dominant (heterozygous), or X-linked (hemizygous) disorder with full \
            penetrance expected at an early age.",
        "bs3":
            "Well-established in vitro or in vivo functional studies shows no damaging \
            effect on protein function or splicing.",
        "bs4":
            "Lack of segregation in affected members of a family. \r\n\r\n\
            Caveat: The presence of phenocopies for common phenotypes (i.e. cancer, \
                epilepsy) can mimic lack of segregation among affected individuals. Also, \
                families may have more than one pathogenic variant contributing to an \
                autosomal dominant disorder, further confounding an apparent lack of \
                segregation.",
        
        // supporting benign
        "bp1":
            "Missense variant in a gene for which primarily truncating variants are \
            known to cause disease",
        "bp2":
            "Observed in trans with a pathogenic variant for a fully penetrant dominant \
            gene/disorder; or observed in cis with a pathogenic variant in any \
            inheritance pattern.",
        "bp3":
            "In-frame deletions/insertions in a repetitive region without a known \
            function",
        "bp4":
            "Multiple lines of computational evidence suggest no impact on gene or \
            gene product (conservation, evolutionary, splicing impact, etc) \r\n\r\n\
            Caveat: As many in silico algorithms use the same or very similar input for \
            their predictions, each algorithm cannot be counted as an independent \
            criterion. BP4 can be used only once in any evaluation of a variant.",
        "bp5":
            "Variant found in a case with an alternate molecular basis for disease.",
        "bp6":
            "Reputable source recently reports variant as benign but the evidence is not \
            available to the laboratory to perform an independent evaluation.",
        "bp7":
            "A synonymous (silent) variant for which splicing prediction algorithms \
            predict no impact to the splice consensus sequence nor the creation of a \
            new splice site AND the nucleotide is not highly conserved."
    },
    'TP53': {
        // very strong pathogenic
        "pvs1":
            "Null variant (nonsense, frameshift, canonical ±1 or 2 splice sites, initiation codon,\
            single or multiexon deletion) in a gene where LOF is a known mechanism of disease \r\n\r\n\
            Use SVI-approved decision tree to determine the strength of this criterion\
            (refer to Abou Tayoun et al. for more details).",
        
        // strong pathogenic
        "ps1":
            "Same amino acid change as a previously established pathogenic variant \
            regardless of nucleotide change. \r\n\r\n\
            Use original description with the following additions: \r\n\
                PS1: \r\n\
                    - Must confirm there is no difference in splicing using RNA data. \r\n\
                    - Can only be used to compare to variants classified as Pathogenic or Likely Pathogenic by the \
                      TP53 VCEP (see ClinVar for VCEP classifications). \r\n\r\n\
                PS1_Moderate: \r\n\
                    - Must confirm there is no difference in splicing using a metapredictor. \r\n\
                    - Can only be used to compare to variants classified as Pathogenic or Likely Pathogenic by the TP53 VCEP (see ClinVar).",
        "ps2":
            "De novo (both maternity and paternity confirmed) in a patient with the \
            disease and no family history. \r\n\r\n\
            Use SVI-approved scoring system to determine the strength of this criterion \
            (refer to Table 2 from original publication: PMC8374922 (linked above) for more details)",
        "ps3":
            "Well-established in vitro or in vivo functional studies supportive of a \
            damaging effect on the gene or gene product. \r\n\r\n\
            The following additions have been made by the TP53 ACMG specification: \r\n\
                - PS3: transactivation assays in yeast demonstrate a low functioning allele \
                  (≤20% activity) AND there is evidence of dominant negative effect and loss-of-function \
                  OR there is a second assay showing low function (colony formation assays, apoptosis assays, \
                  tetramer assays, knock-in mouse models and growth suppression assays).\r\n\r\n\
                - PS3_Moderate: transactivation assays in yeast demonstrate a partially \
                  functioning allele (>20% and ≤75% activity) AND there is evidence of dominant \
                  negative effect and loss-of-function OR there is a second assay showing low function \
                  (colony formation assays, apoptosis assays, tetramer assays, knock-in mouse models and \
                  growth suppression assays).\r\n\r\n\
                - PS3_Moderate: there is no data available from transactivation assays in yeast BUT \
                  there is evidence of dominant negative effect and loss-of-function AND there is a second \
                  assay showing low function (colony formation assays, apoptosis assays, tetramer assays, \
                  knock-in mouse models and growth suppression assays).\r\n\r\n\
                ==> Refer to Figure 1 from original publication: PMC8374922 (linked above) for more details.",
        "ps4":
            "The prevalence of the variant in affected individuals is significantly \
            increased compared to the prevalence in controls. \r\n\r\n\
            Use SVI-approved scoring system to determine the strength of this criterion \
            (refer to Table 3 from original publication: PMC8374922 (linked above) for more details). \
            This criterion cannot be applied when a variant also meets BA1 or BS1. Refrain from considering \
            probands who have another pathogenic variant(s) in a highly penetrant cancer gene(s) that is a \
            logical cause for presentation. \r\n\r\n\
            Caveat: \r\n\
                Please be mindful of the risk of clonal hematopoieses of indeterminate potential with TP53 variants \
                (Coffee et al., 2017; Weitzel et al., 2017). One should take care to ensure that probands have \
                germline and not mosaic somatic TP53 variants.",
        
        // moderate pathogenic
        "pm1":
            "Located in a mutational hot spot and/or critical and well-established \
            functional domain (e.g. active site of an enzyme) without benign variation. \r\n\r\n\
            Located in a mutational hotspot defined as: \r\n\
                - Variants within the following codons on protein NP_000537.3: 175, 273, 245, 248, 282, 249. \r\n\
                - Variants seen in cancerhotspots.org (v2) with >10 somatic occurrences (recommendation from the ClinGen \
                  Germline/Somatic Variant Curation Subcommittee).",
        "pm2":
            "Absent from controls (or at extremely low frequency if recessive)\
            in Exome Sequencing Project, 1000 Genomes or ExAC. \r\n\r\n\
            Caveat: Population data for indels may be poorly called by next generation \
            sequencing. \r\n\r\n\
            PM2_Supporting: absent from population databases (gnomAD (most up-to-date non-cancer dataset) is the \
            preferred population database at this time http://gnomad.broadinstitute.org).",
        "pm3":
            "Excluded.",
        "pm4":
            "Excluded.",
        "pm5":
            "Novel missense change at an amino acid residue where a different \
            missense change determined to be pathogenic has been seen before. \r\n\r\n \
            Example: Arg156His is pathogenic; now you observe Arg156Cys. \r\n\r\n\
            PM5: novel missense change at an amino acid residue where at least two other different missense changes \
                determined to be pathogenic by the TP53 VCEP have been seen before. \
                PM5_Supporting: novel missense change at an amino acid residue where a different missense \
                change determined to be pathogenic by the TP53 VCEP has been seen before. \r\n\r\n\
            Both criteria require the following additions: \r\n\
                - Grantham should be used to compare the variants, and the variant being evaluated must have \
                  equal to or higher score than the observed pathogenic variants. \r\n\
                - Splicing should be ruled out using a metapredictor. \r\n\
                - This criterion cannot be applied when a variant also meets PM1.",
        "pm6":
            "Assumed de novo, but without confirmation of paternity and maternity. \r\n\r\n\
            Use SVI-approved scoring system to determine the strength of this criterion (refer to Table 2 from original \
            publication: PMC8374922 (linked above) for more details).",
        
        // supporting pathogenic
        'pp1':
            "Co-segregation with disease in multiple affected family members in a gene \
            definitively known to cause the disease. \r\n\r\n\
            PP1: co-segregation with disease is observed in 3–4 meioses in one family. \r\n\
            PP1_Moderate: co-segregation with disease is observed in 5–6 meioses in one family. \r\n\
            PP1_Strong: co-segregation with disease is observed >7 meioses in >1 family.",
        "pp2":
            "Excluded.",
        "pp3":
            "Multiple lines of computational evidence support a deleterious effect on \
            the gene or gene product (conservation, evolutionary, splicing impact, etc). \r\n\r\n\
            Caveat: As many in silico algorithms use the same or very similar input for \
            their predictions, each algorithm should not be counted as an independent \
            criterion. PP3 can be used only once in any evaluation of a variant. \r\n\r\n\
            PP3: Use original description with the following additions: \r\n\
                - For missense variants, use a combination of BayesDel (≥0.16) and optimised Align-GVGD (C55-C25). \r\n\
                - For splicing variants, use a metapredictor. \r\n\r\n\
            PP3_Moderate: for missense variants, use a combination of BayesDel (≥0.16) and optimized Align-GVGD (C65).",
        "pp4":
            "Excluded.",
        "pp5":
            "Excluded.",
        
        // stand alone benign
        "ba1":
            "Allele frequency is above 5% in Exome Sequencing Project, 1000 Genomes, \
            or ExAC.\r\n\r\n\
            Allele frequency is ≥0.1% in a non-founder population with a minimum of five alleles \
            (gnomAD (most up-to-date non-cancer dataset)) is the preferred population database \
            at this time http://gnomad.broadinstitute.org).",
        
        // strong benign
        "bs1":
            "Allele frequency is greater than expected for disorder. \r\n\r\n\
            Allele frequency is ≥0.03% and <0.1% in a non-founder population with a minimum of five alleles \
            (gnomAD (most up-to-date non-cancer dataset) is the preferred population database at this time \
            http://gnomad.broadinstitute.org).",
        "bs2":
            "Observed in a healthy adult individual for a recessive (homozygous), \
            dominant (heterozygous), or X-linked (hemizygous) disorder with full \
            penetrance expected at an early age.\r\n\r\n\
            BS2: observed in a single dataset in ≥8 females, who have reached at least 60 years of age without cancer \
                (i.e. cancer diagnoses after age 60 are ignored). \r\n\r\n\
            BS2_Supporting: observed in a single dataset in 2–7 females, who have reached at least 60 years of age without cancer. \r\n\r\n\
            Caveat: Be mindful of the risk of clonal hematopoiesis of indeterminate potential with TP53 variants (Coffee et al., 2017; Weitzel et al., 2017). \
                Individuals with mosaic somatic TP53 variants should not be included as evidence for BS2.",
        "bs3":
            "Well-established in vitro or in vivo functional studies shows no damaging \
            effect on protein function or splicing. \r\n\r\n\
            - BS3: transactivation assays in yeast demonstrate a functional allele or super-transactivation \
                (>75% activity) AND there is no evidence of dominant negative effect and loss-of-function OR \
                there is a second assay showing retained function (colony formation assays, apoptosis assays, \
                tetramer assays, knock-in mouse models and growth suppression assays). \r\n\r\n\
            - BS3_Supporting: transactivation assays in yeast demonstrate a partially functioning allele \
                (>20% and ≤75% activity) AND there is no evidence of dominant negative effect and loss-of-function \
                OR there is a second assay showing retained function (colony formation assays, apoptosis assays, \
                tetramer assays, knock-in mouse models and growth suppression assays). \r\n\r\n\
            - BS3_Supporting: there is no data available from transactivation assays in yeast BUT there is no \
                evidence of dominant negative effect and loss-of-function AND there is a second assay showing \
                retained function (colony formation assays, apoptosis assays, tetramer assays, knock-in mouse \
                models and growth suppression assays). \r\n\r\n\
            ==> Refer to Figure 1 from original publication: PMC8374922 (linked above) for more details.",
        "bs4":
            "Lack of segregation in affected members of a family. \r\n\r\n\
            The variant segregates to opposite side of the family meeting LFS criteria, or the variant is \
            present in >3 living unaffected individuals (at least two of three should be female) above 55 years of age.",
            
        // supporting benign
        "bp1":
            "Excluded",
        "bp2":
            "Observed in trans with a pathogenic variant for a fully penetrant dominant \
            gene/disorder; or observed in cis with a pathogenic variant in any \
            inheritance pattern. \r\n\r\n\
            Variant is observed in trans with a TP53 pathogenic variant (phase confirmed), \
            or there are three or more observations with a TP53 pathogenic variant when phase is unknown (at least two different \
            TP53 pathogenic variants). The other observed pathogenic variants must have been classified using \
            the TP53-specific guidelines.",
        "bp3":
            "Excluded",
        "bp4":
            "Multiple lines of computational evidence suggest no impact on gene or \
            gene product (conservation, evolutionary, splicing impact, etc) \r\n\r\n\
            Caveat: As many in silico algorithms use the same or very similar input for \
            their predictions, each algorithm cannot be counted as an independent \
            criterion. BP4 can be used only once in any evaluation of a variant. \r\n\r\n\
            Same rule description with the following additions: \r\n\
                - For missense variants, use a combination of BayesDel (<0.16) and optimized Align-GVGD (C15-C0). \r\n\
                - For splicing variants, use a metapredictor.",
        "bp5":
            "Excluded",
        "bp6":
            "Excluded",
        "bp7":
            "A synonymous (silent) variant for which splicing prediction algorithms \
            predict no impact to the splice consensus sequence nor the creation of a \
            new splice site AND the nucleotide is not highly conserved. \r\n\r\n\
            Same description with the following additions: \r\n\
                - Splicing should be ruled out using a metapredictor. \r\n\
                - If a new alternate site is predicted, compare strength to native site in interpretation."
    }
    
}

