ALTER TABLE `HerediVar_ahdoebm1`.`classification_criterium` 
CHANGE COLUMN `relevant_info` `relevant_info` TEXT NOT NULL DEFAULT '' ;




INSERT INTO `HerediVar_ahdoebm1`.`classification_scheme` (`name`, `display_name`, `type`, `reference`) VALUES ('enigma-brca1', 'ClinGen ENIGMA BRCA1', 'acmg-enigma-brca1', 'https://cspec.genome.network/cspec/ui/svi/doc/GN092');






INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "PVS1", 
"ACMG summary:
Null variant (nonsense, frameshift, canonical +/-1 or 2 splice sites, initiation codon, single or multi-exon deletion) in a gene where loss of function (LOF) is a known mechanism of disease.
Caveats:
 - Beware of genes where LOF is not a known disease mechanism (e.g. GFAP, MYH7).
 - Use caution interpreting LOF variants at the extreme 3' end of a gene.
 - Use caution with splice variants that are predicted to lead to exon skipping but leave the remainder of the protein intact.
 - Use caution in the presence of multiple transcripts.

Gene-specific modifications:
Null variant (nonsense, frameshift, splice site (donor/acceptor +/-1,2), initiation codon, single or multi-exon deletion) in a gene where loss of function (LOF) is a known mechanism of disease. Apply at appropriate strength according to PVS1 flowchart, which considers knowledge of clinically important functional domains. See Specifications Table 4 and Appendix D for details.
Well-established in vitro or in vivo functional studies supportive of a damaging effect as measured by effect on mRNA transcript profile (mRNA assay only). Apply as PVS1 (RNA) at appropriate strength. See Specifications Figure1B and Appendix E for details.

Instructions:
In alignment with SVI recommendations for PVS1 code application, evidence strength and description has been separated for different variant types. Apply according to PVS1 flowchart, which considers knowledge of clinically important functional domains. For predicted protein termination codon (PTC) variants, apply with exon-specific weights derived for the PM5_PTC code (See Appendix D for details).
See Specifications Table 4, provided as a separate searchable excel file, for a comprehensive summary of codes applicable for all variants considered against the BRCA1 and BRCA2 PVS1 decision trees (initiation, nonsense/frameshift, deletion, duplication, splice site (donor/acceptor +/- 1,2)) - organized by exon. See Appendix Figure 3,4 and Table 5 for further justification.
See Specifications Figure 1B for process to apply codes for splicing data, in content of location and predicted bioinformatic impact of the variant, and adaptive weighting according to assay methodology and proportion of functional transcript retained.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "PS1", 
"ACMG summary:
Same amino acid change as a previously established pathogenic variant regardless of nucleotide change.
Example: Val->Leu caused by either G>C or G>T in the same codon.
Caveat: Beware of changes that impact splicing rather than at the amino acid/protein level.

Strong:
Apply PS1, for predicted missense substitutions, where a previously classified pathogenic variant is considered to act via protein change (no confirmed or predicted effect on mRNA splicing (SpliceAI≤0.1)).
Apply PS1, for exonic and intronic variants with same predicted impact on splicing, as a previously classified pathogenic variant. Vary weight depending on relative positions, and confidence in classification of the reference variant. 
See Specifications Table 5 and Appendix E, J and K for details.

Moderate:
Apply PS1_Moderate, for predicted missense substitutions, where previously classified likely pathogenic variant is considered to act via protein change (no confirmed or predicted effect on mRNA splicing (SpliceAI≤0.1)).
Apply PS1_Moderate, for exonic and intronic variants with same predicted impact on splicing, as a previously classified (likely) pathogenic variant. Vary weight depending on relative positions, and confidence in classification of the reference variant.
See Specifications Table 5 and Appendix E, J and K for details.

Supporting:
Apply PS1_Supporting, for exonic and intronic variants with same predicted impact on splicing, as a previously classified (likely) pathogenic variant. Vary weight depending on relative positions, and confidence in classification of the reference variant.
See Specifications Table 5 and Appendix E, J and K for details.

Instructions:
For both missense and splicing scenarios, (Likely) Pathogenic variant classification should be assigned using VCEP specifications.
For application of PS1 for splicing predictions, see Specifications Table 5. The predicted event of the VUA must precisely match the predicted event of the known (likely) pathogenic variant (e.g. both predicted to lead to exon A skipping, or both to enhanced use of cryptic site B), AND the strength of the prediction for the VUA must be of similar or higher strength than the strength of the prediction for the known (likely) pathogenic variant. For an exonic variant, predicted or proven functional effect of missense substitution/s encoded by the variant and the previously classified pathogenic variant should also be considered before PS1 code application for splicing prediction.
",
1
);


INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "PS2", 
"ACMG summary:
De novo (both maternity and paternity confirmed) in a patient with the disease and no family history.
Note: Confirmation of paternity only is insufficient. Egg donation, surrogate motherhood, errors in embryo transfer, etc. can contribute to non-maternity.
Not applicable
Comments: BRCA1/2-related cancers occur relatively commonly. No information to calibrate the predictive capacity of de novo occurrences.
",
0
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "PS3", 
"ACMG summary:
Well-established in vitro or in vivo functional studies supportive of a damaging effect on the gene or gene product.
Note: Functional studies that have been validated and shown to be reproducible and robust in a clinical diagnostic laboratory setting are considered the most well-established.

Gene-specific modifications:
Well-established in vitro or in vivo functional studies supportive of a damaging effect. Apply PS3 for assays measuring effect via protein only OR mRNA and protein combined. See Specifications Table 9 for code recommendations from calibrated published assays. Also see Figure1C and Appendix E for details.
Well-established in vitro or in vivo functional studies supportive of a damaging effect as measured by effect on mRNA transcript profile (mRNA assay only). Apply as PVS1 (RNA) at appropriate strength. See Specifications Figure1B and Appendix E for details.

Instructions:
See Specifications Figure 1C for simplified flowchart/s to advise application of codes for functional data, in content of variant type and location within a (potentially) clinically important functional domain. Do not apply when conflicting results are present from well-established assays with sufficient controls, which cannot be explained by experimental design.
See Specifications Figure 1B for process to apply codes for splicing data, in content of location and predicted bioinformatic impact of the variant, and adaptive weighting according to assay methodology and proportion of functional transcript retained.
See Specifications Table 9, provided as a separate file in excel format to facilitate searches and look-ups by variant c. and p. nomenclature. It includes PS3 and BS3 code recommendations and rationale for code application of published functional assays data that has been calibrated, and considered against predicted/reported splicing.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "PS4", 
"ACMG summary:
The prevalence of the variant in affected individuals is significantly increased compared to the prevalence in controls.
Note 1: Relative risk (RR) or odds ratio (OR), as obtained from case-control studies, is >5.0 and the confidence interval around the estimate of RR or OR does not include 1.0. See manuscript for detailed guidance.
Note 2: In instances of very rare variants where case-control studies may not reach statistical significance, the prior observation of the variant in multiple unrelated patients with the same phenotype, and its absence in controls, may be used as moderate level of evidence.

Gene-specific modifications:
The prevalence of the variant in affected individuals is significantly increased compared to the prevalence in controls. Case-control studies; p-value ≤0.05 and OR ≥4 (lower confidence interval excludes 2.0). See Appendix F for details.
Modification Type: Clarification,Gene-specific

Instructions:
Case dataset should be ethnicity and country-matched to control dataset. If case-control LR estimates are available for a given dataset, these should be used in preference to case-control OR data, under code PP4 (or BP5, if appropriate). Do not use Proband Counting as originally described.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "PM1", 
"ACMG summary:
Located in a mutational hot spot and/or critical and well-established functional domain (e.g. active site of an enzyme) without benign variation.
Not Applicable
Comments: Considered as component of bioinformatic analysis (PP3/BP4).
",
0
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "PM2", 
"ACMG summary:
Absent from controls (or at extremely low frequency if recessive) in Exome Sequencing Project, 1000 Genomes or Exome Aggregation Consortium.
Caveat: Population data for indels may be poorly called by next generation sequencing.

Gene-Specific modifications:
Absent from controls in an outbred population, from gnomAD v2.1 (non-cancer, exome only subset) and gnomAD v3.1 (non-cancer). Region around the variant must have an average read depth ≥25. See Appendix G for details.
Modification Type: Gene-specific

Instructions:
Observation of a variant only once in a gnomAD outbred population is not informative. Do not apply for insertion, deletion or delins variants. Do not apply if read depth <25 at region around the variant.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "PM3", 
"ACMG summary:
For recessive disorders, detected in trans with a pathogenic variant
Note: This requires testing of parents (or offspring) to determine phase.

Strong:
Apply for patient with phenotype consistent with BRCA1- or BRCA2-related Fanconi Anemia (FA), and co-occurrent variants in the same gene.Phenotype is considered consistent with BRCA1- or BRCA2-related FA if:
(i) Increased chromosome breakage (DEB, MMC, or spontaneous) and at least one clinical feature indicative of BRCA1/2-related FA, categorized under: physical features, pathology and laboratory findings, cancer diagnosis ≤5yr.
(ii) Result unknown for chromosome breakage, and at least two clinical features indicative of BRCA1/2-related FA under at least two of the three categories: physical features, pathology and laboratory findings, cancer diagnosis ≤5yr.
See Specifications Table 6 for approach to assign points per proband, and final PM3 code assignment based on the sum of PM3-related points. Also see Appendix H for additional details.

PM3_Strong = ≥4 points

Moderate:
Apply for patient with phenotype consistent with BRCA1- or BRCA2-related Fanconi Anemia (FA), and co-occurrent variants in the same gene.Phenotype is considered consistent with BRCA1- or BRCA2-related FA if:
(i) Increased chromosome breakage (DEB, MMC, or spontaneous) and at least one clinical feature indicative of BRCA1/2-related FA, categorized under: physical features, pathology and laboratory findings, cancer diagnosis ≤5yr.
(ii) Result unknown for chromosome breakage, and at least two clinical features indicative of BRCA1/2-related FA under at least two of the three categories: physical features, pathology and laboratory findings, cancer diagnosis ≤5yr.
See Specifications Table 6 for approach to assign points per proband, and final PM3 code assignment based on the sum of PM3-related points. Also see Appendix H for additional details.

PM3 = 2 points

Supporting:
Apply for patient with phenotype consistent with BRCA1- or BRCA2-related Fanconi Anemia (FA), and co-occurrent variants in the same gene.Phenotype is considered consistent with BRCA1- or BRCA2-related FA if:
(i) Increased chromosome breakage (DEB, MMC, or spontaneous) and at least one clinical feature indicative of BRCA1/2-related FA, categorized under: physical features, pathology and laboratory findings, cancer diagnosis ≤5yr.
(ii) Result unknown for chromosome breakage, and at least two clinical features indicative of BRCA1/2-related FA under at least two of the three categories: physical features, pathology and laboratory findings, cancer diagnosis ≤5yr.
See Specifications Table 6 for approach to assign points per proband, and final PM3 code assignment based on the sum of PM3-related points. Also see Appendix H for additional details.

PM3_Supporting = 1 point

Instructions:
Co-occurrent P or LP variant should be assigned classification using VCEP specifications. 
Variant under assessment must be sufficiently rare (meet PM2_Supporting, or PM2 not applicable).
See Specifications Table 6 for approach to assign points per proband, and final PM3 code assignment based on the sum of PM3-related points.
For related individuals score only most severe presentation.
Also see Specifications Table 6 for additional stipulations
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "PM4", 
"ACMG summary:
Protein length changes due to in-frame deletions/insertions in a non-repeat region or stop-loss variants.
Not Applicable
Comments: Considered as component of bioinformatic analysis (PP3/BP4).
",
0
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "PM5", 
"ACMG summary:
Novel missense change at an amino acid residue where a different missense change determined to be pathogenic has been seen before.
Example: Arg156His is pathogenic; now you observe Arg156Cys.
Caveat: Beware of changes that impact splicing rather than at the amino acid/protein level.

Gene-specific modifications:
Protein termination codon (PTC) variant in an exon where a different proven pathogenic PTC variant has been seen before. Use to justify additional weight for PTC variants annotated as PVS1. See Specifications Table 4 for PM5_PTC code strengths applicable per exon. See Appendix D for additional details.

Instructions:
Only applied to genomic PTC changes (not splicing). Weight determined by exon where the termination codon occurs (may not be the same exon as the variant position). See Specifications Table 4, provided as a separate searchable excel file, for PM5_PTC codes applicable for predicted termination codon variants - organized by exon.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "PM6", 
"ACMG summary:
Assumed de novo, but without confirmation of paternity and maternity.
Not Applicable
Comments: BRCA1/2-related cancers occur relatively commonly. No information to calibrate the predictive capacity of de novo occurrences.
",
0
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "PP1", 
"ACMG summary:
Co-segregation with disease in multiple affected family members in a gene definitively known to cause the disease.
Note: May be used as stronger evidence with increasing segregation data.

Gene-specific modifications:
Co-segregation with disease in multiple affected family members in a gene definitively known to cause the disease, as measured by a quantitative co-segregation analysis method. See Appendix I for details.

Apply weight as per Bayes Score:
PP1_Very Strong - LR>350:1
PP1_Strong - LR>18.7:1
PP1_Moderate - LR>4.3:1
PP1 - LR >2.08:1

Instructions:
Recommend use of online tool: https://fengbj-laboratory.org/cool3/analysis.html 
Additional information, including pedigree formatting, is available at: https://fengbj-laboratory.org/cool3/manual.html.
Stipulation: to apply code as Pathogenic Very Strong, VUS should have bioinformatically predicted (or experimentally proven) effect on protein or mRNA splicing. If co-segregation score is from a single family, or several families from an isolated population, assess the possibility of a different causative pathogenic variant.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "PP2", 
"ACMG summary:
Missense variant in a gene that has a low rate of benign missense variation and where missense variants are a common mechanism of disease.
Not Applicable
Comments: High frequency of benign missense variants.
",
0
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "PP3", 
"ACMG summary:
Multiple lines of computational evidence support a deleterious effect on the gene or gene product (conservation, evolutionary, splicing impact, etc.).
Caveat: As many in silico algorithms use the same or very similar input for their predictions, each algorithm should not be counted as an independent criterion. PP3 can be used only once in any evaluation of a variant.

Gene-specific modifications:
Apply PP3 for missense or in-frame insertion, deletion or delins variants inside a (potentially) clinically important functional domain and predicted impact via protein change (BayesDel no-AF score ≥0.28). As justified in the appendices, (potentially) clinically important functional domains are defined as: BRCA1 RING aa 2-101; BRCA1 coiled-coil aa 1391-1424; BRCA1 BRCT repeats aa 1650-1857.
Apply PP3 for predicted splicing (SpliceAI ≥0.2) for silent, missense/in-frame (irrespective of location in clinically important functional domain) and for intronic variants outside of donor and acceptor 1,2 sites.
See Specifications Figure1A and Appendix J for details.

Instructions:
See Specifications Figure 1A for process to apply codes according to variant type, location and predicted bioinformatic impact.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "PP4", 
"ACMG summary:
Patient's phenotype or family history is highly specific for a disease with a single genetic etiology.

Gene-specific modifications:
Breast cancer is very common and has a high degree of genetic heterogeneity (caused by pathogenic variants in numerous genes). Use ONLY to capture combined LR towards pathogenicity, based on multifactorial likelihood clinical data.

PP4_Very Strong - LR>350:1
PP4_Strong - LR>18.7:1
PP4_Moderate - LR>4.3:1
PP4 - LR >2.08:1 
Combined LR 1.00-2.08 is not informative (PP4 not applicable).
See Specifications Table7 and Appendix B for details.

Instructions:
Use in the context of clinically calibrated evidence types, with sufficient detail to review data sources, types and weights. Published data points may include co-segregation with disease, co-occurrence with a pathogenic variant in the same gene, reported family history, breast tumor pathology, and case-control data. Can also apply for unpublished data, where there is no appropriate ACMG/AMP code. Assign weight based on combined LR for clinical data.
See Specifications Table7 for example application.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "PP5", 
"ACMG summary:
Reputable source recently reports variant as pathogenic, but the evidence is not available to the laboratory to perform an independent evaluation.
Not Applicable
This criterion is not for use as recommended by the ClinGen Sequence Variant Interpretation VCEP Review Committee. 
",
0
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "BA1", 
"ACMG summary:
Allele frequency is above 5% in Exome Sequencing Project, 1000 Genomes or Exome Aggregation Consortium.

Gene-specific modifications:
Filter allele frequency (FAF) is above 0.1% (FAF > 0.001) in gnomAD v2.1 (non-cancer, exome only subset) and/or gnomAD v3.1 (non-cancer), non-founder population(s). See Appendix G for details.

Instructions:
Apply based on maximum filter allele frequency observed in a gnomAD non-founder population, considering exome and genome data separately.
Do not apply if read depth <20. Do not apply to well-established pathogenic founder variants.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "BS1", 
"ACMG summary:
Allele frequency is greater than expected for disorder.

Strong:
Filter allele frequency (FAF) is above 0.01% (FAF > 0.0001) in gnomAD v2.1 (non-cancer, exome only subset) and/or gnomAD v3.1 (non-cancer), non-founder population(s). See Appendix G for details.

Supporting:
Filter allele frequency (FAF) is above 0.002% (FAF > 0.00002) and less than or equal to 0.01% (FAF ≤ 0.0001) in gnomAD v2.1 (non-cancer, exome only subset) and/or gnomAD v3.1 (non-cancer), non-founder population(s). See Appendix G for details.

Instructions:
Apply based on maximum filter allele frequency in a gnomAD non-founder population, considering exome and genome data separately.
Do not apply if read depth <20. Do not apply to well-established pathogenic founder variants.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "BS2", 
"ACMG summary:
Observed in a healthy adult individual for a recessive (homozygous), dominant (heterozygous), or X-linked (hemizygous) disorder, with full penetrance expected at an early age.

Gene-specific modifications:
Applied in absence of features of recessive disease, namely Fanconi Anemia phenotype. See Specifications Table 8 for additional stipulations, and approach to assign points per proband, and final BS2 code assignment based on the sum of BS2-related points. See Appendix H for additional details.

BS2 = ≥ 4 points
BS2_Moderate = 2 points
BS2_Supporting = 1 points

Instructions:
Co-occurrent P or LP variant should be assigned classification using VCEP specifications. 
See Specifications Table 8 for approach to assign points per proband, and final BS2 code assignment based on the sum of BS2-related points.
Also see Specifications Table 8 for additional stipulations.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "BS3", 
"ACMG summary:
Well-established in vitro or in vivo functional studies show no damaging effect on protein function or splicing.

Gene-specific modifications:
Well-established in vitro or in vivo functional studies shows no damaging effect on protein function. Assay measures effect via protein only OR mRNA and protein combined. See Specifications Table 9 for code recommendations from calibrated published assays. Also see Figure1C and Appendix E for details.
Well-established in vitro or in vivo functional studies supportive of no damaging effect as measured by effect on mRNA transcript profile (mRNA assay only). Apply as BP7 (RNA) at appropriate strength. See Specifications Figure1B and Appendix E for details.

Instructions:
See Specifications Figure 1C for simplified flowchart/s to advise application of codes for functional data, in content of variant type and location within a (potentially) clinically important functional domain. Do not apply when conflicting results are present from well-established assays with sufficient controls, which cannot be explained by experimental design.
See Specifications Figure 1B for process to apply codes for splicing data, in content of location and predicted bioinformatic impact of the variant, and adaptive weighting according to assay methodology and proportion of functional transcript retained.
See Specifications Table 9, provided as a separate file in excel format to facilitate searches and look-ups by variant c. and p. nomenclature. It includes PS3 and BS3 code recommendations and rationale for code application of published functional assays data that has been calibrated, and considered against predicted/reported splicing.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "BS4", 
"ACMG summary:
Lack of segregation in affected members of a family.
Caveat: The presence of phenocopies for common phenotypes (i.e. cancer, epilepsy) can mimic lack of segregation among affected individuals. Also, families may have more than one pathogenic variant contributing to an autosomal dominant disorder, further confounding an apparent lack of segregation.

Gene-specific modifications:
Lack of segregation in affected members of a family, as measured by a quantitative co-segregation analysis method. See Appendix I for details.

Apply weight as per Bayes Score:
BS4_VeryStrong - LR <0.00285:1
BS4 - LR <0.05:1
BS4_Moderate - LR <0.23:1
BS4_Supporting  - LR 0.23-0.48:1

Instructions:
Recommend use of online tool: https://fengbj-laboratory.org/cool3/analysis.html 
Additional information, including pedigree formatting, is available at: https://fengbj-laboratory.org/cool3/manual.html.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "BP1", 
"ACMG summary:
Missense variant in a gene for which primarily truncating variants are known to cause disease.

Gene-specific modifications:
Apply BP1_Strong for silent substitution, missense or in-frame insertion, deletion or delins variants outside a (potentially) clinically important functional domain AND no splicing predicted (SpliceAI ≤0.1). As justified in the appendices, (potentially) clinically important functional domains are defined as: BRCA1 RING aa 2-101; BRCA1 coiled-coil aa 1391-1424; BRCA1 BRCT repeats aa 1650-1857. See Specifications Figure1A and Appendix J for details.

Instructions:
See Specifications Figure 1A for process to apply codes according to variant type, location and predicted bioinformatic impact. Missense prediction not applicable.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "BP2", 
"ACMG summary:
Observed in trans with a pathogenic variant for a fully penetrant dominant gene/disorder or observed in cis with a pathogenic variant in any inheritance pattern.
Not Applicable
Comments: Applied only in the context of BS2.
",
0
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "BP3", 
"ACMG summary:
In frame-deletions/insertions in a repetitive region without a known function.
Not Applicable
Comments: Captured by bioinformatic tool prediction, and domain analysis. See Appendix J for details
",
0
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "BP4", 
"ACMG summary:
Multiple lines of computational evidence suggest no impact on gene or gene product (conservation, evolutionary, splicing impact, etc)
Caveat: As many in silico algorithms use the same or very similar input for their predictions, each algorithm cannot be counted as an independent criterion. BP4 can be used only once in any evaluation of a variant.

Gene-specific modifications:
Missense or in-frame insertion, deletion or delins variants inside a (potentially) clinically important functional domain, and no predicted impact via protein change or splicing (BayesDel no-AF score ≤ 0.15 AND SpliceAI ≤0.1).
Silent variant inside a (potentially) clinically important functional domain, if no predicted impact via splicing (SpliceAI ≤0.1).
Intronic variants outside of the native donor and acceptor splice sites (i.e. not +/- 1,2 positions) AND no predicted impact via splicing (SpliceAI ≤0.1).
As justified in the appendices, (potentially) clinically important functional domains are defined as: BRCA1 RING aa 2-101; BRCA1 coiled-coil aa 1391-1424; BRCA1 BRCT repeats aa 1650-1857. See Specifications Figure1A and Appendix J for details.

Instructions:
See Specifications Figure 1A for process to apply codes according to variant type, location and predicted bioinformatic impact.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "BP5", 
"ACMG summary:
Variant found in a case with an alternate molecular basis for disease.

Gene-specific modifications:
Use ONLY to capture combined LR against pathogenicity, based on multifactorial likelihood clinical data.

BP5_VeryStrong - LR <0.00285:1
BP5_Strong  - LR <0.05:1
BP5_Moderate - LR <0.23:1
BP5 - LR 0.23-0.48:1

Not applicable for co-observation: cases with pathogenic variants in two (or more) different known breast-ovarian cancer risk genes have no specific phenotype.

Instructions:
Use in the context of clinically calibrated evidence types, with sufficient detail to review data sources, types and weights. Published data points may include co-segregation with disease, co-occurrence with a pathogenic variant in the same gene, reported family history, breast tumor pathology, and case-control data. Can also apply for unpublished data, where there is no appropriate ACMG/AMP code. Assign weight based on combined LR for clinical data.
See Specifications Table7 for example application.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "BP6", 
"ACMG summary:
Reputable source recently reports variant as benign, but the evidence is not available to the laboratory to perform an independent evaluation.
Not Applicable
This criterion is not for use as recommended by the ClinGen Sequence Variant Interpretation VCEP Review Committee. 
",
0
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
7, "BP7", 
"ACMG summary:
A synonymous variant for which splicing prediction algorithms predict no impact to the splice consensus sequence nor the creation of a new splice site AND the nucleotide is not highly conserved.

Strong:
Well-established in vitro or in vivo functional studies shows no damaging effect on protein function as measured by effect on mRNA transcript profile - mRNA assay only. Apply as BP7 (RNA) for intronic and silent variants, as well as missense/in-frame variants located outside a (potentially) clinically important functional domain. See Specifications Figure1B and Appendix E for details.
As justified in the appendices, (potentially) clinically important functional domains are defined as: BRCA1 RING aa 2-101; BRCA1 coiled-coil aa 1391-1424; BRCA1 BRCT repeats aa 1650-1857. See Specifications Figure1A and Appendix J for details.

Supporting:
Silent variant inside a (potentially) clinically important functional domain, IF BP4 met.
Intronic variants located outside conserved donor or acceptor motif positions (at or beyond positions +7/-21) IF BP4 met.
See Specifications Figure1A and Appendix J for additional details.
As justified in the appendices, (potentially) clinically important functional domains are defined as: BRCA1 RING aa 2-101; BRCA1 coiled-coil aa 1391-1424; BRCA1 BRCT repeats aa 1650-1857. See Specifications Figure1A and Appendix J for details.

Instructions:
See Specifications Figure 1B for process to apply codes for splicing data, in content of location and predicted bioinformatic impact of the variant, and adaptive weighting according to assay methodology and proportion of functional transcript retained. Not applicable for missense variants inside a (potentially) clinically important functional domain as they may still impact protein function through the amino acid change.
Following convention, this code is applied in addition to BP4 (no splicing prediction, Splice AI ≤0.1) to capture the low prior probability of pathogenicity of silent variants. Nucleotide conservation is not considered relevant. See Specifications Figure 1A for process to apply codes according to variant type, location and predicted bioinformatic impact.
",
1
);





INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('152', 'pvs', 'very strong pathogenic', '1');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('152', 'ps', 'strong pathogenic', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('152', 'pm', 'medium pathogenic', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('152', 'pp', 'supporting pathogenic', '0');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('153', 'ps', 'strong pathogenic', '1');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('153', 'pm', 'medium pathogenic', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('153', 'pp', 'supporting pathogenic', '0');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('154', 'ps', 'strong pathogenic', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('155', 'ps', 'strong pathogenic', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('156', 'ps', 'strong pathogenic', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('157', 'pm', 'medium pathogenic', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('158', 'pp', 'supporting pathogenic', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('159', 'ps', 'strong pathogenic', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('159', 'pm', 'medium pathogenic', '1');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('159', 'pp', 'supporting pathogenic', '0');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('160', 'pm', 'medium pathogenic', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('161', 'pvs', 'very strong pathogenic', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('161', 'ps', 'strong pathogenic', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('161', 'pm', 'medium pathogenic', '1');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('161', 'pp', 'supporting pathogenic', '0');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('162', 'pm', 'medium pathogenic', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('163', 'pp', 'supporting pathogenic', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('164', 'pvs', 'very strong pathogenic', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('164', 'ps', 'strong pathogenic', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('164', 'pm', 'medium pathogenic', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('164', 'pp', 'supporting pathogenic', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('165', 'pp', 'supporting pathogenic', '1');


INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('166', 'ps', 'strong pathogenic', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('166', 'pm', 'medium pathogenic', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('166', 'pp', 'supporting pathogenic', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('167', 'bp', 'supporting pathogenic', '1');



INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('169', 'ba', 'stand-alone benign', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('170', 'bs', 'strong benign', '1');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('170', 'bp', 'supporting benign', '0');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('171', 'bs', 'strong benign', '1');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('171', 'bm', 'medium benign', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('171', 'bp', 'supporting benign', '0');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('172', 'bs', 'strong benign', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('173', 'bs', 'strong benign', '1');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('173', 'bm', 'medium benign', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('173', 'bp', 'supporting benign', '0');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('174', 'bs', 'strong benign', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('175', 'bp', 'supporting benign', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('176', 'bp', 'supporting benign', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('177', 'bp', 'supporting benign', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('178', 'bs', 'strong benign', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('178', 'bm', 'medium benign', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('178', 'bp', 'supporting benign', '1');


INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('179', 'bp', 'supporting benign', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('180', 'bs', 'strong benign', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('180', 'bp', 'supporting benign', '1');




















INSERT INTO `HerediVar_ahdoebm1`.`classification_scheme` (`name`, `display_name`, `type`, `reference`) VALUES ('enigma-brca2', 'ClinGen ENIGMA BRCA2', 'acmg-enigma-brca2', 'https://cspec.genome.network/cspec/ui/svi/doc/GN097');



INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "PVS1", 
"ACMG summary:
Null variant (nonsense, frameshift, canonical +/-1 or 2 splice sites, initiation codon, single or multi-exon deletion) in a gene where loss of function (LOF) is a known mechanism of disease.
Caveats:
 - Beware of genes where LOF is not a known disease mechanism (e.g. GFAP, MYH7).
 - Use caution interpreting LOF variants at the extreme 3' end of a gene.
 - Use caution with splice variants that are predicted to lead to exon skipping but leave the remainder of the protein intact.
 - Use caution in the presence of multiple transcripts.

Gene-specific modifications:
Null variant (nonsense, frameshift, splice site (donor/acceptor +/-1,2), initiation codon, single or multi-exon deletion) in a gene where loss of function (LOF) is a known mechanism of disease. Apply at appropriate strength according to PVS1 flowchart, which considers knowledge of clinically important functional domains. See Specifications Table 4 and Appendix D for details.
Well-established in vitro or in vivo functional studies supportive of a damaging effect as measured by effect on mRNA transcript profile (mRNA assay only). Apply as PVS1 (RNA) at appropriate strength. See Specifications Figure1B and Appendix E for details.

Instructions:
In alignment with SVI recommendations for PVS1 code application, evidence strength and description has been separated for different variant types.  Apply according to PVS1 flowchart, which considers knowledge of clinically important functional domains. For predicted protein termination codon (PTC) variants, apply with exon-specific weights derived for the PM5_PTC code (See Appendix D for details).
See Specifications Table 4, provided as a separate searchable excel file, for a comprehensive summary of codes applicable for all variants considered against the BRCA1 and BRCA2 PVS1 decision trees (initiation, nonsense/frameshift, deletion, duplication, splice site (donor/acceptor ±1,2)) – organized by exon. See Appendix Figure 5,6 and Table 5 for further justification.
See Specifications Figure 1B for process to apply codes for splicing data, in content of location and predicted bioinformatic impact of the variant, and adaptive weighting according to assay methodology and proportion of functional transcript retained.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "PS1", 
"ACMG summary:
Same amino acid change as a previously established pathogenic variant regardless of nucleotide change.
Example: Val->Leu caused by either G>C or G>T in the same codon.
Caveat: Beware of changes that impact splicing rather than at the amino acid/protein level.

Strong:
Apply PS1, for predicted missense substitutions, where a previously classified pathogenic variant is considered to act via protein change (no confirmed or predicted effect on mRNA splicing (SpliceAI≤0.1)).
Apply PS1, for exonic and intronic variants with same predicted impact on splicing, as a previously classified pathogenic variant. Vary weight depending on relative positions, and confidence in classification of the reference variant. 
See Specifications Table 5 and Appendix E, J and K for details.

Moderate:
Apply PS1_Moderate, for predicted missense substitutions, where a previously classified likely pathogenic variant is considered to act via protein change (no confirmed or predicted effect on mRNA splicing (SpliceAI≤0.1)).
Apply PS1_Moderate, for exonic and intronic variants with same predicted impact on splicing, as a previously classified (likely) pathogenic variant. Vary weight depending on relative positions, and confidence in classification of the reference variant.
See Specifications Table 5 and Appendix E, J and K for details.

Supporting:
Apply PS1, for exonic and intronic variants with same predicted impact on splicing, as a previously classified (likely) pathogenic variant. Vary weight depending on relative positions, and confidence in classification of the reference variant.
See Specifications Table 5 and Appendix E, J and K for details.


Instructions:
For both missense and splicing scenarios, (Likely) Pathogenic variant classification should be assigned using VCEP specifications.
For application of PS1 for splicing predictions, see Specifications Table 5. The predicted event of the VUA must precisely match the predicted event of the known (likely) pathogenic variant (e.g. both predicted to lead to exon A skipping, or both to enhanced use of cryptic site B), AND the strength of the prediction for the VUA must be of similar or higher strength than the strength of the prediction for the known (likely) pathogenic variant. For an exonic variant, predicted or proven functional effect of missense substitution/s encoded by the variant and the established pathogenic variant should also be considered before PS1 code application for splicing prediction.
",
1
);


INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "PS2", 
"ACMG summary:
De novo (both maternity and paternity confirmed) in a patient with the disease and no family history.
Note: Confirmation of paternity only is insufficient. Egg donation, surrogate motherhood, errors in embryo transfer, etc. can contribute to non-maternity.
Not Applicable
Comments: BRCA1/2-related cancers occur relatively commonly. No information to calibrate the predictive capacity of de novo occurrences.
",
0
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "PS3", 
"ACMG summary:
Well-established in vitro or in vivo functional studies supportive of a damaging effect on the gene or gene product.
Note: Functional studies that have been validated and shown to be reproducible and robust in a clinical diagnostic laboratory setting are considered the most well-established.

Gene-specific modifications:
Well-established in vitro or in vivo functional studies supportive of a damaging effect. Apply PS3 for assays measuring effect via protein only OR mRNA and protein combined. See Specifications Table 9 for code recommendations from calibrated published assays. Also see Figure1C and Appendix E for details.
Well-established in vitro or in vivo functional studies supportive of a damaging effect as measured by effect on mRNA transcript profile (mRNA assay only). Apply as PVS1 (RNA) at appropriate strength. See Specifications Figure1B and Appendix E for details.

Instructions:
See Specifications Figure 1C for simplified flowchart/s to advise application of codes for functional data, in content of variant type and location within a (potentially) clinically important functional domain. Do not apply when conflicting results are present from well-established assays with sufficient controls, which cannot be explained by experimental design.
See Specifications Figure 1B for process to apply codes for splicing data, in content of location and predicted bioinformatic impact of the variant, and adaptive weighting according to assay methodology and proportion of functional transcript retained.
See Specifications Table 9, provided as a separate file in excel format to facilitate searches and look-ups by variant c. and p. nomenclature. It includes PS3 and BS3 code recommendations and rationale for code application of published functional assays data that has been calibrated, and considered against predicted/reported splicing.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "PS4", 
"ACMG summary:
The prevalence of the variant in affected individuals is significantly increased compared to the prevalence in controls.
Note 1: Relative risk (RR) or odds ratio (OR), as obtained from case-control studies, is >5.0 and the confidence interval around the estimate of RR or OR does not include 1.0. See manuscript for detailed guidance.
Note 2: In instances of very rare variants where case-control studies may not reach statistical significance, the prior observation of the variant in multiple unrelated patients with the same phenotype, and its absence in controls, may be used as moderate level of evidence.

Gene-specific modifications:
The prevalence of the variant in affected individuals is significantly increased compared to the prevalence in controls. Case-control studies; p-value ≤0.05 and OR ≥4 (lower confidence interval excludes 2.0). See Appendix F for details.

Instructions:
Case dataset should be ethnicity and country-matched to control dataset. If case-control LR estimates are available for a given dataset, these should be used in preference to case-control OR data, under code PP4 (or BP5, if appropriate). Do not use Proband Counting as originally described.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "PM1", 
"ACMG summary:
Located in a mutational hot spot and/or critical and well-established functional domain (e.g. active site of an enzyme) without benign variation.
Not Applicable
Comments: Considered as component of bioinformatic analysis (PP3/BP4).
",
0
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "PM2", 
"ACMG summary:
Absent from controls (or at extremely low frequency if recessive) in Exome Sequencing Project, 1000 Genomes or Exome Aggregation Consortium.
Caveat: Population data for indels may be poorly called by next generation sequencing.

Gene-specific modifications:
Absent from controls in an outbred population, from gnomAD v2.1 (non-cancer, exome only subset) and gnomAD v3.1 (non-cancer). Region around the variant must have an average read depth ≥25. See Appendix G for details.

Instructions:
Observation of a variant only once in a gnomAD outbred population is not informative. Do not apply for insertion, deletion or delins variants. Do not apply if read depth <25 at region around the variant.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "PM3", 
"ACMG summary:
For recessive disorders, detected in trans with a pathogenic variant
Note: This requires testing of parents (or offspring) to determine phase.

Strong:
Apply for patient with phenotype consistent with BRCA1- or BRCA2-related Fanconi Anemia (FA), and co-occurrent variants in the same gene. Phenotype is considered consistent with BRCA1- or BRCA2-related FA if:
(i) Increased chromosome breakage (DEB, MMC, or spontaneous) and at least one clinical feature indicative of BRCA1/2-related FA, categorized under: physical features, pathology and laboratory findings, cancer diagnosis ≤5yr.
(ii) Result unknown for chromosome breakage, and at least two clinical features indicative of BRCA1/2-related FA under at least two of the three categories: physical features, pathology and laboratory findings, cancer diagnosis ≤5yr.
See Specifications Table 6 for approach to assign points per proband, and final PM3 code assignment based on the sum of PM3-related points. Also see Appendix H for additional details.
PM3_Strong = ≥4 points

Moderate:
Apply for patient with phenotype consistent with BRCA1- or BRCA2-related Fanconi Anemia (FA), and co-occurrent variants in the same gene. Phenotype is considered consistent with BRCA1- or BRCA2-related FA if:
(i) Increased chromosome breakage (DEB, MMC, or spontaneous) and at least one clinical feature indicative of BRCA1/2-related FA, categorized under: physical features, pathology and laboratory findings, cancer diagnosis ≤5yr.
(ii) Result unknown for chromosome breakage, and at least two clinical features indicative of BRCA1/2-related FA under at least two of the three categories: physical features, pathology and laboratory findings, cancer diagnosis ≤5yr.
See Specifications Table 6 for approach to assign points per proband, and final PM3 code assignment based on the sum of PM3-related points. Also see Appendix H for additional details.
PM3 = 2 points

Supporting:
Apply for patient with phenotype consistent with BRCA1- or BRCA2-related Fanconi Anemia (FA), and co-occurrent variants in the same gene.Phenotype is considered consistent with BRCA1- or BRCA2-related FA if:
(i) Increased chromosome breakage (DEB, MMC, or spontaneous) and at least one clinical feature indicative of BRCA1/2-related FA, categorized under: physical features, pathology and laboratory findings, cancer diagnosis ≤5yr.
(ii) Result unknown for chromosome breakage, and at least two clinical features indicative of BRCA1/2-related FA under at least two of the three categories: physical features, pathology and laboratory findings, cancer diagnosis ≤5yr.
See Specifications Table 6 for approach to assign points per proband, and final PM3 code assignment based on the sum of PM3-related points. Also see Appendix H for additional details.
PM3_Supporting = 1 point

Instructions:
Co-occurrent P or LP variant should be assigned classification using VCEP specifications. 
Variant under assessment must be sufficiently rare (meet PM2_Supporting, or PM2 not applicable).
See Specifications Table 6 for approach to assign points per proband, and final PM3 code assignment based on the sum of PM3-related points.
For related individuals score only most severe presentation.
Also see Specifications Table 6 for additional stipulations
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "PM4", 
"ACMG summary:
Protein length changes due to in-frame deletions/insertions in a non-repeat region or stop-loss variants.
Not Applicable
Comments: Considered as component of bioinformatic analysis (PP3/BP4).
",
0
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "PM5", 
"ACMG summary:
Novel missense change at an amino acid residue where a different missense change determined to be pathogenic has been seen before.
Example: Arg156His is pathogenic; now you observe Arg156Cys.
Caveat: Beware of changes that impact splicing rather than at the amino acid/protein level.

Gene-specific modifications:
Protein termination codon (PTC) variant in an exon where a different proven pathogenic PTC variant has been seen before. Use to justify additional weight for PTC variants annotated as PVS1. See Specifications Table 4 for PM5_PTC code strengths applicable per exon. See Appendix D for additional details.

Instructions:
Only applied to genomic PTC changes (not splicing). Weight determined by exon where the termination codon occurs (may not be the same exon as the variant position). See Specifications Table 4, provided as a separate searchable excel file, for PM5_PTC codes applicable for predicted termination codon variants - organized by exon.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "PM6", 
"ACMG summary:
Assumed de novo, but without confirmation of paternity and maternity.
Not Applicable
Comments: BRCA1/2-related cancers occur relatively commonly. No information to calibrate the predictive capacity of de novo occurrences.
",
0
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "PP1", 
"ACMG summary:
Co-segregation with disease in multiple affected family members in a gene definitively known to cause the disease.
Note: May be used as stronger evidence with increasing segregation data.

Gene-specific modifications
Co-segregation with disease in multiple affected family members in a gene definitively known to cause the disease, as measured by a quantitative co-segregation analysis method. See Appendix I for details.
Apply weight as per Bayes Score:
PP1_Very Strong - LR>350:1
PP1_Strong - LR>18.7:1
PP1_Moderate - LR>4.3:1
PP1 - LR >2.08:1

Instructions:
Recommend use of online tool: https://fengbj-laboratory.org/cool3/analysis.html 
Additional information, including pedigree formatting, is available at: https://fengbj-laboratory.org/cool3/manual.html.
Stipulation: to apply code as Pathogenic Very Strong, VUS should have bioinformatically predicted (or experimentally proven) effect on protein or mRNA splicing. If co-segregation score is from a single family, or several families from an isolated population, assess the possibility of a different causative pathogenic variant.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "PP2", 
"ACMG summary:
Missense variant in a gene that has a low rate of benign missense variation and where missense variants are a common mechanism of disease.
Not Applicable
Comments: High frequency of benign missense variants.
",
0
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "PP3", 
"ACMG summary:
Multiple lines of computational evidence support a deleterious effect on the gene or gene product (conservation, evolutionary, splicing impact, etc.).
Caveat: As many in silico algorithms use the same or very similar input for their predictions, each algorithm should not be counted as an independent criterion. PP3 can be used only once in any evaluation of a variant.

Gene-specific modifications:
Apply PP3 for missense or in-frame insertion, deletion or delins variants inside a (potentially) clinically important functional domain and predicted impact via protein change (BayesDel no-AF score ≥0.30). As justified in the appendices, (potentially) clinically important functional domains are defined as: BRCA2 PALB2 binding domain aa 10-40; BRCA2 DNA binding aa 2481-3186.
Apply PP3 for predicted splicing (SpliceAI ≥0.2) for silent, missense/in-frame (irrespective of location in clinically important functional domain) and for intronic variants outside of donor and acceptor 1,2 sites.
See Specifications Figure1A and Appendix J for details.

Instructions:
See Specifications Figure 1A for process to apply codes according to variant type, location and predicted bioinformatic impact.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "PP4", 
"ACMG summary:
Patient's phenotype or family history is highly specific for a disease with a single genetic etiology.

Gene-specific modifications:
Breast cancer is very common and has a high degree of genetic heterogeneity (caused by pathogenic variants in numerous genes). Use ONLY to capture combined LR towards pathogenicity, based on multifactorial likelihood clinical data.

PP4_Strong - LR>18.7:1
PP4_Very Strong - LR>350:1
PP4_Moderate - LR>4.3:1
PP4 - LR >2.08:1

Combined LR 1.00-2.08 is not informative (PP4 not applicable).
See Specifications Table7 and Appendix B for details.

Instructions:
Use in the context of clinically calibrated evidence types, with sufficient detail to review data sources, types and weights. Published data points may include co-segregation with disease, co-occurrence with a pathogenic variant in the same gene, reported family history, breast tumor pathology, and case-control data. Can also apply for unpublished data, where there is no appropriate ACMG/AMP code. Assign weight based on combined LR for clinical data.
See Specifications Table7 for example application.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "PP5", 
"ACMG summary:
Reputable source recently reports variant as pathogenic, but the evidence is not available to the laboratory to perform an independent evaluation.
Not Applicable
This criterion is not for use as recommended by the ClinGen Sequence Variant Interpretation VCEP Review Committee. 
",
0
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "BA1", 
"ACMG summary:
Allele frequency is above 5% in Exome Sequencing Project, 1000 Genomes or Exome Aggregation Consortium.

Gene-specific modifications:
Filter allele frequency (FAF) is above 0.1% (FAF > 0.001) in gnomAD v2.1 (non-cancer, exome only subset) and/or gnomAD v3.1 (non-cancer), non-founder population(s). See Appendix G for details.

Instructions:
Apply based on maximum filter allele frequency observed in a gnomAD non-founder population, considering exome and genome data separately.
Do not apply if read depth <20. Do not apply to well-established pathogenic founder variants.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "BS1", 
"ACMG summary:
Allele frequency is greater than expected for disorder.

Strong:
Filter allele frequency (FAF) is above 0.01% (FAF > 0.0001) in gnomAD v2.1 (non-cancer, exome only subset) and/or gnomAD v3.1 (non-cancer), non-founder population(s). See Appendix G for details.

Supporting
Filter allele frequency (FAF) is above 0.002% (FAF > 0.00002) and less than or equal to 0.01% (FAF ≤ 0.0001) in gnomAD v2.1 (non-cancer, exome only subset) and/or gnomAD v3.1 (non-cancer), non-founder population(s). See Appendix G for details.

Instructions:
Apply based on maximum filter allele frequency in a gnomAD non-founder population, considering exome and genome data separately.
Do not apply if read depth <20. Do not apply to well-established pathogenic founder variants.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "BS2", 
"ACMG summary:
Observed in a healthy adult individual for a recessive (homozygous), dominant (heterozygous), or X-linked (hemizygous) disorder, with full penetrance expected at an early age.

Gene-specific modifications:
Applied in absence of features of recessive disease, namely Fanconi Anemia phenotype. See Specifications Table 8 for additional stipulations, and approach to assign points per proband, and final BS2 code assignment based on the sum of BS2-related points. See Appendix H for additional details.
BS2 = ≥ 4 points
BS2_Moderate = 2 points
BS2_Supporting = 1 points

Instructions:
Co-occurrent P or LP variant should be assigned classification using VCEP specifications. 
See Specifications Table 8 for approach to assign points per proband, and final BS2 code assignment based on the sum of BS2-related points.
Also see Specifications Table 8 for additional stipulations.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "BS3", 
"ACMG summary:
Well-established in vitro or in vivo functional studies show no damaging effect on protein function or splicing.

Gene-specific modifications:
Well-established in vitro or in vivo functional studies shows no damaging effect on protein function. Assay measures effect via protein only OR mRNA and protein combined. See Specifications Table 9 for code recommendations from calibrated published assays. Also see Figure1C and Appendix E for details.
Well-established in vitro or in vivo functional studies supportive of no damaging effect as measured by effect on mRNA transcript profile (mRNA assay only). Apply as BP7 (RNA) at appropriate strength. See Specifications Figure1B and Appendix E for details.

Instructions:
See Specifications Figure 1C for simplified flowchart/s to advise application of codes for functional data, in content of variant type and location within a (potentially) clinically important functional domain. Do not apply when conflicting results are present from well-established assays with sufficient controls, which cannot be explained by experimental design.
See Specifications Figure 1B for process to apply codes for splicing data, in content of location and predicted bioinformatic impact of the variant, and adaptive weighting according to assay methodology and proportion of functional transcript retained.
See Specifications Table 9, provided as a separate file in excel format to facilitate searches and look-ups by variant c. and p. nomenclature. It includes PS3 and BS3 code recommendations and rationale for code application of published functional assays data that has been calibrated, and considered against predicted/reported splicing.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "BS4", 
"ACMG summary:
Lack of segregation in affected members of a family.
Caveat: The presence of phenocopies for common phenotypes (i.e. cancer, epilepsy) can mimic lack of segregation among affected individuals. Also, families may have more than one pathogenic variant contributing to an autosomal dominant disorder, further confounding an apparent lack of segregation.

Gene-specific modifications:
Lack of segregation in affected members of a family, as measured by a quantitative co-segregation analysis method. See Appendix I for details.

Apply weight as per Bayes Score:
BS4_VeryStrong - LR <0.00285:1
BS4 - LR <0.05:1
BS4_Moderate - LR <0.23:1
BS4_Supporting  - LR 0.23-0.48:1

Instructions:
Recommend use of online tool: https://fengbj-laboratory.org/cool3/analysis.html 
Additional information, including pedigree formatting, is available at: https://fengbj-laboratory.org/cool3/manual.html.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "BP1", 
"ACMG summary:
Missense variant in a gene for which primarily truncating variants are known to cause disease.

Gene-specific modifications
Apply BP1_Strong for silent substitution, missense or in-frame insertion, deletion or delins variants outside a (potentially) clinically important functional domain AND no splicing predicted (SpliceAI ≤0.1). As justified in the appendices, (potentially) clinically important functional domains are defined as: BRCA2 PALB2 binding domain aa 10-40; BRCA2 DNA binding aa 2481-3186. See Specifications Figure1A and Appendix J for details.

Instructions:
See Specifications Figure 1A for process to apply codes according to variant type, location and predicted bioinformatic impact. Missense prediction not applicable.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "BP2", 
"ACMG summary:
Observed in trans with a pathogenic variant for a fully penetrant dominant gene/disorder or observed in cis with a pathogenic variant in any inheritance pattern.
Not Applicable
Comments: Applied only in the context of BS2.
",
0
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "BP3", 
"ACMG summary:
In frame-deletions/insertions in a repetitive region without a known function.
Not Applicable
Comments: Captured by bioinformatic tool prediction, and domain analysis. See Appendix J for details
",
0
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "BP4", 
"ACMG summary:
Multiple lines of computational evidence suggest no impact on gene or gene product (conservation, evolutionary, splicing impact, etc)
Caveat: As many in silico algorithms use the same or very similar input for their predictions, each algorithm cannot be counted as an independent criterion. BP4 can be used only once in any evaluation of a variant.

Gene-specific modifications:
Missense or in-frame insertion, deletion or delins variants inside a (potentially) clinically important functional domain, and no predicted impact via protein change or splicing (BayesDel no-AF score ≤ 0.18 AND SpliceAI ≤0.1).
Silent variant inside a (potentially) clinically important functional domain, if no predicted impact via splicing (SpliceAI ≤0.1).
Intronic variants outside of the native donor and acceptor splice sites (i.e. not +/- 1,2 positions) AND no predicted impact via splicing (SpliceAI ≤0.1).
As justified in the appendices, (potentially) clinically important functional domains are defined as: BRCA2 PALB2 binding domain aa 10-40; BRCA2 DNA binding aa 2481-3186. See Specifications Figure1A and Appendix J for details.

Instructions:
See Specifications Figure 1A for process to apply codes according to variant type, location and predicted bioinformatic impact.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "BP5", 
"ACMG summary:
Variant found in a case with an alternate molecular basis for disease.

Strong
Use ONLY to capture combined LR against pathogenicity, based on multifactorial likelihood clinical data.

BP5_VeryStrong - LR <0.00285:1
BP5_Strong  - LR <0.05:1
BP5_Moderate - LR <0.23:1
BP5 - LR 0.23-0.48:1

Not applicable for co-observation: cases with pathogenic variants in two (or more) different known breast-ovarian cancer risk genes have no specific phenotype.

Instructions:
Use in the context of clinically calibrated evidence types, with sufficient detail to review data sources, types and weights. Published data points may include co-segregation with disease, co-occurrence with a pathogenic variant in the same gene, reported family history, breast tumor pathology, and case-control data. Can also apply for unpublished data, where there is no appropriate ACMG/AMP code. Assign weight based on combined LR for clinical data.
See Specifications Table7 for example application.
",
1
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "BP6", 
"ACMG summary:
Reputable source recently reports variant as benign, but the evidence is not available to the laboratory to perform an independent evaluation.
Not Applicable
This criterion is not for use as recommended by the ClinGen Sequence Variant Interpretation VCEP Review Committee. 
",
0
);
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium` (`classification_scheme_id`, `name`, `description`, `is_selectable`) VALUES (
8, "BP7", 
"ACMG summary:
A synonymous variant for which splicing prediction algorithms predict no impact to the splice consensus sequence nor the creation of a new splice site AND the nucleotide is not highly conserved.

Strong
Well-established in vitro or in vivo functional studies shows no damaging effect on protein function as measured by effect on mRNA transcript profile - mRNA assay only. Apply as BP7_Strong (RNA) for intronic and silent variants, as well as missense/in-frame variants located outside a (potentially) clinically important functional domain. See Specifications Figure1B and Appendix E for details.
As justified in the appendices, (potentially) clinically important functional domains are defined as: BRCA2 PALB2 binding domain aa 10-40; BRCA2 DNA binding aa 2481-3186. See Specifications Figure1A and Appendix J for details.

Supporting
Silent variant inside a (potentially) clinically important functional domain, IF BP4 met.
Intronic variants located outside conserved donor or acceptor motif positions (at or beyond positions +7/-21) IF BP4 met.
See Specifications Figure1A and Appendix J for additional details.
As justified in the appendices, (potentially) clinically important functional domains are defined as: BRCA2 PALB2 binding domain aa 10-40; BRCA2 DNA binding aa 2481-3186. See Specifications Figure1A and Appendix J for details.

Instructions:
See Specifications Figure 1B for process to apply codes for splicing data, in content of location and predicted bioinformatic impact of the variant, and adaptive weighting according to assay methodology and proportion of functional transcript retained. Not applicable for missense variants inside a (potentially) clinically important functional domain as they may still impact protein function through the amino acid change.
Following convention, this code is applied in addition to BP4 (no splicing prediction, Splice AI ≤0.1) to capture the low prior probability of pathogenicity of silent variants. Nucleotide conservation is not considered relevant. See Specifications Figure 1A for process to apply codes according to variant type, location and predicted bioinformatic impact.
",
1
);





INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('181', 'pvs', 'very strong pathogenic', '1');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('181', 'ps', 'strong pathogenic', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('181', 'pm', 'medium pathogenic', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('181', 'pp', 'supporting pathogenic', '0');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('182', 'ps', 'strong pathogenic', '1');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('182', 'pm', 'medium pathogenic', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('182', 'pp', 'supporting pathogenic', '0');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('183', 'ps', 'strong pathogenic', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('184', 'ps', 'strong pathogenic', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('185', 'ps', 'strong pathogenic', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('186', 'pm', 'medium pathogenic', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('187', 'pp', 'supporting pathogenic', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('188', 'ps', 'strong pathogenic', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('188', 'pm', 'medium pathogenic', '1');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('188', 'pp', 'supporting pathogenic', '0');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('189', 'pm', 'medium pathogenic', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('190', 'ps', 'strong pathogenic', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('190', 'pm', 'medium pathogenic', '1');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('190', 'pp', 'supporting pathogenic', '0');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('191', 'pm', 'medium pathogenic', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('192', 'ps', 'strong pathogenic', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('192', 'pm', 'medium pathogenic', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('192', 'pp', 'supporting pathogenic', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('193', 'pp', 'supporting pathogenic', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('194', 'pp', 'supporting pathogenic', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('195', 'ps', 'strong pathogenic', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('195', 'pm', 'medium pathogenic', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('195', 'pp', 'supporting pathogenic', '1');


INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('196', 'pp', 'supporting pathogenic', '1');






INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('197', 'ba', 'stand-alone benign', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('198', 'bs', 'strong benign', '1');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('198', 'bp', 'supporting benign', '0');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('199', 'bs', 'strong benign', '1');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('199', 'bm', 'medium benign', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('199', 'bp', 'supporting benign', '0');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('200', 'bs', 'strong benign', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('201', 'bs', 'strong benign', '1');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('201', 'bm', 'medium benign', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('201', 'bp', 'supporting benign', '0');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('202', 'bs', 'strong benign', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('203', 'bp', 'supporting benign', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('204', 'bp', 'supporting benign', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('205', 'bp', 'supporting benign', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('206', 'bs', 'strong benign', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('206', 'bm', 'medium benign', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('206', 'bp', 'supporting benign', '1');


INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('207', 'bp', 'supporting benign', '1');

INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('208', 'bs', 'strong benign', '0');
INSERT INTO `HerediVar_ahdoebm1`.`classification_criterium_strength` (`classification_criterium_id`, `name`, `description`, `is_default`) VALUES ('208', 'bp', 'supporting benign', '1');







INSERT INTO `HerediVar_ahdoebm1`.`mutually_exclusive_criteria` (`source`, `target`) VALUES ('152', '165');
INSERT INTO `HerediVar_ahdoebm1`.`mutually_exclusive_criteria` (`source`, `target`) VALUES ('165', '152');
INSERT INTO `HerediVar_ahdoebm1`.`mutually_exclusive_criteria` (`source`, `target`) VALUES ('181', '194');
INSERT INTO `HerediVar_ahdoebm1`.`mutually_exclusive_criteria` (`source`, `target`) VALUES ('194', '181');






ALTER TABLE `HerediVar_ahdoebm1`.`import_variant_queue` 
ADD INDEX `fk_import_variant_queue_import_queue_idx` (`import_queue_id` ASC);
;
ALTER TABLE `HerediVar_ahdoebm1`.`import_variant_queue` 
ADD CONSTRAINT `fk_import_variant_queue_import_queue`
  FOREIGN KEY (`import_queue_id`)
  REFERENCES `HerediVar_ahdoebm1`.`import_queue` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION;











CREATE TABLE `HerediVar_ahdoebm1`.`variant_heredicare_annotation` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `variant_id` INT UNSIGNED NOT NULL,
  `vid` VARCHAR(45) NOT NULL,
  `n_fam` INT NOT NULL DEFAULT 0 COMMENT 'consensus class: 1:pathogen, 2: vus, 3: polymorphismus/neutral, 11: class1, 12: class2, 32: class3-, 13: class3, 34: class3+, 14: class4, 15: class5, 20: artefakt, 21: nicht klassifiziert, 4: unbekannt',
  `n_pat` INT NOT NULL DEFAULT 0,
  `consensus_class` ENUM('1', '2', '3', '11', '12', '32', '13', '34', '14', '15', '20', '21', '4') NOT NULL,
  `comment` TEXT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC));

ALTER TABLE `HerediVar_ahdoebm1`.`variant_heredicare_annotation` 
ADD COLUMN `date` DATE NULL AFTER `comment`;


GRANT INSERT, DELETE ON HerediVar_ahdoebm1.variant_heredicare_annotation TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar_ahdoebm1.variant_heredicare_annotation TO 'HerediVar_annotation';
GRANT SELECT ON HerediVar_ahdoebm1.variant_heredicare_annotation TO 'HerediVar_superuser';
GRANT SELECT ON HerediVar_ahdoebm1.variant_heredicare_annotation TO 'HerediVar_read_only';
GRANT SELECT ON HerediVar_ahdoebm1.variant_ids TO 'HerediVar_annotation';




DELETE FROM `HerediVar_ahdoebm1`.`annotation_type` WHERE (`id` = '34');
DELETE FROM `HerediVar_ahdoebm1`.`annotation_type` WHERE (`id` = '35');

ALTER TABLE `HerediVar_ahdoebm1`.`import_queue` 
CHANGE COLUMN `status` `status` ENUM('pending', 'progress', 'success', 'error', 'retry') NOT NULL DEFAULT 'pending' ;



GRANT DELETE ON HerediVar_ahdoebm1.variant_ids TO 'HerediVar_superuser';


ALTER TABLE `HerediVar_ahdoebm1`.`variant_consequence` 
CHANGE COLUMN `exon_nr` `exon_nr` VARCHAR(45) NULL DEFAULT NULL ,
CHANGE COLUMN `intron_nr` `intron_nr` VARCHAR(45) NULL DEFAULT NULL ;


ALTER TABLE `HerediVar_ahdoebm1`.`import_variant_queue` 
DROP FOREIGN KEY `fk_import_variant_queue_import_queue`;
ALTER TABLE `HerediVar_ahdoebm1`.`import_variant_queue` 
CHANGE COLUMN `import_queue_id` `import_queue_id` INT(10) UNSIGNED NULL DEFAULT NULL ;
ALTER TABLE `HerediVar_ahdoebm1`.`import_variant_queue` 
ADD CONSTRAINT `fk_import_variant_queue_import_queue`
  FOREIGN KEY (`import_queue_id`)
  REFERENCES `HerediVar_ahdoebm1`.`import_queue` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION;


ALTER TABLE `HerediVar_ahdoebm1`.`consensus_classification` 
CHANGE COLUMN `classification` `classification` ENUM('1', '2', '3', '4', '5', '3+', '3-', 'M') NOT NULL ;

ALTER TABLE `HerediVar_ahdoebm1`.`user_classification` 
CHANGE COLUMN `classification` `classification` ENUM('1', '2', '3', '4', '5', '3-', '3+', 'M') NOT NULL ;


GRANT INSERT,UPDATE ON HerediVar_ahdoebm1.classification_scheme TO 'HerediVar_superuser';
GRANT INSERT,UPDATE,DELETE ON HerediVar_ahdoebm1.classification_criterium TO 'HerediVar_superuser';
GRANT INSERT,UPDATE,DELETE ON HerediVar_ahdoebm1.classification_criterium_strength TO 'HerediVar_superuser';
GRANT INSERT,UPDATE,DELETE ON HerediVar_ahdoebm1.mutually_exclusive_criteria TO 'HerediVar_superuser';


ALTER TABLE `HerediVar_ahdoebm1`.`classification_criterium_strength` 
CHANGE COLUMN `name` `name` VARCHAR(32) NOT NULL ,
ADD UNIQUE INDEX `UNIQUE_strength_key` (`classification_criterium_id` ASC, `name` ASC);
ALTER TABLE `HerediVar_ahdoebm1`.`mutually_exclusive_criteria` 
ADD UNIQUE INDEX `UNIQUE_mutually_exclusive` (`source` ASC, `target` ASC);


ALTER TABLE `HerediVar_ahdoebm1`.`classification_criterium` 
DROP INDEX `UNIQUE_scheme_id_name` ;

ALTER TABLE `HerediVar_ahdoebm1`.`classification_criterium` 
ADD UNIQUE INDEX `UNIQUE_classification_criterium` (`classification_scheme_id` ASC, `name` ASC);


ALTER TABLE `HerediVar_ahdoebm1`.`classification_criterium_strength` 
DROP FOREIGN KEY `FK_criterium_strength_classification_criterium`;
ALTER TABLE `HerediVar_ahdoebm1`.`classification_criterium_strength` 
ADD CONSTRAINT `FK_criterium_strength_classification_criterium`
  FOREIGN KEY (`classification_criterium_id`)
  REFERENCES `HerediVar_ahdoebm1`.`classification_criterium` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION;


ALTER TABLE `HerediVar_ahdoebm1`.`mutually_exclusive_criteria` 
DROP FOREIGN KEY `FK_mutually_exclusive_criteria_classification_criteria_1`,
DROP FOREIGN KEY `FK_mutually_exclusive_criteria_classification_criterium`;
ALTER TABLE `HerediVar_ahdoebm1`.`mutually_exclusive_criteria` 
ADD CONSTRAINT `FK_mutually_exclusive_criteria_classification_criteria_1`
  FOREIGN KEY (`source`)
  REFERENCES `HerediVar_ahdoebm1`.`classification_criterium` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION,
ADD CONSTRAINT `FK_mutually_exclusive_criteria_classification_criterium`
  FOREIGN KEY (`target`)
  REFERENCES `HerediVar_ahdoebm1`.`classification_criterium` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION;
