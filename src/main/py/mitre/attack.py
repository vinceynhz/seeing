"""
 :author: vic on 2023-10-15
"""
import logging

import requests
from stix2 import MemoryStore, Filter

from mitre import _load_json
from taxonomy import Taxonomy


class AttackMatrix(Taxonomy):
    def __init__(self, file_path=None):
        self.log = logging.getLogger("attack.matrix")
        self.file_path = file_path
        self.source = None
        self.adversaries = []
        self.tactics = []

    def start(self):
        """
        To load a MITRE matrix data as a source for the current Taxonomy, and then extract the tactics and adversary
        groups.

        :return: None
        """
        if self.file_path is not None:
            self.log.info("Loading file: %s", self.file_path)
            stix = _load_json(self.file_path)
        else:
            self.log.info("Loading remotely")
            stix = requests.get(
                "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json").json()

        self.log.info("Creating in-memory matrix")
        self.source = MemoryStore(stix_data=stix["objects"])
        self.log.info("MITRE Att&ck matrix loaded")

        self.tactics = self._extract_tactics()
        self.adversaries = self._extract_adversaries()

    def _extract_tactics(self):
        """
        To extract the list of Tactics available in the source

        :return: the list of tactics present in the first Mitre Matrix provided by the source
        """
        self.log.info("Extracting available tactics")
        matrix = self.source.query([
            Filter('type', '=', 'x-mitre-matrix'),
        ])
        if len(matrix) == 0:
            return []
        matrix = matrix[0]
        tactics = []
        for order, tactic_id in enumerate(matrix['tactic_refs']):
            stix_tactic = self.source.get(tactic_id)
            tactics.append({
                'id': stix_tactic['id'],
                'order': order,
                'name': stix_tactic['name'],
                'description': stix_tactic['description'],
                'x_mitre_shortname': stix_tactic['x_mitre_shortname']
            })
            # tactics[stix_tactic['id']] = tactic
        self.log.info("Tactics extracted")
        return tactics

    def _extract_adversaries(self):
        """
        To extract the list of Groups available in the source

        :return: the list of non deprecated or revoked intruders provided by the source
        """
        self.log.info("Extracting available adversary groups")
        stix_adversaries = self.source.query([Filter("type", "=", "intrusion-set")])
        stix_adversaries = AttackMatrix._remove_revoked_deprecated(stix_adversaries)
        adversaries = []
        for stix_adversary in stix_adversaries:
            adversaries.append({
                'id': stix_adversary['id'],
                'name': stix_adversary['name'],
                'aliases': stix_adversary['aliases']
            })
            # adversaries[stix_group['id']] = group
        self.log.info("Adversary groups extracted")
        return adversaries

    def organisms(self) -> list:
        return self.adversaries

    def domains(self) -> list:
        # TODO(vic): this could be expanded to include the other Att&ck domains
        return ["enterprise"]

    def families(self, ancestor=None, family_id=None) -> list:
        if family_id is not None:
            return [tactic for tactic in self.tactics if tactic['id'] == family_id]
        return self.tactics

    def species(self, ancestor=None, organism=None) -> list:
        """
        To get the techniques/subtechniques used by a group

        :param ancestor: to retrieve
        :param organism: to retrieve
        :return: should return an hierarchical object of the taxonomy for this adversary
        """
        techniques = []
        if organism is not None:
            self.log.info("Getting techniques by %s", organism)
            relationships = self.source.relationships(organism)
            relationships = AttackMatrix._remove_revoked_deprecated(relationships)
            for relationship in relationships:
                target_obj = self.source.get(relationship.target_ref)
                if target_obj.type != "attack-pattern" or AttackMatrix._is_revoked_deprecated(target_obj):
                    continue
                technique = {
                    'id': target_obj.id,
                    'external_id': target_obj.external_references[0]["external_id"],
                    'tactics': [kc["phase_name"] for kc in target_obj.kill_chain_phases],
                    'name': target_obj.name,
                    'type': 'subtechnique' if target_obj.x_mitre_is_subtechnique else 'technique'
                }
                techniques.append(technique)
            self.log.info("Found %d techniques", len(techniques))
        return techniques

    def subspecies(self, ancestor=None) -> list:
        return []

    def classify(self, organism) -> list:
        techniques = self.species(organism=organism)
        classification = {t["x_mitre_shortname"]: {"family": t, "species": []} for t in self.tactics}

        for technique in techniques:
            for tactic in technique["tactics"]:
                tq = {k: technique[k] for k in technique if k != 'tactics'}
                classification[tactic]["species"].append(tq)

        classification = [classification[k] for k in classification if len(classification[k]['species']) > 0]
        classification.sort(key=lambda x: x['family']['order'], reverse=True)
        return classification

    @staticmethod
    def _is_revoked_deprecated(stix_object):
        return stix_object.get("x_mitre_deprecated", False) or stix_object.get("revoked", False)

    @staticmethod
    def _remove_revoked_deprecated(stix_objects):
        """Remove any revoked or deprecated objects from queries made to the data source"""
        # Note we use .get() because the property may not be present in the JSON data. The default is False
        # if the property is not set.
        return list(
            filter(
                lambda x: not AttackMatrix._is_revoked_deprecated(x),
                stix_objects
            )
        )
