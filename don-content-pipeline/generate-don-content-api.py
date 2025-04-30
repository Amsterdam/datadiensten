#!/usr/bin/env python
from schematools.loaders import get_schema_loader
import yaml

SCHEMA_URL = "https://schemas.data.amsterdam.nl/datasets/"

def camelcase_to_kebabcase(string):
    return ''.join(['-' + char.lower() if char.isupper() else char for char in string]).lstrip('-')

def _get_all_dataset_info(schema_url=SCHEMA_URL):
    loader = get_schema_loader(schema_url)
    response = []
    
    try:
        datasets = loader.get_all_datasets()
        for dataset in datasets:
            if datasets[dataset].auth == frozenset(["OPENBAAR"]) and datasets[dataset].status.value == 'beschikbaar':
                id = datasets[dataset].id
                path = loader.get_dataset_path(datasets[dataset].id)
                auth = datasets[dataset].auth
                title = datasets[dataset].title if datasets[dataset].title else datasets[dataset].id
                description = datasets[dataset].description
                response.append({'path': path, 'id': id, 'auth': auth, 'title': title, 'description': description})
        return response
    
    except Exception as e:
        raise("Dataset not found") from e

datasets = _get_all_dataset_info()

for dataset in datasets:
    
    template = {
        'service_name': dataset['title'],
        'description': dataset['description'],
        'organization': {
            'name': 'Gemeente Amsterdam',
            'ooid': 25698
        },
        'api_type': 'rest_json',
        'api_authentication': 'none',
        'environments': [{
            'name': 'production',
            'api_url': f"https://api.data.amsterdam.nl/v1/{dataset['path']}",
            'specification_url': f"https://api.data.amsterdam.nl/v1/{dataset['path']}/openapi.json",
            'documentation_url': f"https://api.data.amsterdam.nl/v1/docs/datasets/{dataset['path']}.html"
        }],
        'contact': {
            'email': 'dataplatform@amsterdam.nl',
            'url': 'https://api.data.amsterdam.nl/api/'
        },
        'terms_of_use': {
            'government_only': False,
            'pay_per_use': False,
            'uptime_guarantee': 0
        }
    }

    print(f"writing gemeente-amsterdam-{camelcase_to_kebabcase(dataset['id'])}.yml")
    with open(f"datasets/gemeente-amsterdam-{camelcase_to_kebabcase(dataset['id'])}.yml", "w") as file:
        yaml.dump(template, file, sort_keys=False, allow_unicode=True)
