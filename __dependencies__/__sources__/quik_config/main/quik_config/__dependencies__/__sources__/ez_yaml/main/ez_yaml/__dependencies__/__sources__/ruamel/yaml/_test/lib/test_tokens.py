
exec(f"""import {".".join(__name__.split(".")[:-2])}.yaml;ruamel = {".".join(__name__.split(".")[:-2])}""")
import pprint

# Tokens mnemonic:
# directive:            %
# document_start:       ---
# document_end:         ...
# alias:                *
# anchor:               &
# tag:                  !
# scalar                _
# block_sequence_start: [[
# block_mapping_start:  {{
# block_end:            ]}
# flow_sequence_start:  [
# flow_sequence_end:    ]
# flow_mapping_start:   {
# flow_mapping_end:     }
# entry:                ,
# key:                  ?
# value:                :

_replaces = {
    ruamel.yaml.DirectiveToken: '%',
    ruamel.yaml.DocumentStartToken: '---',
    ruamel.yaml.DocumentEndToken: '...',
    ruamel.yaml.AliasToken: '*',
    ruamel.yaml.AnchorToken: '&',
    ruamel.yaml.TagToken: '!',
    ruamel.yaml.ScalarToken: '_',
    ruamel.yaml.BlockSequenceStartToken: '[[',
    ruamel.yaml.BlockMappingStartToken: '{{',
    ruamel.yaml.BlockEndToken: ']}',
    ruamel.yaml.FlowSequenceStartToken: '[',
    ruamel.yaml.FlowSequenceEndToken: ']',
    ruamel.yaml.FlowMappingStartToken: '{',
    ruamel.yaml.FlowMappingEndToken: '}',
    ruamel.yaml.BlockEntryToken: ',',
    ruamel.yaml.FlowEntryToken: ',',
    ruamel.yaml.KeyToken: '?',
    ruamel.yaml.ValueToken: ':',
}


def test_tokens(data_filename, tokens_filename, verbose=False):
    tokens1 = []
    with open(tokens_filename, 'r') as fp:
        tokens2 = fp.read().split()
    try:
        yaml = ruamel.yaml.YAML(typ='unsafe', pure=True)
        with open(data_filename, 'rb') as fp1:
            for token in yaml.scan(fp1):
                if not isinstance(token, (ruamel.yaml.StreamStartToken, ruamel.yaml.StreamEndToken)):
                    tokens1.append(_replaces[token.__class__])
    finally:
        if verbose:
            print('TOKENS1:', ' '.join(tokens1))
            print('TOKENS2:', ' '.join(tokens2))
    assert len(tokens1) == len(tokens2), (tokens1, tokens2)
    for token1, token2 in zip(tokens1, tokens2):
        assert token1 == token2, (token1, token2)


test_tokens.unittest = ['.data', '.tokens']


def test_scanner(data_filename, canonical_filename, verbose=False):
    for filename in [data_filename, canonical_filename]:
        tokens = []
        try:
            yaml = ruamel.yaml.YAML(typ='unsafe', pure=False)
            with open(filename, 'rb') as fp:
                for token in yaml.scan(fp):
                    tokens.append(token.__class__.__name__)
        finally:
            if verbose:
                pprint.pprint(tokens)


test_scanner.unittest = ['.data', '.canonical']

if __name__ == '__main__':
    import test_appliance

    test_appliance.run(globals())
