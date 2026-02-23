CREATE INDEX idx_cc_upload_recent_variant
ON consensus_classification (needs_heredicare_upload, is_recent, variant_id);

CREATE INDEX idx_phq_variant_requested_status
ON publish_heredicare_queue (variant_id, requested_at, status);

CREATE INDEX idx_variant_sv
ON variant (id, sv_variant_id);

CREATE INDEX idx_vc_variant_source_exon_intron
ON variant_consequence (variant_id, source, exon_nr, intron_nr);

CREATE INDEX idx_cc_clinvar_upload_recent_variant
ON consensus_classification (needs_clinvar_upload, is_recent, variant_id);

CREATE INDEX idx_pcq_variant_requested
ON publish_clinvar_queue (variant_id, requested_at);