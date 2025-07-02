import json
import argparse
import os
from collections import defaultdict

def load_crate_manifest(filepath):
    """Load an RO-Crate manifest file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_validation_rules(filepath="validation_rules.json"):
    """Load validation rules from a JSON file."""
    if not os.path.exists(filepath):
        print(f"Validation rules file '{filepath}' not found.")
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_entity_counts(crate_json, composite_mode=False):
    """Extract counts of entities by their @type."""
    entity_counts = defaultdict(int)
    graph = crate_json.get('@graph', [])
    for entity in graph:
        types = entity.get('@type')
        if types:
            if isinstance(types, str):
                types = [types]
            if composite_mode:
                key = "+".join(sorted(types))
                entity_counts[key] += 1
            else:
                for t in types:
                    entity_counts[t] += 1
    return entity_counts

def compare_entity_shapes(ref_counts, test_counts, expected_types=None):
    """Compare the entity type counts from the reference and test crates."""
    all_types = expected_types if expected_types is not None else set(ref_counts.keys()).union(set(test_counts.keys()))
    print(f"{'Entity Type':<60}{'Ref Count':<12}{'Test Count':<12}{'Match?'}")
    print("-" * 90)
    for t in sorted(all_types):
        ref = ref_counts.get(t, 0)
        test = test_counts.get(t, 0)
        match = "✅" if ref == test else "❌"
        print(f"{t:<60}{ref:<12}{test:<12}{match}")

def follow_relation(entity, relation):
    """Utility to follow a relation which can be a dict with @id or a string."""
    if isinstance(entity, dict):
        rel = entity.get(relation)
        if isinstance(rel, dict):
            return rel.get("@id")
        return rel
    return None

def count_entities_by_type(graph, entity_type):
    """Count entities of a given @type in a graph."""
    count = 0
    for entity in graph:
        types = entity.get("@type")
        if types:
            if isinstance(types, str):
                types = [types]
            if entity_type in types:
                count += 1
    return count

def validate_entity_relation_count(graph, rule):
    """Validate that entities of source_type have relations to target_type with expected count.
    Supports:
      - fuzzy: if true, source entities are selected by type presence and relation, not strict match
      - relation: may be a list of relation keys
      - expected_count: may be a list of valid values
      - discriminator_relation: optional, string or list, used for fuzzy filtering instead of relation
      - target_type_groups: optional list of lists of types for target matching
    Returns True if validation passes, False if any failure.
    """
    source_type = rule["source_type"]
    target_type = rule.get("target_type")
    target_type_groups = rule.get("target_type_groups")
    relation = rule["relation"]
    expected_count = rule.get("expected_count")
    fuzzy = rule.get("fuzzy", False)
    discriminator_relation = rule.get("discriminator_relation")
    if isinstance(discriminator_relation, str):
        discriminator_relation = [discriminator_relation]
    discriminator_mode = rule.get("discriminator_mode", "include")

    if isinstance(source_type, str):
        source_type = [source_type]
    source_type_set = set(source_type)

    if isinstance(relation, str):
        relation = [relation]

    if isinstance(expected_count, int):
        expected_count = [expected_count]

    # Filter source entities
    source_entities = []
    for e in graph:
        types = e.get("@type")
        if types:
            if isinstance(types, str):
                types = [types]
            type_set = set(types)
            if fuzzy:
                rel_check = discriminator_relation if discriminator_relation else relation
                if source_type_set.issubset(type_set):
                    if discriminator_mode == "include" and any(rel in e for rel in rel_check):
                        source_entities.append(e)
                    elif discriminator_mode == "exclude" and all(rel not in e for rel in rel_check):
                        source_entities.append(e)
            else:
                if type_set == source_type_set:
                    source_entities.append(e)

    # Normalize target_type_groups if present
    if target_type_groups:
        # Normalize each group into sets
        target_type_group_sets = [set(g) for g in target_type_groups]
    elif isinstance(target_type, str):
        target_type = [target_type]

    # Collect all target entity IDs
    target_ids = set()
    target_id_to_types = {}
    for e in graph:
        types = e.get("@type")
        if types:
            if isinstance(types, str):
                types = [types]
            eid = e.get("@id")
            if eid:
                if target_type_groups:
                    if any(set(types) == group for group in target_type_group_sets):
                        target_ids.add(eid)
                        target_id_to_types[eid] = types
                elif target_type and any(t in types for t in target_type):
                    target_ids.add(eid)
                    target_id_to_types[eid] = types

    all_passed = True
    for entity in source_entities:
        all_related_ids = set()
        for rel in relation:
            rel_vals = entity.get(rel, [])
            if not isinstance(rel_vals, list):
                rel_vals = [rel_vals]
            for r in rel_vals:
                rid = r.get("@id") if isinstance(r, dict) else r
                if rid:
                    all_related_ids.add(rid)

        valid_count = len(all_related_ids)
        if expected_count and valid_count not in expected_count:
            print(f"\nValidation failed for source entity {entity.get('@id', '[unknown]')}: expected {expected_count} '{target_type if target_type else target_type_groups}' via {relation}, found {valid_count}.")
            all_passed = False
            continue
        if not all_related_ids <= target_ids:
            print(f"\nValidation failed: some related targets not found in graph: {all_related_ids - target_ids}")
            all_passed = False
            continue
        print(f"\nValidation passed for source entity {entity.get('@id', '[unknown]')} ({valid_count} '{target_type if target_type else target_type_groups}' via {relation}).")
    return all_passed

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare entity shapes in two RO-Crate manifests.")
    parser.add_argument("--composite", action="store_true", help="Count composite @type sets instead of individual types.")
    args = parser.parse_args()

    reference = load_crate_manifest("validation/reference_manifest.json")
    test = load_crate_manifest("Distributed_Provenance_Crate/ro-crate-metadata.json")

    ref_counts = extract_entity_counts(reference, composite_mode=args.composite)
    expected_entity_types = set(ref_counts.keys())

    test_counts = extract_entity_counts(test, composite_mode=args.composite)

    # Compare and display results
    compare_entity_shapes(ref_counts, test_counts, expected_types=expected_entity_types)

    # Prepare shape comparison data
    shape_comparison = []
    for t in sorted(expected_entity_types):
        shape_comparison.append({
            "Entity Type": t,
            "Ref Count": ref_counts.get(t, 0),
            "Test Count": test_counts.get(t, 0),
            "Match": ref_counts.get(t, 0) == test_counts.get(t, 0)
        })

    os.makedirs("validation", exist_ok=True)
    # with open("validation/entity_shape_comparison.json", "w", encoding="utf-8") as f:
    #     json.dump(shape_comparison, f, indent=2)

    test_graph = test.get("@graph", [])

    validation_rules = load_validation_rules()
    for rule in validation_rules:
        validate_entity_relation_count(test_graph, rule)

    validation_summary = []

    for rule in validation_rules:
        source_type = rule["source_type"]
        relation = rule["relation"]
        target_type = rule.get("target_type") or rule.get("target_type_groups")
        expected_count = rule.get("expected_count", "N/A")
        fuzzy = rule.get("fuzzy", False)
        discriminator = rule.get("discriminator_relation", None)
        discriminator_mode = rule.get("discriminator_mode", None)

        if isinstance(source_type, list):
            source_type_str = "+".join(source_type)
        else:
            source_type_str = source_type

        if isinstance(relation, list):
            relation_str = "+".join(relation)
        else:
            relation_str = relation

        if isinstance(target_type, list):
            if isinstance(target_type[0], list):  # Handle target_type_groups
                target_type_str = "|".join(["+".join(g) for g in target_type])
            else:
                target_type_str = "+".join(target_type)
        else:
            target_type_str = str(target_type)

        rule_result = {
            "Source Type": source_type_str,
            "Relation": relation_str,
            "Target Type": target_type_str,
            "Expected Count": expected_count,
            "Fuzzy": fuzzy,
            "Discriminator": discriminator,
            "Discriminator Mode": discriminator_mode,
            "Passed": "✅"  # default to passed, mark failed inside validation
        }

        # Modify validate_entity_relation_count to return a result
        result = validate_entity_relation_count(test_graph, rule)
        rule_result["Passed"] = "✅" if result else "❌"
        validation_summary.append(rule_result)

    # Print the summary table
    print("\nValidation Summary Table:")
    print(f"{'Source Type':<25}{'Relation':<15}{'Target Type':<40}{'Expected':<12}{'Fuzzy':<8}{'Disc.':<15}{'Mode':<10}{'Pass?'}")
    print("-" * 135)
    for row in validation_summary:
        print(f"{row['Source Type']:<25}{row['Relation']:<15}{row['Target Type']:<40}{str(row['Expected Count']):<12}{str(row['Fuzzy']):<8}{str(row['Discriminator']):<15}{str(row['Discriminator Mode']):<10}{row['Passed']}")

    with open("validation/validation_output.json", "w", encoding="utf-8") as f:
        json.dump(validation_summary, f, indent=2)
