import attr
from pathlib import Path

from pylexibank import Concept, Language
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.util import progressbar

import lingpy
from clldutils.misc import slug

from collections import defaultdict
from pysen.glosses import to_concepticon


@attr.s
class CustomConcept(Concept):
    Number = attr.ib(default=None)
    MSA = attr.ib(default=None)


@attr.s 
class CustomLanguage(Language):
    Name = attr.ib(default=None)
    Dataset = attr.ib(default=None)
    Source = attr.ib(default=None)

    
class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "bdpa"
    concept_class = CustomConcept
    language_class = CustomLanguage

    def cmd_makecldf(self, args):
        args.writer.add_sources()
        languages, sources = {}, {}
        for language in self.languages:
            languages[language['Name']] = language['ID']
            sources[language['Name']] = language['Source']
            args.writer.add_language(**language)
        concepts = {}
        for concept in self.concepts:
            idx = '{0}_{1}'.format(concept['NUMBER'], slug(concept['GLOSS']))
            concepts[concept['MSA_NAME'].replace('"', '')] = idx
            args.writer.add_concept(
                    ID=idx,
                    Name=concept['GLOSS'],
                    Concepticon_ID=concept['CONCEPTICON_ID'],
                    Concepticon_Gloss=concept['CONCEPTICON_GLOSS'],
                    Number=concept['NUMBER'],
                    MSA=concept['MSA_NAME'])
        
        for f in progressbar(self.raw_dir.joinpath('msa').glob('*.msa')):
            msa = lingpy.align.sca.MSA(f.as_posix())
            cogid = msa.infile.split('_')[-1][:-4]
            for language, seq, alignment in zip(msa.taxa, msa.seqs,
                    msa.alignment):
                lexeme = args.writer.add_form_with_segments(
                    Language_ID=languages[language],
                    Parameter_ID=concepts[msa.seq_id.replace('"', '')],
                    Value=''.join(seq.split()),
                    Form=''.join(seq.split()),
                    Segments=seq.split(),
                    Cognacy=cogid,
                    Source=sources[language]
                    )
                args.writer.add_cognate(
                        lexeme=lexeme,
                        Cognateset_ID=cogid,
                        Alignment=alignment,
                        Source=['List2014e'])
        #languages = defaultdict(list)
        #visited = set()
        #count = 1
        #with open('etc/languages.tsv', 'w') as l, open('etc/concepts.tsv', 'w') as c:
        #    c.write('NUMBER\tGLOSS\tCONCEPTICON_ID\tCONCEPTICON_GLOSS\n')
        #    l.write('ID\tName\tDataset\tGlottocode\tSource\n')
        #    for f in self.raw_dir.glob('*.msa'):
        #        msa = lingpy.align.sca.MSA(f.as_posix())
        #        concept = msa.seq_id.split('"')[1] if '"' in msa.seq_id else msa.seq_id
        #        for taxon in msa.taxa:
        #            if taxon not in visited:
        #                visited.add(taxon)
        #                l.write('{0}\t{1}\t{2}\t{3}\t{4}\n'.format(
        #                    slug(taxon, lowercase=False),
        #                    taxon,
        #                    msa.dataset, '', ''))
        #            if msa.seq_id not in visited:
        #                visited.add(msa.seq_id)
        #                match = to_concepticon([{'gloss': concept}])
        #                if match[concept]:
        #                    cid, cgl = match[concept][0][0], match[concept][0][1]
        #                else:
        #                    cid, cgl = '', ''
        #                c.write('{0}\t{1}\t{2}\t{3}\t{4}\n'.format(
        #                    count, concept, msa.seq_id, cid, cgl))
        #                count += 1


        # TODO: add concepts with `add_concepts`
        #concepts = {}
        #for concept in self.conceptlists[0].concepts.values():
        #    idx = concept.id.split("-")[-1] + "_" + slug(concept.english)
        #    args.writer.add_concept(
        #        ID=idx,
        #        Name=concept.gloss,
        #        Number=concept.number,
        #        Concepticon_ID=concept.concepticon_id,
        #        Concepticon_Gloss=concept.concepticon_gloss,
        #    )
        #    concepts[concept.english] = idx
        #languages = args.writer.add_languages(lookup_factory="Name")

