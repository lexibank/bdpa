import attr
from pathlib import Path

from pylexibank import Concept, Language
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.util import progressbar

import lingpy
from clldutils.misc import slug


@attr.s
class CustomConcept(Concept):
    Number = attr.ib(default=None)
    MSA = attr.ib(default=None)


@attr.s
class CustomLanguage(Language):
    Latitude = attr.ib(default=None)
    Longitude = attr.ib(default=None)
    Name = attr.ib(default=None)
    Dataset = attr.ib(default=None)
    Source = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "bdpa"
    concept_class = CustomConcept
    language_class = CustomLanguage
    writer_options = dict(keep_languages=False, keep_parameters=False)

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
        converter = {
                '˗': '-',
                'ı': 'ɨ',
                '_': '+',
                'ɴ̣': 'ɴ̩',
                'ŋ̣̩': 'ŋ̍',
                'ɸ͡x': 'ɸ͡x/ɸ',
                "ouɚ": "ouɚ/oɚ",
                "ʌiə": "ʌiə/ʌə",
                "aːəiə": "aːəiə/aːə",
                "œːiə": "œːiə/œːə",
                "æiə": "æiə/æə",
                "ɛeə": "ɛeə/ɛə",
                "ɛiɪ": "ɛiɪ/ɛɪ",
                "ɛɪə": "ɛɪə/ɛə",
                "ʊuʌ": "ʊuʌ/ʊʌ",
                "euə": "euə/eə",
                "aʊə": "aʊə/aə",
                "æɪə": "æɪə/æə",
                "ɛiə": "ɛiə/ɛə",
                "ɒʊe": "ɒʊe/ɒe",
                "ɪiə": "ɪiə/ɪə",
                "iɪə": "iɪə/iə",
                "æɛo": "æɛo/æo",
                "æɪɛ": "æɪɛ/æɛ",
                "əɪɜ": "əɪɜ/əɜ",
                "ɐuɐ": "ɐuɐ/ɐɐ",
                "ɔuɐ": "ɔuɐ/ɔɐ",
                "aɪɐ": "aɪɐ/aɐ",
                "ɔʊə": "ɔʊə/ɔə",
                "iuə": "iuə/yə",
                "œʊɑ": "œʊɑ/œɑ",
                "ɑʊɔ": "ɑʊɔ/ɑɔ",
                "ɔɪɛ": "ɔɪɛ/ɔɛ",
                "oʊɤ": "oʊɤ/oɤ",
                "ouə": "ouə/oə",
                "oʊə": "oʊə/oə",
                "ʊɛʊ": "ʊɛʊ/ɛʊ",
                "uˡ": "uˡ/u",
                "ɾ̆": "ɾ̆/r",
                "ıiı": "ıiı/ɨi",
                "ɛɪʊ": "ɛɪʊ/ɛʊ",
                "ʌɪɤ": "ʌɪɤ/ʌɤ",
                "ɛɪɤ": "ɛɪɤ/ɛɤ",
                "eiə": "eiə/eə",
                "eɪə": "eɪə/eə",
                "øʊə": "øʊə/øə",
                "æeo": "æeo/æo",
                "ɛɪɐ": "ɛɪɐ/ɛɐ",
                "aɪə": "aɪə/aə",
                "uɛi": "uɛi/ɛi",
                "m̆": "m̆/m",
                "ɜıi": "ɜıi/ɜi",
                "ɒʊə": "ɒʊə/ɒə",
                "ʧ": "tʃ",
                "ʦ": "ts",
                "ʨ": "tɕ",
                "ʣ": "dz",
                "ʤ": "dʒ",
                "ʥ": "dʑ",
                "ʧʰ": "tʃʰ",
                "k͡χ": "kx",
                "aei": "aei/ai"
                }

        for f in progressbar(self.raw_dir.joinpath('msa').glob('*.msa')):
            msa = lingpy.align.sca.MSA(f.as_posix())
            cogid = msa.infile.split('_')[-1][:-4]
            for language, alignment in zip(msa.taxa, msa.alignment):
                alm = [converter.get(x, x) for x in alignment]
                seq = [x for x in alm if x != '-']
                lexeme = args.writer.add_form_with_segments(
                    Language_ID=languages[language],
                    Parameter_ID=concepts[msa.seq_id.replace('"', '')],
                    Value=''.join(seq),
                    Form=''.join(seq),
                    Segments=seq,
                    Cognacy=cogid,
                    Source=sources[language]
                    )
                args.writer.add_cognate(
                        lexeme=lexeme,
                        Cognateset_ID=cogid,
                        Alignment=alm,
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

