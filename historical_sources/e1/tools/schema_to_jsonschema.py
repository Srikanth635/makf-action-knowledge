#!/usr/bin/env python3
"""Compile the deliberately small supported LinkML schema subset into JSON Schema.

Canonical contract is schema/makf_extraction.linkml.yaml; this is an offline
subset compiler, NOT a replacement for the full LinkML toolchain.
"""
import argparse
import json
from pathlib import Path
import yaml

PRIMITIVE = {
    'string': {'type': 'string'},
    'integer': {'type': 'integer'},
    'boolean': {'type': 'boolean'},
    'float': {'type': 'number'},
    'double': {'type': 'number'},
    'datetime': {'type': 'string', 'format': 'date-time'},
    'uri': {'type': 'string', 'format': 'uri'},
}

def compile_schema(spec):
    classes, enums = spec['classes'], spec['enums']
    defs = {}
    for name, defn in classes.items():
        properties, required = {}, []
        for key, attr in defn.get('attributes', {}).items():
            attr = attr or {}
            range_name = attr.get('range', spec.get('default_range', 'string'))
            if range_name in PRIMITIVE:
                p = dict(PRIMITIVE[range_name])
            elif range_name in enums:
                p = {'type': 'string', 'enum': list(enums[range_name]['permissible_values'])}
            elif range_name in classes:
                p = {'$ref': '#/$defs/' + range_name}
            else:
                raise ValueError(f'Unsupported range {name}.{key}: {range_name}')
            if attr.get('multivalued'):
                p = {'type': 'array', 'items': p}
                if attr.get('required'):
                    p['minItems'] = 1
            elif p.get('type') == 'string' and attr.get('required'):
                p['minLength'] = 1
            if attr.get('description'):
                p['description'] = attr['description']
            properties[key] = p
            if attr.get('required') or attr.get('identifier'):
                required.append(key)
        defs[name] = {
            'type': 'object',
            'description': defn.get('description', ''),
            'properties': properties,
            'required': required,
            'additionalProperties': False,
        }
    return {
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        '$id': spec['id'] + '/json-schema',
        'title': spec['name'],
        '$ref': '#/$defs/ExtractionBatch',
        '$defs': defs,
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--schema', default='schema/makf_extraction.linkml.yaml')
    parser.add_argument('--out', default='schema/makf_extraction.schema.json')
    args = parser.parse_args()
    result = compile_schema(yaml.safe_load(Path(args.schema).read_text()))
    Path(args.out).write_text(json.dumps(result, indent=2) + '\n')
    print('Wrote', args.out)
