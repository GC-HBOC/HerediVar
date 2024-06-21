

def prepare_variant(variant):
    result = {
        "id": variant.id,
        "chrom": variant.chrom,
        "pos": variant.pos,
        "ref": variant.ref,
        "alt": variant.alt,
        "variant_type": variant.variant_type,
        "hidden": variant.is_hidden
    }
    return result

def prepare_classification(classification):
    result = {
        "comment": classification.comment,
        "date": classification.date,
        "literature": classification.literature,
        "scheme": {"name": classification.scheme.display_name, "reference": classification.scheme.reference},
        "criteria": classification.scheme.criteria,
        "class_by_scheme": classification.scheme.selected_class,
        "selected_class": classification.selected_class,
        "classification_type": classification.type
    }
    return result