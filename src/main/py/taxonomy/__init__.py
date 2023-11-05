"""
This provides the Abstract Base Class (ABC) Taxonomy from which any specific domain-specific data might be represented.

Formally, Taxonomy is the science of naming, describing, and classifying organisms into groups and levels.

This base class provides the following levels for the taxonomy:

- Domains
    - Families
        - Species
            - Subspecies

Please note that this classification is not fixed and can be easily extended to more specialized or granular taxonomies.

Additionally, this class provides also the organisms available within the domain of the taxonomy

Please note that this class does not dictate the rules for classification nor

 :author: vic on 2023-10-14
"""

from abc import ABC, abstractmethod


class Taxonomy(ABC):
    @abstractmethod
    def start(self):
        """
        To initialize the taxonomy data.
        :return: None
        """
        pass

    #
    # Organisms
    #

    @abstractmethod
    def organisms(self) -> list:
        """
        Core point of interest and study for the particular taxonomy.

        :return: a list of the organisms to study in the current taxonomy.
        """
        pass

    #
    # Classification
    #

    @abstractmethod
    def domains(self) -> list:
        """
        This is the highest level of classification in the taxonomy. This corresponds to the large groups covered by
        this taxonomy.

        :return: a list of the domains available in the current taxonomy.
        """
        pass

    @abstractmethod
    def families(self, ancestor=None, family_id=None) -> list:
        """
        A taxonomic rank to group related genera together. Families are composed of one or more genera that share a
        common ancestor and similar characteristics.

        :param family_id: to pick a specific family
        :param ancestor: to which this family belongs.
        :return: a list of the families available in the current taxonomy for a given ancestor.
        """
        pass

    @abstractmethod
    def species(self, ancestor=None) -> list:
        """
        The most specific level of classification. Each species has a unique name within its given ancestry. The current
        taxonomy may define any appropriate naming rules

        :param ancestor: to which the species belongs
        :return: a list of the species available in the current taxonomy for a given ancestor.
        """
        pass

    @abstractmethod
    def subspecies(self, ancestor=None) -> list:
        """
        A taxonomic rank used to group populations of a species that have distinct characteristics but are correlated in
        the parent species.

        :param ancestor: to which the subspecies belong
        :return: a list of the subspecies available in the current taxonomy for a given ancestor.
        """
        pass

    @abstractmethod
    def classify(self, organism) -> list:
        pass
