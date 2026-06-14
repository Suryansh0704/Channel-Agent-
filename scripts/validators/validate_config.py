"""
Validates config files against schema and value ranges.
Used by push_configs.py before pushing.
"""
import json
import os

def load_schema():
    schema_path = os.path.join(os.path.dirname(__file__), 'config_schema.json')
    with open(schema_path, 'r') as f:
        return json.load(f)

def validate_type(value, expected_type):
    type_map = {
        'string': str,
        'number': (int, float),
        'boolean': bool,
        'array': list,
        'object': dict
    }
    
    expected = type_map.get(expected_type)
    if expected is None:
        return True
    
    return isinstance(value, expected)

def validate_value(value, constraints):
    errors = []
    
    if 'minimum' in constraints and value < constraints['minimum']:
        errors.append(f'Value {value} below minimum {constraints["minimum"]}')
    
    if 'maximum' in constraints and value > constraints['maximum']:
        errors.append(f'Value {value} above maximum {constraints["maximum"]}')
    
    if 'minLength' in constraints and len(value) < constraints['minLength']:
        errors.append(f'Length {len(value)} below minimum {constraints["minLength"]}')
    
    if 'enum' in constraints and value not in constraints['enum']:
        errors.append(f'Value "{value}" not in allowed values: {constraints["enum"]}')
    
    return errors

def validate_object(obj, schema, path=''):
    errors = []
    
    if schema.get('type') == 'object':
        for required in schema.get('required', []):
            if required not in obj:
                errors.append(f'{path}: Missing required field "{required}"')
        
        for prop, prop_schema in schema.get('properties', {}).items():
            if prop in obj:
                prop_path = f'{path}.{prop}' if path else prop
                
                if not validate_type(obj[prop], prop_schema.get('type')):
                    errors.append(f'{prop_path}: Type mismatch (expected {prop_schema.get("type")})')
                    continue
                
                value_errors = validate_value(obj[prop], prop_schema)
                errors.extend([f'{prop_path}: {e}' for e in value_errors])
                
                if prop_schema.get('type') == 'object' and 'properties' in prop_schema:
                    nested_errors = validate_object(obj[prop], prop_schema, prop_path)
                    errors.extend(nested_errors)
                
                if prop_schema.get('type') == 'array' and 'items' in prop_schema:
                    for i, item in enumerate(obj[prop]):
                        if not validate_type(item, prop_schema['items'].get('type')):
                            errors.append(f'{prop_path}[{i}]: Type mismatch')
    
    return errors

def validate_config_file(config_data, filename):
    schema = load_schema()
    
    file_schema = schema.get(filename)
    if not file_schema:
        return True, 'No schema found (skipping validation)'
    
    errors = validate_object(config_data, file_schema)
    
    if errors:
        return False, '; '.join(errors)
    
    return True, 'Valid'

def main():
    import sys
    
    if len(sys.argv) < 2:
        print('Usage: python validate_config.py <config_file.json>')
        return
    
    filepath = sys.argv[1]
    filename = os.path.basename(filepath)
    
    with open(filepath, 'r') as f:
        config = json.load(f)
    
    is_valid, msg = validate_config_file(config, filename)
    print(f'{"VALID" if is_valid else "INVALID"}: {filename}: {msg}')

if __name__ == '__main__':
    main()
