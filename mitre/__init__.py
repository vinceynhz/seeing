"""
 :author: vic on 2023-10-07
"""
import logging
import requests
import json
import tqdm

from stix2 import MemoryStore, Filter


def progress_hook(obj, pbar: tqdm.tqdm):
    pbar.update(1)
    return obj


def _load_json(file_path):
    with open(file_path, "r", encoding='utf-8') as infile:
        pbar = tqdm.tqdm()
        pbar.set_description("Loading JSON file")
        data = json.load(infile, object_hook=lambda obj: progress_hook(obj, pbar))
        pbar.close()
    return data


def _is_revoked_deprecated(stix_object):
    return stix_object.get("x_mitre_deprecated", False) or stix_object.get("revoked", False)


def _remove_revoked_deprecated(stix_objects):
    """Remove any revoked or deprecated objects from queries made to the data source"""
    # Note we use .get() because the property may not be present in the JSON data. The default is False
    # if the property is not set.
    return list(
        filter(
            lambda x: not _is_revoked_deprecated(x),
            stix_objects
        )
    )


def init_mitre_matrix(file_path=None):
    """
    To load a MITRE matrix data
    :param file_path: to load the stix data from a local file
    :return: a MemoryStore that can be used to access the stix data
    """
    logging.info("Loading MITRE Att&ck matrix into memory")
    stix = None
    if file_path is not None:
        logging.info("Loading file: %s", file_path)
        stix = _load_json(file_path)
    else:
        logging.info("Loading remotely")
        stix = requests.get(
            "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json").json()

    logging.info("Creating in-memory matrix")
    mem_store = MemoryStore(stix_data=stix["objects"])

    logging.info("MITRE Att&ck matrix loaded")
    return mem_store


def extract_tactics(source: MemoryStore):
    """
    To extract the list of Tactics available in the source
    :param source: of stix data
    :return: the list of tactics present in the first MITRE matrix provided by the source
    """
    logging.info("Extracting available tactics")
    tactics = []
    matrix = source.query([
        Filter('type', '=', 'x-mitre-matrix'),
    ])
    if len(matrix) == 0:
        return []
    matrix = matrix[0]
    for tactic_id in matrix['tactic_refs']:
        stix_tactic = source.get(tactic_id)
        tactics.append({
            'id': stix_tactic['id'],
            'name': stix_tactic['name'],
            'description': stix_tactic['description'],
            'x_mitre_shortname': stix_tactic['x_mitre_shortname']
        })
        # tactics[stix_tactic['id']] = tactic
    logging.info("Tactics extracted")
    return tactics


def extract_groups(source: MemoryStore):
    """
    To extract the list of Groups available in the source
    :param source: of stix data
    :return: the list of non deprecated or revoked intruders provided by the source
    """
    logging.info("Extracting available groups")
    stix_groups = source.query([Filter("type", "=", "intrusion-set")])
    stix_groups = _remove_revoked_deprecated(stix_groups)
    groups = []
    for stix_group in stix_groups:
        groups.append({
            'id': stix_group['id'],
            'name': stix_group['name'],
            'aliases': stix_group['aliases']
        })
        # groups[stix_group['id']] = group
    logging.info("Groups extracted")
    return groups


def techniques_by_group(source: MemoryStore, group_id: str):
    """
    To get the techniques/subtechniques used by a group

    :param source: of stix data
    :param group_id: to retrieve
    :return:
    """
    logging.info("Getting techniques by %s", group_id)
    relationships = source.relationships(group_id)
    relationships = _remove_revoked_deprecated(relationships)
    techniques = []
    for relationship in relationships:
        target_obj = source.get(relationship["target_ref"])
        if target_obj["type"] != "attack-pattern" or _is_revoked_deprecated(target_obj):
            continue
        technique = {
            'id': target_obj["external_references"][0]["external_id"],
            'tactics': [kc["phase_name"] for kc in target_obj["kill_chain_phases"]],
            'name': target_obj["name"]
        }
        techniques.append(technique)
    logging.info("Found %d techniques", len(techniques))
    return techniques
